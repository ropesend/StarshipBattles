# Dead Code Hunter Report

## Summary
- **Total issues found:** 12
- **Critical:** 1, **Major:** 4, **Minor:** 6, **Info:** 1

---

## Findings

### CRITICAL: Unused Import in Core Logger
**ID:** DC-001
**Location:** `game/core/logger.py:2`
**Issue:** Import `sys` is declared but never used in the module.
**Impact:** Code cleanliness; unused imports increase cognitive load.
**Recommendation:** Remove the unused `import sys` statement.
**Effort:** Simple

### MAJOR: Deprecated Builder Screen - Maintenance Burden
**ID:** DC-002
**Location:** `game/ui/screens/builder_screen.py:1-156`
**Issue:** Entire file marked as "DEPRECATED" with 144 lines of backward compatibility wrapper code.
**Impact:** Doubles testing surface, confuses new developers, maintains two parallel interfaces.
**Recommendation:** Migrate all remaining usages to `DesignWorkshopGUI` and delete builder_screen.py.
**Effort:** Medium

### MAJOR: Commented Console Handler in Logger
**ID:** DC-003
**Location:** `game/core/logger.py:38`
**Issue:** Commented-out console handler - dead code from previous implementation.
**Impact:** Code noise; suggests incomplete refactoring.
**Recommendation:** Remove the commented line entirely.
**Effort:** Simple

### MAJOR: Commented Component Type Note
**ID:** DC-004
**Location:** `game/simulation/entities/ship_physics.py:4`
**Issue:** Comment about removed imports is a refactoring artifact.
**Impact:** Creates confusion; belongs in git history, not code.
**Recommendation:** Remove the explanatory comment.
**Effort:** Simple

### MAJOR: Stub Implementation in Component Validation
**ID:** DC-005
**Location:** `game/simulation/components/component.py:535-538`
**Issue:** Method `_apply_custom_stats()` contains only a `pass` statement.
**Impact:** Creates confusion about incomplete functionality.
**Recommendation:** Either implement the method or remove it entirely.
**Effort:** Medium

### Minor: Incomplete Arrow Button Implementation
**ID:** DC-006
**Location:** `game/ui/panels/system_tree_panel.py:95-97`
**Issue:** Method `set_position()` contains `pass` statement inside conditional block.
**Impact:** If arrow buttons are ever shown, positioning won't update.
**Recommendation:** Implement arrow position logic or remove conditional block.
**Effort:** Medium

### Minor: Orphaned Test Artifacts
**ID:** DC-007
**Location:** `Debugging/Marked_for_Deletion_2026-01-20/` (6 files)
**Issue:** Directory contains 6 debug/test scripts marked for deletion but still in repository.
**Impact:** Repository clutter; creates confusion about current debugging procedures.
**Recommendation:** Delete the entire directory.
**Effort:** Simple

### Minor: Unreachable Code Block
**ID:** DC-008
**Location:** `game/ui/screens/planet_list_window.py:779-780`
**Issue:** Duplicate line: `btn.set_text(f"{t}")` appears twice in succession.
**Impact:** Dead code; inefficiency in update loop.
**Recommendation:** Remove the duplicate line.
**Effort:** Simple

### Minor: Incomplete Hex Ring Algorithm Documentation
**ID:** DC-009
**Location:** `game/strategy/data/hex_math.py:109-131`
**Issue:** Incomplete commented explanations about the algorithm.
**Impact:** Creates false impression of work-in-progress.
**Recommendation:** Replace comments with clear docstring.
**Effort:** Simple

### Minor: Pre-Calculation Comments Not Maintained
**ID:** DC-011
**Location:** `game/simulation/entities/ship_physics.py:27-44`
**Issue:** Extensive inline comments with rhetorical questions indicate exploratory development.
**Impact:** Code clarity reduced.
**Recommendation:** Convert comments to clear docstring, remove rhetorical questions.
**Effort:** Simple

### Info: PresetManager Deprecation Not Complete
**ID:** DC-012
**Location:** `game/ui/screens/builder_screen.py:23`, `game/ui/screens/planet_list_window.py:32`
**Issue:** "PresetManager removed" comment but PresetManager still used in planet_list_window.py.
**Impact:** Inconsistent API; confusion about what's deprecated.
**Recommendation:** Complete the PresetManager deprecation or clarify status.
**Effort:** Complex

---

## Top 5 Priority Issues

1. **DC-002**: Delete builder_screen.py deprecated wrapper - 144 lines of pure overhead
2. **DC-001**: Remove unused `sys` import in logger.py
3. **DC-007**: Clean up Debugging/Marked_for_Deletion_2026-01-20/ directory
4. **DC-005**: Remove or implement `_apply_custom_stats()` stub
5. **DC-003**: Remove commented console handler in logger.py

---

## Code Quality Metrics

- **Total codebase**: ~44,000 lines in game/ directory
- **Deprecated/stub code**: ~200+ lines identified
- **Dead code percentage**: ~0.5% of active game code
- **Maintenance burden**: Moderate; primarily in UI layer and test artifacts
