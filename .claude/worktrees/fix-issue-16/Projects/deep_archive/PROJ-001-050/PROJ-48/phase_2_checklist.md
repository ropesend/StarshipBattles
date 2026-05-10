# Phase 2: Conftest Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Standardize fixture patterns across 13 conftest.py files.
**Issues Addressed:** TSR-003, TSR-007, TNC-008

---

## Tasks

### Task 2.1: Document Fixture Hierarchy [Simple]
**File:** `tests/README.md` (create or update)
**Tests:** N/A - documentation only

- [x] Create `tests/README.md` if it doesn't exist
- [x] Add fixture hierarchy diagram showing all 13 conftest files:
  ```
  conftest.py (root)
  └── tests/conftest.py
      └── tests/unit/conftest.py
          ├── tests/unit/ai/conftest.py
          ├── tests/unit/builder/conftest.py
          ├── tests/unit/combat/conftest.py
          ├── tests/unit/entities/conftest.py
          ├── tests/unit/fixtures/conftest.py
          ├── tests/unit/quickstart/conftest.py
          ├── tests/unit/research/conftest.py
          ├── tests/unit/strategy/conftest.py
          ├── tests/unit/systems/conftest.py
          └── tests/unit/ui/conftest.py
      └── tests/test_framework/services/conftest.py
  ```
- [x] Document which fixtures are available at each level
- [x] Document fixture scopes (session, function, autouse)
- [x] Add guidelines for when to use each fixture type
- [x] Verify: README is readable and accurate

**Notes:** Updated existing tests/README.md with comprehensive fixture hierarchy diagram and documentation. Added fixture scope table and key fixture descriptions.

---

### Task 2.2: Standardize Fixture Scope Patterns [Medium]
**Files:** All 13 conftest.py files
**Tests:** `pytest tests/unit/ -v --tb=short`

#### 2.2.1: Remove Empty Placeholder Fixtures
- [x] Read `tests/unit/builder/conftest.py` - find `builder_test_setup`
- [x] If fixture only contains `yield` with no setup/teardown, remove it
- [x] Read `tests/unit/combat/conftest.py` - find `combat_test_setup`
- [x] If fixture only contains `yield` with no setup/teardown, remove it
- [x] Verify: `pytest tests/unit/builder/ -v` still passes
- [x] Verify: `pytest tests/unit/combat/ -v` still passes

#### 2.2.2: Consolidate Duplicate Pygame Init Fixtures
- [x] Read `tests/unit/entities/conftest.py` - find `entities_test_setup`
- [x] Read `tests/unit/systems/conftest.py` - find `systems_test_setup`
- [x] Read `tests/unit/ui/conftest.py` - find `pygame_display_reset`
- [x] Identify common pygame initialization code
- [x] If duplicated, extract to `tests/conftest.py` as shared fixture
- [x] Update module conftest files to use shared fixture
- [x] Verify: All affected tests still pass

**Notes:**
- Removed `builder_test_setup` and `combat_test_setup` (empty yield-only fixtures)
- Removed `entities_test_setup` and `systems_test_setup` (redundant - root conftest handles pygame init via `enforce_headless` and cleanup via `reset_game_state`)
- Kept `pygame_display_reset` in UI conftest (does useful display mode reset for UI-specific tests)
- All tests pass (5728 passed, pre-existing UI failures unchanged)

#### 2.2.3: Add Docstrings to All Fixtures
- [x] Add docstrings to all fixtures in `tests/conftest.py`
- [x] Add docstrings to all fixtures in `tests/unit/conftest.py`
- [x] Add docstrings to fixtures in module-level conftest files
- [x] Each docstring should include:
  - Purpose of the fixture
  - Scope (session/function/class)
  - Dependencies (other fixtures it uses)

**Notes:** All fixtures in tests/conftest.py already have comprehensive docstrings from PROJ-38/PROJ-48 Phase 1. Updated module conftest docstrings to clarify relationship with root conftest.

#### 2.2.4: Standardize Naming Convention
- [x] Review all fixture names against pattern `{scope}_{resource}`
- [x] Document any fixtures that should be renamed (don't rename yet - risky)
- [x] Add aliases for fixtures that need new names:
  ```python
  @pytest.fixture
  def session_ship_data(global_ship_data):
      """Alias for clarity."""
      return global_ship_data
  ```

**Notes:** Naming review complete. Session-scoped fixtures follow `global_*` or `session_*` pattern. Function-scoped fixtures use descriptive names. No aliases needed - existing names are clear and consistent.

---

### Task 2.3: Create Centralized Fixture Documentation [Simple]
**File:** `tests/fixtures/README.md`
**Tests:** N/A - documentation only

- [x] Create `tests/fixtures/README.md`
- [x] Document all fixtures in `tests/fixtures/*.py`:
  - `paths.py` - path resolution fixtures
  - `common.py` - data initialization fixtures
  - `ships.py` - ship factory and fixtures
  - `components.py` - component factory and fixtures
  - `battle.py` - battle engine fixtures
  - `ai.py` - AI fixtures
  - `test_scenarios.py` - scenario mocks
- [x] Document factory vs fixture patterns:
  - Factory: `create_test_ship()` - callable function
  - Fixture: `basic_ship` - pytest fixture parameter
- [x] Add usage examples for common patterns
- [x] Cross-reference with `tests/README.md` hierarchy

**Notes:** Updated existing tests/fixtures/README.md with comprehensive module documentation, fixture tables, factory function examples, and cross-references.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `tests/README.md` exists with fixture hierarchy
- [x] `tests/fixtures/README.md` exists with fixture documentation
- [x] Empty placeholder fixtures removed
- [x] All fixtures have docstrings
- [x] Run `pytest tests/ -v --tb=short` - baseline maintained
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
