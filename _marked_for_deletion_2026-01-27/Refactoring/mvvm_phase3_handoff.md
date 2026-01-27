# MVVM Phase 3 Handoff: Panel Refactoring

## Context

The Ship Builder UI has been partially refactored to MVVM architecture:
- **Phase 1** ✓ Planning and analysis complete
- **Phase 2** ✓ `BuilderViewModel` created and integrated
- **Phase 3** ◦ Panel refactoring to consume ViewModel (THIS TASK)

## Current State

### New Files Created
| File | Purpose |
|------|---------|
| `game/ui/screens/builder_viewmodel.py` | Central ViewModel (287 lines) |
| `tests/unit/builder/test_builder_viewmodel.py` | 16 unit tests |

### Architecture
```
BuilderSceneGUI (View Coordinator)
    ├── viewmodel: BuilderViewModel (state management)
    │       ├── ship (observable)
    │       ├── selected_components (observable)
    │       ├── template_modifiers (observable)
    │       └── dragged_item (observable)
    ├── event_bus: EventBus (pub/sub)
    └── Panels (still use builder reference, need refactoring):
            ├── BuilderLeftPanel
            ├── BuilderRightPanel
            ├── LayerPanel
            └── ModifierEditorPanel
```

### Backward Compatibility
`BuilderSceneGUI` has proxy properties that delegate to ViewModel:
```python
@property
def ship(self):
    return self.viewmodel.ship
```
This allows existing code to work, but panels should be updated to use ViewModel directly.

---

## Phase 3 Tasks

### 1. Refactor BuilderLeftPanel
**File:** `ui/builder/left_panel.py` (477 lines)

**Current:** Constructor takes `builder` reference, accesses `builder.ship`, `builder.template_modifiers`

**Target:** Accept `viewmodel` parameter OR access `builder.viewmodel`

**Changes:**
1. Update constructor to store `viewmodel` reference
2. Replace `self.builder.ship` → `self.viewmodel.ship`
3. Replace `self.builder.template_modifiers` → `self.viewmodel.template_modifiers`
4. Replace `self.builder.available_components` → `self.viewmodel.available_components`

### 2. Refactor BuilderRightPanel
**File:** `ui/builder/right_panel.py` (565 lines)

**Current:** Uses `builder.ship` for stats display

**Target:** Use `viewmodel.ship`, already subscribes to `SHIP_UPDATED` events

**Changes:**
1. Update constructor to store `viewmodel` reference
2. Replace `self.builder.ship` → `self.viewmodel.ship`
3. `on_ship_updated()` already receives ship from event - minimal changes

### 3. Refactor LayerPanel
**File:** `ui/builder/layer_panel.py` (505 lines)

**Current:** Uses `builder.ship`, `builder.selected_components`

**Target:** Use `viewmodel` properties

**Changes:**
1. Update constructor to store `viewmodel` reference
2. Replace `self.builder.ship` → `self.viewmodel.ship`
3. Replace `self.builder.selected_components` → `self.viewmodel.selected_components`
4. Consider subscribing to `SELECTION_CHANGED` instead of polling

### 4. Update ModifierEditorPanel
**File:** `game/ui/panels/builder_widgets.py` (182 lines)

**Current:** Uses callback pattern with `on_change_callback`

**Changes:** May not need changes - already uses callback pattern

### 5. Update BuilderSceneGUI._create_ui
**File:** `game/ui/screens/builder_screen.py`

After refactoring panels, update their instantiation to pass `viewmodel`:
```python
# Before
self.left_panel = BuilderLeftPanel(self, self.ui_manager, rect, event_bus=self.event_bus)

# After
self.left_panel = BuilderLeftPanel(self.viewmodel, self.ui_manager, rect, event_bus=self.event_bus)
```

### 6. Remove Proxy Properties (Final Step)
Once all panels use ViewModel directly, remove proxy properties from `BuilderSceneGUI`:
- `ship`
- `selected_components`
- `template_modifiers`
- `available_components`

---

## Testing Requirements

### Regression Tests
```powershell
# All builder tests must pass
pytest tests/unit/builder/ --tb=no -q

# All repro tests must pass
pytest tests/repro_issues/ --tb=no -q
```

### Manual Testing Checklist
1. Launch Ship Builder (`python launcher.py`)
2. Add components from left panel
3. Select components in layer list
4. Multi-select with Ctrl+click
5. Remove components
6. Modify component modifiers
7. Save/load ship
8. Clear design
9. Change ship class

---

## Key ViewModel Methods

| Method | Purpose |
|--------|---------|
| `viewmodel.ship` | Get/set current ship |
| `viewmodel.selected_components` | Get selection list |
| `viewmodel.select_component(sel, append, toggle)` | Update selection |
| `viewmodel.template_modifiers` | Get/set template modifiers |
| `viewmodel.notify_ship_changed()` | Emit SHIP_UPDATED after mutations |
| `viewmodel.sync_modifiers_to_selection()` | Copy modifiers to all selected |
| `viewmodel.clear_design()` | Clear ship (preserves hull) |

---

## Risks & Gotchas

1. **Test fixtures bypassing __init__**: Tests using `BuilderSceneGUI.__new__()` need to initialize `viewmodel` manually (see `test_bug_13_clear_removes_hull.py` for example)

2. **Event emission timing**: When updating ship state, call `viewmodel.notify_ship_changed()` to emit events

3. **Backward compatibility**: Keep proxy properties until ALL usages are migrated, then remove in final step

4. **Selection homogeneity**: ViewModel enforces that multi-selection only works with same component type
