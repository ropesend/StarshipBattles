# Phase 1: Minor — comment-only cleanups + doc-tag fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-393 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete 4 documentation comments that reference removed legacy code or carry stale PROJ tags. Zero logic changes; all 4 ship together as a single tiny PR.

---

## Tasks

### Task 1.1: Delete the 4 stale comments in one pass
**File:** Four files (one task to keep them in one PR)
**Tests:** `pytest tests/ --testmon` (sanity only — no logic change)

- [ ] Delete legacy snap comment at `game/simulation/combat/formation.py:357` (keep the EPS snap logic — only the comment is legacy) (LEG-03-002)
- [ ] Delete legacy `EnvironmentalEffects` path comment at `game/strategy/combat/spec_compiler.py:462` (the canonical PROJ-300 path lives just below) (LEG-03-003)
- [ ] Delete the historical `# legacy` comment at `game/strategy/systems/save_game_service.py:68` (audit verifier had said keep, but user opted to clean up alongside the rest) (LEG-02-005 INFO-included)
- [ ] Update or remove the stale `# PROJ-258: Initial implementation as wrapper around existing singletons.` comment at `game/context.py:13` — replace with a current-state line referencing PROJ-372 (or simply delete) (LEG-02-017 INFO-included)
- [ ] Verify: `pytest tests/ --testmon` passes (no logic changed); `grep -rn "PROJ-258" game/context.py` returns zero hits

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220621_legacy-audit/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
