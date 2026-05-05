# Architecture Analysis: PROJ-342 Layer Boundary Review

**Analyst:** Architecture Analyst role (read-only exploration)  
**Date:** 2026-05-04  
**Document:** Analysis of proposed TestLabScreen refactor against docs/01_ARCHITECTURE.md

---

## Executive Summary

The proposed refactor introduces **one real layer-boundary violation** and two design questions. The violation is **fixable with a specific alternative pattern** already established elsewhere in the codebase.

**Verdict:** Plan requires revision before approval.

---

## 1. Layer Assignments (per docs/01_ARCHITECTURE.md § Layer Structure)

### TestLabScreen
- **Assigned layer:** UI Layer (game/ui/screens/test_lab/screen.py)
- **Rationale:** Part of game/ui/, implements IScene protocol, handles Pygame rendering
- **Current allowed dependencies per Layer Structure:** AI, Strategy, Research, Simulation, Engine, Services, Assets, Core

### BattleScreen
- **Assigned layer:** UI Layer (game/ui/screens/battle_screen.py)
- **Rationale:** Part of game/ui/, implements IScene protocol, drives BattleService and BattleUI
- **Current allowed dependencies per Layer Structure:** same as TestLabScreen

### TestExecutionService / TestResultsService
- **Assigned layer:** Combat Lab module (outside standard layer hierarchy; in combat_lab/)
- **Status:** Not governed by docs/01_ARCHITECTURE.md layer rules
- **Note:** combat_lab/ is a test harness, not part of the production game layer stack

---

## 2. Cross-Screen References: Is TestLabScreen → BattleScreen Direct Access Acceptable?

### Current State (Violation)
TestLabScreen currently holds self.game (a reference to the Game composition root) and accesses:
`python
# game/ui/screens/test_lab/screen.py:382-384
screen_center_x = self.game.screen.get_width() // 2
self.game.screen.blit(...)  # rendering to pygame display

# game/ui/screens/test_lab/screen.py:394, 398, 400, 489
self.game.battle_scene.engine
self.game.battle_scene._battle_service.create_battle(...)
self.game.battle_scene.start_battle(controller)
`

### Architectural Rule Check
docs/01_ARCHITECTURE.md § "Dependency Rules" (lines 44-56):
- **UI Layer is allowed:** to depend on AI, Strategy, Research, Simulation, Engine, Services, Assets, Core
- **UI Layer is NOT explicitly forbidden** from depending on other UI-layer components

**However**, docs/01_ARCHITECTURE.md § "Layer Structure" (lines 8-42) describes the rule model:
> "Eight layers with **strict downward-only dependency flow**"

This establishes **the principle**: layers depend downward, not sideways.

### Pattern Survey: Do Other Screens Hold References to Other Screens?

Checked all screens in game/ui/screens/:
- BattleScreen.__init__ → takes screen_width, screen_height, scene_callback; **no cross-screen references**
- StrategyScreen.__init__ → takes screen_width, screen_height, scene_callback, input_mapper; **no cross-screen references**
- DesignWorkshopScreen.__init__ → takes screen_width, screen_height, context; **no cross-screen references**
- FleetBattleSetupScreen.__init__ → takes screen_width, screen_height, scene_callback; **no cross-screen references**
- TestLabScreen.__init__ → takes game, scene_callback; **HOLDS GAME REFERENCE** ← unique

**Verdict:** TestLabScreen is the **only screen in the UI layer that holds a direct reference to another screen**. This is unprecedented.

---

## 3. The _require_display_surface() Helper: Is pygame.display.get_surface() a Layer Violation?

### Proposal
Replace self.game.screen (a reference to pygame.display.get_surface() captured at Game init) with a fresh call to pygame.display.get_surface() wrapped in _require_display_surface().

### Current Practice in Codebase

**StrategyGameStateManager** (game/ui/screens/strategy_game_state_manager.py) uses pygame.display.get_surface() directly:

`python
# Lines ~120-125
screen = pygame.display.get_surface()
if screen:
    self._screen.draw(screen)
    pygame.display.flip()

# Lines ~140-145
surface = pygame.display.get_surface()
if surface is not None:
    self._screen.draw(surface)
    pygame.display.flip()
`

This is **same-layer (UI→Pygame API)**, not a cross-layer dependency.

### Architectural Rule Check

docs/01_ARCHITECTURE.md § "Dependency Rules":
- Pygame is a **third-party library**, not a game layer
- Direct Pygame API calls from UI layer are expected and correct
- No layer is "above" Pygame; all rendering ultimately calls pygame

**Verdict:** Using pygame.display.get_surface() from a screen is **not a layer violation**. It is the standard pattern (see StrategyGameStateManager precedent).

---

## 4. Deletion of TestExecutionService / TestResultsService: Does It Collapse a Documented Boundary?

### Current Architecture Status

combat_lab/ services are **not part of the standard game layer hierarchy** described in docs/01_ARCHITECTURE.md. They are not mentioned in the document and do not appear in the "Package Directory Map" (§ "Package Directory Map", lines 88-225).

### Service Coupling Analysis

**TestExecutionService usage:**
- Constructor: TestLabUIController.__init__ (line 41)
- Callers: TestLabUIController.handle_run_visual (line 102), handle_run_headless (line 137), handle_run_* internals (line 150)
- External callers: **None detected** (verified by plan discussion artifact line 18-20)

**TestResultsService usage:**
- Constructor: TestLabUIController.__init__ (line 43)
- Callers: TestLabUIController.handle_run_* methods (internal only)
- External callers: **None detected**

**Plan assertion (r002 lines 58-61):** Both services are deleted when their only callers (handle_run_visual, handle_run_headless) are deleted.

### Verdict
Deletion is **safe and correct** — the services are true orphans with no boundary to collapse. They were internal test-harness helpers, not production-layer infrastructure.

---

## 5. The Real Layer Violation: TestLabScreen(battle_scene) Direct Reference

### The Issue

The proposed signature is:
`python
def __init__(
    self,
    screen_width: int,
    screen_height: int,
    battle_scene: BattleScreen,
    scene_callback=None
):
    self.battle_scene = battle_scene
`

This couples TestLabScreen **directly to BattleScreen** at the UI-layer.

Current usages in the proposed implementation:
- Line 394: self.battle_scene.engine — access to combat engine
- Line 398: self.battle_scene.engine is None
- Line 400: self.battle_scene._battle_service.create_battle(...)
- Line 489: self.battle_scene.start_battle(controller)

### Why This Violates the Architecture

docs/01_ARCHITECTURE.md § "Layer Structure" (lines 8-42) establishes:
- **Strict downward-only dependency flow** — layers depend on lower layers, not peers

Two screens (TestLabScreen, BattleScreen) are both **in the same layer (UI)**. Direct peer-to-peer coupling **violates the "downward-only" principle** by creating a lateral dependency at the same level.

**The architecture does not permit UI components to couple to each other directly.** They must route through the router or pass state via protocols/DTOs.

### Precedent Check: How Do Screens Interact Elsewhere?

**ScreenRouter pattern** (game/screen_router.py:56-127):
- Router holds the long-lived scene instances
- Scenes do **not** reference each other
- Scenes communicate back to Game/Router via scene_callback (lines 125-126 in ScreenRouter)
- Router decides which scene to activate based on callback action

**Example flow:**
1. BattleScreen calls self.scene_callback("return_to_test_lab", ...)
2. Router's _handle_battle_action is invoked (actually Game._handle_battle_action)
3. Router switches self.active_scene = self.test_lab_scene
4. TestLabScreen is now active; BattleScreen never directly invoked it

This is the **established pattern in production code**.

---

## 6. Proposed Fix: Re-Routing Through ScreenRouter

### The Problem with Current Plan

TestLabScreen directly accessing BattleScreen.engine and BattleScreen.start_battle() bypasses the router and creates a hidden, undocumented dependency at the UI layer.

### Correct Solution (Alternative Pattern)

Instead of passing attle_scene: BattleScreen to TestLabScreen, refactor to:

1. **Pass attle_scene reference** (as currently proposed) **only for reading displayable state** (e.g., the scenario being run for status updates)

2. **Move battle-start logic out of TestLabScreen** into a callback that the router handles:
   `python
   # In test_lab/screen.py (current line 489, refactored)
   # Old: self.game.battle_scene.start_battle(controller)
   # New:
   if self.scene_callback:
       self.scene_callback("start_test_battle", controller=controller)
   `

3. **Router receives the callback and handles the state change:**
   `python
   # In game/screen_router.py
   def _handle_test_lab_action(self, action, **kwargs):
       if action == "start_test_battle":
           controller = kwargs.get("controller")
           self.battle_scene.start_battle(controller)
           self._switch_scene(GameState.BATTLE, self.battle_scene)
   `

This preserves TestLabScreen's **use of BattleScreen data** (e.g., checking test status) while removing the **direct state-mutation coupling** that violates the architecture.

### Equivalent to Existing Patterns

This follows the same pattern used by BattleScreen itself:
`python
# game/ui/screens/battle_screen.py:436-439
if self.scene_callback:
    self.scene_callback("show_results", results=results, ...)
`

**The callback is the architectural gateway.**

---

## 7. Spot-Check: BattleStateViewer Sizing (Lines 137-138, 623-628)

### Current Issue
TestLabScreen constructs BattleStateViewer with fixed constants:
`python
# game/ui/screens/test_lab/screen.py:137-138
BattleStateViewer(WIDTH, HEIGHT)  # hardcoded DisplayConfig values
`

But TestLabScreen.handle_resize does not forward to the viewer (lines 623-628):
`python
def handle_resize(self, width, height):
    self.screen_width = width
    self.screen_height = height
    self.ui_manager.set_window_resolution((width, height))
    # BattleStateViewer is NOT updated — inconsistency
`

### Proposed Fix in r002
Lines 45, 48 of r002:
- Construct with explicit dimensions: BattleStateViewer(self.screen_width, self.screen_height)
- Forward resize: self.battle_state_viewer.handle_resize(width, height)

### Verdict
This is **correct and good**. The fix closes a real inconsistency and aligns with the convention pattern.

---

## Summary of Findings

| Finding | Layer Violation? | Verdict |
|---------|------------------|---------|
| 1. TestLabScreen → BattleScreen direct reference | **YES** | Violates "strict downward-only" rule by coupling peers in same layer |
| 2. _require_display_surface() helper + pygame.display.get_surface() | **NO** | Established precedent (StrategyGameStateManager); Pygame is third-party, not a layer |
| 3. Deletion of TestExecutionService / TestResultsService | **NO** | True orphans; no documented boundary to collapse; safe to delete |
| 4. BattleStateViewer sizing fix | **NO** | Correct; closes a real inconsistency |
| 5. Screen parameter pattern (width, height, deps, callback) | **NO** | Matches BattleScreen and every other screen exactly |

---

## Recommendations

### REQUIRED CHANGE (Blocking Approval)

Replace direct attle_scene.start_battle() call with callback routing:

`python
# Current (VIOLATES ARCHITECTURE):
self.game.battle_scene.start_battle(controller)

# Proposed (CORRECT):
if self.scene_callback:
    self.scene_callback("start_test_battle", controller=controller)
`

And handle in router:
`python
# In game/screen_router.py _handle_test_lab_action or Game._handle_test_lab_action
if action == "start_test_battle":
    controller = kwargs.get("controller")
    self.battle_scene.start_battle(controller)
    self._switch_scene(GameState.BATTLE, self.battle_scene)
`

### OPTIONAL IMPROVEMENTS (Follow-up)

1. Clarify whether TestLabScreen should hold a attle_scene reference at all, or just access read-only state (test status, scenario metadata) via DTOs from the router instead. Current design allows TestLabScreen to read BattleScreen.engine for display purposes — this is defensible if read-only, but consider whether that state could be passed as a parameter instead.

2. Document in docs/01_ARCHITECTURE.md that UI-layer components do not couple directly; see ScreenRouter routing pattern as the mandated inter-screen communication mechanism.

---

## References

- docs/01_ARCHITECTURE.md § "Layer Structure" (lines 8-42): establishes "strict downward-only dependency flow"
- docs/01_ARCHITECTURE.md § "Dependency Rules" (lines 44-56): defines allowed inter-layer dependencies
- game/screen_router.py (lines 56-127): canonical ScreenRouter pattern with scene callback routing
- game/ui/screens/battle_screen.py (lines 68-89, 436-443): exemplar screen using scene_callback for routing
- game/ui/screens/strategy_game_state_manager.py (lines ~120-150): precedent for direct pygame.display.get_surface() calls
- Projects/active_projects/PROJ-342/plan.md and AgentCoordination/.../testlab_drop_game_handle_r002.md (planning artifacts)
