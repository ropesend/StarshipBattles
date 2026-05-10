# Phase 2: Inject Quality / Atmosphere / Water engines

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-369 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (Committed)
**Depends on:** phase_1
**Review Mode:** standard
**Files (planned):**
- `game/strategy/interfaces/engines.py` (modify — add 3 protocols)
- `game/strategy/engine/turn_engine_config.py` (modify — add 3 fields)
- `game/strategy/engine/turn_engine.py` (modify — 3 ctor kwargs + 3 lazy properties)
- `game/strategy/engine/turn_phase_registry.py` (modify — descriptor resolvers use injected engines)
- `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py` (modify — 3 new lazy-default tests)
- `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py` (modify — replace mock patches with constructor injection)

**Objective:** Replace function-local `from … import QualityEngine/AtmosphereEngine/WaterEngine` with constructor injection. Add `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` protocols. Add 3 fields to `TurnEngineConfig`. Add 3 lazy properties to `TurnEngine` (mirrors PROJ-365 pattern, will be retired in Phase 3 along with the other 15). Update descriptor resolvers in Phase 1's `turn_phase_registry.py` to use the injected engines instead of locally constructing them. Behavior identical.

---

## Pre-flight

- [ ] Verify Phase 1 status is `verified` (or at minimum `committed`) per `phase_dag.py status`
- [ ] Read `game/strategy/engine/quality_engine.py`, `atmosphere_engine.py`, `water_engine.py` — confirm each has the expected method signature

---

## Tasks

### Task 2.1: Add 3 protocols to `engines.py` (TDD-first via lint pass) [Medium]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** No direct test — verified by import + Phase 5 AST guard

- [ ] After `IPopulationEngine` (around line 446), add `IQualityEngine`:
  ```python
  class IQualityEngine(ABC):
      """Abstract interface for per-turn planet quality improvement.

      PROJ-369 Phase 2: Promoted from locally-constructed to injectable.
      """

      @abstractmethod
      def process_quality_improvement(self, empires: List) -> None:
          """Process planet-quality changes for all empires (once per turn).

          Args:
              empires: List of Empire objects to process.
          """
          pass
  ```
- [ ] Add `IAtmosphereEngine` (mirror shape; method `process_atmosphere(empires)`)
- [ ] Add `IWaterEngine` (mirror shape; method `process_water_modification(empires)`)
- [ ] Add the 3 names to `__all__` (line 29-45)
- [ ] **Verify:** `python -c "from game.strategy.interfaces.engines import IQualityEngine, IAtmosphereEngine, IWaterEngine"` succeeds
- [ ] **Verify:** existing import test (if any) still passes; otherwise nothing to assert until Task 2.4 wires them

**Notes:** docs/03_CONVENTIONS.md §8 — modern type annotations. `List` (from typing) is used by neighbors; matching the file convention is acceptable. New code may prefer `list` per modern syntax — phase task review.

### Task 2.2: Add 3 fields to `TurnEngineConfig` [Simple]
**File:** `game/strategy/engine/turn_engine_config.py`
**Tests:** verified indirectly by Task 2.4

- [ ] After the `happiness_engine` field (line 53), add:
  ```python
  # PROJ-369 Phase 2: per-turn terraforming engines now injectable.
  quality_engine: Optional[Any] = None
  atmosphere_engine: Optional[Any] = None
  water_engine: Optional[Any] = None
  ```
- [ ] Update class docstring count: "16 fields → 19 fields"
- [ ] **Verify:** `python -c "from game.strategy.engine.turn_engine_config import TurnEngineConfig; cfg = TurnEngineConfig(); assert cfg.quality_engine is None and cfg.atmosphere_engine is None and cfg.water_engine is None"` succeeds

**Notes:**

### Task 2.3: Add 3 ctor kwargs + 3 lazy properties to `TurnEngine` [Medium]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py -v` (after Task 2.5)

- [ ] In `TYPE_CHECKING` block (line 82-98), add: `IQualityEngine, IAtmosphereEngine, IWaterEngine`
- [ ] Add 3 ctor kwargs after `happiness_engine` (line 165-166):
  ```python
  quality_engine: Optional['IQualityEngine'] = None,
  atmosphere_engine: Optional['IAtmosphereEngine'] = None,
  water_engine: Optional['IWaterEngine'] = None,
  ```
- [ ] After the `_happiness_engine` field assignment (line 221-223), add:
  ```python
  self._quality_engine: Optional['IQualityEngine'] = quality_engine or cfg.quality_engine
  self._atmosphere_engine: Optional['IAtmosphereEngine'] = atmosphere_engine or cfg.atmosphere_engine
  self._water_engine: Optional['IWaterEngine'] = water_engine or cfg.water_engine
  ```
- [ ] After `happiness_engine` property (line 481), add 3 lazy properties (mirror the established pattern):
  ```python
  @property
  def quality_engine(self) -> 'IQualityEngine':
      """Return quality engine, lazily creating default if not injected."""
      if self._quality_engine is None:
          from game.strategy.engine.quality_engine import QualityEngine
          self._quality_engine = QualityEngine(registries=self._registries)
      return self._quality_engine

  @property
  def atmosphere_engine(self) -> 'IAtmosphereEngine':
      """Return atmosphere engine, lazily creating default if not injected."""
      if self._atmosphere_engine is None:
          from game.strategy.engine.atmosphere_engine import AtmosphereEngine
          self._atmosphere_engine = AtmosphereEngine(registries=self._registries)
      return self._atmosphere_engine

  @property
  def water_engine(self) -> 'IWaterEngine':
      """Return water engine, lazily creating default if not injected."""
      if self._water_engine is None:
          from game.strategy.engine.water_engine import WaterEngine
          self._water_engine = WaterEngine(registries=self._registries)
      return self._water_engine
  ```
- [ ] **Verify:** `python -c "from game.strategy.engine.turn_engine import TurnEngine; ..."` constructs cleanly; `engine.quality_engine` returns a `QualityEngine` instance

**Notes:** These properties are intentionally added in Phase 2 (matching the pattern of the other 15) and DELETED in Phase 3 alongside the others. Phase 2's lazy-property addition lets us land Phase 1's Task 1.3 → Task 1.2's resolvers in turn_phase_registry.py without breaking, while Phase 3 cleans up the whole class of fallback init.

### Task 2.4: Update Phase 1 descriptor resolvers to use injected engines [Medium]
**File:** `game/strategy/engine/turn_phase_registry.py` (the `_resolve_quality_engine` etc. helpers from Phase 1 Task 1.2)
**Tests:** `pytest tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py -v`

- [ ] Replace local-construction resolvers added in Phase 1 with engine-property accessors:
  ```python
  # Old (Phase 1 — local construction, kept until Phase 2):
  def _resolve_quality_engine(engine):
      from game.strategy.engine.quality_engine import QualityEngine
      return QualityEngine(registries=engine._registries).process_quality_improvement

  # New (Phase 2 — injected lazy property):
  # Just use a lambda inline in the descriptor:
  callable_target=lambda e: e.quality_engine.process_quality_improvement,
  ```
- [ ] Apply same change for `atmosphere_engine` and `water_engine`
- [ ] DELETE the 3 `_resolve_*_engine` helpers added in Phase 1 (no longer needed)
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_default_end_of_turn_phase_list.py -v` — golden-list test still passes

**Notes:**

### Task 2.5: Add 3 lazy-default tests to `test_turn_engine_lazy_properties.py` [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py -v`

- [ ] Add to `TestLazyPropertyDefaults` class (mirror existing tests at lines 26-180):
  - `test_quality_engine_property_returns_default_class_and_is_idempotent`
  - `test_atmosphere_engine_property_returns_default_class_and_is_idempotent`
  - `test_water_engine_property_returns_default_class_and_is_idempotent`
- [ ] Each test: instantiate `TurnEngine(registries=fresh_registries)`, access the property, assert isinstance of the production class, assert second access returns the same instance
- [ ] **Verify:** all 3 new tests pass

**Notes:**

### Task 2.6: Update `test_turn_engine_end_of_turn_order.py` to use constructor injection [Medium]
**File:** `tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py -v`

- [ ] Replace `patch('game.strategy.engine.quality_engine.QualityEngine')` (line 70-76) with constructor injection:
  ```python
  # Old:
  with patch('game.strategy.engine.quality_engine.QualityEngine'), \
       patch('game.strategy.engine.atmosphere_engine.AtmosphereEngine'), \
       patch('game.strategy.engine.water_engine.WaterEngine'):
      engine.process_turn(...)

  # New:
  quality = MagicMock(spec=IQualityEngine)
  atmosphere = MagicMock(spec=IAtmosphereEngine)
  water = MagicMock(spec=IWaterEngine)
  engine = TurnEngine(
      registries=fresh_registries,
      ai_factory=MagicMock(),
      quality_engine=quality,
      atmosphere_engine=atmosphere,
      water_engine=water,
      ...
  )
  engine.process_turn([mock_empire], mock_galaxy)
  ```
- [ ] Apply same pattern to lines 110-116 and 163-169
- [ ] Delete the `D-004 OBSERVATION` comment (lines 12-17, 95-99) — no longer applicable; the engines are now injectable
- [ ] **Verify:** `pytest tests/unit/strategy/turn_engine/test_turn_engine_end_of_turn_order.py -v` — all 3 tests pass with constructor injection (cleaner than module patching)

**Notes:**

### Task 2.7: Full focused-test pass [Medium]
**Tests:** `pytest tests/unit/strategy/turn_engine/ -v`

- [ ] Run focused unit tests; assert pass count = Phase 1 baseline + 3 (Task 2.5 added 3 tests)
- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 2.8: Sharded suite green [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run sharded suite; pass count ≥ Phase 1 baseline + 3
- [ ] **Acceptance:** zero regressions

**Notes:**

### Task 2.9: Commit Phase 2 [Simple]

- [ ] Commit message: `feat(PROJ-369): Phase 2 — inject Quality/Atmosphere/Water engines via TurnEngineConfig`
- [ ] Sign-off as before
- [ ] Run `phase_complete.py PROJ-369 2`

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `IQualityEngine`, `IAtmosphereEngine`, `IWaterEngine` exported from `engines.py`
- [ ] `TurnEngineConfig` has 19 fields (16 + 3)
- [ ] `TurnEngine` has 3 new ctor kwargs and 3 new lazy properties
- [ ] `DEFAULT_END_OF_TURN_PHASE_LIST` resolvers use injected engines
- [ ] `test_turn_engine_end_of_turn_order.py` uses constructor injection (no module patching)
- [ ] Update status at top of this file to `Complete (Committed)`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
