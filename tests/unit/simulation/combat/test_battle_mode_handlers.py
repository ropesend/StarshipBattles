"""BattleModeHandler tests — DELETED in PROJ-269 Phase 6.

`BattleModeHandler` ABC + 4 concrete handlers + `get_handler_for_mode`
factory are gone. Their behavior was replaced by explicit fields on
`BattleSpec` (boundary, end_condition, modifier_stack, telemetry_level,
post_battle_hook) consumed directly by `run_battle`.

This empty module is retained so older test-discovery / git history
references resolve to a valid path. The post-PROJ-269 sweep will remove
it entirely.
"""
