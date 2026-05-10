# Phase 3: C2 — Migrate FoodAllocationEditor to multi-resource preview

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-291 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the FoodAllocationEditor runtime crash on `EconomyConfig.food_per_pop_per_turn` (deleted by PROJ-286). Migrate the editor to iterate `population_consumption: Dict[str, float]` and show per-resource preview rows. Migrate the 13 broken test fixtures. Retire the `population_food_resource` shim (auto-fix for prior-audit m4) if no remaining callers.

---

## Tasks

### Task 3.1: Read the editor + understand the consumption-preview contract [Simple]
**File:** [game/ui/screens/food_allocation_editor.py](game/ui/screens/food_allocation_editor.py)
**Tests:** None (read-only orientation)

- [x] Open the editor file. Locate:
  - Line 258 — the broken read of `self._economy.food_per_pop_per_turn`.
  - The `compute_consumption_preview(pop, allocation, food_per_pop_per_turn) -> float` function (search for the def).
  - The UI row construction code that currently displays a single-resource preview.
  - Any other places that read `self._economy.*` fields.
- [x] Open [game/strategy/engine/organics_consumption_engine.py:75-108](game/strategy/engine/organics_consumption_engine.py#L75-L108) and confirm the formula being previewed: `needed = pop.count * cfg.food_allocation * per_pop_rate` per resource. The preview should reproduce this for every resource in `economy.population_consumption`.
- [x] Document in your task notes: the editor currently displays ONE preview value per slider; the migration will display ONE preview value per (slider × resource) — a cluster.

**Notes:**

### Task 3.2: Write failing tests for the new multi-resource preview [Medium]
**File:** `tests/unit/ui/screens/test_food_allocation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_food_allocation_editor.py -v`

- [x] First, **migrate the 13 broken fixtures** to the new schema. Find every `EconomyConfig(population_food_resource=..., food_per_pop_per_turn=...)` construction and replace with `EconomyConfig(population_consumption={"organics": 0.001, ...})`. The exact resources + rates depend on the test's assertion — most should use `{"organics": 0.001}` to match the prior single-resource behaviour, but some will benefit from a multi-resource setup.
- [x] Add new tests (in a new class `TestMultiResourcePreview` or inline if the existing classes are the right home):
  - Test 1: `test_compute_consumption_preview_returns_per_resource_dict`. Call the new `compute_consumption_preview(pop, allocation, population_consumption)` with `pop.count=1000, allocation=2.0, consumption={"organics": 0.001, "metals": 0.0001}`. Assert the return is `{"organics": 2.0, "metals": 0.2}`.
  - Test 2: `test_zero_allocation_yields_zero_per_resource`. Allocation=0 → all values 0.
  - Test 3: `test_zero_pop_yields_zero_per_resource`. count=0 → all values 0.
  - Test 4: `test_editor_renders_one_preview_label_per_resource`. Construct the editor (bypass-init pattern), render its rows, assert that for a 2-resource economy each row has 2 preview labels visible.
- [x] Run the file. Confirm migrated fixtures pass on the OLD function signature (when called with single-resource), and new tests FAIL (function signature is still old; preview UI is still single-row).

**Notes:** The 13 migrated fixtures might pass before the implementation if they only construct the editor without exercising the slider preview path. That's fine — they should pass post-implementation too.

### Task 3.3: Implement the multi-resource preview function [Medium]
**File:** `game/ui/screens/food_allocation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_food_allocation_editor.py -v`

- [x] Update `compute_consumption_preview` signature:
  ```python
  def compute_consumption_preview(
      pop, allocation: float, population_consumption: Dict[str, float]
  ) -> Dict[str, float]:
      """PROJ-291 C2: per-resource consumption preview for the food allocation
      slider. Mirrors `OrganicsConsumptionEngine._process_colony` exactly:
      needed = pop.count * allocation * per_pop_rate."""
      return {
          resource: pop.count * allocation * rate
          for resource, rate in population_consumption.items()
      }
  ```
- [x] Update line 258 (the broken call site):
  ```python
  consumption = compute_consumption_preview(
      pop, allocation, self._economy.population_consumption
  )
  ```
- [x] Run Task 3.2's tests for the function signature — Tests 1, 2, 3 should pass.

**Notes:**

### Task 3.4: Rewrite the editor row UI for per-resource preview [Complex]
**File:** `game/ui/screens/food_allocation_editor.py`
**Tests:** `pytest tests/unit/ui/screens/test_food_allocation_editor.py -v`

- [x] Update the row UI: each row currently shows one preview label per slider. Update it to show one preview label PER (slider × resource). For a single-resource economy this looks identical to the pre-migration UI. For a multi-resource economy the player sees one preview line per resource consumed.
- [x] Update any title / heading text that referenced "Food" or "Organics" — pull the primary resource name from `economy_config.primary_resource` if a primary-resource label is needed.
- [x] Run Task 3.2's Test 4 — should pass.
- [x] Run the full file — all 13+ tests green.

**Notes:** Be conservative on visual layout — the goal is "no AttributeError + per-resource preview displays". UX polish (column alignment, color coding) is out of scope; PROJ-292 m9 covers UI assembly tests.

### Task 3.5: Retire the `population_food_resource` shim if no callers remain [Simple]
**File:** `game/strategy/config/economy_config.py`
**Tests:** `pytest tests/unit/strategy/config/test_economy_config.py -v`

- [x] Run `grep -rn "population_food_resource" game/ tests/ | grep -v "population_consumption"` to find all remaining consumers.
- [x] If ZERO production callers remain (only test references and the shim itself), delete the shim property from `economy_config.py` AND any test fixtures that were only testing the shim.
- [x] If callers DO remain (e.g. label / title resolution that legitimately wants "the primary resource"), leave the shim in place and update its docstring to note it's the only remaining caller.
- [x] Run the targeted test — green either way.

**Notes:** Auto-fixes prior-audit m4. If you delete the shim, leave the comment explaining why for future audits.

### Task 3.6: Run targeted suite [Simple]
**Tests:** `pytest tests/unit/ui/screens/test_food_allocation_editor.py tests/unit/strategy/config/test_economy_config.py tests/unit/strategy/engine/test_organics_consumption_engine.py -q`

- [x] All three files green.
- [x] Suite-wide regression check: `pytest tests/unit/ui/ tests/unit/strategy/ -q --ignore=tests/unit/quickstart/` — no new failures.

**Notes:** Manual smoke (open the editor on a colonized planet) is in Phase 4 Task 4.4.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
