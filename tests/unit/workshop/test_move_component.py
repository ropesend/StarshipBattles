"""
Tests for moving components between layers in the Design Workshop.

Tests cover:
- resolve_move_target: finding next valid layer in a direction
- VehicleDesignService.move_component: atomic remove + re-add
- WorkshopViewModel.move_component: single component move with events
- WorkshopViewModel.move_component_group: stack move with events

Movement rules:
- "up" = toward inner (lower LayerType value), "down" = toward outer
- HULL is never a valid move target
- Skips layers where the component fails restriction validation
- Mass budget does NOT block moves (violation shown as warning)
- Modifiers and component state are preserved across moves

Note: On Escort, layers are HULL/CORE/OUTER/ARMOR.
  - armor_plate is valid in CORE, OUTER, ARMOR (used for movement tests)
  - standard_engine is only valid in OUTER (used for edge-case tests)
"""
import pytest
import pygame

from game.core.constants import LayerType
from game.core.registry import GameRegistries, get_default_registry_provider
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode


class MockEventBus:
    """Mock EventBus for testing event emissions."""

    def __init__(self):
        self.emitted_events = []

    def emit(self, event_type, data=None):
        self.emitted_events.append((event_type, data))

    def subscribe(self, event_type, callback):
        pass

    def get_events(self, event_type):
        return [e for e in self.emitted_events if e[0] == event_type]

    def clear(self):
        self.emitted_events = []


@pytest.fixture(scope="class")
def move_class_setup():
    """Class-level setup: initialize pygame and load game data."""
    pygame.init()
    from game.simulation.entities.ship_loader import initialize_ship_data
    from game.simulation.components.component import load_components, load_modifiers
    from tests.fixtures.paths import get_project_root, get_data_dir

    provider = get_default_registry_provider()
    initialize_ship_data(str(get_project_root()), registry_provider=provider)
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    load_modifiers(str(data_dir / "modifiers.json"), registry_provider=provider)

    yield
    pygame.quit()


@pytest.fixture
def mock_registries(move_class_setup):
    """Create GameRegistries with real data for testing."""
    from game.simulation.components.component import load_components_data, load_modifiers_data
    from game.simulation.entities.ship_loader import load_vehicle_classes_data

    minimal_registries = GameRegistries(components={}, modifiers={}, vehicle_classes={}, resources={})
    return GameRegistries(
        components=load_components_data(registries=minimal_registries),
        modifiers=load_modifiers_data(),
        vehicle_classes=load_vehicle_classes_data(),
        resources={}
    )


@pytest.fixture
def viewmodel_with_ship(mock_registries):
    """Create a viewmodel with a default Escort ship."""
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel

    event_bus = MockEventBus()
    context = WorkshopContext(mode=WorkshopMode.STANDALONE, registries=mock_registries)
    viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)
    viewmodel.create_default_ship("Escort")
    event_bus.clear()
    return viewmodel, event_bus, mock_registries


@pytest.fixture
def design_service(mock_registries):
    """Create a VehicleDesignService instance."""
    from game.simulation.services.vehicle_design_service import VehicleDesignService
    return VehicleDesignService(registries=mock_registries)


@pytest.fixture
def ship_with_armor(mock_registries):
    """Create an Escort ship with an armor_plate in OUTER."""
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import create_component

    ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
    armor = create_component('armor_plate', registries=mock_registries)
    ship.add_component(armor, LayerType.OUTER)
    ship.recalculate_stats()
    return ship, armor


# ─────────────────────────────────────────────────────────────────
# resolve_move_target tests
# ─────────────────────────────────────────────────────────────────

class TestResolveMoveTarget:
    """Tests for resolve_move_target — finding next valid layer in a direction."""

    def test_move_down_from_core(self, viewmodel_with_ship):
        """armor_plate moving down from CORE should reach OUTER."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        result = viewmodel.resolve_move_target(comp, LayerType.CORE, direction="down")

        assert result is not None
        assert result == LayerType.OUTER

    def test_move_up_from_armor(self, viewmodel_with_ship):
        """armor_plate moving up from ARMOR should reach OUTER."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        result = viewmodel.resolve_move_target(comp, LayerType.ARMOR, direction="up")

        assert result is not None
        assert result == LayerType.OUTER

    def test_move_up_from_core_returns_none(self, viewmodel_with_ship):
        """Moving up from CORE (innermost non-HULL) returns None."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        result = viewmodel.resolve_move_target(comp, LayerType.CORE, direction="up")

        assert result is None

    def test_move_down_from_outermost_returns_none(self, viewmodel_with_ship):
        """Moving down from ARMOR (outermost) returns None."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        result = viewmodel.resolve_move_target(comp, LayerType.ARMOR, direction="down")

        assert result is None

    def test_never_returns_hull(self, viewmodel_with_ship):
        """HULL is never returned as a move target."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        for layer in LayerType:
            for direction in ("up", "down"):
                result = viewmodel.resolve_move_target(comp, layer, direction)
                if result is not None:
                    assert result != LayerType.HULL

    def test_skips_invalid_layers(self, viewmodel_with_ship):
        """Engine only valid in OUTER — no movement possible in either direction."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('standard_engine', registries=registries)
        up = viewmodel.resolve_move_target(comp, LayerType.OUTER, direction="up")
        down = viewmodel.resolve_move_target(comp, LayerType.OUTER, direction="down")

        assert up is None
        assert down is None

    def test_no_ship_returns_none(self, mock_registries):
        """Returns None when no ship is loaded."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel
        from game.simulation.components.component import create_component

        event_bus = MockEventBus()
        context = WorkshopContext(mode=WorkshopMode.STANDALONE, registries=mock_registries)
        viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)

        comp = create_component('armor_plate', registries=mock_registries)
        result = viewmodel.resolve_move_target(comp, LayerType.CORE, direction="down")
        assert result is None


# ─────────────────────────────────────────────────────────────────
# VehicleDesignService.move_component tests
# ─────────────────────────────────────────────────────────────────

class TestServiceMoveComponent:
    """Tests for VehicleDesignService.move_component — atomic remove + re-add."""

    def test_move_preserves_instance(self, design_service, ship_with_armor):
        """Moving preserves the same component instance."""
        ship, armor = ship_with_armor

        result = design_service.move_component(ship, LayerType.OUTER, 0, LayerType.ARMOR)

        assert result.success
        assert armor in ship.layers[LayerType.ARMOR].components
        assert armor not in ship.layers[LayerType.OUTER].components

    def test_move_returns_success(self, design_service, ship_with_armor):
        """Successful move returns DesignResult with success=True."""
        ship, _ = ship_with_armor

        result = design_service.move_component(ship, LayerType.OUTER, 0, LayerType.ARMOR)

        assert result.success
        assert result.ship is ship

    def test_move_invalid_source_layer(self, design_service, ship_with_armor):
        """Move from a non-existent layer returns failure."""
        ship, _ = ship_with_armor

        # INNER does not exist on Escort
        result = design_service.move_component(ship, LayerType.INNER, 0, LayerType.OUTER)
        assert not result.success

    def test_move_invalid_index(self, design_service, ship_with_armor):
        """Move with out-of-range index returns failure."""
        ship, _ = ship_with_armor

        result = design_service.move_component(ship, LayerType.OUTER, 99, LayerType.ARMOR)
        assert not result.success

    def test_move_same_layer_is_noop(self, design_service, ship_with_armor):
        """Move to the same layer is a no-op success."""
        ship, armor = ship_with_armor

        result = design_service.move_component(ship, LayerType.OUTER, 0, LayerType.OUTER)

        assert result.success
        assert armor in ship.layers[LayerType.OUTER].components


# ─────────────────────────────────────────────────────────────────
# WorkshopViewModel.move_component tests
# ─────────────────────────────────────────────────────────────────

class TestViewModelMoveComponent:
    """Tests for WorkshopViewModel.move_component — single component move."""

    def test_move_component_succeeds(self, viewmodel_with_ship):
        """Moving a single component between layers succeeds."""
        viewmodel, _, registries = viewmodel_with_ship

        viewmodel.add_component('armor_plate', LayerType.OUTER)
        outer_before = len(viewmodel.ship.layers[LayerType.OUTER].components)

        result = viewmodel.move_component(LayerType.OUTER, 0, LayerType.ARMOR)

        assert result is True
        assert len(viewmodel.ship.layers[LayerType.OUTER].components) == outer_before - 1

    def test_move_component_emits_ship_updated(self, viewmodel_with_ship):
        """Moving a component emits SHIP_UPDATED event."""
        viewmodel, event_bus, _ = viewmodel_with_ship

        viewmodel.add_component('armor_plate', LayerType.OUTER)
        event_bus.clear()

        viewmodel.move_component(LayerType.OUTER, 0, LayerType.ARMOR)

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1

    def test_move_component_no_ship_returns_false(self, mock_registries):
        """Returns False when no ship is loaded."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel

        event_bus = MockEventBus()
        context = WorkshopContext(mode=WorkshopMode.STANDALONE, registries=mock_registries)
        viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)

        result = viewmodel.move_component(LayerType.OUTER, 0, LayerType.ARMOR)
        assert result is False

    def test_move_preserves_instance_identity(self, viewmodel_with_ship):
        """Moving preserves the exact same component object (modifiers, state intact)."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        comp.add_modifier('hardened')
        comp.recalculate_stats()

        viewmodel.add_component_instance(comp, LayerType.OUTER)
        idx = viewmodel.ship.layers[LayerType.OUTER].components.index(comp)

        viewmodel.move_component(LayerType.OUTER, idx, LayerType.ARMOR)

        # Same object instance in the target layer
        armor_comps = viewmodel.ship.layers[LayerType.ARMOR].components
        assert any(c is comp for c in armor_comps), "Same instance should be in target layer"


# ─────────────────────────────────────────────────────────────────
# WorkshopViewModel.move_component_group tests
# ─────────────────────────────────────────────────────────────────

class TestViewModelMoveComponentGroup:
    """Tests for WorkshopViewModel.move_component_group — stack move."""

    def test_move_group_moves_all(self, viewmodel_with_ship):
        """Moving a group moves all components with matching group_key."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.ui.screens.builder.grouping_strategies import get_component_group_key
        from game.simulation.components.component import create_component

        # Add 3 armor_plates to OUTER
        comps = []
        for _ in range(3):
            c = create_component('armor_plate', registries=registries)
            viewmodel.add_component_instance(c, LayerType.OUTER)
            comps.append(c)

        group_key = get_component_group_key(comps[0])
        armor_before = len(viewmodel.ship.layers[LayerType.ARMOR].components)

        result = viewmodel.move_component_group(group_key, LayerType.OUTER, LayerType.ARMOR)

        assert result is True
        armor_after = len(viewmodel.ship.layers[LayerType.ARMOR].components)
        assert armor_after >= armor_before + 3

    def test_move_group_emits_ship_updated(self, viewmodel_with_ship):
        """Moving a group emits SHIP_UPDATED event."""
        viewmodel, event_bus, registries = viewmodel_with_ship
        from game.ui.screens.builder.grouping_strategies import get_component_group_key
        from game.simulation.components.component import create_component

        c = create_component('armor_plate', registries=registries)
        viewmodel.add_component_instance(c, LayerType.OUTER)
        group_key = get_component_group_key(c)
        event_bus.clear()

        viewmodel.move_component_group(group_key, LayerType.OUTER, LayerType.ARMOR)

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1

    def test_move_group_no_matching_components(self, viewmodel_with_ship):
        """Returns False when no components match the group_key in source layer."""
        viewmodel, _, _ = viewmodel_with_ship

        result = viewmodel.move_component_group("nonexistent_group", LayerType.CORE, LayerType.OUTER)
        assert result is False
