# Phase 3: Build Queue Screen - Layout Restructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-69 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Reorganize the build queue modal to add a queue selector column and support multiple queue sources.

**New Layout:**
```
┌─────────────────────────────────────────────────────────────────────┐
│ Context Rpt  │ Queue Selector  │ Build Queue    │ Design Report    │
│ (480w)       │ (200w)          │ (flexible w)   │ (400w)           │
│ top-left     │ full height     │ full height    │ full height      │
│              │ scrollable      │ shows active   │                  │
├──────┬───────┤ toggle buttons  │ queue contents │                  │
│Filter│Avail  │ for multi-sel   │                │                  │
│(200) │Designs│                 │                │                  │
│      │(280)  │                 │                │                  │
├──────┴───────┴─────────────────┴────────────────┴──────────────────┤
│ Bottom Bar (Close, Turn info)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Tasks

### Task 3.1: Update BuildQueueScreen constructor to accept hex context [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test + existing tests

- [ ] Add new constructor parameters: `hex_coord=None`, `galaxy=None`, `empire=None`
- [ ] When hex context provided, call `collect_build_queues_at_hex(hex_coord, galaxy, empire)` to populate `self.queue_sources: List[BuildQueueSource]`
- [ ] When only `build_context` provided (backward compat during transition), create a single BuildQueueSource from it
- [ ] Add state tracking:
  - `self.selected_queue_indices: Set[int]` - indices into `queue_sources` list
  - `self.active_queue_source: Optional[BuildQueueSource]` - the single selected queue (for content viewing)
- [ ] Default: select first queue source (index 0)
- [ ] Remove `self.planet = build_context` backward-compat alias (line 59)

**Notes:** The constructor should work both ways during transition: old callers pass build_context, new callers pass hex context. Eventually old path removed in Phase 5.

---

### Task 3.2: Create queue selector panel [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test

- [ ] Add `_create_queue_selector_panel()` method
- [ ] Position: to the right of context report, full height from top to bottom bar
  - `x = 10 + context_report_width + 10` (= ~500)
  - `y = 10`
  - `width = 200`
  - `height = screen_height - 10 - 80` (same as build queue panel)
- [ ] Header: "Build Queues" (UITextBox, 30px height)
- [ ] Scrollable container below header for queue entries
- [ ] For each `BuildQueueSource` in `self.queue_sources`, create a row:
  - UIPanel row (height 45px, width=panel_width-20)
  - Toggle button or clickable panel with queue `display_name`
  - Item count label: `f"({len(source.construction_queue)} items)"`
  - Visual indicator for selected state (highlight/border)
- [ ] Store queue selector UI elements for event handling

**Notes:** Use button toggle pattern from `planet_list_window.py` for selection visual feedback.

---

### Task 3.3: Adjust panel positions for new layout [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test at 1920x1080

- [ ] Reduce context report width: `report_width = 480` (was 580, line 130)
- [ ] Queue selector panel: `x = 500, width = 200, full height`
- [ ] Adjust filter panel left to remain at `x = 10` (unchanged)
- [ ] Adjust filter panel width to `200` (unchanged)
- [ ] Adjust available designs panel:
  - `panel_left = 220` (unchanged: 10 + 200 + 10)
  - `panel_width = 280` (was 360, reduced to fit)
- [ ] Adjust build queue panel:
  - `panel_left = 10 + 480 + 10 + 200 + 10 = 710` (after context report + queue selector)
  - `panel_width = screen_width - 710 - 400 - 20` (remaining space before design report)
  - Minimum width check: `if panel_width < 250: panel_width = 250`
- [ ] Design report: keep at `screen_width - 410` (unchanged, 400w)
- [ ] Bottom bar: unchanged
- [ ] Verify layout fits at 1920x1080 (710 + 250min + 420 = 1380 < 1920)
- [ ] Update all `_create_*_panel` methods with new coordinates

**Notes:** The key coordinate changes: context report narrower (480), queue selector inserted (200w), available designs narrower (280), build queue shifts right.

---

### Task 3.4: Wire up queue selector to build queue display [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual test

- [ ] Add `_on_queue_selected(index: int)` method:
  - Single click: `self.selected_queue_indices = {index}`, set `self.active_queue_source = self.queue_sources[index]`
  - Call `_refresh_queue_display()` and `_refresh_queue_selector()` (update visual selection)
- [ ] Add `_on_queue_toggled(index: int)` method (ctrl+click or checkbox):
  - Toggle index in `self.selected_queue_indices`
  - If exactly 1 selected: set `active_queue_source` and show contents
  - If multiple selected: set `active_queue_source = None`, show multi-select message
  - If none selected: select first queue (prevent empty selection)
- [ ] Update `_refresh_queue_display()`:
  - When `active_queue_source` is set: read from `self.active_queue_source.construction_queue` (instead of `self.build_context.construction_queue`)
  - When `active_queue_source` is None (multi-select): show message "Adding to N queues" with list of selected queue names
- [ ] Add `_refresh_queue_selector()` method to update visual selection state of queue list items
- [ ] Update queue item count badges when queue contents change

**Notes:** This is the core interaction logic. Single-select behaves identically to current system. Multi-select is additive behavior.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual visual test: queue selector appears and responds to clicks
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
