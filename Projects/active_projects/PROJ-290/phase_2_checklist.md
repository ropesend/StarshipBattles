# Phase 2: Uncolonized-planet per-species habitability list (0-100)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-290 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add an "uncolonized habitability for your species" section to `format_planet_info` when `planet.owner_id is None`. List every `empire.resident_species()` entry with a 0-100 integer score, sorted best-fit first.

---

## Tasks

### Task 2.1: Write failing tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py::TestUncolonizedHabitabilityForEmpire`

- [ ] Test: uncolonized planet + empire with 0 resident species → section omitted from output.
- [ ] Test: uncolonized planet + empire with 1 resident species → section rendered with one line: `"{race_name}: {score}/100"`.
- [ ] Test: uncolonized planet + 3 resident species → 3 lines, sorted by score DESCENDING.
- [ ] Test: colonized planet (owner_id is not None) + empire + registry → section NOT rendered (goes through the colonized branch instead).
- [ ] Test: race_id in `resident_species()` but registry returns None → that species is silently skipped.
- [ ] Test: score rendering — ideal planet for Earth-prefs race produces ~94/100; magma planet produces <5/100.

**Notes:**

### Task 2.2: Implement `format_uncolonized_habitability_for_empire` helper [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [ ] Add helper function as sketched in design.md § Section 4:
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
- [ ] Place the helper at module level so tests can call it directly without constructing a full panel.

**Notes:**

### Task 2.3: Extend `format_planet_info` signature + wire the helper [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py`

- [ ] Update signature: `format_planet_info(planet, view=None, empire=None, race_registry=None)`.
- [ ] When `planet.owner_id is None` AND `empire is not None` AND `race_registry is not None`, append `format_uncolonized_habitability_for_empire(planet, empire, race_registry)` to the text.
- [ ] Preserves backward compat when the new kwargs are omitted.

**Notes:**

### Task 2.4: Thread new kwargs through `PlanetReportPanel` + caller [Medium]
**File:** `game/ui/panels/planet_report_panel.py` + `game/ui/screens/strategy_screen.py`
**Tests:** Existing panel + screen tests; update as needed.

- [ ] `PlanetReportPanel.update_planet(planet, registries=None, view=None, empire=None, race_registry=None)` — accept and forward.
- [ ] Strategy screen caller: pass `empire = scene.current_empire` and `race_registry = facade.get_race_registry()`.
- [ ] Coordinate with PROJ-289: BOTH projects add kwargs to the same methods. Confirm their signatures stack rather than conflict.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3: docs + cleanup)
