"""Battle factory functions — DELETED in PROJ-269 Phase 6.

This module previously housed `create_started_battle_controller`,
`create_manual_battle`, `create_test_battle`, `create_strategy_battle`,
and `create_hypothetical_battle`. All four mode-specific factories
have been deleted; their callers now construct `BattleController`
directly with a plain `BattleConfig` (or, for the strategy and combat
lab paths, route through `run_battle(spec)` entirely).

The module is retained as an empty stub so older imports still resolve
to a valid module path. Once the deprecation period is over (next
sweep), it can be deleted entirely.
"""

__all__: list = []
