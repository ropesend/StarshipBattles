# PROJ-13 Phase 1: Dead Code Cleanup

## Phase Overview
Remove all identified dead code and deprecated wrappers.

## Tasks

### DC-001: Remove Unused sys Import
- [x] Open `game/core/logger.py`
- [x] Remove `import sys` at line 2
- [x] Verify no other usage of sys in file
- [x] Run tests

### DC-002: Remove Deprecated builder_screen.py
**Status: DEFERRED** - Medium effort migration required
- [ ] Find all imports of `BuilderSceneGUI` (game/app.py and ~15 test files)
- [ ] Update imports to use `DesignWorkshopGUI` from `workshop_screen.py`
- [ ] Delete `game/ui/screens/builder_screen.py`
- [ ] Run tests to verify no breaks

**Note:** This is a backward-compatibility wrapper that many tests depend on. Migration requires updating game/app.py and multiple test files. Recommend handling in a dedicated session.

### DC-003: Remove Commented Console Handler
- [x] Open `game/core/logger.py`
- [x] Remove commented line at line 38
- [x] Clean up any related commented code
- [x] Verify logging still works

### DC-004: Remove Refactoring Artifact Comment
- [x] Open `game/simulation/entities/ship_physics.py`
- [x] Remove comment at line 4 about removed imports
- [x] Verify no useful information lost
- [x] Run tests

### DC-005: Handle Stub _apply_custom_stats()
- [x] Open `game/simulation/components/component.py`
- [x] Review lines 535-538
- [x] Determine if method should be implemented or removed
- [x] Removed method and its call (no subclasses exist; ability system handles all type-specific behavior)
- [x] Run tests

### DC-006: Review Arrow Button Implementation
- [x] Open `game/ui/panels/system_tree_panel.py`
- [x] Review lines 95-97
- [x] Removed dead conditional block (arrow_button is always None)
- [x] Run tests

### DC-007: Delete Orphaned Debug Files
- [x] Delete `Debugging/Marked_for_Deletion_2026-01-20/` directory
- [x] Verify no active references to these files
- [x] N/A - no documentation referenced them

### DC-008: Remove Duplicate Line
- [x] Open `game/ui/screens/planet_list_window.py`
- [x] Remove duplicate `btn.set_text(f"{t}")` at lines 779-780
- [x] Run tests

### DC-009: Clean Up Hex Ring Comments
- [x] Open `game/strategy/data/hex_math.py`
- [x] Review lines 109-131
- [x] Replace confusing comments with clear docstring
- [x] Run tests

### DC-011: Clean Up Physics Comments
- [x] Open `game/simulation/entities/ship_physics.py`
- [x] Review lines 27-44
- [x] Convert rhetorical questions to clear docstring
- [x] Remove exploratory comments
- [x] Run tests

### DC-012: Clarify PresetManager Status
- [x] Check if PresetManager is deprecated or active
- [x] **Result:** PresetManager in `planet_list_presets.py` is ACTIVE (for planet list filters)
- [x] Removed misleading comment in `builder_screen.py` (it referred to old ship builder presets)
- [x] Documented decision: Planet list PresetManager is production code, not deprecated

## Verification
- [x] All simple dead code items removed (10 of 11 tasks complete)
- [x] No references to deleted files
- [x] All tests pass (3573 passed, 1 skipped; 1 pre-existing flaky test)
- [x] No new warnings at startup

## Notes
- DC-002 (builder_screen.py migration) deferred - requires medium effort migration
- Pre-existing flaky test: `test_intercept_integration` fails in parallel but passes in isolation
