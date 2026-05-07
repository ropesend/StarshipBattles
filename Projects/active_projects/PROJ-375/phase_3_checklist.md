# Phase 3: UI-layer duplication consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-375 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate 3 verified UI-layer duplication clusters (DUP-X-03, DUP-X-04, Cluster 6) identified by audit `2026-05-05_185819_audit_shrink`.

---

## Tasks

### Task 3.1: Workshop dropdown handler dispatch (DUP-X-03) [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/ui/screens/test_workshop_event_router.py`

The 5 dropdown handlers at lines 441, 464, 493, 505, 517 share most of their structure. Movement and targeting are pure clones (options-list lookup + setter); role uses a registry-loop resolution; class and vehicle_type share a confirmation-dialog pattern with different sizing/text. Replace with a config-driven dispatcher.

**Dispatcher shape (flagged by both verification passes):** The dispatcher is **not** a single uniform call — pass 2 confirmed two distinct strategies are needed:
- A **resolver-based** strategy for movement/targeting/role. Movement/targeting use options-list lookup; role uses registry-loop iteration. Parameterize the resolver function, not just the setter name.
- A **confirmation-dialog** strategy for class/vehicle_type. They differ in dialog sizing (600x400 vs 400x200) and warning text — config must carry both.

- [ ] Define dropdown-handler config (e.g., `dict[str, DropdownConfig]`) capturing options-source, resolver, viewmodel-setter, optional confirmation
- [ ] Replace `_handle_movement_dropdown` (line 493) with a config-driven dispatch entry
- [ ] Replace `_handle_targeting_dropdown` (line 505) with a config-driven dispatch entry
- [ ] Replace `_handle_role_dropdown` (line 517) with a config-driven dispatch entry (uses registry-loop resolver)
- [ ] Replace `_handle_class_dropdown` (line 441) with a config-driven dispatch entry (with confirmation dialog config)
- [ ] Replace `_handle_vehicle_type_dropdown` (line 464) with a config-driven dispatch entry (with confirmation dialog config)
- [ ] Update event-router dispatch to call the unified handler
- [ ] Verify: `pytest tests/unit/ui/screens/test_workshop_event_router.py` passes
- [ ] Verify: LOC delta ≈ -50

**Notes:**

---

### Task 3.2: Extract `ListWindowBase` for planet/star list windows (DUP-X-04) [Medium]
**Files:** `game/ui/screens/planet_list_window.py`, `game/ui/screens/star_list_window.py`, plus a new mixin/base in `game/ui/screens/`
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window.py tests/unit/ui/screens/test_star_list_window.py`

Both `update()` methods (planet 541-573, star 389-421) follow an identical 4-step pattern: scrollbar → slider sync → header sort/swap → preset dropdown. Both `_set_all_filters` / `_toggle_filter` helpers are also structurally identical. Both classes already inherit from `DataListWindowMixin` and `StrategyModalWindow` — extend the existing mixin or add a sibling rather than introducing a third layer.

- [ ] Decide: extend `DataListWindowMixin` (recommended) vs new `ListWindowUpdateMixin` sibling — record choice in `decisions.md`
- [ ] Implement the shared `_update_template(slider_fields, column_manager, preset_manager)` (or equivalent) in the chosen home
- [ ] Implement shared `_set_all_filters` / `_toggle_filter` in the same place
- [ ] Migrate `PlanetListWindow.update()` (lines 541-573) to call the shared template; keep its `_sync_slider_text` and filter-helper specifics
- [ ] Migrate `StarListWindow.update()` (lines 389-421) to call the shared template; keep its `_sync_slider_text` and filter-helper specifics
- [ ] Verify: `pytest tests/unit/ui/screens/test_planet_list_window.py tests/unit/ui/screens/test_star_list_window.py` passes
- [ ] Verify: LOC delta ≈ -60

**Notes:**

---

### Task 3.3: Extract shared `_rebuild_modifier_icons` (Cluster 6) [Medium]
**File:** `game/ui/screens/builder/structure_list_items.py`
**Tests:** `pytest tests/unit/ui/screens/builder/test_structure_list_items.py`

`IndividualComponentItem._rebuild_modifier_icons` (line 195) and `LayerComponentItem._rebuild_modifier_icons` (line 472 — note: the source audit miscalls this `GroupComponentItem`) are functionally identical for ~40 lines, with only one comment differing on line 484. Extract to a shared static method or mixin.

- [ ] Choose extraction shape: shared static helper vs mixin (record in `decisions.md`)
- [ ] Implement shared `_rebuild_modifier_icons` in chosen location (private module-level function or `ComponentItemBase` mixin)
- [ ] Replace `IndividualComponentItem._rebuild_modifier_icons` (lines 195-237) with delegating call
- [ ] Replace `LayerComponentItem._rebuild_modifier_icons` (lines 472-514) with delegating call
- [ ] Verify: `pytest tests/unit/ui/screens/builder/test_structure_list_items.py` passes
- [ ] Verify: LOC delta ≈ -40

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-05_185819_audit_shrink/`. See [findings/source_audit.md](findings/source_audit.md) for the link._
