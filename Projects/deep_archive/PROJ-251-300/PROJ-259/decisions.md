# PROJ-259: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-08 | Project initialized | Starting point for Infrastructure - Screen State Machine, TurnEngine Config, Battle Engine Phases |
| 2026-04-08 | ScreenStateMachine in `game/core/state_machine.py` | Generic infrastructure with no UI dependencies. Uses GameState from `game/core/constants.py`. Same layer as SingletonMeta, ValidationResult. |
| 2026-04-08 | Transition table as `frozenset[tuple[GameState, GameState]]` | Immutable set of allowed (from, to) pairs. Simple to declare, validate, and test. No need for a heavier graph structure. |
| 2026-04-08 | State stack for return-to-previous | Replaces three ad-hoc fields (`builder_return_state`, `_keybindings_return_state`, `return_state`) with a single generic stack. push_and_transition() on entry, pop_and_return() on exit. |
| 2026-04-08 | Guards are optional per-transition callables | Not all transitions need guards. Guards are `(from_state, to_state) -> bool` predicates. Keeps the common case simple (just a transition table) while supporting conditional transitions. |
| 2026-04-08 | on_enter/on_exit hooks keyed by state | Allows cleanup/setup logic per state (e.g., builder cleanup on exit). Optional -- most states won't need them initially. |
| 2026-04-08 | StateException on illegal transitions | Fail-fast on programmer error. An illegal transition is always a bug, never a runtime condition to handle gracefully. Uses existing `StateException` from `game/core/exceptions.py`. |
| 2026-04-08 | TurnEngineConfig is `@dataclass(frozen=True)` | Immutability prevents mid-turn config changes. Matches GameRegistries pattern. |
| 2026-04-08 | All TurnEngineConfig fields default to None | None means "use default implementation" (lazy init). Same semantics as current individual kwargs. No behavior change. |
| 2026-04-08 | Keep `create_default_turn_engine()` factory | Factory still useful as a convenience for production code. Updated to accept optional TurnEngineConfig. |
| 2026-04-08 | ITickPhase protocol with priority ordering | Phases execute in priority order (lower first). Spacing of 100 between defaults allows custom phases to be inserted without renumbering. |
| 2026-04-08 | Phase classes are thin wrappers calling existing private methods | Existing `_rebuild_grid()`, `_update_ai_and_ships()`, etc. stay on BattleEngine as implementation. Phase classes delegate to them. Zero behavior change. |
| 2026-04-08 | TickPhaseRegistry sorts on insert | Maintains sorted order. `execute_all()` iterates without re-sorting. Simple and efficient for the small number of phases (5 default). |
| 2026-04-08 | Depends on PROJ-258 completion | ApplicationContext from PROJ-258 provides the DI container needed for injecting services into state machine guards and for constructing TurnEngineConfig in production code. |
| 2026-04-08 | Three phases are independent, executed sequentially | Phases 1-3 touch different files (app.py, turn_engine.py, battle_engine.py). No cross-dependencies. Sequential execution is safer for a single agent. |
