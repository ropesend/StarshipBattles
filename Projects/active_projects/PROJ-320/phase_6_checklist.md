# Phase 6: Documentation Update

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-320 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update authoritative docs to reflect the new combat-trigger model. Close the BUG-126 follow-up note in `combat_simulation.md` §9. Bump `Last verified:` dates per `docs/03_CONVENTIONS.md` §9. The docs are the source of truth — code and docs must agree (CLAUDE.md "Documentation First" rule).

---

## Tasks

### Task 6.1: Update `docs/systems/strategy_layer.md` §3 (Turn Engine) [Medium]

**File:** `docs/systems/strategy_layer.md`
**Tests:** None — doc change. Visual review only.

- [ ] Locate §3 "Turn Engine" → "Per-Tick Phase Execution Order" (around line 183)
- [ ] In the Phase 4 row description (`ConflictResolutionEngine` → "Combat detection and resolution"), add a sub-bullet or footnote explaining the new triggering rule:
  > **PROJ-320:** Combat is dispatched per-fleet on each fleet's movement-opportunity tick (`tick % get_tick_interval(fleet.speed) == 0`), gated by whether the fleet successfully left the contested hex on that tick. Replaces the legacy per-tick contested-hex scan (~100 battles per turn) with one battle per fleet per movement opportunity. Multi-fleet-per-empire encounters now have every fleet contributing rounds independently.
- [ ] Locate `_resolve_combat_at_hex` references in the doc (search for "ConflictResolution") and ensure they reflect the new `Dict[int, List[Fleet]]` shape.
- [ ] Bump the `Last verified:` line at the top of the file per `docs/03_CONVENTIONS.md` §9 (format: `> **Last verified:** YYYY-MM-DD — PROJ-320 ...`).

**Notes:** Keep the prose changes minimal — the doc is large and dense. The point is to record the model, not to lecture.

---

### Task 6.2: Update `docs/systems/combat_simulation.md` §9 (close BUG-126 follow-up) [Medium]

**File:** `docs/systems/combat_simulation.md`
**Tests:** None — doc change.

- [ ] Locate §9 "Multi-Team Battle Support (PROJ-275)" → "Performance follow-up (out of BUG-126 scope)" paragraph (around line 1054-1061). The current text reads:
  > Two stationary co-located fleets re-engage every sub-tick of every turn (up to 100 battles per turn) until one side is wiped... A follow-on ticket should add an early-termination condition...
- [ ] Replace with PROJ-320 closure note:
  > **PROJ-320 (closed):** Two stationary co-located fleets historically re-engaged every sub-tick (~100 battles per turn). PROJ-320 reframed strategy combat to per-fleet movement-opportunity triggering: combat fires once per fleet per `tick % get_tick_interval(fleet.speed) == 0` tick, gated by whether the fleet left the hex that tick. A speed-6 vs speed-4 stalemate now resolves in 6 + 4 = 10 rounds (10× reduction vs the legacy per-tick path). Multi-fleet-per-empire encounters now have every fleet contributing rounds independently. See `Projects/active_projects/PROJ-320/` (or `Projects/archived_projects/PROJ-320/` post-archive) for design and decisions.
- [ ] Bump the `Last verified:` line.

**Notes:** Pre-existing strategy `absolute_max_ticks` ceiling tightening is still a separate optimization opportunity — leave a one-line note pointing that out if it was previously documented.

---

### Task 6.3: Update `docs/02_PATTERNS.md` if a new pattern was introduced [Simple]

**File:** `docs/02_PATTERNS.md`
**Tests:** None.

- [ ] Read the patterns index. If "per-fleet movement-opportunity triggering" feels like a reusable pattern (not a one-off), add it as Pattern #32 with a brief example. Otherwise, skip.
- [ ] **Likely outcome:** SKIP — the pattern is internal to `ConflictResolutionEngine` and not a generalizable abstraction. The pattern is a specific application of "iterate fleets, check `tick % interval == 0`" which already lives in `FleetMovementEngine`.

**Notes:** Pattern Scout swarm agent did not recommend a new pattern. Default is to skip.

---

### Task 6.4: Update CLAUDE.md / AGENTS.md if any project-wide conventions changed [Simple]

**File:** `CLAUDE.md`, `AGENTS.md`
**Tests:** None.

- [ ] Read both files. Confirm no project-wide rule was changed by PROJ-320.
- [ ] **Expected outcome:** SKIP — PROJ-320 is a localized scheduling change, not a conventions change.

**Notes:** Default is to skip.

---

### Task 6.5: Re-read updated docs and verify accuracy [Simple]

**Tests:** None.

- [ ] Read the modified sections of `strategy_layer.md` and `combat_simulation.md` end-to-end. Confirm:
  - All file:line references point to actual current code
  - No stale claims about "every tick" or "100 battles per turn" remain
  - `Last verified:` dates reflect today's date
- [ ] Cross-check against the actual implementation in `conflict_resolution_engine.py` post-Phase-4 — confirm the doc text matches the code.

**Notes:** This is the "code and docs must agree" rule (CLAUDE.md Rule 2). If a discrepancy is found here, fix the doc OR open a follow-up ticket if the code is wrong.

---

### Task 6.6: Run final full-suite verification [Simple]

**Tests:**
```bash
.venv/Scripts/python.exe Tools/test_sharded/test_sharded.py
```

- [ ] Final sharded baseline passes
- [ ] Total test count is approximately baseline + new tests added in Phases 1-5 (~16,374 + 10-15 new)
- [ ] No skipped tests beyond the existing 3
- [ ] Document the final count in this checklist's `Notes`

**Notes:** This is the gate before user verification. If anything regresses, drop back to the offending Phase and fix.

---

## Phase Completion Checklist

When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `docs/systems/strategy_layer.md` §3 reflects the new triggering rule
- [ ] `docs/systems/combat_simulation.md` §9 closes the BUG-126 follow-up
- [ ] All `Last verified:` dates bumped
- [ ] Final sharded baseline passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update [plan.md](plan.md) phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete — pending user verification"
- [ ] Notify user the project is ready for manual end-turn smoke testing
