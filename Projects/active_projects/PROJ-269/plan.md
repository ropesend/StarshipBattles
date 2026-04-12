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
| 1. DTO boundary + spec compilers | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Component HP persistence | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Boundary + N-team engine support | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Formation system | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Telemetry levels | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Delete legacy paths | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-12
**Active Phase:** Planning complete — awaiting user approval to begin Phase 1
**Last Action:** Project plan authored following architectural review + user-answered design questions
**Next Action:** User reviews plan / design / decisions / phase checklists. On approval, begin Phase 1 Task 1.1.
**Blockers:** None
**Context for Next Agent:** All seven architectural decisions are locked in [decisions.md](decisions.md). The design is sketched in [design.md](design.md). Each phase has a detailed checklist. Start by reading `docs/systems/combat_simulation.md` to understand the current state of the simulator, then `design.md` for the target state.

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
