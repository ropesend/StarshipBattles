# PROJ-244: Team Naming Standardization

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-244` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-244 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Rename all production code (signatures, call sites, local vars) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Update test fixtures and verify full suite | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-04-05
**Active Phase:** Planning
**Last Action:** Plan rewritten with full protocol compliance and swarm findings
**Next Action:** Begin Phase 1 — rename BattleEngine.start() parameters
**Blockers:** None
**Context for Next Agent:** Pure mechanical rename. Every change is `team1_ships` -> `team0_ships` and `team2_ships` -> `team1_ships`. No behavioral changes. Rename must be done in dependency order: engine first, then callers, then local variables, then tests.

## Overview
The battle simulator uses inconsistent 0-based and 1-based team naming. `BattleService` internally stores `_team0_ships` and `_team1_ships` (0-indexed, correct), but passes them to `BattleEngine.start(team1_ships=..., team2_ships=...)` where `team1_ships` receives team 0 and `team2_ships` receives team 1. This naming mismatch propagates through factories, screens, and test fixtures. The project standardizes all parameter names, local variables, and docstrings to use 0-based naming (`team0_ships`, `team1_ships`) throughout.

## Goals
- Eliminate the confusing `team1_ships` / `team2_ships` naming where the numbers don't match `team_id`
- Standardize on 0-based naming (`team0_ships`, `team1_ships`) matching the actual `team_id` values (0 and 1)
- Update all docstrings to remove the "team1 = team 0" clarifications that exist to explain the mismatch
- No runtime behavior changes -- purely a rename refactor

## Scope
**In Scope:**
- `BattleEngine.start()` parameter names, docstring, and internal references
- `BattleScreen.start()` parameter names, docstring, and internal references
- `BattleService._start_battle()` call site keyword arguments
- `create_manual_battle()` factory parameter names and docstring
- `App.start_battle()` parameter names and call to factory
- `SimulationAdapter.simulate_battle()` local variables
- `setup_screen.py` local variables and return tuple
- `battle_panels.py` local variables
- Test fixtures (`tests/fixtures/battle.py`) function signature, docstring, local variables
- Test file docstrings referencing old naming
- Module docstring example in `battle_engine.py`

**Out of Scope:**
- `BattleResult.team0_survivors` / `team1_survivors` -- already uses correct 0-based naming
- `BattleService._team0_ships` / `_team1_ships` -- already uses correct 0-based naming
- `battle_results_screen.py` -- already uses correct 0-based naming
- `battle_orchestrator.py` -- already uses correct 0-based naming
- Display labels ("TEAM 1" / "TEAM 2" in UI panels) -- user-facing 1-based display labels
- Any `team_id` integer values -- these stay as 0 and 1
- All `simulation_tests/` scenarios -- use `add_ships(team_id=)` pattern, no old naming
- `BattleService` test file internal attribute access (`service._team1_ships`) -- already correct 0-based

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| BattleEngine | `game/simulation/systems/battle_engine.py` | `BattleEngine.start()` |
| BattleService | `game/simulation/services/battle_service.py` | `BattleService._start_battle()` |
| BattleScreen | `game/ui/screens/battle_screen.py` | `BattleScreen.start()` |
| Battle factories | `game/ui/services/battle_factories.py` | `create_manual_battle()` |
| App entry point | `game/app.py` | `App.start_battle()` |
| SimulationAdapter | `game/strategy/adapters/simulation_adapter.py` | `SimulationAdapter.simulate_battle()` |
| Setup screen | `game/ui/screens/setup_screen.py` | `SetupScreen.get_ships()` |
| Battle panels | `game/ui/panels/battle_panels.py` | `BattleTeamPanel.draw()` |
| Test fixtures | `tests/fixtures/battle.py` | `create_battle_engine_with_ships()` |
| Battle screen tests | `tests/unit/ui/test_battle_screen_simulation.py` | docstring on line 90 |
| Integration tests | `tests/integration/fleet_combat/test_service_integration.py` | local variables lines 146-147 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-05 | Standardize on 0-based (`team0_ships`, `team1_ships`) | Matches the actual `team_id` values (0, 1). Eliminates the off-by-one confusion where `team1_ships` has `team_id=0`. |
| 2026-04-05 | Keep UI display labels as "TEAM 1" / "TEAM 2" | Display labels are user-facing and 1-based is natural for users. Only code identifiers change. |
| 2026-04-05 | Phase by dependency layer (engine -> callers -> locals -> tests) | Engine first so callers can be updated against the new API. Tests last since they follow the public API. |
| 2026-04-05 | Collapsed from 4 phases to 2 | Mechanical rename doesn't warrant 4 separate phases. Phase 1 = all production code, Phase 2 = test fixtures + verification. |
| 2026-04-05 | battle_panels.py local vars stay as `team0_ships`/`team1_ships` | Even though display says "TEAM 1", the variable filtering `team_id == 0` should be `team0_ships` for code clarity. |

## Initial Analysis

### Affected Code (80+ occurrences across 12 files)

**Function signatures (4 functions):**
1. `battle_engine.py:221-224` -- `start(team1_ships, team2_ships)`
2. `battle_screen.py:226` -- `start(team1_ships, team2_ships, ...)`
3. `app.py:511` -- `start_battle(team1_ships, team2_ships, ...)`
4. `battle_factories.py:80-82` -- `create_manual_battle(team1_ships, team2_ships, ...)`

**Call sites (1 keyword call):**
1. `battle_service.py:207-209` -- `engine.start(team1_ships=self._team0_ships, team2_ships=self._team1_ships)`

**Local variables (3 files):**
1. `battle_panels.py:121,134` -- `team1_ships = [s for s in ships if s.team_id == 0]`
2. `simulation_adapter.py:84-85,89-90,94,103,109,112,117,141-142` -- fleet conversion locals
3. `setup_screen.py:100-102` -- `team1_ships, team2_ships` load and return

**Test fixtures (1 file):**
1. `tests/fixtures/battle.py:62-63,74-75,85-86,97,100,112,115` -- function params, docstring, locals

**Tests to verify (docstring/local updates only):**
1. `tests/unit/ui/test_battle_screen_simulation.py:90` -- docstring says "team1" / "team2"
2. `tests/integration/fleet_combat/test_service_integration.py:143,146-147` -- param + local var names

### Already Correct (NO changes needed)
- `BattleService._team0_ships` / `_team1_ships` (internal attributes, already 0-based)
- `battle_orchestrator.py` (already 0-based)
- `battle_results_screen.py` (already 0-based)
- ALL `simulation_tests/` scenarios (use `add_ships(team_id=)` pattern)
- `test_battle_service.py` references to `service._team1_ships` (internal attribute, correct)

### Risk Assessment
- **Low risk:** Pure rename, no behavioral changes
- **Mechanical:** Every change is `team1_ships` -> `team0_ships`, `team2_ships` -> `team1_ships`
- **Test coverage:** Battle service and battle screen have dedicated test files
- **Simulation tests:** `simulation_tests/` does NOT use these parameter names

---

## Phases

### Phase 1: Rename All Production Code [Simple]
**Objective:** Rename all function signatures, call sites, and local variables in production code
**Status:** Not Started
**Checklist:** [phase_1_checklist.md](phase_1_checklist.md)

---

### Phase 2: Update Test Fixtures and Verify Full Suite [Simple]
**Objective:** Update test helper functions, docstrings, and verify everything passes
**Status:** Not Started
**Checklist:** [phase_2_checklist.md](phase_2_checklist.md)

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Run full test suite: `python scripts/test_sharded.py` -- establish baseline

### After Each Phase
- [ ] Run targeted tests for affected files
- [ ] No behavioral changes -- only names changed

### Final Verification
- [ ] `python scripts/test_sharded.py` -- all tests pass
- [ ] `grep -r "team2_ships" game/ tests/` returns zero results
- [ ] All `team1_ships` references now correctly map to `team_id == 1` (not `team_id == 0`)
- [ ] Docstrings are clean -- no "team1 means team 0" disclaimers remain
- [ ] No documentation updates needed (this is an internal naming change, not an architecture change)

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

---

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for parallel execution
