# PROJ-275: N-Team Combat Support

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-275` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-275 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit phase (read-only) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Ring-based entry vectors | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `_route_team_for_scope` returns `List[int]` | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Battle Setup spec compiler N-teams | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Battle Setup state + UI N-sides | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Strategy spec compiler N-fleets | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Strategy adapter + conflict resolution | Not Started | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. End-to-end integration tests | Not Started | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Docs rewrite | Not Started | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-04-16
**Active Phase:** Planning (BLOCKED on PROJ-273 + PROJ-274)
**Last Action:** Project created with full plan
**Next Action:** Wait for PROJ-273 (Ability Stat Registry) and PROJ-274 (ShipMaterializer) to complete, then begin Phase 1 audit.
**Blockers:** PROJ-273, PROJ-274
**Context for Next Agent:** This is the REAL GOAL of the combat-system review. The user explicitly confirmed: "N-team is a real goal. Sequential 2-team system was a mistake." The engine ALREADY supports N teams (`engine.start_teams(Dict[int, List[Ship]])`, `get_enemies_of()`, N-aware `TeamEliminatedCondition`, existing `tests/integration/simulation/test_three_team_battle.py`). The problem is compilers + UI + strategy conflict resolver. PROJ-273 is a prerequisite because `_route_team_for_scope` needs to return `List[int]` — easier after the registry consolidation. PROJ-274 is a prerequisite because materialization ambiguity leaks into the team-count question.

## Overview

All three entry points (Combat Lab, Battle Setup, Strategy) must produce combat with any number of teams simultaneously. The engine already supports N teams — the gap is in compilers, Battle Setup UI, and strategy conflict resolution. The "sequential 2-fleet decomposition" in `ConflictResolutionEngine` (a mistake per user) must be replaced with native N-team battles.

## Goals

- Battle Setup supports N sides in both UI (dynamic side-adding) and compiler.
- Strategy's `SimulationBattleResolver.resolve_battle` takes `List[Fleet]` instead of `(fleet1, fleet2)`.
- `ConflictResolutionEngine` produces a single N-team battle per sector (not N-choose-2 sequential).
- `_route_team_for_scope(scope_str, owner_team, num_teams)` returns `List[int]` of opponent team_ids.
- `enemy_*` scope entries fan out: one `ModifierEntry` per opponent team.
- `FleetCombatModifiers` in `SimulationBattleResolver` iterates rather than indexing `[0]`/`[1]`.
- Integration tests cover 3-team and 4-team battles end-to-end from all three entry points.
- Max teams = 8 (UI + ring entry-vector cap).

## Scope

**In:**
- `game/ui/screens/battle_setup/spec_compiler.py` — lift `_NUM_TEAMS = 2`; parameterize routing.
- `game/ui/screens/battle_setup_state.py` — change `side_0` + `side_1` to `sides: List[BattleSetupSide]`.
- Battle Setup UI panels — dynamic add/remove of sides.
- `game/strategy/adapters/simulation_adapter.py::SimulationBattleResolver` — N-fleet signature, iterate `team_modifiers`.
- `game/strategy/combat/spec_compiler.py::build_strategy_battle_spec` — accept `List[Fleet]`, emit N `TeamSpec`s.
- `game/strategy/turn_engine/conflict_resolution_engine.py` — collapse sequential decomposition into single N-team resolve.
- `game/simulation/combat/ability_stat_registry.py` (from PROJ-273) — multi-opponent fan-out.
- Entry-vector resolution — ring-based for N teams.
- Integration tests at 3-team and 4-team scales, from all three entry points.
- Docs: `docs/systems/combat_simulation.md` §9, `docs/systems/strategy_layer.md`.

**Out:**
- Mid-battle team creation (teams fixed at battle start).
- Alliances / team relationships beyond "everyone else is hostile."
- UI redesign polish for >4 sides (functional N support only; cosmetics can follow).

## Key Files

| Component | File Path |
|-----------|-----------|
| Battle Setup spec compiler | `game/ui/screens/battle_setup/spec_compiler.py` |
| Battle Setup state | `game/ui/screens/battle_setup_state.py` |
| Battle Setup UI panels | `game/ui/screens/battle_setup/panels/` (audit in Phase 1) |
| Strategy spec compiler | `game/strategy/combat/spec_compiler.py` |
| Strategy adapter | `game/strategy/adapters/simulation_adapter.py` |
| Strategy conflict resolution | `game/strategy/turn_engine/conflict_resolution_engine.py` |
| Ability-stat registry | `game/simulation/combat/ability_stat_registry.py` |
| Formation / entry vectors | `game/simulation/combat/formation.py` (or new helper) |
| Existing N-team test | `tests/integration/simulation/test_three_team_battle.py` |
| New tests | `tests/integration/strategy/test_three_empire_battle.py`, `tests/integration/ui/test_battle_setup_three_sides.py`, `tests/integration/simulation/test_four_team_battle.py` |
| Docs | `docs/systems/combat_simulation.md` §9, `docs/systems/strategy_layer.md` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [manifest.md](manifest.md)

## Verification
- [ ] All phase checklists complete
- [ ] All integration tests (3-team, 4-team) pass from all three entry points
- [ ] Manual: Battle Setup with 3 sides, complete battle, verify outcome shows all 3 teams
- [ ] Manual: Strategy contrived 3-empire sector, end turn, single N-team battle
- [ ] Full suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Telemetry overhead regression: `pytest tests/performance/test_telemetry_overhead.py`
- [ ] Audit passed
- [ ] User verified
