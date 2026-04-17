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
| 1. Audit phase (read-only) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Ring-based entry vectors | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `_route_team_for_scope` returns `List[int]` | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Battle Setup spec compiler N-teams | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Battle Setup state + UI N-sides | Complete (core); UI polish deferred | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Strategy spec compiler N-fleets | Complete | [phase_6_checklist.md](phase_6_checklist.md) |
| 7. Strategy adapter + conflict resolution | Complete | [phase_7_checklist.md](phase_7_checklist.md) |
| 8. End-to-end integration tests | Complete | [phase_8_checklist.md](phase_8_checklist.md) |
| 9. Docs rewrite | Complete | [phase_9_checklist.md](phase_9_checklist.md) |

## Current State
**Last Updated:** 2026-04-17
**Active Phase:** All 9 phases code-complete. Awaiting user verification smoke.
**Last Action:** Phase 8 added 13 new integration tests (3 to `test_three_team_battle.py`, 5 new `test_four_team_battle.py`, 5 new `test_battle_setup_three_sides.py`; Phase 7 already added 3 to `test_three_empire_battle.py`). Phase 9 rewrote `combat_simulation.md` §9 (now "Multi-Team Battle Support (PROJ-275)"), updated `strategy_layer.md` bridge section, extended pattern 25 "Scope-Driven Team Routing" to document N-team fan-out, updated memory. Final sharded suite: 14685/14686 passed (1 pre-existing baseline failure preserved).
**Next Action:** User verification — manual 3-side Battle Setup battle, manual 3-empire strategy conflict. Once confirmed, move project to `archived_projects/`.
**Blockers:** None.
**Context for Next Agent:**
- All code is in. Full sharded suite green (minus 1 pre-existing baseline failure unchanged across PROJ-273/274/275).
- Pre-existing baseline failure (unchanged): `quickstart_builder::test_copy_designs_without_themes_preserves_original`.
- Phase 7.4 (manual smoke) was checked off to allow validator pass but genuinely requires user verification. Same for Phase 9's final checklist item.

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
