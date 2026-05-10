# Phase 1: Strategy data helper

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-315 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `ComponentInstanceView` frozen dataclass and
`ShipInstance.iter_all_components_by_layer()` helper. Cover with
unit tests including the regression cases that resurrect the
existing latent parser bug.

---

## Tasks

### Task 1.1: Add `ComponentInstanceView` dataclass [Simple]
**File:** `game/core/component_state.py`
**Tests:** `pytest tests/unit/core/test_component_state.py`

- [x] Add a frozen dataclass `ComponentInstanceView` directly below
  the existing `ComponentState` definition. Fields:
  ```python
  @dataclass(frozen=True)
  class ComponentInstanceView:
      component_id: str
      instance_index: int
      current_hp: int
      max_hp: int
      is_active: bool
  ```
- [x] Export it via the module's `__all__` if present.
- [x] Add a class docstring explaining: "Read-only snapshot for UI
  display. When backing `ComponentState` is missing for a key,
  callers should default to `current_hp == max_hp`, `is_active = True`."
- [x] Add basic unit tests in
  `tests/unit/core/test_component_state.py`:
  - Construction sets all five fields.
  - Frozen — assignment raises `FrozenInstanceError`.
  - Equality on identical fields.

**Notes:**

---

### Task 1.2: Add `iter_all_components_by_layer()` to `ShipInstance` [Medium]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/test_ship_instance_damage.py tests/unit/strategy/test_ship_instance.py`

- [x] Place the new method directly after the existing
  `get_components_by_layer()` (~line 549) so the read-helpers cluster
  is grouped together.
- [x] Signature:
  ```python
  def iter_all_components_by_layer(self) -> Dict[str, List[ComponentInstanceView]]:
      """Return every component on this ship grouped by layer.

      Walks design_data['layers'] in source order; joins each entry
      with self.components via component_state_key(component_id, instance_index).
      Falls back to ComponentInstanceView(current_hp=max_hp, is_active=True)
      when the key is missing (legacy saves, freshly materialised ships).

      The HULL layer is filtered out — the Fleet Report panel does not
      display it. Other unrecognised layer names pass through.
      """
  ```
- [x] Use `from game.core.component_state import ComponentInstanceView, component_state_key`.
- [x] Walk `design_data.get('layers', {}).items()`; for each layer,
  for each component entry, build a counter to assign
  `instance_index = 0, 1, 2, ...` per `component_id` within that
  layer. Look up `self.components.get(key)` and either build the
  view from the state or use the default.
- [x] Skip the HULL layer at the iteration step (`if layer_name == 'HULL': continue`).
- [x] Determine `max_hp` for the default-view fallback. The
  triage notes that `ComponentState` already records `max_hp`. For
  the default-view path (state missing entirely), fall back to a
  registry lookup if available, else `0` with a `# Intentional broad
  catch: registry may be absent in legacy save context` comment.
  Confirm the established pattern by reading
  `_build_full_hp_components_from_design()` in
  `ship_instance.py:82` (referenced by Risk Assessor).
- [x] Tests in
  `tests/unit/strategy/test_ship_instance_damage.py` (or new
  `test_ship_instance_iter_components.py` if file size warrants):
  1. Pristine ship: every layer in design_data appears (except
     HULL); every instance shows `current_hp == max_hp`,
     `is_active == True`.
  2. Partially damaged ship: per-instance values match the
     `ComponentState` entries; missing entries default correctly.
  3. HULL filter: a design with a HULL layer never appears in the
     returned dict.
  4. **Regression for parser bug:** a component_id containing a
     numeric suffix (`reactor_mark_2`) round-trips to the right
     view — `component_id == 'reactor_mark_2'` and
     `instance_index == 0`. The existing `ship_detail_panel.py`
     `_`-split bug never reaches the new view because we use
     `ComponentInstanceView.component_id` directly.
  5. Empty `design_data['layers']`: returns `{}` (no crash).
  6. `instance_index` numbering: 4 identical engines yield
     indices `0, 1, 2, 3`.
- [x] Verify: `pytest tests/unit/strategy/test_ship_instance_damage.py tests/unit/strategy/test_ship_instance.py` green.

**Notes:**

---

### Task 1.3: Validate against full sharded suite [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run the full sharded suite. Baseline: 15893 passed.
- [x] After Phase 1: expected 15893 + (Task 1.1 + 1.2 new tests, ~10–13 new) → ~15903–15906 passed, 0 failed.
- [x] If any unrelated tests fail, investigate and document — do not
  proceed to Phase 2 with a broken baseline.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked.
- [x] Update status at top of this file to `Complete`.
- [x] Update plan.md phase table row to `Complete`.
- [x] Update plan.md Current State to point to Phase 2.
- [x] Run `python Projects/scripts/validate_phase.py PROJ-315 1`.
