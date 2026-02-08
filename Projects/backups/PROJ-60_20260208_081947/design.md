# PROJ-60: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State
- `galaxy_test_screen.py` is 1160 lines containing a single `GalaxyTestScreen` class
- Three modes: MENU (mode selection), GALAXY (galaxy layout testing), SYSTEM (star system inspector)
- Only imported by `game/app.py` (line 31)
- No existing unit tests (it's a developer testing tool)
- Uses `Camera` from `game/ui/renderer/camera.py` for pan/zoom
- Heavy use of `pygame_gui` for sidebar UI elements

### Method Inventory (by responsibility)
| Category | Methods | ~Lines |
|----------|---------|--------|
| UI Creation | `_create_menu_ui`, `_create_galaxy_ui`, `_create_system_ui`, `_clear_ui`, `_get_blueprint_options` | 330 |
| Galaxy Generation | `_generate_galaxy` | 86 |
| System Generation | `_generate_system` | 80 |
| Galaxy Rendering | `_draw_galaxy`, `_draw_warp_lanes` | 65 |
| System Rendering | `_draw_system` | 88 |
| Inspector/Formatting | `_update_inspector_panel`, `_format_star_info`, `_format_planet_info`, `_get_classification_reason`, `_handle_system_click` | 120 |
| Camera | `_center_camera_on_galaxy`, `_center_camera_on_system` | 65 |
| Lifecycle | `__init__`, `update`, `draw`, `handle_event`, `handle_resize`, `handle_input`, mode transitions | 160 |

## Architecture Decision: 4-Module Package

### Design Pattern: Mode Helper Classes
Each mode module exposes a helper class that receives a reference to the screen:

```python
class GalaxyModeHelper:
    def __init__(self, screen):
        self.screen = screen  # Access to camera, ui_manager, canvas dims

    def create_ui(self) -> list:  # Returns list of UI elements
    def generate(self):           # Galaxy generation
    def draw(self, surface):      # Galaxy rendering
    def get_buttons(self) -> dict: # {button: callback} mapping for dispatch
```

### Key Patterns to Reuse
- **`formation/` package pattern**: `__init__.py` with docstring, absolute imports, `__all__`
- **Composition over inheritance**: screen.py holds mode helper instances, delegates to them

### Dependencies & Risks
1. **Circular imports** - Mitigated by constants.py being leaf module, mode modules not importing each other
2. **Shared state** - Mode modules access camera, ui_manager, canvas_width via screen reference
3. **UI element references** - Mode helpers own their button references; screen dispatches via `get_buttons()`

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
