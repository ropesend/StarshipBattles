# Dead Code Hunter Report

## Summary
- Total issues found: 27
- Critical: 3, Major: 9, Minor: 10, Info: 5

## Findings

### CRITICAL: Legacy Migration Scripts in docs/_legacy_docs/Tools/
**ID:** DC-001
**Location:** `docs/_legacy_docs/Tools/*.py` (10 files, ~35KB)
**Issue:** One-time migration scripts from old refactoring phases: fix_modifiers.py, migrate_data.py, refactor_phase2-6b.py.
**Impact:** Never executed, serve no purpose. Creates confusion about active tools.
**Deliberate?:** No - retained "just in case" but migrations already applied.
**Recommendation:** Delete entire docs/_legacy_docs/Tools/ directory.
**Effort:** Simple

### CRITICAL: Duplicate formatimg.py Scripts in Asset Folders
**ID:** DC-002
**Location:** `assets/ShipThemes/*/Origonal Art/*/formatimg.py` (5 identical files, 80 lines each)
**Issue:** Five copies of same image processing script scattered across ship theme folders. Not part of game runtime.
**Impact:** Duplication, confusion.
**Deliberate?:** No - left behind from manual asset processing.
**Recommendation:** Delete all 5 copies. If needed, create one in scripts/.
**Effort:** Simple

### CRITICAL: Orphaned test_framework/ Directory (~338KB)
**ID:** DC-003
**Location:** `test_framework/` (17 Python files)
**Issue:** Legacy test framework superseded by simulation_tests/. Only 4 files in game/ import it (all in test_lab UI). No actual tests use it.
**Impact:** Large legacy framework, potential confusion.
**Deliberate?:** Partially - kept for Test Lab UI compatibility.
**Recommendation:** Audit if Test Lab can use simulation_tests directly. If so, delete.
**Effort:** Complex

### MAJOR: Unused Tool Scripts in Tools/
**ID:** DC-004
**Location:** `Tools/component_manager.py` (1084 lines), `Tools/component_graphic_picker.py` (528 lines)
**Issue:** Large Pygame-based utility scripts never imported by game code.
**Impact:** Large, unmaintained, possibly obsolete.
**Deliberate?:** Unclear.
**Recommendation:** Document, test, or delete.
**Effort:** Medium

### MAJOR: Debugging Utilities
**ID:** DC-005
**Location:** `Debugging/archive_confirmed.py`, `Debugging/confirm_bugs_ui.py`
**Issue:** Custom bug tracking utilities that duplicate GitHub Issues functionality.
**Impact:** Maintenance burden, confusion about tracking method.
**Deliberate?:** Yes, but questionable.
**Recommendation:** Migrate to GitHub Issues, archive Debugging/.
**Effort:** Medium

### MAJOR: Unused Helper Scripts in scripts/
**ID:** DC-006
**Location:** `scripts/reorg_tests.py`, `scripts/find_alias_usages.py`, `scripts/check_legacy_data.py`, `scripts/repro_*.py`
**Issue:** One-time migration/debugging scripts. Migrations complete.
**Impact:** Clutter.
**Deliberate?:** Partially.
**Recommendation:** Move to docs/_legacy_docs/ or delete.
**Effort:** Medium

### MAJOR: 176 __pycache__ Directories
**ID:** DC-007
**Location:** Throughout codebase (1593 .pyc files)
**Issue:** Compiled Python files should not be in version control.
**Impact:** Pollutes repo.
**Deliberate?:** No.
**Recommendation:** Add to .gitignore, git rm -r --cached.
**Effort:** Simple

### MAJOR: Legacy tkinter_utils.py Module
**ID:** DC-008
**Location:** `game/ui/services/tkinter_utils.py` (231 lines)
**Issue:** Tkinter utilities for file dialogs. Only used by 4 files. Heavyweight platform-dependent dependency.
**Impact:** Fragile, platform-dependent.
**Deliberate?:** Yes - consolidation of duplication, but Tkinter dependency questionable.
**Recommendation:** Replace with pygame_gui or pyperclip alternatives.
**Effort:** Complex

### MAJOR: Unused NotImplementedError Stub
**ID:** DC-009
**Location:** `game/ui/panels/battle_panels.py:21`
**Issue:** BattlePanel.draw() raises NotImplementedError but may have no active subclasses.
**Impact:** Confusion if unused.
**Deliberate?:** Unclear.
**Recommendation:** Audit BattlePanel subclasses.
**Effort:** Medium

### MAJOR: Empty __init__.py Files
**ID:** DC-010
**Location:** 25 empty __init__.py files
**Issue:** Python 3.3+ doesn't require these.
**Impact:** Minimal but unnecessary.
**Deliberate?:** Yes - legacy habit.
**Recommendation:** Leave as-is (low priority).
**Effort:** Simple

### MAJOR: tests/refactor/ Directory
**ID:** DC-011
**Location:** `tests/refactor/test_deprecated_code_removed.py` (136 lines)
**Issue:** Regression guard test in oddly named directory.
**Impact:** Directory structure inconsistency.
**Deliberate?:** Yes - guard against regression.
**Recommendation:** Move to tests/regression/ or tests/unit/refactor/.
**Effort:** Simple

### MINOR: Protocol classes with pass stubs
**ID:** DC-012
**Location:** `game/ai/interfaces/controllable.py`
**Issue:** Protocol with 30+ pass stubs. Could use `...` instead.
**Deliberate?:** Yes - how protocols work.
**Recommendation:** Cosmetic: use `...` instead of `pass`.
**Effort:** Simple

### MINOR: Exception classes with only pass
**ID:** DC-013
**Location:** `game/core/exceptions.py`
**Issue:** 9 exception classes with only pass. This is standard Python pattern.
**Deliberate?:** Yes. Not dead code.

### MINOR: if __name__ == "__main__" in app.py
**ID:** DC-014
**Location:** `game/app.py:40`
**Issue:** Guard technically redundant for entry point.
**Deliberate?:** Yes - best practice.
**Recommendation:** Keep as-is.

### MINOR: Commented Code Blocks (Explanatory)
**ID:** DC-015 through DC-020
**Location:** Various strategy/ and ui/ files
**Issue:** Comments explaining past bugs or decisions. These are documentation, not dead code.
**Deliberate?:** Yes.
**Recommendation:** Keep.

### MINOR: Minimal TODO/FIXME Comments
**ID:** DC-021
**Issue:** Only 2 TODO comments in entire game/. Positive finding.

### INFO: Formation Editor in Tools/
**ID:** DC-022
**Location:** `game/app.py:22` imports from `Tools/formation_editor.py`
**Issue:** Game code importing from Tools/ directory. Architectural inconsistency.
**Deliberate?:** Unclear.
**Recommendation:** Move to game/ui/screens/formation_editor.py.
**Effort:** Simple

### INFO: test_framework Used Only by Test Lab
**ID:** DC-023
**Issue:** See DC-003.

### INFO: sys import in test_lab/screen.py
**ID:** DC-024
**Location:** `game/ui/screens/test_lab/screen.py:10`
**Issue:** import sys may be unused.
**Recommendation:** Run linter project-wide.
**Effort:** Simple

### INFO: High Comment Density Files
**ID:** DC-025
**Location:** 20 files with 5+ consecutive comment lines
**Issue:** May be documentation or obsolete explanations.
**Recommendation:** Low priority review.

### INFO: ShipComponentManager Deletion Verification
**ID:** DC-027
**Issue:** MEMORY.md mentions deletion. Verify it's truly gone.
**Recommendation:** Quick grep to verify.
**Effort:** Simple

## Estimated Dead Code
- Confirmed dead: ~35KB (legacy tools) + 400 bytes (formatimg scripts)
- Probable dead: ~338KB (test_framework if migrateable)
- Build artifacts: 176 __pycache__ directories

## Top 5 Priority Issues

1. **DC-001 (CRITICAL):** Delete legacy migration scripts - 5 min, zero risk
2. **DC-002 (CRITICAL):** Delete duplicate formatimg.py - 5 min, zero risk
3. **DC-007 (MAJOR):** Remove __pycache__ from git - 10 min
4. **DC-003 (CRITICAL):** Audit test_framework obsolescence - 2-4 hours
5. **DC-006 (MAJOR):** Clean up scripts/ directory - 1-2 hours
