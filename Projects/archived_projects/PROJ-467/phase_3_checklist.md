# Phase 3: Minor path drift + staleness

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-467 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the 12 verified MINOR items: path-drift dead refs, hardcoded checkout path, Combat-Lab non-pytest note, retired-protocol pointer, perf-review example path, and missing `Last verified:` stamps, identified by audit `2026-05-20_073330_docs-audit`.

---

## Tasks

### Task 3.1: 01_ARCHITECTURE.md path drift [Simple]
**File:** `docs/01_ARCHITECTURE.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update dead reference `data/galaxy_protocols.py` (line 155) to `game/strategy/data/galaxy_protocols.py` (the same doc references the correct path at line 270)
- [x] Move the "pathfinding" mention from the `data/` listing (line 154) to the `services/` listing — pathfinding lives in `game/strategy/services/galaxy_pathfinding_service.py`, not `data/` (the `services/` listing at line 157 already reads "galaxy pathfinding"; removed the stray "pathfinding," from the `data/` listing)
- [x] Verify: `grep -rn "data/galaxy_protocols.py" docs/01_ARCHITECTURE.md` returns nothing

### Task 3.2: 02_PATTERNS.md package-path drift [Simple]
**File:** `docs/02_PATTERNS.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update `game/strategy/engine/commands.py` (line 170) to the `game/strategy/engine/commands/` package
- [x] Update `game/strategy/engine/command_handlers.py` (lines 187, 827) to the `game/strategy/engine/handlers/` package — **only** for refs that present it as a live path; leave any explicit "REMOVED/stale" warning-block mentions intact — N/A: both line-187 and line-827 mentions of `command_handlers.py` are inside explicit "(Removed PROJ-383)" warning blocks, so per the rule they are left intact. No live `command_handlers.py` path ref exists in this doc.
- [x] Rewrite the `data/classes/` reference (line 38) — reworded "data/classes/callables" to "data, classes, or callables" (it was a slash-separated list of value KINDS, not a directory path; `data/classes/` never existed). See decisions.md.
- [x] Verify: live (non-warning) references resolve to existing packages

### Task 3.3: 03_CONVENTIONS.md hardcoded checkout path [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Verification:** Read the doc end-to-end after edits; bump `Last verified:` stamp.

- [x] Replace the hardcoded user-memory path `C:/Users/rossr/.claude/.../feedback_one_component_per_role.md` (line 332) with a repo-relative reference or remove the external path — it violates the same doc's no-checkout-path convention (lines 231-240) — removed the broken external link; replaced with prose noting the preference lives in the per-user Claude auto-memory store, not the repo

### Task 3.4: AGENTS.md Combat-Lab non-pytest note + Last verified [Simple]
**File:** `AGENTS.md`
**Verification:** Read the doc end-to-end after edits.

- [x] Add a note where `python -m combat_lab.run_tests` is listed (line 27) clarifying the Combat Lab scenario suite does NOT run under pytest (mirrors `docs/guides/simulation_testing.md:16-17`)
- [x] Add a `> **Last verified:** YYYY-MM-DD` line below the H1

### Task 3.5: CLAUDE.md + CODEX.md Last verified [Simple]
**File:** `CLAUDE.md`
**Verification:** Read the doc end-to-end after edits.

- [x] Add a `> **Last verified:** YYYY-MM-DD` line below the H1 of `CLAUDE.md`
- [x] Add a `> **Last verified:** YYYY-MM-DD` line below the H1 of `.agents/CODEX.md`

### Task 3.6: README.md Last verified [Simple]
**File:** `docs/README.md`
**Verification:** Read the doc end-to-end after edits.

- [x] Add a `> **Last verified:** YYYY-MM-DD - <summary>` line below the `# Starship Battles Documentation Routing` heading

### Task 3.7: WORKER_TEMPLATE.md retired-protocol pointer [Simple]
**File:** `Projects/protocols/WORKER_TEMPLATE.md`
**Verification:** Read the doc end-to-end after edits.

- [x] Update line 37 ("Follow Protocol 08 (Automated Loop Protocol) strictly") to reflect the current workflow (Protocol 03a) — Protocol 08 is retired (the line-189 note already says so)

### Task 3.8: 06_performance_review.md example path [Simple]
**File:** `Reviews/protocols/06_performance_review.md`
**Verification:** Read the doc end-to-end after edits.

- [x] Update the example workflow path `game/combat/` (line 430) to `game/simulation/combat/` to match the real codebase structure

### Task 3.9: Phase-wide verification [Simple]
**File:** (multiple — verification only)

- [x] Verify: `Last verified:` stamps updated on all docs touched this phase; deterministic scan re-run shows zero dead refs in modified files

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_073330_docs-audit/`. See `findings/source_audit.md` for the link._
