import unittest

import numpy as np
try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    torch = None

if torch is not None:
    from src.train.online_learning import device
    from src.train.online_learning_parts.step_processor import _process_single_step_impl, _initialize_ekf_state_impl


class _DummyModel:
    def __init__(self):
        self.training = True

    def eval(self):
        self.training = False

    def train(self):
        self.training = True

    def __call__(self, step_data_tensor, num_sources_this_step):
        out = torch.linspace(0.1, 0.1 * num_sources_this_step, num_sources_this_step, device=step_data_tensor.device)
        return out.unsqueeze(0), None, None


class _DummySelf:
    trained_model = None

    @staticmethod
    def _get_optimal_permutation(predictions, true_angles):
        _ = predictions
        _ = true_angles
        return np.arange(len(true_angles))


class _DummyFilter:
    def __init__(self):
        self.initialized = None
        self.P = 1.0

    def initialize_state(self, x):
        self.initialized = x


@unittest.skipIf(torch is None, "torch is not installed in this environment")
class TestStepProcessorImpl(unittest.TestCase):
    def test_near_field_fallback_keeps_success_and_restores_model_mode(self):
        host = _DummySelf()
        model = _DummyModel()

        success, step_result = _process_single_step_impl(
            host,
            step=0,
            time_series_steps=torch.randn(1, 8, 16, device=device),
            sources_num_per_step=[2],
            labels_per_step_list=[np.array([0.0, 0.1], dtype=np.float32)],
            ekf_filters=[],
            model=model,
            is_near_field=True,
            Pretrained_model=True,
        )

        self.assertTrue(success)
        self.assertTrue(model.training)  # restored in finally
        self.assertIn('step_innovation_covariance', step_result)
        self.assertEqual(len(step_result['step_innovation_covariance']), 2)
        self.assertEqual(step_result['num_sources'], 2)

    def test_initialize_ekf_state_raises_when_filters_insufficient(self):
        host = _DummySelf()
        ekf_filters = [_DummyFilter()]
        with self.assertRaises(RuntimeError):
            _initialize_ekf_state_impl(
                host,
                step=0,
                num_sources_this_step=2,
                true_angles_this_step=np.array([0.1, 0.2], dtype=np.float32),
                ekf_filters=ekf_filters,
                is_first_window=True,
                last_ekf_predictions=None,
                last_ekf_covariances=None,
            )


if __name__ == '__main__':
    unittest.main()
