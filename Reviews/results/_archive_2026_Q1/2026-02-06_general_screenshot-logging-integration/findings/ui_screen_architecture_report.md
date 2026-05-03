# UI Screen Architecture Analysis Report

## Summary
- **Total issues found:** 9
- **Critical:** 1
- **Major:** 3
- **Minor:** 3
- **Info:** 2

---

## Findings

### CRITICAL: No Base Screen Class — No Uniform Capture Hook
**ID:** UI-01
**Location:** `game/ui/screens/` (all screen files)
**Issue:** There is no base screen class or shared interface. Each screen implements its own `draw()` and `handle_event()` with different signatures:

| Screen | draw() signature | Event handling |
|--------|-----------------|----------------|
| BattleScreen | `draw(self, screen)` | BattleInputHandler |
| StrategyScreen | `draw(self, screen)` | StrategyInputHandler |
| DesignWorkshopScreen | `draw(self, screen)` | WorkshopEventRouter |
| FormationEditorScreen | `draw(self, screen)` | FormationInputHandler |
| TestLabScreen | `draw(self, screen)` | handle_event + handle_input |
| GalaxyTestScreen | `draw(self, screen)` | handle_event + handle_input |
| BuildQueueScreen | `draw(self, screen)` | handle_event |
| BattleSetupScreen | `draw(self, screen)` | update() |
| PlanetListWindow | extends UIWindow | handle_event |
| FleetReportWindow | extends UIWindow | UIManager auto-handles |

**Impact:** There is no single hook point where "capture the current screen" can be added uniformly. A diagnostic capture call must be placed per-screen or at the game loop level (using `pygame.display.get_surface()` after all drawing is complete).

**Recommendation:** For diagnostic purposes, the simplest approach is to capture `pygame.display.get_surface()` — the final composed frame — from the game loop level, after all screens have drawn and before `pygame.display.flip()`. This avoids needing per-screen hooks. When agents need screen-specific captures, they insert `capture_diagnostic()` calls directly into the screen code they're debugging.
**Effort:** N/A (design guidance)

### MAJOR: Game Loop Has No Pre-Flip Hook Point
**ID:** UI-02
**Location:** `game/app.py` (draw/update cycle)
**Issue:** The game loop calls each screen's `draw()` method and then `pygame.display.flip()`. There is no hook or callback between "all drawing complete" and "flip to display". A diagnostic system that wants to capture the composed frame at a reliable point has no built-in hook.

Current flow in `app.py`:
1. Screen-specific `draw(self.screen)` called
2. `pygame.display.flip()` called
3. No intermediate point for diagnostic capture

**Impact:** Agents must insert capture calls either inside a specific screen's `draw()` method (screen-specific) or before `pygame.display.flip()` in `app.py` (global). Both work but require temporary code insertion.
**Recommendation:** This is acceptable for the temporary-code-insertion workflow. Agents will add `capture_diagnostic()` at the specific point they need to diagnose. A global pre-flip hook could be added later if needed.
**Effort:** N/A (acceptable as-is for temporary insertion approach)

### MAJOR: No Game State Tracking Accessible Outside app.py
**ID:** UI-03
**Location:** `game/app.py` — `self.state` (GameState)
**Issue:** The current `GameState` is stored as `self.state` on the `Game` instance. It is not exposed via any module-level accessor or service. When a diagnostic capture call is placed in an arbitrary screen file, there's no way to query "what is the current game state?" without having a reference to the `Game` instance.
**Impact:** Diagnostic captures placed in screen code cannot auto-detect the game state for logging purposes. The caller must explicitly pass the screen name.
**Recommendation:** Require callers to always pass `screen_name` explicitly to the diagnostic capture function. Since agents are inserting the call into specific screen code (e.g., inside `BuildQueueScreen.draw()`), they inherently know the screen name. This avoids adding global state tracking.
**Effort:** N/A (design decision — explicit > implicit)

### MAJOR: Modal Windows Layer on Top of Screens — Capture Timing Matters
**ID:** UI-04
**Location:**
- `game/ui/screens/strategy_screen.py` — `build_queue_screen` drawn after main UI
- `game/app.py` — modal window flags (`showing_race_setup`, etc.)
- `game/ui/screens/build_queue_screen.py` — drawn as overlay

**Issue:** Modal windows (BuildQueueScreen, FleetReportWindow, PlanetListWindow, etc.) are drawn on top of their parent screen. If a diagnostic capture is taken during the parent screen's `draw()` before the modal is drawn, the modal won't appear in the screenshot. Conversely, capturing after `pygame.display.flip()` or via `pygame.display.get_surface()` will always include all visible layers.

**Modal rendering order in StrategyScreen.draw():**
1. `screen.fill()` — background
2. `self._renderer.draw(screen)` — galaxy map
3. `self.ui.draw(screen)` — sidebar, top bar
4. `self.build_queue_screen.draw(screen)` — modal overlay (if active)
5. Return to `app.py` → `pygame.display.flip()`

**Impact:** Agents need to be aware that capture timing affects what's visible. Capturing via `pygame.display.get_surface()` always gets the full composed frame, which is the recommended default.
**Recommendation:** Document that `capture_diagnostic()` with no explicit `surface` parameter captures the display surface (full composed frame including all modals). For layer-specific captures, agents should pass a specific surface.
**Effort:** N/A (documentation)

### MINOR: Screen Surface Ownership Is Implicit
**ID:** UI-05
**Location:** `game/app.py:82`
**Issue:** The display surface is created via `pygame.display.set_mode()` in `Game.__init__()` and passed to screen `draw()` methods as a parameter. But `pygame.display.get_surface()` also returns this same surface globally. The ownership model is implicit — screens draw to a surface they receive, but anyone can grab it via the global pygame function.
**Impact:** Minor — `pygame.display.get_surface()` is the standard pygame pattern. The diagnostic system can safely use it.
**Effort:** N/A

### MINOR: Screenshot Support Inconsistent Across Screens
**ID:** UI-06
**Location:** See SS-02 for complete list
**Issue:** Only 4 of 14+ screens have F11/F12 screenshot support. This inconsistency means agents familiar with screenshots in one screen may expect them in others. The `capture_strategy_layer()` method in ScreenshotManager is specific to StrategyScreen and cannot be reused.
**Impact:** Minor for the diagnostic integration (since diagnostic captures are code-inserted, not keyboard-triggered). But indicates the screenshot feature was added incrementally without a uniform approach.
**Recommendation:** The diagnostic capture system provides a uniform API that works everywhere, making per-screen keyboard shortcuts a separate concern.
**Effort:** N/A

### MINOR: Config Patterns Established But No Diagnostic Config Exists
**ID:** UI-07
**Location:** `game/core/config.py`
**Issue:** The config module has established class-based configuration patterns (`DisplayConfig`, `UIConfig`, `PhysicsConfig`, `BattleConfig`, `AIConfig`, `TestConfig`). There is no `DiagnosticConfig` or `DebugConfig` class for diagnostic tool settings.
**Impact:** Minor — the diagnostic throttle interval and other settings have no established home.
**Recommendation:** Add a `DiagnosticConfig` class to `game/core/config.py` for diagnostic settings (throttle interval, max screenshots per session, etc.).
**Effort:** Simple

### INFO: Composition Pattern Is Well-Established
**ID:** UI-08
**Location:** Multiple screens
**Issue:** Not an issue — an observation. The codebase uses a healthy composition pattern:
- `StrategyScreen` delegates to `StrategyRenderer` + `StrategyInputHandler`
- `DesignWorkshopScreen` delegates to `WorkshopEventRouter`
- `BattleScreen` delegates to `BattleInputHandler` + `BattleUI`

This means a diagnostic capture system doesn't need to modify screen classes — it can be a standalone module that any code location can call.
**Effort:** N/A

### INFO: GameState Enum Covers All Screens
**ID:** UI-09
**Location:** `game/core/constants.py:34-44`
**Issue:** Not an issue. The GameState enum provides clean string names for all game states:
```
MENU, BUILDER, BATTLE, BATTLE_SETUP, FORMATION,
TEST_LAB, STRATEGY, RACE_SETUP, RESEARCH_TREE, GALAXY_TEST
```
These names can be used directly as `screen_name` values in diagnostic capture calls.
**Effort:** N/A
