# Consistency Violations Sweep: UI-Screens

## Summary
- **Shard:** UI-Screens
- **Files Scanned:** 108
- **Total Issues Found:** 12
- **Critical:** 0 | **Major:** 5 | **Minor:** 4 | **Info:** 3

## Findings

#### MAJOR: Event Handler Naming Inconsistency (handle_event vs process_event)
**ID:** CON-UI1-001
**Location:** ~35 files with `process_event` vs ~30 files with `handle_event` (50/50 split across screens/panels)
**Issue:** Two competing naming conventions for event handling methods with nearly equal usage. Callers must remember which convention each component uses.
**Impact:** Event routing code must check both patterns. High cognitive load.
**Recommendation:** Standardize on one convention (suggest `handle_event` as it's more common in framework code). Create migration task.
**Effort:** Complex

#### MAJOR: Type Hint Coverage Inconsistency
**ID:** CON-UI1-002
**Location:** 20+ files with mixed type hint coverage (e.g., column_manager.py, fleet_report_view_model.py, builder/stats_config.py)
**Issue:** Functions with identical signatures have inconsistent type hint coverage. Some methods fully typed, others not, even within the same class.
**Impact:** Type checkers cannot verify correctness; IDE autocomplete unreliable.
**Recommendation:** Add comprehensive type hints to all public methods. Enforce with mypy.
**Effort:** Medium

#### MAJOR: Docstring Coverage Gap
**ID:** CON-UI1-003
**Location:** 15+ files in panels/ consistently lack docstrings; screens/ has mixed coverage
**Issue:** Public API methods missing docstrings (50+ methods). Panels directory consistently lacks them; screens has mixed coverage.
**Impact:** Developers cannot understand parameter meanings without reading source code.
**Recommendation:** Add Google-style docstrings to all public methods.
**Effort:** Medium

#### MAJOR: Return Type Inconsistency in Similar Functions
**ID:** CON-UI1-004
**Location:** 25+ files with mixed return patterns (None vs False vs raise for errors; bool vs tuple for click handlers)
**Issue:** Same operation returns different types across similar code. Click handlers return bool, tuple, or None inconsistently. Error handling uses None, False, or raises inconsistently.
**Impact:** Callers must remember different patterns for each method. Bug-prone.
**Recommendation:** Standardize: click handlers return bool, error operations use Optional or raise.
**Effort:** Complex

#### MAJOR: Click Handler Parameter Inconsistency
**ID:** CON-UI1-005
**Location:** battle_ui.py, strategy_input_handler.py, battle_screen.py, galaxy_test/system_mode.py, builder/layer_panel.py
**Issue:** Click handlers use different parameter names and counts: (mx, my, button), (mx, my, button, screen_size), (mx, my) with no consistency.
**Impact:** No uniform click handler contract. Each component has unique signature.
**Recommendation:** Define standard click handler protocol with consistent parameters.
**Effort:** Medium

#### MINOR: Error Handling Strategy Mixing
**ID:** CON-UI1-006
**Location:** 20+ files with mixed approaches (broad catches with comments, specific raises, silent returns)
**Issue:** Inconsistent error handling: some domains raise descriptive exceptions, some catch broadly, some fail silently with None.
**Impact:** Unpredictable error behavior across UI layer.
**Recommendation:** Define error handling policy: raise for logic errors, return None for not-found, log for non-critical.
**Effort:** Medium

#### MINOR: Class Suffix Naming Overload
**ID:** CON-UI1-007
**Location:** All screens/panels files (40+ classes)
**Issue:** Manager suffix overloaded (business logic, UI state, resource management). Mixed Screen vs Scene naming. Widget vs Panel confusion.
**Impact:** Makes class discovery harder. No clear suffix convention.
**Recommendation:** Document naming conventions: Manager=state, Service=operations, Panel=UI display, Screen=full-screen view.
**Effort:** Simple

#### MINOR: Import Organization Inconsistency
**ID:** CON-UI1-008
**Location:** ~10 files (5-10% of total) with interleaved imports
**Issue:** Most files follow stdlib → third-party → local pattern, but exceptions exist with interleaved imports.
**Impact:** Low - 90%+ compliance. Cosmetic inconsistency.
**Recommendation:** Run isort on affected files.
**Effort:** Simple

#### MINOR: Magic Numbers in UI Rendering
**ID:** CON-UI1-009
**Location:** battle_panels.py, battle_ui.py, and 10+ other files
**Issue:** Hard-coded font sizes (28, 22, 18), colors ((30, 30, 50)), and Y offsets (y += 30, y += 15) throughout rendering code.
**Impact:** Makes theme customization harder. Low correctness impact.
**Recommendation:** Extract to UIConfig constants.
**Effort:** Medium

#### INFO: Getter Method Naming Consistent
**ID:** CON-UI1-010
**Location:** All screens/panels
**Issue:** All getter methods use get_ prefix consistently (no retrieve_ or fetch_ variants found). Internally consistent.
**Impact:** None - observation only.
**Recommendation:** Document as established convention.
**Effort:** None

#### INFO: Boolean Method Naming Mostly Consistent
**ID:** CON-UI1-011
**Location:** All screens/panels
**Issue:** Boolean methods consistently use is_/has_/can_ prefixes. A few private methods could be public but naming is correct.
**Impact:** None - good compliance.
**Recommendation:** None needed.
**Effort:** None

#### INFO: Private Method Naming Edge Cases
**ID:** CON-UI1-012
**Location:** BattlePanel, ShipStatsPanel
**Issue:** Some "internal" methods that coordinate UI logic could reasonably be public. Minor naming edge cases.
**Impact:** None - functional code.
**Recommendation:** Review during next refactoring cycle.
**Effort:** None

## Top 5 Priority Issues
1. **CON-UI1-004**: Return type inconsistency - bug-prone, affects all callers
2. **CON-UI1-005**: Click handler parameter inconsistency - no uniform contract
3. **CON-UI1-001**: Event handler naming split - 50/50 split creates confusion
4. **CON-UI1-002**: Type hint coverage gaps - blocks static analysis
5. **CON-UI1-003**: Docstring coverage gaps - blocks developer productivity
