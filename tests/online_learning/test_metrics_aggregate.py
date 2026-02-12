import unittest

try:
    import torch  # noqa: F401
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    torch = None

if torch is not None:
    from src.train.online_learning_parts.metrics_aggregate import _average_online_learning_results_across_trajectories_impl


def _make_result(window_losses, online_losses=None, training_losses=None):
    if online_losses is None:
        online_losses = []
    if training_losses is None:
        training_losses = []

    window_count = len(window_losses)
    covariances = [0.1 + i for i in range(window_count)]

    # Minimal nested placeholders: [window][step][source]
    nested = [[[0.0]] for _ in range(window_count)]

    return {
        'window_losses': window_losses,
        'window_covariances': covariances,
        'window_eta_values': [0.0 for _ in range(window_count)],
        'window_updates': [0 for _ in range(window_count)],
        'drift_detected_count': 1,
        'model_updated_count': 2,
        'window_count': window_count,
        'window_size': 10,
        'stride': 5,
        'loss_threshold': 0.5,
        'ekf_predictions': nested,
        'ekf_covariances': nested,
        'ekf_innovations': nested,
        'ekf_kalman_gains': nested,
        'ekf_kalman_gain_times_innovation': nested,
        'ekf_y_s_inv_y': nested,
        'pre_ekf_losses': window_losses,
        'window_labels': [[0.0] for _ in range(window_count)],
        'window_pre_ekf_angles_pred': nested,
        'window_avg_ekf_angle_pred': [0.0],
        'window_avg_pre_ekf_angle_pred': [0.0],
        'online_window_losses': online_losses,
        'online_window_covariances': online_losses,
        'online_pre_ekf_losses': online_losses,
        'online_ekf_predictions': nested,
        'online_ekf_covariances': nested,
        'online_ekf_innovations': nested,
        'online_ekf_kalman_gains': nested,
        'online_ekf_kalman_gain_times_innovation': nested,
        'online_ekf_y_s_inv_y': nested,
        'online_window_indices': list(range(len(online_losses))),
        'online_pre_ekf_angles_pred': nested,
        'online_avg_ekf_angle_pred': [0.0],
        'online_avg_pre_ekf_angle_pred': [0.0],
        'training_window_losses': training_losses,
        'training_window_covariances': training_losses,
        'training_pre_ekf_losses': training_losses,
        'training_ekf_predictions': nested,
        'training_ekf_covariances': nested,
        'training_ekf_innovations': nested,
        'training_ekf_kalman_gains': nested,
        'training_ekf_kalman_gain_times_innovation': nested,
        'training_ekf_y_s_inv_y': nested,
        'training_window_indices': list(range(len(training_losses))),
        'learning_start_window': 0 if training_losses else None,
        'training_pre_ekf_angles_pred': nested,
        'training_avg_ekf_angle_pred': [0.0],
        'training_avg_pre_ekf_angle_pred': [0.0],
    }


@unittest.skipIf(torch is None, "torch is not installed in this environment")
class TestMetricsAggregateImpl(unittest.TestCase):
    def test_average_basic_static_metrics(self):
        results_list = [
            _make_result([1.0, 3.0]),
            _make_result([3.0, 5.0]),
        ]

        out = _average_online_learning_results_across_trajectories_impl(None, results_list)
        self.assertEqual(out['window_losses'], [2.0, 4.0])
        self.assertAlmostEqual(out['drift_detected_count'], 1.0)
        self.assertAlmostEqual(out['model_updated_count'], 2.0)

    def test_average_handles_partial_online_and_training_data(self):
        results_list = [
            _make_result([1.0, 3.0], online_losses=[2.0, 4.0], training_losses=[5.0, 7.0]),
            _make_result([3.0, 5.0], online_losses=[], training_losses=[]),
        ]

        out = _average_online_learning_results_across_trajectories_impl(None, results_list)
        self.assertEqual(out['online_window_losses'], [2.0, 4.0])
        self.assertEqual(out['training_window_losses'], [5.0, 7.0])
        self.assertEqual(out['online_window_indices'], [0, 1])
        self.assertEqual(out['training_window_indices'], [0, 1])


if __name__ == '__main__':
    unittest.main()
