# PROJ-349: Closeout Sprint 7 - Documentation drift and convention violations from review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-349` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Tier-6 documentation drift + convention violations | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Tier-7 polish (test-quality MAJORs) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Final closeout — full sharded suite + merge readiness | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff after PROJ-343..348 land)
**Last Action:** Project scaffolded
**Next Action:** Begin Phase 1
**Blockers:** PROJ-343..348 should land first; PROJ-349 is the final closeout that culminates in merge-readiness.

## Overview

Tier 6 (8 documentation drift + convention violations) and Tier 7 (test-quality MAJORs from synthesis lines 105-122). Mostly small, mechanical fixes. T6.1 (delete legacy save compat) requires user confirmation per CLAUDE.md "old saves disposable" rule + caution about explicit sign-off.

## Goals

**Tier 6:**
- T6.1: PROJ-decision on `PlanetaryFacility.from_dict()` legacy `resource_levels` fallback (delete or keep with rationale).
- T6.2: `RaceEnvironmentPanel` broad-catch annotated with `# Intentional broad catch: <reason>`.
- T6.3: `ActionExecutionEngine` actually uses injected `action_time_resolver` (or removes the parameter).
- T6.4: `PlanetAbilitiesController` hardcoded ability lists replaced with registry scan.
- T6.5: `LLMUnexpectedError` in ErrorCode taxonomy.
- T6.6: Strategy load dialog tracked as blocking modal.
- T6.7: `docs/05_ERROR_HANDLING.md` "Last verified" timestamp bumped.
- T6.8: Facade `_session` lint enforcement decision.

**Tier 7 (selected from synthesis lines 105-122):**
- LLMBackgroundCall `_done_event` race fix.
- `production_spawner` dispatch tests use `assert_called_once_with` (not `assert_called_once`).
- Brittle import patches in `_collect_team_modifiers` test.
- Dead-branch pin annotations in `_apply_damage_to_ship` (link to ticket).
- ActionExecutionEngine dead-DI test — link to ticket once T6.3 lands.
- PROJ-332 5 lazy-property defaults + `create_default_turn_engine` factory test.
- PROJ-335 4 from_dict gaps.
- PROJ-336 2 vacuous module-constant tests.
- `test_get_font_enforces_minimum_size_8` quantize-to-2 step.
- PROJ-326 misc (allowlist header, AST linter blind spot, Python version comment).
- `test_format_value_zero_thousands_and_rounding` brittleness.
- `test_first_tick_clears_shortage_logged_flags` ambiguous reset.
- PROJ-321 deleted `test_start_battle_ship_builder_*` — REWRITE not delete (recover from history).
- `TestRegisterOnConstruction` retrofit — currently doesn't test construction-registration.
- `bypass_init` MRO leak risk on base classes under pytest-xdist.
- `race_setup/screen.py` (484 LOC) and `new_game_setup_screen.py` (733 LOC) §2.4 violations — DEFER to dedicated split projects if scope balloons.

**Final closeout (Phase 3):**
- Full sharded suite: `python Tools/test_sharded/test_sharded.py`.
- `Projects/projects_index.md` final status pass.
- Merge-readiness summary to user.

## Scope

**In:** all Tier-6 and Tier-7 items listed above.

**Out:**
- T6.1 production-code change without user sign-off.
- §2.4 LOC-ceiling refactors of `race_setup/screen.py` (484 LOC) and `new_game_setup_screen.py` (733 LOC) — these are non-trivial splits. NOTED in this project's design.md, deferred to a follow-up if scope grows.

## Key Files

| Component | File Path |
|-----------|-----------|
| T6.1 | `game/strategy/data/planetary_facility.py:73, 80-81` |
| T6.2 | `game/ui/panels/race_environment_panel.py:322-333` |
| T6.3 | `game/strategy/engine/action_execution_engine.py:55-68, 165-168` |
| T6.4 | `game/ui/screens/planet_abilities_controller.py:29-48` |
| T6.5 | `game/services/llm/errors.py` |
| T6.6 | `game/ui/screens/strategy_screen_lifecycle.py:64-77`, `strategy_window_manager.py:122-143` |
| T6.7 | `docs/05_ERROR_HANDLING.md` |
| T7 LLM race | `game/services/llm/background.py:210, 291-297` |
| T7 spawner | `tests/unit/strategy/engine/test_production_spawner.py` |
| T7 PROJ-321 | locate via grep on the deleted test name |

## Verification

- [ ] All 3 phase checklists complete
- [ ] `python -m pytest tests/unit/ -q` — full unit suite green
- [ ] `python Tools/test_sharded/test_sharded.py` from repo root — full sharded suite green
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] All PROJ-321..341 follow-on projects (343..349) marked `Awaiting Verification`
- [ ] Merge-readiness summary delivered to user
- [ ] User verified
