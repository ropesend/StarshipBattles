# PROJ-410 Findings: Perf Optimizations from PROJ-373 Phase 3 & PROJ-376 Phase 2

> **Purpose:** Identify perf-critical code paths and design decisions from recent landings that PROJ-410 must preserve while fixing stale-widget-cache contamination.

## 1. PROJ-373 Phase 3: VirtualTable Row-Pool Reuse Guard

**Commit:** aca743a25 (2026-05-05)

### Files Changed
- game/ui/components/table/virtual_table.py — early-return guard added
- tests/unit/ui/components/table/test_virtual_table.py — 4 new test cases

### Perf Mechanism: Dimension-Change Check
**Early-return condition** (virtual_table.py:148-153):
- Compares cached _last_pool_dims (tuple of panel_height, row_height) against current dimensions
- Returns early from _rebuild_row_pool() when dimensions unchanged and a pool already exists
- Early-return skips ~1.5s of widget tear-down/recreate per yard switch

**Implementation details:**
- _last_pool_dims cached as 2-tuple at line 103
- Cache updated after rebuild at line 189: self._last_pool_dims = (panel_rect.height, self._row_height)
- Constructor always builds (no prior pool, early-return never fires on init)
- _pool_dims_changed() method is single point of truth (lines 148-153)

### Claimed Perf Improvement
- ~1.5s/click saved when panel dimensions unchanged AND pool already exists
- Materializes only when Phase 2 (screen reuse) active; Phase 3 ships independently to prevent future regression

### Tests Protecting the Perf Win
**TestRowPoolReuseGuard class** (test_virtual_table.py:1097-1292):
1. test_rebuild_skipped_when_dimensions_unchanged — pool widgets NOT killed on identity-dims reopen
2. test_rebuild_runs_when_panel_height_changes — rebuild triggers on height change
3. test_rebuild_runs_when_row_height_changes — rebuild triggers on row_height change
4. test_force_update_does_not_force_pool_rebuild — force_update() doesn't invalidate dims cache

**Lock-in mechanism:** Tests assert widget .kill() call counts; dimension-check logic changes fail immediately.

---

## 2. PROJ-376 Phase 2: BuildQueueScreen Instance Reuse

**Commit:** a93330bb9 (2026-05-07)

### Files Changed
- game/ui/screens/build_queue_screen.py — _close() removed, _request_close()/hide()/show()/is_visible() added
- game/ui/screens/strategy_build_queue_manager.py — lazy construct + reuse via _open_build_queue()
- game/ui/screens/strategy_event_router.py:58 — is not None → is_visible() gate
- game/ui/screens/strategy_input_handler.py:55 — is not None → is_visible() gate
- game/ui/screens/strategy_screen.py:246 — is not None → is_visible() gate

### Perf Mechanism: Panel-Tree Survival Across Opens

**Manager construction pattern** (strategy_build_queue_manager.py:165-218):
- First click: constructs BuildQueueScreen(initial_yard=None) (~6.9s)
- Subsequent clicks: rebind design_library, design_loader, portrait_loader on cached instance, then call open_for_yard() (~150ms)
- Dependency rebinding inline in _open_build_queue(), not via separate method on screen

**Close path** (build_queue_screen.py:806-823):
- Old: _close() killed panel tree + nulled slot
- New: _request_close() calls hide() (panels survive invisible) then on_close()
- Manager's _on_build_queue_close() no longer nulls self._screen.build_queue_screen
- Pattern: close-button + Esc handler both route through _request_close()

**Visibility gates** (all three sites required):
- strategy_event_router.py:58-65 — modal-block check gates on is_visible()
- strategy_input_handler.py:55-61 — event routing gates on is_visible()
- strategy_screen.py:246-251 — draw call gates on is_visible()

### Claimed Perf Improvement
- ~3-4s/click on repeat opens via elimination of panel-tree reconstruction
- First open: ~6.9s (unavoidable construction)
- Combines with Phase 1 validation cache (~2.2s) + Phase 3 row-pool guard (~1.5s) toward <0.5s repeat-open target

### Tests Protecting Reuse Behavior
**Manager tests** (test_strategy_build_queue_manager.py:533-658):
1. test_reopens_when_build_queue_already_constructed — second click calls open_for_yard() not __init__
2. test_second_click_calls_open_for_yard_not_construct — dual-click flow validation
3. test_navigate_reuses_cached_instance — reuse works for on_navigate_to_hex_build entry point

**Lifecycle tests** (test_build_queue_screen_lifecycle.py:453-525):
1. test_request_close_hides_and_invokes_on_close — panels survive (.alive() true after close)
2. test_close_method_is_removed — regression guard: _close must not exist
3. test_request_close_can_be_re_opened — panels reusable after _request_close(); identity unchanged

**Lock-in mechanism:** Tests assert panel .alive() and object identity; lifecycle changes fail immediately.

---

## 3. Critical Design Decisions

### Validation Cache (PROJ-373 Phase 1)
- Lives on BuildQueueController._validation_cache (dict, keyed by (design_id, mtime))
- **Critical:** PROJ-373 review MAJ-003 flags cache destruction per-click today; Phase 2 reuse makes cache cross-open effective
- Must survive across open_for_yard() calls

### Row-Pool Guard Dependency
- Precondition: Phase 2 must keep pool alive across yard switches
- Phase 3 deferred in PROJ-373; Phase 2 implemented in PROJ-376; now both active
- Out-of-scope in PROJ-373 itself; PROJ-376 landing makes guard effective

### Instance-Reuse Constraints
- **Dependency rebinding:** Manager constructs DesignLibrary + DesignLoaderAdapter per click; rebound onto cached screen (lines 199-214 of strategy_build_queue_manager.py)
- **portrait_loader reconstruction:** Rebuilt with new library reference (mandatory; carries design registry)
- **drag_handler.design_library rebinding:** Handled inside open_for_yard() (existing)
- **Cross-context transitions (planet ↔ fleet):** Trigger _rebuild_panels() (rare; acceptable cost)
- **PlanetSelectionWindow lifecycle:** hide() kills modal (replicates old _close() pattern at line 641-643)

### Facade Contract (PROJ-382 Phase 1 eradication)
Per docs/02_PATTERNS.md Pattern #5, "when NOT to use" section:
> "PROJ-382 Phase 1 specifically eradicated facade-bypass paths from BuildQueueScreen and EmpireBuildQueueWindow"

**BuildQueueScreen facade usage** (build_queue_screen.py):
- Stored at line 95: self.facade = facade
- Command dispatch: lines 448, 482, 515 (self.facade.handle_command())
- Registry access: lines 212, 217, 238, 296, 522 (self.facade.get_registries())

**PROJ-410 constraint:** Invalidation hooks must route through self.facade.handle_command(), NOT bypass via direct session access. Static guard at tests/static_guards/test_facade_bypass_guard.py will catch regressions.

---

## 4. Perf Budgets & Acceptance Criteria

**From PROJ-373 decisions.md (line 19):**
- Repeat-open: <0.5s wall-clock at baseline resolution

**From PROJ-376 plan.md (lines 149-150):**
- Repeat-open BuildQueueScreen.__init__-equivalent cumulative: <0.5s
- First-open cost preserved: ~3.7-4.0s (with Phases 1 + 4)

**Profiling baseline:** Projects/active_projects/PROJ-373/findings/profile_summary.md
- Pre-landing cost: 6.83s / 6.82s / 6.96s (mean 6.87s per click)

---

## 5. Summary: What PROJ-410 Must Preserve

1. **Row-pool dimension check** — _pool_dims_changed() at line 148 prevents rebuild when (panel_height, row_height) unchanged. Tests assert .kill() counts.

2. **Screen instance reuse** — Cached instance + panel tree must survive hide()/show() cycles. Tests assert .alive() and object identity.

3. **Three is_visible() gates** — Input, draw, modal-block checks must use is_visible() not is not None. Instance always exists post-first-open; visibility is the gate.

4. **Facade-route compliance** — All command dispatch via self.facade.handle_command(). No direct session bypass.

5. **<0.5s repeat-open latency** — Cache invalidation logic must not force full reconstruction.

---

**Key file:line references:**
- game/ui/components/table/virtual_table.py:103, 148-153, 189 — dims cache
- game/ui/screens/build_queue_screen.py:95, 448, 482, 515, 806-823 — facade + close
- game/ui/screens/strategy_build_queue_manager.py:165-218 — lazy construct
- game/ui/screens/strategy_event_router.py:58-65, strategy_input_handler.py:55-61, strategy_screen.py:246-251 — visibility gates
- tests/unit/ui/components/table/test_virtual_table.py:1097-1292 — row-pool tests
- tests/unit/ui/screens/test_strategy_build_queue_manager.py:533-658, test_build_queue_screen_lifecycle.py:453-525 — reuse tests
