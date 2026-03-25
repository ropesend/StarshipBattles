# PROJ-226 Phase 1: Bug Fix & Critical Dedup

## DUP-SE-001: Superweapon Mission Move Bug
- [x] Identify the incorrect movement logic in `game/strategy/engine/superweapon_command_handlers.py`
- [x] Write failing test that demonstrates the bug
- [x] Fix the mission move logic
- [x] Verify test passes

Note: `_setup_mission_move` was a buggy duplicate of `add_move_order_if_needed` — it only checked the last order (not reverse-iterating to skip non-MOVE orders like BUG-70 fix). Deleted `_setup_mission_move` entirely and replaced all 6 mission handler call sites with `add_move_order_if_needed`. Existing tests already covered the correct behavior; the fix was the replacement itself.

## DUP-SE-002: Combat Event Logging
- [x] Identify duplicated combat event logging across engine modules
- [x] Consolidate into a single logging path
- [x] Update all call sites
- [x] Verify no logging regressions

Extracted `_log_combat_result()` helper in `conflict_resolution_engine.py`. Both `_resolve_combat` (RNG path) and `_resolve_combat_simulated` now call the helper.

## DUP-SE-008: Private API Access (`session.turn_engine._registries`)
- [x] Ensure `turn_engine` exposes a public `registries` property
- [x] Replace `session.turn_engine._registries.components` in `superweapon_command_handlers.py` (10 sites)
- [x] Replace `session.turn_engine._registries.components` in `command_handlers.py` (1 site)
- [x] Update test files that mock or reference `_registries` directly
- [x] Verify all tests pass

Used existing `session.registries` public property (on GameSession). Updated 3 test fixture files to mock `session.registries` instead of `session.turn_engine._registries`.

## DUP-SE-009: Backward Compat Alias (`process_end_turn_orders`)
- [x] Remove `process_end_turn_orders` alias from `game/strategy/engine/fleet_order_processor.py`
- [x] Remove from `game/strategy/interfaces/engines.py` if present
- [x] Update all call sites to use the canonical method name
- [x] Verify all tests pass

Removed alias from fleet_order_processor.py and mock_engines.py. Updated 10 test call sites across 3 test files. Interface file only had a comment reference (kept for historical context).

## Completion
- [x] Run full test suite: `pytest tests/ -n 12`
- [x] All Phase 1 items verified
