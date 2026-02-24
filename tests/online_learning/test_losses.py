import unittest
from types import SimpleNamespace

import numpy as np
try:
    import torch
except ModuleNotFoundError:  # pragma: no cover - environment-dependent
    torch = None

if torch is not None:
    from src.trainer_module.online_learning_parts import losses as losses_impl
    from src.trainer_module.online_learning import device
    from src.eval_module.metrics.rmspe_loss import RMSPELoss
    from src.eval_module.metrics.rmape_loss import RMAPELoss


class _DummyLossHost:
    def _fix_tensor_shape_for_loss(self, tensor):
        return losses_impl._fix_tensor_shape_for_loss_impl(self, tensor)


@unittest.skipIf(torch is None, "torch is not installed in this environment")
class TestLossesImpl(unittest.TestCase):
    def setUp(self):
        self.host = _DummyLossHost()
        self.rmspe = RMSPELoss().to(device)
        self.rmape = RMAPELoss().to(device)

    def test_fix_tensor_shape_for_loss_squeezes_middle_dim(self):
        x = torch.randn(4, 1, 3, device=device)
        y = losses_impl._fix_tensor_shape_for_loss_impl(self.host, x)
        self.assertEqual(tuple(y.shape), (4, 3))

    def test_get_optimal_permutation_matches_swapped_pair(self):
        predictions = np.array([0.8, 0.2], dtype=np.float32)
        true_angles = np.array([0.2, 0.8], dtype=np.float32)
        perm = losses_impl._get_optimal_permutation_impl(self.host, predictions, true_angles)
        self.assertEqual(perm.flatten().tolist(), [1, 0])

    def test_calculate_window_training_loss_empty(self):
        out = losses_impl._calculate_window_training_loss_impl(
            self.host,
            step_results_list=[],
            loss_config=SimpleNamespace(training_loss_type='unsupervised_rmspe'),
            rmspe_criterion=self.rmspe,
            rmape_criterion=self.rmape,
        )
        self.assertTrue(out.requires_grad)
        self.assertAlmostEqual(out.item(), 0.0, places=7)

    def test_calculate_window_training_loss_unknown_type_raises(self):
        step_results_list = [
            {
                'success': True,
                'pre_ekf_angles_pred_tensor': torch.tensor([[0.1, 0.2]], device=device),
                'ekf_angles_pred_tensor': torch.tensor([[0.1, 0.3]], device=device),
                'true_angles_tensor': torch.tensor([[0.0, 0.2]], device=device),
            }
        ]

        with self.assertRaises(RuntimeError):
            losses_impl._calculate_window_training_loss_impl(
                self.host,
                step_results_list=step_results_list,
                loss_config=SimpleNamespace(training_loss_type='invalid_loss_type'),
                rmspe_criterion=self.rmspe,
                rmape_criterion=self.rmape,
            )


if __name__ == '__main__':
    unittest.main()
