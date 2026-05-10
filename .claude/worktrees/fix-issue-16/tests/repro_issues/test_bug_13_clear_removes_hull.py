"""
BUG-13 Reproduction Test: Clear Design removes hull.

PROJ-40: Updated to use DI pattern with WorkshopContext.
PROJ-43: Updated to remove deprecated registry function patches.
"""
import pytest
from unittest.mock import MagicMock
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component
from game.core.constants import LayerType
from game.core.registry import GameRegistries
from game.ui.screens.workshop_screen import DesignWorkshopScreen
from game.ui.screens.workshop_context import WorkshopContext, WorkshopMode
from game.simulation.entities.layer_data import LayerData


@pytest.fixture
def simple_ship_registry(fresh_registries):
    """Set up registry with minimal ship data for testing."""
    classes = {
        "Escort": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "hull_escort",
            "layers": [
                {"type": "HULL", "radius_pct": 0.1, "max_mass_pct": 0.2},
                {"type": "CORE", "radius_pct": 0.5, "max_mass_pct": 1.0}
            ]
        }
    }

    components = {
        "hull_escort": {
            "id": "hull_escort",
            "name": "Escort Hull",
            "type": "Hull",
            "mass": 100,
            "hp": 500
        }
    }

    # Set up fresh_registries with test data (DI pattern - PROJ-195)
    fresh_registries.vehicle_classes.update(classes)
    for comp_id, comp_data in components.items():
        fresh_registries.components[comp_id] = Component(comp_data, registries=fresh_registries)

    yield classes, components, fresh_registries


def test_clear_design_removes_hull_logic_repro(simple_ship_registry):
    """
    BUG-13 Regression: Verify that clear_design preserves the hull component.

    The original bug caused _clear_design to remove all components including
    the mandatory hull. The fix delegates to viewmodel.clear_design() which
    calls ship.clear_non_hull_components(), preserving the hull.
    """
    classes, components, fresh_registries = simple_ship_registry

    # Instantiate DesignWorkshopScreen without calling __init__ to avoid UI complexity
    gui = DesignWorkshopScreen.__new__(DesignWorkshopScreen)

    # Setup minimal required state - MVVM architecture requires viewmodel
    from game.ui.screens.builder.event_bus import EventBus
    from game.ui.screens.workshop_viewmodel import WorkshopViewModel

    # Create registries for DI - use fresh_registries components (PROJ-195)
    registries = GameRegistries(
        components={k: v for k, v in fresh_registries.components.items()},
        modifiers={},
        vehicle_classes=classes,
        resources={},
        resource_catalog=fresh_registries.resource_catalog,
    )
    context = WorkshopContext(
        mode=WorkshopMode.STANDALONE,
        registries=registries
    )

    gui.event_bus = EventBus()
    gui.viewmodel = WorkshopViewModel(gui.event_bus, 1280, 720, context=context)

    # Setup ship via viewmodel with DI registries
    gui.viewmodel._ship = Ship(
        "Test Ship", 0, 0, (255, 255, 255),
        ship_class="Escort",
        registries=registries
    )
    gui.viewmodel._template_modifiers = {"some_mod": 1.0}

    gui.controller = MagicMock()
    gui.right_panel = MagicMock()
    gui.modifier_panel = MagicMock()
    gui.layer_panel = MagicMock()
    gui.weapons_report_panel = MagicMock()

    # Verify initial hull exists (added by Ship.__init__ for Escort class)
    hull_comps = gui.viewmodel.ship.layers[LayerType.HULL].components
    assert len(hull_comps) == 1, "Ship should start with a hull component"

    # Add a non-hull component to another layer
    laser = Component({"id": "small_laser", "name": "Laser", "type": "Weapon", "mass": 10, "hp": 50},
                      registries=registries)
    gui.viewmodel.ship.layers[LayerType.CORE].components.append(laser)

    # Trigger clear design - this now delegates to viewmodel.clear_design()
    # which properly preserves the hull
    DesignWorkshopScreen._clear_design(gui)

    # Verify the fix is working:
    # 1. Non-hull component is correctly removed
    assert len(gui.viewmodel.ship.layers[LayerType.CORE].components) == 0, \
        "CORE layer should be cleared"

    # 2. Hull component is preserved (this was the bug - hull was removed)
    hull_comps_after = gui.viewmodel.ship.layers[LayerType.HULL].components
    assert len(hull_comps_after) > 0, \
        "BUG-13: Hull component should NOT be removed by Clear Design"


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__]))
