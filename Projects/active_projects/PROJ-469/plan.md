# PROJ-469: Docs cleanup — cross-doc consistency + terminology (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-469` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-469 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Cross-doc consistency + terminology | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Codex-audit follow-ups (terminology drift in satellites.md recovery; checklist objective count) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-20
**Active Phase:** Phase 2 complete — implementation done, awaiting user verification
**Last Action:** Implemented Phase 1 (3 surviving cross-doc/terminology fixes + satellites.md sibling #40→#41 occurrences) and Phase 2 (Codex-audit follow-ups: satellites.md recovery-prose DeployedGroup drift; checklist objective count). Codex audit ran one round (3 (c) findings: 2 VERIFIED + implemented, 1 REJECTED + logged as DI-2026-05-21-003). Out-of-scope sibling #40 refs logged as DI-2026-05-21-004.
**Next Action:** User verification; orchestrator commits.
**Blockers:** None

## Overview
Created from the docs-audit at `Reviews/results/2026-05-20_073330_docs-audit/` after an independent third-pass re-verification. This is the dedicated cross-doc consistency bundle (protocol 17 always isolates terminology/cross-reference findings so a single reviewer applies a canonical decision uniformly). Originally 4 verified MAJOR findings; after the 2026-05-20 revision (protocol 06, dual independent+Codex review) the README "33 patterns" finding was DROPPED as a stale finding (README:169 already frames it as a stale-name warning, not a live assertion — see decisions.md). 3 surviving findings span three doc files: a wrong pattern-number cross-reference (also fixed at a sibling occurrence in satellites.md:13), an internal terminology contradiction (Fleet vs DeployedGroup), and a cross-reference to a non-existent directory.

## Goals
- Phase 1: Fix 3 MAJOR cross-doc/terminology issues (down from 4; README "33 patterns" dropped as stale finding) — correct the Pattern #40→#41 cross-reference in `03_CONVENTIONS.md` (and the sibling occurrence in `satellites.md`), the "satellite_group fleet namespace"→deployed-group terminology in `satellites.md`, and the `newdocs/02_PATTERNS.md`→`docs/02_PATTERNS.md` dead cross-reference in `testing_infrastructure.md`.

## Scope
**In:** `terminology_drift` and `cross_doc_inconsistency` findings that span multiple files or carry a canonical-term/canonical-location decision.
**Out:** Root agent / architecture / protocol docs (see sibling [PROJ-467](../PROJ-467/plan.md)); systems + guides dead refs and content errors (see sibling [PROJ-468](../PROJ-468/plan.md)); REJECTED and OUT_OF_SCOPE items including the audit's own false-positive cross-doc claims (see `findings/verification_report.md`).

## Key Files
| Doc File | Items |
|----------|-------|
| `docs/03_CONVENTIONS.md` | 1 (#40→#41) |
| `docs/README.md` | 0 (finding dropped — see decisions.md) |
| `docs/systems/satellites.md` | 2 (fleet→deployed-group terminology; sibling #40→#41 at line 13) |
| `docs/guides/testing_infrastructure.md` | 1 (newdocs dead ref) |

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
