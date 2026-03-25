# PROJ-226 Phase 1: Bug Fix & Critical Dedup

## DUP-SE-001: Superweapon Mission Move Bug
- [ ] Identify the incorrect movement logic in `game/strategy/engine/superweapon_command_handlers.py`
- [ ] Write failing test that demonstrates the bug
- [ ] Fix the mission move logic
- [ ] Verify test passes

## DUP-SE-002: Combat Event Logging
- [ ] Identify duplicated combat event logging across engine modules
- [ ] Consolidate into a single logging path
- [ ] Update all call sites
- [ ] Verify no logging regressions

## DUP-SE-008: Private API Access (`session.turn_engine._registries`)
- [ ] Ensure `turn_engine` exposes a public `registries` property
- [ ] Replace `session.turn_engine._registries.components` in `superweapon_command_handlers.py` (11 sites)
- [ ] Replace `session.turn_engine._registries.components` in `command_handlers.py` (1 site)
- [ ] Update test files that mock or reference `_registries` directly
- [ ] Verify all tests pass

## DUP-SE-009: Backward Compat Alias (`process_end_turn_orders`)
- [ ] Remove `process_end_turn_orders` alias from `game/strategy/engine/fleet_order_processor.py`
- [ ] Remove from `game/strategy/interfaces/engines.py` if present
- [ ] Update all call sites to use the canonical method name
- [ ] Verify all tests pass

## Completion
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] All Phase 1 items verified
