# PROJ-376: BuildQueueScreen Lifecycle Refactor (PROJ-373 Phase 2 follow-up)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-376` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-376 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Lifecycle seam — split `BuildQueueScreen.__init__` into shell + `open_for_yard()` (manager unchanged) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Instance reuse — manager constructs once, calls `open_for_yard()` thereafter; replace `_close()` with `hide()` / `show()` | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Acceptance + dead-code activation — close PROJ-373 acceptance bar, activate `reset_filters()`, address PROJ-373 review MIN findings | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-07
**Active Phase:** Phase 1 complete; ready for Phase 2.
**Last Action:** Phase 1 shipped — `BuildQueueScreen.__init__` split into shell + `open_for_yard(yard, *, hex_coord, portrait_surface=None)`; new `hide()`, `show()`, `is_visible()`, private `_construct_collaborators()` + `_rebuild_panels()`; `BuildQueueDragHandler.reset_state()` clears 5 fields; `handle_event` is visibility-gated. Manager unchanged. 10/10 lifecycle tests pass; 555/555 focused regression; sharded 19067 passed (+10 from new tests) / 1 pre-existing failure unchanged. **Note:** pygame_gui's `UIPanel` does not expose `set_visible()` — `hide()`/`show()` use `panel.hide()`/`panel.show()`; `is_visible()` reads `panel.visible`.
**Next Action:** Phase 2 — manager rewires to lazy-construct + reuse instance.
**Blockers:** None.

## Overview

This project completes the **Phase 2 deferral** carried over from PROJ-373 (build-queue open latency). PROJ-373 shipped Phases 1 (validation cache, MAJ-003), 3 (row-pool guard, MAJ-001/002 already remediated), and 4 (`@fast_panel` scoped theme). The acceptance bar — `< 0.5s` repeat-open wall-clock — is gated entirely by Phase 2's instance reuse, because today's `BuildQueueScreen` is reconstructed per click (~6.9 s) and Phase 1's controller cache is destroyed with it (PROJ-373 review MAJ-003, INFO-008). PROJ-376 splits `BuildQueueScreen.__init__` into "construct shell" + `open_for_yard(yard)`, replaces `_close()` with `hide()` / `show()`, threads `reset_state()` / `reset_filters()` through the open path, and rewires `StrategyBuildQueueManager`'s 3 construction sites and its close callback. The reward is the bulk of the 4.4 s/click panel construction cost on every repeat open within a session.

## Goals

- **Phase 1 closed:** `BuildQueueScreen.__init__` accepts `initial_yard: Planet | Fleet | None = None`. UI-shell construction (factory, renderer, controller, drag handler, tooltips) is unconditional; yard-specific state (`build_context`, `hex_coord`, `queue_sources`, `active_queue_source`, `selected_queue_indices`, `planet_selection_window`) only populates when an `initial_yard` is supplied. New public method `open_for_yard(yard)` runs the yard-specific reset path. New method `BuildQueueDragHandler.reset_state()` zeros all five drag-state fields (`dragged_item`, `drag_preview`, `drag_start_pos`, `_pending_queue_index`, `selected_design`). Manager-side construction sites are **unchanged** — every call still constructs a fresh screen. Behavior parity is the acceptance criterion. New unit tests assert that `open_for_yard` reproduces today's post-init state for the same yard.
- **Phase 2 closed:** `StrategyBuildQueueManager` constructs `BuildQueueScreen` once on first build-yard click (lazy first open), stores the instance, and reuses it for every subsequent open via `open_for_yard()`. `_close()` is replaced by `hide()` / `show()` — the panel tree survives close. The close callback no longer nulls `self._screen.build_queue_screen`; callers that gated on `is not None` migrate to `is_visible()`. Cross-context-type opens (planet ↔ fleet) trigger `_rebuild_panels()`. FEAT-17 pause-button label is correctly resynced on every `open_for_yard` via the existing `renderer.refresh_pause_button(...)` path. Sharded suite green; manual smoke (5+ open/close cycles, planet→fleet→planet, drag-and-drop across opens) clean.
- **Phase 3 closed:** PROJ-373's `< 0.5s` repeat-open acceptance bar is met under re-profile. `BuildQueueController.reset_filters()` (added in PROJ-373 Phase 1, dead until now) becomes live code via `open_for_yard`. PROJ-373 review MIN-001 (dead-code comment), MIN-002 (HFS+ mtime resolution comment), MIN-003 (rebuild_row_pool layout-pass docstring), MIN-005 (column-config-change test) are addressed. PROJ-373 plan.md Phase 1 Quick Status caveat (review MAJ-003) and Phase 2 detailed-status update (review MAJ-004) backfilled. PROJ-373 row-pool guard now actually pays the ~1.5 s/click it was designed for (PROJ-373 review INFO-003).

## Scope

**In:**
- `game/ui/screens/build_queue_screen.py` — Phase 1: split `__init__`; add `open_for_yard()`, `hide()`, `show()`, `is_visible()`, private `_rebuild_panels(context_type)`. Phase 2: delete `_close()`, route close button + Esc + `_handle_keydown` `BUILD_QUEUE_CLOSE` through `hide()` + invoke `on_close`. Visibility-gate `handle_event`.
- `game/ui/panels/build_queue_drag_handler.py` — Phase 1: add `reset_state()` (3 attribute clears + the unmentioned `_pending_queue_index` and `drag_preview`).
- `game/ui/screens/strategy_build_queue_manager.py` — Phase 2: extract a single `_open_build_queue(yard, hex_coord, portrait_surface)` helper; the 3 entry points (lines 71, 175, 229) call it. The first call constructs `BuildQueueScreen`; subsequent calls call `open_for_yard()`. Update `_on_build_queue_close` (line 116) to call `hide()` and stop nulling the screen. Remove the 3 entry guards (lines 74, 186, 232) since reopens are no-ops.
- `game/ui/screens/strategy_event_router.py:58` — keep as is; the `is not None` check still works (instance is constructed lazily on first open).
- `game/ui/screens/strategy_input_handler.py:55-56` — wrap with `is_visible()` so events route only when the screen is actually visible.
- `game/ui/screens/strategy_screen.py:246` — wrap with `is_visible()` for the draw call (otherwise we'd draw a hidden screen).
- `game/ui/panels/build_queue_controller.py` — Phase 3: add the dead-code comment per PROJ-373 review MIN-001.
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (new) — Phase 1 + 2: tests for shell-only construction, `open_for_yard` state mutation, `hide`/`show`/`is_visible`, instance reuse across N opens, planet↔fleet panel rebuild, drag-state reset.
- `tests/unit/ui/screens/test_strategy_build_queue_manager.py` — Phase 2: existing tests update to assert `open_for_yard()` is called rather than `BuildQueueScreen.__init__` on the second open; add tests for the close-callback no longer nulling.
- `tests/integration/ui/build_queue_screen/test_basics.py:188` — Phase 2: update `_close()` reference to `hide()`.
- `Projects/active_projects/PROJ-373/plan.md` — Phase 3: backfill the MAJ-003/MAJ-004 caveats.

**Out:**
- Other panel-construction wins (e.g., applying `@fast_panel` to `VirtualTable` row backgrounds — see PROJ-373 review INFO-006). Future project.
- New visual or UX changes to the build queue.
- Battle-screen / strategy-grid latency. Separate projects.
- pygame_gui upstream changes.
- Refactoring `BuildQueueController` further (no field renames, no method renames beyond `reset_filters` activation).
- Re-baselining all of pygame_gui's modal-stack semantics — this project does NOT migrate `BuildQueueScreen` to `StrategyModalWindow` (BuildQueueScreen is a full-screen overlay, not a `UIWindow` subclass; PROJ-313's machinery is not the right shape here — see decisions.md row 1).

## Key Files

| Component | File Path |
|-----------|-----------|
| Build queue screen — split target | `game/ui/screens/build_queue_screen.py:48` (`__init__`) |
| Build queue screen — close target | `game/ui/screens/build_queue_screen.py:639` (`_close`) |
| Build queue screen — event entry | `game/ui/screens/build_queue_screen.py:397` (`handle_event`) |
| Drag handler — reset target | `game/ui/panels/build_queue_drag_handler.py:73-81` (`__init__` drag-state block) |
| Manager — 3 construction sites | `game/ui/screens/strategy_build_queue_manager.py:100, 213, 257` |
| Manager — close callback | `game/ui/screens/strategy_build_queue_manager.py:116-148` |
| Manager — entry guards | `game/ui/screens/strategy_build_queue_manager.py:74, 186, 232` |
| Strategy screen — `build_queue_screen` slot | `game/ui/screens/strategy_screen.py:116, 246` |
| Strategy event router — modal check | `game/ui/screens/strategy_event_router.py:58` |
| Strategy input handler — event routing | `game/ui/screens/strategy_input_handler.py:55-56` |
| Controller — `reset_filters` (dead until Phase 2) | `game/ui/panels/build_queue_controller.py:260-268` |
| Panel factory (no changes; reused on rebuild) | `game/ui/screens/build_queue_panel_factory.py` |
| Renderer (no changes) | `game/ui/screens/build_queue_renderer.py` |
| VirtualTable row-pool guard (already remediated) | `game/ui/components/table/virtual_table.py:148-211` |
| Panel-set dataclass | `game/ui/screens/build_queue_panel_factory.py:50` (`BuildQueuePanels`) |

## Related Documents

- [design.md](design.md) — yard-specific reference catalogue, modal-stack analysis, alternatives, risks
- [decisions.md](decisions.md) — pre-populated architectural decisions
- [findings/initial_review.md](findings/initial_review.md) — top 5 surprising facts from the investigation
- `Projects/active_projects/PROJ-373/plan.md` — original 4-phase plan; PROJ-376 picks up the deferred Phase 2
- `Projects/active_projects/PROJ-373/decisions.md` (2026-05-06 row) — deferral rationale
- `Projects/active_projects/PROJ-373/phase_2_checklist.md` — task seed (this project supersedes and refines it)
- `Projects/active_projects/PROJ-373/findings/01_lifecycle_research.md` — reference Explore-subagent investigation
- `Projects/active_projects/PROJ-373/findings/profile_summary.md` — pyinstrument evidence
- `Reviews/results/2026-05-06_051908_code_proj-373-build-queue-latency-phases-1-3-4-cache-co_req-req_20260506_051906_ddfd29/report.md` — review with MIN-001/MAJ-003/MAJ-004 etc.
- `Projects/deep_archive/PROJ-301-350/PROJ-313/findings/strategy_modal_window_base_class.md` — the modal-window machinery this project intentionally does NOT use

## Today's vs. target pipeline (one-line diff)

**Today** (`strategy_build_queue_manager.py:71-114`, every click):
```
on_build_yard_click → if build_queue_screen is None: build_queue_screen = BuildQueueScreen(planet, ...)   # 6.9s
on_close_callback   → screen._close() → panels.background.kill() → manager.update(0); build_queue_screen = None
```

**Target** (after PROJ-376 Phase 2):
```
on_build_yard_click → _open_build_queue(yard, hex_coord, portrait_surface)
   if build_queue_screen is None: build_queue_screen = BuildQueueScreen(initial_yard=None, ...)            # 6.9s once
   build_queue_screen.open_for_yard(yard)                                                                  # ~150ms
on_close_callback   → screen.hide()                                                                        # ~ms
```

## Phases

#### Phase 1 summary: Lifecycle seam (no behavior change) [Medium]
**Objective:** Split `BuildQueueScreen.__init__` into "UI shell" + `open_for_yard(yard)`. Add `hide()` / `show()` / `is_visible()` / `_rebuild_panels()` and `BuildQueueDragHandler.reset_state()`. **Manager unchanged.** Today's behavior is preserved bit-for-bit (manager still constructs a fresh screen per click); the seam is the only change. Acceptance: identical post-init field values for any given yard whether traversed via `__init__(initial_yard=yard)` or `__init__(initial_yard=None)` + `open_for_yard(yard)`.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md).

#### Phase 2 summary: Instance reuse [Medium]
**Objective:** `StrategyBuildQueueManager` constructs `BuildQueueScreen` lazily on first build-yard click and reuses the instance. Replace `_close()` (kills panel tree) with `hide()` (panels survive). Replace null-the-slot close-callback with hide-the-screen close-callback. Migrate all three call sites (input handler, draw, event-router modal-block check) to `is_visible()`. Rationale per `decisions.md:12`. Add `_rebuild_panels()` for the rare planet↔fleet transition. Validate FEAT-17 pause-button label and PlanetSelectionWindow lifecycle.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md).

#### Phase 3 summary: Acceptance + close-out [Simple]
**Objective:** Re-profile build-queue opens; assert `< 0.5s` repeat-open per PROJ-373's acceptance criterion. Activate `BuildQueueController.reset_filters()` (used by Phase 1 in `open_for_yard`; PROJ-373 review MIN-001 dead-code comment becomes obsolete and is replaced with a "live since PROJ-376" comment). Backfill PROJ-373 plan.md MAJ-003 caveat (Phase 1 row) and MAJ-004 detailed-status update (Phase 2 row) per the deferred review. Update PROJ-373 review MIN-002 (HFS+ comment) and MIN-003 (`rebuild_row_pool` layout-pass docstring) and MIN-005 (column-config test).
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`, `docs/06_UI_STYLE_GUIDE.md`
- [ ] Read `docs/systems/strategy_layer.md`
- [ ] Read PROJ-373 `plan.md`, `design.md`, `decisions.md`, `phase_2_checklist.md`, `findings/01_lifecycle_research.md`, `findings/profile_summary.md`
- [ ] Read the 2026-05-06 OpenCode review of PROJ-373 (MIN-001, MAJ-003, MAJ-004, INFO-002, INFO-008)
- [ ] Read [findings/initial_review.md](findings/initial_review.md)
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count

### After Each Phase
- [ ] Run focused tests: `pytest tests/unit/ui/screens/test_build_queue_screen_lifecycle.py tests/unit/ui/screens/test_strategy_build_queue_manager.py tests/integration/ui/build_queue_screen/ -v`
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically (Phase 1 adds ~7 tests, Phase 2 adds ~5, Phase 3 modifies 1 existing test)
- [ ] Run `python Projects/scripts/phase_complete.py PROJ-376 {phase-id}` (per 03c protocol — runs `validate_phase.py` + tests + commit + cumulative review dispatch)
- [ ] Update `Current State` in this plan with handoff context

### Final Verification
- [ ] Sharded suite green; pass count ≥ baseline + 12 new tests
- [ ] Re-profile under `python Tools/profile_game/profile_game.py`: open build queue 3× at the same yard (matches PROJ-373's repro). Repeat-open `BuildQueueScreen.__init__`-equivalent cumulative time **< 0.5s**. First-open cost preserved (~3.7-4.0 s with PROJ-373 Phase 1+4 still in effect).
- [ ] Manual smoke: 5 open/close cycles at the same planet; switch to a fleet build queue; switch back to a planet; drag-and-drop a queue item across two opens; edit a design in the workshop and reopen — invalid badge appears.
- [ ] Acceptance: PROJ-373 `< 0.5s` repeat-open bar met (recorded in `findings/post_proj376_profile.md`).
- [ ] PROJ-373 review MIN-001/MIN-002/MIN-003/MIN-005, MAJ-003/MAJ-004 close-outs landed.
- [ ] No `_close()` symbol remains in `game/ui/screens/build_queue_screen.py` (grep regression).

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Re-profile shows the per-click acceptance bar met
- [ ] PROJ-373 plan.md backfill landed
- [ ] User verified
