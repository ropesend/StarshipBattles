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
  - battery (Infrastructure) is valid in CORE and OUTER (used for movement tests)
  - standard_engine is only valid in OUTER (used for edge-case tests)
  - armor components (major_classification=Armor) are valid ONLY in ARMOR
    (BUG-116) — used to assert manual moves into non-ARMOR layers are rejected.
"""
import pytest

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
    """Class-level setup: load game data."""
    from game.simulation.entities.ship_loader import initialize_ship_data
    from game.simulation.components.component import load_components, load_modifiers
    from tests.fixtures.paths import get_project_root, get_data_dir

    provider = get_default_registry_provider()
    initialize_ship_data(str(get_project_root()), registry_provider=provider)
    data_dir = get_data_dir()
    load_components(str(data_dir / "components.json"), registry_provider=provider)
    load_modifiers(str(data_dir / "modifiers.json"), registry_provider=provider)

    yield


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
def ship_with_movable_component(mock_registries):
    """Create an Escort ship with a battery (Infrastructure) in OUTER.

    Battery is valid in both CORE and OUTER on the Capital_Escort template,
    so it exercises the move pipeline cleanly without colliding with the
    BUG-116 armor-restriction rule.
    """
    from game.simulation.entities.ship import Ship
    from game.simulation.components.component import create_component

    ship = Ship("Test", 640, 360, (255, 255, 255), ship_class="Escort", registries=mock_registries)
    movable = create_component('battery', registries=mock_registries)
    ship.add_component(movable, LayerType.OUTER)
    ship.recalculate_stats()
    return ship, movable


# ─────────────────────────────────────────────────────────────────
# resolve_move_target tests
# ─────────────────────────────────────────────────────────────────

class TestResolveMoveTarget:
    """Tests for resolve_move_target — finding next valid layer in a direction."""

    def test_move_down_from_core(self, viewmodel_with_ship):
        """battery (Infrastructure) moving down from CORE should reach OUTER.

        Battery is valid in CORE+OUTER on Capital_Escort; ARMOR rejects via
        allow_classification:Armor whitelist, so OUTER is the only step.
        """
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('battery', registries=registries)
        result = viewmodel.resolve_move_target(comp, LayerType.CORE, direction="down")

        assert result is not None
        assert result == LayerType.OUTER

    def test_move_up_from_armor(self, viewmodel_with_ship):
        """battery moving up from ARMOR should reach OUTER (nearest valid)."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('battery', registries=registries)
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

    def test_move_preserves_instance(self, design_service, ship_with_movable_component):
        """Moving preserves the same component instance."""
        ship, movable = ship_with_movable_component

        result = design_service.move_component(ship, LayerType.OUTER, 0, LayerType.CORE)

        assert result.success
        assert movable in ship.layers[LayerType.CORE].components
        assert movable not in ship.layers[LayerType.OUTER].components

    def test_move_returns_success(self, design_service, ship_with_movable_component):
        """Successful move returns DesignResult with success=True."""
        ship, _ = ship_with_movable_component

        result = design_service.move_component(ship, LayerType.OUTER, 0, LayerType.CORE)

        assert result.success
        assert result.ship is ship

    def test_move_invalid_source_layer(self, design_service, ship_with_movable_component):
        """Move from a non-existent layer returns failure."""
        ship, _ = ship_with_movable_component

        # INNER does not exist on Escort
        result = design_service.move_component(ship, LayerType.INNER, 0, LayerType.OUTER)
        assert not result.success

    def test_move_invalid_index(self, design_service, ship_with_movable_component):
        """Move with out-of-range index returns failure."""
        ship, _ = ship_with_movable_component

        result = design_service.move_component(ship, LayerType.OUTER, 99, LayerType.ARMOR)
        assert not result.success

    def test_move_same_layer_is_noop(self, design_service, ship_with_movable_component):
        """Move to the same layer is a no-op success."""
        ship, movable = ship_with_movable_component

        result = design_service.move_component(ship, LayerType.OUTER, 0, LayerType.OUTER)

        assert result.success
        assert movable in ship.layers[LayerType.OUTER].components

    @pytest.mark.parametrize("target_layer", [
        LayerType.CORE,
        LayerType.INNER,
        LayerType.OUTER,
    ])
    def test_armor_cannot_be_moved_into_non_armor_layer(
        self, design_service, mock_registries, target_layer
    ):
        """BUG-116: VehicleDesignService.move_component must reject moving an
        armor component out of the ARMOR layer into CORE / INNER / OUTER.

        Cruiser is the test ship because its Capital_Standard template carries
        all four non-HULL layers (CORE, INNER, OUTER, ARMOR), so every target
        layer in this parametrisation actually exists on the ship.

        On failure, the source layer must retain the armor (rollback) and the
        target layer must remain unchanged.
        """
        from game.simulation.entities.ship import Ship
        from game.simulation.components.component import create_component

        ship = Ship(
            "Test Cruiser", 0, 0, (255, 255, 255),
            ship_class="Cruiser", registries=mock_registries,
        )
        armor = create_component('armor_plate', registries=mock_registries)
        assert ship.add_component(armor, LayerType.ARMOR), (
            "Test setup: armor must place in ARMOR before the move attempt."
        )
        armor_idx = ship.layers[LayerType.ARMOR].components.index(armor)
        target_before = list(ship.layers[target_layer].components)

        result = design_service.move_component(
            ship, LayerType.ARMOR, armor_idx, target_layer,
        )

        assert not result.success, (
            f"Armor must NOT be movable into {target_layer.name}; "
            f"VehicleDesignService.move_component should reject the move."
        )
        # Source rollback: armor still in ARMOR.
        assert armor in ship.layers[LayerType.ARMOR].components, (
            "Failed move must roll back the source-layer removal."
        )
        # Target unchanged.
        assert ship.layers[target_layer].components == target_before, (
            f"Failed move must not append to the target layer "
            f"({target_layer.name})."
        )


# ─────────────────────────────────────────────────────────────────
# WorkshopViewModel.move_component tests
# ─────────────────────────────────────────────────────────────────

class TestViewModelMoveComponent:
    """Tests for WorkshopViewModel.move_component — single component move."""

    def test_move_component_succeeds(self, viewmodel_with_ship):
        """Moving a single component between layers succeeds."""
        viewmodel, _, registries = viewmodel_with_ship

        # battery (Infrastructure) is valid in CORE and OUTER on Escort.
        viewmodel.add_component('battery', LayerType.OUTER)
        outer_before = len(viewmodel.ship.layers[LayerType.OUTER].components)

        # Move the last battery in OUTER (index = count-1) to CORE.
        idx = outer_before - 1
        result = viewmodel.move_component(LayerType.OUTER, idx, LayerType.CORE)

        assert result is True
        assert len(viewmodel.ship.layers[LayerType.OUTER].components) == outer_before - 1

    def test_move_component_emits_ship_updated(self, viewmodel_with_ship):
        """Moving a component emits SHIP_UPDATED event."""
        viewmodel, event_bus, _ = viewmodel_with_ship

        viewmodel.add_component('battery', LayerType.OUTER)
        outer_count = len(viewmodel.ship.layers[LayerType.OUTER].components)
        event_bus.clear()

        viewmodel.move_component(LayerType.OUTER, outer_count - 1, LayerType.CORE)

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

        comp = create_component('battery', registries=registries)
        comp.add_modifier('hardened_mount', 1.0)
        comp.recalculate_stats()

        viewmodel.add_component_instance(comp, LayerType.OUTER)
        idx = viewmodel.ship.layers[LayerType.OUTER].components.index(comp)

        viewmodel.move_component(LayerType.OUTER, idx, LayerType.CORE)

        # Same object instance in the target layer (modifiers preserved).
        target_comps = viewmodel.ship.layers[LayerType.CORE].components
        assert any(c is comp for c in target_comps), "Same instance should be in target layer"


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

        # Add 3 batteries (Infrastructure) to OUTER. Batteries are valid in
        # both CORE and OUTER, so the OUTER -> CORE group move is permitted.
        comps = []
        for _ in range(3):
            c = create_component('battery', registries=registries)
            viewmodel.add_component_instance(c, LayerType.OUTER)
            comps.append(c)

        group_key = get_component_group_key(comps[0])
        core_before = len(viewmodel.ship.layers[LayerType.CORE].components)

        result = viewmodel.move_component_group(group_key, LayerType.OUTER, LayerType.CORE)

        assert result is True
        core_after = len(viewmodel.ship.layers[LayerType.CORE].components)
        assert core_after >= core_before + 3

    def test_move_group_emits_ship_updated(self, viewmodel_with_ship):
        """Moving a group emits SHIP_UPDATED event."""
        viewmodel, event_bus, registries = viewmodel_with_ship
        from game.ui.screens.builder.grouping_strategies import get_component_group_key
        from game.simulation.components.component import create_component

        c = create_component('battery', registries=registries)
        viewmodel.add_component_instance(c, LayerType.OUTER)
        group_key = get_component_group_key(c)
        event_bus.clear()

        viewmodel.move_component_group(group_key, LayerType.OUTER, LayerType.CORE)

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1

    def test_move_group_no_matching_components(self, viewmodel_with_ship):
        """Returns False when no components match the group_key in source layer."""
        viewmodel, _, _ = viewmodel_with_ship

        result = viewmodel.move_component_group("nonexistent_group", LayerType.CORE, LayerType.OUTER)
        assert result is False
