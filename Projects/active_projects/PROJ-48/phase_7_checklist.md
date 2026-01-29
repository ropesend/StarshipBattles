# Phase 7: Mock Pattern Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Establish consistent mock patterns across 3011 mock usages.
**Issues Addressed:** TSR-006, TNC-009, TNC-010

---

## Tasks

### Task 7.1: Create Mock Factory Module [Medium]
**File:** `tests/fixtures/mocks.py` (new)
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Create `tests/fixtures/mocks.py`
- [ ] Add common mock factories:
  ```python
  """
  Centralized mock factories for tests.

  Usage:
      from tests.fixtures.mocks import create_mock_ship, create_mock_component

      def test_something():
          ship = create_mock_ship(name="Test Ship")
  """
  from unittest.mock import MagicMock, Mock

  def create_mock_ship(name="MockShip", team=1, **kwargs):
      """Create a mock ship with configurable properties."""
      ship = MagicMock()
      ship.name = name
      ship.team = team
      for key, value in kwargs.items():
          setattr(ship, key, value)
      return ship

  def create_mock_component(comp_id="test_component", **kwargs):
      """Create a mock component."""
      component = MagicMock()
      component.id = comp_id
      for key, value in kwargs.items():
          setattr(component, key, value)
      return component

  def create_mock_battle_engine(**kwargs):
      """Create a mock battle engine."""
      engine = MagicMock()
      engine.ships = []
      engine.projectiles = []
      for key, value in kwargs.items():
          setattr(engine, key, value)
      return engine
  ```
- [ ] Add exports to `tests/fixtures/__init__.py`
- [ ] Document in `tests/fixtures/README.md`
- [ ] Verify: Mocks can be imported and used

**Notes:**

---

### Task 7.2: Standardize @patch Usage [Medium]
**Tests:** `pytest tests/ -v --tb=short`

- [ ] Document preferred patch pattern in `tests/README.md`:
  ```markdown
  ## Mock Patterns

  ### Preferred: Context Manager
  ```python
  from unittest.mock import patch, MagicMock

  def test_something():
      with patch('module.path.ClassName') as mock_class:
          mock_class.return_value = MagicMock()
          # test code
  ```

  ### Also Acceptable: Decorator
  ```python
  @patch('module.path.ClassName')
  def test_something(mock_class):
      # test code
  ```

  ### Avoid: Mixed styles in same file
  ```
- [ ] Identify files with mixed mock patterns
- [ ] Document findings (don't fix all - too large scope)
- [ ] Create issue/note for future cleanup

**Notes:**

---

### Task 7.3: Document Factory Function Naming [Simple]
**File:** `tests/README.md`
**Tests:** N/A - documentation only

- [ ] Add factory function naming guidelines:
  ```markdown
  ## Factory Functions

  ### Naming Convention
  - Pattern: `create_<resource>()` for factory functions
  - Example: `create_test_ship()`, `create_mock_component()`

  ### Location
  - Shared factories: `tests/fixtures/` modules
  - Test-specific factories: Within test file or conftest.py

  ### Factory vs Fixture
  - Use factory when you need custom parameters
  - Use fixture when you need consistent setup
  ```
- [ ] Review existing factories follow pattern:
  - `tests/fixtures/ships.py` - `create_test_ship()`
  - `tests/fixtures/battle.py` - `create_battle_engine()`
  - `tests/fixtures/components.py` - `create_weapon()`, etc.

**Notes:**

---

### Task 7.4: Audit Mock Class Naming [Simple]
**Tests:** N/A - audit only

- [ ] Search for inline mock classes:
  ```bash
  grep -r "class Mock" tests/ --include="test_*.py"
  ```
- [ ] List any inconsistent naming (not Mock* prefix)
- [ ] For files with many inline mocks, consider:
  - Moving to `tests/fixtures/mocks.py`
  - Creating test-specific conftest.py

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `tests/fixtures/mocks.py` created with common mock factories
- [ ] Mock patterns documented in `tests/README.md`
- [ ] Factory naming convention documented
- [ ] Mock class audit completed
- [ ] Run `pytest tests/ -v --tb=short` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8
