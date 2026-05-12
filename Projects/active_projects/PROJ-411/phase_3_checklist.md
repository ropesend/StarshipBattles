# Phase 3: Regression Gates + Docs

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-411 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress — Task 3.0 (Track B kickoff) complete + F9 verified (20 % win); original 3.1–3.x lock-in tasks still pending
**Objective:** Lock in the wins from Phases 1 and 2 with regression gates and doc updates, AND attack first-open cost (Track B) — the dominant remaining UX lag after Phase 2 reuse eliminated re-open cost.

---

## Tasks

### Task 3.0: pygame_gui cache-key fix via scoped UI adapter [Medium] — Track B kickoff
**Files:**
- `game/ui/pygame_gui_patch.py` (new) — `StarshipUIAppearanceTheme` + `StarshipUIManager` subclasses + source-fingerprint guard
- 8 production sites migrated from `pygame_gui.UIManager(...)` to `StarshipUIManager(...)`: `strategy_ui.py:75`, `battle_setup/renderer.py:42`, `research_scene.py:120,268`, `workshop_screen.py:88`, `menu_scene.py:45`, `keybindings_scene.py:101,350`, `galaxy_test/screen.py:68,272`, `test_lab/screen.py:89`
- `requirements.txt` — pin `pygame_gui==0.6.14`

**Tests:** `tests/unit/ui/test_pygame_gui_patch.py` — 11 tests

- [x] Phase 1 cProfile attribution refreshed: 47/65 s (~72 %) of total open time in `str.join` + `build_all_combined_ids` self-time.
- [x] Root cause found in pygame_gui 0.6.14 `ui_appearance_theme.py:1625-1627`: cache key built via chained `str.join` where each `str(x)` is the *separator*; each character of the prior result becomes an element. Key balloons to ~10 KB; ~15 MB of string allocation per window open.
- [x] Codex consult (planning mode) reviewed approach — pushed back on monkey-patching, recommended scoped UI adapter; consult artifact at `AgentCoordination/Scratchpad/Consult/20260512T035945Z_pygame-gui-cache-key-patch/`.
- [x] Implemented `StarshipUIAppearanceTheme` (private tuple-keyed cache `_combined_ids_cache`; preserves upstream body otherwise — `ValueError` validation, `_get_next_id_node` recursion, dotted-id suffix loop).
- [x] Implemented `StarshipUIManager.create_new_theme` returning the subclass.
- [x] Source-fingerprint guard `UPSTREAM_HAS_KNOWN_BUG` — detects the unique `str(element_base_ids).join(` pattern in upstream source via `inspect.getsource`. Flips False when upstream fixes the bug; cue to delete the patch.
- [x] 11 new tests covering: guard truthy, manager returns subclass, parity (4 parametrized inputs incl. empty / None), `ValueError` preserved, no tuple keys leak into `unique_theming_ids`, cache is idempotent, key size bounded (<1 KB), perf smoke (≥2× faster than upstream on 1000 hits).
- [x] All 8 production UIManager construction sites migrated. Tests still use `pygame_gui.UIManager` directly (no migration needed — they don't pay the per-window cost).
- [x] `requirements.txt`: `pygame_gui>=0.6.9` → `pygame_gui==0.6.14` with a note tying the pin to this patch's lifecycle.
- [x] Sharded suite green: 20,157 / 20,153 passed / 0 failed / 4 skipped (after retargeting 7 test patches from `module.pygame_gui` → `module.StarshipUIManager`).
- [x] User F9 verified — actual payoff ~20 % (less than projected ~70 %). PlanetRegistry 4527.9→3720.9 ms (−18 %), StarRegistry 5026.9→3883.8 ms (−23 %), EventLog 2676.9→2147.6 ms (−20 %). EmpireOverview not exercised. cProfile self-time attribution turned out to overcount parallel/opportunistic work; cache-key fix wasn't fully on the serial critical path. User accepted the 20 % win; deeper first-open optimisation deferred. Task 3.0 complete.

**Notes:**
- Codex's main pushbacks addressed: (1) no monkey-patching — subclass instead; (2) source-fingerprint guard instead of signature-only; (3) private tuple cache attribute instead of mutating `unique_theming_ids: Dict[str, List[str]]` (type-shape preserved); (4) pinned `pygame_gui` while the patch is live.
- Patch removal procedure: when `UPSTREAM_HAS_KNOWN_BUG` flips False (upstream fix released), delete `game/ui/pygame_gui_patch.py`, revert all 8 migration sites to `pygame_gui.UIManager`, un-pin `pygame_gui` in `requirements.txt`, delete `tests/unit/ui/test_pygame_gui_patch.py`. Single-PR cleanup.

### Task 3.1: Count-based regression gates [Medium]
**Files:**
- `tests/performance/test_strategy_panel_regression.py` (new — facade-level integration gates)

**Tests:** `pytest tests/performance/test_strategy_panel_regression.py`

- [x] **Audit existing coverage first.** Most of the originally-listed gates were already shipped with Phase 1's cache tests (`test_scan_designs_caching.py`, `test_gather_planets_caching.py`, `test_facade_state_proj411_caches.py`, `test_empire_economy_caching.py`, `test_event_log_no_copy.py`, `test_empire_panel_lazy_load.py`). Listed those in the new test file's docstring as the canonical coverage map rather than duplicating them.
- [x] Added `test_facade_process_turn_clears_all_proj411_caches` — production turn-advance entry-point integration: seeds all four PROJ-411 caches, calls `facade.process_turn()` against the smoke scenario, asserts every cache is empty. The existing tests cover `FacadeSessionState.invalidate_all` directly; this gate catches a future refactor that drops the call from `process_turn`.
- [x] Added `test_load_resource_icons_module_cache_short_circuits_second_call` — verifies the module-level `_RESOURCE_ICON_CACHE` returns the SAME dict by identity on the second call. No previous test asserted this invariant.

**Notes:**
- Task 3.3's intent (extending `TestRowPoolReuseGuard` to Planet/Star/EventLog data sources) is **redundant** — the guard tests `VirtualTable.rebuild_row_pool`'s dimension-change behaviour, not data source identity. Swapping `MockDataSource` for `PlanetDataSource` exercises the same code paths. Skipping.
- Empire overview UI integration tests (asset-load counts during shell construction) were on the original list but require pygame display setup and produce limited value — `test_empire_panel_lazy_load.py` already covers the Population-tab deferral that was the main concern.

### Task 3.2: Wall-clock benchmarks (informational) [Simple]
**Files:**
- `tests/performance/benchmark_strategy_panels.py` (new — modeled on `benchmark_planet_list.py`)

**Tests:** `pytest tests/performance/benchmark_strategy_panels.py` (informational; prints values)

- [ ] Add one benchmark per panel: open the panel under the smoke scenario, time with `time.perf_counter()`, print median of 5 runs.
- [ ] Each benchmark fails only if its measured median is >2× the Phase 1 `findings/profile_after.md` recorded median. Print measured values regardless of pass/fail for visibility.
- [ ] Mark all five with `@pytest.mark.performance`.

**Notes:** Per Risk Assessor and `docs/guides/performance_profiling.md`: wall-clock gates are informational. Hard gates are count-based (Task 3.1).

### Task 3.3: Extend `TestRowPoolReuseGuard` to Planet/Star/Event Log virtual tables [Medium]
**Files:**
- `tests/unit/ui/components/table/test_virtual_table.py` (extend `TestRowPoolReuseGuard` class)

**Tests:** `pytest tests/unit/ui/components/table/test_virtual_table.py -k RowPoolReuse`

- [ ] Add `test_rebuild_skipped_when_dimensions_unchanged_planet_data_source`.
- [ ] Add `test_rebuild_skipped_when_dimensions_unchanged_star_data_source`.
- [ ] Add `test_rebuild_skipped_when_dimensions_unchanged_event_log_data_source`.
- [ ] Each test mirrors the existing `test_rebuild_skipped_when_dimensions_unchanged` (line 1170) with the panel-specific data source.

**Notes:** PROJ-373 phase 3 row-pool reuse perf lock currently has 5 tests covering only Build Queue's virtual table. Extending to the other panels enforces the same invariant repo-wide.

### Task 3.4: Documentation updates [Simple]
**Files:**
- `docs/02_PATTERNS.md` (Pattern #11 Surface Caching — note PROJ-411 per-turn extension)
- `docs/guides/performance_profiling.md` (note cProfile self-time gotcha + scoped-subclass exception)

**Tests:** N/A (doc-only changes)

- [x] In `docs/02_PATTERNS.md` Pattern #11: bumped "Last verified" to 2026-05-12. Added three subsections after the PROJ-410 cross-context invalidation note: per-turn `FacadeSessionState` caches (Phase 1), window-reuse via `hide()`/`show()` + per-empire filter snapshots (Phase 2), and the `StarshipUIAppearanceTheme` subclass workaround (Phase 3).
- [x] In `docs/guides/performance_profiling.md`: bumped "Last verified" to 2026-05-12. Added two callouts: (1) cProfile self-time can over-attribute serial cost when the hot function is on a parallel-opportunistic path; PROJ-411 Phase 3 demonstrated this (eliminated 80 % of `str.join` self-time but only ~20 % of wall-clock). (2) the `StarshipUIAppearanceTheme` subclass routes through pygame_gui's own `UIManager.create_new_theme` seam (NOT a monkey-patch); `UPSTREAM_HAS_KNOWN_BUG` flips False when upstream is fixed.
- Original third bullet about `docs/systems/strategy_layer.md` skipped — the per-turn caches are now adequately covered by Pattern #11's new subsection, and `strategy_layer.md`'s "performance/caching" section already references the facade slice without per-cache enumeration that would drift fast.

**Notes:**

### Task 3.5: Project-final smoke profile [Simple]
**Files:**
- `Projects/active_projects/PROJ-411/findings/profile_final.md` (new)

**Tests:** N/A (measurement)

- [ ] Re-run `python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance/test_strategy_panel_smoke_scalene.py`.
- [ ] Record final per-panel wall-clock numbers and the dominant remaining hotspots (if any) for each panel.
- [ ] Document any open hotspot that wasn't worth fixing (and the rationale).
- [ ] Compare to `findings/profile_baseline.md` — produce a one-table summary of before/after per panel for the user to verify.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `python Tools/test_sharded/test_sharded.py` passes (full suite, not testmon)
- [ ] All count-based regression gates pass on a fresh checkout
- [ ] Doc bumps include accurate "Last verified" dates
- [ ] `findings/profile_final.md` exists with the before/after table
- [ ] Manual user smoke: open each of the 5 panels in a running game; subjective verdict is "noticeably faster"
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete - awaiting close`
