"""FEAT-27: GameConfig validation tests.

Validates the dataclass `__post_init__` rules introduced for the
"galaxy size as low as 1" feature:

- 1 ≤ system_count ≤ 150 (range bounds)
- N=1 is the special shared-system mode and bypasses the
  empire-vs-system count check
- N≥2 with len(players) > system_count is rejected
- The dataclass field default for `system_count` is 2 (single source
  of truth — UI imports from here)
"""
import pytest

from game.core.exceptions import ValidationException
from game.strategy.engine.game_config import (
    DEFAULT_SYSTEM_COUNT,
    GameConfig,
    PlayerConfig,
)


class TestGameConfigDefaultSystemCount:
    """The dataclass is the single source of truth for the default."""

    def test_default_system_count_is_2(self):
        config = GameConfig()
        assert config.system_count == 2

    def test_default_system_count_constant_is_2(self):
        assert DEFAULT_SYSTEM_COUNT == 2


class TestGameConfigSystemCountBounds:
    """1 ≤ system_count ≤ 150."""

    def test_system_count_1_accepted(self):
        # N=1 + default 2 players is the shared-system mode and should be allowed.
        config = GameConfig(system_count=1)
        assert config.system_count == 1

    def test_system_count_2_accepted(self):
        config = GameConfig(system_count=2)
        assert config.system_count == 2

    def test_system_count_150_accepted(self):
        config = GameConfig(system_count=150)
        assert config.system_count == 150

    def test_system_count_zero_rejected(self):
        with pytest.raises(ValidationException):
            GameConfig(system_count=0)

    def test_system_count_negative_rejected(self):
        with pytest.raises(ValidationException):
            GameConfig(system_count=-1)

    def test_system_count_151_rejected(self):
        with pytest.raises(ValidationException):
            GameConfig(system_count=151)

    def test_system_count_huge_rejected(self):
        with pytest.raises(ValidationException):
            GameConfig(system_count=10000)


class TestGameConfigEmpiresVsSystems:
    """N≥2 requires len(players) ≤ system_count. N=1 bypasses."""

    def _players(self, n: int):
        return [PlayerConfig(name=f"E{i}") for i in range(n)]

    def test_N2_E2_accepted(self):
        config = GameConfig(system_count=2, players=self._players(2))
        assert len(config.players) == 2 and config.system_count == 2

    def test_N2_E3_rejected(self):
        with pytest.raises(ValidationException):
            GameConfig(system_count=2, players=self._players(3))

    def test_N2_E4_rejected(self):
        with pytest.raises(ValidationException):
            GameConfig(system_count=2, players=self._players(4))

    def test_N5_E4_accepted(self):
        config = GameConfig(system_count=5, players=self._players(4))
        assert config.system_count == 5

    def test_N1_E1_accepted(self):
        config = GameConfig(system_count=1, players=self._players(1))
        assert config.system_count == 1 and len(config.players) == 1

    def test_N1_E2_accepted_shared_system_mode(self):
        # N=1 explicitly allows multiple empires (shared-system mode).
        config = GameConfig(system_count=1, players=self._players(2))
        assert config.system_count == 1 and len(config.players) == 2

    def test_N1_E4_accepted_shared_system_mode(self):
        config = GameConfig(system_count=1, players=self._players(4))
        assert config.system_count == 1 and len(config.players) == 4
