"""BattleConfig tests — PROJ-270 Phase 7.5 re-fill.

The previous file was a docstring-only stub retained after PROJ-269
Phase 6 deleted `BattleMode` and the variance-bearing fields on the
dataclass. PROJ-270 Phase 7.5 re-fills it with tests that lock the
current trimmed surface:
  - seed / end_condition / absolute_max_ticks
  - headless / start_paused / enable_logging
  - allow_retreat / allow_reinforcements
  - return_destination / show_results

PROJ-270 deletions that this test file guards:
  - `test_scenario` field (Phase 5.1)
  - `map_bounds` field (Phase 5.4 — replaced by BattleSpec.boundary)
  - `team_modifiers`, `global_modifiers`, `environmental_effects`,
    `per_tick_callback`, `source_fleets`, `mode` (PROJ-269 Phase 6)
"""
from dataclasses import fields

from game.simulation.battle_config import BattleConfig
from game.core.return_destination import ReturnDestination


class TestBattleConfigDefaults:
    """Default field values match the post-PROJ-270 surface."""

    def test_defaults_constructable(self):
        """BattleConfig() constructs without arguments."""
        config = BattleConfig()
        assert config is not None

    def test_default_headless_is_false(self):
        assert BattleConfig().headless is False

    def test_default_start_paused_is_false(self):
        assert BattleConfig().start_paused is False

    def test_default_enable_logging_is_true(self):
        assert BattleConfig().enable_logging is True

    def test_default_allow_retreat_is_false(self):
        assert BattleConfig().allow_retreat is False

    def test_default_allow_reinforcements_is_false(self):
        assert BattleConfig().allow_reinforcements is False

    def test_default_show_results_is_true(self):
        assert BattleConfig().show_results is True

    def test_default_return_destination_is_battle_setup(self):
        assert BattleConfig().return_destination == ReturnDestination.BATTLE_SETUP

    def test_default_seed_is_none(self):
        assert BattleConfig().seed is None

    def test_default_end_condition_is_team_eliminated(self):
        """Default end_condition is a TeamEliminatedCondition instance."""
        from game.simulation.systems.battle_end_conditions import TeamEliminatedCondition
        config = BattleConfig()
        assert isinstance(config.end_condition, TeamEliminatedCondition)


class TestBattleConfigDeletedFields:
    """Fields deleted by PROJ-269 Phase 6 + PROJ-270 must not reappear.

    These are regression guards against re-adding legacy variance-bearing
    state that belongs on `BattleSpec` instead.
    """

    # PROJ-270 Phase 12.6: each entry carries a sunset date — once passed,
    # re-evaluate whether the regression-guard is still load-bearing or
    # has outlived its purpose. Guards with no sunset date accumulate
    # unboundedly as a ledger of past sins.
    #
    # Format: {field_name: "YYYY-MM-DD"} — date is ~6 months from the
    # project that added it. On/after sunset, audit + prune or renew.
    FORBIDDEN_FIELDS_WITH_SUNSET = {
        "mode":                  "2026-10-01",  # PROJ-269
        "team_modifiers":        "2026-10-01",  # PROJ-269
        "global_modifiers":      "2026-10-01",  # PROJ-269
        "environmental_effects": "2026-10-01",  # PROJ-269
        "per_tick_callback":     "2026-10-01",  # PROJ-269
        "source_fleets":         "2026-10-01",  # PROJ-269
        "test_scenario":         "2027-04-01",  # PROJ-270 Phase 5.1
        "map_bounds":            "2027-04-01",  # PROJ-270 Task 5.4
    }
    FORBIDDEN_FIELDS = frozenset(FORBIDDEN_FIELDS_WITH_SUNSET.keys())

    def test_no_forbidden_fields(self):
        """BattleConfig dataclass has no forbidden fields."""
        field_names = {f.name for f in fields(BattleConfig)}
        leaks = field_names & self.FORBIDDEN_FIELDS
        assert not leaks, (
            f"BattleConfig has regressed and re-added forbidden fields: "
            f"{leaks}. These fields belong on BattleSpec or run_battle's "
            f"kwargs, not on BattleConfig."
        )


class TestBattleConfigKwargs:
    """Explicit construction with kwargs."""

    def test_seed_kwarg(self):
        assert BattleConfig(seed=42).seed == 42

    def test_headless_kwarg(self):
        assert BattleConfig(headless=True).headless is True

    def test_allow_retreat_kwarg(self):
        assert BattleConfig(allow_retreat=True).allow_retreat is True

    def test_return_destination_kwarg(self):
        config = BattleConfig(return_destination=ReturnDestination.TEST_LAB)
        assert config.return_destination == ReturnDestination.TEST_LAB

    def test_absolute_max_ticks_kwarg(self):
        assert BattleConfig(absolute_max_ticks=500).absolute_max_ticks == 500
