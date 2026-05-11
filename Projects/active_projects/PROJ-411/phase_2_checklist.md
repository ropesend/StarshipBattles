# Phase 2: Per-Panel Hotspot Fixes (Profile-Driven)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-411 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Prerequisite:** Phase 1 complete; `findings/profile_after.md` shows the remaining hotspot list.
**Objective:** Address per-panel hotspots that survived Phase 1's shared wins. Each task is evidence-driven from the Scalene output, not pre-decided.

---

## How To Use This Phase

Tasks 2.1-2.5 are **candidates** identified during planning. Before starting Phase 2, read `findings/profile_after.md` and:

1. **Cross off** any candidate whose hotspot disappeared in Phase 1.
2. **Confirm** the line numbers from the Scalene output (line numbers in this file are based on Phase A investigation, may have shifted).
3. **Add** any new hotspot not anticipated here as `Task 2.N+1`.
4. **Order** the surviving tasks by CPU-time impact (highest first).

Each task follows the protocol:
1. Write or identify the failing regression test (count-based, e.g. "compute_planet_effect_keys called at most N times per open").
2. Confirm test fails on `main`.
3. Implement the fix.
4. Confirm test passes.
5. Re-run Scalene; assert hotspot moved out of top-5 lines for the relevant panel.

---

## Candidate Tasks

### Task 2.1 (CANDIDATE): `compute_planet_effect_keys()` per-turn cache [Simple]
**File:** `game/ui/screens/planet_list_filters.py` (line 133-146)
**Likely** to surface: scans `all_planets` intrinsic_abilities to discover effect-column set on every open.

- [ ] Confirm hotspot in `findings/profile_after.md`. If not present, **SKIP this task**.
- [ ] If present: add `effect_keys_cache: Optional[set[str]] = None` to `FacadeSessionState`.
- [ ] Wrap `compute_planet_effect_keys` to check cache, build on miss.
- [ ] Add cache-clear to `invalidate_all()`.
- [ ] Add count-based test `test_compute_effect_keys_cached_per_turn`.

**Notes:**

### Task 2.2 (CANDIDATE): `BuildQueueRowCollector.collect()` deeper fix [Medium]
**File:** `game/ui/screens/build_queue_list_window.py` (`BuildQueueRowCollector.collect()` line ~51)
**Likely** to surface: rebuilds row list on every refresh; not affected by Phase 1 DesignLibrary cache.

- [ ] Confirm hotspot. If absent, **SKIP**.
- [ ] If present: analyse whether the collect step is rebuildable from incremental data-source updates (mirror `VirtualTable.update_visible_rows` model).
- [ ] Implement and add count-based regression test.

**Notes:**

### Task 2.3 (CANDIDATE): Event Log incremental filter update [Medium]
**File:** `game/ui/screens/event_log_data_source.py::_recompute_filtered`
**Likely** to surface: full O(N) refilter on every category-button click.

- [ ] Confirm hotspot. If absent, **SKIP**.
- [ ] If present: switch to an incremental filter that maintains per-category indices instead of re-walking the events list.
- [ ] Add count-based test asserting filter change doesn't re-walk the full list.

**Notes:**

### Task 2.4 (CANDIDATE): Empire Overview Population first-click prefetch [Medium]
**File:** `game/ui/screens/empire_panel_window.py` + possibly `game/ui/screens/race_asset_loader.py`
**Likely** to surface: if Phase 1's lazy-load profile shows the first Population-tab click is >50 ms wall-clock, the freeze is still user-visible.

- [ ] Read Phase 1 wall-clock data for the first Population-tab click.
- [ ] If <50 ms: **SKIP** — lazy-load alone is sufficient.
- [ ] If >50 ms: design an idle-time prefetch (e.g. trigger asset load after the window has been visible for 500 ms with no user input). Reuse Pattern #28 (Background Service Call) only if the load actually warrants threading.
- [ ] Add wall-clock test that records first-Population-click time post-fix; expect <50 ms.

**Notes:**

### Task 2.5 (CANDIDATE): EmpireEconomyService snapshot construction micro-optimisation [Simple]
**File:** `game/strategy/services/empire_economy_service.py::get_snapshot`
**Likely** to surface: even after caching, the first build cost may be high on the smoke scenario (e.g. resource-by-resource accumulation).

- [ ] Confirm Scalene shows `get_snapshot` first-build >10 ms. If under, **SKIP**.
- [ ] If over: identify the dominant sub-call (likely a per-empire / per-resource loop) and reduce its complexity.
- [ ] Add wall-clock test.

**Notes:**

### Task 2.N+1: [Unanticipated hotspot from Phase 1 profile]
**File:** TBD
**Tests:** TBD

- [ ] Add tasks here as the profile output dictates.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All chosen tasks above are checked (SKIPPED tasks documented in Notes)
- [ ] Re-run Scalene profile; save as `findings/profile_after_phase2.md`
- [ ] `python Tools/test_sharded/test_sharded.py` passes
- [ ] Wall-clock per-panel before/after numbers documented for any task that changed timing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
