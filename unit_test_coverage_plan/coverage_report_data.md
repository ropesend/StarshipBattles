# Data & Infrastructure Coverage Audit Report

## 1. Coverage Summary

The Data and Infrastructure layer (`ship_io.py`, `ship_validator.py`, `resources.py`) deals with persistence, data integrity, and resource management.

*   **`resources.py`**: **High Coverage (90%)**. Core logic, caching, and ship integration are well tested in `test_resources.py` and `test_ship_resources.py`.
*   **`ship_validator.py`**: **Medium Coverage (60%)**. Basic structural rules (Layers, unique items, mass) are tested in `test_builder_validation.py`. Complex design rules (class requirements, resource dependencies) are **completely untested**.
*   **`ship_io.py`**: **Low Coverage (10%)**. Explicit tests for `load_ship`/`save_ship` methodology (dialogs, error handling) are missing. Tests rely on `Ship.from_dict` directly, bypassing the IO controller.

## 2. Missing Tests (Coverage Gaps)

### A. interactive I/O (`ship_io.py`)
The `ShipIO` class uses `tkinter.filedialog` and direct file access. These paths are not tested.
*   **Gap:** `save_ship` handling of permissions errors or invalid filenames.
*   **Gap:** `save_ship` output verification (ensuring it actually writes valid JSON to the target path).
*   **Gap:** `load_ship` handling of "File Not Found" or corrupt JSON.
*   **Gap:** `load_ship` version warnings (legacy attribute checks).

### B. Complex Validation Rules (`ship_validator.py`)
`test_builder_validation.py` covers component addition constraints well, but misses whole-design checks.
*   **Gap:** `ClassRequirementsRule`: Not tested. We need to verify that a ship with insufficient Crew or Life Support generates specific `errors` in the validation result.
*   **Gap:** `ResourceDependencyRule`: Not tested. We need to verify that a ship with weapons (ammo consumers) but no Ammo Storage generates `warnings`.
*   **Gap:** `LayerRestrictionDefinitionRule`: "Allow" vs "Block" logic is complex. We should add edge cases for conflicting rules.

### C. Resource Edge Cases (`resources.py`)
*   **Gap:** `reset_stats`: ensuring max values reset but current values persist (crucial for game state).

## 3. Plan to Reach 100% Coverage

To achieve 100% coverage, we will create/extend the following test files:

### 1. `unit_tests/test_io_interactive.py` (New)
*   **Test:** `test_save_ship_success`: Mock `filedialog.asksaveasfilename` and `open`. Verify `json.dump` is called with correct data.
*   **Test:** `test_save_ship_failure`: Mock `open` to raise PermissionError. Verify method returns `(False, "Save failed: ...")`.
*   **Test:** `test_load_ship_corrupt`: Mock `open` to return invalid JSON string. Verify `(None, "Load failed: ...")`.
*   **Test:** `test_load_ship_stats_correction`: Load a ship with legacy stats (mocked). Verify `_loading_warnings` are captured in the return message.

### 2. Extend `unit_tests/test_builder_validation.py`
*   **Task:** Add `test_class_requirements_validation`:
    *   Create ship with `CrewRequired=10` (via components) but `CrewCapacity=0`. Assert validator returns error "Need 10 more crew housing".
*   **Task:** Add `test_resource_dependency_validation`:
    *   Create ship with a Fuel Consumer (Engine) but no Fuel Storage. Assert validator returns warning "Needs Fuel Storage".

### 3. Extend `unit_tests/test_resources.py`
*   **Task:** Add `test_reset_stats_persistence`:
    *   Set `current_value = 50`. Call `reset_stats`. Verify `max_value` is 0 but `current_value` remains 50.

## 4. Prioritization
1.  **High**: `test_builder_validation.py` extensions (Critical for Builder stability).
2.  **Medium**: `test_io_interactive.py` (Important for user experience, but lower implementation risk).
3.  **Low**: `test_resources.py` (Already well covered).
