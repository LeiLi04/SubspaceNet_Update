import unittest
from pathlib import Path


class TestOnlineLearningIntegrationContracts(unittest.TestCase):
    def test_pipeline_return_contract_has_required_sections(self):
        src = Path('src/train/online_learning_parts/pipeline.py').read_text(encoding='utf-8', errors='ignore')
        required_tokens = [
            '"status": "success"',
            '"online_learning_results"',
            '"pretrained_trajectory_results"',
            '"online_trajectory_results"',
            '"avg_drift_detected"',
            '"avg_model_updated"',
            '"dataset_size"',
            '"averaged_results"',
        ]
        for token in required_tokens:
            self.assertIn(token, src, msg=f'Missing pipeline return token: {token}')

    def test_average_results_contract_has_required_sections(self):
        src = Path('src/utils/utils.py').read_text(encoding='utf-8', errors='ignore')
        required_tokens = [
            '"status": "success"',
            '"averaged_results"',
            '"averaged_pretrained_trajectory"',
            '"averaged_online_trajectory"',
            '"summary_statistics"',
            '"trajectory_count"',
        ]
        for token in required_tokens:
            self.assertIn(token, src, msg=f'Missing average-results token: {token}')

    def test_online_learning_wrapper_still_exposes_split_api(self):
        src = Path('src/train/online_learning.py').read_text(encoding='utf-8', errors='ignore')
        required_tokens = [
            'def run_online_learning(',
            'def _run_single_trajectory_online_learning(',
            'def _online_training_window(',
            'from src.train.online_learning_parts.pipeline import run_online_learning_impl',
            'from src.train.online_learning_parts.pipeline import _run_single_trajectory_online_learning_impl',
            'from src.train.online_learning_parts.pipeline import _online_training_window_impl',
            'from src.train.online_learning_parts.metrics import _calculate_metrics_impl',
            'from src.train.online_learning_parts.losses import _calculate_all_losses_impl',
        ]
        for token in required_tokens:
            self.assertIn(token, src, msg=f'Missing wrapper token: {token}')


if __name__ == '__main__':
    unittest.main()
