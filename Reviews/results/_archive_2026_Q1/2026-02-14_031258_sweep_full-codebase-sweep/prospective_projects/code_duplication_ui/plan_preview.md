# Plan: Code Duplication - UI Layer

## Project Information
- **Project ID:** TBD (will be assigned on creation)
- **Created:** 2026-02-14
- **Source:** Sweep 2026-02-14_031258

## Objective

Consolidate duplicated code in the UI layer into shared utilities and base classes.

## Current State

- 3 ColumnManager implementations with overlapping functionality
- HP color calculation in 3 places with inconsistent values
- Number formatting (k/M) in 4+ places
- RaceThemeGallery doesn't extend BaseGallery despite identical pattern
- Various utility patterns duplicated

## Target State

- Single BaseColumnManager base class
- Single get_hp_color() utility function
- Single format_quantity() utility function
- All galleries extend BaseGallery
- Common patterns extracted to utilities

## Phases

### Phase 1: Column Manager Consolidation
**Files to modify:**
- Create `game/ui/shared/base_column_manager.py`
- Refactor `game/ui/screens/column_manager.py`
- Refactor `game/ui/screens/planet_list_columns.py`
- Refactor `game/ui/screens/empire_build_queue_filter_manager.py`

**Design:**
```python
class BaseColumnManager:
    def get_visible_columns(self) -> List[str]
    def toggle_visibility(self, column_id: str) -> None
    def swap_columns(self, col1: str, col2: str) -> None
```

### Phase 2: UI Utility Consolidation
**Files to create/modify:**
- Create `game/ui/utils/color_utils.py`
- Create `game/ui/utils/number_format.py`
- Update all HP color callers
- Update all number format callers

**Functions:**
```python
def get_hp_color(hp_pct: float, is_active: bool = True) -> Tuple[int, int, int]
def format_quantity(value: float, precision: int = 1) -> str
```

### Phase 3: Gallery Consolidation
**Files to modify:**
- `game/ui/panels/base_gallery.py` (add layout variants)
- `game/ui/panels/race_theme_gallery.py` (extend BaseGallery)

### Phase 4: Simulation Layer Duplication
**Files to modify:**
- Extract common ability boilerplate
- Consolidate formula evaluation pattern
- Consolidate validation patterns

### Phase 5: Strategy Layer Duplication
**Files to modify:**
- Extract layer iteration helper
- Consolidate ability extraction pattern

### Phase 6: Service Pattern Cleanup
**Files to modify:**
- Consolidate registry provider access
- Document singleton manager pattern
- Remove draw_stat_bar wrapper

## Checklist

### Phase 1: Column Manager
- [ ] Create BaseColumnManager
- [ ] Migrate column_manager.py
- [ ] Migrate planet_list_columns.py
- [ ] Migrate empire_build_queue_filter_manager.py
- [ ] Update all usages
- [ ] Delete duplicate implementations

### Phase 2: UI Utilities
- [ ] Create color_utils.py
- [ ] Create number_format.py
- [ ] Update ship_stats_renderer.py
- [ ] Update ship_detail_panel.py
- [ ] Update battle_panels.py
- [ ] Update all format_quantity callers

### Phase 3: Gallery
- [ ] Extend BaseGallery for list layout
- [ ] Refactor RaceThemeGallery
- [ ] Remove duplicated _sanitize_object_id

### Phase 4: Simulation
- [ ] Extract ability base helpers
- [ ] Document formula evaluation pattern
- [ ] Consolidate validation helpers

### Phase 5: Strategy
- [ ] Create layer iteration utility
- [ ] Update 7+ files to use utility

### Phase 6: Services
- [ ] Document registry provider pattern
- [ ] Remove draw_stat_bar wrapper
- [ ] Add pattern documentation

## Dependencies

- None - can run independently

## Risks

- API changes may affect many callers
- Visual differences may result from HP color consolidation (verify thresholds)
