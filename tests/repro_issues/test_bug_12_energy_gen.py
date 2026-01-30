"""
Reproduction Test for BUG-12: Generator not generating energy (shows 0 instead of 25/s)

Expected: Ship with Generator component should have energy generation rate of 25/s
Actual: Energy generation shows 0/s

ROOT CAUSE IDENTIFIED:
The Generator component has 'CrewRequired: 1' in its abilities definition.
When a ship lacks Crew Quarters or Life Support, the Generator is deactivated
due to unmet crew requirements, causing its ResourceGeneration to be skipped.
This is WORKING AS DESIGNED - not a code bug.

PROJ-50: Updated to use fresh_registries for DI.
"""
import pytest

from game.simulation.entities.ship import Ship, LayerType
from game.simulation.components.component import Component, load_components, create_component
from game.core.registry import RegistryManager
from game.simulation.entities.ship_stats import ShipStatsCalculator


def _get_layer_key(ship, layer_name):
    """Robust lookup by name to handle potential Enum identity issues."""
    for k in ship.layers:
        if k.name == layer_name:
            return k
    return None


def test_generator_without_crew_is_inactive(fresh_registries):
    """
    Demonstrates the 'bug' behavior: Generator shows 0 energy when ship has no crew.
    This is EXPECTED behavior - Generator requires crew to operate.

    PROJ-50: Updated to use DI via fresh_registries fixture.
    """
    # Setup test-specific vehicle classes in our registries
    test_vehicle_classes = {"Cruiser": {'max_mass': 5000, 'type': 'Ship'}}
    fresh_registries.vehicle_classes.update(test_vehicle_classes)

    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Cruiser", registries=fresh_registries)
    layer_key = _get_layer_key(ship, 'INNER')
    if layer_key is None:
        # Fallback for debug: what DO we have?
        print(f"DEBUG: Ship layers keys: {[k.name if hasattr(k, 'name') else str(k) for k in ship.layers]}")
        # If still None, append to a default layer if exists
        layer_key = list(ship.layers.keys())[0] if ship.layers else None

    # Add ONLY generator (no crew quarters/life support)
    generator = create_component("generator", registries=fresh_registries)
    ship.layers[layer_key]['components'].append(generator)
    generator.ship = ship

    calc = ShipStatsCalculator(fresh_registries.vehicle_classes)
    calc.calculate(ship)

    # Generator should be INACTIVE due to missing crew
    assert generator.is_active is False, "Generator should be INACTIVE without crew"

    # Energy generation rate should be 0 (because component is inactive)
    energy_resource = ship.resources.get_resource('energy')
    assert energy_resource is None or energy_resource.regen_rate == 0.0, \
        "Energy gen should be 0 when generator is inactive"


def test_generator_with_crew_is_active(fresh_registries):
    """
    Demonstrates correct behavior: Generator works when crew is available.

    PROJ-50: Updated to use DI via fresh_registries fixture.
    """
    # Setup test-specific vehicle classes in our registries
    test_vehicle_classes = {"Cruiser": {'max_mass': 5000, 'type': 'Ship'}}
    fresh_registries.vehicle_classes.update(test_vehicle_classes)

    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="Cruiser", registries=fresh_registries)
    layer_key = _get_layer_key(ship, 'INNER')
    if layer_key is None:
        layer_key = list(ship.layers.keys())[0] if ship.layers else None

    # Add crew support first
    quarters = create_component("crew_quarters", registries=fresh_registries)  # Provides crew capacity
    ship.layers[layer_key]['components'].append(quarters)
    quarters.ship = ship

    life_support = create_component("life_support", registries=fresh_registries)  # Provides life support
    ship.layers[layer_key]['components'].append(life_support)
    life_support.ship = ship

    # Now add generator
    generator = create_component("generator", registries=fresh_registries)
    ship.layers[layer_key]['components'].append(generator)
    generator.ship = ship

    calc = ShipStatsCalculator(fresh_registries.vehicle_classes)
    calc.calculate(ship)

    # Generator should be ACTIVE with crew available
    assert generator.is_active is True, f"Generator should be ACTIVE with crew. Status: {generator.status}"

    # Energy generation rate should be 25/s
    energy_resource = ship.resources.get_resource('energy')
    assert energy_resource is not None, "Energy resource not registered"
    assert energy_resource.regen_rate == 25.0, f"Energy gen rate should be 25.0, got {energy_resource.regen_rate}"


# Note: __main__ block removed since tests now require fresh_registries fixture
# Run tests via pytest instead: pytest tests/repro_issues/test_bug_12_energy_gen.py -v
