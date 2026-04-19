# Phase 2: Uncolonized-planet per-species habitability list (0-100)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-290 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add an "uncolonized habitability for your species" section to `format_planet_info` when `planet.owner_id is None`. List every `empire.resident_species()` entry with a 0-100 integer score, sorted best-fit first.

---

## Tasks

### Task 2.1: Write failing tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py::TestUncolonizedHabitabilityForEmpire`

- [x] Test: uncolonized planet + empire with 0 resident species → section omitted from output.
- [x] Test: uncolonized planet + empire with 1 resident species → section rendered with one line: `"{race_name}: {score}/100"`.
- [x] Test: uncolonized planet + 3 resident species → 3 lines, sorted by score DESCENDING.
- [x] Test: colonized planet (owner_id is not None) + empire + registry → section NOT rendered (goes through the colonized branch instead).
- [x] Test: race_id in `resident_species()` but registry returns None → that species is silently skipped.
- [x] Test: score rendering — ideal planet for Earth-prefs race produces ~94/100; magma planet produces <5/100.

**Notes:** Patched `score_planet_for_race` in tests to control scores without requiring real RaceConfig + real Planet setup (decouples from PROJ-283 formula internals). Two test classes added: `TestUncolonizedHabitabilityForEmpire` (helper) + `TestFormatPlanetInfoUncolonizedHabitabilitySection` (integration). 10 tests green.

### Task 2.2: Implement `format_uncolonized_habitability_for_empire` helper [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [x] Add helper function as sketched in design.md § Section 4:
  ```python
  def format_uncolonized_habitability_for_empire(planet, empire, race_registry) -> str:
      species_ids = sorted(empire.resident_species())
      scored = []
      for race_id in species_ids:
          race = race_registry.get_race(race_id)
          if race is None:
              continue
          score = int(round(score_planet_for_race(planet, race) * 100))
          display_name = (
              getattr(race, "race_name", None)
              or getattr(race, "name", None)
              or race_id
          )
          scored.append((score, display_name))
      if not scored:
          return ""
      scored.sort(reverse=True)
      lines = "<br>".join(f" - {name}: {score}/100" for score, name in scored)
      return f"<br><b>Habitability for your species:</b><br>{lines}<br>"
  ```
- [x] Place the helper at module level so tests can call it directly without constructing a full panel.

**Notes:** Sort key uses `lambda entry: entry[0]` (score only, reverse=True) so ties keep alphabetical order from the initial `sorted(species_ids)` pre-sort (Python's sort is stable). Implementation lives in [game/ui/screens/strategy_detail_fmt.py](game/ui/screens/strategy_detail_fmt.py).

### Task 2.3: Extend `format_planet_info` signature + wire the helper [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [x] Update signature: `format_planet_info(planet, view=None, empire=None, race_registry=None)`.
- [x] When `planet.owner_id is None` AND `empire is not None` AND `race_registry is not None`, append `format_uncolonized_habitability_for_empire(planet, empire, race_registry)` to the text.
- [x] Preserves backward compat when the new kwargs are omitted.

**Notes:** PROJ-290 added only the `empire` + `race_registry` kwargs (keyword-only via `*,` separator). `view=None` is PROJ-289's kwarg — it will stack independently when that agent adds it, no conflict. Section emits only when all three conditions hold: unowned planet + empire + race_registry. Partial deps (empire present but registry None) cleanly skip — also covered by test `test_uncolonized_with_empire_but_no_registry_skips_section`.

### Task 2.4: Thread new kwargs through `PlanetReportPanel` + caller [Medium]
**File:** `game/ui/panels/planet_report_panel.py` + `game/ui/screens/strategy_screen.py`
**Tests:** Existing panel + screen tests; update as needed.

- [x] `PlanetReportPanel.update_planet(planet, registries=None, view=None, empire=None, race_registry=None)` — accept and forward.
- [x] Strategy screen caller: pass `empire = scene.current_empire` and `race_registry = facade.get_race_registry()`.
- [x] Coordinate with PROJ-289: BOTH projects add kwargs to the same methods. Confirm their signatures stack rather than conflict.

**Notes:**
- `PlanetReportPanel.__init__` + `update_planet` accept `empire` + `race_registry`; stored on the instance so `update_planet` can default to construction-time values when called without fresh deps.
- Wired through the Planet List path: [strategy_window_manager.py](game/ui/screens/strategy_window_manager.py) (where `_open_planet_list_window` now pulls `facade.get_race_registry()`) → [planet_list_window.py:43](game/ui/screens/planet_list_window.py#L43) (new `race_registry=None` kwarg) → [planet_report_panel.py](game/ui/panels/planet_report_panel.py) (existing `empire` + `race_registry` kwargs).
- Other construction sites (`planet_selection_window.py`, `build_queue_panel_factory.py`) NOT wired — they default to None → section auto-hides. Not in scope for PROJ-290: those contexts are for colonize/build-queue workflows, not planet-browsing. Can be enabled later by threading the same pair.
- **PROJ-289 coordination:** PROJ-290 added only `empire` + `race_registry` (keyword-only). `view=None` (PROJ-289's kwarg) will stack cleanly. No signature conflict as long as PROJ-289 also uses keyword-only arguments via `*,` separator.
- No regressions in `tests/unit/ui/panels/` + `tests/unit/ui/screens/` (2358 pass; 13 unrelated pre-existing failures are the PROJ-289-pending food_allocation_editor cases from the PROJ-286 handoff).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3: docs + cleanup)
