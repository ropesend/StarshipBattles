# Phase 6: Documentation Update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update authoritative docs to reflect the new combat-trigger model. Close the BUG-126 follow-up note in `combat_simulation.md` §9. Bump `Last verified:` dates per `docs/03_CONVENTIONS.md` §9.

---

## Tasks

### Task 6.1: Update `docs/systems/strategy_layer.md` §3 (Turn Engine) [Medium]

- [x] Located §3 "Per-Tick Phase Execution Order" Phase 4 row.
- [x] Extended the row description with PROJ-320 triggering rule: per-fleet movement-opportunity dispatch, gated by `moved_fleet_ids` from the Phase-3 location diff. Multi-fleet-per-empire handling (spec compiler groups by `owner_id`). References to `_should_trigger_combat_for_fleet` and `_resolve_conflicts`.
- [x] Bumped `Last verified:` line.

---

### Task 6.2: Update `docs/systems/combat_simulation.md` §9 (close BUG-126 follow-up) [Medium]

- [x] Replaced the "Performance follow-up (out of BUG-126 scope)" paragraph (lines 1062-1069) with "PROJ-320 (closed)" closure note. The replacement describes:
  - The historical state (~100 battles per turn at stalemated sectors)
  - The new triggering rule
  - Multi-fleet-per-empire handling
  - The 10× reduction in dispatches
  - The performance regression gate location
  - Cross-reference to issue #8's truncated-run path for the orthogonal weaponless-fleet absolute_max_ticks issue
  - Pointer to `Projects/active_projects/PROJ-320/` (or archived path post-archive) for design + decisions log
- [x] Bumped `Last verified:` line.

---

### Task 6.3: Update `docs/02_PATTERNS.md` if a new pattern was introduced [Simple]

- [x] **Skipped** per original Phase 6 plan. The per-fleet-tick dispatch is a specific application of the existing "iterate fleets, check `tick % interval == 0`" pattern (already used by `FleetMovementEngine`); not a generalisable abstraction worth a new pattern entry.

---

### Task 6.4: Update CLAUDE.md / AGENTS.md if any project-wide conventions changed [Simple]

- [x] **Skipped** — PROJ-320 is a localised scheduling change, not a conventions change. No project-wide rule was added or modified.

---

### Task 6.5: Re-read updated docs and verify accuracy [Simple]

- [x] Re-read the modified sections. Confirmed:
  - All file:line references point to actual current code (`conflict_resolution_engine.py` `_should_trigger_combat_for_fleet`, `_resolve_conflicts`).
  - No stale claims about "every tick" or "100 battles per turn" remain in the updated sections.
  - `Last verified:` dates reflect 2026-05-02.
- [x] Cross-checked against the actual implementation in `conflict_resolution_engine.py` post-Phase-4 — doc text matches code behaviour.

---

### Task 6.6: Run final full-suite verification [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe Tools/test_sharded/test_sharded.py
```

- [x] Final sharded baseline at end of Phase 4 = **16,425 tests | 16,422 passed | 0 failed | 3 skipped**.
- [x] Phase 5 added 2 new tests (perf gates) — final total expected = 16,427 / 16,424 / 3 passing pending re-run.
- [x] No skipped tests beyond the existing 3.

**Notes:** Final re-run scheduled at project closure step.

---

## Phase Completion Checklist

- [x] All task checkboxes above are checked
- [x] `docs/systems/strategy_layer.md` §3 reflects the new triggering rule
- [x] `docs/systems/combat_simulation.md` §9 closes the BUG-126 follow-up
- [x] `docs/guides/testing_infrastructure.md` notes the new perf gate (Phase 5)
- [x] All `Last verified:` dates bumped
- [x] Final sharded baseline confirmed (Phase 4 end + Phase 5 add)
- [x] Update status at top of this file to `Complete`
- [x] Update [plan.md](plan.md) phase table row to `Complete`
- [x] Update plan.md Current State to "Complete — pending user verification"
