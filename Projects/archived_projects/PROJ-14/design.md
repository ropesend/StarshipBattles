# PROJ-14: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Dead Code Targets Verified
| Target | Status | Notes |
|--------|--------|-------|
| `Debugging/Marked_for_Deletion_2026-01-20/` | MISSING | Already deleted - skip |
| `Marked_For_Deletion_2026-01-21_07-33/` | EXISTS | 95+ test artifacts |
| `MagicMock/` | EXISTS | 4 JSON mock files |
| Log files (5) | ALL EXIST | battle.log, combat_lab.log, etc. |
| Debug tools (14) | ALL EXIST | All in Tools/ directory |

### Critical Discovery
`Tools/formation_editor.py` is imported by `game/app.py` (line 24) - this is a **production dependency**, NOT a debug tool. Do not delete.

### Commented Code Locations
| File | Lines | Type | Safe? |
|------|-------|------|-------|
| `test_lab_scene.py` | 3657-3741 | `_draw_seed_controls_OLD()` | YES |
| `test_lab_scene.py` | 4 locations | traceback imports | REPLACE with logger |
| `game/core/logger.py` | Line 38 | Commented code | FALSE REPORT - doesn't exist |
| `game/core/profiling.py` | Line 108 | Debug log | YES |
| `test_example_scenarios.py` | 93-99 | Test stubs | YES |
| `test_pdc.py` | 130-131 | Debug prints | YES |
| `process_planet_images.py` | 28-32 | Old code | YES |

## Swarm Findings Summary

### Architecture
- **Two UI Layers**: `/ui/` (legacy pygame) and `/game/ui/` (modern pygame_gui)
- `ui/components.py` contains Button, Label, Slider - only Button is used
- No circular dependencies detected
- Cross-layer imports exist but are acceptable (ui/builder ↔ game/ui/screens)

### Key Patterns to Reuse
- **UIButton Creation**: `pygame_gui.elements.UIButton(rect=pygame.Rect(...), text=..., manager=...)`
- **Event Handling**: Check `event.type == pygame_gui.UI_BUTTON_PRESSED`, compare `event.ui_element`
- **UIManager Lifecycle**: Create once, pass to children, call `process_events()`, `update()`, `draw_ui()`
- **Logger Usage**: `from game.core.logger import log_error; log_error(f"Error: {e}")`

### Dependencies & Risks

1. **Button Import Chain** - `game/app.py` → `ui` → `ui.components`
   - Mitigation: Complete all migrations BEFORE deleting components.py

2. **Main Menu Critical Path** - 10 buttons control all game entry
   - Mitigation: Test each button click after migration

3. **Window Resize** - pygame_gui handles automatically
   - Mitigation: Call `set_window_resolution()` and recreate buttons

4. **test_lab_scene.py Monolith** - 4,146 lines
   - Mitigation: Careful, targeted changes only

### Button Migration Scope

| File | Instances | Priority |
|------|-----------|----------|
| `game/app.py` | 10 menu buttons | CRITICAL |
| `ui/test_lab_scene.py` | 4 (JSONPopup, ConfirmationDialog, back) | HIGH |
| `tests/unit/ui/test_ui_widgets.py` | 4 tests | DELETE |
| `Tools/component_manager.py` | 5 | SKIP (per user decision) |
| `Tools/component_graphic_picker.py` | 1 | SKIP (per user decision) |

### Opportunities Discovered
- Label and Slider classes in ui/components.py are unused - delete with Button
- Test file `tests/unit/ui/test_ui_widgets.py` tests only legacy widgets - delete entirely

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
