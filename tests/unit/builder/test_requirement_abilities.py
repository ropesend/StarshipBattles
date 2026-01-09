import pytest
from game.simulation.entities.ship import Ship
from game.simulation.components.component import Component, LayerType
from game.core.registry import RegistryManager
from game.simulation.ship_validator import ShipDesignValidator
from game.simulation.entities.ship_stats import ShipStatsCalculator

@pytest.fixture
def registry_setup():
    """Setup custom registry data for requirement ability testing."""
    mgr = RegistryManager.instance()
    mgr.clear()
    
    # Define a simple vehicle class
    mgr.vehicle_classes.update({
        "TestClass": {
            "type": "Ship",
            "max_mass": 1000,
            "default_hull_id": "test_hull",
            "layers": [
                {"type": "CORE", "radius_pct": 0.2, "restrictions": []},
                {"type": "OUTER", "radius_pct": 0.5, "restrictions": []},
            ]
        }
    })
    
    # Define Hull with requirements
    hull_data = {
        "id": "test_hull",
        "name": "Requirement Hull",
        "type": "Hull",
        "mass": 50,
        "hp": 100,
        "abilities": {
            "RequiresCommandAndControl": True,
            "RequiresCombatMovement": True
        }
    }
    mgr.components["test_hull"] = Component(hull_data)
    
    # Define Bridge (provides C&C)
    bridge_data = {
        "id": "test_bridge",
        "name": "Test Bridge",
        "type": "Bridge",
        "mass": 10,
        "hp": 50,
        "abilities": {"CommandAndControl": True}
    }
    mgr.components["test_bridge"] = Component(bridge_data)
    
    # Define Engine (provides CombatPropulsion)
    engine_data = {
        "id": "test_engine",
        "name": "Test Engine",
        "type": "Engine",
        "mass": 20,
        "hp": 50,
        "abilities": {"CombatPropulsion": 100} # Numeric value
    }
    mgr.components["test_engine"] = Component(engine_data)
    
    yield mgr
    mgr.clear()

def test_marker_abilities_tallied_as_boolean(registry_setup):
    """Verify that ShipStatsCalculator tallies marker abilities (no numeric value) as True."""
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
    
    stats_calculator = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)
    all_components = [c for layer in ship.layers.values() for c in layer['components']]
    
    totals = stats_calculator.calculate_ability_totals(all_components)
    
    # Marker abilities from hull should be True
    assert totals.get("RequiresCommandAndControl") is True
    assert totals.get("RequiresCombatMovement") is True
    
    # CommandAndControl (explicitly set to True in calculator override)
    # Bridge isn't added yet, so it should be missing
    assert "CommandAndControl" not in totals

def test_validation_fails_when_markers_unmet(registry_setup):
    """Verify that validator fails if markers are present but capabilities are missing."""
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
    validator = ShipDesignValidator()
    
    result = validator.validate_design(ship)
    assert not result.is_valid
    assert any("Needs Command capability" in e for e in result.errors)
    assert any("Needs Combat propulsion" in e for e in result.errors)

def test_validation_passes_when_requirements_met(registry_setup):
    """Verify that validator passes when Bridge and Engine are added to satisfy hull markers."""
    ship = Ship(name="TestShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
    
    # Add Bridge to CORE
    from game.simulation.components.component import create_component
    bridge = create_component("test_bridge")
    ship.add_component(bridge, LayerType.CORE)
    
    # Add Engine to OUTER
    engine = create_component("test_engine")
    ship.add_component(engine, LayerType.OUTER)
    
    validator = ShipDesignValidator()
    result = validator.validate_design(ship)
    
    # Should be valid now (Bridge provides C&C, Engine provides CombatPropulsion)
    assert result.is_valid, f"Validation failed unexpectedly: {result.errors}"

def test_satellite_hull_requirements(registry_setup):
    """Verify marker validation for a Satellite (which only requires C&C)."""
    mgr = RegistryManager.instance()
    mgr.vehicle_classes["SatClass"] = {
        "type": "Satellite",
        "max_mass": 100,
        "default_hull_id": "sat_hull",
        "layers": [{"type": "CORE", "radius_pct": 1.0, "restrictions": []}]
    }
    
    sat_hull_data = {
        "id": "sat_hull",
        "name": "Sat Hull",
        "type": "Hull",
        "mass": 10,
        "hp": 20,
        "abilities": {"RequiresCommandAndControl": True}
    }
    mgr.components["sat_hull"] = Component(sat_hull_data)
    
    ship = Ship(name="TestSat", x=0, y=0, color=(255, 255, 255), ship_class="SatClass")
    validator = ShipDesignValidator()
    
    # Should fail for C&C but NOT for Propulsion
    result = validator.validate_design(ship)
    assert not result.is_valid
    assert any("Needs Command capability" in e for e in result.errors)
    assert not any("Needs Combat propulsion" in e for e in result.errors)

def test_redundant_requirements_satisfied(registry_setup):
    """Verify that multiple components providing the same capability satisfy the requirement."""
    ship = Ship(name="RedundantShip", x=0, y=0, color=(255, 255, 255), ship_class="TestClass")
    from game.simulation.components.component import create_component
    
    # Add TWO bridges
    ship.add_component(create_component("test_bridge"), LayerType.CORE)
    ship.add_component(create_component("test_bridge"), LayerType.CORE)
    
    # Add one engine
    ship.add_component(create_component("test_engine"), LayerType.OUTER)
    
    validator = ShipDesignValidator()
    result = validator.validate_design(ship)
    assert result.is_valid

def test_stats_calculator_direct_marker_check(registry_setup):
    """Directly test ShipStatsCalculator for marker ability tallying."""
    from game.simulation.components.component import create_component
    hull = create_component("test_hull")
    
    stats_calculator = ShipStatsCalculator(RegistryManager.instance().vehicle_classes)
    totals = stats_calculator.calculate_ability_totals([hull])
    
    # Marker abilities (Requires...) should be True
    assert totals.get("RequiresCommandAndControl") is True
    assert totals.get("RequiresCombatMovement") is True
    
    # Non-existent ability should be missing (not False/0)
    assert "NonExistent" not in totals
