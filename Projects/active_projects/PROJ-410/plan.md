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
**Last Updated:** 2026-05-10 22:25
**Active Phase:** Planning complete — Codex review (arc01-002) folded in; awaiting user approval to begin implementation
**Last Action:** Codex review surfaced 4 material issues + 5 Q&A corrections; all accepted with file:line evidence verified. Plan + decisions + design + manifest + 4 phase checklists revised. Discussion plan revision artifact at `AgentCoordination/Scratchpad/Discussion/20260510T215920Z_proj-410-plan-review/plans/proj410_revisions_r001.md`.
**Next Action:** User approval. After "Plan Approved", a separate "Continue Project" session begins Phase 1.
**Blockers:** None.
**Context for Next Agent:** Strict TDD — Phase 1 writes failing tests first; production fixes follow in phases 2–4. Codex review resolved both prior open questions: (1) `BuildQueueDragHandler.reset_state()` DOES clear `selected_design` (Phase 1 Task 1.1 is now a lock test); (2) active-empire accessor is `self._screen.current_empire.id` (`strategy_screen.py:192`), not a new facade method. Critical addition: A-hook must rebind cached screen domain context (`facade`/`galaxy`/`empire`) before every `open_for_yard()`, not just invalidate caches.

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
- **Cached `BuildQueueScreen` domain context rebind on player change** (`facade`/`galaxy`/`empire`), executed in `StrategyBuildQueueManager._open_build_queue()`. Without this, the cached screen still queries as the previous empire after `on_active_player_changed()`.
- `BuildQueueController` zero-source reset (new Task 3.6) and verification of existing reset paths.
- `BuildQueueSelector` container visibility fix — possibly redundant after the empire rebind; gated on whether Phase 1 Task 1.7 still fails after Phase 4 lands.
- Turn-boundary handling via `StrategyBuildQueueManager` polling `self._screen.current_empire.id` (existing `StrategyScreen` property at `strategy_screen.py:192`) on each open.
- Production save/load coverage: assert `ScreenRouter._on_load_game()` produces a fresh `StrategyScreen` with `build_queue_screen is None` (Phase 1 Task 1.8).
- Regression tests under `tests/unit/ui/components/table/`, `tests/unit/ui/screens/`, `tests/unit/ui/panels/`, `tests/unit/test_screen_router.py`, and `tests/integration/ui/build_queue_screen/`.
- Pattern #11 (Surface Caching) doc extension in `docs/02_PATTERNS.md` describing cross-context invalidation.

**Out:**
- Re-architecting `VirtualTable` or `BuildQueueScreen` beyond what's needed for correct invalidation.
- Adding a new facade event/callback subscription API. Phase B swarm consensus + Codex review is that polling `self._screen.current_empire.id` (existing property) is more consistent than introducing facade infrastructure.
- Adding `get_active_empire_id()` to `StrategySessionFacade`. Existing `StrategyScreen.current_empire` property is sufficient. Deferred unless facade-purity becomes a priority.
- Hooking the `StrategyScreen.session` setter for production save/load. Per `screen_router.py:324-344`, production load creates a fresh `StrategyScreen`; the setter is test-only. Phase 1 Task 1.8 asserts the production guarantee instead.
- Closure refactor of action button handlers. Per Codex review, `check_action_button_press()` already reads `row.get("row_index")` at click time (`virtual_table.py:516-524`). Phase 2 Task 2.4 simplified to verification + cross-yard regression coverage.
- Save-file migration. There is none for this UI state.
- Performance work beyond preserving the existing budgets.
- Changes to PROJ-373 phase 3's geometry check semantics.
- A generation counter on `BuildQueueQueueDataSource` (Performance Analyst noted ~1–2 ms redundancy per refresh; below threshold to justify the change in this project).

## Final Design

### Three layered hooks (revised after Codex review, arc01-002)

1. **B-hook (renderer → table)**: `BuildQueueRenderer.refresh_queue_display()` calls `virtual_table.invalidate_widget_caches()` before `update_visible_rows()` whenever it pushes new data via `set_queue()`. Fires on every queue mutation (add/remove/reorder). *Note: the existing `force_update()` call in the same method already trips the scroll/count guard for BQ specifically; the dirty flag is defense-in-depth + clean semantics for generic VirtualTable consumers.*
2. **C-hook (screen → collaborators)**: `BuildQueueScreen.open_for_yard()` explicitly resets controller queue refs (including the **zero-source case**, new Task 3.6), drag handler `selected_design` (already cleared per Codex — locked by Phase 1 Task 1.1), and (transitively, via the renderer) the table caches before `_refresh_queue_display()`. Fires once per yard switch / reopen.
3. **A-hook (manager polling + cached-screen rebind)**: `StrategyBuildQueueManager._open_build_queue()` polls `self._screen.current_empire.id` (per `strategy_screen.py:192` — *not* a new facade method) and compares against the last-seen empire id; on change, calls `cached_screen.on_active_player_changed()` to flush state. **Always before `open_for_yard()`**: rebinds `cached_screen.empire` / `cached_screen.galaxy` / `cached_screen.facade` to current values. Without the rebind, the cached screen still queries as the previous empire (`build_queue_source.py:412-416`). Save/load is handled by the **production scene-replacement guarantee** (`screen_router.py:324-344` constructs a new `StrategyScreen`); Phase 1 Task 1.8 asserts the new screen has `build_queue_screen is None`.

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
| Build queue controller | `game/ui/panels/build_queue_controller.py` | 3 (zero-source reset, Task 3.6) |
| Build queue drag handler | `game/ui/panels/build_queue_drag_handler.py` | (no edit — `selected_design` already cleared at line 101 per Codex review; Phase 1 Task 1.1 locks behavior) |
| Strategy build queue manager | `game/ui/screens/strategy_build_queue_manager.py` | 4 |
| Strategy screen | `game/ui/screens/strategy_screen.py` | (no edit — Task 4.3 dropped; production load creates fresh `StrategyScreen` per `screen_router.py:324-344`. `current_empire` property at line 192 is read by the manager, not modified.) |
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
