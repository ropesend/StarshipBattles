# PROJ-369: Strategy: TurnEngine Decomposition (phase-aware ITickPhase migration completion)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-369` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-369 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist | Depends on |
|-------|--------|-----------|------------|
| 1. Extract end-of-turn block to descriptor list (`DEFAULT_END_OF_TURN_PHASE_LIST`) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) | — |
| 2. Make the 3 locally-constructed end-of-turn engines (Quality / Atmosphere / Water) injectable + lazy-property + `TurnEngineConfig` fields | Not Started | [phase_2_checklist.md](phase_2_checklist.md) | phase_1 |
| 3. Replace per-property lazy fallback init with required-kwarg injection from `TurnEngineConfig` (factory pre-fills defaults) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) | phase_2 |
| 4. Convert tick + end-of-turn loops to a unified `for phase in self._phases: phase.run(ctx)` body | Not Started | [phase_4_checklist.md](phase_4_checklist.md) | phase_3 |
| 5. AST guard test + per-phase unit tests with mock context; remove `_NullBattleResolver`; finalize docs | Not Started | [phase_5_checklist.md](phase_5_checklist.md) | phase_4 |

## Current State
**Last Updated:** 2026-05-05
**Active Phase:** Planning
**Last Action:** Plan drafted; awaiting user approval.
**Next Action:** User reviews plan; on approval, run `claude-proj-start PROJ-369` to seed `phase_state.json` and create `proj/PROJ-369/main` branch.
**Blockers:** Awaiting user approval.
**Context for Next Agent:** This project completes (does NOT supersede) PROJ-259 + PROJ-365. Per-tick descriptor migration shipped in PROJ-365 (`game/strategy/engine/turn_phase_registry.py:174-297` defines `DEFAULT_TICK_PHASE_LIST`). PROJ-259 added `TurnEngineConfig`. The 13 sub-engines have lazy fallback init in 15 properties at `turn_engine.py:319-481`; 3 end-of-turn engines (`QualityEngine`/`AtmosphereEngine`/`WaterEngine`) are still locally constructed inline at `turn_engine.py:606-620` (function-local imports — non-injectable today). Constructor still accepts 20 kwargs. The fallback init defeats DI: tests cannot tell which default got used; behavior diverges between CI and local.

## Overview

This project finishes the `ITickPhase`-style migration that PROJ-259 started and PROJ-365 advanced. PROJ-365 turned the 100-tick body into a descriptor-iteration loop over `DEFAULT_TICK_PHASE_LIST` (15 phases) but explicitly excluded the 6-engine end-of-turn block. PROJ-369 (a) extends the descriptor pattern to the end-of-turn block, (b) makes the three locally-constructed end-of-turn engines injectable, (c) eliminates per-property lazy fallback initialization in favor of required-kwarg injection seeded by `TurnEngineConfig.create_default()`, and (d) collapses the two remaining call sites (per-tick, end-of-turn) into a single unified loop. The result is one execution body, no implicit defaults, every engine traceable to a single construction site.

## Goals

- **Phase 1:** New `DEFAULT_END_OF_TURN_PHASE_LIST` in `turn_phase_registry.py` covering organics_consumption, happiness, population_growth, quality_improvement, atmosphere, water_modification — all 6 routed through `_time_phase` already, just needs descriptor extraction. End-of-turn block in `process_turn` becomes a 3-line loop.
- **Phase 2:** `QualityEngine` / `AtmosphereEngine` / `WaterEngine` get protocol interfaces (`IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` in `game/strategy/interfaces/engines.py`); ctor kwargs added to `TurnEngine`; `TurnEngineConfig` gains 3 `Optional` fields; lazy properties added (mirroring the 13 existing lazy properties). After Phase 2 the sub-engine count is **18** (15 tick + 3 end-of-turn additions; population/organics/happiness already injectable).
- **Phase 3:** `TurnEngineConfig.create_default(registries, *, ai_factory=None, race_registry=None, event_bus=None) -> TurnEngineConfig` factory builds every engine eagerly. `TurnEngine.__init__` becomes: `def __init__(self, *, registries, config, ai_factory=None, race_registry=None, event_bus=None, battle_resolver=None, tick_phases=None, end_of_turn_phases=None)`. The 13 fallback `if self._foo_engine is None: self._foo_engine = FooEngine(...)` blocks (~155 LOC of `turn_engine.py:319-481`) **deleted**. Properties become trivial passthroughs (`return self._foo_engine`) or are deleted in favor of direct attribute access (decision deferred to phase tasks).
- **Phase 4:** `_process_tick` and the end-of-turn block both become a single helper `_run_phases(self, phases: tuple[TickPhase, ...], ctx: TickContext) -> None`. `process_turn` body collapses to: 100-tick loop calling `_run_phases(self._tick_phases, ctx)` + one call to `_run_phases(self._end_of_turn_phases, end_of_turn_ctx)`.
- **Phase 5:** AST guard test pinning zero `if self._<x>_engine is None` patterns in `turn_engine.py`. Per-phase unit tests demonstrating injection through mock `TurnEngineConfig`. Remove `_NullBattleResolver` (dead after Phase 3 — config factory installs `SimulationBattleResolver` or raises). Update `docs/systems/strategy_layer.md` and `docs/02_PATTERNS.md` § 35 (TurnEngineConfig).

## Scope

**In:**
- `game/strategy/engine/turn_engine.py` — constructor reduction (20 → 8 kwargs), removal of 15 lazy-property fallback bodies, removal of `_NullBattleResolver` class, end-of-turn block replaced with descriptor iteration.
- `game/strategy/engine/turn_engine_config.py` — add `create_default()` classmethod; add `quality_engine` / `atmosphere_engine` / `water_engine` fields.
- `game/strategy/engine/turn_phase_registry.py` — add `DEFAULT_END_OF_TURN_PHASE_LIST`; extract `_run_phases` helper signature decision (in turn_engine.py — registry stays data-only).
- `game/strategy/interfaces/engines.py` — add `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` protocols.
- `game/strategy/engine/quality_engine.py`, `atmosphere_engine.py`, `water_engine.py` — verify they satisfy the new protocols (no implementation change expected; doc-only).
- `game/strategy/engine/game_session.py:102-107, 386-391` — both `TurnEngine(...)` call sites updated to use `TurnEngineConfig.create_default(...)`.
- Tests under `tests/unit/strategy/turn_engine/` — fixture in `conftest.py:24-26` updated; lazy-property tests at `test_turn_engine_lazy_properties.py` repurposed to verify config-injected defaults.

**Out:**
- `game/simulation/systems/battle_engine.py` — battle (simulation) layer is OUT of scope. PROJ-259 added `ITickPhase` for battle_engine separately; that integration is a sibling concern.
- `game/strategy/engine/order_processor.py` — sibling project PROJ-368 owns OrderProcessor decomposition. PROJ-369 only consumes `OrderProcessor` via the existing `IOrderProcessor` interface; we do not modify it.
- `BattleResolver` substitution / combat fallback semantics — `_NullBattleResolver` removal is a clean delete (dead code after Phase 3); no behavioral substitute is added.
- The 15-phase tick body — already done by PROJ-365. Untouched here.
- New gameplay phases / new sub-engines / save-format changes.
- `app.py` screen-state migration (PROJ-259 Phase 1 deferred follow-up — separate concern).

## Key Files

| Component | File Path | Touched By |
|-----------|-----------|------------|
| TurnEngine (god class) | `game/strategy/engine/turn_engine.py` (802 LOC) | Phases 1, 3, 4, 5 |
| TurnEngineConfig | `game/strategy/engine/turn_engine_config.py` (54 LOC) | Phases 2, 3 |
| Tick phase registry | `game/strategy/engine/turn_phase_registry.py` (298 LOC) | Phases 1, 4 |
| Engine protocols | `game/strategy/interfaces/engines.py` (714 LOC) | Phase 2 |
| QualityEngine | `game/strategy/engine/quality_engine.py` | Phase 2 (verify protocol compliance) |
| AtmosphereEngine | `game/strategy/engine/atmosphere_engine.py` | Phase 2 (verify protocol compliance) |
| WaterEngine | `game/strategy/engine/water_engine.py` | Phase 2 (verify protocol compliance) |
| GameSession (production caller) | `game/strategy/engine/game_session.py:102-107, 386-391` | Phase 3 |
| Conftest fixture | `tests/unit/strategy/turn_engine/conftest.py:24-26` | Phase 3 |
| Lazy property tests | `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (306 LOC) | Phases 3, 5 |
| End-of-turn order test | `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` (180 LOC) | Phase 1 |
| Phase-timing test | `tests/unit/strategy/turn_engine/test_turn_engine_phase_timing.py` | Phase 4 |
| AST guard test (NEW) | `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py` | Phase 5 |
| Per-phase mock-context tests (NEW) | `tests/unit/strategy/turn_engine/test_phase_isolation_with_mock_context.py` | Phase 5 |
| Strategy layer docs | `docs/systems/strategy_layer.md` | Phase 5 |
| Pattern docs | `docs/02_PATTERNS.md` § 35 (TurnEngineConfig) | Phase 5 |

## Related Documents

- [design.md](design.md) — Initial Analysis, current vs target architecture diagrams, alternatives, risks, open questions
- [decisions.md](decisions.md) — Pre-populated architectural decisions
- [manifest.md](manifest.md) — Full file table for parallel-execution conflict detection
- [findings/initial_review.md](findings/initial_review.md) — top 5 surprises from the deep code review
- **PROJ-259** (deep_archive/PROJ-251-300/PROJ-259) — produced `TurnEngineConfig` + `ITickPhase` (sim layer); PROJ-369 completes its strategy-layer half
- **PROJ-365** (active_projects/PROJ-365) — produced `DEFAULT_TICK_PHASE_LIST` + descriptor iteration for `_process_tick`; PROJ-369 extends to end-of-turn
- **PROJ-258** (deep_archive) — `ApplicationContext` DI baseline; PROJ-369 inherits the principle (no module-level lazy `get_default_*`) but wires services via `TurnEngineConfig`, not `ApplicationContext` directly (the strategy turn engine is one layer below `ApplicationContext`)
- **PROJ-367** (active_projects/PROJ-367) — recent rigorous 03c-phase-aware project; mirrored for plan style and AST-guard pattern
- **PROJ-368** (active_projects/PROJ-368) — sibling OrderProcessor decomposition; PROJ-369 consumes `IOrderProcessor` unchanged. Manifests must be checked for file overlap before parallel execution (none expected: OrderProcessor lives in `order_processor.py`; PROJ-369 touches `turn_engine.py`)

## Today's vs target pipeline (one-line diff)

**Today** (`turn_engine.py:319-481`, 15 lazy properties; `turn_engine.py:587-620`, 6 imperative end-of-turn calls; `turn_engine.py:744-755`, 1 descriptor-iteration tick loop):

```
self._foo_engine = foo_engine or cfg.foo_engine                       # ctor (15x)
@property
def foo_engine(self):
    if self._foo_engine is None:
        from game.strategy.engine.foo_engine import FooEngine
        self._foo_engine = FooEngine(registries=...)                   # 15x lazy fallback
    return self._foo_engine

# ...
self._time_phase('organics_consumption', ...process_consumption, ...)  # end-of-turn (6x)
# ...
QualityEngine(registries=...).process_quality_improvement(...)         # locally-constructed (3x)

for phase in self._tick_phases: ...  # tick body, descriptor-iterated already
```

**Target** (after Phase 4):

```
# turn_engine_config.py
@classmethod
def create_default(cls, registries, *, ai_factory=None, ...) -> 'TurnEngineConfig':
    return cls(movement_engine=FleetMovementEngine(), ...)              # eager, single site

# turn_engine.py
def __init__(self, *, registries, config, ai_factory=None, ...):
    self._tick_phases = tick_phases or DEFAULT_TICK_PHASE_LIST
    self._end_of_turn_phases = end_of_turn_phases or DEFAULT_END_OF_TURN_PHASE_LIST
    # bind 18 engines from config — one assignment line each, no fallback

@property
def foo_engine(self): return self._foo_engine                           # trivial passthrough

# process_turn
for tick in range(1, TICKS_PER_TURN + 1):
    self._run_phases(self._tick_phases, TickContext(tick=tick, ...))
self._run_phases(self._end_of_turn_phases, TickContext(tick=0, ...))
```

## Phases

### Phase 1: Extract end-of-turn block to `DEFAULT_END_OF_TURN_PHASE_LIST` [Medium]
**Objective:** Mirror PROJ-365 for the 6 end-of-turn engines so `process_turn:587-620` becomes one descriptor iteration. Treat locally-constructed engines as descriptors that materialize the engine on first call. Pin order via golden-list test (mirrors `test_default_tick_phase_list.py`). No protocol or constructor changes yet.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Inject Quality / Atmosphere / Water engines [Medium]
**Objective:** Replace function-local `from ... import QualityEngine` (and Atmosphere, Water) inside `process_turn` with constructor injection. Add `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` protocols to `engines.py`. Add 3 fields to `TurnEngineConfig`. Add 3 lazy properties to `TurnEngine`. Update Phase 1 descriptor list to use injected engines. Behavior identical; existing `test_turn_engine_end_of_turn_order.py:94-138` patches via `patch('game.strategy.engine.quality_engine.QualityEngine')` continue to work.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Required-kwarg injection — eliminate lazy fallback init [Complex]
**Objective:** Add `TurnEngineConfig.create_default(registries, *, ai_factory=None, race_registry=None, event_bus=None)` classmethod that eagerly constructs every default engine. Migrate 2 production call sites (`game_session.py:102, 386`) to use it. Migrate 17 test files to use it via the existing `turn_engine` conftest fixture. Delete the 15 lazy-property fallback bodies (`turn_engine.py:319-481`); properties become `return self._foo_engine` (or are deleted in favor of underscore-prefixed direct access — task-level decision). Delete `_NullBattleResolver` (`turn_engine.py:109-122`) — config factory either installs `SimulationBattleResolver` (when `ai_factory` provided) or leaves `battle_resolver=None` and lets `ConflictResolutionEngine` raise loudly when combat actually triggers (no silent warning path).
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md).

### Phase 4: Unified phase-execution loop [Medium]
**Objective:** Extract `TurnEngine._run_phases(self, phases, ctx)` helper. `_process_tick` becomes 4 lines (build ctx, call `_run_phases`, surface env events). `process_turn`'s end-of-turn block becomes 1 call site. Phase-timing test asserts both lists' bucket keys appear in `_phase_times` after a `process_turn` run.
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md).

### Phase 5: AST guard + mock-context tests + docs [Medium]
**Objective:** AST regression test walking `turn_engine.py` and asserting zero `if self._\w+_engine is None:` patterns and zero function-local `from ... import \w+Engine` outside `_run_phases`. Per-phase unit tests demonstrating descriptor isolation: each phase invocable with a mocked `TurnEngine` exposing only the engines that phase reads. Update `docs/systems/strategy_layer.md` "Turn execution" section. Update `docs/02_PATTERNS.md` § 35 to describe `TurnEngineConfig.create_default()` as the canonical injection pattern. Verify `> **Last verified:**` blockquote per docs/03_CONVENTIONS.md §9.
**Status:** Not Started

See [phase_5_checklist.md](phase_5_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [ ] Read `docs/systems/strategy_layer.md` (turn execution section)
- [ ] Read PROJ-365 design.md and findings/01_architecture.md (the per-tick descriptor work this builds on)
- [ ] Read PROJ-259 deep_archive plan.md + decisions.md (the parent project this completes)
- [ ] Run full sharded suite: `python Tools/test_sharded/test_sharded.py` — capture baseline pass count and pin in plan.md Current State

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/turn_engine/ -v` — focused tests pass
- [ ] Run `pytest tests/integration/strategy/ -v` — strategy integration tests pass
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] Update `Current State` in this plan with handoff context for the next agent

### Final Verification
- [ ] Sharded suite green; pass count ≥ baseline + new tests
- [ ] `_NullBattleResolver` removed; symbol no longer importable from `game.strategy.engine.turn_engine`
- [ ] Zero `if self._\w+_engine is None:` patterns in `turn_engine.py` (AST regression test passes)
- [ ] Zero function-local `from game.strategy.engine.\w+_engine import \w+Engine` statements inside `TurnEngine` methods (AST regression test passes — exception: lazy imports inside `TurnEngineConfig.create_default()` are allowed)
- [ ] `TurnEngine.__init__` signature has ≤ 8 parameters (verified via `inspect.signature`)
- [ ] `process_turn` body contains exactly 2 `_run_phases` invocations (one for tick loop, one for end-of-turn) — visual + AST check
- [ ] `_phase_times` dict in `_reset_phase_times` has 21 keys (unchanged from PROJ-365 baseline)
- [ ] Manual smoke: load `tests/integration/gameplay_loop` baseline save, advance 5 turns, verify combat resolves and end-of-turn engines run
- [ ] `docs/systems/strategy_layer.md` describes the unified phase-execution pattern; `> **Last verified:**` blockquote updated
- [ ] `docs/02_PATTERNS.md` § 35 reflects `TurnEngineConfig.create_default()` factory

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Audit passed (no significant issues)
- [ ] User verified
