# Phase 1: Lifecycle seam — split `BuildQueueScreen.__init__` into shell + `open_for_yard()`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-376 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** (none — first phase)
**Review Mode:** standard
**Files (planned):**
- `game/ui/screens/build_queue_screen.py`
- `game/ui/panels/build_queue_drag_handler.py`
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (new)
**Objective:** Split `BuildQueueScreen.__init__` into "construct UI shell" (always runs) + "populate yard-specific state" (`open_for_yard(yard, *, hex_coord, portrait_surface)`). Add `hide()`, `show()`, `is_visible()`, private `_rebuild_panels(context_type)`. Add `BuildQueueDragHandler.reset_state()` clearing 5 fields. **Manager-side construction sites are unchanged** — every click still constructs a fresh screen. Behavior parity with today is the acceptance criterion.

---

## Pre-flight (TDD baseline)

- [ ] Read `Projects/active_projects/PROJ-376/plan.md`, `design.md`, `decisions.md`, `findings/initial_review.md`.
- [ ] Read `game/ui/screens/build_queue_screen.py` end-to-end (~660 LOC).
- [ ] Read `game/ui/panels/build_queue_drag_handler.py` lines 32-90 (init + drag-state block).
- [ ] Read `game/ui/screens/build_queue_panel_factory.py:206-241` (planet vs fleet panel dispatch).
- [ ] Run `pytest tests/unit/ui/screens/ tests/integration/ui/build_queue_screen/ tests/unit/ui/panels/ -q` — capture baseline pass count + any pre-existing failures.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline.

---

## Tasks

### Task 1.1: Define lifecycle test surface (TDD-first) [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -v`

Write these tests first; confirm they fail on current code; implementation lands in 1.2-1.5.

- [ ] Use the existing `tests/integration/ui/build_queue_screen/conftest.py` patterns (`MockGalaxy`, `MockSession`, `Empire`, `HexCoord`, `Planet`) for fixture parity.
- [ ] `test_init_with_no_yard_constructs_ui_shell_only` — call `BuildQueueScreen(manager, build_context=None, session, on_close, ..., hex_coord=None, galaxy, empire)` (or new `initial_yard=None` kwarg per Task 1.2 signature). Assert: `panels` is constructed, `controller` is constructed, `drag_handler` is constructed, `build_context is None`, `hex_coord is None`, `queue_sources == []`, `active_queue_source is None`, `selected_queue_indices == set()`.
- [ ] `test_open_for_yard_populates_state_for_planet` — construct shell-only, call `open_for_yard(planet, hex_coord=hex_coord, portrait_surface=None)`. Assert: `build_context is planet`, `hex_coord is hex_coord`, `queue_sources == collect_build_queues_at_hex(...)` result, `active_queue_source is queue_sources[0]`, `selected_queue_indices == {0}`, `selected_queue_index is None`, `planet_selection_window is None`, `controller.build_context is planet`, `controller.hex_coord is hex_coord`, `controller.active_queue_source is active_queue_source`, `controller.selected_category == "complex"`, `controller.selected_role == "Any"`.
- [ ] `test_open_for_yard_initial_yard_kwarg_matches_post_open_state` — call `BuildQueueScreen(..., initial_yard=planet, hex_coord=hex_coord)` (eager) and `BuildQueueScreen(..., initial_yard=None) → open_for_yard(planet, hex_coord=hex_coord)` (lazy). Assert all 12 yard-specific attributes match between the two screens. (Behavior-parity guarantee.)
- [ ] `test_open_for_yard_planet_to_fleet_rebuilds_panels` — open with planet (verify `panels.context_report` is `PlanetReportPanel`), then call `open_for_yard(fleet)`. Assert: a fresh `panels` object exists; old `panels.background` was killed (track via spy or `.alive`); new `panels.context_report` is the fleet info panel (not `PlanetReportPanel`).
- [ ] `test_open_for_yard_planet_to_planet_does_not_rebuild_panels` — open with planet A, then `open_for_yard(planet_b)` (same context type). Assert: `panels` is the SAME object (`id(panels)` unchanged); `panels.background.alive` still True; queue_selector reflects new `queue_sources`.
- [ ] `test_drag_handler_reset_state_clears_all_5_fields` — set `drag_handler.dragged_item = {...}`, `.drag_preview = surface`, `.drag_start_pos = (10, 10)`, `._pending_queue_index = 3`, `.selected_design = "ship_001"`. Call `reset_state()`. Assert all 5 are None.
- [ ] `test_hide_makes_panels_invisible_but_alive` — open screen, call `hide()`. Assert: `panels.background.alive` is True; `panels.background.visible` is False (or whatever pygame_gui's visibility predicate is).
- [ ] `test_show_after_hide_makes_panels_visible` — `hide()` then `show()`. Assert: `panels.background.visible` is True.
- [ ] `test_is_visible_reflects_panel_visibility` — covers the four states: shell-only (`is_visible()` False — no panels constructed for visibility check OR False because background is hidden by default? — define explicitly per Task 1.4), opened, hidden, shown.
- [ ] `test_hide_kills_planet_selection_window_if_open` — open screen, set `screen.planet_selection_window = MagicMock(spec=PlanetSelectionWindow)`, call `hide()`. Assert: `mock.kill.called`; `screen.planet_selection_window is None`.
- [ ] **Verify:** Run; **all tests fail** on current code (no `open_for_yard`, no `reset_state`, no `hide`/`show`/`is_visible`).

**Notes:**

### Task 1.2: Update `BuildQueueScreen.__init__` signature [Medium]
**File:** `game/ui/screens/build_queue_screen.py:48`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -v`

- [ ] Extend `__init__` signature: add keyword-only `initial_yard: Union[Planet, Fleet, BuildContext, None] = None`. Keep existing `build_context` parameter for back-compat — when `initial_yard is None` and `build_context is not None`, treat `build_context` as the initial yard (legacy callers).
- [ ] Refactor `__init__` body into three sequential blocks; preserve line ordering as much as possible:
  - **Shell block** (always runs):
    - DI / shell assignments (lines 70-89 minus the yard-specific `build_context`, `hex_coord`, `selected_queue_index` defaults).
    - Screen geometry (lines 105-107).
    - **Defer panel construction** until we know the yard context type. If `initial_yard is not None` (or legacy `build_context is not None`), pass that in; otherwise construct panels with `build_context=None` and `queue_sources=[]` and rely on `_rebuild_panels` later.
    - Construct `BuildQueuePanelFactory` ONLY if we have a yard. If shell-only, set `self.panels = None`, `self.renderer = None`, `self.controller = None`, `self.drag_handler = None`. (Decision: defer all panel-dependent collaborator construction to `_rebuild_panels`/`open_for_yard`.)
  - **Yard population block** (only if `initial_yard is not None`):
    - Call `self.open_for_yard(initial_yard, hex_coord=hex_coord, portrait_surface=portrait_surface)`.
- [ ] Update `_validate_params` (lines 168-196) — relax to allow `build_context is None` AND `hex_coord is None` when `initial_yard is None`. Keep stronger validation for the non-None case.
- [ ] **Verify:** `test_init_with_no_yard_constructs_ui_shell_only` passes; `test_open_for_yard_initial_yard_kwarg_matches_post_open_state` passes for the eager-init branch.

**Notes:** Be careful with the `manager.get_root_container().get_container().get_size()` call (line 105) — it must run regardless of yard, because screen dimensions are stable across yards. The `BuildQueuePortraitLoader` (line 88) takes `design_library` and `session` — both available without a yard, so it's part of the shell.

### Task 1.3: Implement `open_for_yard(yard, *, hex_coord, portrait_surface=None)` [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Task 1.1 tests

- [ ] Add public method on `BuildQueueScreen`:
  ```python
  def open_for_yard(
      self,
      yard,  # Planet | Fleet | BuildContext
      *,
      hex_coord: 'HexCoord',
      portrait_surface: Optional[pygame.Surface] = None,
  ) -> None:
  ```
- [ ] Method body (per design.md Today's vs. target pipeline):
  1. Detect context-type change: `prev_type = self.build_context.context_type if self.build_context else None`. `new_type = yard.context_type`.
  2. If `self.panels is None` (shell-only) OR `prev_type is not None and prev_type != new_type`: call `self._rebuild_panels(yard, hex_coord, portrait_surface)` (Task 1.4). Else continue with existing panels.
  3. Set `self.build_context = yard`, `self.hex_coord = hex_coord`, `self.portrait_surface = portrait_surface or self.portrait_surface`.
  4. `self.queue_sources = collect_build_queues_at_hex(hex_coord, self.galaxy, self.empire, registries=self.session.registries)`.
  5. `self.active_queue_source = self.queue_sources[0] if self.queue_sources else None`.
  6. `self.selected_queue_indices = {0} if self.queue_sources else set()`.
  7. `self.selected_queue_index = None`.
  8. `self.planet_selection_window = None`.
  9. Update controller: `self.controller.build_context = yard`, `self.controller.hex_coord = hex_coord`, `self.controller.galaxy = self.galaxy`, `self.controller.empire = self.empire`.
  10. `if self.active_queue_source is not None: self.controller.set_active_queue(self.active_queue_source)`.
  11. `self.controller.reset_filters()`. (PROJ-373 Phase 1 method becomes live here.)
  12. `self.drag_handler.reset_state()` (added in Task 1.6).
  13. `self.drag_handler.design_library = self.design_library` (the design library can change between Planet vs Fleet calls per `strategy_build_queue_manager.py:90` and `:207` — both create fresh `DesignLibrary(savegame_path, empire_id)`; today this isn't an issue because the screen is reconstructed; in our world, we must rebind. For Phase 1, since the manager hasn't changed, rebinding is a no-op but the structural correctness is preserved.)
  14. Refresh queue selector to reflect new sources. Inspect `BuildQueueSelector` for an existing public method (`refresh()` or similar). If absent, mutate `self._queue_selector.queue_sources = self.queue_sources` and call its existing rebuild path. **Investigate during implementation; record the chosen approach in the Notes block below.**
  15. `self._refresh_items_list()`.
  16. `self._refresh_queue_display()` (resyncs FEAT-17 pause label via `renderer.refresh_pause_button` at line 387).
  17. `self.show()` (Task 1.4).
- [ ] **Verify:** `test_open_for_yard_populates_state_for_planet`, `test_open_for_yard_planet_to_planet_does_not_rebuild_panels` pass.

**Notes:** Step 14 (queue-selector refresh) is the open question. Read `game/ui/screens/build_queue_selector.py` start to finish to choose the approach. If `BuildQueueSelector.refresh()` already exists and accepts no args, it likely reads `self.queue_sources` — direct attribute mutation + `refresh()` is fine. If it takes args, use the public API.

### Task 1.4: Implement `hide()`, `show()`, `is_visible()`, `_rebuild_panels()` [Medium]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Task 1.1 tests

- [ ] `hide()`:
  ```python
  def hide(self) -> None:
      """Hide the build-queue overlay without destroying widgets.

      PROJ-376: replaces destroy-then-reconstruct close path. Kills the
      transient PlanetSelectionWindow if open (matching today's _close()).
      Panels remain alive.
      """
      if self.planet_selection_window is not None:
          self.planet_selection_window.kill()
          self.planet_selection_window = None
      if self.panels is not None:
          self.panels.background.set_visible(False)
          # Provisional: mirror today's _close() flush. See decisions.md.
          self.manager.update(0)
  ```
- [ ] `show()`:
  ```python
  def show(self) -> None:
      if self.panels is not None:
          self.panels.background.set_visible(True)
          self.manager.update(0)
  ```
- [ ] `is_visible()`:
  ```python
  def is_visible(self) -> bool:
      return self.panels is not None and bool(self.panels.background.visible)
  ```
  (Verify pygame_gui's `UIPanel.visible` is a public boolean attribute; if it's `_visible` or via a getter, adapt.)
- [ ] `_rebuild_panels(yard, hex_coord, portrait_surface)`:
  ```python
  def _rebuild_panels(self, yard, hex_coord, portrait_surface) -> None:
      """Tear down and rebuild the panel tree for a context-type transition.

      Called from open_for_yard when build_context.context_type changes
      (planet ↔ fleet). The collaborators (renderer, controller, drag_handler)
      hold references INTO panels, so we must reconstruct them too.
      """
      if self.panels is not None:
          self.panels.background.kill()
          self.manager.update(0)
      # Re-run the factory + collaborators block from __init__ with the new yard.
      factory = BuildQueuePanelFactory(
          manager=self.manager,
          build_context=yard,
          session=self.session,
          queue_sources=collect_build_queues_at_hex(hex_coord, self.galaxy, self.empire, registries=self.session.registries),
          portrait_loader=self.portrait_loader,
          on_queue_selection_changed=self._on_queue_selection_changed,
          portrait_surface=portrait_surface,
          facade=self.facade,
      )
      self.panels = factory.create_all_panels(format_empire_resources)
      self._queue_selector = self.panels.queue_selector
      self.renderer = BuildQueueRenderer(
          manager=self.manager,
          panels=self.panels,
          portrait_loader=self.portrait_loader,
      )
      self.controller = BuildQueueController(
          build_context=yard,
          design_library=self.design_library,
          design_loader=self.design_loader,
          design_report=self.panels.design_report,
          on_queue_changed=self._refresh_queue_display,
          hex_coord=hex_coord,
          galaxy=self.galaxy,
          empire=self.empire,
          on_planet_selection_needed=self._prompt_target_planet,
          add_to_queue_callback=self._dispatch_add_to_queue_command,
          registries=getattr(self.session, 'registries', None),
      )
      self.drag_handler = BuildQueueDragHandler(
          portrait_loader=self.portrait_loader,
          design_library=self.design_library,
          on_add_to_queue=self.controller.add_to_queue,
          on_refresh_queue=self._refresh_queue_display,
          on_refresh_design_report=self.controller.refresh_design_report,
          on_remove_from_queue=self._dispatch_remove_from_queue_command,
      )
      self._apply_tooltips()
  ```
- [ ] **Verify:** `test_hide_*`, `test_show_after_hide`, `test_is_visible_*`, `test_open_for_yard_planet_to_fleet_rebuilds_panels`, `test_hide_kills_planet_selection_window_if_open` pass.

**Notes:** This task duplicates ~30 lines of factory/collaborator wiring from `__init__`. Acceptable: the alternative is extracting both into a private `_construct_collaborators(yard, hex_coord, portrait_surface)` and calling it from both sites. **Decision (in implementation):** if the duplication is identical, extract it. If it diverges (e.g., __init__ has shell-side state to set), keep them separate to maintain the 500 LOC ceiling on `build_queue_screen.py` (currently 658 LOC; needs care).

### Task 1.5: Add `BuildQueueDragHandler.reset_state()` [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py:73-81`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py::test_drag_handler_reset_state_clears_all_5_fields -v`

- [ ] Add public method:
  ```python
  def reset_state(self) -> None:
      """Clear all transient drag/selection state.

      PROJ-376: called from BuildQueueScreen.open_for_yard when the
      screen is reused across yard switches. Clears the 5 fields
      established at __init__ lines 73-81.
      """
      self.dragged_item = None
      self.drag_preview = None
      self.drag_start_pos = None
      self._pending_queue_index = None
      self.selected_design = None
  ```
- [ ] **Verify:** `test_drag_handler_reset_state_clears_all_5_fields` passes; existing `tests/integration/ui/build_queue_screen/test_drag_handler_multi_queue.py` still passes.

**Notes:**

### Task 1.6: Visibility-gate `handle_event` (defensive) [Simple]
**File:** `game/ui/screens/build_queue_screen.py:397`
**Tests:** Existing tests in `tests/integration/ui/build_queue_screen/`

- [ ] At the top of `handle_event`, add early-return:
  ```python
  def handle_event(self, event: pygame.event.Event) -> None:
      if not self.is_visible():
          return
      ... existing body ...
  ```
- [ ] **Verify:** existing event-handling tests still pass; the defensive gate doesn't break the construct-and-immediately-handle flow because Phase 1 manager-side behavior calls `open_for_yard` which calls `show()` before any event arrives.

**Notes:** Phase 1 manager doesn't change yet, so the construct path goes `__init__(initial_yard=planet)` → `open_for_yard(planet)` → `show()` BEFORE the manager returns and events start flowing. Confirm by reading the legacy `_validate_params` flow.

### Task 1.7: Sharded suite + commit [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Pass count = baseline + ~10 new tests (Task 1.1).
- [ ] `git status --short` confirms only Phase 1 files dirty (`build_queue_screen.py`, `build_queue_drag_handler.py`, new test file).
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-376 phase_1 --repo .worktrees/phases/PROJ-376/phase_1`. (Per 03c protocol — handles validation, regression, commit, project-branch merge, cumulative review dispatch.)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `BuildQueueScreen.__init__` accepts `initial_yard=None` and runs in shell-only mode
- [ ] `BuildQueueScreen.open_for_yard(yard, *, hex_coord, portrait_surface=None)` exists and reproduces today's post-init state
- [ ] `BuildQueueScreen.hide()`, `.show()`, `.is_visible()`, `._rebuild_panels()` exist
- [ ] `BuildQueueDragHandler.reset_state()` exists and clears all 5 fields
- [ ] `handle_event` is visibility-gated
- [ ] **Manager unchanged** — every click still constructs a fresh screen (verify by `git diff` showing zero changes to `strategy_build_queue_manager.py`)
- [ ] Sharded suite green
- [ ] Update status at top of this file to `Complete (Committed)` then `Complete (Verified)` after review
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
