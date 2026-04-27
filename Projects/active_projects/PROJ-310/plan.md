# PROJ-310: Deep Nesting Investigative Review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-310` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-310 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Quantify and rank deeply-nested code | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Categorize causes (per archetype) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Recommend remediation projects | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (approved, ready for investigation)
**Last Action:** Project created from 2026-04-26 review remaining-items list. Verified deep-nesting count: 389 of 563 `.py` files in `game/` (69.1%) contain code at 4+ indent levels (vs. claim of 373/67%)
**Next Action:** Begin Phase 1 — quantify deep nesting per file and per function with a Python AST script
**Blockers:** None — read-only project
**Context for Next Agent:** This is an INVESTIGATIVE project, not a refactor. Output is a written review document (`findings/nesting_review.md`) that proposes specific follow-up refactor projects. The user's directive: "I want a focused review on the > 3 layers deep nesting." 4-level nesting often signals a code-smell (compounded conditionals, nested loops, defensive checks) but is sometimes legitimate (parsing, state machines). The review must distinguish.

## Overview
Read-only investigation: identify the worst deep-nesting offenders, classify their causes (defensive checks, parser logic, nested loops, etc.), and recommend specific follow-up refactor projects. No production code changes.

This project produces a written review document. Subsequent projects (out of scope here) execute the recommended refactors.

## Goals
- Quantify deep nesting per file and per function (4+ indent levels)
- Identify the worst-offending files and functions
- Categorize each by cause: defensive checks / nested loops / state machine / parser / control flow
- Recommend specific remediation projects, sized appropriately

## Scope

**In:**
- All `.py` files under `game/` (production source)
- AST-level analysis: count nodes at each depth; per-function max depth
- Categorization: each high-nesting site classified by cause
- Written review: `findings/nesting_review.md` with quantitative summary, archetype catalog, and recommended remediation projects

**Out:**
- Test files (the 4-level nesting Python convention is for production source maintainability; tests have different ergonomics)
- ANY code changes (this is a research project)
- Implementation of the recommendations (each becomes its own follow-up project)

## Key Files
| Component | File Path |
|-----------|-----------|
| Investigation script | `Projects/active_projects/PROJ-310/findings/nesting_analysis.py` (NEW — small AST tool) |
| Per-file nesting metrics | `Projects/active_projects/PROJ-310/findings/nesting_metrics.csv` (NEW) |
| Final review | `Projects/active_projects/PROJ-310/findings/nesting_review.md` (NEW — the deliverable) |

## Related Documents
- [design.md](design.md) - Methodology
- [decisions.md](decisions.md) - Decisions log
- [PROJ-309 plan.md](../PROJ-309/plan.md) - File decomposition project (the reduction-in-deep-nesting that PROJ-309 produces by extraction may dent these numbers)

## Verification
- [ ] All phase checklists complete
- [ ] `findings/nesting_review.md` exists and answers: how bad is the problem, what are the worst sites, what should we do about them
- [ ] Review proposes specific follow-up projects (with rough sizing)
- [ ] User reviewed the deliverable
