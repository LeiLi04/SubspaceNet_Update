from __future__ import annotations

import numpy as np

def _average_online_learning_results_across_trajectories_impl(self, results_list):
    """
    Average results across multiple trajectories.

    Args:
        results_list: List of dictionaries containing results from each trajectory

    Returns:
        Dictionary with averaged results
    """
    # Initialize lists to store results from all trajectories
    all_window_losses = []
    all_window_covariances = []
    all_window_eta_values = []
    all_window_updates = []
    all_drift_detected = []
    all_model_updated = []
    all_window_count = []
    all_window_size = []
    all_stride = []
    all_loss_threshold = []
    all_ekf_predictions = []
    all_ekf_covariances = []
    all_ekf_innovations = []  # New list for innovations
    all_ekf_kalman_gains = []  # New list for Kalman gains
    all_ekf_kalman_gain_times_innovation = []  # New list for K*y
    all_ekf_y_s_inv_y = []  # New list for y*(S^-1)*y
    all_pre_ekf_losses = []
    all_window_labels = []
    all_window_pre_ekf_angles_pred = []

    # Online learning data
    all_online_window_losses = []
    all_online_window_covariances = []
    all_online_pre_ekf_losses = []
    all_online_ekf_predictions = []
    all_online_ekf_covariances = []
    all_online_ekf_innovations = []
    all_online_ekf_kalman_gains = []
    all_online_ekf_kalman_gain_times_innovation = []
    all_online_ekf_y_s_inv_y = []
    all_online_window_indices = []
    all_online_pre_ekf_angles_pred = []

    # Training data
    all_training_window_losses = []
    all_training_window_covariances = []
    all_training_pre_ekf_losses = []
    all_training_ekf_predictions = []
    all_training_ekf_covariances = []
    all_training_ekf_innovations = []
    all_training_ekf_kalman_gains = []
    all_training_ekf_kalman_gain_times_innovation = []
    all_training_ekf_y_s_inv_y = []
    all_training_window_indices = []
    all_learning_start_windows = []
    all_training_pre_ekf_angles_pred = []

    # Collect results from each trajectory
    for result in results_list:
        all_window_losses.append(result["window_losses"])
        all_window_covariances.append(result["window_covariances"])
        all_window_eta_values.append(result["window_eta_values"])
        all_window_updates.append(result["window_updates"])
        all_drift_detected.append(result["drift_detected_count"])
        all_model_updated.append(result["model_updated_count"])
        all_window_count.append(result["window_count"])
        all_window_size.append(result["window_size"])
        all_stride.append(result["stride"])
        all_loss_threshold.append(result["loss_threshold"])
        all_ekf_predictions.append(result["ekf_predictions"])
        all_ekf_covariances.append(result["ekf_covariances"])
        all_ekf_innovations.append(result["ekf_innovations"])  # Collect innovations
        all_ekf_kalman_gains.append(result["ekf_kalman_gains"])
        all_ekf_kalman_gain_times_innovation.append(result["ekf_kalman_gain_times_innovation"])
        all_ekf_y_s_inv_y.append(result["ekf_y_s_inv_y"])  # Collect y*(S^-1)*y
        all_pre_ekf_losses.append(result["pre_ekf_losses"])
        all_window_labels.append(result["window_labels"])

        # Collect pre-EKF angle predictions for static model
        if "window_pre_ekf_angles_pred" in result:
            all_window_pre_ekf_angles_pred.append(result["window_pre_ekf_angles_pred"])
        else:
            all_window_pre_ekf_angles_pred.append([])

        # Collect online learning results if available
        if "online_window_losses" in result and len(result["online_window_losses"]) > 0:
            all_online_window_losses.append(result["online_window_losses"])
            all_online_window_covariances.append(result["online_window_covariances"])
            all_online_pre_ekf_losses.append(result["online_pre_ekf_losses"])
            all_online_ekf_predictions.append(result["online_ekf_predictions"])
            all_online_ekf_covariances.append(result["online_ekf_covariances"])
            all_online_ekf_innovations.append(result["online_ekf_innovations"])
            all_online_ekf_kalman_gains.append(result["online_ekf_kalman_gains"])
            all_online_ekf_kalman_gain_times_innovation.append(result["online_ekf_kalman_gain_times_innovation"])
            all_online_ekf_y_s_inv_y.append(result["online_ekf_y_s_inv_y"])
            all_online_window_indices.append(result["online_window_indices"])

            # Collect online pre-EKF angle predictions if available
            if "online_pre_ekf_angles_pred" in result:
                all_online_pre_ekf_angles_pred.append(result["online_pre_ekf_angles_pred"])
            else:
                all_online_pre_ekf_angles_pred.append([])
        else:
            # Add empty lists if no online learning data
            all_online_window_losses.append([])
            all_online_window_covariances.append([])
            all_online_pre_ekf_losses.append([])
            all_online_ekf_predictions.append([])
            all_online_ekf_covariances.append([])
            all_online_ekf_innovations.append([])
            all_online_ekf_kalman_gains.append([])
            all_online_ekf_kalman_gain_times_innovation.append([])
            all_online_ekf_y_s_inv_y.append([])
            all_online_window_indices.append([])
            all_online_pre_ekf_angles_pred.append([])

        # Collect training data if available
        if "training_window_losses" in result and len(result["training_window_losses"]) > 0:
            all_training_window_losses.append(result["training_window_losses"])
            all_training_window_covariances.append(result["training_window_covariances"])
            all_training_pre_ekf_losses.append(result["training_pre_ekf_losses"])
            all_training_ekf_predictions.append(result["training_ekf_predictions"])
            all_training_ekf_covariances.append(result["training_ekf_covariances"])
            all_training_ekf_innovations.append(result["training_ekf_innovations"])
            all_training_ekf_kalman_gains.append(result["training_ekf_kalman_gains"])
            all_training_ekf_kalman_gain_times_innovation.append(result["training_ekf_kalman_gain_times_innovation"])
            all_training_ekf_y_s_inv_y.append(result["training_ekf_y_s_inv_y"])
            all_training_window_indices.append(result["training_window_indices"])
            all_learning_start_windows.append(result["learning_start_window"])

            # Collect training pre-EKF angle predictions if available
            if "training_pre_ekf_angles_pred" in result:
                all_training_pre_ekf_angles_pred.append(result["training_pre_ekf_angles_pred"])
            else:
                all_training_pre_ekf_angles_pred.append([])
        else:
            # Add empty lists if no training data
            all_training_window_losses.append([])
            all_training_window_covariances.append([])
            all_training_pre_ekf_losses.append([])
            all_training_ekf_predictions.append([])
            all_training_ekf_covariances.append([])
            all_training_ekf_innovations.append([])
            all_training_ekf_kalman_gains.append([])
            all_training_ekf_kalman_gain_times_innovation.append([])
            all_training_ekf_y_s_inv_y.append([])
            all_training_window_indices.append([])
            all_learning_start_windows.append(None)
            all_training_pre_ekf_angles_pred.append([])

    # Average numerical results
    avg_window_losses = np.mean(all_window_losses, axis=0)
    avg_window_covariances = np.mean(all_window_covariances, axis=0)
    avg_window_eta_values = all_window_eta_values[0]  # Should be same for all trajectories
    avg_window_updates = np.mean(all_window_updates, axis=0)
    avg_drift_detected = np.mean(all_drift_detected)
    avg_model_updated = np.mean(all_model_updated)
    avg_pre_ekf_losses = np.mean(all_pre_ekf_losses, axis=0)

    # Average innovations - handle nested structure
    avg_ekf_innovations = []
    for window_idx in range(len(all_ekf_innovations[0])):  # For each window
        window_innovations = []
        for step_idx in range(len(all_ekf_innovations[0][window_idx])):  # For each step
            step_innovations = []
            for source_idx in range(len(all_ekf_innovations[0][window_idx][step_idx])):  # For each source
                innovations = [traj[window_idx][step_idx][source_idx] for traj in all_ekf_innovations]
                step_innovations.append(np.mean(innovations)) # source innovation averaged over all trajectories
            window_innovations.append(step_innovations) # step innovation averaged on all trajectories
        avg_ekf_innovations.append(window_innovations) # window innovation averaged over all trajectories

    # Average Kalman gains - handle nested structure
    avg_ekf_kalman_gains = []
    for window_idx in range(len(all_ekf_kalman_gains[0])):  # For each window
        window_kalman_gains = []
        for step_idx in range(len(all_ekf_kalman_gains[0][window_idx])):  # For each step
            step_kalman_gains = []
            for source_idx in range(len(all_ekf_kalman_gains[0][window_idx][step_idx])):  # For each source
                kalman_gains = [traj[window_idx][step_idx][source_idx] for traj in all_ekf_kalman_gains]
                step_kalman_gains.append(np.mean(kalman_gains))
            window_kalman_gains.append(step_kalman_gains)
        avg_ekf_kalman_gains.append(window_kalman_gains)

    # Average K*y - handle nested structure
    avg_ekf_kalman_gain_times_innovation = []
    for window_idx in range(len(all_ekf_kalman_gain_times_innovation[0])):  # For each window
        window_k_times_y = []
        for step_idx in range(len(all_ekf_kalman_gain_times_innovation[0][window_idx])):  # For each step
            step_k_times_y = []
            for source_idx in range(len(all_ekf_kalman_gain_times_innovation[0][window_idx][step_idx])):  # For each source
                k_times_y = [traj[window_idx][step_idx][source_idx] for traj in all_ekf_kalman_gain_times_innovation]
                step_k_times_y.append(np.mean(k_times_y))
            window_k_times_y.append(step_k_times_y)
        avg_ekf_kalman_gain_times_innovation.append(window_k_times_y)

    # Average y*(S^-1)*y - handle nested structure
    avg_ekf_y_s_inv_y = []
    for window_idx in range(len(all_ekf_y_s_inv_y[0])):  # For each window
        window_y_s_inv_y = []
        for step_idx in range(len(all_ekf_y_s_inv_y[0][window_idx])):  # For each step
            step_y_s_inv_y = []
            for source_idx in range(len(all_ekf_y_s_inv_y[0][window_idx][step_idx])):  # For each source
                y_s_inv_y = [traj[window_idx][step_idx][source_idx] for traj in all_ekf_y_s_inv_y]
                step_y_s_inv_y.append(np.mean(y_s_inv_y))
            window_y_s_inv_y.append(step_y_s_inv_y)
        avg_ekf_y_s_inv_y.append(window_y_s_inv_y)

    # Average online learning results if available
    has_online_data = any(len(online_losses) > 0 for online_losses in all_online_window_losses)
    if has_online_data:
        # Filter out empty trajectories for online learning averaging
        valid_online_trajectories = [i for i, online_losses in enumerate(all_online_window_losses) if len(online_losses) > 0]

        if valid_online_trajectories:
            # Average online window losses
            valid_online_losses = [all_online_window_losses[i] for i in valid_online_trajectories]
            avg_online_window_losses = np.mean(valid_online_losses, axis=0).tolist()

            # Average online window covariances
            valid_online_covs = [all_online_window_covariances[i] for i in valid_online_trajectories]
            avg_online_window_covariances = np.mean(valid_online_covs, axis=0).tolist()

            # Average online pre-EKF losses
            valid_online_pre_ekf = [all_online_pre_ekf_losses[i] for i in valid_online_trajectories]
            avg_online_pre_ekf_losses = np.mean(valid_online_pre_ekf, axis=0).tolist()

            # For nested structures, take the first valid trajectory's data
            first_valid_idx = valid_online_trajectories[0]
            avg_online_ekf_predictions = all_online_ekf_predictions[first_valid_idx]
            avg_online_ekf_covariances = all_online_ekf_covariances[first_valid_idx]
            avg_online_ekf_innovations = all_online_ekf_innovations[first_valid_idx]
            avg_online_ekf_kalman_gains = all_online_ekf_kalman_gains[first_valid_idx]
            avg_online_ekf_kalman_gain_times_innovation = all_online_ekf_kalman_gain_times_innovation[first_valid_idx]
            avg_online_ekf_y_s_inv_y = all_online_ekf_y_s_inv_y[first_valid_idx]
            avg_online_window_indices = all_online_window_indices[first_valid_idx]
            avg_online_pre_ekf_angles_pred = all_online_pre_ekf_angles_pred[first_valid_idx]
        else:
            # No valid online data
            avg_online_window_losses = []
            avg_online_window_covariances = []
            avg_online_pre_ekf_losses = []
            avg_online_ekf_predictions = []
            avg_online_ekf_covariances = []
            avg_online_ekf_innovations = []
            avg_online_ekf_kalman_gains = []
            avg_online_ekf_kalman_gain_times_innovation = []
            avg_online_ekf_y_s_inv_y = []
            avg_online_window_indices = []
            avg_online_pre_ekf_angles_pred = []
    else:
        # No online data at all
        avg_online_window_losses = []
        avg_online_window_covariances = []
        avg_online_pre_ekf_losses = []
        avg_online_ekf_predictions = []
        avg_online_ekf_covariances = []
        avg_online_ekf_innovations = []
        avg_online_ekf_kalman_gains = []
        avg_online_ekf_kalman_gain_times_innovation = []
        avg_online_ekf_y_s_inv_y = []
        avg_online_window_indices = []
        avg_online_pre_ekf_angles_pred = []

    # Average training data if available
    has_training_data = any(len(training_losses) > 0 for training_losses in all_training_window_losses)
    if has_training_data:
        # Filter out empty trajectories for training data averaging
        valid_training_trajectories = [i for i, training_losses in enumerate(all_training_window_losses) if len(training_losses) > 0]

        if valid_training_trajectories:
            # Average training window losses
            valid_training_losses = [all_training_window_losses[i] for i in valid_training_trajectories]
            avg_training_window_losses = np.mean(valid_training_losses, axis=0).tolist()

            # Average training window covariances
            valid_training_covs = [all_training_window_covariances[i] for i in valid_training_trajectories]
            avg_training_window_covariances = np.mean(valid_training_covs, axis=0).tolist()

            # Average training pre-EKF losses
            valid_training_pre_ekf = [all_training_pre_ekf_losses[i] for i in valid_training_trajectories]
            avg_training_pre_ekf_losses = np.mean(valid_training_pre_ekf, axis=0).tolist()

            # For nested structures, take the first valid trajectory's data
            first_valid_idx = valid_training_trajectories[0]
            avg_training_ekf_predictions = all_training_ekf_predictions[first_valid_idx]
            avg_training_ekf_covariances = all_training_ekf_covariances[first_valid_idx]
            avg_training_ekf_innovations = all_training_ekf_innovations[first_valid_idx]
            avg_training_ekf_kalman_gains = all_training_ekf_kalman_gains[first_valid_idx]
            avg_training_ekf_kalman_gain_times_innovation = all_training_ekf_kalman_gain_times_innovation[first_valid_idx]
            avg_training_ekf_y_s_inv_y = all_training_ekf_y_s_inv_y[first_valid_idx]
            avg_training_window_indices = all_training_window_indices[first_valid_idx]
            avg_learning_start_window = all_learning_start_windows[first_valid_idx]
            avg_training_pre_ekf_angles_pred = all_training_pre_ekf_angles_pred[first_valid_idx]
        else:
            # No valid training data
            avg_training_window_losses = []
            avg_training_window_covariances = []
            avg_training_pre_ekf_losses = []
            avg_training_ekf_predictions = []
            avg_training_ekf_covariances = []
            avg_training_ekf_innovations = []
            avg_training_ekf_kalman_gains = []
            avg_training_ekf_kalman_gain_times_innovation = []
            avg_training_ekf_y_s_inv_y = []
            avg_training_window_indices = []
            avg_learning_start_window = None
            avg_training_pre_ekf_angles_pred = []
    else:
        # No training data at all
        avg_training_window_losses = []
        avg_training_window_covariances = []
        avg_training_pre_ekf_losses = []
        avg_training_ekf_predictions = []
        avg_training_ekf_covariances = []
        avg_training_ekf_innovations = []
        avg_training_ekf_kalman_gains = []
        avg_training_ekf_kalman_gain_times_innovation = []
        avg_training_ekf_y_s_inv_y = []
        avg_training_window_indices = []
        avg_learning_start_window = None
        avg_training_pre_ekf_angles_pred = []

    return {
        "window_losses": avg_window_losses.tolist(),
        "window_covariances": avg_window_covariances.tolist(),
        "window_eta_values": avg_window_eta_values,
        "window_updates": avg_window_updates.tolist(),
        "drift_detected_count": float(avg_drift_detected),
        "model_updated_count": float(avg_model_updated),
        "window_count": all_window_count[0],  # Should be same for all trajectories
        "window_size": all_window_size[0],    # Should be same for all trajectories
        "stride": all_stride[0],              # Should be same for all trajectories
        "loss_threshold": all_loss_threshold[0],  # Should be same for all trajectories
        "ekf_predictions": all_ekf_predictions[0],  # Take first trajectory's predictions
        "ekf_covariances": all_ekf_covariances[0],  # Take first trajectory's covariances
        "ekf_innovations": avg_ekf_innovations,  # Add averaged innovations
        "ekf_kalman_gains": avg_ekf_kalman_gains,  # Add averaged Kalman gains
        "ekf_kalman_gain_times_innovation": avg_ekf_kalman_gain_times_innovation,  # Add averaged K*y
        "ekf_y_s_inv_y": avg_ekf_y_s_inv_y,  # Add averaged y*(S^-1)*y
        "pre_ekf_losses": avg_pre_ekf_losses.tolist(),
        "window_labels": all_window_labels[0],  # Take first trajectory's labels
        "window_pre_ekf_angles_pred": all_window_pre_ekf_angles_pred[0] if all_window_pre_ekf_angles_pred else [],  # Take first trajectory's pre-EKF angle predictions
        "window_avg_ekf_angle_pred": results_list[0].get("window_avg_ekf_angle_pred", []) if results_list else [],  # Take first trajectory's averaged EKF angle predictions
        "window_avg_pre_ekf_angle_pred": results_list[0].get("window_avg_pre_ekf_angle_pred", []) if results_list else [],  # Take first trajectory's averaged pre-EKF angle predictions

        # Online learning results
        "online_window_losses": avg_online_window_losses,
        "online_window_covariances": avg_online_window_covariances,
        "online_pre_ekf_losses": avg_online_pre_ekf_losses,
        "online_ekf_predictions": avg_online_ekf_predictions,
        "online_ekf_covariances": avg_online_ekf_covariances,
        "online_ekf_innovations": avg_online_ekf_innovations,
        "online_ekf_kalman_gains": avg_online_ekf_kalman_gains,
        "online_ekf_kalman_gain_times_innovation": avg_online_ekf_kalman_gain_times_innovation,
        "online_ekf_y_s_inv_y": avg_online_ekf_y_s_inv_y,
        "online_window_indices": avg_online_window_indices,
        "online_pre_ekf_angles_pred": avg_online_pre_ekf_angles_pred,
        "online_avg_ekf_angle_pred": results_list[0].get("online_avg_ekf_angle_pred", []) if results_list else [],  # Take first trajectory's online averaged EKF angle predictions
        "online_avg_pre_ekf_angle_pred": results_list[0].get("online_avg_pre_ekf_angle_pred", []) if results_list else [],  # Take first trajectory's online averaged pre-EKF angle predictions

        # Training data results
        "training_window_losses": avg_training_window_losses,
        "training_window_covariances": avg_training_window_covariances,
        "training_pre_ekf_losses": avg_training_pre_ekf_losses,
        "training_ekf_predictions": avg_training_ekf_predictions,
        "training_ekf_covariances": avg_training_ekf_covariances,
        "training_ekf_innovations": avg_training_ekf_innovations,
        "training_ekf_kalman_gains": avg_training_ekf_kalman_gains,
        "training_ekf_kalman_gain_times_innovation": avg_training_ekf_kalman_gain_times_innovation,
        "training_ekf_y_s_inv_y": avg_training_ekf_y_s_inv_y,
        "training_window_indices": avg_training_window_indices,
        "learning_start_window": avg_learning_start_window,
        "training_pre_ekf_angles_pred": avg_training_pre_ekf_angles_pred,
        "training_avg_ekf_angle_pred": results_list[0].get("training_avg_ekf_angle_pred", []) if results_list else [],  # Take first trajectory's training averaged EKF angle predictions
        "training_avg_pre_ekf_angle_pred": results_list[0].get("training_avg_pre_ekf_angle_pred", []) if results_list else []  # Take first trajectory's training averaged pre-EKF angle predictions
    }
