# PROJ-344: Closeout Sprint 2 - Doc and test misalignments from PROJ-321..341 review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-344` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-344 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Doc + test misalignment cleanup (T2.1 .. T2.6) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff after PROJ-343 closeout)
**Last Action:** Project scaffolded
**Next Action:** Begin Phase 1 once PROJ-343 fresh-OpenCode review returns clean
**Blockers:** PROJ-343 should land first so the doc updates reflect the fixed reality. T2.5 (concurrent_commit_audit update) does NOT depend on PROJ-343 and could land earlier if a checkpoint window opens.

## Overview

Six small, mostly-textual fixes flagged by ≥2 reviewers each in the PROJ-321..341 review streams. All cross-validated. Minimal risk. Total effort: ~0.5 session. Each fix is one or two lines of markdown or a small test addition; commits are scoped per concern.

## Goals

- T2.1: PROJ-336 D-008 doc matches production "any non-positive load fills to capacity" semantics.
- T2.2: PROJ-327 `-3.9s` retraction is consistent across all 8+ in-repo references.
- T2.3: PROJ-332 docs say `harvesting` (matching production), not `harvest`.
- T2.4: `MockStrategyScreenComposition` guard has tests + correct docstring.
- T2.5: `concurrent_commit_audit.md` records all 4 contaminated commits, not just 2.
- T2.6: StrategySessionFacade public-method-surface invariant is preserved (PROJ-321 deletion replaced by PROJ-326 contract test, or restored if gap exists).

## Scope

**In:**
- `Projects/active_projects/PROJ-336/decisions.md` (T2.1)
- `Projects/active_projects/PROJ-327/{decisions.md, runtime_delta.md, phase_5_checklist.md, phase_1_checklist.md, virtual_table_runtime.md}` (T2.2)
- `docs/known-issues.md` (T2.2)
- `Projects/active_projects/PROJ-332/{design.md, phase_1_checklist.md}` (T2.3)
- `tests/unit/ui/screens/test_strategy_screen_composition.py` or wherever `MockStrategyScreenComposition` lives (T2.4 — both production class and test additions)
- `Projects/active_projects/PROJ-329A/findings/concurrent_commit_audit.md` (T2.5)
- `tests/unit/strategy/services/test_strategy_session_facade_contract.py` (T2.6 — read & verify; possibly restore method-surface invariant test)

**Out:**
- Any other findings from the review streams.
- Rebasing of the contaminated commits (per existing audit disposition).

## Key Files

| Component | File Path |
|-----------|-----------|
| T2.1 stale D-008 | `Projects/active_projects/PROJ-336/decisions.md` |
| T2.1 production reference | `game/strategy/services/fleet_cargo_projector.py:54-61` |
| T2.2 retraction multi-doc | `Projects/active_projects/PROJ-327/*.md`, `docs/known-issues.md:128,132` |
| T2.3 stale `harvest` | `Projects/active_projects/PROJ-332/{design.md:69-72, phase_1_checklist.md:31}` |
| T2.4 guard | `tests/unit/ui/screens/test_strategy_screen_composition.py` (locate via grep `MockStrategyScreenComposition`) |
| T2.5 audit | `Projects/active_projects/PROJ-329A/findings/concurrent_commit_audit.md` |
| T2.6 facade contract | `tests/unit/strategy/services/test_strategy_session_facade_contract.py` |

## Related Documents

- [design.md](design.md) — context analysis
- [decisions.md](decisions.md) — decisions log
- [manifest.md](manifest.md) — file manifest
- Master arc plan: `C:\Users\rossr\.claude\plans\you-are-picking-up-vivid-spindle.md`

## Verification

- [ ] All Phase 1 tasks checked
- [ ] `pytest tests/unit/strategy/services/ tests/unit/ui/screens/test_strategy_screen_composition.py -x -q` — all pass (only T2.4 + T2.6 changes touch tests)
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
