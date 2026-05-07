# PROJ-373: Build queue open latency

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-373` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-373 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Cache `_validate_designs` results | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Reuse `BuildQueueScreen` instance across opens | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Reuse VirtualTable row pool across opens | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Reduce rounded-rect drawable cost (theme/pre-bake) | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-05 (project scaffolded)
**Active Phase:** Phase 1 — Cache `_validate_designs` results
**Last Action:** Project scaffolded from a pyinstrument profile of 3 sequential build-queue opens (~6.9s each, ~20.6s total = 35.7% of a 58s session). Three Explore subagents produced research reports under `findings/`.
**Next Action:** Begin Phase 1 — implement validation result cache on `BuildQueueController._validate_designs`.
**Blockers:** None.

**Profile baseline (from `findings/profile_summary.md`):**
- Per-click cost: 6.83s / 6.82s / 6.96s (mean 6.87s)
- `_validate_designs`: 2.2s/click → Phase 1 target
- `BuildQueueScreen.__init__` (panel construction): 4.4s/click → Phase 2+3+4 target
- `_rebuild_row_pool`: 1.5s/click (subset of the 4.4s) → Phase 3 target
- Rounded-rect rasterization: ~3s/click (subset of the 4.4s) → Phase 4 target

## Overview

The build-queue overlay takes ~6.9 seconds to open. The pyinstrument profile (`findings/profile_summary.md`) localizes the cost to two halves: ~2.2s spent re-validating unchanged designs (deserialize + simulation-layer validation per design, every click), and ~4.4s spent reconstructing the entire pygame_gui panel tree from scratch (UIPanel `__init__` → `RoundedRectangleShape.redraw_state`). Both are pure waste — the screen is opened multiple times in a session, the designs typically don't change between opens, and the panel layout only depends on the build context's *type* (planet vs. fleet), not on which specific yard.

The four phases tackle these costs in ascending order of risk and decreasing order of ROI/effort, leaving the most surgical low-risk wins first so each phase can ship and be measured independently.

## Goals

- **Phase 1 closed:** `_validate_designs` populates a per-controller cache keyed by `(design_id, design-data fingerprint)`. Repeat opens with unchanged designs hit the cache and skip both `Ship.from_dict` and `validator.validate`. Saves ~2.2s on every repeat open. Cache invalidates correctly when a design is saved/edited.
- **Phase 2 closed:** `BuildQueueScreen` is constructed once per `StrategyBuildQueueManager` lifetime and reused across opens. The close path becomes "hide", not "kill". Yard-switch goes through a new `open_for_yard(yard)` method that resets the minimum yard-specific state (queue sources, selection, controller filters, drag handler) and calls existing refresh paths. Saves the bulk of the 4.4s/click panel-construction cost on second-and-later opens.
- **Phase 3 closed:** VirtualTable's row-pool widgets survive across screen reuses where panel dimensions are unchanged. After Phase 2 lands, this is largely automatic; Phase 3 verifies and adds explicit guards so geometry-change paths still rebuild the pool correctly. Saves ~1.5s/click in the subset of cases where row pool would otherwise be rebuilt.
- **Phase 4 closed:** Either (a) the global `panel` theme switches `shape` from `rounded_rectangle` to `rectangle` (one-line change in `data/builder_theme.json`), or (b) build-queue panels get a scoped `object_id` override that selects a `rectangle` shape. Eliminates anti-aliased corner rasterization on first open and on every other panel-heavy screen in the game.
- **Final acceptance:** A repeat open of the build queue costs **< 0.5s** wall-clock at the same screen resolution as the baseline profile. Verified by re-profiling and comparing `BuildQueueScreen.__init__` cumulative time against the baseline.

## Scope

**In:**
- `game/ui/panels/build_queue_controller.py` — Phase 1: cache for `_validate_designs`. Cache invalidation hook.
- `game/strategy/services/design_validator.py` — Phase 1: optional — if cache lives on the validator instead of the controller, this is the cache owner.
- `game/strategy/systems/design_library.py:184` (`save_design`) — Phase 1: invalidation point if we don't use mtime-based keying.
- `game/ui/screens/strategy_build_queue_manager.py` — Phase 2: move construction out of `on_build_yard_click` (3 sites: lines 100, 213, 257). Replace close-callback nulling with hide.
- `game/ui/screens/build_queue_screen.py` — Phase 2: split `__init__` into "construct shell" + `open_for_yard(yard)` refresh. Replace `_close()` with `hide()`. Keep instance alive across opens.
- `game/ui/screens/build_queue_drag_handler.py` — Phase 2: add `reset_state()` for reuse.
- `game/ui/components/table/virtual_table.py` — Phase 3: verify row pool is reused on yard switch when panel dimensions are unchanged; add explicit guard for dimension-change rebuild.
- `data/builder_theme.json:60-70` (the `panel` block) — Phase 4: shape change OR add scoped object_id overrides.
- `game/ui/screens/build_queue_panel_factory.py` — Phase 4: if scoped, set `object_id` on the build-queue panels to opt into the rectangle shape.
- `tests/unit/ui/panels/test_build_queue_controller.py` — Phase 1: cache hit/miss/invalidate tests.
- `tests/unit/ui/screens/test_build_queue_screen_lifecycle.py` (new) — Phase 2: instance-reuse tests, yard-switch state-reset tests.
- `tests/unit/ui/components/table/test_virtual_table.py` — Phase 3: pool-reuse tests.

**Out:**
- Other slow interactions in the game (battle screen, galaxy panning, design workshop) — separate projects if profiling justifies them.
- Refactors to `pygame_gui` itself.
- Changes to the build-queue *visual layout* — this project is purely about latency, not UX.
- Strategy-screen grid caching — separate project (PROJ-374).
- Caching `load_design_data` (file load) inside `DesignLibrary` — possibly worth a follow-up, but the profile shows the validation cost dominates the load cost; out of scope for this round.

## Key Files

| Component | File Path |
|-----------|-----------|
| Build-queue click handler (3 entry points) | `game/ui/screens/strategy_build_queue_manager.py:100,213,257` |
| Build queue screen constructor | `game/ui/screens/build_queue_screen.py:48` |
| Build queue close path | `game/ui/screens/build_queue_screen.py:639` |
| Panel factory | `game/ui/screens/build_queue_panel_factory.py:136` |
| Validation entry point | `game/ui/panels/build_queue_controller.py:193` |
| Design validator | `game/strategy/services/design_validator.py:53` |
| Design library save | `game/strategy/systems/design_library.py:184` |
| Virtual table row pool | `game/ui/components/table/virtual_table.py:143` |
| Drag handler | `game/ui/screens/build_queue_drag_handler.py:74` |
| Theme JSON | `data/builder_theme.json:60-70` |
| Profile evidence | `findings/profile_summary.md` |
| Lifecycle research | `findings/01_lifecycle_research.md` |
| Drawable cost research | `findings/02_drawable_cost_research.md` |

## Related Documents
- [design.md](design.md) — diagnosis, target pipelines, alternatives, risks
- [decisions.md](decisions.md) — design choices and rejected alternatives
- [findings/profile_summary.md](findings/profile_summary.md) — originating pyinstrument evidence
- [findings/01_lifecycle_research.md](findings/01_lifecycle_research.md) — build-queue UI lifecycle code map
- [findings/02_drawable_cost_research.md](findings/02_drawable_cost_research.md) — pygame_gui rounded-rect cost map

## Phases

### Phase 1: Cache `_validate_designs` results [Simple]
**Objective:** Eliminate the ~2.2s/click validation cost. Cache validation results keyed by design fingerprint; invalidate when a design is saved.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md).

### Phase 2: Reuse `BuildQueueScreen` instance across opens [Medium]
**Objective:** Construct `BuildQueueScreen` once per `StrategyBuildQueueManager` lifetime; subsequent opens go through a new `open_for_yard(yard)` method that refreshes only yard-specific state. Replace `_close()` with `hide()`. Eliminates ~3-4s/click on second-and-later opens.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md).

### Phase 3: Reuse VirtualTable row pool across opens [Simple]
**Objective:** Verify Phase 2's reuse keeps the row pool alive. Add an explicit guard so `_rebuild_row_pool` is only called when panel dimensions change, not on every yard switch. Saves ~1.5s/click in the steady state.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md).

### Phase 4: Reduce rounded-rect drawable cost [Simple]
**Objective:** Switch the global `panel` theme (or scoped build-queue object_id) from `rounded_rectangle` to `rectangle`. Eliminates anti-aliased corner rasterization on first open and benefits every other panel-heavy screen in the game.
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md).

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`, `docs/03_CONVENTIONS.md`
- [ ] Read `findings/profile_summary.md`, `findings/01_lifecycle_research.md`, `findings/02_drawable_cost_research.md`
- [ ] Run `python Tools/test_sharded/test_sharded.py` — capture baseline pass count

### After Each Phase
- [ ] Run focused tests for the touched modules
- [ ] Run `python Tools/test_sharded/test_sharded.py` — sharded suite green; pass count grows monotonically
- [ ] Re-profile the build-queue open under `python Tools/profile_game/profile_game.py` and confirm the per-click cost dropped as expected
- [ ] Update Current State in this plan with handoff context for the next agent

### Final Verification
- [ ] Sharded suite green; pass count ≥ baseline + new tests
- [ ] Repeat-open of build queue under pyinstrument: `BuildQueueScreen.__init__`-or-equivalent cumulative time **< 0.5s** at the same screen resolution as the baseline (was ~6.9s)
- [ ] First-open cost reduced by ≥ 30% (Phase 4 contribution)
- [ ] Manual smoke test: open + close build queue 5x in a row, switch between two different yards, edit a design and reopen the queue — all behave correctly with no stale state
- [ ] Visual regression on other panel-heavy screens after Phase 4 (Phase 4 can move to scoped object_id if a regression shows up)

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing (sharded suite green)
- [ ] Re-profile shows the per-click cost goal met
- [ ] User verified
