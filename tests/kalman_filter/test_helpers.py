"""
Unit tests for helper functions in the kalman_filter package.
"""

import unittest
from unittest.mock import MagicMock, patch
from config.schema import TrajectoryType
from simulation.kalman_filter import get_kalman_filter
from simulation.kalman_filter.base import KalmanFilter1D
from simulation.kalman_filter.extended import ExtendedKalmanFilter1D


class TestHelperFunctions(unittest.TestCase):
    """Test the helper functions in the kalman_filter package."""

    @patch('simulation.kalman_filter.ExtendedKalmanFilter1D.create_from_config')
    @patch('simulation.kalman_filter.KalmanFilter1D.create_from_config')
    def test_get_kalman_filter_standard(self, mock_kf_create_from_config, mock_ekf_create_from_config):
        """Test get_kalman_filter with standard filter type."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.RANDOM_WALK
        config.kalman_filter.filter_type = "standard"

        mock_kf = MagicMock(spec=KalmanFilter1D)
        mock_kf_create_from_config.return_value = mock_kf

        filt = get_kalman_filter(config)

        mock_kf_create_from_config.assert_called_once_with(config)
        mock_ekf_create_from_config.assert_not_called()
        self.assertEqual(filt, mock_kf)

    @patch('simulation.kalman_filter.ExtendedKalmanFilter1D.create_from_config')
    @patch('simulation.kalman_filter.KalmanFilter1D.create_from_config')
    def test_get_kalman_filter_extended(self, mock_kf_create_from_config, mock_ekf_create_from_config):
        """Test get_kalman_filter with extended filter type."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.RANDOM_WALK
        config.kalman_filter.filter_type = "extended"

        mock_ekf = MagicMock(spec=ExtendedKalmanFilter1D)
        mock_ekf_create_from_config.return_value = mock_ekf

        filt = get_kalman_filter(config)

        mock_ekf_create_from_config.assert_called_once_with(config, TrajectoryType.RANDOM_WALK)
        mock_kf_create_from_config.assert_not_called()
        self.assertEqual(filt, mock_ekf)

    @patch('simulation.kalman_filter.ExtendedKalmanFilter1D.create_from_config')
    @patch('simulation.kalman_filter.KalmanFilter1D.create_from_config')
    def test_get_kalman_filter_nonlinear_trajectory(self, mock_kf_create_from_config, mock_ekf_create_from_config):
        """Test get_kalman_filter with non-linear trajectory type."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.SINE_ACCEL_NONLINEAR
        config.kalman_filter.filter_type = "standard"

        mock_ekf = MagicMock(spec=ExtendedKalmanFilter1D)
        mock_ekf_create_from_config.return_value = mock_ekf

        filt = get_kalman_filter(config)

        mock_ekf_create_from_config.assert_called_once_with(config, TrajectoryType.SINE_ACCEL_NONLINEAR)
        mock_kf_create_from_config.assert_not_called()
        self.assertEqual(filt, mock_ekf)

    @patch('simulation.kalman_filter.ExtendedKalmanFilter1D.create_from_config')
    @patch('simulation.kalman_filter.KalmanFilter1D.create_from_config')
    def test_get_kalman_filter_with_trajectory_type_param(self, mock_kf_create_from_config, mock_ekf_create_from_config):
        """Test get_kalman_filter with trajectory_type parameter."""
        config = MagicMock()
        config.trajectory.trajectory_type = TrajectoryType.RANDOM_WALK
        config.kalman_filter.filter_type = "standard"

        mock_ekf = MagicMock(spec=ExtendedKalmanFilter1D)
        mock_ekf_create_from_config.return_value = mock_ekf

        filt = get_kalman_filter(config, TrajectoryType.SINE_ACCEL_NONLINEAR)

        mock_ekf_create_from_config.assert_called_once_with(config, TrajectoryType.SINE_ACCEL_NONLINEAR)
        mock_kf_create_from_config.assert_not_called()
        self.assertEqual(filt, mock_ekf)


if __name__ == '__main__':
    unittest.main()
