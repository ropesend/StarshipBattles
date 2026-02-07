# PROJ-65: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State of `game/app.py` (759 lines, 43 methods)

**Game Class** is a monolithic orchestrator managing 10 GameStates via 5 major if/elif chains:
1. `_forward_event_to_scene()` — 8 branches routing events to scenes
2. `_handle_resize()` — 8 branches routing resize to scenes
3. `_update_and_draw()` — 10 branches for scene update/draw/action polling
4. `_handle_click()` — 2 branches (Battle, Strategy only)
5. `_handle_scroll()` — 2 branches (Battle, Strategy only)

**Module-level side effects:**
- `argparse` parsing at import time (lines 13-16)
- `pygame.font.init()` + font creation at import (lines 53-56)
- Global `WIDTH, HEIGHT` variables mutated via `global` keyword (lines 43, 70, 558)

**Scene lifecycle inconsistencies:**
- Eager: Builder, BattleSetup, Battle, Strategy, Formation, TestLab (created in `__init__`)
- Lazy: ResearchTree, GalaxyTest (created on demand, guarded with `hasattr`)
- Recreated: Builder (new instance per `start_builder()`), Strategy (new per game start)
- Dialog windows: NewGameSetup, SaveSelection, RaceSetup (pygame_gui windows, not scenes)

### Scene Interface Audit

| Scene | handle_event | update | draw | handle_resize |
|-------|-------------|--------|------|--------------|
| DesignWorkshopScreen | `(event)` | `(dt)` | `(screen)` | MISSING |
| BattleSetupScreen | MISSING | `(events, screen_size)` | `(screen)` | MISSING |
| BattleScreen | MISSING | `(events)` | `(screen)` | `(w,h)` |
| StrategyScreen | `(event)` | `(dt)` | `(screen)` | `(w,h)` |
| FormationEditorScreen | `(event)` | `(dt)` | `(screen)` | `(w,h)` |
| TestLabScreen | `handle_input([events])` | `()` no args | `(screen)` | via `_create_ui()` |
| ResearchTreeScene | `(event)` | `(dt)` | `(screen)` | `(w,h)` |
| GalaxyTestScreen | `(event)` | `(dt)` | `(screen)` | `(w,h)` |

### Constructor Inconsistencies

| Scene | Constructor Args |
|-------|-----------------|
| DesignWorkshopScreen | `(width, height, context: WorkshopContext)` |
| BattleSetupScreen | `()` — no dimensions! |
| BattleScreen | `(width, height)` |
| StrategyScreen | `(width, height, session=None)` |
| FormationEditorScreen | `(width, height, on_return_callback)` |
| TestLabScreen | `(game)` — receives entire Game instance! |
| ResearchTreeScene | `(width, height, on_close_callback=None)` |
| GalaxyTestScreen | `(width, height, on_close_callback=None)` |

## Swarm Findings Summary

### Architecture
- **No circular dependencies:** Game is not imported by any scene. One-directional dependency.
- **Clean layer separation:** Core → Simulation → Strategy → UI. app.py sits at the top.
- **battle_coordinator.py** is a set of free functions that take `game` as parameter, accessing `game._battle_accumulator` and calling `game.start_battle_setup()`.
- **BattleInputHandler** is a static class checking `game.state` and accessing `game.battle_scene` directly.
- **exit_dialog.py** is stateless overlay functions — not a scene.

### Key Patterns to Reuse
- **Protocol pattern**: `game/core/protocols.py` — `@runtime_checkable class IFoo(Protocol)` with TypeGuard helpers
- **Callback pattern**: ResearchTreeScene/GalaxyTestScreen use `on_close_callback` — extend this to all scenes
- **WorkshopContext factory**: `WorkshopContext.standalone()` / `WorkshopContext.integrated()` — good model for scene construction

### Dependencies & Risks
1. **TestLabScreen tight coupling (HIGH)** — Accesses `game.battle_scene`, `game.state`, `game.screen` directly. Most work to decouple.
2. **Strategy→Builder flag pattern (MEDIUM)** — `action_open_design` + `workshop_context_data` polled in 37-line block in app.py lines 643-680.
3. **BattleScreen update(events) signature (MEDIUM)** — Must split into handle_event(event) + update(dt).
4. **BattleCoordinator accumulator (MEDIUM)** — `game._battle_accumulator` tracks cross-frame timing; must move into BattleScreen.

### Opportunities Discovered
- Extracting MenuScene eliminates the MENU special case entirely
- After refactor, adding a new scene requires: create class implementing IScene, add GameState enum value, register in scene callback handler. Zero changes to dispatch code.
- app.py target: <300 lines (from 759), ~15 methods (from 43)

## Design Decisions

### IScene Protocol Design

Minimal protocol — only 4 required methods:
```python
@runtime_checkable
class IScene(Protocol):
    def handle_event(self, event: Any) -> None: ...
    def update(self, dt: float) -> None: ...
    def draw(self, screen: Any) -> None: ...
    def handle_resize(self, width: int, height: int) -> None: ...
```

**Rationale:** `draw(screen)` is universal across all scenes. `handle_event(event)` standardizes the inconsistent `handle_input([events])` / `update(events, size)` patterns. `update(dt)` provides frame-time for animation. `handle_resize(w,h)` handles window resize.

### Scene Communication: Callback Pattern

Replace action flags with a `scene_callback(action, **kwargs)` function passed to scene constructors.

**Before (flag polling):**
```python
# In StrategyScreen:
self.action_open_design = True
self.workshop_context_data = {...}

# In Game._update_and_draw():
if self.strategy_scene.action_open_design:
    self.strategy_scene.action_open_design = False
    # ... 37 lines of context extraction
```

**After (callback):**
```python
# In StrategyScreen:
self.scene_callback("open_builder", context=workshop_context)

# In Game._handle_scene_action():
def _handle_scene_action(self, action, **kwargs):
    if action == "open_builder":
        self.start_builder(return_to=GameState.STRATEGY, context=kwargs["context"])
```

**Rationale:** Explicit, testable, no polling overhead, no risk of missed flags.

### Menu as Scene

MenuScene implements IScene. Game always has `self.active_scene` pointing to a valid scene. No special-casing for MENU state.

### WIDTH/HEIGHT as Instance State

Replace module-level `WIDTH, HEIGHT` globals with `self.width, self.height` on Game. Passed to scenes via constructors and `handle_resize()`.

See [decisions.md](decisions.md) for the full log with rationale.
