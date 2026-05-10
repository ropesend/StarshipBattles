# Phase 2: Thread Ship Instance ID Through Battle

**Objective:** Match battle survivors by `instance_id` instead of `name`, eliminating silent data loss when fleets contain duplicate ship names.

**Key Principle:** Ship identity is `instance_id` (unique per game). Ship `name` is presentation only — never use it for matching or lookup.

---

## Background

`FleetBattleAdapter.update_from_battle_results()` builds `survivors_by_name = {s.name: s for s in surviving_ships}`. If two ships share a name (e.g., "Fighter-01"), the last one overwrites the first in the dict — silent data loss. `ShipInstance` already has `.instance_id: str` (uuid4), but it's not threaded through the battle layer.

## Design

1. Add `instance_id: str` property to `IPostBattleShip` protocol
2. When creating simulation `Ship` from `ShipInstance` for battle, copy `instance_id` onto the Ship
3. After battle, `BattleResult` surfaces `instance_id` on surviving ships
4. `FleetBattleAdapter` matches by `instance_id` instead of `name`

---

## Checklist

### Discovery
- [ ] Read `fleet_battle_adapter.py` fully — understand the battle setup and result reconciliation flow
- [ ] Find `IPostBattleShip` protocol definition — see what properties it currently exposes
- [ ] Read `ShipInstance` — confirm `instance_id` field exists and is populated
- [ ] Trace battle setup: where does `ShipInstance` → simulation `Ship` conversion happen?
- [ ] Trace battle results: where does simulation `Ship` → `IPostBattleShip` conversion happen?

### Tests First (TDD)
- [ ] Write test: fleet with two identically-named ships → battle → both survivors correctly updated (not just one)
- [ ] Write test: `IPostBattleShip` exposes `instance_id` property
- [ ] Write test: simulation `Ship` created from `ShipInstance` carries `instance_id`
- [ ] Write test: `update_from_battle_results()` matches by `instance_id`, not `name`
- [ ] Write test: fleet with unique names still works correctly (backward compat)
- [ ] Run tests — confirm duplicate-name test fails (current code matches by name)

### Implementation
- [ ] Add `instance_id: str` property to `IPostBattleShip` protocol
- [ ] Add `instance_id: Optional[str]` field to simulation `Ship` (or use existing metadata mechanism)
- [ ] Update battle setup code to copy `ShipInstance.instance_id` onto simulation `Ship`
- [ ] Update battle result / `IPostBattleShip` implementation to expose `instance_id`
- [ ] Update `fleet_battle_adapter.py` to build `survivors_by_id` instead of `survivors_by_name`
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python Tools/test_sharded/test_sharded.py`) — no regressions
- [ ] Run simulation tests — all pass
- [ ] Grep for `survivors_by_name` — should be removed or replaced
- [ ] Grep for `.name` used as lookup key in battle reconciliation — should be zero
