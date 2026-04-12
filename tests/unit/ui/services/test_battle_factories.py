"""Battle factory tests — DELETED in PROJ-269 Phase 6.

`create_started_battle_controller`, `create_manual_battle`,
`create_test_battle`, `create_strategy_battle`, and
`create_hypothetical_battle` were deleted. Callers now construct
`BattleController` directly with a plain `BattleConfig` (or, for the
strategy and combat lab paths, route through `run_battle(spec)`
entirely).

This empty module is retained so older test-discovery references
resolve to a valid path.
"""
