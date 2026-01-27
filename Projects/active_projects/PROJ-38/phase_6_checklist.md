# Phase 6: Cleanup & Test Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove transitional code, update test fixtures, and finalize the refactor

---

## Tasks

### Task 6.1: Create New Test Fixtures [Medium]
**File:** `tests/conftest.py`
**Tests:** `pytest tests/`

- [ ] Add `session_registries` fixture (session-scoped):
  ```python
  @pytest.fixture(scope="session")
  def session_registries() -> GameRegistries:
      """Session-scoped registries loaded once per test session."""
      cache = SessionRegistryCache.instance()
      cache.load_all_data()
      return GameRegistries(
          components=cache.get_components(),
          modifiers=cache.get_modifiers(),
          vehicle_classes=cache.get_vehicle_classes(),
          resources=cache.get_resources()
      )
  ```
- [ ] Add `fresh_registries` fixture (function-scoped, deep copies):
  ```python
  @pytest.fixture
  def fresh_registries(session_registries) -> GameRegistries:
      """Function-scoped registries with fresh copies."""
      import copy
      return GameRegistries(
          components=copy.deepcopy(session_registries.components),
          modifiers=copy.deepcopy(session_registries.modifiers),
          vehicle_classes=copy.deepcopy(session_registries.vehicle_classes),
          resources=copy.deepcopy(session_registries.resources)
      )
  ```
- [ ] Add `minimal_registries` fixture (empty, for isolated unit tests)
- [ ] Keep existing `reset_singletons` fixture during transition
- [ ] Verify: `pytest tests/` passes

**Notes:**

---

### Task 6.2: Migrate Critical Test Files [Medium]
**Files:** Various test files
**Tests:** `pytest tests/ -x`

- [ ] Update `tests/unit/builder/test_builder_ui_sync.py`:
  - Replace `SessionRegistryCache` workaround with `fresh_registries` fixture
  - Remove manual `hydrate()` calls
- [ ] Update `tests/unit/builder/test_designs.py`:
  - Inject registries via fixture instead of global `initialize_ship_data()`
- [ ] Update `tests/unit/entities/test_ship.py`:
  - Use `fresh_registries` fixture
  - Pass registries to Ship constructor
- [ ] Update `tests/unit/combat/test_combat.py`:
  - Use `fresh_registries` fixture
  - Pass registries when creating ships
- [ ] Verify: `pytest tests/ -x` passes

**Notes:**

---

### Task 6.3: Remove Transitional Code [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/`

- [ ] Remove `set_default_registries()` function
- [ ] Remove `get_default_registries()` function
- [ ] Remove `_default_registries` module variable
- [ ] Make `registries` parameter required (not Optional) in all constructors
- [ ] Update all `registries or get_default_registries()` patterns to just use `registries`
- [ ] Verify: `pytest tests/` passes

**Notes:**

---

### Task 6.4: Deprecate Old Accessor Functions [Simple]
**File:** `game/core/registry.py`
**Tests:** `pytest tests/`

- [ ] Add deprecation warnings to `get_component_registry()`:
  ```python
  def get_component_registry() -> Dict[str, Any]:
      warnings.warn("get_component_registry() is deprecated. Use GameRegistries.", DeprecationWarning)
      return RegistryManager.instance().components
  ```
- [ ] Add deprecation warnings to `get_modifier_registry()`
- [ ] Add deprecation warnings to `get_vehicle_classes()`
- [ ] Add deprecation warnings to `get_resource_registry()`
- [ ] Add deprecation warnings to `get_validator()`
- [ ] Verify: `pytest tests/` passes (warnings OK)

**Notes:** Consider removing these entirely if no external tools depend on them.

---

### Task 6.5: Remove Old Test Workarounds [Simple]
**Files:** Various conftest.py files
**Tests:** `pytest tests/`

- [ ] Evaluate if `SessionRegistryCache` is still needed (may be useful for session-scoped fixture)
- [ ] Remove manual `hydrate()` calls in test setup where replaced by fixtures
- [ ] Simplify `reset_singletons` fixture if possible
- [ ] Remove redundant cleanup in module-level conftest files
- [ ] Verify: `pytest tests/` passes

**Notes:**

---

### Task 6.6: Final Cleanup Verification [Simple]
**Tests:** Full verification

- [ ] Grep for `RegistryManager.instance()` - should only appear in registry.py or deprecated accessors
- [ ] Grep for `get_component_registry()` - should only appear in registry.py
- [ ] Grep for `get_modifier_registry()` - should only appear in registry.py
- [ ] Grep for `get_vehicle_classes()` - should only appear in registry.py
- [ ] Grep for module-level `COMPONENT_REGISTRY` - should not exist
- [ ] Grep for module-level `MODIFIER_REGISTRY` - should not exist
- [ ] Grep for module-level `VEHICLE_CLASSES` - should not exist
- [ ] Verify: All greps return expected results

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/` passes (full suite, not --testmon)
- [ ] All deprecation warnings documented
- [ ] No transitional code remains (get_default_registries removed)
- [ ] Game fully functional:
  - [ ] Main menu works
  - [ ] Design Workshop works
  - [ ] Quickstart 1P battle works
  - [ ] New game + strategy layer works
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Run final audit: `python Projects/scripts/audit_project.py PROJ-38`
