from ast import Not
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
import logging
import numpy as np
import torch
import torch.optim as optim
from tqdm import tqdm
import datetime
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import time
import copy
import yaml
from itertools import permutations
import itertools
from dataclasses import dataclass
from typing import Optional, List, Union, Dict, Any

from config.schema import Config
from src.data_module.trajectory import TrajectoryDataHandler, create_online_learning_dataset
from src.trainer_module.training import Trainer, TrainingConfig, TrajectoryTrainer, OnlineTrainer
from src.eval_module.evaluation import Evaluator
from src.utils.plotting import plot_online_learning_results, plot_online_learning_trajectory
from src.utils.utils import log_window_summary, save_model_state, log_online_learning_window_summary
from simulation.kalman_filter import KalmanFilter1D, BatchKalmanFilter1D, BatchExtendedKalmanFilter1D
from src.eval_module.metrics.rmspe_loss import RMSPELoss
from src.eval_module.metrics.rmape_loss import RMAPELoss
from src.eval_module.metrics.multimoment_innovation_consistency_loss import MultiMomentInnovationConsistencyLoss
from DCD_MUSIC.src.signal_creation import Samples
from DCD_MUSIC.src.evaluation import get_model_based_method, evaluate_model_based
from simulation.kalman_filter.extended import ExtendedKalmanFilter1D
from src.trainer_module.sandbox import glrt_changepoint_detection, plot_results


class KalmanInnovationLoss:
    """
    Loss function for Kalman gain times innovation.
    
    This loss encourages the model to produce predictions that result in
    smaller Kalman gain times innovation values, which indicates better
    measurement quality and filter performance.
    """
    
    def __init__(self):
        """Initialize the Kalman Innovation Loss."""
        pass
    
    def __call__(self, kalman_gain_times_innovation: torch.Tensor) -> torch.Tensor:
        """
        Calculate the absolute value of Kalman gain times innovation.
        
        Args:
            kalman_gain_times_innovation: Tensor of K*y values from EKF
            
        Returns:
            Loss tensor (absolute value of K*y)
        """
        return torch.abs(kalman_gain_times_innovation)


class YSInvYLoss:
    """
    Loss function for y*S^-1*y metric.
    
    This loss encourages the model to produce predictions that result in
    smaller y*S^-1*y values, which indicates better measurement quality
    and filter performance in terms of normalized innovation squared.
    """
    
    def __init__(self):
        """Initialize the Y*S^-1*Y Loss."""
        pass
    
    def __call__(self, y_s_inv_y: torch.Tensor) -> torch.Tensor:
        """
        Calculate the absolute value of y*S^-1*y.
        
        Args:
            y_s_inv_y: Tensor of y*S^-1*y values from EKF
            
        Returns:
            Loss tensor (absolute value of y*S^-1*y)
        """
        return torch.abs(y_s_inv_y)


logger = logging.getLogger(__name__)

# Device setup for evaluation
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@dataclass
class StepMetrics:
    """Encapsulates step-level metrics for a window evaluation."""
    covariances: torch.Tensor  # Shape: [window_size, max_sources]
    innovations: torch.Tensor  # Shape: [window_size, max_sources]
    kalman_gains: torch.Tensor  # Shape: [window_size, max_sources]
    kalman_gain_times_innovation: torch.Tensor  # Shape: [window_size, max_sources]
    y_s_inv_y: torch.Tensor  # Shape: [window_size, max_sources]


@dataclass
class DOAMetrics:
    """Encapsulates DOA (Direction of Arrival) prediction metrics for a window evaluation."""
    ekf_predictions: torch.Tensor  # Shape: [window_size, max_sources] - EKF angle predictions
    pre_ekf_predictions: torch.Tensor  # Shape: [window_size, max_sources] - Pre-EKF angle predictions
    true_angles: torch.Tensor  # Shape: [window_size, max_sources] - Ground truth angles
    avg_ekf_angle_pred: List[float] = None  # Averaged EKF angle predictions per source
    avg_pre_ekf_angle_pred: List[float] = None  # Averaged pre-EKF angle predictions per source


@dataclass
class LossMetrics:
    """Encapsulates all loss-related metrics for a window evaluation."""
    main_loss: float              # Primary loss (uses supervision + metric)
    main_loss_db: float           # Primary loss in dB units (20 * log10(main_loss))
    main_loss_config: str         # Configuration string for main loss (e.g., "supervised_rmspe")
    online_training_reference_loss: float  # Training reference loss (uses training_loss_type)
    online_training_reference_loss_config: str  # Configuration string for training reference loss (e.g., "multimoment")
    pre_ekf_loss: float          # Raw model performance
    ekf_gain_rmspe: float        # EKF improvement (RMSPE)
    ekf_gain_rmape: float        # EKF improvement (RMAPE)
    


@dataclass
class WindowMetrics:
    """Encapsulates window-level metrics and state."""
    window_size: int
    num_sources: int
    avg_covariance: float  # Average covariance across all sources and steps
    eta_value: float  # Current eta value from system model
    is_near_field: bool  # Whether processing near-field or far-field
    # Averaged metrics across time steps
    avg_ekf_angle_pred: List[float] = None  # Averaged EKF angle predictions per source
    avg_pre_ekf_angle_pred: List[float] = None  # Averaged pre-EKF angle predictions per source
    avg_ekf_covariances: List[float] = None  # Averaged EKF covariances per source
    avg_ekf_innovations: List[float] = None  # Averaged EKF innovations per source
    avg_ekf_kalman_gains: List[float] = None  # Averaged EKF Kalman gains per source
    avg_ekf_kalman_gain_times_innovation: List[float] = None  # Averaged EKF Kalman gain times innovation per source
    avg_ekf_y_s_inv_y: List[float] = None  # Averaged EKF y_s_inv_y per source
    avg_step_innovation_covariances: List[float] = None  # Averaged step innovation covariances per source


@dataclass
class TrajectoryResults:
    """Encapsulates all results for a single trajectory using structured approach."""
    # Window-level results
    window_results: List['WindowEvaluationResult']
    
    # Basic trajectory tracking
    window_indices: List[int]
    window_eta_values: List[float]
    
    # Labels
    window_labels: List[List[np.ndarray]]
    
    def __init__(self):
        # Initialize all lists
        self.window_results = []
        self.window_indices = []
        self.window_eta_values = []
        self.window_labels = []
    
    def add_window_result(self, window_idx: int, window_result: 'WindowEvaluationResult', eta_value: float, labels: List[np.ndarray]):
        """Add a window result to the trajectory results."""
        self.window_results.append(window_result)
        self.window_indices.append(window_idx)
        self.window_eta_values.append(eta_value)
        self.window_labels.append(labels)


@dataclass
class WindowEvaluationResult:
    """Main return type for window evaluation containing all metrics and data."""
    # Core metrics
    loss_metrics: LossMetrics
    window_metrics: WindowMetrics
    step_metrics: StepMetrics
    doa_metrics: DOAMetrics
    
    
    # Success indicators
    is_valid: bool = True
    error_message: Optional[str] = None
    
    def to_tuple(self) -> Tuple:
        """Convert to the original tuple format for backward compatibility."""
        return (
            self.loss_metrics.main_loss,
            self.window_metrics.avg_covariance,
            self.doa_metrics.ekf_predictions,
            self.step_metrics.covariances,
            self.loss_metrics.pre_ekf_loss,
            self.step_metrics.innovations,
            self.step_metrics.kalman_gains,
            self.step_metrics.kalman_gain_times_innovation,
            self.step_metrics.y_s_inv_y,
            self.loss_metrics.ekf_gain_rmspe,
            self.doa_metrics.pre_ekf_predictions,
            self.loss_metrics.ekf_gain_rmape,
            self.window_metrics.avg_ekf_angle_pred,
            self.window_metrics.avg_pre_ekf_angle_pred
        )
    
    @classmethod
    def create_error_result(cls, error_message: str) -> 'WindowEvaluationResult':
        """Create an error result with default values."""
        return cls(
            loss_metrics=LossMetrics(
                main_loss=float('inf'),
                main_loss_db=float('inf'),
                main_loss_config="error",
                online_training_reference_loss=float('inf'),
                online_training_reference_loss_config="error",
                pre_ekf_loss=float('inf'),
                ekf_gain_rmspe=0.0,
                ekf_gain_rmape=0.0
            ),
            window_metrics=WindowMetrics(
                window_size=0,
                num_sources=0,
                avg_covariance=float('nan'),
                eta_value=0.0,
                is_near_field=False,
                avg_ekf_angle_pred=[],
                avg_pre_ekf_angle_pred=[],
                avg_ekf_covariances=[],
                avg_ekf_innovations=[],
                avg_ekf_kalman_gains=[],
                avg_ekf_kalman_gain_times_innovation=[],
                avg_ekf_y_s_inv_y=[],
                avg_step_innovation_covariances=[]
            ),
            step_metrics=StepMetrics(
                covariances=torch.empty(0, 0, dtype=torch.float64),
                innovations=torch.empty(0, 0, dtype=torch.float64),
                kalman_gains=torch.empty(0, 0, dtype=torch.float64),
                kalman_gain_times_innovation=torch.empty(0, 0, dtype=torch.float64),
                y_s_inv_y=torch.empty(0, 0, dtype=torch.float64)
            ),
            doa_metrics=DOAMetrics(
                ekf_predictions=torch.empty(0, 0, dtype=torch.float64),
                pre_ekf_predictions=torch.empty(0, 0, dtype=torch.float64),
                true_angles=torch.empty(0, 0, dtype=torch.float64),
                avg_ekf_angle_pred=[],
                avg_pre_ekf_angle_pred=[]
            ),
            is_valid=False,
            error_message=error_message
        )


class OnlineLearning:
    """
    Handles all online learning functionality for the simulation.
    
    This class encapsulates the online learning pipeline including:
    - Multi-trajectory online learning
    - EKF-based state estimation
    - Dynamic eta updates
    - Results plotting and analysis
    """
    
    def __init__(self, config: Config, system_model, trained_model, output_dir: Path, results: Dict[str, Any]):
        """
        Initialize the OnlineLearning handler.
        
        Args:
            config: Configuration object
            system_model: System model instance
            trained_model: Trained neural network model
            output_dir: Directory for saving results
            results: Results dictionary to store outputs
        """
        self.config = config
        self.system_model = system_model
        self.trained_model = trained_model
        self.output_dir = output_dir
        self.results = results
        print(self.system_model.params.snr)
        # Dual model online learning state variables
        self.drift_detected = False
        self.learning_done = False
        self.online_model = None
        self.online_training_count = 0
        self.first_eta_change = True  # Track if this is the first eta change
        self.learning_start_window = None  # Track when learning started
        self.training_window_indices = []  # Track which windows were used for training
        
        # Get time_to_learn from configuration
        online_config = self.config.online_learning
        self.time_to_learn = getattr(online_config, 'time_to_learn', None)
        if self.time_to_learn is None:
            logger.warning("time_to_learn not specified in config, online learning will not start automatically")
        else:
            logger.info(f"Online learning will start at window {self.time_to_learn}")
        
        logger.info("OnlineLearning handler initialized")
    


    def run_online_learning(self) -> Dict[str, Any]:
        from src.trainer_module.online_learning_parts.pipeline import run_online_learning_impl
        return run_online_learning_impl(self)

    def _create_averaged_trajectory_result(self, averaged_metrics: dict) -> TrajectoryResults:
        from src.trainer_module.online_learning_parts.pipeline import _create_averaged_trajectory_result_impl
        return _create_averaged_trajectory_result_impl(self, averaged_metrics)

    def _run_single_trajectory_online_learning(self, trajectory_idx: int = 0) -> Dict[str, Any]:
        from src.trainer_module.online_learning_parts.pipeline import _run_single_trajectory_online_learning_impl
        return _run_single_trajectory_online_learning_impl(self, trajectory_idx)

    def _online_training_window(self, window_time_series, window_sources_num, window_labels, trajectory_idx: int = 0, window_idx: int = 0, 
                               is_first_window: bool = True, last_ekf_predictions: Optional[torch.Tensor] = None, 
                               last_ekf_covariances: Optional[torch.Tensor] = None, model=None, loss_config_override=None) -> WindowEvaluationResult:
        from src.trainer_module.online_learning_parts.pipeline import _online_training_window_impl
        return _online_training_window_impl(self, window_time_series, window_sources_num, window_labels, trajectory_idx, window_idx, is_first_window, last_ekf_predictions, last_ekf_covariances, model, loss_config_override)

    def _check_gradients(self, model, step: int, gd_step: int) -> bool:
        from src.trainer_module.online_learning_parts.step_processor import _check_gradients_impl
        return _check_gradients_impl(self, model, step, gd_step)

    def _validate_inputs(self, window_time_series: torch.Tensor, window_sources_num: List[int], 
                        window_labels: List[np.ndarray]) -> Tuple[int, str]:
        from src.trainer_module.online_learning_parts.step_processor import _validate_inputs_impl
        return _validate_inputs_impl(self, window_time_series, window_sources_num, window_labels)

    def _initialize_ekf_filters(self, max_sources: int, window_idx: int = 0, step_idx: int = 0) -> List[ExtendedKalmanFilter1D]:
        from src.trainer_module.online_learning_parts.step_processor import _initialize_ekf_filters_impl
        return _initialize_ekf_filters_impl(self, max_sources, window_idx, step_idx)

    def _initialize_ekf_state(self, step: int, num_sources_this_step: int, true_angles_this_step: np.ndarray,
                            ekf_filters: List[ExtendedKalmanFilter1D], is_first_window: bool,
                            last_ekf_predictions: Optional[List], last_ekf_covariances: Optional[List]) -> None:
        from src.trainer_module.online_learning_parts.step_processor import _initialize_ekf_state_impl
        return _initialize_ekf_state_impl(self, step, num_sources_this_step, true_angles_this_step, ekf_filters, is_first_window, last_ekf_predictions, last_ekf_covariances)

    def _process_single_step(self, step: int, time_series_steps: torch.Tensor, sources_num_per_step: List[int],
                           labels_per_step_list: List[np.ndarray], ekf_filters: List[ExtendedKalmanFilter1D],
                           model, is_near_field: bool, Pretrained_model: bool) -> Tuple[bool, Dict]:
        from src.trainer_module.online_learning_parts.step_processor import _process_single_step_impl
        return _process_single_step_impl(self, step, time_series_steps, sources_num_per_step, labels_per_step_list, ekf_filters, model, is_near_field, Pretrained_model)

    def _calculate_metrics(self, step_results_list: List[Dict], current_window_len: int, 
                          max_sources: int, current_eta: float, is_near_field: bool, 
                          loss_config=None) -> WindowEvaluationResult:
        from src.trainer_module.online_learning_parts.metrics import _calculate_metrics_impl
        return _calculate_metrics_impl(self, step_results_list, current_window_len, max_sources, current_eta, is_near_field, loss_config)

    def _evaluate_window(self, window_time_series, window_sources_num, window_labels, trajectory_idx: int = 0, window_idx: int = 0,
                         is_first_window: bool = True, last_ekf_predictions: List = None, last_ekf_covariances: List = None, model=None) -> WindowEvaluationResult:
        from src.trainer_module.online_learning_parts.step_processor import _evaluate_window_impl
        return _evaluate_window_impl(self, window_time_series, window_sources_num, window_labels, trajectory_idx, window_idx, is_first_window, last_ekf_predictions, last_ekf_covariances, model)

    def _fix_tensor_shape_for_loss(self, tensor: torch.Tensor) -> torch.Tensor:
        from src.trainer_module.online_learning_parts.losses import _fix_tensor_shape_for_loss_impl
        return _fix_tensor_shape_for_loss_impl(self, tensor)

    def _calculate_all_losses(self, pre_ekf_preds: torch.Tensor, ekf_preds: torch.Tensor, 
                            true_angles: torch.Tensor, innovation_covariances: list = None, loss_config=None) -> 'LossMetrics':
        from src.trainer_module.online_learning_parts.losses import _calculate_all_losses_impl
        return _calculate_all_losses_impl(self, pre_ekf_preds, ekf_preds, true_angles, innovation_covariances, loss_config)

    def _calculate_window_training_loss(self, step_results_list: List[Dict], 
                                      loss_config=None, rmspe_criterion=None, rmape_criterion=None) -> torch.Tensor:
        from src.trainer_module.online_learning_parts.losses import _calculate_window_training_loss_impl
        return _calculate_window_training_loss_impl(self, step_results_list, loss_config, rmspe_criterion, rmape_criterion)

    def _get_optimal_permutation(self, predictions: np.ndarray, true_angles: np.ndarray) -> np.ndarray:
        from src.trainer_module.online_learning_parts.losses import _get_optimal_permutation_impl
        return _get_optimal_permutation_impl(self, predictions, true_angles)

    def _get_optimal_permutation_tensor(self, predictions: torch.Tensor, true_angles: torch.Tensor) -> torch.Tensor:
        from src.trainer_module.online_learning_parts.losses import _get_optimal_permutation_tensor_impl
        return _get_optimal_permutation_tensor_impl(self, predictions, true_angles)

    def _average_online_learning_results_across_trajectories(self, results_list):
        from src.trainer_module.online_learning_parts.metrics import _average_online_learning_results_across_trajectories_impl
        return _average_online_learning_results_across_trajectories_impl(self, results_list)
