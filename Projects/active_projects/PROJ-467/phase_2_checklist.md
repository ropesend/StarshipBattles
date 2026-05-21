# Phase 2: Major drift + rule alignment

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-467 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Correct the 4 verified MAJOR items: broad-except rule drift in `CLAUDE.md`, the `_marked_for_deletion` pointer, the dead `pathfinding.py` path in `03_CONVENTIONS.md`, and the wrong `json_utils.py` path in protocol 14, identified by audit `2026-05-20_073330_docs-audit`.

---

## Tasks

### Task 2.1: CLAUDE.md broad-except rule + marked-for-deletion pointer [Simple]
**File:** `CLAUDE.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Remove "or immediately above" from the broad-except rule (line 112) to match canonical wording in `AGENTS.md:54` and `docs/03_CONVENTIONS.md:427` ("`# Intentional broad catch: <reason>` on the same line")
- [x] Remove or restructure the `_marked_for_deletion_2026-05-29/Projects/` reference (line 5) — it points to a directory scheduled for deletion 2026-05-29; do not direct agents to a soon-deleted location

### Task 2.2: 03_CONVENTIONS.md dead pathfinding path [Simple]
**File:** `docs/03_CONVENTIONS.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves; bump `Last verified:` stamp.

- [x] Update dead reference `game/strategy/data/pathfinding.py` (line 32) — `get_system_at_hex()` now lives in `game/strategy/services/galaxy_pathfinding_service.py` (`GalaxyPathfindingService.get_system_at_hex()`, confirmed at `galaxy_pathfinding_service.py:113`)
- [x] Verify: `grep -rn "data/pathfinding.py" docs/03_CONVENTIONS.md` returns nothing

### Task 2.3: Protocol 14 wrong json_utils path [Simple]
**File:** `Projects/protocols/14_create_from_error_audit.md`
**Verification:** Read the doc end-to-end after edits; check every cited code reference resolves.

- [x] Correct `game/services/json_utils.py` to `game/core/json_utils.py` at line 124 (and the `# I/O pattern` comment at line 122) — actual path is `game/core/json_utils.py`; `game/services/json_utils.py` does not exist
- [x] Verify: `grep -rn "game/services/json_utils.py" Projects/protocols/14_create_from_error_audit.md` returns nothing

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_073330_docs-audit/`. See `findings/source_audit.md` for the link._
