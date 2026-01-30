# Phase 7: Mock Pattern Standardization

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Establish consistent mock patterns across 3011 mock usages.
**Issues Addressed:** TSR-006, TNC-009, TNC-010

---

## Tasks

### Task 7.1: Create Mock Factory Module [Medium]
**File:** `tests/fixtures/mocks.py` (new)
**Tests:** `pytest tests/ -v --tb=short`

- [x] ~~Create `tests/fixtures/mocks.py`~~ **DECISION:** Not needed - mock factories already exist in domain-specific modules
- [x] ~~Add common mock factories~~ **EXISTING:** `battle.py` has `create_mock_battle_engine()`, `create_mock_battle_screen()`; `test_scenarios.py` has 4 mock factories
- [x] ~~Add exports to `tests/fixtures/__init__.py`~~ Already exports mock factories from domain modules
- [x] Document mock factory organization in `tests/fixtures/README.md`
- [x] Verified: All existing mock factories are importable and work

**Notes:** Better design decision: mock factories co-located with related fixtures (domain cohesion). Created documentation explaining this pattern in fixtures README.

---

### Task 7.2: Standardize @patch Usage [Medium]
**Tests:** `pytest tests/ -v --tb=short`

- [x] Document preferred patch pattern in `tests/README.md` - Added "Mock Patterns" section
- [x] Identify files with mixed mock patterns:
  - @patch decorator: 152 occurrences across 24 files
  - with patch() context manager: 237 occurrences across 54 files
  - Both patterns are acceptable, documented guidelines for consistency within files
- [x] Document findings in README (both patterns acceptable, prefer consistency within file)
- [x] No cleanup needed - existing usage is reasonable

**Notes:** Both patch styles are used appropriately. Context managers for localized patches, decorators for whole-function patches. Documented guidelines in README.

---

### Task 7.3: Document Factory Function Naming [Simple]
**File:** `tests/README.md`
**Tests:** N/A - documentation only

- [x] Add factory function naming guidelines to `tests/README.md`
- [x] Review existing factories follow pattern:
  - `tests/fixtures/ships.py` - `create_test_ship()` ✓
  - `tests/fixtures/battle.py` - `create_battle_engine()`, `create_mock_battle_engine()` ✓
  - `tests/fixtures/components.py` - `create_weapon()`, etc. ✓
  - `tests/fixtures/test_scenarios.py` - `create_mock_test_*()` ✓

**Notes:** All existing factories follow naming conventions. Pattern documented: `create_<resource>()` for real objects, `create_mock_<resource>()` for mocks.

---

### Task 7.4: Audit Mock Class Naming [Simple]
**Tests:** N/A - audit only

- [x] Search for inline mock classes: Found 52 inline mock classes
- [x] List any inconsistent naming: **None found** - all use `Mock*` prefix
- [x] Evaluation: Mock classes are appropriately scoped to their test files

**Notes:** All 52 inline mock classes follow `Mock*` naming convention. Examples: `MockEventBus`, `MockFleetOrdersWindow`, `MockDropTarget`, `MockComponent`, etc. No consolidation needed.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] ~~`tests/fixtures/mocks.py` created~~ Decision: Not needed, documented rationale
- [x] Mock patterns documented in `tests/README.md`
- [x] Factory naming convention documented
- [x] Mock class audit completed
- [x] Run `pytest tests/ -v --tb=short` - 5746 passed (pre-existing failures excluded)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 8
