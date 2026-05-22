# Phase 1: Re-inventory tooling imports against post-474/475/477 live code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-476 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Confirm PROJ-474/475/477 have landed, then derive the EXACT
post-gate tooling-exemption residue set from live code (the 2026-05-22 snapshot
in plan.md is provisional). Produce the authoritative triple list Phase 2 will
encode. No code/guard edits in this phase.

---

## Tasks

### Task 1.1: Confirm the gate is cleared [Simple]
**Files:** `Projects/active_projects/PROJ-474/plan.md`, `PROJ-475/plan.md`, `PROJ-477/plan.md`
**Tests:** n/a (verification only)

- [ ] Confirm PROJ-474 is COMPLETE: `_UISAFE_SYMBOLS` exists in
      `tests/static_guards/test_facade_read_path_imports_guard.py` and the pure
      symbols (`RaceConfig`, `RacePointBudget`, `FieldStatus`, `PlanetType`,
      `BattleRole`, `CombatPolicy`, `VALID_GALAXY_TYPES`, `StrategicKind`,
      `abilities_with_kind_tag`, `SUPERWEAPONS`) are no longer in the tooling
      files' `TAIL` lines.
- [ ] Confirm PROJ-475 + PROJ-477 are COMPLETE (live `.session` readers + render
      pass-throughs migrated; their guard allowlist entries removed).
- [ ] If any of 474/475/477 is NOT complete: STOP. PROJ-476 is gated; do not
      proceed.
- [ ] Verify: gate-clearance state recorded in Notes below.

### Task 1.2: Re-grep for session reads in the tooling dirs [Simple]
**Files:** `game/ui/screens/{battle_setup,galaxy_test,race_setup,builder}/`, `battle_setup_state.py`, `design_selector_window.py`, `workshop_event_router.py`
**Tests:** grep (no test change)

- [ ] Grep `\.session\b|\._session\b|facade_state\.session` across all in-scope
      tooling files. EXPECT zero matches (confirmed 2026-05-22).
- [ ] If any match appears (a regression introduced by 475/477 or new code):
      STOP and reclassify — that file may belong to PROJ-475/477, not 476.
- [ ] Verify: confirm PROJ-476 remains import-guard-only.

### Task 1.3: Re-inventory the tooling `game.strategy.*` imports [Medium]
**Files:** in-scope tooling files (see plan.md "Key Files")
**Tests:** grep / AST (no test change)

- [ ] Grep `from game.strategy|import game.strategy` across each tooling file;
      list every runtime (non-`TYPE_CHECKING`) `(file, module, member)` import.
- [ ] For each, classify: UISAFE (already moved by 474 → DROP from 476) |
      tooling-exemption (KEEP) | live-defer (should already be gone via 475/477;
      if present, flag).
- [ ] Cross-check the residual `TAIL` block of the import guard: every remaining
      tooling-file triple must be a genuine tooling exemption.
- [ ] Re-confirm the screens-root boundary: `battle_setup_state.py` IN;
      `design_selector_window.py` + `workshop_event_router.py` IN
      (`design-editor`); `build_queue_panel_factory.py` OUT.
- [ ] Verify: produce the authoritative `_TOOLING_EXEMPTIONS` triple set (with
      tag + reason per entry) in Notes — this is Phase 2's input.

**Notes:** [Filled during execution — record gate state, grep results, and the
final triple set. Flag any drift from the 2026-05-22 plan snapshot.]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] The authoritative post-gate triple set is recorded in Notes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
