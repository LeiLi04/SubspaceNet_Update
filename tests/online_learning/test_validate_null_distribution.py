import numpy as np

from scripts.validate_null_distribution import (
    _decimate,
    _load_per_source_values,
    _load_values,
)


def test_load_values_supports_total_c_key(tmp_path):
    path = tmp_path / "null_dump.npz"
    np.savez(path, c=np.array([1.0, 2.0, 3.0]))

    np.testing.assert_allclose(_load_values(path), np.array([1.0, 2.0, 3.0]))


def test_load_per_source_values_supports_pipeline_key(tmp_path):
    path = tmp_path / "null_dump.npz"
    values = np.array([[0.5, 1.0, 1.5], [2.0, 2.5, 3.0]])
    np.savez(path, c_per_step_per_source=values)

    np.testing.assert_allclose(_load_per_source_values(path), values)


def test_decimate_keeps_every_nth_row_for_1d_and_2d():
    np.testing.assert_allclose(_decimate(np.arange(6), 2), np.array([0, 2, 4]))
    np.testing.assert_allclose(
        _decimate(np.arange(12).reshape(6, 2), 3),
        np.array([[0, 1], [6, 7]]),
    )
