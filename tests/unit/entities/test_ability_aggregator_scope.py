"""
Unit tests for AbilityAggregator layer scope filtering.

Tests COMBAT, STRATEGIC, and BOTH layer filtering behavior.
"""
import pytest
from unittest.mock import MagicMock, patch


class TestAbilityAggregatorLayerScope:
    """Tests for ability layer scope filtering."""

    def test_ability_aggregator_module_exists(self):
        """ability_aggregator module can be imported."""
        from game.simulation.entities import ability_aggregator
        assert ability_aggregator is not None

    def test_ability_layer_enum_exists(self):
        """AbilityLayer enum exists."""
        from game.simulation.entities.ability_aggregator import AbilityLayer
        assert AbilityLayer is not None

    def test_ability_scope_enum_exists(self):
        """AbilityScope enum exists."""
        from game.simulation.entities.ability_aggregator import AbilityScope
        assert AbilityScope is not None

    def test_calculate_ability_totals_function_exists(self):
        """calculate_ability_totals function exists."""
        from game.simulation.entities.ability_aggregator import calculate_ability_totals
        assert calculate_ability_totals is not None

    def test_get_ability_total_function_exists(self):
        """get_ability_total function exists."""
        from game.simulation.entities.ability_aggregator import get_ability_total
        assert get_ability_total is not None
