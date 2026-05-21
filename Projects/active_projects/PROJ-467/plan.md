# PROJ-467: Docs cleanup — foundation: root agent + architecture/core docs + protocols (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-467` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-467 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical content errors | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major drift + rule alignment | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor path drift + staleness | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Codex-audit remediation (revision) | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-20
**Active Phase:** All phases complete (Phases 1-4)
**Last Action:** Codex audit returned 4 findings, all VERIFIED; added Phase 4 (revision) and remediated all 4. All phase validators PASS.
**Next Action:** Orchestrator commit + final audit gate
**Blockers:** None

## Overview
Created from the docs-audit at `Reviews/results/2026-05-20_073330_docs-audit/` after an independent third-pass re-verification that filtered the audit's claims (4 audit false positives rejected). This is the foundation/governance bundle: the root agent docs (`AGENTS.md`, `CLAUDE.md`), architecture/core docs (`docs/0N_*.md`), and procedural protocol docs (`Projects/protocols/`, `Reviews/protocols/`). It carries **1 CRITICAL item that actively misleads developers**: `AGENTS.md` declares the wrong Python baseline (3.14 vs the canonical 3.13+). 17 verified items total (was 18; `DEAD-PAT-legacy` dropped on revision — see below).

> **REVISION (2026-05-20, protocol 06):** The second CRITICAL item (`DEAD-PAT-legacy`: remove deleted-file pattern examples at `docs/02_PATTERNS.md:818-827`) was DROPPED after dual independent+Codex review. Those lines are explicitly marked as removed historical shims, not live examples — deleting them is churn, not accuracy work. Recorded in decisions.md.

## Goals
- Phase 1: Correct 1 CRITICAL content error (Python baseline in `AGENTS.md`). (Originally 2; the `02_PATTERNS.md` deleted-file-examples item was dropped on revision as a false/stale finding.)
- Phase 2: Fix 4 MAJOR items — broad-except rule drift in `CLAUDE.md`, the soon-to-be-deleted `_marked_for_deletion` reference, the dead `pathfinding.py` path in `03_CONVENTIONS.md`, and the wrong `json_utils.py` path in protocol 14.
- Phase 3: Fix 12 MINOR items — path-drift dead refs in `01_ARCHITECTURE.md` / `02_PATTERNS.md`, hardcoded checkout path, Combat-Lab non-pytest note, retired-protocol pointer in `WORKER_TEMPLATE.md`, perf-review example path, and missing `Last verified:` stamps.

## Scope
**In:** `dead_ref`, `content_error`, `cross_doc_inconsistency` (single-root-doc), and `doc_staleness` findings localized to root agent docs, `docs/0N_*.md`, and procedural protocol docs.
**Out:** Systems + guides docs (see sibling [PROJ-468](../PROJ-468/plan.md)); cross-doc/terminology findings spanning multiple files (see sibling [PROJ-469](../PROJ-469/plan.md)); REJECTED and OUT_OF_SCOPE items (see `findings/verification_report.md`).

## Key Files
| Doc File | Items |
|----------|-------|
| `docs/02_PATTERNS.md` | 4 |
| `AGENTS.md` | 3 |
| `docs/03_CONVENTIONS.md` | 2 |
| `docs/01_ARCHITECTURE.md` | 2 |
| `CLAUDE.md` | 3 |
| `Projects/protocols/14_create_from_error_audit.md` | 1 |
| `Projects/protocols/WORKER_TEMPLATE.md` | 1 |
| `Reviews/protocols/06_performance_review.md` | 1 |
| `docs/README.md` | 1 |
| `.agents/CODEX.md` | 1 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [findings/verification_report.md](findings/verification_report.md) - Independent re-verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) - Pointer to the source audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) - Interactive bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
