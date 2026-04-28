# Phase 7: Migrate Untracked Editor Windows (5 windows) — Behaviour-Change Phase

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-313 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate the 5 editor windows that are currently NOT tracked at all — they have no slot, no `has_modal_open()` clause, no `_is_blocking_ui_element_at()` clause. This phase fixes the click-through bug class structurally by bringing them under the new base class.

**This phase changes behaviour:** these editors will start being seen by `has_modal_open()` (returning True while open) and `_is_blocking_ui_element_at()` (blocking clicks at their rect). Audit any code path that depends on `has_modal_open() == False` while one of these editors is open BEFORE migrating.

---

## Tasks

### Task 7.1: Audit `has_modal_open()` consumer code paths [Medium]
**File:** Read-only — search across `game/ui/`
**Tests:** N/A (audit task)

- [ ] Grep `has_modal_open` across `game/ui/` and list all callers
- [ ] For each caller, determine what it does when `has_modal_open() == True` (typically: skip hotkey processing, skip mouse-event routing to underlying screens, etc.)
- [ ] Determine which (if any) consumers would break or surprise the user if newly returning True while a Food / Atmosphere / Gravity / Water / RadiationShield editor is open
- [ ] Document findings in this file's Notes section. Common consumers expected: scroll-wheel zoom guard, keyboard hotkey handlers, drag-pan handler. All should already correctly defer to modal-open.
- [ ] If any consumer would BREAK (not just defer), flag the design issue here and decide whether to (a) migrate the editors anyway and accept the user-visible change, (b) tweak the consumer to behave correctly, or (c) raise to user before proceeding.
**Notes:** [Filled during audit]

### Task 7.2: Migrate `FoodAllocationEditor` [Medium]
**File:** `game/ui/screens/food_allocation_editor.py`
**Spawn site:** `strategy_event_router.py:294` in `_open_food_allocation_editor()`
**Tests:** New regression test (see Task 7.7) + existing food allocation tests

- [ ] Subclass `StrategyModalWindow`
- [ ] Update `__init__` signature: keep existing `on_close_callback` param for now (backward compat with whatever existing test code may pass it); add `window_manager` keyword forwarding to `super().__init__`
- [ ] Update spawn site at `strategy_event_router.py:294` to pass `window_manager=self.window_manager` (or however the manager is reachable from the router)
- [ ] No slot field to delete (none existed)
- [ ] Run targeted tests — pass
**Notes:**

### Task 7.3: Migrate `AtmosphereTargetEditor` [Medium]
**File:** `game/ui/screens/atmosphere_target_editor.py`
**Spawn site:** `strategy_event_router.py:197` in `_open_atmosphere_editor()`
**Tests:** Targeted + new regression test

- [ ] Same migration steps as Task 7.2
**Notes:**

### Task 7.4: Migrate `GravityTargetEditor` [Medium]
**File:** `game/ui/screens/gravity_target_editor.py`
**Spawn site:** `strategy_event_router.py:234` in `_open_gravity_editor()`
**Tests:** Targeted + new regression test

- [ ] Same migration steps
**Notes:**

### Task 7.5: Migrate `WaterTargetEditor` [Medium]
**File:** `game/ui/screens/water_target_editor.py`
**Spawn site:** `strategy_event_router.py:254` in `_open_water_editor()`
**Tests:** Targeted + new regression test

- [ ] Same migration steps
**Notes:**

### Task 7.6: Migrate `RadiationShieldEditor` [Medium]
**File:** `game/ui/screens/radiation_shield_editor.py`
**Spawn site:** `strategy_event_router.py:274` in `_open_radiation_shield_editor()`
**Tests:** Targeted + new regression test

- [ ] Same migration steps
**Notes:**

### Task 7.7: Add click-blocking regression tests [Medium]
**File:** `tests/integration/ui/test_editor_click_blocking.py` (NEW) or extend an appropriate existing integration test file
**Tests:** `pytest tests/integration/ui/test_editor_click_blocking.py -v`

- [ ] Parametrise across the 5 editor classes (Food, Atmosphere, Gravity, Water, RadiationShield)
- [ ] Per editor: open the editor with a stub spawn site, simulate a `MOUSEBUTTONDOWN` event at strategy-map hex coordinates that would otherwise change selection, route the event through `StrategyEventRouter`, assert the underlying map's selection did NOT change
- [ ] Assertion: `_is_blocking_ui_element_at(point)` returns True when point is within the editor's rect; `has_modal_open()` returns True while editor is alive
- [ ] After `editor.kill()`: `has_modal_open()` returns False, click no longer blocked
**Notes:** Reuse existing test fixtures for strategy-screen setup if possible. The original food-allocation click-through bug from QA Session 20260428_052952 is the canonical repro this test class enforces.

### Task 7.8: Phase verification [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] All 5 editors migrated
- [ ] 5 new regression tests pass (one per editor)
- [ ] Full sharded suite passing — count is 15893 + 5 (or however many new tests landed in Task 7.7); document the new total here
- [ ] Manual smoke: open each of the 5 editors in turn over a planet on the strategy map; while open, click the strategy map at a different hex; confirm map selection did NOT change
**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 8 (Demolition + docs)
