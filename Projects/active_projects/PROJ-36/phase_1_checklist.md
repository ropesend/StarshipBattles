# Phase 1: ConflictResolutionEngine

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-36 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract all combat resolution logic (~145 lines) to dedicated engine

---

## Tasks

### Task 1.1: Create ConflictResolutionEngine file [Medium]
**File:** `game/strategy/engine/conflict_resolution_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_conflict_resolution_engine.py`

- [x] Create new file with module docstring:
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
- [x] Add imports: `typing`, `dataclasses`, `random`, `game.core.logger`
- [x] Create `ConflictResult` dataclass:
  ```python
  @dataclass
  class ConflictResult:
      combats_resolved: int
      fleets_destroyed: List[int]  # fleet IDs
  ```
- [x] Create `ConflictResolutionEngine` class with `__init__(battle_resolver=None)`
- [x] Move `_generate_battle_seed` logic (TurnEngine lines 114-117)
- [x] Move `_resolve_conflicts` logic (TurnEngine lines 323-344)
- [x] Move `_resolve_combat_at_hex` logic (TurnEngine lines 346-383)
- [x] Move `_resolve_combat` logic (TurnEngine lines 385-400)
- [x] Move `_resolve_combat_simulated` logic (TurnEngine lines 402-431)
- [x] Add public method: `resolve_all_conflicts(empires) -> ConflictResult`
- [x] Verify: File follows patterns in FleetMovementEngine

**Notes:** Created `game/strategy/engine/conflict_resolution_engine.py` with all combat logic extracted from TurnEngine. Tests in `tests/unit/strategy/test_conflict_resolution_engine.py` - all 25 tests pass.

---

### Task 1.2: Update TurnEngine to delegate combat [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/test_turn_engine.py -k combat`

- [x] Add TYPE_CHECKING import for ConflictResolutionEngine
- [x] Add `_conflict_engine: Optional['ConflictResolutionEngine'] = None` to __init__
- [x] Add lazy property `conflict_engine` following pattern at lines 90-112:
  ```python
  @property
  def conflict_engine(self) -> 'ConflictResolutionEngine':
      if self._conflict_engine is None:
          from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
          self._conflict_engine = ConflictResolutionEngine(self._battle_resolver)
      return self._conflict_engine
  ```
- [x] Replace `self._resolve_conflicts(empires)` call (line 241) with:
  ```python
  self.conflict_engine.resolve_all_conflicts(empires)
  ```
- [x] Remove `_generate_battle_seed` method (lines 114-117)
- [x] Remove `_battle_seed_counter` instance variable (line 76)
- [x] Remove `_resolve_conflicts` method (lines 323-344)
- [x] Remove `_resolve_combat_at_hex` method (lines 346-383)
- [x] Remove `_resolve_combat` method (lines 385-400)
- [x] Remove `_resolve_combat_simulated` method (lines 402-431)
- [x] Remove unused `_apply_battle_results` method (lines 433-467)
- [x] Verify: TurnEngine compiles without errors

**Notes:** TurnEngine reduced from 479 to 338 lines (141 lines removed). Delegation to ConflictResolutionEngine added via lazy property. All 52 TurnEngine tests pass.

---

### Task 1.3: Create/migrate combat tests [Simple]
**File:** `tests/unit/strategy/test_conflict_resolution_engine.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_conflict_resolution_engine.py`

- [x] Create new test file with imports and fixtures from test_turn_engine.py
- [x] Move `TestCombatResolution` class tests:
  - `test_resolve_conflicts_detects_collision`
  - `test_no_conflict_same_empire`
  - `test_resolve_combat_rng_fallback_for_empty_fleet`
  - `test_resolve_combat_uses_simulation`
- [x] Move `TestBattleResolverInjection` class tests (9 methods):
  - `test_turn_engine_accepts_battle_resolver`
  - `test_turn_engine_defaults_to_simulation_resolver`
  - `test_resolve_combat_simulated_uses_injected_resolver`
  - `test_mock_resolver_enables_unit_testing`
  - `test_battle_results_applied_to_fleets`
  - `test_draw_returns_fleet_with_more_survivors`
  - `test_seed_passed_to_resolver`
  - `test_seed_counter_increments`
  - `test_seed_counter_starts_at_one`
- [x] Add test: 3+ empires simultaneous combat at same hex
- [x] Add test: Empty fleet vs fleet with ships (verify loser semantics)
- [x] Add test: Both fleets empty (RNG fallback)
- [x] Update test imports to use ConflictResolutionEngine
- [x] Verify: All tests pass with `pytest tests/unit/strategy/test_conflict_resolution_engine.py`

**Notes:** Created `tests/unit/strategy/test_conflict_resolution_engine.py` with 25 tests covering all combat resolution functionality. Removed corresponding tests from `test_turn_engine.py` since the methods no longer exist in TurnEngine. Added tests for `resolve_all_conflicts` public API.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/strategy/test_turn_engine.py` - passes (52 tests)
- [x] Run `pytest tests/unit/strategy/test_conflict_resolution_engine.py` - passes (25 tests)
- [x] Run `pytest tests/integration/` - passes (44 tests)
- [x] TurnEngine reduced by ~145 lines (479 → 338 = 141 lines removed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
