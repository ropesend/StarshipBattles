# PROJ-410: Build Queue Widget Cache Invalidation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-410` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-410 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Failing regression tests (TDD) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. VirtualTable invalidation surface | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Screen lifecycle resets + selector fix | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Turn-boundary + save/load hooks | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Final verification + doc updates | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-10 08:10
**Active Phase:** Planning complete — awaiting user approval to begin implementation
**Last Action:** Phase B swarm review complete (8 agents). All open questions resolved (turn-boundary mechanism switched to manager polling per swarm consensus). Detailed phase tasks drafted.
**Next Action:** User approval. After "Plan Approved", a separate "Continue Project" session begins Phase 1.
**Blockers:** None.
**Context for Next Agent:** Strict TDD — Phase 1 writes failing tests first; production fixes follow in phases 2–4. Two known discrepancies to verify in Phase 1 by reading source: (1) whether `BuildQueueDragHandler.reset_state()` already clears `selected_design`, (2) the exact facade accessor for active empire (likely `get_active_empire()` or via `get_human_player_ids()`/turn rotation).

## Overview

A Build Queue UI bug emerged when two perf optimizations composed badly: PROJ-373 phase 3 (`aca743a25`) made `VirtualTable._rebuild_row_pool()` early-return when panel geometry is unchanged, and PROJ-376 phase 2 (`a93330bb9`) made `BuildQueueScreen` a reused singleton across yards / panel reopens / player turns. Together they leave row widgets with stale `_last_text` / `_last_img` / `_last_color` and stale button-handler closures bound to the previous yard's data — producing ghost rows below legitimate items, cross-yard contamination, cross-player turn-boundary contamination, and destructive `+/-` clicks that fire on the wrong rows. PROJ-410 builds a targeted invalidation strategy that flushes widget state when the displayed *content* (not just geometry) changes, while preserving the perf wins of PROJ-373 and PROJ-376.

## Goals

- Eliminate the four observed contamination scenarios: ghost rows on second open of same yard; merged display of multiple yards on the same planet; cross-player merged display at turn boundary; destructive `+/-` clicks on ghost rows.
- Preserve PROJ-373 phase 3's row-pool reuse perf win (no widget `.kill()` when geometry unchanged) and PROJ-376 phase 2's screen-instance reuse perf win (`<0.5s` repeat-open).
- Preserve PROJ-382 phase 1's facade-bypass eradication: invalidation hooks must route through `self.facade.handle_command()` and `self.facade.get_registries()`; no direct session bypass.
- Resolve the missing yard-selector on the second player's planet — confirmed by Phase B swarm to be a *separate* container-visibility bug; fold the small fix into PROJ-410 per the user's scope answer.
- Add explicit regression coverage for the five user-approved scenarios plus yard-selector and save/load.

## Scope

**In:**
- `VirtualTable` widget-cache invalidation surface (`game/ui/components/table/virtual_table.py`).
- `BuildQueueRenderer` content-invalidation hook (`game/ui/screens/build_queue_renderer.py`).
- `BuildQueueScreen` lifecycle hooks for yard switch, close/reopen, and player change (`game/ui/screens/build_queue_screen.py`).
- `BuildQueueController` and `BuildQueueDragHandler` state resets (verification + small fixes).
- `BuildQueueSelector` container visibility fix (`game/ui/screens/build_queue_selector.py`).
- Turn-boundary handling via `StrategyBuildQueueManager` polling `facade.get_active_empire()` on each open.
- Save/load hook in `StrategyScreen.session` setter.
- Regression tests under `tests/unit/ui/components/table/`, `tests/unit/ui/screens/`, and `tests/integration/ui/build_queue_screen/`.
- Pattern #11 (Surface Caching) doc extension in `docs/02_PATTERNS.md` describing cross-context invalidation.

**Out:**
- Re-architecting `VirtualTable` or `BuildQueueScreen` beyond what's needed for correct invalidation.
- Adding a new facade event/callback subscription API. Phase B swarm consensus is that polling the existing read accessor is more consistent with what's there. (See Decision 4.)
- Save-file migration. There is none for this UI state.
- Performance work beyond preserving the existing budgets.
- Changes to PROJ-373 phase 3's geometry check semantics.
- A generation counter on `BuildQueueQueueDataSource` (Performance Analyst noted ~1–2 ms redundancy per refresh; below threshold to justify the change in this project).

## Final Design

### Three layered hooks

1. **B-hook (renderer → table)**: `BuildQueueRenderer.refresh_queue_display()` calls `virtual_table.invalidate_widget_caches()` before `update_visible_rows()` whenever it pushes new data via `set_queue()`. Fires on every queue mutation (add/remove/reorder).
2. **C-hook (screen → collaborators)**: `BuildQueueScreen.open_for_yard()` explicitly resets controller queue refs, drag handler `selected_design`, and (transitively, via the renderer) the table caches before `_refresh_queue_display()`. Fires once per yard switch / reopen.
3. **A-hook (manager polling)**: `StrategyBuildQueueManager._open_build_queue()` polls `facade.get_active_empire()` and compares against the last-seen empire id; on change, calls `screen.on_active_player_changed()` before `open_for_yard()`. Save/load is handled separately via `StrategyScreen.session` setter calling the same hook.

### `VirtualTable.invalidate_widget_caches()` semantics

- Nulls `_last_text`, `_last_img`, `_last_color` on every existing pool row.
- Sets a private `_data_identity_dirty: bool = True` flag.
- Does NOT call `.kill()` on any widget — `TestRowPoolReuseGuard` stays green.
- The next `update_visible_rows()` call ignores its `(scroll_pct, row_count)` early-return guard while `_data_identity_dirty` is true, re-renders all visible rows, then clears the flag (**ephemeral** — no per-frame perf hit after the first refresh).

### Button-handler re-binding

When a pool row is mapped to a new data row index inside `update_visible_rows()`, action button handlers bound during `_rebuild_row_pool()` may capture the old `(row_index, data_source)`. The fix is to update the captured row index on each pool row whenever `_data_identity_dirty` was true on entry, before the next click reaches `check_action_button_press()`.

## Key Files

| Component | File Path | Phases |
|-----------|-----------|--------|
| Triage source | `Projects/active_projects/PROJ-410/findings/build_queue_caching_overhaul.md` | (reference) |
| VirtualTable component | `game/ui/components/table/virtual_table.py` | 2 |
| Build queue renderer | `game/ui/screens/build_queue_renderer.py` | 3 |
| Build queue screen | `game/ui/screens/build_queue_screen.py` | 3, 4 |
| Build queue panel factory | `game/ui/screens/build_queue_panel_factory.py` | (reference) |
| Build queue queue data source | `game/ui/screens/build_queue_queue_data_source.py` | (reference) |
| Build queue selector | `game/ui/screens/build_queue_selector.py` | 3 |
| Build queue controller | `game/ui/panels/build_queue_controller.py` | 3 (verify) |
| Build queue drag handler | `game/ui/panels/build_queue_drag_handler.py` | 3 (conditional) |
| Strategy build queue manager | `game/ui/screens/strategy_build_queue_manager.py` | 4 |
| Strategy screen (session setter) | `game/ui/screens/strategy_screen.py` | 4 |
| Strategy facade | `game/strategy/facade/strategy_session_facade.py` | (reference) |
| Pattern doc | `docs/02_PATTERNS.md` | 5 |
| VirtualTable tests | `tests/unit/ui/components/table/test_virtual_table.py` | 1, 2 |
| Build queue lifecycle tests | `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` | 1, 3, 4 |
| Manager reuse tests | `tests/unit/ui/screens/test_strategy_build_queue_manager.py` | 1, 4 |
| Queue selector integration tests | `tests/integration/ui/build_queue_screen/test_queue_selector.py` | 1, 3 |
| Static guard | `tests/static_guards/test_facade_bypass_guard.py` | (verify green at end of every phase) |

## Decisions Log

See [decisions.md](decisions.md) for the full log with rationale.

## Initial Analysis & Swarm Findings

Detailed findings live in `findings/`:
- [build_queue_caching_overhaul.md](findings/build_queue_caching_overhaul.md) — original QA triage with screenshots.
- [swarm_virtualtable_datasource.md](findings/swarm_virtualtable_datasource.md), [swarm_screen_lifecycle.md](findings/swarm_screen_lifecycle.md), [swarm_perf_landings.md](findings/swarm_perf_landings.md) — Phase A deep code review.
- [swarm_b_summary.md](findings/swarm_b_summary.md) — consolidated Phase B (8 agents).
- [swarm_b_api.md](findings/swarm_b_api.md), [swarm_b_dependencies.md](findings/swarm_b_dependencies.md), [swarm_b_performance.md](findings/swarm_b_performance.md), [swarm_b_yard_selector.md](findings/swarm_b_yard_selector.md) — Phase B agent reports written to disk.

Architecture, Pattern, Risk, and Test summaries are consolidated in `swarm_b_summary.md` (the four read-only agents reported in chat only).

## Verification Checklist

### Project Start
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS, 06_UI_STYLE_GUIDE)
- [x] Run full test suite `python Tools/test_sharded/test_sharded.py` — 19828 tests, 19824 passed, 4 skipped, 0 failures (baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` — all affected tests pass
- [ ] `TestRowPoolReuseGuard` still passes (no widget `.kill()` calls added)
- [ ] `tests/static_guards/test_facade_bypass_guard.py` still passes
- [ ] Update `## Current State` and the per-phase status row in Quick Status

### Final Verification
- [ ] All 5 user-approved regression scenarios pass: yard-switch identical-geometry, close+reopen, end-of-turn, ship-yard ↔ planetary-yard, destructive `+/-` click after switch
- [ ] Yard-selector visible on second player's planet
- [ ] Save/load mid-session does not leak previous-session data into the build queue
- [ ] Run full sharded suite `python Tools/test_sharded/test_sharded.py`
- [ ] Smoke timing: repeat-open `<0.5s` at baseline resolution
- [ ] `docs/02_PATTERNS.md` Pattern #11 updated; `Last verified` stamp bumped if changed

---

## Phases

### Phase 1: Failing Regression Tests (TDD) [Medium]
**Objective:** Write or extend tests for every observed bug + new risks before any production code change. Each new test must fail on current `main` and pass after the fix lands.
**Status:** Not Started
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/unit/ui/components/table/test_virtual_table.py tests/integration/ui/build_queue_screen/`

#### Task 1.1: Verify the `selected_design` reset gap [Simple]
**File:** `game/ui/panels/build_queue_drag_handler.py` (read-only) and `tests/unit/ui/panels/test_build_queue_drag_handler.py` (or wherever `reset_state` is tested)
**Tests:** Test addition only; production unchanged.
- [ ] Read `game/ui/panels/build_queue_drag_handler.py:88–101` directly to confirm whether `reset_state()` clears `self.selected_design`. The triage and one Phase B agent disagree.
- [ ] If gap exists: write a failing test asserting `selected_design is None` after `reset_state()`.
- [ ] If already cleared: skip the production fix in Phase 3 Task 3.3 and add a regression test that *locks in* the existing behavior (so future refactors don't regress it).
**Notes:**

#### Task 1.2: Failing test — yard switch with identical geometry [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k yard_switch_invalidates`
- [ ] Add `test_same_context_type_yard_switch_invalidates_cache`. Setup: a planet with two yards; open yard A with N items; switch to yard B with M items where M < N (or items differ). Assert: rows beyond M are hidden; row[0..M-1] cells reflect yard B's data, not yard A's.
- [ ] Use `tests.fixtures.ui_widget_factory.make_ui_widget` / `bypass_init` per Pattern #33.
- [ ] Confirm the test fails on current code (run it once to verify red).
**Notes:**

#### Task 1.3: Failing test — close + reopen on same yard [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k close_and_reopen`
- [ ] Add `test_close_and_reopen_invalidates_cache`. Setup: open yard A; mutate queue; close via `_request_close()`; reopen on same yard. Assert: panels survive (`alive() == True`), row caches refreshed, no ghost rows from prior open.
- [ ] Confirm it fails on current code.
**Notes:**

#### Task 1.4: Failing test — turn boundary → next-player open [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k turn_boundary`
- [ ] Add `test_turn_boundary_invalidates_cross_player_cache`. Setup: empire 1 opens build queue on planet P1; advance turn (or simulate `facade.get_active_empire()` returning empire 2); empire 2 opens build queue on planet P2. Assert: empire 2 sees only P2's queues, no leak from P1's display.
- [ ] Confirm it fails on current code.
**Notes:**

#### Task 1.5: Failing test — ship-yard ↔ planetary-yard on same planet [Medium]
**File:** `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k same_planet_different_yard`
- [ ] Add `test_same_planet_different_yard_type_invalidates`. Setup: planet with both `qs_shipyard` and `qs_planetary_yard`; open shipyard; switch to planetary yard. Assert: planetary-yard view shows only complexes (not the prior shipyard's ships); controller's `active_queue_source` updates.
- [ ] Confirm fails.
**Notes:**

#### Task 1.6: Failing test — destructive `+/-` click after yard switch [Medium]
**File:** `tests/unit/ui/components/table/test_virtual_table.py` (extend) or `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k button_press_after_yard_switch`
- [ ] Add `test_button_press_after_yard_switch_targets_new_row_index`. Setup: open yard A; switch to yard B; simulate `+`-button click on row 0. Assert: handler fires for yard B's row 0 design id, not yard A's.
- [ ] Confirm fails on current code (this is the most critical scenario — the click is destructive).
**Notes:**

#### Task 1.7: Failing test — yard-selector visible on second player's planet [Medium]
**File:** `tests/integration/ui/build_queue_screen/test_queue_selector.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/test_queue_selector.py -k second_player_planet`
- [ ] Add `test_yard_selector_visible_on_second_player_planet`. Setup: two empires, both with planets that have ship-yard *and* planetary-yard; empire 1 opens build queue, closes, advance turn; empire 2 opens build queue. Assert: selector enumerates both yards and renders the buttons visible.
- [ ] Confirm fails.
**Notes:**

#### Task 1.8: Failing test — save/load does not leak prior session [Medium]
**File:** `tests/integration/ui/build_queue_screen/test_basics.py` (extend) or new file
**Tests:** `pytest tests/integration/ui/build_queue_screen/ -k save_load`
- [ ] Add `test_build_queue_screen_after_save_load_reflects_new_session`. Setup: open build queue with empire 1's planet; save game; load a different saved game with a different empire/planet; open build queue. Assert: new session's data, not prior session.
- [ ] Use existing `SaveGameService` test fixtures.
- [ ] Confirm fails.
**Notes:**

#### Phase 1 completion check
- [ ] Run all 7 new tests: each should be red.
- [ ] `TestRowPoolReuseGuard` and `TestSecondClickReuse` still green (no production change yet).
- [ ] `python Projects/scripts/validate_phase.py PROJ-410 1` shows PASSED.

---

### Phase 2: VirtualTable Invalidation Surface [Medium]
**Objective:** Add the targeted invalidation surface inside `VirtualTable` itself. Pure component-layer changes — no facade or screen code touched. After this phase, scenario (a) and (e) tests from Phase 1 *can* pass once the screen-side hook (Phase 3) wires it up.
**Status:** Not Started
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py`

#### Task 2.1: Add `_data_identity_dirty` private flag [Simple]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** New unit test asserting flag default + after-call value.
- [ ] In `__init__` (around the existing `_last_pool_dims` declaration at ~line 103), add `self._data_identity_dirty: bool = True`.
- [ ] Add a unit test in `tests/unit/ui/components/table/test_virtual_table.py` verifying the flag's initial state.
**Notes:**

#### Task 2.2: Add `invalidate_widget_caches()` public method [Medium]
**File:** `game/ui/components/table/virtual_table.py`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k invalidate_widget_caches`
- [ ] Add `def invalidate_widget_caches(self) -> None:` near the other public lifecycle methods.
- [ ] Implementation: iterate `self._row_pool`; for each row, set `row["_last_color"] = None`; for each widget in `row["widgets"]`, set `widget["_last_text"] = None` (label) or `widget["_last_img"] = None` (image). Set `self._data_identity_dirty = True`. Do NOT call `.kill()`. Idempotent.
- [ ] Add unit tests:
  - [ ] After call, every pool widget's `_last_text` / `_last_img` / `_last_color` is None.
  - [ ] After call, `_data_identity_dirty` is True.
  - [ ] No widget `.kill()` calls (use a Mock spy or inspect pygame_gui state).
  - [ ] Idempotent: calling twice yields same observable state.
**Notes:**

#### Task 2.3: Gate `update_visible_rows()` early-return on the dirty flag [Medium]
**File:** `game/ui/components/table/virtual_table.py:309–323`
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k update_visible_rows`
- [ ] Modify the early-return at lines 318–323. New condition:
  ```python
  if (current_pct == self._last_scroll_pct and
      current_count == self._last_row_count and
      not self._data_identity_dirty):
      return
  ```
- [ ] After the per-row update loop completes (around line 423), set `self._data_identity_dirty = False`. **Ephemeral** — flag clears on first re-render.
- [ ] Add unit test: invalidate + same scroll + same count → re-render fires; second call without invalidate → re-render skipped (flag was cleared).
**Notes:**

#### Task 2.4: Re-bind action button row indices on dirty refresh [Complex]
**File:** `game/ui/components/table/virtual_table.py` — inside `update_visible_rows()` per-row mapping (~lines 332–423)
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k button_press` and Phase 1 Task 1.6 test now passes.
- [ ] When `_data_identity_dirty` was True on entry, also update each pool row's `row_index` to the new data row index so `check_action_button_press()` (lines 503–531) dispatches against the correct index.
- [ ] If button handlers bind `row_index` via closure (read source carefully), refactor so handlers read `row.get("row_index")` at click time, not at construction time. This makes pool rows truly index-agnostic and avoids stale closures.
- [ ] Add unit test: invalidate + new data; click `+` button on visible row 0; verify handler observes the new data's row 0 design, not the old.
- [ ] Verify Phase 1 Task 1.6 test now passes.
**Notes:**

#### Task 2.5: Verify perf-lock tests stay green [Simple]
**File:** (no edit) — verification only
**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard -v`
- [ ] All 4–5 `TestRowPoolReuseGuard` tests pass unchanged.
- [ ] `test_force_update_does_not_force_pool_rebuild` still passes — `invalidate_widget_caches()` does not affect `_last_pool_dims`.
**Notes:**

#### Phase 2 completion check
- [ ] All new + existing VirtualTable tests green.
- [ ] `TestRowPoolReuseGuard` green.
- [ ] `python Projects/scripts/validate_phase.py PROJ-410 2` PASSED.

---

### Phase 3: Screen Lifecycle Resets + Selector Fix [Medium]
**Objective:** Wire B-hook (renderer) and C-hook (screen) so yard switch and close+reopen invalidate correctly. Fix `BuildQueueSelector` container visibility regression. After this phase, Phase 1 scenarios (a), (b), (d), (e), and yard-selector should pass.
**Status:** Not Started
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/integration/ui/build_queue_screen/`

#### Task 3.1: B-hook in `BuildQueueRenderer.refresh_queue_display()` [Simple]
**File:** `game/ui/screens/build_queue_renderer.py:140–164`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_renderer.py` (add coverage if not present)
- [ ] Inside `refresh_queue_display()`, after `data_source.set_queue(...)` and before `virtual_table.update_visible_rows()`, call `virtual_table.invalidate_widget_caches()`.
- [ ] Add a unit test (or extend existing) asserting `invalidate_widget_caches` is called exactly once per `refresh_queue_display()`.
**Notes:**

#### Task 3.2: C-hook in `BuildQueueScreen.open_for_yard()` [Medium]
**File:** `game/ui/screens/build_queue_screen.py:264–344`
**Tests:** Phase 1 tests 1.2, 1.4, 1.5 should now pass.
- [ ] Verify `controller.set_active_queue(self.active_queue_source)` and `controller.reset_filters()` (lines 317–324) already cover queue-source reset. If `selected_queue_sources` is not cleared by `set_active_queue`, add explicit reset.
- [ ] Verify `drag_handler.reset_state()` (line 327) clears `selected_design` (depends on Phase 1 Task 1.1 finding). If not, the production fix lands in Task 3.3.
- [ ] Confirm the renderer's B-hook (Task 3.1) fires via `_refresh_queue_display()` (line 342) — no extra screen-level `invalidate_widget_caches()` call needed.
- [ ] Add `# PROJ-410:` comment near the C-hook code with a short rationale and a link to this plan.
**Notes:**

#### Task 3.3: Fix `BuildQueueDragHandler.reset_state()` if Phase 1 confirmed gap [Simple — conditional]
**File:** `game/ui/panels/build_queue_drag_handler.py:88–101`
**Tests:** Phase 1 Task 1.1 test passes after this change.
- [ ] **Conditional**: only if Phase 1 Task 1.1 found `selected_design` is not cleared. Add `self.selected_design = None` to the body of `reset_state()`.
- [ ] If Task 1.1 found it's already cleared (transitively), skip — the regression test from 1.1 locks in the existing behavior.
**Notes:**

#### Task 3.4: Fix `BuildQueueSelector` container visibility [Medium]
**File:** `game/ui/screens/build_queue_selector.py:50–134` and possibly `build_queue_screen.py:369–373`
**Tests:** Phase 1 Task 1.7 test passes.
- [ ] Read `BuildQueueSelector.refresh()` (lines 89–134) and `BuildQueueScreen.show()` (lines 369–373) to confirm the swarm's diagnosis: when the screen was previously hidden, the selector's `UIScrollingContainer` is not re-shown when `refresh()` adds new buttons.
- [ ] Pick the smallest fix:
  - Option 1 (preferred): in `BuildQueueScreen.show()`, after showing the background panel, propagate `show()` to known child containers including the selector container.
  - Option 2: in `BuildQueueSelector.refresh()`, ensure the selector's container is shown before populating buttons.
- [ ] Verify Phase 1 Task 1.7 test passes.
**Notes:**

#### Task 3.5: Run scenarios (a), (b), (d), (e), (yard-selector) and verify pass [Simple]
**File:** (verification only)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/integration/ui/build_queue_screen/test_queue_selector.py -v`
- [ ] All Phase 1 tests except 1.4 (turn boundary) and 1.8 (save/load) pass.
- [ ] `TestRowPoolReuseGuard` still green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` green.
**Notes:**

#### Phase 3 completion check
- [ ] All Phase 1 scenarios except (c) and save/load pass.
- [ ] No new test failures elsewhere (`pytest tests/ --testmon`).
- [ ] `python Projects/scripts/validate_phase.py PROJ-410 3` PASSED.

---

### Phase 4: Turn-Boundary + Save/Load Hooks [Medium]
**Objective:** Wire A-hook (manager polls active empire) and the `StrategyScreen.session` setter hook. After this phase all Phase 1 tests pass.
**Status:** Not Started
**Tests:** `pytest tests/unit/ui/screens/test_strategy_build_queue_manager.py tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/integration/ui/build_queue_screen/`

#### Task 4.1: Add `BuildQueueScreen.on_active_player_changed()` [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Add unit test in `test_build_queue_screen_lifecycle.py`.
- [ ] Add `def on_active_player_changed(self) -> None:` after `_request_close()` (near line 823–838).
- [ ] Body: if `self.is_visible()`, call `self.hide()`. Then if `self.panels` is not None, call `self.panels.virtual_table.invalidate_widget_caches()` and reset cached references (`self.queue_sources = []`, `self.active_queue_source = None`). Idempotent.
- [ ] Add unit test asserting: after call, `is_visible()` is False, table caches are invalidated, references cleared.
- [ ] Naming follows the existing `on_*_changed()` convention in `game/ui/`.
**Notes:**

#### Task 4.2: Manager polling in `_open_build_queue()` [Medium]
**File:** `game/ui/screens/strategy_build_queue_manager.py:89–147`
**Tests:** Phase 1 Task 1.4 test passes.
- [ ] Verify the right facade accessor for "current active empire id". Likely `self.facade.get_active_empire()` or via existing `EventSlice` accessors. Read `game/strategy/facade/strategy_session_facade.py` and slices to confirm.
- [ ] Add `self._last_active_empire_id: int | None = None` to manager `__init__`.
- [ ] In `_open_build_queue()` (around line 89), before reusing the cached `BuildQueueScreen`:
  - [ ] Read current empire id from facade.
  - [ ] If `self._last_active_empire_id is not None` and `current != last`, call `self._screen.build_queue_screen.on_active_player_changed()` before continuing.
  - [ ] Update `self._last_active_empire_id = current`.
- [ ] Add unit test using the existing manager-test fixtures: simulate two opens with different active empires; assert `on_active_player_changed()` is called between them.
**Notes:**

#### Task 4.3: Save/load hook in `StrategyScreen.session` setter [Medium]
**File:** `game/ui/screens/strategy_screen.py:231–248` (session setter)
**Tests:** Phase 1 Task 1.8 test passes.
- [ ] Read the current session setter to confirm the line range and the existing facade-rebind pattern.
- [ ] After the facade rebind (around line 247), if `self.build_queue_screen` is not None, call `self.build_queue_screen.on_active_player_changed()` to flush state. Reset `self._build_queue_manager._last_active_empire_id` so the next open re-detects.
- [ ] Add a `# PROJ-410:` comment explaining why the hook exists.
- [ ] Add unit test asserting the hook fires on session swap.
**Notes:**

#### Task 4.4: Run scenarios (c) and save/load and verify pass [Simple]
**File:** (verification only)
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py -k turn_boundary tests/integration/ui/build_queue_screen/ -k save_load`
- [ ] Phase 1 Tasks 1.4 and 1.8 tests pass.
- [ ] `TestRowPoolReuseGuard`, `TestSecondClickReuse`, lifecycle close+reopen tests still green.
- [ ] `tests/static_guards/test_facade_bypass_guard.py` green.
**Notes:**

#### Phase 4 completion check
- [ ] All 7+ Phase 1 tests pass.
- [ ] `pytest tests/ --testmon` clean.
- [ ] `python Projects/scripts/validate_phase.py PROJ-410 4` PASSED.

---

### Phase 5: Final Verification + Doc Updates [Simple]
**Objective:** Full-suite verification and Pattern #11 doc extension.
**Status:** Not Started
**Tests:** `python Tools/test_sharded/test_sharded.py`

#### Task 5.1: Full sharded test suite [Simple]
**File:** (no edit)
**Tests:** `python Tools/test_sharded/test_sharded.py`
- [ ] All shards pass.
- [ ] Test count ≥ baseline (19828) plus the new tests added in Phase 1 (~7–9 net additions).
**Notes:**

#### Task 5.2: Static guards + perf-lock tests [Simple]
**File:** (no edit)
**Tests:** `pytest tests/static_guards/ tests/unit/ui/components/table/test_virtual_table.py::TestRowPoolReuseGuard tests/unit/ui/screens/test_strategy_build_queue_manager.py tests/unit/ui/screens/test_build_queue_screen_lifecycle.py`
- [ ] All pass.
**Notes:**

#### Task 5.3: Smoke timing — repeat-open `<0.5s` [Simple]
**File:** (no edit) — manual smoke test
**Tests:** Manual.
- [ ] Run the game, open build queue, switch yards 5 times. Confirm wall-clock per-switch is `<0.5s` at baseline resolution. (Profiler optional; the goal is "no obvious regression vs PROJ-376 phase 2 baseline.")
- [ ] If timing regresses, profile the new B-hook overhead per Performance Analyst's notes; consider adding a generation counter on `BuildQueueQueueDataSource` as a follow-up project.
**Notes:**

#### Task 5.4: Update `docs/02_PATTERNS.md` Pattern #11 [Simple]
**File:** `docs/02_PATTERNS.md` Pattern #11 (Surface Caching)
**Tests:** None.
- [ ] Add a short subsection or note: "When a cached widget is reused for *different content* (e.g. yard switch in `BuildQueueScreen`), expose an `invalidate_widget_caches()` method that nulls per-cell caches without `.kill()`-ing pool widgets. Pair with an ephemeral `_data_identity_dirty` flag that is cleared after one re-render."
- [ ] Bump `> **Last verified:**` line below the H1.
- [ ] No new pattern number — extending #11.
**Notes:**

#### Task 5.5: Close-out updates [Simple]
**File:** `Projects/projects_index.md`, `Projects/active_projects/PROJ-410/plan.md` (Current State + Quick Status)
**Tests:** None.
- [ ] Update `Projects/projects_index.md` row for PROJ-410 to "Complete".
- [ ] Update plan.md Quick Status table — all phases "Complete".
- [ ] Update Current State to reflect completion.
- [ ] Add final entries to decisions.md if any decisions were made during implementation that aren't already there.
**Notes:**

#### Phase 5 completion check
- [ ] Full sharded suite green.
- [ ] All static + perf-lock guards green.
- [ ] Repeat-open timing acceptable.
- [ ] Docs updated.
- [ ] `python Projects/scripts/validate_phase.py PROJ-410 5` PASSED.
- [ ] User verification.

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All Phase 5 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Related Documents
- [design.md](design.md) — Architecture analysis and design rationale
- [decisions.md](decisions.md) — Full decisions log
- [manifest.md](manifest.md) — File manifest for parallel execution
- [findings/](findings/) — Phase A and Phase B swarm reports
