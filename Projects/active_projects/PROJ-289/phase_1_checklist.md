# Phase 1: Per-species sub-block in planet info

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-289 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace the single-line per-species display in `format_planet_info` with an indented sub-block showing habitability, happiness, growth rate, food ratio, and food allocation per species.

---

## Tasks

### Task 1.1: Add `format_signed_float` helper + tests [Simple]
**File:** `game/ui/utils/formatters.py`
**Tests:** `pytest tests/unit/ui/utils/test_formatters.py`

- [x] Add `format_signed_float(value: float, decimals: int = 1) -> str` — prefixes `+` for positives, relies on Python's native `-` for negatives.
- [x] Tests: positive, negative, zero, decimal precision, very large / very small values.

**Notes:** Implementation also handles the `-0.0` floating-point sign quirk (renders as `+0.0`) so the downstream "negative = red" colour rule isn't fooled. 8 tests in `TestFormatSignedFloat` cover positive/negative/zero/decimals/large/small/negative-zero.

### Task 1.2: Add `_happiness_category` helper + tests [Simple]
**File:** `game/ui/screens/strategy_detail_fmt.py` (or a utility module if cleaner)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [x] `_happiness_category(happiness: float) -> str` — thresholds 1.5 / 0.5; returns "Content" / "Settled" / "Unhappy".
- [x] Tests: boundary cases (exactly 0.5, 1.5), extreme low (< 0), extreme high (> 3).

**Notes:** Lives in `strategy_detail_fmt.py` (the only consumer right now). 8 tests in `TestHappinessCategory` cover both thresholds inclusively, just-below cases, zero/negative, and the [0, 3] HappinessEngine extreme.

### Task 1.3: Write failing tests for per-species sub-block [Medium]
**File:** `tests/unit/ui/screens/test_strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py::TestPerSpeciesSubBlock`

- [x] Test: `format_planet_info(planet, view=None)` (uncolonized or no view) → legacy single-line rendering preserved.
- [x] Test: `format_planet_info(planet, view=view_with_one_species)` → output contains species name, count, category label; 4 metric rows.
- [x] Test: multi-species view → each species has its own sub-block, ordered per `view.species` tuple.
- [x] Test: growth rate formatted as signed percentage (e.g. "+1.2% / turn", "-0.8% / turn").
- [x] Test: habitability / happiness / food ratio formatted to 2 decimals.
- [x] Test: allocation formatted as "{value}×" (e.g. "1.00×", "2.00×").

**Notes:** Added 9 tests in `TestPerSpeciesSubBlock`: legacy fallback when view=None, single-species sub-block presence, all metric line formats, negative growth with `-`, multi-species rendering count, ordering preservation, and three category-label edge cases (Settled at baseline 0.5, Unhappy at 0.2, Content at 2.0). Helpers `_make_basic_planet`, `_make_species_view`, `_make_view` build the minimal Planet mock + real `SpeciesDemographicView` / `ColonyDemographicView` instances.

### Task 1.4: Implement per-species sub-block in `format_planet_info` [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [x] Update signature: `format_planet_info(planet: IPlanet, view: Optional[ColonyDemographicView] = None) -> str`.
- [x] When `view is None`, keep existing per-species line (backward compat).
- [x] When `view` is provided, replace the per-species loop with a sub-block:
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
- [x] Import `ColonyDemographicView` under TYPE_CHECKING to avoid runtime dep.

**Notes:** Implementation matches the design.md sketch exactly (with `\u00d7` instead of literal `×` to avoid Windows console encoding issues). Branching: when `view is not None` use the new sub-block; otherwise fall through to the existing legacy per-species line. Tightened `_happiness_category` thresholds to inclusive `>=`. 79/79 tests in `tests/unit/ui/screens/test_strategy_detail_fmt.py` pass.

### Task 1.5: Update caller — planet_report_panel.update_planet [Medium]
**File:** `game/ui/panels/planet_report_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_planet_report_panel.py`

- [x] `update_planet(planet, registries=None, view=None)` — accept view kwarg.
- [x] Pass `view` through to `format_planet_info(planet, view=view)`.
- [x] If view is None, current behavior preserved.

**Notes:** Also added `view` kwarg to `PlanetReportPanel.__init__` (the panel is constructed fresh per planet rather than reused via update_planet — `update_planet` is a dormant API never called in production today). Both paths thread `view` into `format_planet_info`. Existing 4 callers (`build_queue_panel_factory`, `planet_list_window`, `planet_selection_window`, `strategy_detail_formatter`) keep working unchanged because the kwarg is optional.

### Task 1.6: Wire facade call from strategy screen [Medium]
**File:** `game/ui/screens/strategy_screen.py` (or wherever the panel is updated)
**Tests:** Manual smoke + existing strategy-screen tests.

- [x] Find where `planet_report_panel.update_planet(planet)` is called.
- [x] Replace with:
  ```python
  view = self.facade.get_colony_demographic_view(planet.id) if planet.owner_id is not None else None
  self.planet_report_panel.update_planet(planet, registries=..., view=view)
  ```
- [x] Confirm no regressions in strategy-screen tests.

**Notes:** The actual planet panel construction lives in `game/ui/screens/strategy_detail_formatter.py::_show_planet_report`, not `strategy_screen.py`. Plumbed the facade call there: `view = facade.get_colony_demographic_view(obj.id)` when `obj.owner_id is not None` and the scene exposes a facade (`getattr(self.scene, "facade", None)`). The defensive `getattr` is there because some test scenes pass a stripped-down `scene` mock without the `facade` property — they just get the legacy rendering, which is correct backward-compat behaviour. Updated 4 PlanetReportPanel call sites all kept working unchanged because the new kwarg is optional. UI test suite green: 2377/2377 (excluding the pre-existing PROJ-286 test debt in `test_food_allocation_editor.py`).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 2: resource grid)
