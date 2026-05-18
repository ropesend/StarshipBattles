# PROJ-406: Tier 2 — Audit-readiness reconciliation across PROJ-380..399

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Reconcile audit-readiness records + projects_index status | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09
**Active Phase:** Closeout
**Last Action:** Phase 1 complete. All 20 PROJ-380..399 projects now PASS `validate_audit_ready.py` (was 13/20 before; 7 of those 13 were Index-warning-only). 14 audit-failing projects (A-01..A-09) reconciled — phase checklists ticked, manifests populated where skeletal, plan Quick Status / Current State updated. A-10 index sweep flipped 20 rows from `Planning` → `Complete`. PROJ-395 honestly records MAJ-013/MAJ-014 deferrals → PROJ-409 (Wave 5). PROJ-397 Phase 3 fleet_id text now reflects implemented Path B.
**Next Action:** Awaiting user verification.
**Blockers:** None

## Overview
The independent review of PROJ-380..399 found that, while most projects landed their narrow code goals, the project-system bookkeeping is broadly inconsistent: phase checklists left at `Not Started` after implementation completed, manifests/design docs/decisions logs left as templates, and 14 entries in `Projects/projects_index.md` still showing `Planning` even though the work shipped. **No code changes** belong here — this is a single mechanical bookkeeping sweep that gets `validate_audit_ready.py` to PASS for every PROJ-380..399.

## Goals
- For each of the 14 audit-failing projects (A-01..A-09), make the phase checklists, plan Quick Status / Current State, manifests, and any other artifacts internally consistent with the actually-shipped state.
- Update `Projects/projects_index.md` row for **all** of PROJ-380..PROJ-399 to `Complete` (A-10 sweep).
- Final validator pass: `python Projects/scripts/validate_audit_ready.py PROJ-XXX` PASSED for every PROJ-380..399.

## Scope
**In:**
- Phase checklist Status fields, task checkbox states, phase Notes (filled with brief evidence pulled from each project's verification report or recent commits).
- `plan.md` Quick Status, Current State, Verification checkboxes.
- `manifest.md` and `design.md` — populate enough to remove the "skeletal" complaint flagged in the reviews; do NOT rewrite them as full design docs (these are post-hoc closeout artifacts, not pre-implementation plans).
- `Projects/projects_index.md` — flip 20 rows from `Planning` to `Complete` once each project's audit passes.

**Out:**
- Any code change. If a project's bookkeeping cannot honestly be marked complete because real work is missing, RAISE A BLOCKER and stop — that case is real Tier 1/3/4 follow-up, not Tier 2.
- Wave 1 projects (PROJ-400..405) — their bookkeeping is current.
- Tier 3 doc sweep — that's PROJ-407.

## Affected Projects (per REMEDIATION_PLAN Tier 2)
| Item | Project | Symptom |
|------|---------|---------|
| A-01 | PROJ-382 | Phases 1–5 still `Status: Not Started`. 12 errors, 32 unchecked tasks. Phase 5 Task 5.4 says "deferred" but file is now under 500 LOC. |
| A-02 | PROJ-393 | Phase 1/2/3 task sub-checkboxes unchecked; 3 deferrals (3.2/3.3/3.5) closed via PROJ-397 — reconcile. |
| A-03 | PROJ-395 | 2 of 14 MAJORs deferred (MAJ-013, MAJ-014). Plan claims complete. |
| A-04 | PROJ-397 | Every phase says `Not Started`; Phase 3 text contradicts implemented `fleet_id` decision (Path B simplified). |
| A-05 | PROJ-398 | Phase marked complete; Phase 1 tasks unchecked. Skeleton plan/manifest. |
| A-06 | PROJ-399 | Phase 1 unchecked; project index says `Planning`. |
| A-07 | PROJ-396 | Phase checklists/manifest/design/index never updated. Full regression claim unverifiable. |
| A-08 | PROJ-389 | Task 1.6 partial; verification unchecked; 4 test files + 3 doc files migrated beyond manifest. |
| A-09 | PROJ-384 | Blocker text still in plan; final regression task unchecked. |
| A-10 | All PROJ-380..399 | `Projects/projects_index.md` 20 rows still say `Planning`. |

## Key Files
| Component | File Path |
|-----------|-----------|
| Index | `Projects/projects_index.md` |
| Validators | `Projects/scripts/validate_audit_ready.py`, `Projects/scripts/validate_phase.py` |
| Per-project artifacts | `Projects/active_projects/PROJ-3XX/{plan,phase_*_checklist,manifest,design,decisions}.md` |

## Source Evidence
- `Reviews/results/2026-05-09_proj-380-399-implementation-review/REMEDIATION_PLAN.md` Tier 2 section (A-01..A-10).
- Each per-project review under the same directory.
- For each project, the verification report at `Projects/active_projects/PROJ-3XX/findings/verification_report.md` contains the actually-shipped state.

## Verification
- [x] Phase 1 checklist complete
- [x] `python Projects/scripts/validate_audit_ready.py PROJ-XXX` PASSED for every PROJ-380..399 (20/20; matrix recorded in `findings/audit_baseline.md`)
- [x] `Projects/projects_index.md` shows `Complete` for every PROJ-380..399
- [ ] User verified
