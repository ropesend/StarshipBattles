# PROJ-259: Infrastructure - Screen State Machine, TurnEngine Config, Battle Engine Phases

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-259` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-259 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Screen State Machine | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. TurnEngine Config Object | Complete (abstraction + integration) | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Battle Engine Tick Phases | Complete (abstraction + integration) | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Documentation + Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-08
**Last Updated:** 2026-04-08
**Active Phase:** Phases 2-3 complete, Phase 1 partially complete (app.py refactor pending), Phase 4 (docs) pending
**Last Action:** All 3 new abstractions implemented with full TDD:
  - ScreenStateMachine (game/core/state_machine.py, 19 tests) — transition table, guards, callbacks, push/pop stack
  - TurnEngineConfig (game/strategy/engine/turn_engine_config.py, 6 tests) — frozen dataclass with 13 Optional fields
  - ITickPhase + TickPhaseRegistry (game/simulation/systems/tick_phase.py, 9 tests) — protocol + priority-sorted registry
  14675 tests pass.
**Next Action:** Phase 1 Tasks 1.3-1.4 (app.py refactor with ScreenStateMachine), then Phase 4 (docs)
**Blockers:** None
**Context for Next Agent:** TurnEngine and BattleEngine integrations are DONE. Remaining work:
  - Phase 1 Tasks 1.3-1.4: app.py refactor — replace 23 _switch_scene() calls + 3 return_state fields with ScreenStateMachine. Read design.md for the full transition map.
  - Phase 4: Documentation updates for all three new abstractions.
  - Task 2.4-2.5 (TurnEngine call site migration) deferred — backward compat kwargs still work.

## Overview
This project introduces three infrastructure improvements that formalize existing patterns into explicit, testable abstractions: (1) a screen state machine with a transition table and guards to replace 23 bare `_switch_scene()` calls in `game/app.py`, (2) a `TurnEngineConfig` dataclass to bundle the 15 optional engine parameters of `TurnEngine.__init__()`, and (3) an `ITickPhase` protocol with a phase registry to replace the hardcoded tick loop in `BattleEngine.update()`. None of these fix bugs -- they improve code clarity, testability, and extensibility.

## Goals
- Formalize screen transitions with an explicit transition table, transition guards, and a state stack for return-to-previous behavior
- Reduce `TurnEngine.__init__()` from 20 parameters to 4 (battle_resolver, registries, config, event_bus) by bundling optional engines into a dataclass
- Make `BattleEngine.update()` tick phases pluggable via an `ITickPhase` protocol and ordered registry, preserving the current 5-phase sequence as the default

## Scope
**In Scope:**
- New file `game/core/state_machine.py` -- generic `ScreenStateMachine` with transition table, guards, state stack
- Refactor `game/app.py` -- replace `_switch_scene()` calls with state machine API, remove `self.state` and `self.return_state`
- New file `game/strategy/engine/turn_engine_config.py` -- `TurnEngineConfig` frozen dataclass
- Refactor `game/strategy/engine/turn_engine.py` -- accept `TurnEngineConfig` instead of 15 individual engine kwargs
- New file `game/simulation/systems/tick_phase.py` -- `ITickPhase` protocol, `TickPhaseRegistry`, default phase implementations
- Refactor `game/simulation/systems/battle_engine.py` -- delegate `update()` body to `TickPhaseRegistry`
- Tests for all new abstractions
- Documentation updates to `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/systems/strategy_layer.md`, `docs/systems/combat_simulation.md`

**Out of Scope:**
- Adding new screen transitions or game states
- Changing TurnEngine's phase execution order or adding new strategy phases
- Changing BattleEngine's tick sequence behavior
- Any gameplay behavior changes
- PROJ-258 work (ApplicationContext) -- this project depends on it but does not implement it

## Key Files Reference
| Component | File Path | What Changes |
|-----------|-----------|--------------|
| GameState enum | `game/core/constants.py:26-37` | Referenced, not modified |
| IScene protocol | `game/core/protocols.py:820-841` | Referenced, not modified |
| App entry point | `game/app.py` (774 lines) | Major refactor: replace 23 `_switch_scene()` calls |
| State machine (NEW) | `game/core/state_machine.py` | New file: ScreenStateMachine class |
| TurnEngine | `game/strategy/engine/turn_engine.py` (676 lines) | Refactor constructor to accept TurnEngineConfig |
| TurnEngineConfig (NEW) | `game/strategy/engine/turn_engine_config.py` | New file: frozen dataclass |
| Strategy engine interfaces | `game/strategy/interfaces/engines.py` | Referenced, not modified |
| BattleEngine | `game/simulation/systems/battle_engine.py` (570 lines) | Refactor update() to use TickPhaseRegistry |
| Tick phase (NEW) | `game/simulation/systems/tick_phase.py` | New file: ITickPhase protocol + registry |
| Battle end conditions | `game/simulation/systems/battle_end_conditions.py` | Pattern reference (IEndCondition) |
| TurnEngine DI tests | `tests/unit/strategy/turn_engine/test_dependency_injection.py` | Update for new config interface |
| TurnEngine conftest | `tests/unit/strategy/turn_engine/conftest.py` | Update fixtures for TurnEngineConfig |
| BattleEngine tick tests | `tests/unit/simulation/systems/test_battle_engine_tick.py` | Update for tick phase registry |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | State machine lives in `game/core/` | It is a generic infrastructure pattern with no UI dependencies. App.py (UI layer) uses it, but the class itself is layer-independent. |
| 2026-04-08 | TurnEngineConfig is a frozen dataclass, not a mutable config | Immutability prevents mid-turn config changes. Matches existing pattern (GameRegistries is also a frozen container). |
| 2026-04-08 | ITickPhase follows the IEndCondition protocol pattern | IEndCondition in `battle_end_conditions.py` is the closest existing pattern: protocol-based, composable, with a registry. |
| 2026-04-08 | Phases 1-3 are independent | Each sub-project touches different files. No cross-dependencies between the three refactors. |
| 2026-04-08 | Depends on PROJ-258 | ApplicationContext from PROJ-258 is needed for injecting services into the state machine guards and TurnEngineConfig construction. |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - Complete file manifest for conflict detection

## Verification
- [ ] All phase checklists complete
- [ ] All 14783+ tests passing (no regressions)
- [ ] `_switch_scene()` method removed from app.py (replaced by state machine)
- [ ] TurnEngine constructor has 4 parameters (battle_resolver, registries, config, event_bus)
- [ ] BattleEngine.update() delegates to TickPhaseRegistry
- [ ] Documentation updated
- [ ] Audit passed
- [ ] User verified
