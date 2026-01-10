# Agent Prompt: MVVM Phase 3 - Panel Refactoring

## Your Task

Continue the MVVM refactoring of the Ship Builder UI by refactoring the panel classes to consume the `BuilderViewModel` directly instead of using proxy properties through `BuilderSceneGUI`.

## Background

Phase 2 is complete:
- `BuilderViewModel` class created at `game/ui/screens/builder_viewmodel.py`
- ViewModel integrated into `BuilderSceneGUI` with backward-compatible proxy properties
- 16 ViewModel unit tests passing
- All 116 builder tests passing

## Read First

1. **Handoff document:** `Refactoring/mvvm_phase3_handoff.md`
2. **ViewModel source:** `game/ui/screens/builder_viewmodel.py`
3. **Current integration:** `game/ui/screens/builder_screen.py` (lines 66-130, 392-425)

## Execution Steps

### Step 1: Refactor BuilderLeftPanel
File: `ui/builder/left_panel.py`

1. Update constructor signature to accept `viewmodel` (keep `builder` for backward compat during transition)
2. Store `self.viewmodel = viewmodel or builder.viewmodel`
3. Replace all `self.builder.ship` → `self.viewmodel.ship`
4. Replace all `self.builder.template_modifiers` → `self.viewmodel.template_modifiers`
5. Replace all `self.builder.available_components` → `self.viewmodel.available_components`
6. Run tests: `pytest tests/unit/builder/ -k "left" --tb=short`

### Step 2: Refactor BuilderRightPanel
File: `ui/builder/right_panel.py`

1. Same pattern - store viewmodel reference
2. Replace `self.builder.ship` usages
3. Run tests: `pytest tests/unit/builder/ -k "right" --tb=short`

### Step 3: Refactor LayerPanel
File: `ui/builder/layer_panel.py`

1. Same pattern - store viewmodel reference
2. Replace `self.builder.ship` and `self.builder.selected_components` usages
3. Run tests: `pytest tests/unit/builder/ -k "layer" --tb=short`

### Step 4: Update BuilderSceneGUI panel instantiation
File: `game/ui/screens/builder_screen.py`

Update `_create_ui()` to pass `self.viewmodel` to panels.

### Step 5: Final verification
```powershell
pytest tests/unit/builder/ --tb=no -q
pytest tests/repro_issues/ --tb=no -q
```

### Step 6 (Optional): Remove proxy properties
If all tests pass and panels use ViewModel directly, remove proxy properties from `BuilderSceneGUI`:
- Lines ~392-425 (ship, selected_components, template_modifiers, available_components)

## Testing Requirements

- All 116+ builder tests must pass
- All 31 repro_issues tests must pass
- Manual test: launch `python launcher.py`, use Ship Builder

## Success Criteria

1. Panels consume ViewModel directly (not through builder proxy)
2. No regressions in test suite
3. Manual testing confirms Ship Builder works correctly
