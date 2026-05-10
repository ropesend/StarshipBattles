# Phase 3: Multi-Fleet-per-Empire Combat Support

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Today, when one empire has multiple fleets at the same hex, `_resolve_combat_at_hex` keeps only the FIRST fleet per empire (`conflict_resolution_engine.py:298-300`); the others sit silently idle. PROJ-320 Phase 3 makes every fleet at the contested hex participate. Allies are grouped by `owner_id` in the spec compiler — extra fleets per empire bulk up that team's ship count rather than creating extra teams (the engine has no alliances; same-team ships fight together).

---

## Tasks

### Task 3.1: Promote `fleets_by_empire` to `Dict[int, List[Fleet]]` [Medium]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/conflict_resolution/ tests/integration/strategy/test_three_empire_battle.py -v`

- [x] Located `_resolve_combat_at_hex` (line 269)
- [x] Replaced the silent first-fleet-only batching with `fleets_by_empire.setdefault(empire.id, []).append(fleet)`
- [x] Updated the iteration that flattens these into the resolver's `fleets` argument: deterministic `(empire_id, fleet_id)` order
- [x] Verified `empires={team_id: Empire}` mapping continues to work — `len(empire_order)` entries (one per empire), not `len(fleets)`
- [x] Updated `_collect_team_modifiers` to take `(fleets_by_empire, empire_order)` instead of a flat fleets list — picks one representative fleet per empire (lowest fleet.id) for the modifier collector

**Notes:** Discovered during Task 3.2 that the spec compiler emits one team per FLEET, not per OWNER. Without grouping at the spec-compiler layer, allied fleets would fight each other (engine has no alliances). So Task 3.1 is paired with Task 3.2 — they MUST land together. See expanded Task 3.2 for the spec compiler change.

---

### Task 3.2: Modify the spec compiler to group teams by `owner_id` [Medium]

**File:** `game/strategy/combat/spec_compiler.py`
**Tests:** `pytest tests/unit/strategy/combat/test_spec_compiler.py -v`

**Discovery:** `build_strategy_battle_spec` line 153 enumerated fleets, creating one TeamSpec per fleet. With multi-fleet-per-empire, this would put allied fleets on opposite sides. The Phase 3 plan originally assumed the spec compiler "already grouped by owner" but the audit found it didn't. Spec compiler change is therefore a real production change in scope.

- [x] Added `_team_spec_for_fleet_group(owner_fleets, *, team_id, entry_vector)` — replaces `_team_spec_for_fleet`; supports multiple fleets per team, each contributing its own TaskForce inside the team. Single-fleet case (every existing PROJ-275 caller) behaves identically to the deleted `_team_spec_for_fleet`.
- [x] Modified `build_strategy_battle_spec` to group fleets by `owner_id`. Used insertion order (`list(dict.keys())`) instead of `sorted(...)` so MagicMock fleets in tests with non-comparable owner_ids don't crash; canonical caller `_resolve_combat_at_hex` already sorts fleets by `(empire_id, fleet_id)` so insertion order IS sorted order in production.
- [x] Updated `_build_strategy_post_battle_hook` to mirror the per-owner grouping; `apply_outcome_to_fleets` already accepts `Mapping[int, List[Fleet]]` (verified in `post_battle_hook.py:43`).
- [x] Added `test_compiler_groups_multi_fleet_per_empire_into_one_team` in `test_spec_compiler.py` — passes after the change.

**Notes:** All 39 spec compiler / formation / post-battle-hook tests pass after the change. PROJ-275 N-team tests (3 fleets, one per empire) still produce 3 teams (3 unique owners) — backward-compatible.

---

### Task 3.3: Verify `_log_combat_result` event payload includes all participating fleets [Simple]

**File:** `game/strategy/engine/conflict_resolution_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_conflict_resolution_event_replay.py tests/integration/strategy/test_combat_round_budget.py::test_event_payload_includes_all_participating_fleets -v`

- [x] Verified `_log_combat_result` already iterates `participating_fleet_ids = [f.id for f in fleets]` over the FLAT fleets list (line 169 of conflict_resolution_engine.py). With Task 3.1's flat list now containing every participating fleet, the event payload automatically reflects all of them.
- [x] Confirmed `surviving_fleet_ids` and `destroyed_fleet_ids` (lines 359-360) similarly iterate the flat list.
- [x] `empire_id = min(participating_empire_ids)` (line 175) for the event filter column unchanged — Data-Flow Tracer agent verified this stays correct.

**Notes:** No code change required. The flat-list iteration in `_log_combat_result` was already shape-compatible with the new model.

---

### Task 3.4: Add integration tests for multi-fleet participation [Medium]

**File:** `tests/integration/strategy/test_combat_round_budget.py` (extended)
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py -v`

- [x] Added `test_two_fleets_one_empire_both_participate_in_battle`: Empire 0 has Fleet1 + Fleet2, Empire 1 has Fleet3, all co-located. Direct `_resolve_combat_at_hex` invocation (not the per-tick loop). Asserts the recorded resolver call contains all 3 fleet IDs `[101, 102, 201]`.
- [x] Added `test_event_payload_includes_all_participating_fleets`: Same setup. Captures `COMBAT_RESOLVED` event via a `_RecordingBus`. Asserts `participating_fleet_ids == [11, 12, 21]`.
- [x] Both tests pass. The existing `test_empire_with_two_fleets_each_contributes_rounds` (Phase 1) still fails — gated by Phase 4's per-fleet-tick triggering.

**Notes:** Used `_NonDestructiveResolver` from Phase 1 (no fleets wiped between rounds — test focus is participation, not destruction).

---

### Task 3.5: Run the affected test directories [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/ tests/integration/strategy/ tests/integration/save_load/ tests/unit/simulation/ tests/integration/simulation/
```

- [x] Final result: **9 failed, 7,332 passed, 1 skipped** — same 9 Phase-1-failing tests (gated by Phase 4 trigger predicate); zero new regressions from Phase 3.
- [x] All Phase 1 + Phase 2 tests still pass (regression guards intact).
- [x] All 39 spec compiler / formation / post-battle-hook tests pass (including the new Task 3.2 test).
- [x] Both new Phase 3 integration tests pass (Task 3.4).
- [x] PROJ-275 N-team tests (`test_three_empire_battle.py`) still pass — 3 unique owners → 3 teams, backward-compatible.
- [x] `test_simulation_adapter.py` now uses insertion-order grouping (no MagicMock sorting failure).

**Notes:** Mid-task scare: initial implementation used `sorted(fleets_by_owner.keys())` which broke 8 simulation_adapter tests (MagicMock `owner_id` not comparable). Switched to insertion-order — caller (`_resolve_combat_at_hex`) is already passing fleets in `(empire_id, fleet_id)` sorted order, so determinism is preserved at the layer that owns the responsibility. Lesson recorded in spec_compiler.py docstrings.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `_resolve_combat_at_hex` correctly batches all fleets per empire
- [x] Spec compiler groups fleets by `owner_id` (one team per empire)
- [x] `_log_combat_result` event payload reflects all participating fleets
- [x] Two new integration tests for multi-fleet-per-empire pass
- [x] No regression in N-team battle tests, simulation_adapter tests, or any other suite
- [x] Phase 1 + Phase 2 regression guards still pass
- [x] Phase 1 trigger-predicate + round-budget tests still fail (gated by Phase 4)
- [x] Update status at top of this file to `Complete`
- [x] Update [plan.md](plan.md) phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
