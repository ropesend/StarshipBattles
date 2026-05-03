# Screenshot System Analysis Report

## Summary
- **Total issues found:** 12
- **Critical:** 2
- **Major:** 5
- **Minor:** 4
- **Info:** 1

---

## Findings

### CRITICAL: capture() Returns None — No Programmatic Filepath Access
**ID:** SS-01
**Location:** `game/core/screenshot_manager.py:70-116`
**Issue:** The `capture()` method saves a screenshot and logs the path, but returns `None` implicitly. There is no way for a caller to obtain the filepath of the screenshot they just captured. Any diagnostic system that needs to log "screenshot saved at X" would have to reconstruct the filename independently, duplicating the timestamp-based naming logic.
**Impact:** Blocks any integration where the caller needs the screenshot path (logging, bug tickets, agent reports). The clipboard copy is a side effect, not a programmatic return value.
**Recommendation:** Change `capture()` to return `Optional[str]` — return `abs_path` on success, `None` on failure or disabled. This is backward-compatible since no existing caller checks the return value.
**Files Affected:** `game/core/screenshot_manager.py:70-116`
**Effort:** Simple

### CRITICAL: No Programmatic Capture API — Only Keyboard Triggers
**ID:** SS-02
**Location:** Multiple files (see below)
**Issue:** Screenshots can only be triggered via F11/F12 keyboard shortcuts hardcoded in specific screen handlers. There is no function that an agent can insert into arbitrary code to take a diagnostic screenshot with metadata. The existing `ScreenshotManager.capture()` is the closest, but it:
- Requires the caller to manage surface access
- Has no metadata/context parameter
- Has no structured log output
- Has no throttle protection
- Is tied to the `DEBUG_SCREENSHOTS` compile-time constant

**Current keyboard-triggered screens:**
- `game/ui/screens/strategy_input_handler.py:110-113` (F11/F12)
- `game/ui/screens/workshop_event_router.py:447-461` (F10/F11/F12)
- `game/ui/screens/planet_list_window.py:742-745` (F11/F12)
- `game/ui/screens/build_queue_screen.py:841-846` (F11/F12)

**Screens with NO screenshot support:**
- `game/ui/screens/battle_screen.py` — BattleScreen
- `game/ui/screens/setup_screen.py` — BattleSetupScreen
- `game/ui/screens/formation_editor.py` — FormationEditorScreen
- `game/ui/screens/test_lab_screen.py` — TestLabScreen
- `game/ui/screens/galaxy_test_screen.py` — GalaxyTestScreen
- `game/ui/screens/new_game_setup_screen.py` — NewGameSetupScreen
- `game/ui/screens/race_setup_screen.py` — RaceSetupScreen
- `game/ui/screens/fleet_report_window.py` — FleetReportWindow
- `game/ui/screens/design_selector_window.py` — DesignSelectorWindow
- `game/ui/screens/fleet_orders_window.py` — FleetOrdersWindow

**Impact:** Agents investigating UI bugs in any of the unsupported screens have no way to capture visual state. Even in supported screens, agents can't insert code-level captures at specific draw stages.
**Recommendation:** Create a new `capture_diagnostic()` function that wraps `ScreenshotManager.capture()` with metadata, structured logging, throttling, and an independent enable/disable toggle.
**Effort:** Medium

### MAJOR: No Throttle Protection Against Loop Disasters
**ID:** SS-03
**Location:** `game/core/screenshot_manager.py:70-116`
**Issue:** `capture()` has no rate limiting. If an agent accidentally places a capture call inside a draw loop, update loop, or any high-frequency code path, it will attempt to save a PNG file every frame (60+ times/second), causing:
- Disk I/O saturation (PNG encoding is expensive)
- Thousands of files in `output/screenshots/`
- Clipboard spam (Tkinter window created per capture)
- Potential game freeze from I/O blocking
**Impact:** A single misplaced call could fill disk and freeze the game.
**Recommendation:** Add time-based throttling (minimum 2-second interval) to the diagnostic capture API. Leave the existing `capture()` unthrottled for manual F11/F12 use (which is naturally rate-limited by human input).
**Effort:** Simple

### MAJOR: DEBUG_SCREENSHOTS Is Compile-Time Only
**ID:** SS-04
**Location:** `game/core/constants.py:81`, `game/core/screenshot_manager.py:60`
**Issue:** The `DEBUG_SCREENSHOTS` constant is read once during `ScreenshotManager._setup()` and stored as `self.enabled`. While `self.enabled` can technically be set at runtime, there is no public API to toggle it. The constant is imported at module load time and cannot be changed without restarting. For a diagnostic system that agents enable/disable per investigation session, this is insufficient.
**Impact:** Cannot activate/deactivate diagnostic screenshots at runtime without directly mutating the singleton's internal state.
**Recommendation:** The diagnostic capture system should have its own independent enable/disable toggle, separate from `DEBUG_SCREENSHOTS` (which controls the F11/F12 manual captures).
**Effort:** Simple

### MAJOR: Clipboard Side Effect Is Inappropriate for Diagnostic Use
**ID:** SS-05
**Location:** `game/core/screenshot_manager.py:113, 118-146`
**Issue:** Every `capture()` call triggers `_copy_to_clipboard()`, which creates a Tkinter window (`tkinter.Tk()`) to set the clipboard. In diagnostic mode where multiple captures may occur, this:
- Creates unnecessary overhead (Tkinter window per capture)
- Overwrites the user's clipboard with each screenshot path
- May cause thread-safety issues if called from non-main thread
**Impact:** Undesirable side effects during programmatic diagnostic captures.
**Recommendation:** Diagnostic capture should either skip the clipboard copy entirely, or the clipboard copy should be optional (parameter with default).
**Effort:** Simple

### MAJOR: capture_strategy_layer() Has Hardcoded Scene Assumptions
**ID:** SS-06
**Location:** `game/core/screenshot_manager.py:156-217`
**Issue:** `capture_strategy_layer()` directly accesses `scene._renderer`, `scene.ui`, `scene.build_queue_screen`, `scene.screen_width`, `scene.screen_height`, `scene.SIDEBAR_WIDTH`, `scene.TOP_BAR_HEIGHT`. This method is tightly coupled to `StrategyScreen`'s internal structure and cannot be reused for other screens.
**Impact:** Cannot create similar screen-specific capture methods for BattleScreen, WorkshopScreen, etc. without duplicating the pattern and coupling to each screen's internals.
**Recommendation:** For the diagnostic system, use the simpler approach: capture `pygame.display.get_surface()` (the composed final frame) rather than reconstructing individual layers. Layer-specific captures should remain in the screen-specific code.
**Effort:** N/A (design guidance, not a code fix)

### MAJOR: No Structured Metadata in Screenshot Filenames
**ID:** SS-07
**Location:** `game/core/screenshot_manager.py:88-92`
**Issue:** Screenshot filenames follow the pattern `screenshot_{timestamp}_{label}.png`. The label is a free-form string with no structure. There's no way to encode context like screen name, bug ID, or capture reason into the filename in a parseable way.
**Impact:** Agents browsing the screenshots directory cannot determine what each screenshot shows without opening it. No machine-readable correlation between screenshots and their context.
**Recommendation:** The diagnostic capture system should emit structured log entries that pair the screenshot path with rich metadata (reason, screen, bug_id, context). The filename itself doesn't need to carry all metadata — the log is the index.
**Effort:** Simple (addressed by the log integration, not by changing filenames)

### MINOR: Workshop Holds Its Own ScreenshotManager Reference
**ID:** SS-08
**Location:** `game/ui/screens/workshop_screen.py:88`
**Issue:** `DesignWorkshopScreen` stores `self.screenshot_manager = ScreenshotManager.instance()` as an instance variable, while other screens call `ScreenshotManager.instance()` inline at capture time. This inconsistency is minor but shows there's no established pattern for how screens should access the screenshot manager.
**Recommendation:** Standardize on inline `ScreenshotManager.instance()` calls (which is what most screens do), or inject it via constructor for testability.
**Effort:** Simple

### MINOR: Toast Notification Pattern Duplicated Across 3 Screens
**ID:** SS-09
**Location:**
- `game/ui/screens/strategy_input_handler.py:508-521`
- `game/ui/screens/planet_list_window.py:952-965`
- `game/ui/screens/build_queue_screen.py:859-868`
**Issue:** The screenshot toast notification (UIMessageWindow creation with message text, positioning, and dimensions) is copy-pasted across 3 files with minor variations.
**Impact:** Minor DRY violation. If the toast format changes, 3+ locations need updating.
**Recommendation:** Extract a `show_screenshot_toast(manager, screen_rect)` utility, but this is low priority.
**Effort:** Simple

### MINOR: Region Capture Lacks Validation Logging
**ID:** SS-10
**Location:** `game/core/screenshot_manager.py:96-107`
**Issue:** When a region is provided but is outside surface bounds, the method logs a warning and returns, but doesn't indicate what the caller should do. No return value distinguishes "disabled" from "region invalid" from "success".
**Impact:** Minor — mostly addressed by SS-01 (return value change).
**Effort:** Simple

### MINOR: No Screenshot Cleanup / Rotation
**ID:** SS-11
**Location:** `game/core/screenshot_manager.py` (missing feature)
**Issue:** Screenshots accumulate indefinitely in `output/screenshots/`. Over time with diagnostic use, this directory could grow very large.
**Impact:** Disk usage. Not urgent, but worth noting for a system that will be used more frequently.
**Recommendation:** Consider a maximum screenshot count or age-based cleanup for the diagnostic subdirectory.
**Effort:** Simple (future enhancement)

### INFO: Battle State Capture Is a Separate Parallel System
**ID:** SS-12
**Location:** `test_framework/battle_state_capture.py`
**Issue:** The test framework has its own `BattleStateCapture` system that saves battle state as JSON. This is a separate system from `ScreenshotManager` — it captures data, not visuals. Worth noting that the codebase already has the concept of "capture context for later analysis" in the test framework.
**Impact:** None (informational). The diagnostic screenshot system could learn from this pattern (structured output, context managers, test integration).
**Effort:** N/A
