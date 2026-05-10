from unittest.mock import MagicMock

from game.core.registry import GameRegistries
from game.ui.screens.workshop_data_loader import LoadResult, WorkshopDataLoader


def _registries() -> GameRegistries:
    return GameRegistries(
        components={},
        modifiers={},
        vehicle_classes={"Escort": {"name": "Escort"}},
        resources={},
    )


def test_load_policies_uses_test_files_when_present(tmp_path, monkeypatch):
    (tmp_path / "test_targeting_policies.json").write_text("{}", encoding="utf-8")
    manager = MagicMock()
    monkeypatch.setattr(
        "game.ai.policy_manager.get_default_policy_manager",
        lambda: manager,
    )
    loader = WorkshopDataLoader(str(tmp_path), registries=_registries())

    loader._load_policies(LoadResult())

    manager.clear.assert_called_once_with()
    manager.load_data.assert_called_once_with(
        base_path=str(tmp_path),
        targeting_file="test_targeting_policies.json",
        movement_file="test_movement_policies.json",
    )


def test_load_vehicle_classes_passes_layer_file_path(tmp_path, monkeypatch):
    vehicle_path = tmp_path / "vehicleclasses.json"
    layer_path = tmp_path / "vehiclelayers.json"
    vehicle_path.write_text("{}", encoding="utf-8")
    layer_path.write_text("{}", encoding="utf-8")
    provider = object()
    load_vehicle_classes = MagicMock()
    monkeypatch.setattr(
        "game.ui.screens.workshop_data_loader.get_default_registry_provider",
        lambda: provider,
    )
    monkeypatch.setattr(
        "game.simulation.entities.ship_loader.load_vehicle_classes",
        load_vehicle_classes,
    )
    loader = WorkshopDataLoader(str(tmp_path), registries=_registries())

    loader._load_vehicle_classes(LoadResult())

    load_vehicle_classes.assert_called_once_with(
        str(vehicle_path),
        layers_file_path=str(layer_path),
        registry_provider=provider,
    )

