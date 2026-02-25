from pathlib import Path


def _root() -> Path:
    return Path(__file__).resolve().parents[2]


def test_training_entrypoint_is_moved_to_run_pipeline():
    train_py = (_root() / "run" / "pipeline" / "training" / "train.py").read_text(encoding="utf-8")

    assert "config_path=\"../../conf\"" in train_py
    assert "from config.utils import create_system_model" in train_py
    assert "_build_legacy_overrides" not in train_py
    assert "_build_native_config" not in train_py
    assert not (_root() / "src" / "train_entry.py").exists()


def test_config_yaml_includes_canonical_groups():
    config_yaml = (_root() / "run" / "conf" / "config.yaml").read_text(encoding="utf-8")

    assert "- system_model: default" in config_yaml
    assert "- dataset: default" in config_yaml
    assert "- training: default" in config_yaml
    assert "- simulation: default" in config_yaml
    assert "- runtime: default" in config_yaml


def test_runtime_group_has_target():
    runtime_yaml = (_root() / "run" / "conf" / "runtime" / "default.yaml").read_text(encoding="utf-8")

    assert "_target_: src.trainer_module.runtime_runner.SimulationRuntimeRunner" in runtime_yaml


def test_data_model_trainer_groups_have_targets():
    data_yaml = (_root() / "run" / "conf" / "data" / "default.yaml").read_text(encoding="utf-8")
    model_yaml = (_root() / "run" / "conf" / "model" / "subspacenet.yaml").read_text(encoding="utf-8")
    dcd_model_yaml = (_root() / "run" / "conf" / "model" / "dcd_music.yaml").read_text(encoding="utf-8")
    trainer_yaml = (_root() / "run" / "conf" / "trainer" / "default.yaml").read_text(encoding="utf-8")

    assert "_target_: src.data_module.lit_datamodule.DOADataModule" in data_yaml
    assert "_target_: src.model_module.subspacenet_lightning.SubspaceNetLightning" in model_yaml
    assert "_target_: src.model_module.dcd_music_lightning.DCDMusicLightning" in dcd_model_yaml
    assert "_target_: pytorch_lightning.Trainer" in trainer_yaml


def test_training_default_contains_lightning_switch():
    training_yaml = (_root() / "run" / "conf" / "training" / "default.yaml").read_text(encoding="utf-8")
    assert "use_lightning:" in training_yaml
