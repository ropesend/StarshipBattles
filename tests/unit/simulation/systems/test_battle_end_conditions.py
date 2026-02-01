"""
Tests for BattleEndCondition and BattleEndMode.

TDD tests for extended battle end condition system including:
- ABSOLUTE_MAX_TICKS safety ceiling
- ESCAPE_BASED mode for distance-based battle termination
- Extended BattleEndCondition parameters
"""
import pytest
from unittest.mock import Mock, MagicMock
import pygame

from game.simulation.systems.battle_end_conditions import (
    BattleEndMode,
    BattleEndCondition,
)
from game.core.constants import SimulationConstants


class TestBattleEndMode:
    """Tests for BattleEndMode enum."""

    def test_existing_modes_unchanged(self):
        """Existing modes should still work."""
        assert BattleEndMode.TIME_BASED.value == "time_based"
        assert BattleEndMode.HP_BASED.value == "hp_based"
        assert BattleEndMode.CAPABILITY_BASED.value == "capability"
        assert BattleEndMode.MANUAL.value == "manual"

    def test_escape_based_mode_exists(self):
        """ESCAPE_BASED mode should exist for distance-based termination."""
        assert hasattr(BattleEndMode, 'ESCAPE_BASED')
        assert BattleEndMode.ESCAPE_BASED.value == "escape"


class TestBattleEndConditionBasics:
    """Tests for BattleEndCondition basic functionality."""

    def test_default_values(self):
        """Default BattleEndCondition should have expected values."""
        condition = BattleEndCondition()

        assert condition.mode == BattleEndMode.HP_BASED
        assert condition.max_ticks is None
        assert condition.check_derelict is False

    def test_time_based_with_max_ticks(self):
        """TIME_BASED mode should accept max_ticks."""
        condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=500
        )

        assert condition.mode == BattleEndMode.TIME_BASED
        assert condition.max_ticks == 500

    def test_hp_based_with_derelict_check(self):
        """HP_BASED mode should accept check_derelict flag."""
        condition = BattleEndCondition(
            mode=BattleEndMode.HP_BASED,
            check_derelict=True
        )

        assert condition.mode == BattleEndMode.HP_BASED
        assert condition.check_derelict is True


class TestBattleEndConditionAbsoluteMaxTicks:
    """Tests for absolute_max_ticks safety ceiling."""

    def test_absolute_max_ticks_default(self):
        """absolute_max_ticks should default to SimulationConstants value."""
        condition = BattleEndCondition()

        assert hasattr(condition, 'absolute_max_ticks')
        assert condition.absolute_max_ticks == SimulationConstants.ABSOLUTE_MAX_TICKS

    def test_absolute_max_ticks_custom(self):
        """absolute_max_ticks should be configurable."""
        condition = BattleEndCondition(absolute_max_ticks=500_000)

        assert condition.absolute_max_ticks == 500_000

    def test_absolute_max_ticks_applies_to_all_modes(self):
        """absolute_max_ticks should be present regardless of mode."""
        for mode in BattleEndMode:
            condition = BattleEndCondition(mode=mode)
            assert hasattr(condition, 'absolute_max_ticks')
            assert condition.absolute_max_ticks == SimulationConstants.ABSOLUTE_MAX_TICKS


class TestBattleEndConditionEscapeMode:
    """Tests for ESCAPE_BASED mode configuration."""

    def test_escape_radius_parameter(self):
        """BattleEndCondition should accept escape_radius for ESCAPE_BASED mode."""
        condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        assert condition.mode == BattleEndMode.ESCAPE_BASED
        assert condition.escape_radius == 5000.0

    def test_escape_radius_default_none(self):
        """escape_radius should default to None."""
        condition = BattleEndCondition()

        assert hasattr(condition, 'escape_radius')
        assert condition.escape_radius is None

    def test_escape_team_parameter(self):
        """ESCAPE_BASED should support specifying which team must escape."""
        # escape_team: None = any team, 0 = team 0, 1 = team 1
        condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0,
            escape_team=1
        )

        assert condition.escape_team == 1

    def test_escape_team_default_none(self):
        """escape_team should default to None (any team escaping ends battle)."""
        condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        assert condition.escape_team is None

    def test_escape_all_ships_parameter(self):
        """ESCAPE_BASED should support requiring all ships to escape."""
        condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0,
            escape_all_ships=True
        )

        assert condition.escape_all_ships is True

    def test_escape_all_ships_default_false(self):
        """escape_all_ships should default to False (any ship escaping counts)."""
        condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )

        assert condition.escape_all_ships is False


class TestBattleEndConditionRepr:
    """Tests for BattleEndCondition string representation."""

    def test_repr_time_based(self):
        """TIME_BASED repr should show max_ticks."""
        condition = BattleEndCondition(
            mode=BattleEndMode.TIME_BASED,
            max_ticks=500
        )
        repr_str = repr(condition)

        assert "TIME_BASED" in repr_str
        assert "500" in repr_str

    def test_repr_escape_based(self):
        """ESCAPE_BASED repr should show escape_radius."""
        condition = BattleEndCondition(
            mode=BattleEndMode.ESCAPE_BASED,
            escape_radius=5000.0
        )
        repr_str = repr(condition)

        assert "ESCAPE" in repr_str
        assert "5000" in repr_str

    def test_repr_with_absolute_max(self):
        """repr should include absolute_max_ticks when custom value set."""
        condition = BattleEndCondition(
            mode=BattleEndMode.MANUAL,
            absolute_max_ticks=100_000
        )
        repr_str = repr(condition)

        assert "MANUAL" in repr_str
        # Custom absolute_max should be shown
        assert "100000" in repr_str or "100_000" in repr_str
