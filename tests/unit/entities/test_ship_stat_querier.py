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
