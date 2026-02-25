"""Evaluation pipeline extracted from the monolithic Simulation class."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple
import logging

import numpy as np
import torch
from tqdm import tqdm

from src.eval_module.evaluation import Evaluator
from src.eval_module.metrics.rmspe_loss import RMSPELoss
from simulation.kalman_filter import BatchExtendedKalmanFilter1D, BatchKalmanFilter1D, KalmanFilter1D
from src.trainer_module.simulation.eval_reporting import log_evaluation_results

logger = logging.getLogger(__name__)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class EvalPipeline:
    """Run model evaluation and report comparative metrics."""

    def __init__(self, config, components: Dict[str, Any], simulation, output_dir):
        self.config = config
        self.components = components
        self.sim = simulation
        self.output_dir = output_dir

    def _run_evaluation_pipeline(self) -> None:
        """Execute the evaluation pipeline."""
        logger.info("Starting evaluation pipeline")

        if self.sim.trained_model is None and self.sim.model is not None:
            logger.info("Using loaded model for evaluation")
            self.sim.trained_model = self.sim.model
        elif self.sim.trained_model is None:
            logger.error("No model available for evaluation")
            return

        self.sim.trained_model.eval()

        if self.sim.test_dataloader is None:
            if self.sim.valid_dataloader is not None:
                logger.warning("No test dataloader available, using validation dataloader instead")
                test_dataloader = self.sim.valid_dataloader
            else:
                logger.error("No validation or test dataloader available for evaluation")
                return
        else:
            test_dataloader = self.sim.test_dataloader

        try:
            logger.info("Evaluating model(s) on trajectory test data")

            is_near_field = (
                hasattr(self.sim.trained_model, "field_type")
                and self.sim.trained_model.field_type.lower() == "near"
            )
            if is_near_field:
                error_msg = "Near-field option is not available in the current evaluation pipeline"
                logger.error(error_msg)
                self.sim.results["evaluation_error"] = error_msg
                return

            filter_type = getattr(self.config.kalman_filter, "filter_type", "standard").lower()
            logger.info("Using Kalman filter type: %s", filter_type)

            if filter_type == "standard":
                KalmanFilter1D.from_config(self.config)

            rmspe_criterion = RMSPELoss().to(DEVICE)

            dnn_trajectory_results = []
            dnn_total_loss = 0.0
            ekf_total_loss = 0.0
            dnn_total_samples = 0
            classic_methods_losses: Dict[str, Dict[str, float]] = {}

            classic_methods: List[str] = []
            if hasattr(self.config.simulation, "subspace_methods") and self.config.simulation.subspace_methods:
                classic_methods = self.config.simulation.subspace_methods
                logger.info("Will evaluate classic subspace methods: %s", classic_methods)
                for method in classic_methods:
                    classic_methods_losses[method] = {"total_loss": 0.0, "total_samples": 0}

            evaluator = Evaluator(
                self.config,
                model=self.sim.trained_model,
                system_model=self.sim.system_model,
                output_dir=self.output_dir,
            )

            with torch.no_grad():
                for batch_data in tqdm(test_dataloader, desc="Evaluating trajectories"):
                    trajectories, sources_num, labels = batch_data
                    batch_size, trajectory_length = trajectories.shape[0], trajectories.shape[1]

                    batch_dnn_preds = [[] for _ in range(batch_size)]
                    batch_dnn_kf_preds = [[] for _ in range(batch_size)]
                    batch_kf_covariances = [[] for _ in range(batch_size)]

                    max_sources = torch.max(sources_num).item()

                    if filter_type == "extended":
                        logger.info(
                            "Creating BatchExtendedKalmanFilter1D for batch_size=%s, max_sources=%s",
                            batch_size,
                            max_sources,
                        )
                        batch_kf = BatchExtendedKalmanFilter1D.from_config(
                            self.config,
                            batch_size=batch_size,
                            max_sources=max_sources,
                            device=DEVICE,
                            trajectory_type=self.config.trajectory.trajectory_type,
                        )
                    else:
                        logger.info(
                            "Creating BatchKalmanFilter1D for batch_size=%s, max_sources=%s",
                            batch_size,
                            max_sources,
                        )
                        batch_kf = BatchKalmanFilter1D.from_config(
                            self.config,
                            batch_size=batch_size,
                            max_sources=max_sources,
                            device=DEVICE,
                        )

                    batch_kf.initialize_states(labels[:, 0, :max_sources], sources_num[:, 0])

                    for step in range(trajectory_length):
                        step_data = trajectories[:, step].to(DEVICE)
                        step_sources = sources_num[:, step].to(DEVICE)
                        step_mask = (
                            torch.arange(max_sources, device=DEVICE).expand(batch_size, -1)
                            < step_sources[:, None]
                        )

                        model_preds, kf_preds, step_loss, kf_loss, step_covariances = (
                            self._evaluate_dnn_model_kf_step_batch(
                                step_data,
                                step_sources,
                                labels[:, step, :max_sources],
                                step_mask,
                                batch_kf,
                                rmspe_criterion,
                                is_near_field,
                            )
                        )

                        dnn_total_loss += step_loss
                        ekf_total_loss += kf_loss
                        dnn_total_samples += batch_size

                        for i in range(batch_size):
                            batch_dnn_preds[i].append(model_preds[i])
                            batch_dnn_kf_preds[i].append(kf_preds[i])
                            batch_kf_covariances[i].append(step_covariances[i])

                        if classic_methods:
                            classic_results = evaluator._evaluate_classic_methods_step_batch(
                                step_data,
                                step_sources,
                                labels[:, step, :max_sources],
                                rmspe_criterion,
                                classic_methods,
                            )
                            for method, results in classic_results.items():
                                classic_methods_losses[method]["total_loss"] += results["total_loss"]
                                classic_methods_losses[method]["total_samples"] += results["count"]

                    for i in range(batch_size):
                        num_sources_array = sources_num[i].cpu().numpy()
                        gt_trajectory = np.array(
                            [labels[i, t, : num_sources_array[t]].cpu().numpy() for t in range(trajectory_length)]
                        )

                        dnn_trajectory_results.append(
                            {
                                "model_predictions": batch_dnn_preds[i],
                                "kf_predictions": batch_dnn_kf_preds[i],
                                "kf_covariances": batch_kf_covariances[i],
                                "ground_truth": gt_trajectory,
                                "sources": num_sources_array,
                            }
                        )

            log_evaluation_results(
                simulation=self.sim,
                dnn_total_loss=dnn_total_loss,
                ekf_total_loss=ekf_total_loss,
                dnn_total_samples=dnn_total_samples,
                classic_methods_losses=classic_methods_losses,
                dnn_trajectory_results=dnn_trajectory_results,
                classic_trajectory_results=None,
            )
            self.sim.results["dnn_trajectory_results"] = dnn_trajectory_results
        except Exception as exc:
            logger.exception("Error during evaluation: %s", exc)
            self.sim.results["evaluation_error"] = str(exc)

    def _evaluate_dnn_model_kf_step_batch(
        self,
        step_data: torch.Tensor,
        step_sources: torch.Tensor,
        step_angles: torch.Tensor,
        step_mask: torch.Tensor,
        batch_kf: BatchKalmanFilter1D,
        rmspe_criterion: RMSPELoss,
        is_near_field: bool,
    ) -> Tuple[List[np.ndarray], List[np.ndarray], float, float, List[np.ndarray]]:
        """Evaluate DNN step on a batch and apply Kalman filtering."""
        batch_size = step_data.shape[0]
        max_sources = batch_kf.max_sources

        batch_angles_pred_list = []
        total_loss = 0.0

        for i in range(batch_size):
            single_step_data = step_data[i].unsqueeze(0)
            single_step_sources = step_sources[i]
            num_sources_item = single_step_sources.item()

            if num_sources_item <= 0:
                batch_angles_pred_list.append(torch.empty((0,), device=DEVICE))
                continue

            if is_near_field:
                angles_pred_single, _, _ = self.sim.trained_model(single_step_data, single_step_sources)
            else:
                angles_pred_single, _, _ = self.sim.trained_model(single_step_data, single_step_sources)

            angles_pred_single = angles_pred_single.view(1, -1)[:, :num_sources_item]

            with torch.no_grad():
                truth = step_angles[i, :num_sources_item].unsqueeze(0)
                loss, best_perm = rmspe_criterion(angles_pred_single, truth, return_best_perm=True)
                total_loss += loss.item()
                angles_pred_optimal = angles_pred_single.squeeze(0)[best_perm.squeeze(0)]
                batch_angles_pred_list.append(angles_pred_optimal)

        padded_angles_pred = torch.zeros((batch_size, max_sources), device=DEVICE)
        for i, pred in enumerate(batch_angles_pred_list):
            num_sources = pred.shape[0]
            if num_sources > 0:
                padded_angles_pred[i, :num_sources] = pred

        batch_kf.predict()
        kf_predictions_after_update, kf_covariances = batch_kf.update(padded_angles_pred, step_mask)
        kf_predictions_after_update = kf_predictions_after_update.cpu().numpy()
        kf_covariances = kf_covariances.cpu().numpy()

        model_predictions_list: List[np.ndarray] = []
        kf_predictions_list: List[np.ndarray] = []
        kf_rmspe_list = []
        kf_covariance_list: List[np.ndarray] = []

        for i in range(batch_size):
            num_sources = step_sources[i].item()
            if num_sources > 0:
                model_predictions_list.append(padded_angles_pred[i, :num_sources].cpu().numpy())
                kf_predictions_list.append(kf_predictions_after_update[i, :num_sources])
                kf_covariance_list.append(kf_covariances[i, :num_sources])

                with torch.no_grad():
                    kf_pred_tensor = torch.tensor(
                        kf_predictions_after_update[i, :num_sources], device=DEVICE
                    ).unsqueeze(0)
                    truth_tensor = step_angles[i, :num_sources].unsqueeze(0)
                    kf_rmspe = rmspe_criterion(kf_pred_tensor, truth_tensor).item()
                    kf_rmspe_list.append(kf_rmspe)
            else:
                model_predictions_list.append(np.array([]))
                kf_predictions_list.append(np.array([]))
                kf_covariance_list.append(np.array([]))
                kf_rmspe_list.append(0.0)

        return (
            model_predictions_list,
            kf_predictions_list,
            total_loss,
            float(np.sum(kf_rmspe_list)),
            kf_covariance_list,
        )

    def _save_results(self) -> None:
        """Save simulation results to output dir."""
        logger.info("Saving results to %s", self.output_dir)
        # Placeholder for results persistence implementation.
