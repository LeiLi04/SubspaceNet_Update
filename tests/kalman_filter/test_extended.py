"""
Unit tests for ExtendedKalmanFilter1D implementation.
"""

import unittest
import torch
from unittest.mock import MagicMock, patch
from simulation.kalman_filter.extended import ExtendedKalmanFilter1D
from config.schema import TrajectoryType


class TestExtendedKalmanFilter1D(unittest.TestCase):
    """Test the ExtendedKalmanFilter1D implementation."""

    def setUp(self):
        """Set up a filter with a mock state model for testing."""
        self.state_model = MagicMock()
        self.state_model.f.return_value = torch.tensor(11.0)
        self.state_model.F_jacobian.return_value = torch.tensor(1.2)
        self.state_model.noise_variance.return_value = torch.tensor(0.25)

        self.R = 0.1
        self.P0 = 1.0
        self.filter = ExtendedKalmanFilter1D(
            state_model=self.state_model,
            R=self.R,
            P0=self.P0,
        )

        self.x0 = 10.0
        self.filter.initialize_state(self.x0)

    def test_initialization(self):
        """Test that filter parameters are correctly initialized."""
        self.assertEqual(self.filter.state_model, self.state_model)
        self.assertAlmostEqual(self.filter.R.item(), self.R, places=6)
        self.assertAlmostEqual(self.filter.P0.item(), self.P0, places=6)
        self.assertAlmostEqual(self.filter.x.item(), self.x0, places=6)
        self.assertAlmostEqual(self.filter.P.item(), self.P0, places=6)

    def test_predict(self):
        """Test the prediction step."""
        x_pred = self.filter.predict()

        self.state_model.f.assert_called_once()
        f_args, _ = self.state_model.f.call_args
        self.assertAlmostEqual(f_args[0].item(), self.x0, places=6)
        self.assertEqual(f_args[1], 0)

        self.state_model.F_jacobian.assert_called_once()
        jac_args, _ = self.state_model.F_jacobian.call_args
        self.assertAlmostEqual(jac_args[0].item(), self.x0, places=6)
        self.assertEqual(jac_args[1], 0)

        self.state_model.noise_variance.assert_called_once()
        q_args, _ = self.state_model.noise_variance.call_args
        self.assertAlmostEqual(q_args[0].item(), self.x0, places=6)
        self.assertEqual(q_args[1], 0)

        self.assertAlmostEqual(x_pred.item(), 11.0, places=6)
        self.assertAlmostEqual(self.filter.x.item(), 11.0, places=6)
        # P_pred = F * P * F + Q = 1.2 * 1.0 * 1.2 + 0.25 = 1.69
        self.assertAlmostEqual(self.filter.P.item(), 1.69, places=6)

    def test_update(self):
        """Test the update step."""
        self.filter.x = torch.tensor(11.0)
        self.filter.P = torch.tensor(1.69)

        z = 12.0
        x_new, innovation, kalman_gain, kg_times_innovation, y_s_inv_y, innovation_cov = self.filter.update(z)

        y = z - 11.0
        S = 1.69 + 0.1
        K = 1.69 / S
        expected_x = 11.0 + K * y
        expected_P = (1 - K) * 1.69

        self.assertAlmostEqual(x_new.item(), expected_x, places=6)
        self.assertAlmostEqual(innovation.item(), y, places=6)
        self.assertAlmostEqual(kalman_gain.item(), K, places=6)
        self.assertAlmostEqual(kg_times_innovation.item(), K * y, places=6)
        self.assertAlmostEqual(y_s_inv_y.item(), y * (1.0 / S) * y, places=6)
        self.assertAlmostEqual(innovation_cov.item(), S, places=6)

        self.assertAlmostEqual(self.filter.x.item(), expected_x, places=6)
        self.assertAlmostEqual(self.filter.P.item(), expected_P, places=6)

    @patch('simulation.kalman_filter.extended.SineAccelStateModel')
    @patch('simulation.kalman_filter.extended.MultNoiseStateModel')
    def test_from_config_sine_accel(self, mock_mult_noise, mock_sine_accel):
        """Test parameter creation from config with sine acceleration model."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.SINE_ACCEL_NONLINEAR
        config.trajectory.sine_accel_omega0 = 0.1
        config.trajectory.sine_accel_kappa = 0.5
        config.trajectory.sine_accel_noise_std = 0.2
        config.kalman_filter.process_noise_std_dev = None
        config.kalman_filter.measurement_noise_std_dev = 0.1
        config.kalman_filter.initial_covariance = 2.0
        config.system_model.M = 1

        mock_model = MagicMock()
        mock_sine_accel.return_value = mock_model

        state_model, R, P0 = ExtendedKalmanFilter1D.from_config(config)

        mock_sine_accel.assert_called_once_with([0.1], [0.5], 0.2, device=None, initial_time=0.0)
        mock_mult_noise.assert_not_called()

        self.assertEqual(state_model, mock_model)
        self.assertAlmostEqual(R, 0.01, places=6)
        self.assertEqual(P0, 2.0)

    @patch('simulation.kalman_filter.extended.SineAccelStateModel')
    @patch('simulation.kalman_filter.extended.MultNoiseStateModel')
    def test_from_config_mult_noise(self, mock_mult_noise, mock_sine_accel):
        """Test parameter creation from config with multiplicative noise model."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.MULT_NOISE_NONLINEAR
        config.trajectory.mult_noise_omega0 = 0.2
        config.trajectory.mult_noise_amp = 0.5
        config.trajectory.mult_noise_base_std = 0.3
        config.kalman_filter.process_noise_std_dev = None
        config.kalman_filter.measurement_noise_std_dev = 0.1
        config.kalman_filter.initial_covariance = 2.0

        mock_model = MagicMock()
        mock_mult_noise.return_value = mock_model

        state_model, R, P0 = ExtendedKalmanFilter1D.from_config(config)

        mock_mult_noise.assert_called_once_with(0.2, 0.5, 0.3, device=None)
        mock_sine_accel.assert_not_called()

        self.assertEqual(state_model, mock_model)
        self.assertAlmostEqual(R, 0.01, places=6)
        self.assertEqual(P0, 2.0)

    @patch('simulation.kalman_filter.extended.SineAccelStateModel')
    def test_from_config_random_walk(self, mock_sine_accel):
        """Test parameter creation from config with random walk model."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.RANDOM_WALK
        config.trajectory.random_walk_std_dev = 0.5
        config.kalman_filter.process_noise_std_dev = None
        config.kalman_filter.measurement_noise_std_dev = 0.1
        config.kalman_filter.initial_covariance = 2.0

        mock_model = MagicMock()
        mock_sine_accel.return_value = mock_model

        state_model, R, P0 = ExtendedKalmanFilter1D.from_config(config)

        mock_sine_accel.assert_called_once_with(0.0, 0.0, 0.5, device=None, initial_time=0.0)

        self.assertEqual(state_model, mock_model)
        self.assertAlmostEqual(R, 0.01, places=6)
        self.assertEqual(P0, 2.0)


if __name__ == '__main__':
    unittest.main()
