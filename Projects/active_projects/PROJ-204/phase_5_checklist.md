# Phase 5: Workshop UI Cleanup

**Findings:** CQ-61, CQ-63, CQ-67, CQ-69, CQ-74
**Effort:** Simple-Medium
**Goal:** Eliminate workshop UI widget pattern duplication

## Tasks

### 5.1 Extract modifier range logic (CQ-61)
- [ ] Create `ModifierControlRow._get_local_bounds()` method returning (min, max, clamped_value)
- [ ] Use in `update()` method
- [ ] Use in `handle_event()` method
- [ ] Run builder-related tests

### 5.2 Create panel bootstrap factory (CQ-63)
- [ ] Create `PanelFactory.create_titled_panel(rect, manager, title, object_id)` helper
- [ ] Returns (panel, title_label) tuple
- [ ] Refactor `BuilderRightPanel` to use factory
- [ ] Refactor `LayerPanel` to use factory
- [ ] Refactor `BuilderLeftPanel` to use factory
- [ ] Run builder-related tests

### 5.3 Consolidate enable/disable logic (CQ-67)
- [ ] Create `ModifierControlRow._set_controls_enabled(enabled)` method
- [ ] Replace both enable and disable code paths in `update()`
- [ ] Run builder-related tests

### 5.4 Create UIElementRegistry helper (CQ-69)
- [ ] Create `UIElementRegistry` class with `register()`, `kill_all()`, `clear()` methods
- [ ] Apply to `ModifierControlRow._clear_ui()`
- [ ] Apply to `PresetUI.clear()`
- [ ] Apply to other panels with cleanup patterns
- [ ] Run builder-related tests

### 5.5 Consolidate event constants (CQ-74)
- [ ] Merge `WeaponsEvents` constants into `BuilderEvents` (or create unified `UIEvents`)
- [ ] Update all event subscribers/publishers
- [ ] Run builder-related tests

## Completion Checklist
- [ ] All tasks above completed
- [ ] Full test suite passes
- [ ] Workshop builder UI verified visually (manual check)
