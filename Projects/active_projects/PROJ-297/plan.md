# PROJ-297: Code Review Cleanup - Quick Wins

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-297` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-297 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Architecture & Dead Code | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Stale Tests | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Documentation Fixes | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Tooling & Hygiene | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (approved, ready for implementation)
**Last Action:** Project created from 2026-04-26 code review report; claims verified
**Next Action:** Begin Phase 1 — move `component_state_key` to core, delete dead shims
**Blockers:** None
**Context for Next Agent:** Each finding in the source review report was verified before this plan was written. Refuted items (false `print()`, false TODO placeholders, false PROJ-296 emptiness) are NOT in scope. The FleetOrder rename (1.4a in the review) is split into its own project, **PROJ-298** — do not address it here.

## Overview
Remediate confirmed findings from the 2026-04-26 comprehensive code review. Scope is the small, low-risk, mostly mechanical cleanups: a layer violation fix, three dead-code deletions, three broken test files, four documentation factual errors, and dev-tool installation. Larger refactors (file size, deep nesting, type-annotation gap) and the FleetOrder rename are explicitly out of scope.

## Goals
- Eliminate the only confirmed Simulation→Strategy layer violation (Rule: layer separation)
- Eradicate three dead/legacy systems (System Migration Policy: no graveyards)
- Restore the test suite to a fully-collectible state (3 files currently fail collection)
- Bring CLAUDE.md and docs/ documentation factually in sync with the code
- Add `radon` and `vulture` to dev dependencies for ongoing quality scans

## Scope
**In:**
- Move `component_state_key` to `game/core/`
- Delete `game/simulation/formula_system.py` re-export shim
- Delete `game/core/singleton.py` (zero production users)
- Fix or delete 3 stale test files (collection errors)
- Fix pattern-count mismatch (CLAUDE.md=14, README=25, actual=27) and test-baseline mismatch (CLAUDE.md=14420, actual=15112)
- Add `resource_system.md` to docs/README.md reading table
- Remove deprecated `ship_stats_calculator.py` mention from `docs/04_SERVICES.md`
- Replace 2 bare `except:` with `except Exception:`
- Add `radon` and `vulture` to dev dependencies in `pyproject.toml`

**Out:**
- FleetOrder rename cleanup (1.4a) — see PROJ-298
- File bloat refactors (>500-line files)
- Deep-nesting refactors (4+ indent files)
- Type-annotation backfill (~40% gap)
- Mock-overuse refactor in `test_command_handlers.py`
- `battle_runner.py` DI cleanup — that's the documented PROJ-274 transitional fallback and should land with PROJ-274 closure
- Refuted findings: `print()` in battle_resolver.py:56 (it's in a docstring), 5 TODO/FIXME claim (only 2 real, no placeholders), PROJ-296 "empty" claim (it's the active LLM-services project)

## Key Files
| Component | File Path |
|-----------|-----------|
| Layer-violation source | `game/simulation/entities/ship_design_stats.py` (line 14) |
| Layer-violation symbol | `game/strategy/data/component_state.py` (lines 19-25) |
| New core module | `game/core/component_state.py` (TO BE CREATED) |
| Dead shim 1 | `game/simulation/formula_system.py` (20 lines, zero importers) |
| Dead shim 2 | `game/core/singleton.py` (97 lines, zero importers) |
| Stale test 1 | `tests/unit/ai/test_ai_protocols.py` (`IFormationMaster` missing) |
| Stale test 2 | `tests/unit/ai/test_behavior_units.py` (`FormationBehavior` missing) |
| Stale test 3 | `tests/unit/strategy/engine/test_build_order_command_handler.py` (`create_auto_load_population_order` missing) |
| Pattern count claim | `CLAUDE.md:119` (says "14") |
| Pattern count claim | `docs/README.md:17,66` (says "25") |
| Pattern count truth | `docs/02_PATTERNS.md` (header says "27 patterns", numbered ## 1.–## 27.) |
| Test baseline claim | `CLAUDE.md:312` (says "14420 passed") |
| Resource doc | `docs/systems/resource_system.md` (240 lines, exists, unlinked) |
| Deprecated entry | `docs/04_SERVICES.md:43` (`ship_stats_calculator.py` no longer exists) |
| Bare except 1 | `Reviews/scripts/calculate_agents.py:94` |
| Bare except 2 | `Tools/check_orphans/check_orphans.py:63` |
| Dev deps | `pyproject.toml` |

## Related Documents
- [design.md](design.md) - Verification evidence and design rationale
- [decisions.md](decisions.md) - Decisions log (scope split, refuted items, etc.)
- [PROJ-298](../PROJ-298/plan.md) - The split-out FleetOrder rename project

## Verification
- [ ] All phase checklists complete
- [ ] Full sharded suite at 15112+ passing (no regressions)
- [ ] `pytest tests/unit/ai/ tests/unit/strategy/engine/ --collect-only` shows zero collection errors
- [ ] `python -c "import game.simulation.formula_system"` raises ImportError
- [ ] `python -c "from game.core.singleton import SingletonMeta"` raises ImportError
- [ ] `grep -rn "14 design patterns\|25 design patterns" CLAUDE.md docs/` returns zero
- [ ] `grep -rn "14420" CLAUDE.md` returns zero
- [ ] User verified
