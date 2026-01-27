# Phase 1: ConflictResolutionEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract all combat resolution logic (~145 lines) to dedicated engine

---

## Tasks

### Task 1.1: Create ConflictResolutionEngine file [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_conflict_resolution_engine.py`

- [ ] Create new file with module docstring:
  ```python
  """
  ConflictResolutionEngine - Combat Resolution for Strategy Layer

  PROJ-36: Extracted from TurnEngine to handle combat detection and resolution.

  Responsibilities:
  - Detect multi-empire conflicts at contested hexes
  - Orchestrate battle resolution via IBattleResolver
  - Apply combat results to fleet rosters
  """
  ```
- [ ] Add imports: `typing`, `dataclasses`, `random`, `game.core.logger`
- [ ] Create `ConflictResult` dataclass:
  ```python
  @dataclass
  class ConflictResult:
      combats_resolved: int
      fleets_destroyed: List[int]  # fleet IDs
  ```
- [ ] Create `ConflictResolutionEngine` class with `__init__(battle_resolver=None)`
- [ ] Move `_generate_battle_seed` logic (TurnEngine lines 114-117)
- [ ] Move `_resolve_conflicts` logic (TurnEngine lines 323-344)
- [ ] Move `_resolve_combat_at_hex` logic (TurnEngine lines 346-383)
- [ ] Move `_resolve_combat` logic (TurnEngine lines 385-400)
- [ ] Move `_resolve_combat_simulated` logic (TurnEngine lines 402-431)
- [ ] Add public method: `resolve_all_conflicts(empires) -> ConflictResult`
- [ ] Verify: File follows patterns in FleetMovementEngine

**Notes:**

---

### Task 1.2: Update TurnEngine to delegate combat [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py -k combat`

- [ ] Add TYPE_CHECKING import for ConflictResolutionEngine
- [ ] Add `_conflict_engine: Optional['ConflictResolutionEngine'] = None` to __init__
- [ ] Add lazy property `conflict_engine` following pattern at lines 90-112:
  ```python
  @property
  def conflict_engine(self) -> 'ConflictResolutionEngine':
      if self._conflict_engine is None:
          from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
          self._conflict_engine = ConflictResolutionEngine(self._battle_resolver)
      return self._conflict_engine
  ```
- [ ] Replace `self._resolve_conflicts(empires)` call (line 241) with:
  ```python
  self.conflict_engine.resolve_all_conflicts(empires)
  ```
- [ ] Remove `_generate_battle_seed` method (lines 114-117)
- [ ] Remove `_battle_seed_counter` instance variable (line 76)
- [ ] Remove `_resolve_conflicts` method (lines 323-344)
- [ ] Remove `_resolve_combat_at_hex` method (lines 346-383)
- [ ] Remove `_resolve_combat` method (lines 385-400)
- [ ] Remove `_resolve_combat_simulated` method (lines 402-431)
- [ ] Remove unused `_apply_battle_results` method (lines 433-467)
- [ ] Verify: TurnEngine compiles without errors

**Notes:**

---

### Task 1.3: Create/migrate combat tests [Simple]
**File:** `tests/unit/strategy/test_conflict_resolution_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_conflict_resolution_engine.py`

- [ ] Create new test file with imports and fixtures from test_turn_engine.py
- [ ] Move `TestCombatResolution` class tests:
  - `test_resolve_conflicts_detects_collision`
  - `test_no_conflict_same_empire`
  - `test_resolve_combat_rng_fallback_for_empty_fleet`
  - `test_resolve_combat_uses_simulation`
- [ ] Move `TestBattleResolverInjection` class tests (9 methods):
  - `test_turn_engine_accepts_battle_resolver`
  - `test_turn_engine_defaults_to_simulation_resolver`
  - `test_resolve_combat_simulated_uses_injected_resolver`
  - `test_mock_resolver_enables_unit_testing`
  - `test_battle_results_applied_to_fleets`
  - `test_draw_returns_fleet_with_more_survivors`
  - `test_seed_passed_to_resolver`
  - `test_seed_counter_increments`
  - `test_seed_counter_starts_at_one`
- [ ] Add test: 3+ empires simultaneous combat at same hex
- [ ] Add test: Empty fleet vs fleet with ships (verify loser semantics)
- [ ] Add test: Both fleets empty (RNG fallback)
- [ ] Update test imports to use ConflictResolutionEngine
- [ ] Verify: All tests pass with `pytest tests/unit/strategy/test_conflict_resolution_engine.py`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/strategy/test_turn_engine.py` - passes
- [ ] Run `pytest tests/unit/strategy/test_conflict_resolution_engine.py` - passes
- [ ] Run `pytest tests/integration/` - passes
- [ ] TurnEngine reduced by ~145 lines
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
