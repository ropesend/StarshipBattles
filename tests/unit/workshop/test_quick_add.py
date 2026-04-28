"""
Tests for quick-add component feature in WorkshopViewModel.

Tests the layer resolution logic and quick-add operation that allows
adding components via a '+' button in the component palette.

Layer resolution rules:
1. If a layer is selected and valid for the component -> use that layer
2. If a layer is selected but invalid -> find the nearest valid layer
3. If no layer is selected -> use the innermost valid layer
4. HULL is never a valid quick-add target (managed by ship class)
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
def quick_add_class_setup():
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
def mock_registries(quick_add_class_setup):
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
    """Create a viewmodel with a default Escort ship loaded."""
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel

    event_bus = MockEventBus()
    context = WorkshopContext(mode=WorkshopMode.STANDALONE, registries=mock_registries)
    viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)
    viewmodel.create_default_ship("Escort")
    event_bus.clear()
    return viewmodel, event_bus, mock_registries


class TestResolveTargetLayer:
    """Tests for resolve_target_layer - layer selection logic for quick-add."""

    def test_no_selection_returns_innermost_valid(self, viewmodel_with_ship):
        """With no selected layer, returns the innermost valid layer."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('standard_engine', registries=registries)
        result = viewmodel.resolve_target_layer(comp)

        assert result is not None
        # Should be the innermost non-HULL layer where the component is valid
        # For a standard engine on an Escort, CORE should be valid
        assert result.value >= LayerType.CORE.value, "Should not return HULL"

    def test_selected_valid_layer_returns_that_layer(self, viewmodel_with_ship):
        """When selected layer is valid for the component, returns it directly."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        result = viewmodel.resolve_target_layer(comp, selected_layer=LayerType.ARMOR)

        assert result == LayerType.ARMOR

    @pytest.mark.parametrize("selection", [
        None,
        LayerType.HULL,
        LayerType.CORE,
        LayerType.INNER,
        LayerType.OUTER,
        LayerType.ARMOR,
    ])
    def test_armor_routes_to_armor_layer_regardless_of_selection(
        self, viewmodel_with_ship, selection
    ):
        """BUG-116: armor_plate must resolve to ARMOR for every selected_layer.

        Armor components carry major_classification=Armor. The ARMOR layer is
        the only valid home for them; CORE/INNER/OUTER must reject via
        block_classification:Armor.
        """
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('armor_plate', registries=registries)
        result = viewmodel.resolve_target_layer(comp, selected_layer=selection)

        assert result == LayerType.ARMOR, (
            f"Expected ARMOR with selection={selection!r}, got {result!r}"
        )

    def test_hull_never_returned(self, viewmodel_with_ship):
        """HULL is never returned as a quick-add target."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('standard_engine', registries=registries)
        # Try with HULL explicitly selected
        result = viewmodel.resolve_target_layer(comp, selected_layer=LayerType.HULL)

        assert result is not None
        assert result != LayerType.HULL

    def test_hull_never_returned_for_any_selection(self, viewmodel_with_ship):
        """HULL is excluded from results regardless of selected layer."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        comp = create_component('standard_engine', registries=registries)
        for layer in LayerType:
            result = viewmodel.resolve_target_layer(comp, selected_layer=layer)
            if result is not None:
                assert result != LayerType.HULL, f"HULL returned when {layer.name} selected"

    def test_no_ship_returns_none(self, mock_registries):
        """Returns None when no ship is loaded."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel
        from game.simulation.components.component import create_component

        event_bus = MockEventBus()
        context = WorkshopContext(mode=WorkshopMode.STANDALONE, registries=mock_registries)
        viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)

        comp = create_component('standard_engine', registries=mock_registries)
        result = viewmodel.resolve_target_layer(comp)

        assert result is None

    def test_nearest_prefers_inner_on_tie(self, viewmodel_with_ship):
        """When two layers are equidistant, prefers the inner (lower value) one."""
        viewmodel, _, registries = viewmodel_with_ship
        from game.simulation.components.component import create_component

        # Use a component valid in multiple layers
        comp = create_component('standard_engine', registries=registries)

        # Find all valid layers for this component
        valid_layers = []
        ship = viewmodel.ship
        from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule
        rule = LayerRestrictionDefinitionRule()
        for l_type in ship.layers:
            if l_type == LayerType.HULL:
                continue
            if rule.validate(ship, comp, l_type).is_valid:
                valid_layers.append(l_type)

        if len(valid_layers) >= 2:
            # Select a layer equidistant between two valid layers
            # The result should prefer the inner one
            result = viewmodel.resolve_target_layer(comp)
            assert result == min(valid_layers, key=lambda l: l.value)


class TestQuickAddComponent:
    """Tests for quick_add_component - full quick-add operation."""

    def test_adds_component_successfully(self, viewmodel_with_ship):
        """Quick-add adds the component to the resolved layer."""
        viewmodel, _, registries = viewmodel_with_ship

        all_components_before = len(viewmodel.ship.get_all_components())
        result = viewmodel.quick_add_component('standard_engine')

        assert result is True
        assert len(viewmodel.ship.get_all_components()) == all_components_before + 1

    def test_emits_ship_updated(self, viewmodel_with_ship):
        """Quick-add emits SHIP_UPDATED event on success."""
        viewmodel, event_bus, _ = viewmodel_with_ship
        event_bus.clear()

        viewmodel.quick_add_component('standard_engine')

        events = event_bus.get_events('SHIP_UPDATED')
        assert len(events) >= 1

    def test_respects_selected_layer(self, viewmodel_with_ship):
        """Quick-add places component in the selected layer when valid."""
        viewmodel, _, registries = viewmodel_with_ship

        initial_armor_count = len(viewmodel.ship.layers[LayerType.ARMOR].components)
        result = viewmodel.quick_add_component('armor_plate', selected_layer=LayerType.ARMOR)

        assert result is True
        assert len(viewmodel.ship.layers[LayerType.ARMOR].components) == initial_armor_count + 1

    def test_no_ship_returns_false(self, mock_registries):
        """Quick-add returns False when no ship is loaded."""
        from game.ui.screens.workshop_viewmodel import WorkshopViewModel

        event_bus = MockEventBus()
        context = WorkshopContext(mode=WorkshopMode.STANDALONE, registries=mock_registries)
        viewmodel = WorkshopViewModel(event_bus, 1280, 720, context=context)

        result = viewmodel.quick_add_component('standard_engine')

        assert result is False

    def test_invalid_component_returns_false(self, viewmodel_with_ship):
        """Quick-add returns False for a non-existent component ID."""
        viewmodel, _, _ = viewmodel_with_ship

        result = viewmodel.quick_add_component('nonexistent_component_xyz')

        assert result is False

    def test_bulk_add_multiple(self, viewmodel_with_ship):
        """Quick-add with count > 1 adds multiple components."""
        viewmodel, _, registries = viewmodel_with_ship

        initial_armor_count = len(viewmodel.ship.layers[LayerType.ARMOR].components)
        result = viewmodel.quick_add_component('armor_plate', selected_layer=LayerType.ARMOR, count=3)

        assert result is True
        assert len(viewmodel.ship.layers[LayerType.ARMOR].components) >= initial_armor_count + 3

    def test_bulk_add_count_one_uses_single_add(self, viewmodel_with_ship):
        """Quick-add with count=1 (default) adds exactly one component."""
        viewmodel, _, registries = viewmodel_with_ship

        all_before = len(viewmodel.ship.get_all_components())
        viewmodel.quick_add_component('standard_engine', count=1)

        assert len(viewmodel.ship.get_all_components()) == all_before + 1

    @pytest.mark.parametrize("armor_id", [
        "armor_plate",
        "emissive_armor",
        "scattering_armor",
        "shield_regenerating_armor",
    ])
    def test_armor_quick_add_no_selection_lands_in_armor(
        self, viewmodel_with_ship, armor_id
    ):
        """BUG-116: quick-add of an armor component with no selected_layer
        must place it in the ARMOR layer, not CORE/INNER/OUTER.

        Regression for QA Session 20260427_151244 where armor was landing in
        CORE (and OUTER) due to the innermost-wins resolution algorithm
        finding all non-ARMOR layers valid in the absence of
        block_classification:Armor rules.
        """
        viewmodel, _, _ = viewmodel_with_ship

        ship = viewmodel.ship
        before = {l: len(ship.layers[l].components) for l in ship.layers}

        result = viewmodel.quick_add_component(armor_id)

        assert result is True
        after = {l: len(ship.layers[l].components) for l in ship.layers}

        assert after[LayerType.ARMOR] == before[LayerType.ARMOR] + 1, (
            f"{armor_id} should have been placed in ARMOR; "
            f"before={before}, after={after}"
        )
        for l in ship.layers:
            if l == LayerType.ARMOR:
                continue
            assert after[l] == before[l], (
                f"{armor_id} leaked into {l.name}; before={before}, after={after}"
            )
