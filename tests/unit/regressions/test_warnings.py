import pytest
from unittest.mock import MagicMock, patch
import pygame

from game.simulation.entities.ship import Ship, LayerType
from game.core.registry import RegistryManager
from game.simulation.components.component import Component


@pytest.fixture
def ship_with_registry(fresh_registries):
    """Set up pygame, registry, and ship for testing."""
    if not pygame.get_init():
        pygame.init()
    # Ensure 'Cruiser' exists
    if "Cruiser" not in RegistryManager.instance().vehicle_classes:
        RegistryManager.instance().vehicle_classes["Cruiser"] = {"max_mass": 16000, "default_hull_id": "hull_cruiser"}

    ship = Ship("Test Ship", 0, 0, (255, 255, 255), ship_class="Cruiser", registries=fresh_registries)

    yield ship, fresh_registries

    pygame.quit()


@pytest.fixture
def base_data():
    """Base component data for creating test components."""
    return {
        "id": "test_comp",
        "name": "Test Comp",
        "type": "Component",
        "mass": 10,
        "hp": 10,
        "allowed_layers": ["INNER", "OUTER", "CORE"],
        "allowed_vehicle_types": ["Ship"],
        "abilities": {}
    }


def create_comp(base_data, registries, **kwargs):
    """Helper to create component with modified data."""
    data = base_data.copy()
    data.update(kwargs)
    return Component(data, registries=registries)


class TestValidationWarnings:
    def test_fuel_warning(self, ship_with_registry, base_data):
        ship, registries = ship_with_registry

        # Add Engine requiring fuel
        engine_abilities = {
            "ResourceConsumption": [{"resource": "fuel", "amount": 10, "trigger": "constant"}]
        }
        engine = create_comp(base_data, registries, id="engine", type="Engine", abilities=engine_abilities)

        ship.add_component(engine, LayerType.INNER)

        warnings = ship.get_validation_warnings()
        assert any("Needs Fuel Storage" in w for w in warnings), f"Expected 'Needs Fuel Storage', got {warnings}"

        # Add Fuel Tank
        tank_abilities = {
            "ResourceStorage": [{"resource": "fuel", "amount": 100}]
        }
        tank = create_comp(base_data, registries, id="tank", type="Tank", abilities=tank_abilities)
        ship.add_component(tank, LayerType.INNER)

        warnings = ship.get_validation_warnings()
        assert not any("Needs Fuel Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}"

    def test_ammo_warning(self, ship_with_registry, base_data):
        ship, registries = ship_with_registry

        # Add Railgun requiring ammo
        gun_abilities = {
            "ResourceConsumption": [{"resource": "ammo", "amount": 1, "trigger": "activation"}]
        }
        gun = create_comp(base_data, registries, id="railgun", type="ProjectileWeapon", abilities=gun_abilities)
        ship.add_component(gun, LayerType.OUTER)

        warnings = ship.get_validation_warnings()
        assert any("Needs Ammo Storage" in w for w in warnings), f"Expected 'Needs Ammo Storage', got {warnings}"

        # Add Ordnance Tank
        tank_abilities = {
            "ResourceStorage": [{"resource": "ammo", "amount": 100}]
        }
        tank = create_comp(base_data, registries, id="ammo_tank", type="Tank", abilities=tank_abilities)
        ship.add_component(tank, LayerType.INNER)

        warnings = ship.get_validation_warnings()
        assert not any("Needs Ammo Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}"

    def test_energy_warning(self, ship_with_registry, base_data):
        ship, registries = ship_with_registry

        # Add Laser requiring energy
        laser_abilities = {
            "ResourceConsumption": [{"resource": "energy", "amount": 5, "trigger": "activation"}]
        }
        laser = create_comp(base_data, registries, id="laser", type="BeamWeapon", abilities=laser_abilities)
        ship.add_component(laser, LayerType.OUTER)

        warnings = ship.get_validation_warnings()
        assert any("Needs Energy Storage" in w for w in warnings), f"Expected 'Needs Energy Storage', got {warnings}"

        # Add Battery
        battery_abilities = {
            "ResourceStorage": [{"resource": "energy", "amount": 1000}]
        }
        battery = create_comp(base_data, registries, id="battery", type="Tank", abilities=battery_abilities)
        ship.add_component(battery, LayerType.INNER)

        warnings = ship.get_validation_warnings()
        assert not any("Needs Energy Storage" in w for w in warnings), f"Warning should be resolved, got {warnings}"
