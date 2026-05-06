# PROJ-369: Design — Strategy TurnEngine Decomposition Completion

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Why this project exists

The strategy-layer tech-debt review (`AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md`, target #2) called `TurnEngine` an "802-LOC de-facto god class" with "Constructor DI for 13+ engines, but property fallback initialization defeats DI purpose." It is the second-highest-impact maintainability target in the strategy layer.

PROJ-259 (2026-04-08) introduced `TurnEngineConfig` (a 16-field frozen dataclass) and `ITickPhase` (a battle-engine-side protocol). PROJ-365 (2026-05-04) replaced the 100-tick imperative body with a `DEFAULT_TICK_PHASE_LIST` descriptor iteration. **What remains** is exactly what the review report flags:

1. **Lazy fallback init defeats DI.** Each of the 15 properties at `turn_engine.py:319-481` does `if self._foo_engine is None: self._foo_engine = FooEngine(...)`. The 13 ctor kwargs are honored, but if a caller forgets to wire one through, the property silently substitutes a default — and the default is constructed with whatever happens to be on `self` at that moment. Tests can't distinguish "explicitly defaulted" from "forgotten."
2. **End-of-turn block is still imperative.** `turn_engine.py:587-620` calls 6 engine methods inline through `_time_phase`. Three of those engines (`QualityEngine`, `AtmosphereEngine`, `WaterEngine`) are constructed by `from … import …` statements that live INSIDE the `process_turn` body — they cannot be injected, mocked at the class boundary, or swapped without `unittest.mock.patch` of source modules.
3. **`_NullBattleResolver`** (`turn_engine.py:109-122`) exists solely as an "are you sure?" warning path — both branches that would create one (no `ai_factory`, no `battle_resolver`) are caller mistakes, and the engine raises at use time anyway. It's a band-aid over the absence of fail-fast injection.
4. **Constructor has 20 kwargs**, ~150 chars wide, ~73 lines tall. Adding the 16th sub-engine (e.g. a future `ResearchEngine`) currently requires edits in 6 places: ctor signature, `cfg.foo = …`, field declaration, `@property foo_engine`, lazy-create body, and the end-of-turn or per-tick wire-up. Easy to miss one.

### Quantified survey of `turn_engine.py`

| Concern | Count | Reference |
|---|---|---|
| Sub-engine ctor kwargs | 13 (+ 2 non-engine: `battle_resolver`, `ai_factory`; + 3 misc: `registries`, `race_registry`, `event_bus`; + 1: `tick_phases`) = **20 total** | `turn_engine.py:144-169` |
| Lazy `@property` engines | **15** | lines 319, 327, 336, 344, 371, 380, 390, 398, 406, 418, 426, 434, 447, 455, 468 |
| Sub-engines NOT injectable today | **3** (`QualityEngine`, `AtmosphereEngine`, `WaterEngine`) | `turn_engine.py:607, 612, 617` (function-local imports) |
| `if self._foo is None:` fallback bodies | **13** in lazy properties + **1** in `conflict_engine` (battle_resolver decision tree) = **14** | properties listed above |
| Function-local imports inside `TurnEngine` methods | **18** (every lazy property + 3 in process_turn end-of-turn) | grep `from game.strategy.engine.\w+ import` |
| `_NullBattleResolver` usages | 1 internal (line 360), 1 production-test reference | `turn_engine.py:360`, `test_turn_engine_lazy_properties.py:297` |
| Tick-loop phase descriptors | **15** | `turn_phase_registry.py:174-297` |
| End-of-turn imperative phase calls | **6** (organics_consumption, happiness, population_growth, quality_improvement, atmosphere, water_modification) | `turn_engine.py:589, 597, 602, 609, 612, 618` |
| `_phase_times` bucket keys | **21** (15 tick + 6 end-of-turn) | `turn_engine.py:243-259` |
| Production call sites of `TurnEngine(...)` | **2** | `game_session.py:102, 386` |
| Production call sites of `create_default_turn_engine` | **0** (factory exists at line 763 but no production caller; only tests use it) | grep |
| Test files constructing `TurnEngine(...)` directly | **17** (mostly `tests/unit/strategy/turn_engine/`) | grep |
| Test fixture: shared `turn_engine` | 1 (`conftest.py:24-26`) | `tests/unit/strategy/turn_engine/conftest.py` |

### The phase table

The per-tick descriptor list (`DEFAULT_TICK_PHASE_LIST`, 15 entries) already exists. PROJ-369 adds the missing 6 — call them **end-of-turn descriptors**:

| # | phase_key | Engine | Method | Args | Injectable today? |
|---|---|---|---|---|---|
| 16 | organics_consumption | OrganicsConsumptionEngine | process_consumption | empires | YES |
| 17 | happiness | HappinessEngine | process_happiness | empires, galaxy | YES |
| 18 | population_growth | PopulationEngine | process_population_growth | empires | YES |
| 19 | quality_improvement | QualityEngine | process_quality_improvement | empires | **NO** — function-local import |
| 20 | atmosphere | AtmosphereEngine | process_atmosphere | empires | **NO** — function-local import |
| 21 | water_modification | WaterEngine | process_water_modification | empires | **NO** — function-local import |

PROJ-365 explicitly excluded these from the descriptor migration; PROJ-369 includes them.

### Cross-references against `docs/`

- `docs/systems/strategy_layer.md:280` mentions `create_default_turn_engine(registries)` as the standard initialization. PROJ-369 redirects this to `TurnEngineConfig.create_default(registries, ai_factory=…)` (the factory function survives as a thin shim or is deleted — phase task decision).
- `docs/02_PATTERNS.md:1331` mentions `TurnEngineConfig` as a "pass to `TurnEngine()` or `create_default_turn_engine()`" pattern. PROJ-369 elevates `TurnEngineConfig.create_default()` to the canonical entry point.
- `docs/03_CONVENTIONS.md §8` requires modern type annotations; PROJ-369 will use `Optional[X]`-free syntax (`X | None`) on the new code paths and migrate touched lines.
- `docs/03_CONVENTIONS.md §9` requires `> **Last verified:**` blockquote — Phase 5 updates touched docs.

## Current vs target architecture

### Current (post-PROJ-365)

```
                                                                    ┌─────────────────┐
                                                                    │ GameSession     │
                                                                    │  TurnEngine(    │
                                                                    │    registries=, │
                                                                    │    ai_factory=, │
                                                                    │    event_bus=,  │
                                                                    │    race_reg.=)  │
                                                                    └────────┬────────┘
                                                                             │
                                            ┌────────────────────────────────▼──────────────────────────────┐
                                            │  TurnEngine                                                    │
                                            │   __init__(20 kwargs)                                          │
                                            │     self._foo_engine = foo_engine or cfg.foo_engine  (15x)     │
                                            │                                                                │
                                            │   @property foo_engine:                                        │
                                            │     if self._foo_engine is None:                               │
                                            │       from … import FooEngine                                  │
                                            │       self._foo_engine = FooEngine(registries=…)               │
                                            │     return self._foo_engine                                    │
                                            │   ... 14 more properties just like this                        │
                                            │                                                                │
                                            │   process_turn():                                              │
                                            │     for tick in range(100):                                    │
                                            │       _process_tick(tick)  ──► descriptor iteration (PROJ-365) │
                                            │     _time_phase('organics_consumption', …)  IMPERATIVE         │
                                            │     _time_phase('happiness',           …)  IMPERATIVE         │
                                            │     _time_phase('population_growth',   …)  IMPERATIVE         │
                                            │     QualityEngine(reg=…).process_quality_…() IMPERATIVE+LOCAL  │
                                            │     AtmosphereEngine(reg=…).process_atm…()  IMPERATIVE+LOCAL  │
                                            │     WaterEngine(reg=…).process_water_mod…() IMPERATIVE+LOCAL  │
                                            └─────────────────────────────────────────────────────────────────┘
```

### Target (post-PROJ-369)

```
┌─────────────────┐         ┌──────────────────────────────────────────┐
│ GameSession     │         │ TurnEngineConfig                          │
│  cfg = TurnEng. │────────▶│  @classmethod                             │
│  Config.create_ │         │  create_default(registries, *, ai_factory,│
│  default(...)   │         │      race_registry, event_bus)            │
│  TurnEngine(    │         │                                           │
│    registries=, │         │  Eagerly constructs all 18 engines.       │
│    config=cfg,  │         │  Single site for "what is the default"    │
│    ai_factory=) │         │                                           │
└────────┬────────┘         └──────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│  TurnEngine                                                                   │
│   __init__(*, registries, config, ai_factory=None, race_registry=None,        │
│            event_bus=None, battle_resolver=None,                              │
│            tick_phases=None, end_of_turn_phases=None)        # 8 kwargs       │
│                                                                               │
│     self._<foo>_engine = config.<foo>_engine    # 18 trivial assignments      │
│     self._tick_phases       = tick_phases       or DEFAULT_TICK_PHASE_LIST    │
│     self._end_of_turn_phases= end_of_turn_phases or DEFAULT_END_OF_TURN_PHASE_LIST│
│                                                                               │
│   @property foo_engine: return self._foo_engine    # trivial passthroughs     │
│                                                                               │
│   process_turn():                                                             │
│     for tick in range(1, 101):                                                │
│       self._run_phases(self._tick_phases, TickContext(tick=tick, …))          │
│     self._run_phases(self._end_of_turn_phases, TickContext(tick=0, …))        │
│                                                                               │
│   _run_phases(phases, ctx):                                                   │
│     for phase in phases:                                                      │
│       if phase.pre_exec_hook: phase.pre_exec_hook(self, ctx)                  │
│       result = self._time_phase(phase.timing_bucket or phase.phase_key,       │
│                                  phase.callable_target(self),                 │
│                                  *phase.args_resolver(ctx)[0],                │
│                                  **phase.args_resolver(ctx)[1])               │
│       if phase.post_exec_hook: phase.post_exec_hook(self, ctx, result)        │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Alternatives considered

### A. Keep monolith, just rename
**Rejected.** Doesn't address the review report's #2 finding. Lazy fallback init still defeats DI; testing burden unchanged; the constructor stays 20 wide.

### B. Partial migration — clean up lazy init, leave end-of-turn imperative
**Rejected.** Leaves the 3 non-injectable engines (Quality/Atmosphere/Water) as second-class citizens. Anyone adding a fourth (e.g. a future `TerraformingEngine`) hits the same trap: easier to write `from … import` inline than to thread DI properly. Fixing the symptom without the pattern just re-creates the problem.

### C. Full descriptor migration + required-kwarg DI (chosen)
**Chosen.** This is the canonical PROJ-365 pattern extended to the full turn body. Every engine is constructed in exactly one place (`TurnEngineConfig.create_default()`); every phase invocation is a descriptor; the constructor goes from 20 to 8 kwargs. AST guards prevent regression.

### D. Replace `TurnEngine` entirely with `TurnPhaseExecutor` + state-bag class
**Rejected.** Bigger blast radius than the review recommends. PROJ-365 already proved descriptor iteration is the right shape; we just need to finish that work, not redesign on top of it. Discussed and discarded — the sibling project PROJ-368 has higher value with the saved effort.

### E. Move construction into `ApplicationContext`
**Rejected.** `ApplicationContext` (game/context.py) is a process-level singleton container for 10 services (registry_manager, profiler, asset_manager, etc.). Strategy turn engines are session-scoped (one per `GameSession`), so they don't belong in the global context. `TurnEngineConfig.create_default(registries)` is the right scope: it accepts the session's registries and produces a one-shot config. PROJ-369 keeps `ApplicationContext` untouched.

## Risks

### Phase-ordering correctness (HIGH — mitigated)
The 6 end-of-turn phases have strict ordering invariants documented in PROJ-284 (`OrganicsConsumptionEngine` writes `last_food_ratio` → `HappinessEngine` reads it → `PopulationEngine` reads happiness). Reordering = silent gameplay regression.
**Mitigation:** golden-list test in Phase 1 (mirroring `test_default_tick_phase_list.py`) pins the order. AST guard in Phase 5 ensures `process_turn` body matches the descriptor list, not an alternate inline order.

### Save/load compatibility (LOW)
TurnEngine state is ephemeral (no `to_dict`/`from_dict`). Construction-time changes don't touch save format. `GameSession.from_dict` reconstructs the engine via the Phase 3-updated path.
**Mitigation:** Phase 3 explicitly migrates `game_session.py:386` (the `from_dict` site) alongside `:102` (the `__init__` site). Verified by existing `test_game_session_strategy.py` integration tests.

### Performance overhead (LOW)
Adding a `_run_phases` helper introduces one extra Python call per phase invocation (15 + 6 = 21 per turn × 100 turns of typical play = 2100 extra calls). Negligible vs the engine work itself. PROJ-365 added the 15-call layer with no measurable regression.
**Mitigation:** Phase 4 task includes a phase-timing test asserting `_phase_times['total']` overhead doesn't increase by more than +5% relative to baseline. PROJ-365's `TURN PERF` log gives us the baseline.

### Test-flake from new injection plumbing (MEDIUM — actively mitigated)
17 test files construct `TurnEngine(...)` directly. Phase 3 changes the required-kwarg shape. Drive-by test rot is the most likely failure mode.
**Mitigation:** Phase 3 task list includes (a) updating `tests/unit/strategy/turn_engine/conftest.py:24-26` to use `TurnEngineConfig.create_default(...)`, (b) running a grep-driven inventory of every direct construction and converting them, (c) preserving the existing `mock_engines.py` indirection. Lazy-property tests in `test_turn_engine_lazy_properties.py` are repurposed to verify config-injected defaults.

### Silent removal of `_NullBattleResolver` warning path (LOW — by design)
Today, when a caller forgets `ai_factory` AND `battle_resolver`, `conflict_engine` lazily creates `_NullBattleResolver` and logs a WARNING. Combat then raises at first call. Removing this means the error surfaces from `ConflictResolutionEngine` directly with no upstream warning.
**Mitigation:** Phase 3 verifies `ConflictResolutionEngine` raises a clear error message when `battle_resolver=None`. If it doesn't, we add one. The warning was strictly noise during normal "no combat happens" sessions; raising at point-of-use is more useful than warning at construction.

### `_NullBattleResolver` is currently exported (LOW)
`from game.strategy.engine.turn_engine import _NullBattleResolver` works today — `test_turn_engine_lazy_properties.py:18` imports it. The leading underscore signals private; the test imports it deliberately to verify the contract. Phase 3 deletes the symbol; that test is rewritten to assert the new "raise on combat" contract instead.

## Dependencies

| Dependency | Type | Status |
|---|---|---|
| **PROJ-259** | Parent — produced `TurnEngineConfig` (16 fields, frozen) | Complete (deep_archive) — PROJ-369 EXTENDS it (`create_default()` classmethod + 3 fields) |
| **PROJ-365** | Parent — produced `DEFAULT_TICK_PHASE_LIST` + `_process_tick` descriptor iteration | Complete (active_projects) — PROJ-369 mirrors the pattern for end-of-turn |
| **PROJ-258** | Foundational — `ApplicationContext` DI baseline | Complete; PROJ-369 follows the principle but does not modify ApplicationContext |
| **PROJ-368** | Sibling — OrderProcessor decomposition | In planning. PROJ-369 consumes `IOrderProcessor` unchanged. Manifest overlap = zero (different files: `order_processor.py` vs `turn_engine.py`). Branches can run in parallel; merge order is irrelevant. |
| **PROJ-284** | Behavioral contract — organics → happiness → population_growth ordering | Complete; PROJ-369 preserves order via the golden-list test in Phase 1 |
| **PROJ-291** | Behavioral contract — `race_registry` threads to Population/Happiness | Complete; PROJ-369 preserves the ctor kwarg in the new `create_default(...)` signature |
| **PROJ-343** | Behavioral contract — end-of-turn engines route through `_time_phase` for rollback | Complete; PROJ-369 preserves rollback semantics by routing each descriptor through `_time_phase` (same as the tick loop) |

## Open Questions

1. **Should the 15 lazy properties be deleted after Phase 3, or kept as trivial passthroughs?** Deleting eliminates ~50 LOC and the API leaks `_foo_engine` access. Keeping preserves the public read surface but adds noise. Lean: keep as passthroughs for stable API; revisit in Phase 5.

2. **Should `create_default_turn_engine()` factory survive Phase 3?** It currently does `return TurnEngine(registries=registries, config=config, ai_factory=ai_factory)`. After Phase 3, this becomes `return TurnEngine(registries=registries, config=TurnEngineConfig.create_default(registries, ai_factory=ai_factory))` — three-line shim. Lean: delete it, route docs/tests directly to `TurnEngineConfig.create_default()` + `TurnEngine(...)`. **DECIDE in phase_3 task list.**

3. **Should the `tick_phases=` and `end_of_turn_phases=` ctor kwargs accept callables that return descriptors, or only descriptor tuples?** PROJ-365 chose tuples. Test ergonomics for "swap one phase" is `tuple(replacement if p.phase_key == 'X' else p for p in DEFAULT_TICK_PHASE_LIST)`. Lean: stay with tuples for consistency.

4. **`_NullBattleResolver` deletion timing.** Phase 3 deletes the class. Does Phase 3 also rewrite `ConflictResolutionEngine` to raise an explicit error when `battle_resolver is None`, or do we trust the existing implicit raise from `resolve_battle`? **DECIDE in phase_3 task list — likely we add one explicit check + clear message.**

5. **Should `IQualityEngine` / `IAtmosphereEngine` / `IWaterEngine` protocols include `registries: GameRegistries` as a constructor contract?** Today these engines accept `registries` as a ctor kwarg. Protocols typically describe instance methods, not construction. Lean: protocols describe the `process_*` method only; construction stays in `TurnEngineConfig.create_default()`.

6. **TickContext field naming for end-of-turn.** End-of-turn phases run with `tick=0` (sentinel for "after the loop"). Is that surprising in `TickContext`? Alternative: introduce `EndOfTurnContext` as a sibling dataclass. Lean: reuse `TickContext`; document `tick=0` semantics. Simpler, fewer types.

7. **Phase ordering for parallel execution with PROJ-368.** Both projects are 03c phase-aware and share zero files. The plan allows PROJ-368 and PROJ-369 to run concurrently. Coordinator should confirm zero `manifest.md` overlap before scheduling.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
