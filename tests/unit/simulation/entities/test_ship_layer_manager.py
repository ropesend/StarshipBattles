"""Tests for ShipLayerManager — layer initialization, hull equipping, class changes."""
import pytest
from unittest.mock import MagicMock, patch

from game.core.constants import LayerType
from game.simulation.entities.ship_layer_manager import ShipLayerManager


@pytest.fixture
def mock_ship():
    """Create a minimal mock ship for layer manager tests."""
    ship = MagicMock()
    ship.ship_class = "Cruiser"
    ship.name = "Test Ship"
    ship._registries = MagicMock()
    ship._registries.vehicle_classes = {
        "Cruiser": {
            "type": "Ship",
            "max_mass": 500,
            "default_hull_id": "hull_cruiser",
            "layers": [
                {"type": "CORE", "radius_pct": 0.3, "max_mass_pct": 0.3, "restrictions": []},
                {"type": "INNER", "radius_pct": 0.6, "max_mass_pct": 0.3, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.8, "max_mass_pct": 0.2, "restrictions": []},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.2, "restrictions": []},
            ],
        },
        "Frigate": {
            "type": "Ship",
            "max_mass": 200,
            "default_hull_id": "hull_frigate",
            "layers": [
                {"type": "CORE", "radius_pct": 0.4, "max_mass_pct": 0.5, "restrictions": []},
                {"type": "ARMOR", "radius_pct": 1.0, "max_mass_pct": 0.5, "restrictions": []},
            ],
        },
    }
    ship.layers = {}
    return ship


class TestShipLayerManagerInit:
    """Test ShipLayerManager construction."""

    def test_stores_ship_reference(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        assert mgr._ship is mock_ship


class TestInitializeLayers:
    """Test layer initialization logic."""

    def test_creates_layers_from_class_def(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()
        assert LayerType.HULL in mock_ship.layers
        assert LayerType.CORE in mock_ship.layers
        assert LayerType.INNER in mock_ship.layers
        assert LayerType.OUTER in mock_ship.layers
        assert LayerType.ARMOR in mock_ship.layers

    def test_hull_layer_always_present(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()
        assert LayerType.HULL in mock_ship.layers

    def test_hull_radius_is_zero(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()
        assert mock_ship.layers[LayerType.HULL].radius_pct == 0.0

    def test_fallback_layers_when_no_layers_key(self, mock_ship):
        """Ship class without layers key should get default layers."""
        mock_ship._registries.vehicle_classes["Cruiser"] = {"type": "Ship", "max_mass": 100}
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()
        assert LayerType.HULL in mock_ship.layers
        assert LayerType.CORE in mock_ship.layers
        assert LayerType.ARMOR in mock_ship.layers

    def test_unknown_layer_type_skipped(self, mock_ship):
        """Unknown layer type string should be skipped with warning."""
        mock_ship._registries.vehicle_classes["Cruiser"]["layers"] = [
            {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 0.5, "restrictions": []},
            {"type": "BOGUS", "radius_pct": 1.0, "max_mass_pct": 0.5, "restrictions": []},
        ]
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()
        assert LayerType.CORE in mock_ship.layers
        assert len([k for k in mock_ship.layers if k != LayerType.HULL]) == 1  # Only CORE, not BOGUS


class TestEquipDefaultHull:
    """Test default hull component equipping."""

    def test_hull_component_added_to_hull_layer(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()

        mock_comp = MagicMock()
        with patch('game.simulation.entities.ship_layer_manager.create_component', return_value=mock_comp):
            class_def = mock_ship._registries.vehicle_classes["Cruiser"]
            mgr.equip_default_hull(class_def)
            assert mock_comp in mock_ship.layers[LayerType.HULL].components

    def test_no_hull_when_no_default_hull_id(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()

        class_def = {"type": "Ship", "max_mass": 100}  # No default_hull_id
        initial_count = len(mock_ship.layers[LayerType.HULL].components)
        mgr.equip_default_hull(class_def)
        assert len(mock_ship.layers[LayerType.HULL].components) == initial_count


class TestChangeClass:
    """Test class change orchestration."""

    def test_change_class_updates_ship_class(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()

        with patch('game.simulation.entities.ship_layer_manager.create_component', return_value=MagicMock()):
            mgr.change_class("Frigate")
        assert mock_ship.ship_class == "Frigate"

    def test_change_class_reinitializes_layers(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()

        with patch('game.simulation.entities.ship_layer_manager.create_component', return_value=MagicMock()):
            mgr.change_class("Frigate")
        # Frigate has only CORE + ARMOR (no INNER/OUTER)
        assert LayerType.CORE in mock_ship.layers
        assert LayerType.ARMOR in mock_ship.layers

    def test_change_class_calls_recalculate_stats(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()

        with patch('game.simulation.entities.ship_layer_manager.create_component', return_value=MagicMock()):
            mgr.change_class("Frigate")
        mock_ship.recalculate_stats.assert_called_once()

    def test_change_class_unknown_class_returns_early(self, mock_ship):
        mgr = ShipLayerManager(mock_ship)
        mgr.initialize_layers()
        old_class = mock_ship.ship_class

        mgr.change_class("NonexistentClass")
        assert mock_ship.ship_class == old_class  # Unchanged
