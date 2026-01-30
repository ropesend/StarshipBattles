import pytest
from unittest.mock import MagicMock
from game.simulation.components.component import Component
from game.simulation.components.abilities import CombatPropulsion, ResourceConsumption, WeaponAbility


@pytest.fixture
def mock_ship():
    mock = MagicMock()
    mock.resources = MagicMock()
    return mock


class TestComponentComposition:

    def test_generic_engine_construction(self, mock_ship, fresh_registries):
        # A generic component that acts as an engine via composition
        data = {
            "id": "gen_eng_1",
            "name": "Generic Engine",
            "type": "Generic",
            "mass": 100,
            "hp": 50,
            "abilities": {
                "CombatPropulsion": 1000,
                # Use explicit dict to ensure constant trigger for testing idle consumption
                "ResourceConsumption": {"resource": "energy", "amount": 10, "trigger": "constant"}
            }
        }

        comp = Component(data, registries=fresh_registries)
        comp.ship = mock_ship

        # Verify Abilities exist
        assert comp.has_ability("CombatPropulsion")
        assert comp.has_ability("ResourceConsumption")

        # Verify Attributes via helper
        prop = comp.get_ability("CombatPropulsion")
        assert prop.thrust_force == 1000

        # Test Operation (Resource Consumption)
        # Mock resource
        mock_energy = MagicMock()
        mock_energy.consume.return_value = True
        mock_ship.resources.get_resource.return_value = mock_energy

        comp.update()
        assert comp.is_operational

        # Test Starvation
        mock_energy.consume.return_value = False
        comp.update()
        assert not comp.is_operational, "Component should be non-operational if constant resource consumption fails"

    def test_generic_weapon_composition(self, fresh_registries):
        data = {
            "id": "gen_wep_1",
            "name": "Generic Gun",
            "type": "Generic",
            "mass": 50, # Added mass
            "hp": 20,
            "abilities": {
                "ProjectileWeaponAbility": {
                    "damage": 50,
                    "range": 1000,
                    "reload": 2.0
                }
            }
        }

        comp = Component(data, registries=fresh_registries)

        wep = comp.get_ability("WeaponAbility") # Polymorphic lookup
        assert wep is not None
        assert wep.damage == 50
        assert wep.reload_time == 2.0

        # Verify we can also find it by specific type
        proj = comp.get_ability("ProjectileWeaponAbility")
        assert proj is not None
        assert proj == wep

    def test_get_ui_rows_aggregation(self, fresh_registries):
        """Test that Component.get_ui_rows() aggregates from all abilities."""
        data = {
            "id": "test_ui",
            "name": "Test Component",
            "type": "Generic",
            "mass": 100,
            "hp": 50,
            "abilities": {
                "CombatPropulsion": 1500,
                "ResourceConsumption": {"resource": "fuel", "amount": 5, "trigger": "constant"}
            }
        }

        comp = Component(data, registries=fresh_registries)
        rows = comp.get_ui_rows()

        # Should have rows from both abilities
        assert isinstance(rows, list)
        assert len(rows) > 0

        # Check for expected labels
        labels = [r['label'] for r in rows]
        assert 'Thrust' in labels
        assert 'Fuel Use' in labels
