# Misplaced File & Directory Structure Auditor Report

## Summary
- Files to relocate/consolidate: 1 (formation_editor.py duplicate)
- Directories to rename: 1 (tests/refactor/ → tests/regression/)
- Empty directories to remove: 2 (game/ui/hud/, game/simulation/entities/mixins/)
- Test files to relocate: 1 (test_formation_editor_logic.py)
- Configuration to update: 1 (pytest.ini pythonpath)
- Items confirmed well-placed: 2 (tkinter_utils.py, BattlePanel)

---

## Findings

### Major: Duplicate formation_editor.py — Tools/ vs game/ui/screens/

**ID:** MISPLACED-001
**Current Location:** Both `Tools/formation_editor.py` (1,055 lines) AND `game/ui/screens/formation_editor.py` (941 lines)
**Issue:** Formation editor exists in two locations with divergent implementations. Tools/ version is the legacy standalone tool; game/ui/screens/ version is the refactored, game-integrated version using tkinter_utils.
**Dependencies to Update:**
1. game/app.py line 22: `from Tools.formation_editor import FormationEditorScreen`
2. tests/unit/builder/test_formation_editor_logic.py line 6: `import formation_editor`
3. pytest.ini line 5: `pythonpath = . Tools`
**Proposed Action:** DELETE Tools/formation_editor.py, update game/app.py import to use game/ui/screens/ version, update test imports
**Risk Level:** Low — UI screen only, not critical game path
**Effort:** Simple — delete file, update 3 imports/configs

---

### Minor: tests/refactor/ Directory Misleading Name

**ID:** MISPLACED-002
**Current Location:** tests/refactor/test_deprecated_code_removed.py (136 lines)
**Issue:** Directory named "refactor" but contains regression guard tests (PROJ-42) ensuring deprecated code stays removed. Name implies active refactoring work.
**Proposed Location:** tests/regression/ (already exists as a directory)
**Dependencies to Update:** None (pytest discovers by path)
**Risk Level:** Zero — pure rename, no code changes
**Effort:** Trivial — single directory rename/merge

---

### Minor: Empty game/ui/hud/ Directory

**ID:** MISPLACED-003
**Current Location:** game/ui/hud/
**Issue:** Empty directory — contains only __init__.py and __pycache__. No implementation files.
**Proposed Action:** DELETE entire directory
**Dependencies to Update:** None — no imports reference game.ui.hud
**Risk Level:** Zero
**Effort:** Trivial

---

### Minor: Empty game/simulation/entities/mixins/ Directory

**ID:** MISPLACED-004
**Current Location:** game/simulation/entities/mixins/
**Issue:** Empty or near-empty directory — abandoned scaffolding from earlier refactoring
**Proposed Action:** DELETE if empty
**Dependencies to Update:** None
**Risk Level:** Zero
**Effort:** Trivial

---

### Info: BattlePanel Base Class — Properly Designed (Keep)

**ID:** MISPLACED-005
**Current Location:** game/ui/panels/battle_panels.py
**Issue:** BattlePanel.draw() has NotImplementedError — flagged in prior review as potential dead code
**Assessment:** **NOT dead code.** BattlePanel is an active abstract base class with 3 concrete subclasses:
- ShipStatsPanel (lines 46-247) — implements draw() properly
- SeekerMonitorPanel (lines 249-471) — implements draw() properly
- BattleControlPanel (lines 472-567) — implements draw() properly
- All three imported and instantiated by game/ui/screens/battle_ui.py
**Proposed Action:** KEEP AS-IS — correct abstract base pattern
**Risk Level:** Zero
**Effort:** N/A

---

### Info: tkinter_utils.py — Well Placed (Keep)

**ID:** MISPLACED-006
**Current Location:** game/ui/services/tkinter_utils.py (231 lines)
**Issue:** Tkinter dependency questioned in prior review
**Assessment:** **Properly placed.** This was intentionally extracted (DUP-UI2-001) to eliminate duplication across 4+ consumer files. Provides lazy, thread-safe Tkinter root initialization for file dialogs.
**Consumers:** ship_io.py, screenshot_manager.py, formation_editor.py, workshop_ship_io.py + tests
**Proposed Action:** KEEP — consolidation is correct
**Risk Level:** Zero
**Effort:** N/A

---

### Minor: pytest.ini pythonpath Includes Tools/

**ID:** MISPLACED-007
**Current Location:** pytest.ini line 5: `pythonpath = . Tools`
**Issue:** Tools directory added to Python path to support test imports. After resolving MISPLACED-001, this should be cleaned up.
**Proposed Action:** After MISPLACED-001, change to `pythonpath = .`
**Dependencies:** Blocked by MISPLACED-001
**Risk Level:** Low
**Effort:** Trivial

---

### Minor: Formation Editor Test in Wrong Directory

**ID:** MISPLACED-008
**Current Location:** tests/unit/builder/test_formation_editor_logic.py
**Issue:** Formation editor test is in builder/ directory but formation editor lives in game/ui/screens/. Should be co-located with other UI screen tests.
**Proposed Location:** tests/unit/ui/screens/test_formation_editor_logic.py
**Dependencies to Update:** Import statement (after MISPLACED-001 resolution)
**Risk Level:** Low
**Effort:** Simple — move file, update import
**Blocked By:** MISPLACED-001

---

## Implementation Order

1. **MISPLACED-001** — Delete Tools/formation_editor.py, update game/app.py import
2. **MISPLACED-007** — Update pytest.ini pythonpath (remove Tools)
3. **MISPLACED-008** — Move test_formation_editor_logic.py to tests/unit/ui/screens/
4. **MISPLACED-002** — Rename/merge tests/refactor/ into tests/regression/
5. **MISPLACED-003** — Delete empty game/ui/hud/
6. **MISPLACED-004** — Delete empty game/simulation/entities/mixins/

**Total Effort:** ~45 minutes for careful migration

---

## Top 5 Priority Issues

1. **MISPLACED-001** — Duplicate formation_editor.py causes confusion about authoritative version
2. **MISPLACED-007** — pytest.ini pythonpath includes non-game directory
3. **MISPLACED-002** — tests/refactor/ misleading name
4. **MISPLACED-003/004** — Empty directories are clutter
5. **MISPLACED-008** — Test file not co-located with source
