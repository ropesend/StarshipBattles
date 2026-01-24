# PROJ-13 Phase 1: Dead Code Cleanup

## Phase Overview
Remove all identified dead code and deprecated wrappers.

## Tasks

### DC-001: Remove Unused sys Import
- [ ] Open `game/core/logger.py`
- [ ] Remove `import sys` at line 2
- [ ] Verify no other usage of sys in file
- [ ] Run tests

### DC-002: Remove Deprecated builder_screen.py
- [ ] Find all imports of `BuilderSceneGUI`
- [ ] Update imports to use `DesignWorkshopGUI` from `workshop_screen.py`
- [ ] Delete `game/ui/screens/builder_screen.py`
- [ ] Run tests to verify no breaks

### DC-003: Remove Commented Console Handler
- [ ] Open `game/core/logger.py`
- [ ] Remove commented line at line 38
- [ ] Clean up any related commented code
- [ ] Verify logging still works

### DC-004: Remove Refactoring Artifact Comment
- [ ] Open `game/simulation/entities/ship_physics.py`
- [ ] Remove comment at line 4 about removed imports
- [ ] Verify no useful information lost
- [ ] Run tests

### DC-005: Handle Stub _apply_custom_stats()
- [ ] Open `game/simulation/components/component.py`
- [ ] Review lines 535-538
- [ ] Determine if method should be implemented or removed
- [ ] If removing: delete method, update any calls
- [ ] If keeping: add TODO comment explaining purpose
- [ ] Run tests

### DC-006: Review Arrow Button Implementation
- [ ] Open `game/ui/panels/system_tree_panel.py`
- [ ] Review lines 95-97
- [ ] Either implement arrow positioning or remove conditional
- [ ] Run tests

### DC-007: Delete Orphaned Debug Files
- [ ] Delete `Debugging/Marked_for_Deletion_2026-01-20/` directory
- [ ] Verify no active references to these files
- [ ] Update any documentation referencing them

### DC-008: Remove Duplicate Line
- [ ] Open `game/ui/screens/planet_list_window.py`
- [ ] Remove duplicate `btn.set_text(f"{t}")` at lines 779-780
- [ ] Run tests

### DC-009: Clean Up Hex Ring Comments
- [ ] Open `game/strategy/data/hex_math.py`
- [ ] Review lines 109-131
- [ ] Replace confusing comments with clear docstring
- [ ] Run tests

### DC-011: Clean Up Physics Comments
- [ ] Open `game/simulation/entities/ship_physics.py`
- [ ] Review lines 27-44
- [ ] Convert rhetorical questions to clear docstring
- [ ] Remove exploratory comments
- [ ] Run tests

### DC-012: Clarify PresetManager Status
- [ ] Check if PresetManager is deprecated or active
- [ ] If deprecated: remove from planet_list_window.py
- [ ] If active: update builder_screen.py comment
- [ ] Document decision

## Verification
- [ ] All identified dead code removed
- [ ] No references to deleted files
- [ ] All tests pass
- [ ] No new warnings at startup
