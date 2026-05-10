# Phase 3: Documentation Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-297 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Bring CLAUDE.md and `docs/` into factual alignment with the codebase. Four confirmed mismatches: pattern count (14/25 → 27), test baseline (14420 → 15112), missing `resource_system.md` link, and a deleted-file mention in `04_SERVICES.md`.

---

## Tasks

### Task 3.1: Fix pattern count in CLAUDE.md and docs/README.md [Simple]
**File:** `CLAUDE.md`, `docs/README.md`
**Tests:** Manual grep verification

Three independent statements about pattern count exist; the actual number per `docs/02_PATTERNS.md` is **27**.

- [x] Read `CLAUDE.md` line 119 — confirm it currently says "14 design patterns"
- [x] Update `CLAUDE.md` line 119: change "14 design patterns" → "27 design patterns"
- [x] Read `docs/README.md` lines 17 and 66 — confirm both currently say "25 design patterns"
- [x] Update `docs/README.md` line 17 (table row): "25 design patterns" → "27 design patterns"
- [x] Update `docs/README.md` line 66 (ASCII tree comment): "25 design patterns" → "27 design patterns"
- [x] **Verification:** `grep -rn "14 design patterns\|25 design patterns" CLAUDE.md docs/` returns zero results
- [x] **Verification:** `grep -rn "27 design patterns" CLAUDE.md docs/` returns at least 3 matches

**Notes:**

---

### Task 3.2: Fix test baseline in CLAUDE.md [Simple]
**File:** `CLAUDE.md`
**Tests:** Manual verification

`CLAUDE.md:312` says "Baseline: 14420 passed, 0 skipped." The current verified baseline is 15112 (per MEMORY index entry for PROJ-295).

- [x] Read `CLAUDE.md` lines 305-315 to see surrounding context
- [x] Update line 312: "14420 passed" → "15112 passed"
- [x] Check whether other lines reference baseline counts (e.g., line 273 mentions `pytest tests/ -n 12`); update any other stale numbers
- [x] **Verification:** `grep -n "14420" CLAUDE.md` returns zero results

**Notes:**

---

### Task 3.3: Add `resource_system.md` to docs/README.md reading table [Simple]
**File:** `docs/README.md`
**Tests:** Manual verification

`docs/systems/resource_system.md` exists (240 lines) but is not referenced in the README's reading table or ASCII tree.

- [x] Read `docs/README.md` lines 36-45 (reading table) — identify the format used for other system docs (Combat, Abilities, Strategy, AI, Research, Orders, Production)
- [x] Add a row for `[systems/resource_system.md](systems/resource_system.md)` describing what it covers (read the file's intro paragraph to write a one-line description)
- [x] Read `docs/README.md` near line 66 (ASCII tree) — add `resource_system.md` in alphabetical order under the `systems/` section
- [x] **Verification:** `grep -n "resource_system" docs/README.md` returns at least 2 matches (table row + tree entry)

**Notes:**

---

### Task 3.4: Remove deprecated `ship_stats_calculator.py` mention from `docs/04_SERVICES.md` [Simple]
**File:** `docs/04_SERVICES.md`
**Tests:** Manual verification

The file `game/strategy/services/ship_stats_calculator.py` was deleted; only `__pycache__/.pyc` artifacts remain. `docs/04_SERVICES.md:43` still lists it as DEPRECATED. Per System Migration Policy (eradicate, don't graveyard), the entry should be removed entirely.

- [x] Read `docs/04_SERVICES.md` lines 35-55 to see surrounding context
- [x] Identify the entire entry/row referencing `ship_stats_calculator.py` (likely a table row or section)
- [x] Delete the entry (do not replace with a "moved to X" pointer — Migration Policy says full eradication)
- [x] If the deletion leaves an orphaned section heading or reference elsewhere in the doc, clean it up
- [x] **Verification:** `grep -n "ship_stats_calculator" docs/04_SERVICES.md` returns zero results

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `grep -rn "14 design patterns\|25 design patterns\|14420\|ship_stats_calculator" CLAUDE.md docs/` returns zero results
- [x] `grep -rn "resource_system" docs/README.md` returns at least 2 matches
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 4: Tooling & Hygiene)
