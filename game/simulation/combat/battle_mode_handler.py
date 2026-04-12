"""BattleModeHandler hierarchy — DELETED in PROJ-269 Phase 6.

This module previously housed:
  - `BattleModeHandler` ABC
  - `ManualBattleModeHandler` / `TestBattleModeHandler` /
    `StrategyBattleModeHandler` / `HypotheticalBattleModeHandler`
  - `get_handler_for_mode(mode)` factory

The Strategy pattern was replaced by explicit fields on `BattleSpec`
(boundary, end_condition, modifier_stack, telemetry_level,
post_battle_hook). `BattleController` no longer dispatches on mode;
visual-mode behavior is config-flag-driven, headless callers route
through `run_battle(spec)` directly.

The module is retained as an empty stub so older imports/grep targets
still resolve to a valid module path. Once the next sweep removes the
last lingering doc references, it can be deleted entirely.
"""

__all__: list = []
