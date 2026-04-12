# PROJ-269: Unified Battle Simulator Entry/Exit

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-269` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-269 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. DTO boundary + spec compilers | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Component HP persistence | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Boundary + N-team engine support | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Formation system | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Telemetry levels | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Delete legacy paths | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-12
**Active Phase:** Phase 3 Complete — Phase 4 Task 4.1 next
**Last Action:** Phase 1 complete. All 11 tasks checked off. `validate_phase.py PROJ-269 1` PASSED.

**Phase 1 deliverables shipped:**
- DTOs in simulation layer: `BattleSpec`, `BattleOutcome` + nested types + enums
- `BoundaryRegion` protocol + 3 concrete types (Rect/Circle/Unbounded) + `ExitPolicy`
- `ModifierStack` + `ModifierEntry` (source-tagged, wraps existing `ModifierEffect`)
- `FormationShape` enum + `FormationSpec` (resolver lands Phase 4)
- `TelemetryLevel` IntEnum (subscribers land Phase 5)
- `run_battle(spec, *, ai_factory, ship_builder, headless=True, per_tick_callback=None, pre_tick_loop_callback=None) -> BattleOutcome` engine entry
- 3 spec compilers:
  - `combat_lab/spec_compiler.py::build_test_battle_spec` (StaticTargetScenario supported in Phase 1)
  - `game/ui/screens/battle_setup/spec_compiler.py::build_manual_battle_spec`
  - `game/strategy/combat/spec_compiler.py::build_strategy_battle_spec`
- Combat Lab CLI runner wired behind `SB_USE_BATTLE_RUNNER=1` env flag (BEAMWEAPON-001 passes under both flag states)
- `docs/systems/combat_simulation.md` §0 "Unified Entry (in progress — PROJ-269)" added
- Full regression: **14576 passed** (+108 from baseline 14468); same 3 pre-existing unrelated failures + 3 pre-existing unrelated ImportErrors; combat_lab fast: 162 passed

**Next Action:** Phase 4 Task 4.1. Read `phase_4_checklist.md` for the first task. Phase 4 adds:
- `FormationResolver` — converts `(formation, entry_vector, boundary, ship_list, design_roles) → Dict[ship_instance_id, (position, angle)]`
- `TaskForce.formation: Optional[FormationSpec]` field
- Design-role-based formation defaults (Strike→WEDGE, Carrier→CARRIER_PROTECTED, Defender→LINE_ABREAST, Scout/Skirmisher→LINE_ASTERN, Mixed→LINE_ABREAST)
- Compilers invoke FormationResolver at spec-build time to produce ShipSpec poses
- Per-shape tests (rotation invariance, spacing, custom positions)

**Blockers:** None

**Phase 3 deliverables shipped:**
- `BattleEngine.boundary` per-tick enforcement via new `BoundaryEnforcementPhase` (priority 250). All four ExitPolicy values implemented (DESTROY kills, RETREAT removes + tracks, BOUNCE clamps + reflects, NONE no-op). `run_battle` threads `spec.boundary` to the engine.
- `BattleEngine.start_teams(teams: Dict[int, List[Ship]])` N-team entry. `start(team0, team1)` is now a thin backward-compat wrapper. `engine.teams` is a property, `get_ships_by_team`, `get_enemies_of(ship)` helpers added.
- `engine.get_winner()` returns sole alive team_id (or -1).
- `TeamEliminatedCondition` + `TeamIncapacitatedCondition` generalized to "≤1 team remaining" semantics — N-team correct, 2-team backward-compatible.
- `AIController._find_enemies_in_radius` filter: `obj.team_id != self.ship.get_team_id()`. Every non-self team is equally hostile.
- `extract_outcome` now emits `ShipStatus.RETREATED` for ships that exited with the RETREAT policy; tracked via `engine.retreated_ships`.
- Integration tests: `test_three_team_battle.py` (N-team structural), `test_boundary_retreat.py` (RETREAT end-to-end), plus 26 unit tests across boundary / ExitPolicy / N-team / end conditions.
- `docs/systems/combat_simulation.md` §0 updated with "Boundary Region (Phase 3)" + "N-Team Support (Phase 3)" subsections.

**Baselines going into Phase 4:** pytest **14635 passed** (up from post-Phase-2 14603; +32 new Phase-3 tests). combat_lab fast **162 passed** (maintained throughout).

**Phase 2 deliverables shipped:**
- `ComponentState` dataclass in `game/strategy/data/component_state.py` (note: `data/` not `fleets/` — manifest path diverged; decisions.md logged)
- `ShipInstance.components: Dict[str, ComponentState]` field; populate-on-create via `_build_full_hp_components_from_design`; serialization + clone propagation; graceful degradation for legacy saves
- `ShipInstanceBridge.to_ship` applies per-instance HP from `components`; falls back to legacy `component_damage` when `components` empty
- `ShipInstanceBridge.update_from_ship` authoritatively rebuilds `components` from post-battle Ship layers
- `build_strategy_battle_spec` populates `ShipSpec.components` from `ShipInstance.components`
- `run_battle` applies `ShipSpec.components` via `_apply_spec_components_to_ship`; `extract_outcome` reads per-component HP via `_extract_component_states`
- `apply_outcome_to_fleets` in new `game/strategy/combat/post_battle_hook.py` (surviving → update, destroyed/retreated → remove from fleet, empty fleet → remove from empire)
- `build_strategy_battle_spec` attaches the real hook by default (Phase 1's `_noop_hook` replaced)
- End-to-end `tests/integration/strategy/combat/test_damage_persistence.py` — 2 consecutive battles, damage persists + accumulates
- `docs/systems/combat_simulation.md` §0 "Component HP Persistence (Phase 2)" + `docs/systems/strategy_layer.md` ShipInstance component persistence subsection

**Baselines going into Phase 3:** pytest **14603 passed** (up from post-Phase-1 14576; +27 new Phase-2 tests). combat_lab fast **162 passed**.

**Context for Next Agent (Phase 4):**
- **`FormationSpec` + `FormationShape` enum already exist** in `game/simulation/combat/formation.py` from Phase 1 Task 1.4. Phase 4 adds the resolver that turns a formation into actual per-ship poses.
- **`TaskForceSpec.formation` field exists** but is always `None` in today's compilers — the Phase 1 scaffold. Phase 4 populates it + consumes it.
- **Design-role defaults** (per `decisions.md`): Strike→WEDGE, Carrier→CARRIER_PROTECTED, Defender→LINE_ABREAST, Scout/Skirmisher→LINE_ASTERN, Mixed→LINE_ABREAST. Dominant design_role logic required.
- **Entry vectors** are already on `TeamSpec.entry_vector` (Phase 1); Phase 4 is where the resolver consumes `entry_vector.origin + facing` to rotate formation-local positions into world-space.
- **Strategy compiler's hex-edge entry** lands in Phase 4 too (today it uses hex center as origin, arbitrary facing).
- **Pre-existing pytest failures/errors** (3 build-queue + 3 AI/strategy imports) still unchanged — not PROJ-269's responsibility.
- **Transitional concerns still open:**
  - `ship_builder` kwarg on `run_battle` — Phase 6 subsumes.
  - DTO annotations still use `object` for `FormationSpec` on `TaskForceSpec.formation` — can tighten as part of Phase 4.
  - Legacy `ShipInstance.component_damage` coexists with `components`.
  - Empty TaskForce / Squadron pruning still NOT done. Phase 4 is the natural spot if it becomes relevant.

## Overview

The battle simulator is currently entered via three different, incompatible paths: **Combat Lab** (4 paths, most bypassing the unified controller entirely), **Battle Setup** (clean path, one side-channel issue), and **Strategy combat** (half-factory + adapter-applied side-channel mutations). This project unifies all three around a single **`BattleSpec` → engine → `BattleOutcome`** contract, fills architectural gaps (formation system, boundary region, N-team support, component-HP persistence, graduated telemetry), and deletes the legacy `BattleMode`/`BattleModeHandler` switch along with all half-factories.

After this project, every battle — Combat Lab scenario, UI-configured manual battle, or strategy-layer fleet clash — builds a `BattleSpec` via its own context-specific compiler, hands it to one engine entry, and consumes the resulting `BattleOutcome` for its own purposes. The engine is context-blind.

## Goals

- **Single entry contract**: every battle enters via `run_battle(spec: BattleSpec) -> BattleOutcome`. No half-factories, no direct-engine construction, no state-flag hacks.
- **Fully specified initial conditions**: `BattleSpec` carries boundary, end condition, modifier stack, telemetry level, per-team fleet hierarchy with policies, per-ship pose + per-component HP, entry vectors, formations.
- **Fully specified final conditions**: `BattleOutcome` carries per-ship final pose, per-component HP, fleet hierarchy (survival-annotated), weapon totals, hit log, damage/speed stats, and end-reason.
- **Component-level damage persisted** between battles via `ShipInstance.components: Dict[component_id, ComponentState]`.
- **Formation system** authored per TaskForce with design_role-based defaults; resolved at battle start via `entry_vector + boundary + formation → per-ship poses`.
- **N teams** with explicit entry vectors, no alliance concept (everyone vs. everyone, no target preference).
- **Graduated telemetry**: MINIMAL (near-zero overhead for batch runs) / NORMAL (per-ship totals) / DETAILED (full hit log for Combat Lab forensics).
- **Boundary as first-class**: `BoundaryRegion` (shape, size, exit-policy) passed in; `None` = unbounded; retreat = boundary exit with retreat policy.
- **Kill the mode switch**: `BattleMode` enum and `BattleModeHandler` hierarchy replaced by explicit fields on `BattleSpec`. Variance moves from a switch to named fields.

## Scope

**In scope:**
- `BattleSpec` and `BattleOutcome` DTOs, frozen dataclasses, layered cleanly in `game/simulation/`.
- Three spec compilers: `combat_lab/spec_compiler.py`, `game/ui/screens/battle_setup/spec_compiler.py`, `game/strategy/combat/spec_compiler.py`.
- `ShipInstance.components` persistence at strategic layer; round-trip through battles.
- `BoundaryRegion` abstract + `RectBoundary`, `CircleBoundary`, `UnboundedRegion` concrete types; engine enforcement with configurable exit policies.
- N-team engine support: `BattleSpec.teams: List[TeamSpec]`; end conditions generalized; AI targeting generalized.
- `FormationSpec` + `FormationResolver`; `TaskForce.formation` field.
- `TelemetryLevel` enum + opt-in `CombatEventBus` subscribers; richer fields on `BattleOutcome`.
- Delete `BattleMode`, `BattleModeHandler`, all `create_*_battle` half-factories, `SimulationBattleResolver` ship-mutation side channels, Combat Lab direct-engine construction.
- Update `docs/systems/combat_simulation.md` and any affected patterns docs.

**Out of scope:**
- **Repair mechanic** — component HP is persisted and can accumulate damage across battles; healing is a separate future project.
- **Alliance system** — teams are independent; "non-aggression pact" between teams is a separate future project (today: everyone vs. everyone).
- **Formation authoring UI** — the data model, resolver, and defaults land in this project; the UI for player-authored formations is a separate UI project.
- **Save format migration** — per CLAUDE.md, old saves are discarded; no migration code for existing save files.
- **Multi-sector / extended-combat features** — the engine remains single-region.
- **Combat physics changes** — ship movement, damage, weapons stay as-is; only entry/exit/boundary/telemetry/N-team change.

## Key Files

### New files (created in this project)

| Component | File Path |
|-----------|-----------|
| BattleSpec DTO | `game/simulation/battle_spec.py` |
| BattleOutcome DTO | `game/simulation/battle_outcome.py` |
| TeamSpec + related DTOs | (in `battle_spec.py`) |
| BoundaryRegion types | `game/simulation/combat/boundary.py` |
| FormationSpec + Resolver | `game/simulation/combat/formation.py` |
| TelemetryLevel + subscribers | `game/simulation/combat/telemetry.py` |
| Engine entry point | `game/simulation/battle_runner.py` |
| Strategy spec compiler | `game/strategy/combat/spec_compiler.py` |
| Battle Setup spec compiler | `game/ui/screens/battle_setup/spec_compiler.py` |
| Combat Lab spec compiler | `combat_lab/spec_compiler.py` |

### Files heavily modified

| Component | File Path | Change |
|-----------|-----------|--------|
| BattleController | `game/simulation/battle_controller.py` | Consume `BattleSpec` internally; drop `BattleConfig` variant fields |
| BattleEngine | `game/simulation/systems/battle_engine.py` | Accept `BoundaryRegion`, N teams, `TelemetryLevel` |
| BattleService | `game/simulation/services/battle_service.py` | Pass-through updates |
| ShipInstance | `game/strategy/fleets/ship_instance.py` | Add `components: Dict[str, ComponentState]` with HP persistence |
| SimulationBattleResolver | `game/strategy/combat/simulation_battle_resolver.py` | Use spec compiler; drop ship mutations |
| ConflictResolutionEngine | `game/strategy/engine/conflict_resolution_engine.py` | Call new entry; consume outcome |
| Battle Setup screen | `game/ui/screens/battle_setup_screen.py` | Build spec via compiler; drop in-place modifier mutation |
| Combat Lab runner | `combat_lab/runner.py` | Go through engine entry; no raw BattleEngine |
| Combat Lab templates | `combat_lab/scenarios/templates.py` | `_run_baseline_battle` uses engine entry |
| Test executor | `game/ui/screens/test_lab/test_executor.py` | All paths go through engine entry |
| Test execution service | `combat_lab/services/test_execution_service.py` | Drop `_is_started` hack |
| Battle factories | `game/ui/services/battle_factories.py` | Reduce to single entry or delete |

### Files deleted

| Component | File Path |
|-----------|-----------|
| BattleModeHandler classes | `game/simulation/combat/battle_mode_handler.py` |
| Per-mode factory functions | `game/ui/services/battle_factories.py::create_*_battle` |
| BattleMode enum | inside `game/simulation/battle_config.py` (enum removed; struct reshaped or deleted) |

## Related Documents

- [design.md](design.md) — Architecture, DTO schemas, migration strategy, layer contracts
- [decisions.md](decisions.md) — Full decisions log (all locked design choices)
- Phase checklists: [1](phase_1_checklist.md) · [2](phase_2_checklist.md) · [3](phase_3_checklist.md) · [4](phase_4_checklist.md) · [5](phase_5_checklist.md) · [6](phase_6_checklist.md)
- [manifest.md](manifest.md) — File inventory for parallel execution tracking

## Verification

**Project start (baseline):**
- [ ] Full pytest suite green: `pytest tests/` (record baseline count in Current State)
- [ ] Combat Lab fast suite green: `python -m combat_lab.run_tests --fast` (record pass count)
- [ ] Manual smoke: `python launcher.py` — open Combat Lab, run one scenario visually + headless; start Battle Setup, run a manual battle; start a strategy game, trigger one fleet conflict.

**Per-phase:**
- [ ] Phase 1 complete — all tasks checked; `pytest tests/ --testmon` green; smoke-test all three entry paths.
- [ ] Phase 2 complete — ship damage persists across two consecutive strategy battles.
- [ ] Phase 3 complete — 3-team battle resolves correctly; boundary retreat policy removes ships; unbounded region works.
- [ ] Phase 4 complete — each formation produces expected ship positions given an entry vector; defaults chosen by design_role.
- [ ] Phase 5 complete — MINIMAL run produces empty telemetry; DETAILED run produces hit log; per-level performance measured.
- [ ] Phase 6 complete — no file imports `BattleMode` or `BattleModeHandler`; no direct `BattleEngine(...)` instantiation outside `battle_runner.py`; docs updated.

**Final verification:**
- [ ] `pytest tests/` — full suite green, baseline maintained or increased.
- [ ] Combat Lab fast suite — 162+ passing scenarios.
- [ ] End-to-end manual test: Combat Lab visual + headless + run-all; Battle Setup with modifiers; strategy game fleet conflict with damage persisting to next turn.
- [ ] No occurrences of `BattleMode` / `BattleModeHandler` / `create_manual_battle` / `create_test_battle` / `create_strategy_battle` / `create_hypothetical_battle` in the codebase (excluding archived projects).
- [ ] `docs/systems/combat_simulation.md` rewritten to describe the unified flow; `docs/02_PATTERNS.md` updated if patterns changed.
- [ ] Audit passed
- [ ] User verified
