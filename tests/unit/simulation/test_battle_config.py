"""
Unit tests for battle_config.py.

Tests BattleMode enum and BattleConfig dataclass.
"""
import pytest

from game.simulation.battle_config import BattleMode, BattleConfig
from game.simulation.systems.battle_end_conditions import BattleEndMode
from game.core.constants import SimulationConstants


class TestBattleModeEnum:
    """Tests for BattleMode enum."""

    def test_battle_mode_manual(self):
        """BattleMode.MANUAL.value == 'manual'."""
        assert BattleMode.MANUAL.value == "manual"

    def test_battle_mode_test(self):
        """BattleMode.TEST.value == 'test'."""
        assert BattleMode.TEST.value == "test"

    def test_battle_mode_strategy(self):
        """BattleMode.STRATEGY.value == 'strategy'."""
        assert BattleMode.STRATEGY.value == "strategy"

    def test_battle_mode_hypothetical(self):
        """BattleMode.HYPOTHETICAL.value == 'hypothetical'."""
        assert BattleMode.HYPOTHETICAL.value == "hypothetical"

    def test_battle_mode_all_unique(self):
        """All BattleMode values are distinct."""
        values = [mode.value for mode in BattleMode]
        assert len(values) == len(set(values))


class TestBattleConfigDefaults:
    """Tests for BattleConfig default values."""

    def test_default_mode_is_manual(self):
        """Default mode is MANUAL."""
        config = BattleConfig()
        assert config.mode == BattleMode.MANUAL

    def test_default_max_ticks(self):
        """Default max_ticks matches SimulationConstants."""
        config = BattleConfig()
        assert config.max_ticks == SimulationConstants.DEFAULT_MAX_TICKS

    def test_default_headless_false(self):
        """headless defaults to False."""
        config = BattleConfig()
        assert config.headless is False

    def test_default_logging_enabled(self):
        """enable_logging defaults to True."""
        config = BattleConfig()
        assert config.enable_logging is True

    def test_default_no_retreat(self):
        """allow_retreat defaults to False."""
        config = BattleConfig()
        assert config.allow_retreat is False

    def test_default_allow_reinforcements_false(self):
        """allow_reinforcements defaults to False."""
        config = BattleConfig()
        assert config.allow_reinforcements is False

    def test_default_end_mode(self):
        """end_mode defaults to HP_BASED."""
        config = BattleConfig()
        assert config.end_mode == BattleEndMode.HP_BASED

    def test_default_seed_none(self):
        """seed defaults to None."""
        config = BattleConfig()
        assert config.seed is None

    def test_default_start_paused_false(self):
        """start_paused defaults to False."""
        config = BattleConfig()
        assert config.start_paused is False

    def test_default_test_scenario_none(self):
        """test_scenario defaults to None."""
        config = BattleConfig()
        assert config.test_scenario is None

    def test_default_source_fleets_none(self):
        """source_fleets defaults to None."""
        config = BattleConfig()
        assert config.source_fleets is None


class TestBattleConfigHypotheticalMode:
    """Tests for hypothetical mode settings."""

    def test_hypothetical_mode_isolated(self):
        """isolated defaults to True."""
        config = BattleConfig()
        assert config.isolated is True


class TestBattleConfigCustomValues:
    """Tests for customizing BattleConfig values."""

    def test_custom_seed(self):
        """Seed can be set to specific int."""
        config = BattleConfig(seed=42)
        assert config.seed == 42

    def test_custom_max_ticks(self):
        """max_ticks can be overridden."""
        config = BattleConfig(max_ticks=5000)
        assert config.max_ticks == 5000

    def test_custom_mode(self):
        """mode can be set to any BattleMode."""
        config = BattleConfig(mode=BattleMode.STRATEGY)
        assert config.mode == BattleMode.STRATEGY

    def test_custom_headless(self):
        """headless can be set to True."""
        config = BattleConfig(headless=True)
        assert config.headless is True


class TestBattleConfigMapBounds:
    """Tests for map_bounds configuration."""

    def test_map_bounds_default(self):
        """Default map_bounds tuple has 4 elements."""
        config = BattleConfig()
        assert len(config.map_bounds) == 4
        assert config.map_bounds[0] == 0
        assert config.map_bounds[1] == 0
        assert config.map_bounds[2] == SimulationConstants.DEFAULT_MAP_SIZE
        assert config.map_bounds[3] == SimulationConstants.DEFAULT_MAP_SIZE

    def test_map_bounds_custom(self):
        """map_bounds can be customized."""
        custom_bounds = (100, 200, 5000, 6000)
        config = BattleConfig(map_bounds=custom_bounds)
        assert config.map_bounds == custom_bounds
