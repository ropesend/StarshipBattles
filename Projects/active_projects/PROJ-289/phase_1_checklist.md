# Phase 1: Per-species sub-block in planet info

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-289 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace the single-line per-species display in `format_planet_info` with an indented sub-block showing habitability, happiness, growth rate, food ratio, and food allocation per species.

---

## Tasks

### Task 1.1: Add `format_signed_float` helper + tests [Simple]
**File:** `game/ui/utils/formatters.py`
**Tests:** `pytest tests/unit/ui/utils/test_formatters.py`

- [ ] Add `format_signed_float(value: float, decimals: int = 1) -> str` — prefixes `+` for positives, relies on Python's native `-` for negatives.
- [ ] Tests: positive, negative, zero, decimal precision, very large / very small values.

**Notes:**

### Task 1.2: Add `_happiness_category` helper + tests [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py` (or a utility module if cleaner)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [ ] `_happiness_category(happiness: float) -> str` — thresholds 1.5 / 0.5; returns "Content" / "Settled" / "Unhappy".
- [ ] Tests: boundary cases (exactly 0.5, 1.5), extreme low (< 0), extreme high (> 3).

**Notes:**

### Task 1.3: Write failing tests for per-species sub-block [Medium]
**File:** `tests/unit/ui/screens/test_strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py::TestPerSpeciesSubBlock`

- [ ] Test: `format_planet_info(planet, view=None)` (uncolonized or no view) → legacy single-line rendering preserved.
- [ ] Test: `format_planet_info(planet, view=view_with_one_species)` → output contains species name, count, category label; 4 metric rows.
- [ ] Test: multi-species view → each species has its own sub-block, ordered per `view.species` tuple.
- [ ] Test: growth rate formatted as signed percentage (e.g. "+1.2% / turn", "-0.8% / turn").
- [ ] Test: habitability / happiness / food ratio formatted to 2 decimals.
- [ ] Test: allocation formatted as "{value}×" (e.g. "1.00×", "2.00×").

**Notes:**

### Task 1.4: Implement per-species sub-block in `format_planet_info` [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [ ] Update signature: `format_planet_info(planet: IPlanet, view: Optional[ColonyDemographicView] = None) -> str`.
- [ ] When `view is None`, keep existing per-species line (backward compat).
- [ ] When `view` is provided, replace the per-species loop with a sub-block:
  ```
  for species in view.species:
      text += f"<br><b>{species.race_name}</b>: {format_compact_number(species.count)} "
      text += f"[{_happiness_category(species.happiness)}]<br>"
      text += f"   Habitability: {species.habitability:.2f}&nbsp;&nbsp;"
      text += f"Happiness: {species.happiness:.2f}<br>"
      text += f"   Growth: {format_signed_float(species.growth_rate*100, 1)}% / turn&nbsp;&nbsp;"
      text += f"Food ratio: {species.food_ratio:.2f}<br>"
      text += f"   Allocation: {species.food_allocation:.2f}×<br>"
  ```
- [ ] Import `ColonyDemographicView` under TYPE_CHECKING to avoid runtime dep.

**Notes:**

### Task 1.5: Update caller — planet_report_panel.update_planet [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [ ] `update_planet(planet, registries=None, view=None)` — accept view kwarg.
- [ ] Pass `view` through to `format_planet_info(planet, view=view)`.
- [ ] If view is None, current behavior preserved.

**Notes:**

### Task 1.6: Wire facade call from strategy screen [Medium]
**File:** `game/ui/screens/strategy_screen.py` (or wherever the panel is updated)
**Tests:** Manual smoke + existing strategy-screen tests.

- [ ] Find where `planet_report_panel.update_planet(planet)` is called.
- [ ] Replace with:
  ```python
  view = self.facade.get_colony_demographic_view(planet.id) if planet.owner_id is not None else None
  self.planet_report_panel.update_planet(planet, registries=..., view=view)
  ```
- [ ] Confirm no regressions in strategy-screen tests.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2: resource grid)
