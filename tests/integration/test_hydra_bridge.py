from pathlib import Path

from omegaconf import OmegaConf

def test_build_legacy_overrides_maps_transitional_sections():
    from src import train_entry as module

    cfg = OmegaConf.create(
        {
            "dataset": {"samples_size": 256},
            "training": {"epochs": 30, "batch_size": 128},
            "data": {"samples_size": 64, "create_data": True},
            "trainer": {"max_epochs": 5, "learning_rate": 0.001},
        }
    )

    overrides = module._build_legacy_overrides(cfg)

    assert "dataset.samples_size=256" in overrides
    assert "dataset.create_data=true" in overrides
    assert "dataset.samples_size=64" in overrides
    assert "training.epochs=30" in overrides
    assert "training.batch_size=128" in overrides
    assert "training.epochs=5" in overrides
    assert "training.learning_rate=0.001" in overrides


def test_config_yaml_includes_canonical_groups():
    root = Path(__file__).resolve().parents[2]
    config_yaml = (root / "configs" / "config.yaml").read_text(encoding="utf-8")

    assert "- system_model: default" in config_yaml
    assert "- dataset: default" in config_yaml
    assert "- training: default" in config_yaml
    assert "- simulation: default" in config_yaml
    assert "- runtime: default" in config_yaml


def test_runtime_group_has_target():
    root = Path(__file__).resolve().parents[2]
    runtime_yaml = (root / "configs" / "runtime" / "default.yaml").read_text(encoding="utf-8")

    assert "_target_: src.train.runtime_runner.SimulationRuntimeRunner" in runtime_yaml


def test_data_model_trainer_groups_have_targets():
    root = Path(__file__).resolve().parents[2]
    data_yaml = (root / "configs" / "data" / "default.yaml").read_text(encoding="utf-8")
    model_yaml = (root / "configs" / "model" / "default.yaml").read_text(encoding="utf-8")
    trainer_yaml = (root / "configs" / "trainer" / "default.yaml").read_text(encoding="utf-8")

    assert "_target_: src.train.component_factories.DataComponentFactory" in data_yaml
    assert "_target_: src.train.component_factories.ModelComponentFactory" in model_yaml
    assert "_target_: src.train.component_factories.TrainerComponentFactory" in trainer_yaml


def test_training_default_contains_lightning_switch():
    root = Path(__file__).resolve().parents[2]
    training_yaml = (root / "configs" / "training" / "default.yaml").read_text(encoding="utf-8")
    assert "use_lightning:" in training_yaml
