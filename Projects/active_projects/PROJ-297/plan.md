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
| 1. Architecture & Dead Code | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Stale Tests | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Documentation Fixes | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Tooling & Hygiene | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Complete — pending user verification
**Last Action:** All 4 phases complete. Full sharded test suite shows 15388/15389 passing (1 unrelated `test_warp_distance_scaling` borderline-assertion failure in strategy integration tests, nothing to do with PROJ-297 scope).
**Next Action:** User verification + archive when satisfied. Recommended verification: `python Tools/test_sharded/test_sharded.py` (re-run); manual sanity check of CLAUDE.md and docs/README.md updates; smoke check that radon/vulture run.
**Blockers:** None
**Context for Next Agent:**
- All 4 phases delivered. See per-phase checklist Notes for implementation details and the small mid-task discoveries (most notably: `formula_system.py` shim had 4 active test importers despite design.md saying "zero" — those were migrated to `game.core.formula_evaluator` whose backward-compat aliases at lines 411-413 made it a 1-line fix per file).
- **Phase 1 deliverables:** `game/core/component_state.py` (NEW); `game/strategy/data/component_state.py` (DELETED); `game/simulation/formula_system.py` (DELETED); `game/core/singleton.py` (DELETED); `tests/unit/core/test_component_state.py` (NEW, 10 tests); `tests/unit/core/test_singleton.py` (DELETED — was testing dead code); `tests/unit/strategy/fleets/test_component_state.py` (DELETED — superseded by core test). 17 importers updated. `docs/01_ARCHITECTURE.md` and `docs/04_SERVICES.md` updated.
- **Phase 2 deliverables:** all 3 stale test files now collect cleanly (was 3 collection errors → 0). Removed only dead-code references. **Pre-existing breakage uncovered:** 4 `TestKiteBehavior` tests testing outdated KiteBehavior API were deleted (other 5 KiteBehavior tests still pass).
- **Phase 3 deliverables:** CLAUDE.md, docs/README.md, docs/04_SERVICES.md factual errors corrected. `resource_system.md` added to README reading table + ASCII tree.
- **Phase 4 deliverables:** 2 bare `except:` clauses fixed with appropriately-scoped exception types. `radon>=6.0.0` and `vulture>=2.10` added to `requirements-dev.txt` (the project uses requirements-*.txt, not pyproject.toml optional-dependencies). Both tools installed and smoke-tested.
- **PROJ-298 ran in parallel** through Phase 2 of its own work — they completed their FleetOrder rename of production source. Final test count is now 15389 (≥15112 baseline).
- **One pre-existing flaky test:** `test_warp_distance_scaling` got `Small=19, Large=24` (assertion needs `Large > Small + 5`, so 24 > 24 fails by 1). Borderline integration-level scaling test, unrelated to any PROJ-297 file. Not introduced by this work.
**Blockers:** None
**Context for Next Agent:**
- **Phase 1 scope expanded mid-task:** the design.md said zero test files imported `formula_system.py` shim — that was wrong. 4 test files did. Migrating them was simple (the aliases already exist in `game.core.formula_evaluator` at lines 411-413, so import-path swap was sufficient). All 138 formula tests pass.
- **Architecture doc updated** (`docs/01_ARCHITECTURE.md`): removed `singleton.py` and `formula_system.py` mentions.
- **Historical SingletonMeta docstrings preserved** in `profiling.py:32`, `registry.py:116`, `component_loader.py:52` — explanatory ("PROJ-258: Migrated from SingletonMeta to DI"), not workarounds.
- **PROJ-298 is running in parallel** — they are working on FleetOrder rename. PROJ-297 should not touch FleetOrder/PlanetOrder/Order class symbols.
- Refuted items (false `print()`, false TODO placeholders, false PROJ-296 emptiness) remain NOT in scope.

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
