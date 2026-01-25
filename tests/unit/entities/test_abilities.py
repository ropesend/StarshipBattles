import pytest
from unittest.mock import MagicMock
from game.simulation.components.abilities import (
    create_ability,
    Ability,
    ResourceConsumption,
    ResourceStorage,
    CombatPropulsion,
    ManeuveringThruster,
    WeaponAbility,
    ProjectileWeaponAbility,
    VehicleLaunchAbility
)


@pytest.fixture
def mock_component():
    """Create a mock component with ship and resources."""
    mock_comp = MagicMock()
    mock_ship = MagicMock()
    mock_comp.ship = mock_ship
    mock_resources = MagicMock()
    mock_ship.resources = mock_resources
    return mock_comp


class TestAbilities:
    def test_create_ability_primitives(self, mock_component):
        # Test creation from primitive shortcuts
        ab = create_ability("CombatPropulsion", mock_component, 1500)
        assert isinstance(ab, CombatPropulsion)
        assert ab.thrust_force == 1500

        ab = create_ability("FuelStorage", mock_component, 2000)
        assert isinstance(ab, ResourceStorage)
        assert ab.resource_type == "fuel"
        assert ab.max_amount == 2000

    def test_create_ability_dict(self, mock_component):
        # Test creation from dict
        data = {"value": 50, "tags": ["test"]}
        ab = create_ability("ManeuveringThruster", mock_component, data)
        assert isinstance(ab, ManeuveringThruster)
        assert ab.turn_rate == 50
        assert "test" in ab.tags

    def test_resource_consumption_constant(self, mock_component):
        # Test constant consumption update
        data = {"resource": "fuel", "amount": 10, "trigger": "constant"}
        ab = ResourceConsumption(mock_component, data)

        # Setup mock resource
        mock_fuel = MagicMock()
        mock_fuel.consume.return_value = True
        mock_component.ship.resources.get_resource.return_value = mock_fuel

        # Update (tick)
        result = ab.update()
        assert result is True
        # Should consume amount * 0.01
        mock_fuel.consume.assert_called_with(0.1)

    def test_resource_consumption_activation(self, mock_component):
        # Test activation trigger
        data = {"resource": "energy", "amount": 5, "trigger": "activation"}
        ab = ResourceConsumption(mock_component, data)

        # Update shouldn't consume
        ab.update()
        mock_component.ship.resources.get_resource.assert_not_called()

        # Manual consumption
        mock_energy = MagicMock()
        mock_energy.consume.return_value = True
        mock_component.ship.resources.get_resource.return_value = mock_energy

        success = ab.check_and_consume()
        assert success is True
        mock_energy.consume.assert_called_with(5)

    def test_weapon_ability(self, mock_component):
        data = {
            "damage": 50,
            "range": 1000,
            "cooldown": 2.0,  # Not used, uses reload usually or similar
            "reload": 1.5,
            "projectile_speed": 800
        }
        ab = create_ability("ProjectileWeaponAbility", mock_component, data)
        assert isinstance(ab, ProjectileWeaponAbility)
        assert ab.damage == 50
        assert isinstance(ab, WeaponAbility)
        assert ab.projectile_speed == 800

        # Cooldown Logic
        assert ab.can_fire() is True
        ab.fire(target=None)
        assert ab.can_fire() is False
        assert ab.cooldown_timer == 1.5

        # Update decrements
        ab.update()  # -0.01
        assert ab.cooldown_timer == pytest.approx(1.49)

    def test_vehicle_launch(self, mock_component):
        data = {"fighter_class": "Ace Fighter", "cycle_time": 2.0}
        ab = VehicleLaunchAbility(mock_component, data)

        assert ab.try_launch() is True
        assert ab.try_launch() is False  # Cooldown active

        # fast forward
        ab.cooldown = 0
        assert ab.try_launch() is True

    def test_ui_rows(self, mock_component):
        ab = CombatPropulsion(mock_component, 100)
        rows = ab.get_ui_rows()
        assert rows[0]['label'] == 'Thrust'
        assert rows[0]['value'] == '100 N'
        assert rows[0]['color_hint'] == '#64FF64'

    def test_beam_weapon_ability(self, mock_component):
        from game.simulation.components.abilities import BeamWeaponAbility
        data = {
            "damage": 30,
            "range": 2000,
            "reload": 0.5,
            "accuracy_falloff": 0.002,
            "base_accuracy": 2.0
        }
        ab = create_ability("BeamWeaponAbility", mock_component, data)
        assert isinstance(ab, BeamWeaponAbility)
        assert isinstance(ab, WeaponAbility)  # Polymorphism check
        assert ab.damage == 30
        assert ab.accuracy_falloff == 0.002
        assert ab.base_accuracy == 2.0

    def test_seeker_weapon_ability(self, mock_component):
        from game.simulation.components.abilities import SeekerWeaponAbility
        data = {
            "damage": 100,
            "reload": 5.0,
            "projectile_speed": 500,
            "endurance": 10.0,
            "turn_rate": 45.0,
            "to_hit_defense": 1.5
        }
        ab = create_ability("SeekerWeaponAbility", mock_component, data)
        assert isinstance(ab, SeekerWeaponAbility)
        assert isinstance(ab, WeaponAbility)  # Polymorphism check
        assert ab.projectile_speed == 500
        assert ab.endurance == 10.0
        assert ab.turn_rate == 45.0
        assert ab.to_hit_defense == 1.5
        # Range should be auto-calculated: speed * endurance * 0.8 (maneuvering efficiency)
        assert ab.range == 4000  # 500 * 10 * 0.8

    def test_get_abilities_polymorphism(self):
        """Test that get_abilities() finds abilities by parent class."""
        from game.simulation.components import Component
        data = {
            "id": "poly_test",
            "name": "Polymorphism Test",
            "type": "Generic",
            "mass": 10,
            "hp": 10,
            "abilities": {
                "BeamWeaponAbility": {"damage": 20, "range": 1000, "reload": 1.0}
            }
        }
        comp = Component(data)

        # Should find via polymorphic lookup (BeamWeaponAbility IS-A WeaponAbility)
        weapons = comp.get_abilities("WeaponAbility")
        assert len(weapons) == 1

        # Should also find via exact match
        beams = comp.get_abilities("BeamWeaponAbility")
        assert len(beams) == 1
        assert weapons[0] == beams[0]

    def test_has_pdc_ability(self):
        """Test has_pdc_ability() with tag-based detection."""
        from game.simulation.components import Component
        # Component with 'pdc' tag
        data = {
            "id": "pdc_test",
            "name": "Point Defense Gun",
            "type": "Weapon",
            "mass": 5,
            "hp": 10,
            "abilities": {
                "ProjectileWeaponAbility": {"damage": 5, "range": 500, "reload": 0.1, "tags": ["pdc"]}
            }
        }
        comp = Component(data)
        assert comp.has_pdc_ability() is True

        # Component without 'pdc' tag
        data2 = {
            "id": "regular_test",
            "name": "Regular Gun",
            "type": "Weapon",
            "mass": 5,
            "hp": 10,
            "abilities": {
                "ProjectileWeaponAbility": {"damage": 10, "range": 1000, "reload": 1.0}
            }
        }
        comp2 = Component(data2)
        assert comp2.has_pdc_ability() is False


class TestAbilityFactoryErrorLogging:
    """Tests for ability factory error logging (ERR-014)."""

    def test_create_ability_failure_logs_warning(self, mock_component, caplog):
        """Ability creation failure should log warning with ability name (ERR-014)."""
        import logging
        from unittest.mock import patch

        # Force an exception during ability construction
        with patch.dict('game.simulation.components.abilities.ABILITY_REGISTRY',
                       {'TestBrokenAbility': MagicMock(side_effect=ValueError("Test error"))}):
            with caplog.at_level(logging.WARNING):
                result = create_ability("TestBrokenAbility", mock_component, {"data": "test"})

            assert result is None
            # Should have logged a warning
            warning_logs = [r for r in caplog.records if r.levelno >= logging.WARNING]
            assert len(warning_logs) > 0, "Should log warning when ability creation fails"
            warning_text = ' '.join(r.message for r in warning_logs)
            assert 'TestBrokenAbility' in warning_text, \
                f"Warning should include ability name. Got: {warning_text}"

    def test_create_ability_success_no_warning(self, mock_component, caplog):
        """Successful ability creation should not produce warnings."""
        import logging

        with caplog.at_level(logging.WARNING):
            result = create_ability("CombatPropulsion", mock_component, 1000)

        assert result is not None
        # Should NOT log warnings for successful creation
        ability_warnings = [r for r in caplog.records
                          if 'CombatPropulsion' in r.message or 'ability' in r.message.lower()]
        assert len(ability_warnings) == 0, "Successful creation should not log warnings"

    def test_unknown_ability_returns_none_silently(self, mock_component, caplog):
        """Unknown ability name should return None without warning (expected behavior)."""
        import logging

        with caplog.at_level(logging.WARNING):
            result = create_ability("NonexistentAbility", mock_component, {})

        assert result is None
        # Should NOT log warnings for unknown abilities (that's expected)
        ability_warnings = [r for r in caplog.records
                          if 'NonexistentAbility' in r.message]
        assert len(ability_warnings) == 0, "Unknown ability should not log warning"
