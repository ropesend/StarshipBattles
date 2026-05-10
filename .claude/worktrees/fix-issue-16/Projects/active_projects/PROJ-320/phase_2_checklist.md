# Phase 2: Fleet-Speed Invariant Audit

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** **REFRAMED FROM ORIGINAL PLAN.** During Phase 1, the suspected pre-existing bug in `OrderProcessor._execute_fleet_merge` (Risk Assessor finding HIGH #3) was investigated and **does not exist** — `Fleet.merge_with` already calls `other_fleet.trigger_speed_recalculation()` at `game/strategy/data/fleet.py:459`. Phase 1 wrote a regression guard (`tests/unit/strategy/engine/test_order_processor_fleet_merge.py`) that locks the existing correct behaviour.

Phase 2 became a **defensive sweep** of all `Fleet.ships`-mutation sites in `game/strategy/` to confirm every one of them either (a) goes through `Fleet.add_ship` / `Fleet.remove_ship` / `Fleet.merge_with` (which all trigger recalc) or (b) calls `trigger_speed_recalculation` itself. The new combat-trigger model (Phase 4) depends on `fleet.speed` always reflecting the slowest ship — drift here would produce wrong opportunity-tick cadence.

See [decisions.md](decisions.md) row dated 2026-05-02 (CORRECTION) for the full backstory.

---

## Tasks

### Task 2.1: Sweep `game/strategy/` for `Fleet.ships`-mutation sites [Medium]

**Files:** Search across `game/strategy/` (read-only sweep)
**Tests:** None for this task — investigation only

- [x] Run `Grep` with pattern `\.ships\.(append|extend|remove|pop|clear|insert)|fleet\.ships\s*=` scoped to `game/strategy/data/`, `game/strategy/combat/`, `game/strategy/adapters/`, `game/strategy/engine/`.
- [x] Classify each match (see audit table below).
- [x] Confirm `apply_outcome_to_fleets` (post_battle_hook.py) goes through `Fleet.remove_ship` (it does — line 172 `fleet.remove_ship(instance)`).

**Audit findings:**

| File:line | Mutation kind | Status | Notes |
|-----------|--------------|--------|-------|
| `game/strategy/data/fleet.py:157` | `self.ships.append(ship)` in `Fleet.add_ship` | safe | Followed by `self.trigger_speed_recalculation()` at line 158 |
| `game/strategy/data/fleet.py:163` | `self.ships.remove(ship)` in `Fleet.remove_ship` | safe | Followed by `self.trigger_speed_recalculation()` at line 164 |
| `game/strategy/data/fleet.py:451` | `other_fleet.ships.extend(self.ships)` in `Fleet.merge_with` | safe | Followed by `other_fleet.trigger_speed_recalculation()` at line 459. Phase 1 regression-guarded. |
| `game/strategy/data/fleet.py:452` | `self.ships.clear()` in `Fleet.merge_with` | safe (irrelevant) | Source fleet is then deleted from the empire entirely; its speed never read again |
| `game/strategy/data/fleet.py:541` | `fleet.ships.append(ship)` in `Fleet.from_dict` | safe (by design) | Restores saved `speed` field verbatim. See Task 2.2 for the detailed reasoning |
| `game/strategy/combat/post_battle_hook.py:172` | `fleet.remove_ship(instance)` (delegated) | safe | Goes through Fleet.remove_ship (recalcs) |
| `game/strategy/combat/`, `game/strategy/adapters/`, `game/strategy/engine/` | (no direct ships-list mutations) | safe | All external callers go through Fleet methods |

**Notes:** Bound the audit was intended to be ~30 minutes; landed in ~10 minutes because the surface area is small. The Fleet API (`add_ship`/`remove_ship`/`merge_with`) is the single mutation chokepoint for all production code; `from_dict` is the only direct mutator and is intentionally non-recalcing (see 2.2).

---

### Task 2.2: Lock the `from_dict` no-recalc design choice [Simple]

**File:** `tests/unit/strategy/engine/test_fleet_speed_invariants.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_speed_invariants.py -v`

- [x] **First attempt:** Added `fleet.trigger_speed_recalculation()` at the end of `Fleet.from_dict` (defensive recalc to handle hand-edited saves).
- [x] **Result:** Broke 19 existing save-round-trip tests. The test fixtures use `ShipInstance` objects without proper `get_calculated_stats()`, so `calculate_fleet_speed` returns 0 for them — the recalc zeroed out the saved speed.
- [x] **Reverted** the production change. The trade-off (defensive guard vs round-trip breakage) is not worth it; saved `speed` IS the slowest-ship speed at save time, so normal play preserves the invariant.
- [x] Wrote `test_from_dict_preserves_saved_speed_without_recalcing` — pins the design choice so a future agent doesn't reintroduce the recalc and re-break round-trip tests. Comments in `Fleet.from_dict` and the test file both reference this discovery.

**Notes:** Real-world risk of a from_dict speed mismatch is hypothetical (would require hand-edited saves or a save-format mismatch). Per CLAUDE.md "saves are disposable", deferring this defensive measure to a future ticket if it ever surfaces is correct.

---

### Task 2.3: Run the affected test directories [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe -m pytest tests/unit/strategy/ tests/integration/strategy/ tests/integration/save_load/ -v
```

- [x] All previously-passing tests still pass — confirmed via `tests/integration/save_load/test_roundtrip_fleet.py` (8 tests pass) and `test_order_processor_fleet_merge.py` (2 tests pass)
- [x] Phase 1's `test_order_processor_fleet_merge.py` still passes
- [x] Phase 2's new `test_fleet_speed_invariants.py` passes
- [x] Phase 1's failing tests (`test_conflict_round_budget.py`, `test_combat_round_budget.py`) STILL fail (gated by Phases 3 + 4 — correct red baseline preserved)

**Notes:** Net new test count: +1 (the from_dict pin). No production-code change shipped in Phase 2. The audit confirmed the existing invariant chain works correctly.

---

## Phase Completion Checklist

When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Audit table in Task 2.1 lists every Fleet.ships-mutation site with classification
- [x] No suspect sites required production-code changes
- [x] from_dict design choice is pinned by a regression test
- [x] Phase 1's regression guard still passes
- [x] Phase 1's failing tests still fail (correct red baseline preserved)
- [x] Update status at top of this file to `Complete`
- [x] Update [plan.md](plan.md) phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
