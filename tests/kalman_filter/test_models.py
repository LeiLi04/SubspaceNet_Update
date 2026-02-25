"""
Unit tests for state evolution models used in Extended Kalman Filter.
"""

import unittest
import numpy as np
from simulation.kalman_filter.models import SineAccelStateModel, MultNoiseStateModel


class TestSineAccelStateModel(unittest.TestCase):
    """Test the sine acceleration state evolution model."""

    def setUp(self):
        # Create a model with known parameters for testing
        self.omega0 = 0.1  # rad/s
        self.kappa = 0.5   # rad/s^2
        self.noise_std = 0.1  # rad
        self.time_step = 1.0  # s

        self.model = SineAccelStateModel(
            omega0=self.omega0,
            kappa=self.kappa,
            noise_std=self.noise_std,
            time_step=self.time_step,
        )

    def test_initialization(self):
        """Test that model parameters are correctly initialized."""
        self.assertEqual(self.model.omega0, self.omega0)
        self.assertEqual(self.model.kappa, self.kappa)
        self.assertEqual(self.model.base_noise_variance, self.noise_std**2)
        self.assertEqual(self.model.time_step, self.time_step)

    def test_state_transition(self):
        """Test the state transition function."""
        # Current implementation applies a 0.99 scaling in radians at t=0.
        x = 0.0
        expected = 0.99 * x
        actual = self.model.f(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)

        x = np.pi / 2
        expected = 0.99 * x
        actual = self.model.f(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)

    def test_jacobian(self):
        """Test the Jacobian calculation."""
        # Current implementation returns identity Jacobian for 1D state.
        x = 0.0
        expected = 1.0
        actual = self.model.F_jacobian(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)

        x = np.pi / 2
        expected = 1.0
        actual = self.model.F_jacobian(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)

    def test_noise_variance(self):
        """Test the noise variance."""
        x = 0.0
        expected = self.noise_std**2
        actual = self.model.noise_variance(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)


class TestMultNoiseStateModel(unittest.TestCase):
    """Test the multiplicative noise state evolution model."""

    def setUp(self):
        # Create a model with known parameters for testing
        self.omega0 = 0.2  # rad/s
        self.amp = 0.5     # unitless
        self.base_std = 0.1  # rad
        self.time_step = 1.0  # s

        self.model = MultNoiseStateModel(
            omega0=self.omega0,
            amp=self.amp,
            base_std=self.base_std,
            time_step=self.time_step,
        )

    def test_initialization(self):
        """Test that model parameters are correctly initialized."""
        self.assertEqual(self.model.omega0, self.omega0)
        self.assertEqual(self.model.amp, self.amp)
        self.assertEqual(self.model.base_std, self.base_std)
        self.assertEqual(self.model.base_noise_variance, self.base_std**2)
        self.assertEqual(self.model.time_step, self.time_step)

    def test_state_transition(self):
        """Test the state transition function."""
        # Deterministic part is x + omega0*T in radians.
        x = 30.0
        expected = x + self.omega0 * self.time_step
        actual = self.model.f(x)
        self.assertAlmostEqual(actual.item(), expected, places=5)

    def test_jacobian(self):
        """Test the Jacobian calculation."""
        # Jacobian is always 1 for this model.
        x = 45.0
        expected = 1.0
        actual = self.model.F_jacobian(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)

    def test_noise_variance(self):
        """Test the state-dependent noise variance."""
        # Variance uses sin(x)^2 where x is treated as radians.
        x = 0.0
        std = self.base_std * (1.0 + self.amp * np.sin(x) ** 2)
        expected = std**2
        actual = self.model.noise_variance(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)

        x = np.pi / 2
        std = self.base_std * (1.0 + self.amp * np.sin(x) ** 2)
        expected = std**2
        actual = self.model.noise_variance(x)
        self.assertAlmostEqual(actual.item(), expected, places=6)


if __name__ == '__main__':
    unittest.main()
