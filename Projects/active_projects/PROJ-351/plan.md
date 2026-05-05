# PROJ-351: Closeout follow-up - Engine layer cleanup (T6.3 ActionExecutionEngine DI + T6.4 PlanetAbilities registry scan)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-351` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. T6.3 — ActionExecutionEngine consume injected resolver | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. T6.4 — PlanetAbilitiesController hardcoded list → registry scan | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff)
**Last Action:** Project scaffolded as a closeout follow-up to PROJ-349
**Next Action:** Begin Phase 1 (T6.3) — small DI refactor + test rewrite
**Blockers:** None
**Context for Next Agent:** Both items were deferred from PROJ-349 (Closeout Sprint 7) per Codex review consensus (`AgentCoordination/Scratchpad/Discussion/20260505T020232Z_proj343-349-codex-review/`). They share an "engine layer hygiene" theme: replace static-call / hardcoded-list patterns with proper DI / registry-scan idioms.

## Overview

Two engine-layer cleanups deferred from PROJ-349. Both are small, focused refactors that bring the codebase into compliance with documented conventions: T6.3 fixes a dead-DI surface; T6.4 replaces a hardcoded ability-name list with a registry-scan pattern per `docs/03_CONVENTIONS.md:500-512`.

## Goals

- T6.3: `ActionExecutionEngine` consumes its injected `_action_time_resolver` instead of always calling the static `ActionTimeResolver.resolve_action_time`. The dead-DI test pin in `tests/unit/strategy/engine/test_action_execution_engine_gaps.py:128-156` is rewritten to assert the injected resolver IS consulted.
- T6.4: `PlanetAbilitiesController` hardcoded ability-name lists at lines 29-48 are replaced with generic registry/data scans per `docs/03_CONVENTIONS.md:500-512`. Presentation labels preserved via ability metadata where available.

## Scope

**In:**
- `game/strategy/engine/action_execution_engine.py:55-68` (DI declaration), `:165-168` (consumer site)
- `tests/unit/strategy/engine/test_action_execution_engine_gaps.py:128-156` (test rewrite)
- `game/ui/screens/planet_abilities_controller.py:29-48` (hardcoded lists)
- Tests pinning the hardcoded lists (locate via grep)
- Possibly new tests asserting registry-driven discovery semantics

**Out:**
- Wider DI refactor of other engines.
- Changes to the ability registry itself.
- Any UI/screen changes beyond the controller's discovery method.

## Key Files

| Component | File Path |
|-----------|-----------|
| T6.3 production | `game/strategy/engine/action_execution_engine.py:55-68, 165-168` |
| T6.3 test pin | `tests/unit/strategy/engine/test_action_execution_engine_gaps.py:128-156` |
| T6.4 production | `game/ui/screens/planet_abilities_controller.py:29-48` |
| T6.4 convention | `docs/03_CONVENTIONS.md:500-512` |

## Related Documents

- [design.md](design.md) — context analysis
- [decisions.md](decisions.md) — decisions log
- [manifest.md](manifest.md) — file manifest
- Source synthesis: `AgentCoordination/Scratchpad/plans/proj321_341_unified_remediation_plan.md` (gitignored, Tier 6)
- Codex review consensus: `AgentCoordination/Scratchpad/Discussion/20260505T020232Z_proj343-349-codex-review/plans/proj343_349_remaining_plan_r003.md`

## Verification

- [ ] All phase checklists complete
- [ ] `pytest tests/unit/strategy/engine/ tests/unit/ui/screens/test_planet_abilities_controller* -x -q` — all pass
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
