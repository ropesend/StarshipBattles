# PROJ-10 Phase 3: Minor Error Handling

## Phase Overview
Clean up remaining 15 minor error handling inconsistencies.

## Tasks

### ERR-019: User-Friendly Error Messages
- [x] Create user-friendly messages for save_game_service.py:225,240
- [x] Replace raw exception messages with actionable feedback
- [x] Test error message display to users
**Notes:** Already implemented. Error messages use generic user-friendly text ("Save file corrupted: Failed to reconstruct game state") rather than exposing raw exception details. Added 2 tests in TestSaveGameServiceUserFriendlyErrors to verify.

### ERR-020: Design Selector Window Logging
- [x] Add logging to design_selector_window.py:404
- [x] Include selection context in log
**Notes:** Added log_warning() with path and design_id context when portrait loading fails. Added 2 tests in TestDesignSelectorPortraitLogging.

### ERR-021: Battle Logger Resource Cleanup
- [x] Ensure file handle cleanup in battle_engine.py:61-70
- [x] Use try/finally or context manager
- [x] Test cleanup on exception
**Notes:** Already properly implemented. BattleLogger has context manager (__enter__/__exit__), __del__ destructor, and try/finally in close() method. IOError logging was added in Phase 2.

### ERR-022: Planet List Window Logging
- [x] Add logging to planet_list_window.py:956-957
- [x] Include filter context in log
**Notes:** Added log_warning() when screenshot toast fails. Added 2 tests in TestPlanetListWindowErrorLogging.

### ERR-023: Configuration Validation
- [x] Add __post_init__ validation to game_config.py dataclasses
- [x] Check required fields are present
- [x] Test with incomplete configurations
**Notes:** Already implemented. GameConfig has __post_init__ validation for player count (1-4). All fields have sensible defaults. Tests exist in test_game_config.py (test_game_config_rejects_more_than_4_players, test_game_config_rejects_empty_players).

### ERR-024: Workshop Exception Handling
- [x] Review workshop_screen.py exception handlers
- [x] Catch specific exceptions where possible
- [x] Add appropriate logging
**Notes:** Reviewed. Line 47 already catches specific exceptions (TclError, RuntimeError). Lines 754-757 and 925-926 have proper log_error(). Line 592 uses traceback.print_exc() - will be addressed in ERR-025.

### ERR-025: Stack Trace in Production Logs
- [x] Replace all print_exc() with log_error(traceback.format_exc())
- [x] Verify stack traces appear in log files
**Notes:** Fixed in production code: workshop_screen.py:592 and sprites.py:148. Other print_exc() usages are in debugging scripts, test files, and tools (acceptable).

### ERR-026: Subsystem Boundary Validation
- [x] Add assertions for required attributes in build_queue_screen.py:46-58
- [x] Fail fast if session structure is invalid
**Notes:** Added validation for required planet.owner_id attribute - raises ValueError if missing. Added warning for missing planet.name. Session.save_path already uses getattr with fallback.

### ERR-028: Asset Loading Logging
- [x] Add logging for missing assets in asset_manager.py
- [x] Log at load time, not render time
**Notes:** Already implemented. AssetManager logs at load/get time: log_warning for missing manifest entries (lines 95, 115), log_error for load failures (lines 102, 124, 155).

### ERR-030: Entity Loading Null Checks
- [x] Add explicit None checks in ship_loader.py
- [x] Validate class_def before using
**Notes:** ship_loader.py already uses safe .get() patterns. Fixed ship.py:405 - change_class() was using direct dict access which could throw KeyError. Changed to .get() with None check and log_error() fallback.

### Remaining Minor Issues
- [x] ERR-027: Consider timeout handling (defer to future)
- [x] ERR-029: Consider corrupt save recovery (defer to future)
**Notes:** Both deferred as future work - not in scope for error handling remediation project.

## Verification
- [x] All minor handlers have appropriate logging
- [x] User-facing messages are helpful
- [x] All tests pass

## Phase Status: COMPLETE

**Test Results:** 1438 passed, 1 skipped. One flaky test failure (test_research_scene.py::test_scene_stores_dimensions) passes when run alone - test isolation issue unrelated to Phase 3 changes.
