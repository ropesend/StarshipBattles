# Phase 2: Conftest Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Standardize fixture patterns across 13 conftest.py files.
**Issues Addressed:** TSR-003, TSR-007, TNC-008

---

## Tasks

### Task 2.1: Document Fixture Hierarchy [Simple]
**File:** `tests/README.md` (create or update)
**Tests:** N/A - documentation only

- [ ] Create `tests/README.md` if it doesn't exist
- [ ] Add fixture hierarchy diagram showing all 13 conftest files:
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
- [ ] Document which fixtures are available at each level
- [ ] Document fixture scopes (session, function, autouse)
- [ ] Add guidelines for when to use each fixture type
- [ ] Verify: README is readable and accurate

**Notes:**

---

### Task 2.2: Standardize Fixture Scope Patterns [Medium]
**Files:** All 13 conftest.py files
**Tests:** `pytest tests/unit/ -v --tb=short`

#### 2.2.1: Remove Empty Placeholder Fixtures
- [ ] Read `tests/unit/builder/conftest.py` - find `builder_test_setup`
- [ ] If fixture only contains `yield` with no setup/teardown, remove it
- [ ] Read `tests/unit/combat/conftest.py` - find `combat_test_setup`
- [ ] If fixture only contains `yield` with no setup/teardown, remove it
- [ ] Verify: `pytest tests/unit/builder/ -v` still passes
- [ ] Verify: `pytest tests/unit/combat/ -v` still passes

#### 2.2.2: Consolidate Duplicate Pygame Init Fixtures
- [ ] Read `tests/unit/entities/conftest.py` - find `entities_test_setup`
- [ ] Read `tests/unit/systems/conftest.py` - find `systems_test_setup`
- [ ] Read `tests/unit/ui/conftest.py` - find `pygame_display_reset`
- [ ] Identify common pygame initialization code
- [ ] If duplicated, extract to `tests/conftest.py` as shared fixture
- [ ] Update module conftest files to use shared fixture
- [ ] Verify: All affected tests still pass

#### 2.2.3: Add Docstrings to All Fixtures
- [ ] Add docstrings to all fixtures in `tests/conftest.py`
- [ ] Add docstrings to all fixtures in `tests/unit/conftest.py`
- [ ] Add docstrings to fixtures in module-level conftest files
- [ ] Each docstring should include:
  - Purpose of the fixture
  - Scope (session/function/class)
  - Dependencies (other fixtures it uses)

#### 2.2.4: Standardize Naming Convention
- [ ] Review all fixture names against pattern `{scope}_{resource}`
- [ ] Document any fixtures that should be renamed (don't rename yet - risky)
- [ ] Add aliases for fixtures that need new names:
  ```python
  @pytest.fixture
  def session_ship_data(global_ship_data):
      """Alias for clarity."""
      return global_ship_data
  ```

**Notes:**

---

### Task 2.3: Create Centralized Fixture Documentation [Simple]
**File:** `tests/fixtures/README.md`
**Tests:** N/A - documentation only

- [ ] Create `tests/fixtures/README.md`
- [ ] Document all fixtures in `tests/fixtures/*.py`:
  - `paths.py` - path resolution fixtures
  - `common.py` - data initialization fixtures
  - `ships.py` - ship factory and fixtures
  - `components.py` - component factory and fixtures
  - `battle.py` - battle engine fixtures
  - `ai.py` - AI fixtures
  - `test_scenarios.py` - scenario mocks
- [ ] Document factory vs fixture patterns:
  - Factory: `create_test_ship()` - callable function
  - Fixture: `basic_ship` - pytest fixture parameter
- [ ] Add usage examples for common patterns
- [ ] Cross-reference with `tests/README.md` hierarchy

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `tests/README.md` exists with fixture hierarchy
- [ ] `tests/fixtures/README.md` exists with fixture documentation
- [ ] Empty placeholder fixtures removed
- [ ] All fixtures have docstrings
- [ ] Run `pytest tests/ -v --tb=short` - baseline maintained
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
