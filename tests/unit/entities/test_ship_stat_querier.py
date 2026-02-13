"""Tests for ShipStatQuerier - ship stat aggregation logic extracted from Ship."""

import pytest
from unittest.mock import Mock, MagicMock, PropertyMock

from game.simulation.entities.ship_stat_querier import ShipStatQuerier


class TestShipStatQuerierGetAbilityTotal:
    """Tests for get_ability_total method."""

    def test_get_ability_total_returns_calculated_value(self):
        """get_ability_total delegates to stats_calculator.calculate_ability_totals."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'TestAbility': 42.0
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_ability_total('TestAbility')

        assert result == 42.0

    def test_get_ability_total_returns_zero_when_not_found(self):
        """get_ability_total returns 0 when ability not present."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {}
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_ability_total('MissingAbility')

        assert result == 0

    def test_get_ability_total_creates_stats_calculator_if_missing(self):
        """get_ability_total creates ShipStatsCalculator if ship doesn't have one."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = None  # No calculator yet
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        # This should not raise - it should create a calculator internally
        result = querier.get_ability_total('SomeAbility')

        assert result == 0  # Empty components = 0 total


class TestShipStatQuerierGetTotalAbilityValue:
    """Tests for get_total_ability_value method."""

    def test_get_total_ability_value_sums_primary_values(self):
        """get_total_ability_value sums get_primary_value() across matching abilities."""
        mock_ability1 = Mock()
        mock_ability1.get_primary_value.return_value = 10.0

        mock_ability2 = Mock()
        mock_ability2.get_primary_value.return_value = 15.0

        mock_comp = Mock()
        mock_comp.is_operational = True
        mock_comp.get_abilities.return_value = [mock_ability1, mock_ability2]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility')

        assert result == 25.0

    def test_get_total_ability_value_operational_only_true_skips_non_operational(self):
        """get_total_ability_value with operational_only=True skips non-operational components."""
        mock_ability = Mock()
        mock_ability.get_primary_value.return_value = 10.0

        mock_comp = Mock()
        mock_comp.is_operational = False  # Non-operational
        mock_comp.get_abilities.return_value = [mock_ability]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility', operational_only=True)

        assert result == 0.0  # Skipped because non-operational

    def test_get_total_ability_value_operational_only_false_includes_all(self):
        """get_total_ability_value with operational_only=False includes non-operational components."""
        mock_ability = Mock()
        mock_ability.get_primary_value.return_value = 10.0

        mock_comp = Mock()
        mock_comp.is_operational = False  # Non-operational
        mock_comp.get_abilities.return_value = [mock_ability]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility', operational_only=False)

        assert result == 10.0  # Included despite non-operational


class TestShipStatQuerierSensorAndECMScores:
    """Tests for get_total_sensor_score and get_total_ecm_score."""

    def test_get_total_sensor_score_returns_float(self):
        """get_total_sensor_score returns float value."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitAttackModifier': 1.5
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        assert isinstance(result, float)
        assert result == 1.5

    def test_get_total_sensor_score_returns_zero_when_missing(self):
        """get_total_sensor_score returns 0.0 when no sensors present."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {}
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        assert result == 0.0

    def test_get_total_ecm_score_returns_float(self):
        """get_total_ecm_score returns float value."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitDefenseModifier': 0.8
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ecm_score()

        assert isinstance(result, float)
        assert result == 0.8

    def test_get_total_ecm_score_returns_zero_when_missing(self):
        """get_total_ecm_score returns 0.0 when no ECM present."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {}
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ecm_score()

        assert result == 0.0


class TestShipStatQuerierMaxWeaponRange:
    """Tests for max_weapon_range property."""

    def test_max_weapon_range_returns_max_range_from_weapons(self):
        """max_weapon_range returns the highest range value."""
        # Create mock abilities that look like WeaponAbility
        from game.simulation.components.abilities import WeaponAbility

        mock_ability1 = Mock(spec=WeaponAbility)
        mock_ability1.range = 100.0

        mock_ability2 = Mock(spec=WeaponAbility)
        mock_ability2.range = 200.0

        mock_comp1 = Mock()
        mock_comp1.ability_instances = [mock_ability1]

        mock_comp2 = Mock()
        mock_comp2.ability_instances = [mock_ability2]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp1, mock_comp2]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 200.0

    def test_max_weapon_range_returns_zero_with_no_weapons(self):
        """max_weapon_range returns 0.0 for ship with no weapons."""
        mock_comp = Mock()
        mock_comp.ability_instances = []

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 0.0

    def test_max_weapon_range_handles_seeker_weapons(self):
        """max_weapon_range calculates range from endurance for SeekerWeaponAbility."""
        from game.simulation.components.abilities import SeekerWeaponAbility

        mock_seeker = Mock(spec=SeekerWeaponAbility)
        mock_seeker.range = 0  # Not set, should use endurance calc
        mock_seeker.projectile_speed = 10.0
        mock_seeker.endurance = 20.0  # range = 10 * 20 = 200

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_seeker]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 200.0


class TestShipStatQuerierCachedSummary:
    """Tests for cached_summary property."""

    def test_cached_summary_returns_ship_cached_summary(self):
        """cached_summary returns the ship's _cached_summary dict."""
        mock_ship = Mock()
        mock_ship._cached_summary = {'dps': 100, 'speed': 50}

        querier = ShipStatQuerier(mock_ship)
        result = querier.cached_summary

        assert result == {'dps': 100, 'speed': 50}

    def test_cached_summary_returns_empty_dict_when_empty(self):
        """cached_summary returns empty dict when ship has no cached data."""
        mock_ship = Mock()
        mock_ship._cached_summary = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.cached_summary

        assert result == {}


# ============================================================================
# Additional Edge Case Tests (PROJ-118 Phase 2)
# ============================================================================

class TestShipStatQuerierInitialization:
    """Tests for ShipStatQuerier initialization."""

    def test_init_stores_ship_reference(self):
        """ShipStatQuerier stores reference to the ship."""
        mock_ship = Mock()
        querier = ShipStatQuerier(mock_ship)

        assert querier._ship is mock_ship

    def test_init_with_different_ships(self):
        """Each querier instance references its own ship."""
        ship1 = Mock()
        ship2 = Mock()

        querier1 = ShipStatQuerier(ship1)
        querier2 = ShipStatQuerier(ship2)

        assert querier1._ship is ship1
        assert querier2._ship is ship2
        assert querier1._ship is not querier2._ship


class TestGetAbilityTotalEdgeCases:
    """Edge case tests for get_ability_total method."""

    def test_get_ability_total_with_integer_value(self):
        """get_ability_total handles integer return values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'IntAbility': 5
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_ability_total('IntAbility')

        assert result == 5
        assert isinstance(result, int)

    def test_get_ability_total_with_boolean_value(self):
        """get_ability_total handles boolean return values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'BoolAbility': True
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_ability_total('BoolAbility')

        assert result is True

    def test_get_ability_total_passes_components_to_calculator(self):
        """get_ability_total passes all components to the stats calculator."""
        mock_comp1 = Mock()
        mock_comp2 = Mock()
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp1, mock_comp2]
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {}
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        querier.get_ability_total('TestAbility')

        mock_ship.stats_calculator.calculate_ability_totals.assert_called_once_with(
            [mock_comp1, mock_comp2]
        )


class TestGetTotalAbilityValueEdgeCases:
    """Edge case tests for get_total_ability_value method."""

    def test_get_total_ability_value_multiple_components(self):
        """get_total_ability_value sums across multiple components."""
        mock_ability1 = Mock()
        mock_ability1.get_primary_value.return_value = 5.0

        mock_ability2 = Mock()
        mock_ability2.get_primary_value.return_value = 10.0

        mock_comp1 = Mock()
        mock_comp1.is_operational = True
        mock_comp1.get_abilities.return_value = [mock_ability1]

        mock_comp2 = Mock()
        mock_comp2.is_operational = True
        mock_comp2.get_abilities.return_value = [mock_ability2]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp1, mock_comp2]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility')

        assert result == 15.0

    def test_get_total_ability_value_empty_components_list(self):
        """get_total_ability_value returns 0.0 for empty component list."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility')

        assert result == 0.0

    def test_get_total_ability_value_no_matching_abilities(self):
        """get_total_ability_value returns 0.0 when no abilities match."""
        mock_comp = Mock()
        mock_comp.is_operational = True
        mock_comp.get_abilities.return_value = []  # No matching abilities

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('NonExistentAbility')

        assert result == 0.0

    def test_get_total_ability_value_mixed_operational_status(self):
        """get_total_ability_value correctly filters mixed operational components."""
        mock_ability1 = Mock()
        mock_ability1.get_primary_value.return_value = 10.0

        mock_ability2 = Mock()
        mock_ability2.get_primary_value.return_value = 20.0

        mock_ability3 = Mock()
        mock_ability3.get_primary_value.return_value = 30.0

        mock_comp1 = Mock()
        mock_comp1.is_operational = True
        mock_comp1.get_abilities.return_value = [mock_ability1]

        mock_comp2 = Mock()
        mock_comp2.is_operational = False  # Should be skipped
        mock_comp2.get_abilities.return_value = [mock_ability2]

        mock_comp3 = Mock()
        mock_comp3.is_operational = True
        mock_comp3.get_abilities.return_value = [mock_ability3]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp1, mock_comp2, mock_comp3]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility', operational_only=True)

        # 10 + 30 = 40 (skipping comp2 which has 20)
        assert result == 40.0

    def test_get_total_ability_value_queries_correct_ability_name(self):
        """get_total_ability_value passes correct ability name to get_abilities."""
        mock_comp = Mock()
        mock_comp.is_operational = True
        mock_comp.get_abilities.return_value = []

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        querier.get_total_ability_value('CombatPropulsion')

        mock_comp.get_abilities.assert_called_once_with('CombatPropulsion')


class TestSensorAndECMScoreEdgeCases:
    """Edge case tests for sensor and ECM score methods."""

    def test_get_total_sensor_score_handles_boolean_true_as_numeric(self):
        """get_total_sensor_score converts boolean True to 1.0 (bool is subclass of int)."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitAttackModifier': True  # Boolean - Python bool is subclass of int
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        # In Python, bool is a subclass of int, so True converts to 1.0
        assert result == 1.0
        assert isinstance(result, float)

    def test_get_total_ecm_score_handles_boolean_false_as_numeric(self):
        """get_total_ecm_score converts boolean False to 0.0 (bool is subclass of int)."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitDefenseModifier': False  # Boolean - Python bool is subclass of int
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ecm_score()

        # In Python, bool is a subclass of int, so False converts to 0.0
        assert result == 0.0
        assert isinstance(result, float)

    def test_get_total_sensor_score_converts_int_to_float(self):
        """get_total_sensor_score converts integer result to float."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitAttackModifier': 3  # Integer
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        assert result == 3.0
        assert isinstance(result, float)

    def test_get_total_ecm_score_converts_int_to_float(self):
        """get_total_ecm_score converts integer result to float."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitDefenseModifier': 2  # Integer
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ecm_score()

        assert result == 2.0
        assert isinstance(result, float)


class TestMaxWeaponRangeEdgeCases:
    """Edge case tests for max_weapon_range property."""

    def test_max_weapon_range_seeker_with_explicit_range_uses_range(self):
        """max_weapon_range uses explicit range for SeekerWeaponAbility when set."""
        from game.simulation.components.abilities import SeekerWeaponAbility

        mock_seeker = Mock(spec=SeekerWeaponAbility)
        mock_seeker.range = 150.0  # Explicit range set
        mock_seeker.projectile_speed = 10.0
        mock_seeker.endurance = 20.0  # Would calculate to 200, but 150 is set

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_seeker]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 150.0  # Should use explicit range, not calculated

    def test_max_weapon_range_with_mixed_weapon_types(self):
        """max_weapon_range finds max across different weapon types."""
        from game.simulation.components.abilities import WeaponAbility, SeekerWeaponAbility

        mock_weapon = Mock(spec=WeaponAbility)
        mock_weapon.range = 100.0

        mock_seeker = Mock(spec=SeekerWeaponAbility)
        mock_seeker.range = 0  # Calculate from endurance
        mock_seeker.projectile_speed = 15.0
        mock_seeker.endurance = 10.0  # 150 range

        mock_comp1 = Mock()
        mock_comp1.ability_instances = [mock_weapon]

        mock_comp2 = Mock()
        mock_comp2.ability_instances = [mock_seeker]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp1, mock_comp2]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 150.0  # Seeker's calculated range is higher

    def test_max_weapon_range_ignores_non_weapon_abilities(self):
        """max_weapon_range ignores abilities that are not WeaponAbility."""
        mock_non_weapon = Mock()  # No WeaponAbility spec
        mock_non_weapon.range = 999.0  # Should be ignored

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_non_weapon]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 0.0  # Non-weapon should be ignored

    def test_max_weapon_range_handles_zero_range_regular_weapon(self):
        """max_weapon_range handles weapon with range 0."""
        from game.simulation.components.abilities import WeaponAbility

        mock_weapon = Mock(spec=WeaponAbility)
        mock_weapon.range = 0.0

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_weapon]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 0.0

    def test_max_weapon_range_multiple_components_empty_abilities(self):
        """max_weapon_range handles multiple components with empty ability lists."""
        mock_comp1 = Mock()
        mock_comp1.ability_instances = []

        mock_comp2 = Mock()
        mock_comp2.ability_instances = []

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp1, mock_comp2]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 0.0

    def test_max_weapon_range_seeker_missing_projectile_speed(self):
        """max_weapon_range handles SeekerWeaponAbility missing projectile_speed."""
        from game.simulation.components.abilities import SeekerWeaponAbility

        mock_seeker = Mock(spec=SeekerWeaponAbility)
        mock_seeker.range = 0
        # Missing projectile_speed attribute - hasattr will return False for spec'd mock
        del mock_seeker.projectile_speed
        mock_seeker.endurance = 20.0

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_seeker]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        # Should fallback to range (0) since calculation can't proceed
        assert result == 0.0

    def test_max_weapon_range_weapon_missing_range_attribute(self):
        """max_weapon_range handles weapon missing range attribute gracefully."""
        from game.simulation.components.abilities import WeaponAbility

        mock_weapon = Mock(spec=WeaponAbility)
        # Remove range attribute to test getattr default
        del mock_weapon.range

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_weapon]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        # getattr(ab, 'range', 0.0) should return 0.0
        assert result == 0.0

    def test_max_weapon_range_seeker_missing_endurance(self):
        """max_weapon_range handles SeekerWeaponAbility missing endurance attribute."""
        from game.simulation.components.abilities import SeekerWeaponAbility

        mock_seeker = Mock(spec=SeekerWeaponAbility)
        mock_seeker.range = 0  # Not set
        mock_seeker.projectile_speed = 10.0
        # Missing endurance attribute
        del mock_seeker.endurance

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_seeker]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        # Should fallback to range (0) since calculation can't proceed
        assert result == 0.0

    def test_max_weapon_range_seeker_negative_range(self):
        """max_weapon_range uses endurance calculation when range is negative."""
        from game.simulation.components.abilities import SeekerWeaponAbility

        mock_seeker = Mock(spec=SeekerWeaponAbility)
        mock_seeker.range = -1  # Negative, should trigger calculation
        mock_seeker.projectile_speed = 10.0
        mock_seeker.endurance = 15.0  # range = 10 * 15 = 150

        mock_comp = Mock()
        mock_comp.ability_instances = [mock_seeker]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.max_weapon_range

        assert result == 150.0


class TestSensorECMNonNumericEdgeCases:
    """Edge cases for non-numeric values in sensor/ECM methods."""

    def test_get_total_sensor_score_handles_string_returns_zero(self):
        """get_total_sensor_score returns 0.0 for non-numeric string values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitAttackModifier': "not_a_number"  # String value
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        # isinstance check should fail for string, returning 0.0
        assert result == 0.0
        assert isinstance(result, float)

    def test_get_total_ecm_score_handles_string_returns_zero(self):
        """get_total_ecm_score returns 0.0 for non-numeric string values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitDefenseModifier': "invalid"  # String value
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ecm_score()

        # isinstance check should fail for string, returning 0.0
        assert result == 0.0
        assert isinstance(result, float)

    def test_get_total_sensor_score_handles_list_returns_zero(self):
        """get_total_sensor_score returns 0.0 for list values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitAttackModifier': [1.0, 2.0]  # List value
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        # isinstance check should fail for list, returning 0.0
        assert result == 0.0

    def test_get_total_ecm_score_handles_none_returns_zero(self):
        """get_total_ecm_score returns 0.0 for None values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitDefenseModifier': None  # None value
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ecm_score()

        # isinstance check should fail for None, returning 0.0
        assert result == 0.0

    def test_get_total_sensor_score_handles_negative_float(self):
        """get_total_sensor_score handles negative float values."""
        mock_ship = Mock()
        mock_ship.get_all_components.return_value = []
        mock_ship.stats_calculator = Mock()
        mock_ship.stats_calculator.calculate_ability_totals.return_value = {
            'ToHitAttackModifier': -0.5  # Negative float
        }
        mock_ship._registries = Mock()
        mock_ship._registries.vehicle_classes = {}

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_sensor_score()

        # Should still convert and return the negative value
        assert result == -0.5
        assert isinstance(result, float)


class TestGetTotalAbilityValueFloatAccumulation:
    """Tests for floating point accumulation in get_total_ability_value."""

    def test_get_total_ability_value_handles_float_values(self):
        """get_total_ability_value correctly sums floating point values."""
        mock_ability1 = Mock()
        mock_ability1.get_primary_value.return_value = 0.1

        mock_ability2 = Mock()
        mock_ability2.get_primary_value.return_value = 0.2

        mock_ability3 = Mock()
        mock_ability3.get_primary_value.return_value = 0.3

        mock_comp = Mock()
        mock_comp.is_operational = True
        mock_comp.get_abilities.return_value = [mock_ability1, mock_ability2, mock_ability3]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility')

        # 0.1 + 0.2 + 0.3 = 0.6 (with floating point tolerance)
        assert abs(result - 0.6) < 0.0001

    def test_get_total_ability_value_handles_negative_values(self):
        """get_total_ability_value correctly handles negative ability values."""
        mock_ability1 = Mock()
        mock_ability1.get_primary_value.return_value = 10.0

        mock_ability2 = Mock()
        mock_ability2.get_primary_value.return_value = -3.0  # Negative modifier

        mock_comp = Mock()
        mock_comp.is_operational = True
        mock_comp.get_abilities.return_value = [mock_ability1, mock_ability2]

        mock_ship = Mock()
        mock_ship.get_all_components.return_value = [mock_comp]

        querier = ShipStatQuerier(mock_ship)
        result = querier.get_total_ability_value('TestAbility')

        assert result == 7.0
