# PROJ-398: PROJ-380 remediation — 5 review MAJOR findings (consolidation refinements)

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. MAJOR follow-ups | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-09 (PROJ-406 reconciliation)
**Active Phase:** Closeout
**Last Action:** All 5 MAJOR findings (FND-012, FND-017, FND-031, FND-032, FND-041) closed across 3 commits (c6e0113ec, e14d7f1ce, 6744b44e1); see `phase_1_checklist.md` "Closed Findings" section for per-finding evidence.
**Next Action:** Awaiting user verification.
**Blockers:** None

## Overview
PROJ-380 (audit-shrink, 11 verified items + Phase 2 obsoletion + 9 Phase 3 consolidations) shipped in 12 commits. The OpenCode review had **0 CRITICAL** (good — agent's narrowing decisions held up) and 5 MAJOR follow-ups, mostly around the two narrowing calls (DUP-X-07, DUP-X-12) and the new ProviderFactory consolidation.

## Goals
- Address 5 MAJOR follow-up findings from the PROJ-380 review.

## Scope
**In:** 5 MAJOR findings from `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/report.md`.

**Out:** 8 MINOR + 30 INFO findings (the INFO count is high because the consolidation surface area was large; most are future-cleanup notes).

## Verification
- [x] All 5 MAJOR items closed (commits c6e0113ec, e14d7f1ce, 6744b44e1)
- [x] All tests passing (sharded baseline cleared post-Wave-1 by orchestrator)
- [x] Audit passed (`validate_audit_ready.py PROJ-398` PASSED after PROJ-406 reconciliation)
- [ ] User verified

_Source review: `Reviews/results/2026-05-09_015904_code_proj-380-audit-shrink-cleanup-3-phases-11-verified_req-req_20260509_015902_916201/`_
