# Phase 2: TurnEngine Config Object

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-259 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create a `TurnEngineConfig` frozen dataclass to bundle the 13 optional engine parameters of `TurnEngine.__init__()`, reducing constructor parameters from 20 to 5. Update all 85 `TurnEngine()` call sites across 24 files.

---

## Tasks

### Task 2.1: Write Tests for TurnEngineConfig [Simple]
**File:** `tests/unit/strategy/engine/test_turn_engine_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine_config.py`

- [ ] Create test file `tests/unit/strategy/engine/test_turn_engine_config.py`
- [ ] Test: default TurnEngineConfig has all fields as None
- [ ] Test: TurnEngineConfig is frozen (assignment raises FrozenInstanceError)
- [ ] Test: TurnEngineConfig accepts mock engine values for each field
- [ ] Test: TurnEngineConfig with partial fields (only some engines specified)
- [ ] Test: TurnEngine accepts config parameter and extracts engines correctly
- [ ] Test: TurnEngine with config=None behaves identically to current default behavior
- [ ] Test: TurnEngine with config containing mock engines uses those engines (not defaults)
- [ ] Test: create_default_turn_engine() accepts optional config parameter
- [ ] Run tests -- confirm all fail (no implementation yet)

**Notes:** These tests verify the new interface. Existing TurnEngine tests in `tests/unit/strategy/turn_engine/` verify behavior is unchanged.

---

### Task 2.2: Implement TurnEngineConfig Dataclass [Simple]
**File:** `game/strategy/engine/turn_engine_config.py` (NEW)
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine_config.py`

- [ ] Create `game/strategy/engine/turn_engine_config.py`
- [ ] Define `TurnEngineConfig` as `@dataclass(frozen=True)` with 13 Optional fields, all defaulting to None
- [ ] Fields: `movement_engine`, `production_engine`, `order_processor`, `conflict_engine`, `resource_engine`, `population_engine`, `resupply_engine`, `harvesting_engine`, `action_engine`, `environmental_engine`, `planet_energy_engine`, `planet_action_engine`, `component_activation_engine`
- [ ] Add TYPE_CHECKING imports for all engine interface types from `game/strategy/interfaces/engines.py`
- [ ] Add docstring explaining frozen semantics and None-means-default convention
- [ ] Run config-specific tests -- confirm they pass

**Notes:** This is a pure data class with no logic.

---

### Task 2.3: Add config Parameter to TurnEngine Constructor [Medium]
**File:** `game/strategy/engine/turn_engine.py` (lines 132-211)
**Tests:** `pytest tests/unit/strategy/engine/test_turn_engine_config.py` + `pytest tests/unit/strategy/turn_engine/`

- [ ] Add `config: Optional[TurnEngineConfig] = None` keyword parameter to `TurnEngine.__init__()` (after registries, before ai_factory)
- [ ] At the top of `__init__()`: `cfg = config or TurnEngineConfig()`
- [ ] Initialize all 13 engine fields from `cfg.*` instead of individual kwargs
- [ ] Keep individual kwargs temporarily with deprecation comment: if both config and individual kwargs are provided, individual kwargs take precedence (allows incremental migration)
- [ ] Update `create_default_turn_engine()` (line 637) to accept optional `config` parameter and pass it through
- [ ] Run all turn engine tests: `pytest tests/unit/strategy/turn_engine/ tests/integration/strategy/turn_engine/`
- [ ] Verify no behavior changes

**Notes:** This task adds the new interface while keeping backward compatibility. Task 2.4 migrates callers.

---

### Task 2.4: Migrate All TurnEngine Call Sites [Complex]
**Files:** 24 files containing 85 `TurnEngine()` calls
**Tests:** `python Tools/test_sharded/test_sharded.py`

Production code (2 files):
- [ ] `game/strategy/engine/game_session.py` line 91: `TurnEngine(registries=..., ai_factory=..., event_bus=...)` -- no engines injected, no change needed (uses defaults)
- [ ] `game/strategy/engine/game_session.py` line 327: same pattern -- no change needed

Test conftest files (4 files):
- [ ] `tests/unit/strategy/turn_engine/conftest.py` line 26: `TurnEngine(registries=fresh_registries, ai_factory=MagicMock())` -- no engines injected, no change needed
- [ ] `tests/integration/gameplay_loop/conftest.py` line 62: check if engines are injected -- update if so
- [ ] `tests/integration/colonization/conftest.py` line 92: check if engines are injected -- update if so
- [ ] `tests/integration/strategy/production/conftest.py` line 103: check if engines are injected -- update if so

DI test file (primary migration target):
- [ ] `tests/unit/strategy/turn_engine/test_dependency_injection.py` -- 12 `TurnEngine()` calls. Migrate any that pass individual engine kwargs to use `config=TurnEngineConfig(...)` instead
- [ ] `tests/unit/strategy/mocks/mock_engines.py` line 13: update example comment

Integration test files (update if they inject engines):
- [ ] `tests/integration/test_complex_workflow.py` -- 5 calls
- [ ] `tests/integration/strategy/turn_engine/test_basics.py` -- 5 calls
- [ ] `tests/integration/strategy/turn_engine/test_resupply.py` -- 5 calls
- [ ] `tests/integration/strategy/turn_engine/test_resources.py` -- 14 calls
- [ ] `tests/integration/strategy/turn_engine/test_harvesting.py` -- 4 calls
- [ ] `tests/integration/strategy/turn_engine/test_components.py` -- 6 calls
- [ ] `tests/integration/strategy/test_turn_storms.py` -- 4 calls
- [ ] `tests/integration/strategy/test_resupply_system.py` -- 4 calls
- [ ] `tests/integration/strategy/test_commands.py` -- 4 calls
- [ ] `tests/integration/strategy/test_economy_e2e.py` -- 1 call
- [ ] `tests/integration/strategy/test_fleet_navigation_consistency.py` -- 1 call
- [ ] `tests/integration/resource_system/test_resource_pipeline.py` -- 2 calls
- [ ] `tests/unit/strategy/engine/test_population_engine.py` -- 1 call
- [ ] `tests/unit/strategy/engine/test_environmental_hazard_engine.py` -- 4 calls
- [ ] `tests/unit/strategy/test_advanced_fleet_orders.py` -- 1 call
- [ ] `tests/unit/strategy/turn_engine/test_turn_processing.py` -- 1 call

**Notes:** Most call sites do NOT inject individual engines (they use defaults). Only `test_dependency_injection.py` and possibly a few integration tests inject mock engines. For call sites that don't inject engines, no change is needed. For call sites that do inject engines, wrap the engine kwargs in `config=TurnEngineConfig(...)`.

---

### Task 2.5: Remove Deprecated Individual Engine Kwargs [Simple]
**File:** `game/strategy/engine/turn_engine.py` (lines 132-183)
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Remove all 13 individual engine keyword parameters from `TurnEngine.__init__()`
- [ ] Remove the precedence/fallback logic added in Task 2.3
- [ ] Final constructor signature: `__init__(self, battle_resolver, *, registries, config=None, ai_factory=None, event_bus=None)`
- [ ] Update docstring module header (lines 1-57) to reflect new constructor signature
- [ ] Update `create_default_turn_engine()` docstring
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify TurnEngine constructor now has 5 parameters (battle_resolver, registries, config, ai_factory, event_bus)

**Notes:** Only do this after ALL callers are migrated in Task 2.4. Any missed caller will fail immediately (TypeError from unexpected kwargs).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `TurnEngineConfig` exists in `game/strategy/engine/turn_engine_config.py`
- [ ] `TurnEngine.__init__()` has 5 parameters: battle_resolver, registries, config, ai_factory, event_bus
- [ ] No individual engine kwargs remain in `TurnEngine.__init__()`
- [ ] All tests pass: `python Tools/test_sharded/test_sharded.py`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
