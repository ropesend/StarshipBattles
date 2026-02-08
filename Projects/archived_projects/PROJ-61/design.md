# PROJ-61: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.

## Initial Analysis

`workshop_screen.py` is 943 lines. It has already had significant extraction:
- EventRouter, ViewModel, DataLoader, Context, InteractionController, SchematicView
- All sub-panels (Left, Right, Layer, Detail, Weapons, Modifier)

Remaining bulk: Ship I/O workflows (~175 lines), data reload UI refresh (~95 lines), dropdown manipulation (~60 lines), dead code (~35 lines).

## Extraction Pattern: Composition with Dependency Injection

All extractions follow the same pattern established by `WorkshopEventRouter`:

```python
class WorkshopShipIO:
    def __init__(self, context, ui_manager, ...):
        self.context = context
        # Store dependencies - NO reference to DesignWorkshopScreen itself
```

Key differences from EventRouter:
- EventRouter holds a `gui` reference to the whole screen
- New classes receive **only the specific dependencies they need**
- Callbacks for UI refresh passed as callables, not screen reference

## WorkshopShipIO Design

### Dependencies
- `context: WorkshopContext` - mode, registries, savegame_path, empire_id, built_designs
- `ui_manager` - for DesignSelectorWindow creation
- `screen_width, screen_height` - for window sizing
- `ship_io_adapter: ShipIOAdapter` - standalone save/load
- `design_loader_adapter: DesignLoaderAdapter` - design-to-ship conversion
- `show_error: Callable` - error display callback
- `apply_loaded_ship: Callable` - callback after successful load
- `set_target: Callable` - callback for weapons_report_panel.set_target

### Public API
- `save_ship(ship)` - Context-aware save (standalone or integrated)
- `load_ship()` - Context-aware load (standalone or integrated)
- `select_target()` - Context-aware target selection

### Private
- `_prompt_design_name(default_name)` - Tkinter dialog (with tk_root module-level)

## Right Panel Dropdown Methods

Add to `BuilderRightPanel`:
- `update_class_dropdown(new_class, valid_classes)` - Kill/recreate class dropdown
- `update_vehicle_type_dropdown(new_type, valid_types)` - Kill/recreate type dropdown
- `update_dropdowns_for_data_reload(default_class, vehicle_classes)` - Combined update

These follow the existing `refresh_controls()` pattern but are granular for specific update scenarios.

## Dependencies & Risks

1. **Callback closures in _load_ship** - Inner functions `on_design_selected` and `on_target_selected` capture `self`. Solution: pass `apply_loaded_ship` and `set_target` as constructor callbacks.
2. **38 test files** reference builder/workshop - Thin wrappers on workshop_screen preserve the existing API so event router and tests don't need changes.
3. **DesignLibrary creation** requires savegame_path and empire_id from context - Pass context directly, not individual fields.
