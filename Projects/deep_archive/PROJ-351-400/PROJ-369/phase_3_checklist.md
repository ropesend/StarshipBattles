# Phase 3: Required-kwarg injection — eliminate lazy fallback init

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-369 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Committed)
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):**
- `game/strategy/engine/turn_engine_config.py` (modify — add `create_default()` classmethod)
- `game/strategy/engine/turn_engine.py` (modify — delete 15 lazy-property fallback bodies; delete `_NullBattleResolver`; reduce `__init__` to 8 kwargs; properties become trivial passthroughs)
- `game/strategy/engine/game_session.py:102, 386` (modify — 2 production call sites)
- `tests/unit/strategy/turn_engine/conftest.py:24-26` (modify — fixture uses `TurnEngineConfig.create_default(...)`)
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (modify — repurpose tests for config-injected defaults; remove `_NullBattleResolver` import + warn-fallback test)
- `tests/unit/strategy/turn_engine/test_dependency_injection.py` (modify)
- `tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py` (modify)
- `tests/unit/strategy/mocks/mock_engines.py` (verify — update if construction shape changed)
- 5+ integration test files under `tests/integration/strategy/` (verify — should JUST WORK via fixture migration)

**Objective:** Add `TurnEngineConfig.create_default()` classmethod that eagerly constructs every default engine. Migrate 2 production call sites + ≥35 test sites (re-grepped at task start). Delete the 15 lazy-property fallback bodies; properties become `return self._foo_engine`. Delete `_NullBattleResolver` (dead after this phase). Reduce `TurnEngine.__init__` from 20 to 8 kwargs.

---

## Pre-flight

- [ ] Verify Phase 2 status is `verified` (or `committed`) per `phase_dag.py status`
- [ ] **Re-grep authoritative inventory** at task start: `grep -rln 'TurnEngine(' tests/` and `grep -rn "create_default_turn_engine(" tests/ game/`. Record the file list in this checklist BEFORE any sweeping work begins. Expected: ≥35 test sites (re-grepped at task start) plus 2 production sites in `game_session.py`.
- [ ] Read `game/strategy/engine/conflict_resolution_engine.py` — confirm whether it raises a clear error when constructed with `battle_resolver=None`. If not, decide whether to add one in this phase (open question Q4 in design.md).

---

## Tasks

### Task 3.1: Add AST guard test — TDD-first [Medium]
**File:** `tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py` (new)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py -v`

- [ ] Write test `test_no_if_self_engine_is_none_pattern`: parse `game/strategy/engine/turn_engine.py` via `ast`, walk for `If` nodes whose test matches `Compare(Attribute(self._\w+_engine), Is, Constant(None))`. Assert zero matches.
- [ ] Write test `test_no_function_local_engine_imports_in_TurnEngine_methods`: walk every `FunctionDef` whose direct parent is `TurnEngine`. For each, walk for `ImportFrom` nodes whose module matches `game.strategy.engine.\w+_engine`. Assert zero matches.
- [ ] Write test `test_TurnEngine_init_signature_has_at_most_8_params`: import `TurnEngine`, `len(inspect.signature(TurnEngine).parameters) <= 8` (excluding `self`).
- [ ] Write test `test_NullBattleResolver_symbol_absent`: assert `not hasattr(turn_engine_module, '_NullBattleResolver')`.
- [ ] Run the test; **confirm all 4 fail** on current code (15 fallback patterns + 18 function-local imports + 20 params + symbol present).
- [ ] **Verify:** test fails for the right reasons (the regression-detection invariants are encoded correctly).

**Notes:**

### Task 3.2: Add `TurnEngineConfig.create_default()` classmethod [Complex]
**File:** `game/strategy/engine/turn_engine_config.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_init_precedence.py -v` (after Task 3.6)

- [ ] Add classmethod (after the dataclass declaration):
  ```python
  @classmethod
  def create_default(
      cls,
      registries: GameRegistries,
      *,
      ai_factory: Any = None,
      race_registry: 'IRaceRegistry | None' = None,
      event_bus: Any = None,
  ) -> 'TurnEngineConfig':
      """Eagerly construct all 18 default engines and bundle them.

      This is the canonical entry point for production code. Tests that
      need to override specific engines should construct TurnEngineConfig
      directly with field overrides instead of calling this method.

      PROJ-369 Phase 3: replaces the per-property lazy fallback init
      that previously lived in TurnEngine.{movement_engine, ...}.
      """
      from game.strategy.engine.fleet_movement_engine import FleetMovementEngine
      from game.strategy.engine.production_engine import ProductionEngine
      from game.strategy.engine.order_processor import OrderProcessor
      from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
      from game.strategy.engine.consumable_management_engine import ConsumableManagementEngine
      from game.strategy.engine.population_engine import PopulationEngine
      from game.strategy.engine.resupply_engine import ResupplyEngine
      from game.strategy.engine.harvesting_engine import HarvestingEngine
      from game.strategy.engine.action_execution_engine import ActionExecutionEngine
      from game.strategy.engine.environmental_hazard_engine import EnvironmentalHazardEngine
      from game.strategy.engine.planet_energy_engine import PlanetEnergyEngine
      from game.strategy.engine.planet_action_engine import PlanetActionEngine
      from game.strategy.engine.component_activation_engine import ComponentActivationEngine
      from game.strategy.engine.organics_consumption_engine import OrganicsConsumptionEngine
      from game.strategy.engine.happiness_engine import HappinessEngine
      from game.strategy.engine.quality_engine import QualityEngine
      from game.strategy.engine.atmosphere_engine import AtmosphereEngine
      from game.strategy.engine.water_engine import WaterEngine
      from game.strategy.services.action_time_resolver import ActionTimeResolver

      # Battle resolver: only constructed when ai_factory is provided.
      # battle_resolver=None reaches conflict_engine, which raises loudly
      # at first combat. _NullBattleResolver was deleted in this phase.
      battle_resolver = None
      if ai_factory is not None:
          from game.strategy.adapters.simulation_adapter import SimulationBattleResolver
          battle_resolver = SimulationBattleResolver(ai_factory=ai_factory)

      order_processor = OrderProcessor(event_bus=event_bus)

      return cls(
          movement_engine=FleetMovementEngine(),
          production_engine=ProductionEngine(registries=registries, event_bus=event_bus),
          order_processor=order_processor,
          conflict_engine=ConflictResolutionEngine(
              battle_resolver, registries=registries, event_bus=event_bus,
          ),
          resource_engine=ConsumableManagementEngine(registries=registries),
          population_engine=PopulationEngine(race_registry=race_registry),
          resupply_engine=ResupplyEngine(registries=registries),
          harvesting_engine=HarvestingEngine(registries=registries),
          action_engine=ActionExecutionEngine(
              order_processor=order_processor,
              action_time_resolver=ActionTimeResolver(),
          ),
          environmental_engine=EnvironmentalHazardEngine(),
          planet_energy_engine=PlanetEnergyEngine(registries=registries, event_bus=event_bus),
          planet_action_engine=PlanetActionEngine(
              registries=registries,
              action_time_resolver=ActionTimeResolver(),
              event_bus=event_bus,
          ),
          component_activation_engine=ComponentActivationEngine(),
          organics_consumption_engine=OrganicsConsumptionEngine(),
          happiness_engine=HappinessEngine(race_registry=race_registry),
          quality_engine=QualityEngine(registries=registries),
          atmosphere_engine=AtmosphereEngine(registries=registries),
          water_engine=WaterEngine(registries=registries),
      )
  ```
- [ ] Note: imports are function-local INSIDE `create_default` to avoid module-level circular imports. This is the ONE allowlisted exception in the AST guard test (Task 3.1) — phrase the AST test to allow `ImportFrom` inside `create_default` only.
- [ ] **Verify:** `python -c "from game.strategy.engine.turn_engine_config import TurnEngineConfig; from game.core.registry import GameRegistries; cfg = TurnEngineConfig.create_default(GameRegistries(...))"` succeeds (use a real registries fixture during testing)

**Notes:**

### Task 3.3: Reduce `TurnEngine.__init__` to 8 kwargs [Complex]
**File:** `game/strategy/engine/turn_engine.py:144-240`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v` (after Task 3.4 + 3.6)

- [ ] Replace the 20-kwarg signature (lines 144-169) with:
  ```python
  def __init__(
      self,
      *,
      registries: GameRegistries,
      config: 'TurnEngineConfig',
      ai_factory: Optional[Any] = None,
      race_registry: Optional['IRaceRegistry'] = None,
      event_bus=None,
      battle_resolver: Optional['IBattleResolver'] = None,
      tick_phases: Optional[tuple['TickPhase', ...]] = None,
      end_of_turn_phases: Optional[tuple['TickPhase', ...]] = None,
  ) -> None:
  ```
  Note: `config` is now REQUIRED (no default). `battle_resolver` survives as an explicit override slot for tests that need to skip combat. `ai_factory`/`race_registry`/`event_bus` survive as documentation hooks but are NOT used inside `__init__` itself — config is expected to have already-bound values that used these.
- [ ] Replace the 18 `self._foo_engine = foo_engine or cfg.foo_engine` lines (190-223) with 18 plain assignments:
  ```python
  self._battle_resolver = battle_resolver if battle_resolver is not None else config.conflict_engine._battle_resolver  # see open question Q4
  self._ai_factory = ai_factory
  self._registries = registries
  self._event_bus = event_bus
  self._race_registry = race_registry

  self._movement_engine = config.movement_engine
  self._production_engine = config.production_engine
  self._order_processor = config.order_processor
  self._conflict_engine = config.conflict_engine
  self._resource_engine = config.resource_engine
  self._population_engine = config.population_engine
  self._resupply_engine = config.resupply_engine
  self._harvesting_engine = config.harvesting_engine
  self._action_engine = config.action_engine
  self._environmental_engine = config.environmental_engine
  self._planet_energy_engine = config.planet_energy_engine
  self._planet_action_engine = config.planet_action_engine
  self._component_activation_engine = config.component_activation_engine
  self._organics_consumption_engine = config.organics_consumption_engine
  self._happiness_engine = config.happiness_engine
  self._quality_engine = config.quality_engine
  self._atmosphere_engine = config.atmosphere_engine
  self._water_engine = config.water_engine
  ```
- [ ] Resolve open question Q4: probably `self._battle_resolver = battle_resolver` (let conflict_engine surface its own resolver state). Document the chosen behavior in `decisions.md`.
- [ ] Keep `_tick_phases` / `_end_of_turn_phases` field assignments unchanged (lines 228-230 + Phase 1's addition)
- [ ] **Verify:** `inspect.signature(TurnEngine).parameters` has 8 entries (after `self`)

**Notes:**

### Task 3.4: Convert lazy properties to trivial passthroughs [Medium]
**File:** `game/strategy/engine/turn_engine.py:319-481` (and the 3 added in Phase 2)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py -v`

- [ ] Replace each of the 18 lazy properties' bodies (15 from PROJ-365 + 3 from Phase 2) with a single-line passthrough:
  ```python
  @property
  def movement_engine(self) -> 'IMovementEngine':
      """Return injected movement engine."""
      return self._movement_engine
  ```
- [ ] Apply same change for: `production_engine`, `order_processor`, `conflict_engine`, `resource_engine`, `population_engine`, `resupply_engine`, `harvesting_engine`, `action_engine`, `environmental_engine`, `planet_energy_engine`, `planet_action_engine`, `component_activation_engine`, `organics_consumption_engine`, `happiness_engine`, `quality_engine`, `atmosphere_engine`, `water_engine`.
- [ ] **Special case for `conflict_engine`:** today's lazy body (lines 344-369) does battle-resolver decision tree work. Move that decision into `TurnEngineConfig.create_default()` (Task 3.2 already does — `SimulationBattleResolver` is constructed there when `ai_factory` is provided; otherwise `battle_resolver=None`).

**Notes:**

### Task 3.5: Delete `_NullBattleResolver` [Simple]
**File:** `game/strategy/engine/turn_engine.py:109-122`
**Tests:** AST guard (Task 3.1) verifies absence

- [ ] Delete the entire `class _NullBattleResolver:` block (lines 109-122)
- [ ] Delete the `from game.strategy.engine.turn_engine import _NullBattleResolver` import in `test_turn_engine_lazy_properties.py:18`
- [ ] Update `TestConflictEngineBattleResolverBranches::test_conflict_engine_uses_null_battle_resolver_and_warns_when_both_resolver_and_ai_factory_none` (lines 278-305): replace assertion-on-warning-log with assertion-on-explicit-raise. Specifically: instantiate `TurnEngine` via `TurnEngineConfig.create_default(registries, ai_factory=None)`, access `engine.conflict_engine`, and assert that calling `resolve_battle(...)` raises a clear error from `ConflictResolutionEngine` (not `RuntimeError("No battle resolver configured")` from `_NullBattleResolver` — that path is gone).
- [ ] If `ConflictResolutionEngine` doesn't raise a clear message today, add one as a small concession in this phase: a single guard at the top of `resolve_all_conflicts` checking `if self._battle_resolver is None: raise ValueError("ConflictResolutionEngine constructed without battle_resolver; combat cannot resolve")`.

**Notes:**

### Task 3.6: Migrate 2 production call sites [Medium]
**File:** `game/strategy/engine/game_session.py:102-107, 386-391`
**Tests:** `pytest tests/integration/strategy/test_game_session_strategy.py -v`

- [ ] At line 102-107, replace `TurnEngine(registries=…, ai_factory=…, event_bus=…, race_registry=…)` with:
  ```python
  cfg = TurnEngineConfig.create_default(
      self._registries,
      ai_factory=ai_factory,
      race_registry=self.race_registry,
      event_bus=self._event_bus,
  )
  self.turn_engine = TurnEngine(
      registries=self._registries,
      config=cfg,
      ai_factory=ai_factory,
      race_registry=self.race_registry,
      event_bus=self._event_bus,
  )
  ```
- [ ] Apply same pattern at line 386-391 (`from_dict` path)
- [ ] Add import at top: `from game.strategy.engine.turn_engine_config import TurnEngineConfig`
- [ ] **Verify:** `pytest tests/integration/strategy/test_game_session_strategy.py -v` — passes

**Notes:**

### Task 3.7: Migrate test fixture + direct test constructions [Complex]
**File:** `tests/unit/strategy/turn_engine/conftest.py:24-26` (and the nearest `tests/conftest.py` for the shared factory) and ≥35 test construction sites (re-grepped at task start)
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v`

- [ ] **(a) Re-grep authoritative inventory.** Run `grep -rln 'TurnEngine(' tests/` at task start. Record the file list in this checklist's Notes section before any sweeping work begins. Expected: ≥35 test sites (the previously-quoted "17" was a stale estimate).
- [ ] **(b) Introduce a shared `turn_engine_factory` fixture in the nearest `tests/conftest.py`** returning `TurnEngine(TurnEngineConfig.create_default(...))` parameterised on common engine swaps. Suites that take the factory directly (no per-test override) are migrated en bloc once the factory exists.
  ```python
  # tests/conftest.py (or nearest shared conftest)
  @pytest.fixture
  def turn_engine_factory(fresh_registries):
      """Build TurnEngine via TurnEngineConfig.create_default; accept overrides."""
      from game.strategy.engine.turn_engine_config import TurnEngineConfig
      def _make(**overrides):
          cfg = TurnEngineConfig.create_default(fresh_registries, ai_factory=MagicMock())
          if overrides:
              import dataclasses
              cfg = dataclasses.replace(cfg, **overrides)
          return TurnEngine(registries=fresh_registries, config=cfg, ai_factory=MagicMock())
      return _make
  ```
- [ ] **(c) Update the existing `tests/unit/strategy/turn_engine/conftest.py:24-26` `turn_engine` fixture** to delegate to the factory:
  ```python
  @pytest.fixture
  def turn_engine(turn_engine_factory):
      return turn_engine_factory()
  ```
- [ ] **(d) Per-test overrides** stay supported via `dataclasses.replace(cfg, foo_engine=mock_foo)`. For each call site recorded in step (a):
  - If it constructs the engine for general turn-processing tests: replace with the `turn_engine_factory()` fixture or `TurnEngineConfig.create_default(...)` + `TurnEngine(registries=..., config=cfg)`.
  - If it constructs the engine to override one or more sub-engines (e.g. `test_turn_engine_end_of_turn_order.py`): pass overrides through `turn_engine_factory(foo_engine=mock_foo)` (which internally `dataclasses.replace`s).
- [ ] Pay special attention to:
  - `test_turn_engine_lazy_properties.py:26-180` — repurpose: instead of "lazy property creates default class", assert "config-injected default class flows through to the property". Drop `TestConflictEngineBattleResolverBranches::test_conflict_engine_uses_null_battle_resolver_and_warns…` as obsolete (Task 3.5).
  - `test_dependency_injection.py:336+` — `TestFactoryFunction` updated for `create_default_turn_engine` deletion (decided in Task 3.8).
  - `test_turn_engine_init_precedence.py` — the precedence semantics flip: there are no individual-kwarg overrides anymore. Tests assert `config` field values flow through, and `tick_phases=`/`end_of_turn_phases=` overrides win over config.
  - `mock_engines.py` — verify the mock factories still work; if they construct `TurnEngine` directly, update them.
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/ -v` — green
- [ ] **Verify:** `pytest tests/integration/strategy/turn_engine/ -v` — green (these consume `conftest.py:turn_engine` fixture or construct directly)

**Notes:** This is the largest single task by file count. Sub-task it during execution.

### Task 3.8: Delete `create_default_turn_engine()` factory function [Simple]
**File:** `game/strategy/engine/turn_engine.py:763-801`
**Tests:** AST guard (Task 3.1)

- [ ] Delete the function (lines 763-801, ~39 LOC).
- [ ] Update `docs/systems/strategy_layer.md:280` to point to `TurnEngineConfig.create_default(registries, ...)` + `TurnEngine(registries=..., config=cfg)` (Phase 5 will redo this; leave a TODO comment if needed).
- [ ] Update `docs/02_PATTERNS.md:1331` similarly (Phase 5).
- [ ] Update or delete `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py::TestCreateDefaultTurnEngineFactory` (lines 183-249) — these tests pinned the factory; they no longer apply. Replace with one test asserting `create_default_turn_engine` is no longer importable.
- [ ] **Verify:** `python -c "from game.strategy.engine.turn_engine import create_default_turn_engine"` raises `ImportError`

**Notes:**

### Task 3.9: AST guard test should now pass [Simple]
**Tests:** `pytest tests/unit/strategy/turn_engine/test_no_lazy_fallback_init.py -v`

- [ ] Run the Task 3.1 test; **confirm it now passes** (zero `if self._foo_engine is None` patterns; zero function-local `from game.strategy.engine.\w+ import \w+Engine` outside the create_default allowlist; ≤8 ctor params; symbol absent)
- [ ] **Verify:** the test would fail again if any of Tasks 3.3/3.4/3.5 were reverted (sanity check the AST regex correctness)

**Notes:**

### Task 3.10: Full focused-test pass [Medium]
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v` and `pytest tests/integration/strategy/ -v`

- [ ] Run focused unit + integration tests
- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 3.11: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ Phase 2 baseline + 4 (Task 3.1's 4 AST tests)
- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 3.12: Commit Phase 3 [Simple]

- [ ] Commit message: `feat(PROJ-369): Phase 3 — required-kwarg injection via TurnEngineConfig.create_default(); delete _NullBattleResolver and 15 lazy fallback bodies`
- [ ] Sign-off; do NOT push
- [ ] Run `phase_complete.py PROJ-369 3`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `TurnEngineConfig.create_default()` exists and is the canonical injection entry point
- [ ] `TurnEngine.__init__` has 8 kwargs (was 20)
- [ ] All 18 lazy properties are trivial passthroughs (no fallback init)
- [ ] `_NullBattleResolver` is deleted; symbol absent from module
- [ ] `create_default_turn_engine()` is deleted (or kept as decided)
- [ ] AST guard test (`test_no_lazy_fallback_init.py`) passes
- [ ] All ≥35 test sites (re-grepped at task start) migrated to new construction shape
- [ ] 2 production call sites in `game_session.py` migrated
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
