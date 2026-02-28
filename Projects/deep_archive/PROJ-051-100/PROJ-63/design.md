# PROJ-63: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

**Target file:** `game/ui/screens/build_queue_screen.py` — 945 lines, single `BuildQueueScreen` class.
**Goal:** Reduce to under 500 lines by extracting 3 modules into `game/ui/panels/`.
**Test baseline:** 6248 passed, 0 failed (2026-02-06).

### Current Method Groups

| Group | Methods | Lines | Description |
|-------|---------|-------|-------------|
| Init + Layout | `__init__`, 7x `_create_*` | 1-314 | Panel creation, layout math |
| Portrait Loading | `_load_design_portrait`, `_load_queue_item_portrait` | 404-572 | Image loading, placeholders |
| Items/Queue Display | `_refresh_items_list`, `_refresh_queue_display`, `_load_designs_by_category` | 316-537 | Populating scrollable lists |
| Queue Operations | `_set_category`, `_add_to_queue`, `_refresh_design_report` | 574-664 | Business logic |
| Event Handling | `handle_event` | 678-847 | Button routing, drag-drop |
| Rendering | `draw`, `update`, screenshot methods | 849-945 | Drawing |

### Inbound Dependencies (3 production files)
- `game/ui/screens/strategy_screen.py` — creates instance
- `game/ui/screens/strategy_input_handler.py` — routes events
- `game/core/screenshot_manager.py` — calls `draw()`

### Test Files (9 files)
- `tests/integration/ui/build_queue_screen/` (conftest, test_basics, test_portrait_logging)
- `tests/integration/ui/test_build_queue_drag_drop.py`
- `tests/integration/ui/test_build_queue_formatting.py`
- `tests/integration/ui/test_build_queue_design_report.py`
- `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
- `tests/repro_issues/test_bug_15_screenshot_strategy.py`
- `tests/repro_issues/test_bug_17_drag_preview.py`

## Swarm Findings Summary

### Architecture
- Monolithic screen pattern, pre-decomposition
- Already uses 2 extracted panels: `PlanetReportPanel`, `DesignReportPanel`
- Drag-drop is a 3-phase state machine (MOUSEDOWN/MOUSEMOTION/MOUSEUP) with threshold
- Portrait loading has filesystem I/O, regex, pygame transforms — ideal extraction
- Queue operations contain BUG-24 diagnostic logging

### Key Patterns to Reuse
- **Panel constructor**: `(manager, rect, container=None, **kwargs)` — all `game/ui/panels/`
- **Callback communication**: Parent passes callbacks; panels call on user actions
- **Update methods**: `panel.update_*()` for parent-to-panel state
- **InteractionController**: Builder's `interaction_controller.py` (161 lines) — drag-drop standalone

### Dependencies & Risks
1. **Drag state across event types** — Handler must own `dragged_item`, `drag_start_pos`, `_pending_queue_index`
2. **Portrait loading called from 3 places** — Must be shared dependency
3. **Queue ops mutate `planet.construction_queue`** — Preserve existing pattern
4. **9 test files** — Public API must stay accessible or tests updated

### Opportunities Discovered
- Duplicated color_map in `_load_design_portrait()` and `_load_queue_item_portrait()` — consolidate
- `handle_event()` at 170 lines — extraction naturally decomposes it

## Extraction Plan

### Module 1: `build_queue_portraits.py` (~120 lines)
**Class:** `BuildQueuePortraitLoader`
**Extracts:** `_load_design_portrait()`, `_load_queue_item_portrait()`, shared color maps

### Module 2: `build_queue_drag_handler.py` (~150 lines)
**Class:** `BuildQueueDragHandler`
**Extracts:** Drag-drop state + logic from `handle_event()`

### Module 3: `build_queue_controller.py` (~130 lines)
**Class:** `BuildQueueController`
**Extracts:** `_load_designs_by_category()`, `_add_to_queue()`, `_refresh_design_report()`, `_set_category()`

### Remaining in `build_queue_screen.py` (~400-450 lines)
- `__init__` + 7x `_create_*` methods (~220 lines)
- `_refresh_items_list()`, `_refresh_queue_display()` (~120 lines)
- Thin `handle_event()` router (~40 lines)
- `draw()`, `update()`, close, screenshot (~65 lines)

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
