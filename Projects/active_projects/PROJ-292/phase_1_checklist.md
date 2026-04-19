# Phase 1: H1 — Thread `view` kwarg into PlanetListWindow + BuildQueuePanelFactory

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-292 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Thread the `view: ColonyDemographicView` kwarg into the two PlanetReportPanel callers that currently render colonized planets without the per-species sub-block. Restores PROJ-289's flagship feature in PlanetListWindow + BuildQueuePanelFactory contexts.

---

## Tasks

### Task 1.1: Read the reference wiring [Simple]
**File:** [game/ui/screens/strategy_detail_formatter.py:240-273](game/ui/screens/strategy_detail_formatter.py#L240-L273)
**Tests:** None (read-only)

- [x] Open the file. Locate `_show_planet_report` (around line 240). Note the wiring pattern:
  ```python
  view = None
  if obj.owner_id is not None:
      facade = getattr(self.scene, "facade", None)
      if facade is not None:
          view = facade.get_colony_demographic_view(obj.id)
  self.planet_report_panel = PlanetReportPanel(..., view=view)
  ```
- [x] This is the canonical pattern. Phase 1 backports it to PlanetListWindow + BuildQueuePanelFactory.

**Notes:**

### Task 1.2: Write failing test for PlanetListWindow view threading [Medium]
**File:** `tests/unit/ui/screens/test_planet_list_window.py` (NEW or MODIFY)
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window.py::TestViewThreading -v`

- [x] Add a new test class `TestViewThreading`.
- [x] Test 1: `test_colonized_planet_threads_view_into_panel`. Use the bypass-init pattern. Mock the facade with `get_colony_demographic_view = MagicMock(return_value=stub_view)`. Construct `PlanetListWindow(...)` with the mocked facade in the scene. Trigger `_on_planet_selected(colonized_planet)`. Assert that `PlanetReportPanel` was constructed with `view=stub_view`.
- [x] Test 2: `test_uncolonized_planet_passes_view_none`. Same setup with `planet.owner_id = None`. Assert `view=None` was passed.
- [x] Run the tests. Expect failures (the wiring isn't there yet).

**Notes:**

### Task 1.3: Wire PlanetListWindow [Medium]
**File:** [game/ui/screens/planet_list_window.py:511](game/ui/screens/planet_list_window.py#L511)
**Tests:** `pytest tests/unit/ui/screens/test_planet_list_window.py -v`

- [x] Confirm PlanetListWindow has access to a facade. If it does NOT, but DOES have a `_race_registry` (line 52), find the construction site (likely `strategy_window_manager.py::_open_planet_list_window`) and pass `facade=facade` from the scene.
- [x] At line 511 (the PlanetReportPanel construction), add `view=view` where `view` is resolved as in Task 1.1's pattern.
- [x] Run Task 1.2's tests — both should now pass.
- [x] Run the full file — existing tests still pass.

**Notes:** If you need to extend the constructor to accept `facade`, document the change in decisions.md as a constructor evolution.

### Task 1.4: Write failing test for BuildQueuePanelFactory view threading [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_panel_factory.py` (likely exists; check first)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py::TestViewThreading -v`

- [x] Same pattern as Task 1.2 — bypass-init, mock facade, construct factory, assert `view` threaded through.
- [x] Run the test. Expect failure.

**Notes:**

### Task 1.5: Wire BuildQueuePanelFactory [Medium]
**File:** [game/ui/screens/build_queue_panel_factory.py:181](game/ui/screens/build_queue_panel_factory.py#L181)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_panel_factory.py -v`

- [x] BuildQueuePanelFactory typically has `self.session.facade` access — confirm via the scene context.
- [x] At line 181 (the PlanetReportPanel construction), add `view=view` where `view = self.session.facade.get_colony_demographic_view(self.build_context.id) if self.build_context.owner_id is not None else None`.
- [x] Run Task 1.4's tests — green.
- [x] Run the full file — existing tests still pass.

**Notes:** BuildQueuePanel ONLY shows colonized planets (build queues only exist on owned planets), so this fix is high-value: it goes from 0% PROJ-289 coverage in this context to 100%.

### Task 1.6: Targeted regression suite [Simple]
**Tests:** `pytest tests/unit/ui/screens/ tests/unit/ui/panels/ -q`

- [x] Full UI screens + panels suite green.
- [x] No regressions introduced.

**Notes:** Manual smoke (open a colonized planet from PlanetListWindow + verify per-species sub-block visible) is in Phase 6 Task 6.4.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
