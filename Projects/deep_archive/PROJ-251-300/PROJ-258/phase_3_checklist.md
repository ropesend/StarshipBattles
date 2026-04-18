# Phase 3: Migrate AI + Strategy Singletons

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-258 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the single AI-layer singleton (StrategyManager) to ApplicationContext.

---

## Tasks

### Task 3.1: Migrate StrategyManager [Medium]
**Singleton file:** `game/ai/strategy_manager.py`
**Production .instance() call sites (3):**
- `game/ai/strategy_manager.py:34` -- docstring example
- `game/ai/controller.py:110` -- `StrategyManager.instance().resolve_strategy(strategy_id)`
- `game/ui/screens/workshop_data_loader.py:183` -- `StrategyManager.instance()`

**Test files that reset StrategyManager:**
- `tests/unit/ai/test_strategy_system.py` -- 3 `.reset()` calls
- `tests/unit/ai/test_strategy_manager_singleton.py` -- 3 `.reset()` calls
- `tests/integration/ai_strategy/conftest.py` -- uses `.instance()` and `.clear()` in autouse fixture

**SessionRegistryCache dependency:**
- `tests/infrastructure/session_cache.py:67-71` -- loads strategies via `StrategyManager.instance()`

**TDD steps:**
- [ ] Write test: StrategyManager can be instantiated without SingletonMeta
- [ ] Write test: ApplicationContext provides StrategyManager instance
- [ ] Write test: StrategyManager receives StrategyMetadataService via constructor (not `.instance()`)
- [ ] Remove `metaclass=SingletonMeta` from StrategyManager class definition
- [ ] Add `strategy_metadata` parameter to StrategyManager.__init__() for DI of StrategyMetadataService
- [ ] Update `StrategyManager.clear()` to use injected StrategyMetadataService reference
- [ ] Update `StrategyManager.load_data()` to use injected StrategyMetadataService reference
- [ ] Update `game/ai/controller.py:110` -- AIController needs StrategyManager via DI
  - AIController already receives dependencies in `__init__`; add `strategy_manager` parameter
  - Update `AIControllerFactory` to pass StrategyManager when creating controllers
- [ ] Update `game/ui/screens/workshop_data_loader.py:183` to receive StrategyManager via context
- [ ] Update `game/context.py` `create_production()`:
  - Create StrategyMetadataService first
  - Create StrategyManager with `strategy_metadata=strategy_metadata_instance`
- [ ] Update `tests/unit/ai/test_strategy_system.py` to use fresh instances
- [ ] Update `tests/unit/ai/test_strategy_manager_singleton.py` to use fresh instances
  - Note: singleton-specific tests may need to be rewritten or removed
- [ ] Update `tests/integration/ai_strategy/conftest.py` setup_game_data fixture
- [ ] Update `tests/infrastructure/session_cache.py` StrategyManager usage
- [ ] Run: `pytest tests/unit/ai/ -v` -- all pass
- [ ] Run: `pytest tests/integration/ai_strategy/ -v` -- all pass
- [ ] Run: `python Tools/test_sharded/test_sharded.py` -- 14783+ pass
- [ ] Commit: "refactor: migrate StrategyManager from singleton to DI via ApplicationContext"

**Notes:** StrategyManager currently imports StrategyMetadataService at module level and accesses it via `.instance()`. After migration, StrategyManager receives a StrategyMetadataService reference in its constructor. The `_data_lock` threading.Lock for thread-safe loading should be kept as an instance attribute (not class-level).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] StrategyManager no longer uses SingletonMeta
- [ ] StrategyManager receives StrategyMetadataService via constructor DI
- [ ] AIController receives StrategyManager via DI
- [ ] Full test suite passes (14783+ tests, 0 failures)
- [ ] 1 commit for StrategyManager migration
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
