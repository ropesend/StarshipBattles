import pytest
from unittest.mock import MagicMock, patch
from game.simulation.entities.ship import Ship
from game.simulation.components import Component, LayerType
from game.core.registry import RegistryManager
# Assuming registry is populated or we mock it.
# Better to mock components or use a minimal test case without full registry dependency if possible.


class TestShipCaching:
    @pytest.fixture(autouse=True)
    def setup(self):
        # Create a basic ship
        self.ship = Ship("Test Ship", 0, 0, (255, 255, 255))

        yield

        RegistryManager.instance().clear()
        patch.stopall()

    def test_cached_summary_empty_initially(self):
        assert self.ship.cached_summary == {}

    def test_cached_summary_populated_after_calc(self):
        # Create a mock weapon component
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"damage": 10, "reload": 1.0, "range": 1000}
            }
        }
        weapon = Component(weapon_data)

        # Add to ship - use CORE layer (not HULL, which only accepts hull components)
        self.ship.add_component(weapon, LayerType.CORE)

        summary = self.ship.cached_summary
        assert summary
        assert 'dps' in summary
        assert 'mass' in summary

        # Verify values
        assert summary['dps'] == 10.0  # 10 / 1.0
        assert summary['range'] == 1000
        # Mass: Hull component (50 for Escort) + weapon component (10) = 60
        assert summary['mass'] == 60.0

    def test_cached_summary_updates(self):
        # Add weapon
        weapon_data = {
            "id": "TestWeapon",
            "name": "Test Laser",
            "type": "Weapon",
            "mass": 10,
            "hp": 50,
            "abilities": {
                "WeaponAbility": {"damage": 10, "reload": 2.0, "range": 500}
            }
        }
        weapon = Component(weapon_data)
        self.ship.add_component(weapon, LayerType.CORE)

        summary = self.ship.cached_summary
        assert summary['dps'] == 5.0

        # Add another identical weapon
        weapon2 = Component(weapon_data)
        self.ship.add_component(weapon2, LayerType.CORE)

        summary = self.ship.cached_summary
        assert summary['dps'] == 10.0
        # Mass: Hull component (50) + 2 weapons (10 + 10) = 70
        assert summary['mass'] == 70.0
