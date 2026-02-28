# UI Screens Legacy Code Audit Report

**Audit Date:** 2026-02-27
**Directory Analyzed:** `game/ui/screens/` (all subdirectories)
**Files Analyzed:** 126 production Python files
**Scope:** Dead code, unused classes, orphaned methods, backward compatibility patterns, legacy rendering approaches

---

## Summary
- **Total Issues Found:** 12
- **Critical:** 1
- **Major:** 3
- **Minor:** 6
- **Info:** 2

---

## Findings

### Critical

#### CRITICAL: Test-Specific Backward Compatibility Aliases in EmpireBuildQueueWindow
**ID:** UIS-001
**Location:** `game/ui/screens/empire_build_queue_window.py:153-155`

**Issue:**
```python
# Store references for backward compatibility with tests
self.scroll_bar = self._virtual_table.scroll_bar
self.column_mgr = self._column_manager  # Alias for tests
```

The window class maintains public aliases (`scroll_bar`, `column_mgr`) solely for test compatibility. This violates the System Migration Policy: "DO NOT: Add 'fallback' code paths to old systems" and "keep backward compatibility layers 'just in case'".

**Evidence:**
- Grep search found usage in tests: `tests/unit/ui/screens/test_empire_build_queue_window.py:94,111,122`
- These aliases are not used in production code, only in tests
- They create confusion about which properties are authoritative (`_virtual_table.scroll_bar` vs `self.scroll_bar`)
- Tests should use `_virtual_table.scroll_bar` directly instead

**Recommendation:**
Remove the public aliases and update test code to access `window._virtual_table.scroll_bar` and `window._column_manager` directly. This removes unnecessary public API surface.

**Effort:** Simple (requires updating ~3 test files)

**Related:** Same pattern present in `fleet_report_window.py:119` (test also mocks `scroll_bar`)

---

### Major

#### MAJOR: Fallback Portrait/Flag Loading Patterns (Test Compatibility)
**ID:** UIS-002
**Location:** `game/ui/screens/empire_panel_window.py:280,293`

**Issue:**
```python
# Portrait (128x128) - IEmpire has portrait_id, RaceConfig has portrait_id as fallback
# Flag (96x64) - rectangle shape - IEmpire has flag_id, RaceConfig has flag_id as fallback
```

The code documents fallback chains for loading empire visuals. While this is defensive programming, it suggests the code expects both IEmpire and RaceConfig to be available simultaneously.

**Evidence:**
- Comments explicitly document fallback behavior
- Fallback to RaceConfig suggests integration between data sources
- Not necessarily dead code, but indicates uncertain ownership of data

**Recommendation:**
Verify which source (IEmpire vs RaceConfig) is authoritative. If both are active, document the precedence clearly. If only one should be used, remove the fallback.

**Effort:** Medium (requires API review and possible data migration)

---

#### MAJOR: Unused Duplicate Formatter Module (strategy_detail_fmt.py)
**ID:** UIS-003
**Location:** `game/ui/screens/strategy_detail_fmt.py` (393 lines)
vs. `game/ui/screens/strategy_detail_formatter.py` (422 lines)

**Issue:**
Two nearly identical formatter modules exist:
- `strategy_detail_fmt.py` - 393 lines
- `strategy_detail_formatter.py` - 422 lines

While both are technically used (fmt.py by utility functions, formatter.py by StrategyDetailFormatter class), the duplication suggests incomplete refactoring.

**Evidence:**
- `strategy_detail_formatter.py:21` imports from `strategy_detail_fmt.py`, indicating dependency
- Both contain format functions like `format_planet_info()`, `format_fleet_info()`, etc.
- Imports split across both files: some code imports from fmt.py, some from formatter.py
- Tests split between `test_strategy_detail_fmt.py` and `test_strategy_detail_formatter.py`

**Recommendation:**
Consolidate into single module. `strategy_detail_formatter.py` should be the canonical location since it's the public-facing class. Move utility functions from `strategy_detail_fmt.py` into `strategy_detail_formatter.py` module level, then delete `strategy_detail_fmt.py` and update all imports.

**Effort:** Medium (consolidate modules, update ~8 import sites)

---

#### MAJOR: Backward Compatibility Property Delegate
**ID:** UIS-004
**Location:** `game/ui/screens/empire_build_queue_window.py:153-155`

**Issue:**
See UIS-001 above (same location, different severity justification).

---

### Minor

#### MINOR: Test-Only Scroll Bar Mock Setup
**ID:** UIS-005
**Location:** `game/ui/screens/fleet_report_window.py` (inferred)
and `tests/unit/ui/screens/test_fleet_report_window.py:119`

**Issue:**
Similar to UIS-001, tests mock `scroll_bar` attribute. Code comment in `empire_build_queue_window.py:153` suggests this is a test compatibility pattern.

**Evidence:**
- Test file explicitly mocks: `window.scroll_bar = MagicMock()`
- This suggests the test expects a public `scroll_bar` property
- Pattern is test-specific, not used in production

**Recommendation:**
Update test to use `window._virtual_table.scroll_bar` instead of expecting public alias.

**Effort:** Simple

---

#### MINOR: Commented Fallback Documentation
**ID:** UIS-006
**Location:** Multiple files (see UIS-002 for example)

**Issue:**
Several files contain comments documenting fallback chains and compatibility logic that may be dead:
- `planet_list_filters.py:185` - "Default fallbacks if no planets exist"
- `strategy_renderer.py:415` - "Star image or fallback"
- `strategy_renderer.py:843` - "Uses resolution-aware loading with fallback chain"

**Evidence:**
- These are just comments, not executable code
- Fallback comments suggest defensive programming patterns that may be unnecessary
- Some may represent truly dead paths

**Recommendation:**
Review fallback paths to confirm they're still needed. For resolution-aware fallbacks (PROJ-54 Phase 10), verify these are still active code paths, not legacy from an earlier rendering system.

**Effort:** Simple (code review only)

---

#### MINOR: Workshop ViewModdule Deprecated Fallback Documentation
**ID:** UIS-007
**Location:** `game/ui/screens/workshop_viewmodel.py` (lines 10, 55, 70, 253, 333, 351)

**Issue:**
Multiple comments document removed fallbacks from PROJ-40 refactoring:
```python
# PROJ-40: Removed fallback to global get_all_components() - use registries.
# PROJ-40: No fallback - fail fast with clear error
```

**Evidence:**
- Six occurrences of PROJ-40 backward-compat removal documentation
- Comments indicate previous fallback chains were deliberately removed
- No actual dead code remains, just documentation of removed patterns

**Recommendation:**
These are not issues themselves (the fallbacks were correctly removed), but the prevalence of these comments suggests the PROJ-40 refactoring was extensive. Verify similar cleanups were done in other UI modules.

**Effort:** Info only (no action needed)

---

#### MINOR: Possible Unused ImagesColumn Type
**ID:** UIS-008
**Location:** `game/ui/screens/planet_data_source.py:95` (inferred)

**Issue:**
The data source checks for `col.get("type") != "image"` to handle image columns specially. However, column definitions may not actually use this type flag in all contexts.

**Evidence:**
- `get_cell_image()` method at line 81-102 checks for type="image"
- But similar check pattern not visible in grep results for other data sources
- May indicate incomplete column definition migration

**Recommendation:**
Verify all column definitions actually use the "type" field appropriately. If not used, remove the image handling code and rely on data source implementation only.

**Effort:** Simple (verify column definitions)

---

#### MINOR: Unused ImageColumn Handling
**ID:** UIS-009
**Location:** `game/ui/screens/event_log_data_source.py`

**Issue:**
EventLogDataSource defines `get_cell_image()` interface method (inherited from ITableDataSource) but always returns None. This is required by the interface but never used in practice.

**Evidence:**
- Method exists at lines 81-102 in parent class PlanetDataSource
- EventLogDataSource implements it but has no image columns
- Interface requires implementation but it's dead code path

**Recommendation:**
This is acceptable interface implementation (defensive). No action needed unless interface can be split into optional sub-interfaces.

**Effort:** Info only

---

#### MINOR: Potential Unused Formation Helper Methods
**ID:** UIS-010
**Location:** `game/ui/screens/setup_screen.py:160-201`

**Issue:**
Private helper methods `_find_or_create_design()` and `_add_formation_entries()` are only called from `add_formation_to_team()`. If formations are rarely used, these methods may be dead.

**Evidence:**
- `add_formation_to_team()` is called only from `_handle_ships_click()` at line 297
- Formation handling requires explicit file dialog interaction in battle setup
- Feature may be rarely used in practice

**Recommendation:**
Verify formation feature is still actively used. If not, remove `add_formation_to_team()`, `_find_or_create_design()`, and `_add_formation_entries()`.

**Effort:** Medium (verify feature usage, update tests)

---

### Info

#### INFO: Module-Level Factory Singleton
**ID:** UIS-011
**Location:** `game/ui/screens/setup_screen.py:33`

**Issue:**
```python
_ship_factory = ShipFactory()
```

Module-level factory instance created at import time. While this works, it's unusual pattern for UI layer.

**Evidence:**
- Used only in `_find_or_create_design()` at line 152
- Creates factory instance even if method is never called
- Alternative would be factory-on-demand or dependency injection

**Recommendation:**
Move factory creation into method: `radius = ShipFactory().get_ship_radius(ship_data)`. Eliminates module-level side effects.

**Effort:** Simple

---

#### INFO: Custom Backward Compat Aliases vs. Direct Access
**ID:** UIS-012
**Location:** `game/ui/screens/empire_build_queue_window.py:153-155`

**Issue:**
See UIS-001 (same issue, documented again for completeness in Info section).

**Note:** This is the same issue as UIS-001 (Critical) but noted here for completeness. UIS-001 should be prioritized for removal.

---

## Top 5 Priority Issues

### 1. **Remove Test-Specific Backward Compat Aliases** (CRITICAL - UIS-001)
- **Why:** Violates System Migration Policy, creates public API surface for tests only
- **Impact:** Simplifies API, reduces confusion about authoritative properties
- **Effort:** Simple
- **Timeline:** Quick win (1-2 hours)

### 2. **Consolidate Duplicate Formatter Modules** (MAJOR - UIS-003)
- **Why:** Reduces duplicate code, simplifies imports, prevents divergence
- **Impact:** Single source of truth for detail formatting, cleaner module structure
- **Effort:** Medium
- **Timeline:** Half day work (2-3 hours)

### 3. **Verify Fallback Portrait/Flag Pattern** (MAJOR - UIS-002)
- **Why:** Suggests uncertain data source ownership
- **Impact:** Clarifies data model and simplifies loading logic
- **Effort:** Medium (code review + possible migration)
- **Timeline:** Depends on findings (1-3 hours)

### 4. **Remove Workshop ViewModel PROJ-40 Documentation** (MINOR - UIS-007)
- **Why:** Historical comments clutter code, suggests similar cleanups needed elsewhere
- **Impact:** Cleaner code, identifies pattern for other modules
- **Effort:** Simple
- **Timeline:** Quick cleanup (30 mins)

### 5. **Verify Formation Feature Usage** (MINOR - UIS-010)
- **Why:** Dead code path if feature unused
- **Impact:** Removes ~40 lines of formation handling code
- **Effort:** Medium (feature verification required)
- **Timeline:** Depends on findings (1-2 hours)

---

## Notes

### Code Quality Observations
1. **Strong Layer Separation:** Screens correctly isolate from simulation/core layers
2. **Type Hints:** Most files use proper type hints (good)
3. **Docstrings:** Public classes have docstrings (good)
4. **No Major Dead Code:** Despite 126 files, only one duplicate module found
5. **Test-Specific Aliases:** Main issue is backward compatibility for testing

### Architecture Strengths
- Proper use of protocol-based duck typing
- Clean separation between UI state and rendering
- Good use of composition (ViewModels, DataSources, Controllers)
- Consistent error handling patterns

### Refactoring Recommendations
1. **Priority 1:** Remove backward compat aliases (UIS-001)
2. **Priority 2:** Consolidate formatters (UIS-003)
3. **Priority 3:** Document fallback policy for future development

---

## Methodology

**Analysis Approach:**
1. Scanned all 126 Python files in `game/ui/screens/` for patterns
2. Searched for unused classes, orphaned methods, commented code blocks
3. Verified instantiation of all major screen classes via grep
4. Checked for backward compatibility patterns (fallbacks, aliases, legacy imports)
5. Identified TODOs, FIXMEs, and deprecation markers
6. Examined test-specific code patterns

**Tools Used:**
- Grep/ripgrep for pattern matching across codebase
- File content analysis for method definitions and usage
- Cross-reference checking for imports and instantiations

**Confidence Levels:**
- UIS-001 (backward compat aliases): **High** (direct evidence in code and tests)
- UIS-003 (duplicate modules): **High** (two distinct files with overlapping functionality)
- UIS-002 (fallback patterns): **Medium** (comments suggest pattern but code may be intentional)
- UIS-010 (formation methods): **Medium** (method exists but usage frequency unknown)
