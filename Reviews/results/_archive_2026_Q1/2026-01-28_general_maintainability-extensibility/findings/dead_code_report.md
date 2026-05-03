# Dead Code Review Report

## Summary
- **Total issues found:** 11
- **Critical:** 2
- **Major:** 4
- **Minor:** 4
- **Info:** 1

---

## Findings

### CRITICAL: Broken Import References in Main Application
**ID:** DC-01
**Location:** `game/app.py:28-29`
**Issue:** App imports non-existent modules:
```python
from Tools.formation_editor import FormationEditorScene
from ui.test_lab_scene import TestLabScene
```
These modules don't exist at the referenced paths.
**Impact:** Runtime ImportError will occur if TEST_LAB or FORMATION states are activated.
**Recommendation:** Update imports to correct paths or move modules into proper game package structure.
**Effort:** Simple

### CRITICAL: Backup File Committed to Repository
**ID:** DC-02
**Location:** `ui/test_lab_scene.py.backup`
**Issue:** A 2,731-line backup file of test_lab_scene.py is committed alongside the active version.
**Impact:** Increases repo size, creates confusion about which version is active.
**Recommendation:** Delete the `.backup` file. Use git history if older version is needed.
**Effort:** Simple

### MAJOR: Marked-for-Deletion Directory Unresolved
**ID:** DC-03
**Location:** `./_marked_for_deletion_2026-01-27/`
**Issue:** Entire directory marked for deletion but still in the repository.
**Impact:** Clutters repo, indicates incomplete cleanup.
**Recommendation:** Delete the entire directory or properly archive.
**Effort:** Simple

### MAJOR: Incorrect Import Path for TestLabScene
**ID:** DC-04
**Location:** `game/app.py:29` / Actual module at `ui/test_lab_scene.py`
**Issue:** app.py imports from `ui.test_lab_scene` but ui/ is outside the game package.
**Impact:** Import will fail at runtime when TEST_LAB state is accessed.
**Recommendation:** Move `ui/` into `game/ui/screens/` or create proper import path handling.
**Effort:** Medium

### MAJOR: Incorrect Import Path for FormationEditorScene
**ID:** DC-05
**Location:** `game/app.py:28` / Actual module at `Tools/formation_editor.py`
**Issue:** app.py imports from `Tools.formation_editor` but Tools/ is outside game package.
**Impact:** Import will fail at runtime when FORMATION state is accessed.
**Recommendation:** Move Tools into proper package structure or fix import paths.
**Effort:** Medium

### MAJOR: Empty Init Files - Incomplete Package Setup
**ID:** DC-06
**Location:** Multiple `__init__.py` files (14 files with 0 lines)
**Issue:** Empty __init__.py files without package-level exports for cleaner imports.
**Impact:** Forces deep import paths, makes package exports unclear.
**Recommendation:** Add meaningful __all__ exports or remove unnecessary package structure.
**Effort:** Medium

### MINOR: Unused Backward Compatibility Path Exports
**ID:** DC-07
**Location:** `game/core/paths.py:89-98`
**Issue:** Module exports old-style path constants for backward compatibility that duplicate the Paths class API.
**Impact:** Code duplication, confusing API surface.
**Recommendation:** Migrate all uses to `Paths.` class API. Remove once converted.
**Effort:** Simple

### MINOR: Unused Path Constants
**ID:** DC-08
**Location:** `game/core/paths.py:59-60, 98`
**Issue:** `VEHICLE_CLASSES_FILE` and `VEHICLE_LAYERS_FILE` defined but rarely used in active code.
**Impact:** Dead API surface.
**Recommendation:** Verify not needed; remove or consolidate.
**Effort:** Simple

### MINOR: Duplicate Imports in constants.py
**ID:** DC-09
**Location:** `game/core/constants.py:1-9, 31-53`
**Issue:** File imports from enum twice. Also re-exports from Paths duplicating paths.py.
**Impact:** Code redundancy.
**Recommendation:** Clean up duplicate imports, consolidate re-exports.
**Effort:** Simple

### MINOR: Legacy Comment Marker
**ID:** DC-10
**Location:** `game/ui/screens/test_lab.py:88-100`
**Issue:** Commented-out code block with notes about removed functionality.
**Impact:** Minor - shows incomplete cleanup from refactoring.
**Recommendation:** Remove once surrounding code is stable.
**Effort:** Simple

### INFO: Debugging Scripts Not Integrated
**ID:** DC-11
**Location:** `Debugging/archive_confirmed.py`, `Debugging/confirm_bugs_ui.py`
**Issue:** Debug automation scripts exist but aren't integrated into CI pipeline.
**Impact:** Unused tooling.
**Recommendation:** Integrate into debug workflow or remove if not needed.
**Effort:** Simple

---

## Top 5 Priority Issues

1. **DC-01: Broken Imports in game/app.py** - Will cause immediate runtime failures

2. **DC-02: Backup File Committed** - Quick win: delete backup file

3. **DC-04/DC-05: Incorrect Import Paths** - Fix requires architectural decision about package structure

4. **DC-03: Marked-for-Deletion Directory** - Quick win: delete entire directory

5. **DC-06: Empty __init__.py Files** - Consolidate package structure for better imports
