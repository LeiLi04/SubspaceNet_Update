from __future__ import annotations

from typing import Dict, Any, Optional
import torch
import matplotlib.pyplot as plt

from src.train.online_learning import (
    logger,
    TrajectoryResults,
    WindowEvaluationResult,
    LossMetrics,
    WindowMetrics,
    StepMetrics,
    DOAMetrics,
)


def run_online_learning_impl(self) -> Dict[str, Any]:
    """
    Run online learning pipeline over multiple trajectories and average results.

    This method runs the online learning process over a dataset of trajectories and
    averages the results for more robust analysis.

    Returns:
        Dict containing online learning results.
    """
    logger.info("Starting online learning pipeline")

    try:
        # Check if model is available for online learning
        if self.trained_model is None:
            logger.error("No model available for online learning")
            return {"status": "error", "message": "No model available for online learning"}

        # Get dataset size from config
        online_config = self.config.online_learning
        dataset_size = getattr(online_config, 'dataset_size', 1)

        logger.info(f"Starting online learning over {dataset_size} trajectories")

        all_results = []

        # Run online learning for each trajectory
        for trajectory_idx in range(dataset_size):
            logger.info(f"Processing trajectory {trajectory_idx + 1}/{dataset_size}")

            # Reset eta to initial value for each new trajectory
            initial_eta = 0
            logger.info(f"Resetting eta to initial value {initial_eta:.4f} for trajectory {trajectory_idx + 1}")
            self.system_model.params.eta = initial_eta

            # Reset model eta/noise if helpers are available in this DCD_MUSIC version.
            if hasattr(self.system_model, "_SystemModel__set_eta"):
                self.system_model.eta = self.system_model._SystemModel__set_eta()
            else:
                self.system_model.eta = initial_eta
            if (not getattr(self.system_model.params, 'nominal', True)) and hasattr(self.system_model, "get_distance_noise"):
                self.system_model.location_noise = self.system_model.get_distance_noise(True)

            # Run single trajectory online learning
            trajectory_result = self._run_single_trajectory_online_learning(trajectory_idx)


            if trajectory_result.get("status") == "error":
                logger.error(f"Error in trajectory {trajectory_idx + 1}: {trajectory_result.get('message')}")
                continue

            all_results.append(trajectory_result)

        if not all_results:
            logger.error("No successful trajectory results")
            self.results["online_learning_error"] = "No successful trajectory results"
            return {"status": "error", "message": "No successful trajectory results"}

        # Average results across all trajectories using the new utility method
        from src.utils.utils import average_online_learning_results_across_trajectories
        averaged_results_across_trajectories = average_online_learning_results_across_trajectories(all_results)

        # Store averaged results
        if averaged_results_across_trajectories.get("status") == "success":
            self.results["online_learning_averaged"] = averaged_results_across_trajectories["averaged_results"]
            logger.info(f"Successfully averaged results across {averaged_results_across_trajectories['averaged_results']['trajectory_count']} trajectories")
        else:
            logger.warning(f"Failed to average trajectory results: {averaged_results_across_trajectories.get('message')}")


        # Use structured plotting approach with AVERAGED results
        from src.utils.plotting import plot_online_learning_results_structured

        # Extract individual trajectory results for the old plotting method (will be removed later)
        pretrained_trajectory_results = [result["online_learning_results"]["pretrained_model_trajectory_results"] for result in all_results]
        online_trajectory_results = [result["online_learning_results"]["online_model_trajectory_results"] for result in all_results]

        # Get loss configurations from the first result
        if all_results and all_results[0]["online_learning_results"]["pretrained_model_trajectory_results"].window_results:
            first_window_result = all_results[0]["online_learning_results"]["pretrained_model_trajectory_results"].window_results[0]
            main_loss_config = first_window_result.loss_metrics.main_loss_config
            training_reference_loss_config = first_window_result.loss_metrics.online_training_reference_loss_config
        else:
            main_loss_config = "unknown"
            training_reference_loss_config = "unknown"

        # Get training and eta change info from results
        training_start_window = None
        training_end_window = None
        eta_change_windows = []
        if all_results and len(all_results) > 0:
            # Get training info from first trajectory result
            first_result = all_results[0]["online_learning_results"]
            training_start_window = first_result.get("training_start_window")
            training_end_window = first_result.get("training_end_window")
            eta_change_windows = first_result.get("eta_change_windows", [])

        #plot_online_learning_results_structured(
        #    self.output_dir,
        #    pretrained_trajectory_results,
        #    online_trajectory_results,
        #    main_loss_config,
        #    training_reference_loss_config,
        #    training_start_window,
        #    training_end_window,
        #    eta_change_windows
        #)

        # ALSO call the new direct averaged plotting function
        if averaged_results_across_trajectories.get("status") == "success":
            from src.utils.plotting import plot_averaged_online_learning_results

            averaged_data = averaged_results_across_trajectories["averaged_results"]
            plot_averaged_online_learning_results(
                self.output_dir,
                averaged_data["averaged_pretrained_trajectory"],
                averaged_data["averaged_online_trajectory"],
                main_loss_config,
                training_reference_loss_config,
                training_start_window,
                training_end_window,
                eta_change_windows,
                averaged_data.get("averaged_supervised_trajectory")
            )

        # GLRT drift detection averaged plotting (using results from averaging function)
        glrt_results = averaged_results_across_trajectories.get("averaged_results", {}).get("glrt_results", {})

        # Plot reference loss GLRT results
        if "ref_loss" in glrt_results:
            ref_data = glrt_results["ref_loss"]
            avg_ref_losses = ref_data["avg_losses"]
            min_segment_size = ref_data["min_segment_size"]

            if len(avg_ref_losses) >= 2 * min_segment_size + 1:
                try:
                    ref_changepoint, ref_log_glr, ref_all_log_glr, ref_candidate_points = glrt_changepoint_detection(
                        avg_ref_losses, min_segment_size=min_segment_size
                    )
                    ref_fig = plot_results(avg_ref_losses, ref_changepoint, ref_all_log_glr, ref_candidate_points)
                    title = f'GLRT Drift Detection - Reference Loss (Averaged across {ref_data["trajectory_count"]} trajectories)'
                    if ref_data["avg_changepoint_window"] is not None:
                        title += f'\nAvg Changepoint Window: {ref_data["avg_changepoint_window"]:.2f} ± {ref_data["std_changepoint_window"]:.2f}, Avg Log-GLR: {ref_data["avg_likelihood"]:.4f} ± {ref_data["std_likelihood"]:.4f}'
                    ref_fig.suptitle(title, fontsize=14)
                    ref_plot_path = self.output_dir / "glrt_ref_loss_averaged.png"
                    ref_fig.savefig(ref_plot_path, dpi=300, bbox_inches='tight')
                    plt.close(ref_fig)
                    logger.info(f"Saved averaged GLRT reference loss plot to {ref_plot_path}")
                    logger.info(f"Reference Loss GLRT: Avg Changepoint = {ref_data['avg_changepoint_window']:.2f} ± {ref_data['std_changepoint_window']:.2f}, "
                               f"Avg Log-GLR = {ref_data['avg_likelihood']:.4f} ± {ref_data['std_likelihood']:.4f}")
                except Exception as e:
                    logger.warning(f"Failed to plot averaged GLRT reference loss results: {e}")

        # Plot main loss GLRT results
        if "main_loss" in glrt_results:
            main_data = glrt_results["main_loss"]
            avg_main_losses = main_data["avg_losses"]
            min_segment_size = main_data["min_segment_size"]

            if len(avg_main_losses) >= 2 * min_segment_size + 1:
                try:
                    main_changepoint, main_log_glr, main_all_log_glr, main_candidate_points = glrt_changepoint_detection(
                        avg_main_losses, min_segment_size=min_segment_size
                    )
                    main_fig = plot_results(avg_main_losses, main_changepoint, main_all_log_glr, main_candidate_points)
                    title = f'GLRT Drift Detection - Main Loss (Averaged across {main_data["trajectory_count"]} trajectories)'
                    if main_data["avg_changepoint_window"] is not None:
                        title += f'\nAvg Changepoint Window: {main_data["avg_changepoint_window"]:.2f} ± {main_data["std_changepoint_window"]:.2f}, Avg Log-GLR: {main_data["avg_likelihood"]:.4f} ± {main_data["std_likelihood"]:.4f}'
                    main_fig.suptitle(title, fontsize=14)
                    main_plot_path = self.output_dir / "glrt_main_loss_averaged.png"
                    main_fig.savefig(main_plot_path, dpi=300, bbox_inches='tight')
                    plt.close(main_fig)
                    logger.info(f"Saved averaged GLRT main loss plot to {main_plot_path}")
                    logger.info(f"Main Loss GLRT: Avg Changepoint = {main_data['avg_changepoint_window']:.2f} ± {main_data['std_changepoint_window']:.2f}, "
                               f"Avg Log-GLR = {main_data['avg_likelihood']:.4f} ± {main_data['std_likelihood']:.4f}")
                except Exception as e:
                    logger.warning(f"Failed to plot averaged GLRT main loss results: {e}")

        # Calculate summary statistics from structured results
        total_drift_detected = sum(result["online_learning_results"].get("drift_detected_count", 0) for result in all_results)
        total_model_updated = sum(result["online_learning_results"].get("model_updated_count", 0) for result in all_results)
        avg_drift_detected = total_drift_detected / len(all_results) if all_results else 0
        avg_model_updated = total_model_updated / len(all_results) if all_results else 0

        logger.info(f"Online learning completed over {dataset_size} trajectories: "
                   f"{avg_drift_detected:.1f} avg drifts detected, "
                   f"{avg_model_updated:.1f} avg model updates")

        # Prepare return results
        return_results = {
            "status": "success", 
            "online_learning_results": {
                "pretrained_trajectory_results": pretrained_trajectory_results,
                "online_trajectory_results": online_trajectory_results,
                "avg_drift_detected": avg_drift_detected,
                "avg_model_updated": avg_model_updated,
                "dataset_size": dataset_size
            }
        }

        # Add averaged results if available
        if averaged_results_across_trajectories.get("status") == "success":
            return_results["averaged_results"] = averaged_results_across_trajectories["averaged_results"]
            # Also add GLRT results at top level for easy access
            if "glrt_results" in averaged_results_across_trajectories["averaged_results"]:
                return_results["glrt_results"] = averaged_results_across_trajectories["averaged_results"]["glrt_results"]

        return return_results

    except Exception as e:
        logger.exception(f"Error running online learning: {e}")
        self.results["online_learning_error"] = str(e)
        return {"status": "error", "message": str(e), "exception": type(e).__name__}



def _create_averaged_trajectory_result_impl(self, averaged_metrics: dict) -> TrajectoryResults:
    """
    Create a TrajectoryResults object from averaged metrics for plotting.

    Args:
        averaged_metrics: Dictionary containing averaged metrics from utils.average_online_learning_results_across_trajectories

    Returns:
        TrajectoryResults object containing the averaged data
    """
    import torch
    import numpy as np

    # Create a TrajectoryResults object
    trajectory_result = TrajectoryResults()

    # Get the number of windows from the averaged data
    num_windows = len(averaged_metrics.get("main_losses", []))

    # Create window results for each averaged window
    for window_idx in range(num_windows):
        # Create averaged loss metrics
        loss_metrics = LossMetrics(
            main_loss=averaged_metrics["main_losses"][window_idx],
            main_loss_db=averaged_metrics["main_losses_db"][window_idx],
            main_loss_config="averaged_supervised_rmspe",  # Placeholder
            online_training_reference_loss=averaged_metrics["training_reference_losses"][window_idx],
            online_training_reference_loss_config="averaged_multimoment",  # Placeholder
            pre_ekf_loss=averaged_metrics["main_losses"][window_idx] + averaged_metrics["ekf_gain_rmspe"][window_idx],  # Approximate
            ekf_gain_rmspe=averaged_metrics["ekf_gain_rmspe"][window_idx],
            ekf_gain_rmape=averaged_metrics["ekf_gain_rmape"][window_idx]
        )

        # Create averaged window metrics
        window_metrics = WindowMetrics(
            window_size=10,  # Placeholder
            num_sources=3,   # Placeholder
            avg_covariance=averaged_metrics["avg_covariances"][window_idx],
            eta_value=averaged_metrics["window_eta_values"][window_idx],
            is_near_field=False,  # Placeholder
            avg_ekf_angle_pred=None,  # Not averaged (meaningless)
            avg_pre_ekf_angle_pred=None,  # Not averaged (meaningless)
            avg_ekf_covariances=None,  # Could add if needed
            avg_ekf_innovations=[averaged_metrics["avg_innovations"][window_idx]] if averaged_metrics["avg_innovations"][window_idx] > 0 else None,
            avg_ekf_kalman_gains=[averaged_metrics["avg_kalman_gains"][window_idx]] if averaged_metrics["avg_kalman_gains"][window_idx] > 0 else None,
            avg_ekf_kalman_gain_times_innovation=[averaged_metrics["avg_kalman_gain_times_innovation"][window_idx]] if averaged_metrics["avg_kalman_gain_times_innovation"][window_idx] > 0 else None,
            avg_ekf_y_s_inv_y=[averaged_metrics["avg_y_s_inv_y"][window_idx]] if averaged_metrics["avg_y_s_inv_y"][window_idx] > 0 else None,
            avg_step_innovation_covariances=None
        )

        # Create placeholder step metrics (not used in structured plotting)
        step_metrics = StepMetrics(
            covariances=torch.zeros(1, 3),  # Placeholder
            innovations=torch.zeros(1, 3),  # Placeholder
            kalman_gains=torch.zeros(1, 3),  # Placeholder
            kalman_gain_times_innovation=torch.zeros(1, 3),  # Placeholder
            y_s_inv_y=torch.zeros(1, 3)  # Placeholder
        )

        # Create placeholder DOA metrics (not used in structured plotting)
        doa_metrics = DOAMetrics(
            ekf_predictions=torch.zeros(1, 3),  # Placeholder
            pre_ekf_predictions=torch.zeros(1, 3),  # Placeholder
            true_angles=torch.zeros(1, 3),  # Placeholder
            avg_ekf_angle_pred=None,  # Not meaningful for averaged data
            avg_pre_ekf_angle_pred=None  # Not meaningful for averaged data
        )

        # Create window evaluation result
        window_result = WindowEvaluationResult(
            loss_metrics=loss_metrics,
            window_metrics=window_metrics,
            step_metrics=step_metrics,
            doa_metrics=doa_metrics,
            is_valid=True,
            error_message=None
        )

        # Add to trajectory results
        trajectory_result.add_window_result(
            window_idx=averaged_metrics["window_indices"][window_idx],
            window_result=window_result,
            eta_value=averaged_metrics["window_eta_values"][window_idx],
            labels=[]  # Empty labels for averaged data
        )

    return trajectory_result




def _run_single_trajectory_online_learning_impl(self, trajectory_idx: int = 0) -> Dict[str, Any]:
    from src.train.online_learning_parts.pipeline_run import _run_single_trajectory_online_learning_impl as impl
    return impl(self, trajectory_idx)


def _online_training_window_impl(self, window_time_series, window_sources_num, window_labels, trajectory_idx: int = 0, window_idx: int = 0,
                               is_first_window: bool = True, last_ekf_predictions: Optional[torch.Tensor] = None,
                               last_ekf_covariances: Optional[torch.Tensor] = None, model=None, loss_config_override=None) -> WindowEvaluationResult:
    from src.train.online_learning_parts.pipeline_train import _online_training_window_impl as impl
    return impl(self, window_time_series, window_sources_num, window_labels, trajectory_idx, window_idx, is_first_window, last_ekf_predictions, last_ekf_covariances, model, loss_config_override)
