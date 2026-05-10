# PROJ-373: Design — Build queue open latency

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source: pyinstrument profile

`findings/profile_summary.md` captures a 58s session with 3 sequential
build-queue opens (~6.9s each, 20.6s total = 35.7% of the session). The
profile is the single source of truth for cost numbers used throughout
this design. Numeric claims here trace back to entries in that report.

---

## Today's pipeline (per build-queue click, ~6.9s)

```
on_build_yard_click (strategy_build_queue_manager.py:71)
└── BuildQueueScreen(...)                                              [build_queue_screen.py:48]   ~6.9s
    ├── BuildQueuePanelFactory.create_all_panels(...)                  [panel_factory.py:136]      ~4.4s
    │   ├── _create_background()           → UIPanel(rounded_rect)                                 ~0.9s
    │   ├── _create_build_queue_panel()                                                            ~2.8s
    │   │   ├── VirtualTable.__init__                                  [virtual_table.py:58]       ~2.0s
    │   │   │   ├── _rebuild_row_pool()    → 10-20× UIPanel rows       [virtual_table.py:143]      ~1.5s
    │   │   │   └── _build_containers()    → 1× UIPanel                                            ~0.4s
    │   │   └── 2× sub-panel UIPanel(rounded_rect)                                                 ~0.8s
    │   └── (other panels: context, design, items list, queue selector, filter, bottom bar)        ~0.7s
    └── _refresh_items_list()                                          [build_queue_screen.py:362] ~2.4s
        └── controller.load_designs_by_category()                      [bq_controller.py:137]      ~2.2s
            └── _validate_designs()                                    [bq_controller.py:193]      ~2.2s
                └── for each design d:
                    ├── design_library.load_design_data(d.design_id)   (file load + JSON parse)
                    └── DesignValidator.validate(load_result.data)     [design_validator.py:53]
                        └── Ship.from_dict(...) + ship.recalculate_stats() + sim-validator
```

The 4.4s panel branch is dominated by `pygame_gui.RoundedRectangleShape.__init__` →
`full_rebuild_on_size_change` → `redraw_all_states` → `redraw_state`
(`pygame_gui/core/drawable_shapes/rounded_rect_drawable_shape.py:67-563`),
which performs anti-aliased corner rasterization with 4× upsampling per
panel per UI state.

The 2.4s validation branch re-runs from scratch on every click even though
designs haven't changed.

---

## Target pipeline (after all 4 phases)

```
on_build_yard_click (strategy_build_queue_manager.py)
└── self.build_queue_screen.open_for_yard(planet)                                                  ~150ms
    ├── if build_context_type changed (planet ↔ fleet):
    │   └── factory.create_all_panels(...)         [panels persist normally; this branch is rare]
    ├── reset yard-specific state:
    │   ├── self.queue_sources = collect_build_queues_at_hex(...)
    │   ├── self.active_queue_source = queue_sources[0]
    │   ├── self.selected_queue_indices = {0}
    │   ├── controller.reset_filters()
    │   └── drag_handler.reset_state()
    ├── _refresh_items_list()                       (validate cache hits → milliseconds)
    │   └── controller.load_designs_by_category()
    │       └── _validate_designs()
    │           └── for each design d:
    │               ├── if (d.id, fingerprint) in cache: hit, skip                                 (instant)
    │               └── else: load + validate, store result                                        (rare)
    ├── _refresh_queue_display()                    (already incremental; ms)
    └── show()                                       (just unhide; no kill/reconstruct)
```

`BuildQueueScreen.__init__` runs once per `StrategyBuildQueueManager`
lifetime. The 4.4s panel construction is amortized; subsequent opens take
near-zero. Combined with the validation cache, repeat-open cost should be
well under the 500ms acceptance bar.

---

## Phase 1 — Cache `_validate_designs` results

### Cache shape

The simplest correct cache: a dict on `BuildQueueController` keyed by
design fingerprint, stored as `{design_id: (fingerprint, valid_bool)}`.
Lookup is "is this design's fingerprint unchanged? then return cached
`valid_bool`. else load + validate + store."

```python
# build_queue_controller.py
class BuildQueueController:
    def __init__(self, ...):
        ...
        self._validation_cache: Dict[str, Tuple[Any, bool]] = {}
        # design_id -> (fingerprint, valid_bool)

    def _validate_designs(self, designs) -> None:
        if not self._registries:
            for d in designs:
                d.design_valid = True
            return

        from game.strategy.services.design_validator import DesignValidator
        validator = DesignValidator(self._registries)

        for d in designs:
            fingerprint = self._design_fingerprint(d.design_id)
            cached = self._validation_cache.get(d.design_id)
            if cached is not None and cached[0] == fingerprint:
                d.design_valid = cached[1]
                continue

            try:
                load_result = self.design_library.load_design_data(d.design_id)
                if not load_result.success:
                    d.design_valid = False
                    self._validation_cache[d.design_id] = (fingerprint, False)
                    continue
                result = validator.validate(load_result.data)
                d.design_valid = not result.has_issues
            except Exception:  # see line 217 in current code for rationale
                d.design_valid = True
            self._validation_cache[d.design_id] = (fingerprint, d.design_valid)
```

### Fingerprint choice

Three options, ordered by simplicity:

1. **File mtime** of the design's on-disk JSON. `os.stat` is microseconds; mtime changes on every save. Pro: zero coupling to the save path. Con: if `DesignLibrary` rewrites a file with the same content (or under a clock skew), we get a false invalidation — harmless (re-validates, same result).
2. **Content hash** (e.g., `hashlib.sha1(open(path).read()).hexdigest()`). More robust than mtime, but the file read is itself work.
3. **A monotonic generation counter on `DesignLibrary`**, bumped from `save_design`. Tightest coupling but cheapest check.

Default to **(1) mtime** for Phase 1. It's the cheapest correct option and requires no save-side wiring. Migrate to (3) if the mtime check becomes a bottleneck (it won't — we're saving 2.2s and the os.stat call costs <100µs per design).

### Cache lifetime

Per-`BuildQueueController` instance. The controller is constructed inside
`BuildQueueScreen` ([build_queue_screen.py:132](../../../game/ui/screens/build_queue_screen.py#L132)),
so today the cache lives for one open. After Phase 2, the controller
survives across opens — the cache then survives across opens automatically.

This is intentional: Phase 1 alone gives us "second-and-later opens are
fast" only if the controller is reused. Today the controller is rebuilt
per open, so Phase 1 in isolation is mostly a no-op for the user.
**However:** within a single open, the same designs are validated multiple
times if categories are switched (the user clicks "Ships" then "Complexes"
then back to "Ships"). The cache still helps during a single open.

The bigger win lands when Phase 2 keeps the controller alive across opens.
Phase 1 is the prerequisite — Phase 2 unlocks its full value.

### Phase 1 success criteria
- Repeat opens within one session: `_validate_designs` cumulative time drops by ≥ 95% relative to baseline.
- Editing a design (mtime change) → next open re-validates that design (cache miss for that one entry).
- New unit tests cover: hit, miss, invalidate-on-mtime-change, exception path doesn't poison cache, cache survives controller-internal category switches.

---

## Phase 2 — Reuse `BuildQueueScreen` instance across opens

### Lifecycle change

**Today:**
```
manager.on_build_yard_click(planet):
    if self._screen.build_queue_screen is None:
        self._screen.build_queue_screen = BuildQueueScreen(planet, ...)
    [main UI hidden]

screen._close():
    self.panels.background.kill()        # kills panels recursively
    self.manager.update(0)
    self.on_close_callback()              # → manager sets self._screen.build_queue_screen = None
```

**Target:**
```
manager.__init__(...):
    self._screen.build_queue_screen = BuildQueueScreen(initial_context=None, ...)
    self._screen.build_queue_screen.hide()    # constructed but not visible

manager.on_build_yard_click(planet):
    self._screen.build_queue_screen.open_for_yard(planet)
    [main UI hidden]

screen.open_for_yard(yard):
    if self.build_context_type != yard.context_type:
        self._rebuild_panels(yard)        # rare: planet ↔ fleet transition
    self.build_context = yard
    self.hex_coord = yard.hex_coord
    self.queue_sources = collect_build_queues_at_hex(...)
    self.active_queue_source = self.queue_sources[0]
    self.selected_queue_indices = {0}
    self.selected_queue_index = 0
    self.controller.reset_filters()       # selected_category="complex", selected_role="Any"
    self.drag_handler.reset_state()       # clear dragged_item, drag_start_pos, selected_design
    self.planet_selection_window = None
    self._refresh_items_list()
    self._refresh_queue_display()
    self.show()

screen.hide()/show():
    self.panels.background.visible = False/True
    (no kill, no manager.update(0))
```

### Panel rebuild trigger

The panel layout differs between planet and fleet contexts (different
context-report panel type — `PlanetReportPanel` vs the fleet-info panel).
The reusable common case is repeat opens on the *same* type. Cross-type
transitions (planet → fleet → planet) are rare; we accept paying the full
construction cost on those transitions for simplicity.

### Drag handler reset

`BuildQueueDragHandler` ([build_queue_drag_handler.py:74-81](../../../game/ui/screens/build_queue_drag_handler.py#L74))
holds `dragged_item`, `drag_start_pos`, `selected_design`. New method
`reset_state()` zeros all three. Called from `open_for_yard`.

### Risks

- **R2.1 — UIPanel internal state survives across opens.** pygame_gui
  panels assume their lifecycle is bounded by `kill()`. Hiding instead of
  killing is supported (set `visible = False`), but unusual. If any
  internal state corrupts (e.g., focus stack), we revert this phase to
  scoped pre-baking (Phase 4b) and accept the 4.4s/click cost.
- **R2.2 — Memory growth.** A surviving screen retains all UI widget
  instances. Estimated ≤ 50 MB at 4K. Acceptable; not measured.
- **R2.3 — pygame_gui events leaked.** If buttons fire events while the
  screen is hidden, the handler may execute on a "closed" screen. Mitigate
  by routing `handle_event` to early-return when `not self.visible`.
- **R2.4 — `manager.update(0)` was load-bearing.** Currently called in
  `_close()` before nulling the screen. Moving to hide-instead-of-kill
  may leak deferred work. Verify by running for 30 seconds with the
  screen hidden after one open and confirming no log spam or warnings.

---

## Phase 3 — Reuse VirtualTable row pool across opens

After Phase 2, the `VirtualTable` instance survives across opens. The row
pool is created in `__init__` and reused by `update_visible_rows()`
([virtual_table.py:261](../../../game/ui/components/table/virtual_table.py#L261))
which is already dirty-tracked (lines 272-274).

What Phase 3 must verify and harden:

1. **Pool size is geometry-only.** `visible_rows = max(1, panel_height // row_height + 2)` ([line 161](../../../game/ui/components/table/virtual_table.py#L161)). Pool count does not depend on queue length. Reuse is safe across yard switches with the same panel size.
2. **`_rebuild_row_pool` only fires on dimension change.** Add an explicit guard: cache `(panel_height, row_height)`; on the next refresh, only rebuild if either changed.
3. **Row content is always re-bound on data change.** Verify `update_visible_rows` re-binds labels/buttons to the current queue's items, not stale references.

### Phase 3 success criteria
- After Phase 2 lands, repeat opens of the same yard never call `_rebuild_row_pool`. Verified by adding a counter or assertion in tests.
- Yard switches (same panel size) do not call `_rebuild_row_pool`.
- Window resize does call `_rebuild_row_pool`.

---

## Phase 4 — Reduce rounded-rect drawable cost

### Approach choice

**A. Global theme change.** Edit `data/builder_theme.json:67`:
- `"shape": "rounded_rectangle"` → `"shape": "rectangle"`

This affects every UIPanel using the default panel class. Visual change:
all panels become sharp-cornered. The 3px corner radius is barely visible
in the dark UI; the regression is unlikely to be noticed.

Pro: one-line change. Benefits every panel-heavy screen in the game,
not just the build queue. No code changes.
Con: irreversible without re-introducing the theme entry. Visual regression
across the whole game.

**B. Scoped object_id override.** Add a new theme entry e.g.
`"@build_queue_panel"`, set its `shape` to `rectangle`. Update the panel
factory to pass `object_id={"object_id": "@build_queue_panel"}` on each
build-queue UIPanel construction.

Pro: only affects build queue. Reversible. Other screens still get rounded
corners.
Con: requires touching every UIPanel construction in the factory.
Doesn't help other slow screens.

**Recommendation: A first, with a quick visual-regression review.** If any
specific screen looks bad after, override that one screen back to rounded
via its own object_id (the inverse of B). This way the global default
gives us speed everywhere by default, and the rounded corners become
opt-in for screens that need them.

### Phase 4 success criteria
- `data/builder_theme.json:67` changed; sharded suite green.
- First-open cost of build queue (re-profile with cache reset) drops by ≥ 30% from baseline (~6.9s → ≤ 4.8s).
- Manual visual smoke test of every screen still looks correct.

---

## Alternatives considered

### A. Single project for all 5 items vs. 4-phase split
Picked: 4 phases of one project + 1 separate project (PROJ-374 for grid).
Rejected alternative: one giant project. Rationale: each phase has independent test surface and ships independently.

### B. Validate cache on `DesignValidator` (singleton-style) vs. on `BuildQueueController`
Picked: controller. Rationale: simpler lifecycle; the validator is short-lived (constructed inside `_validate_designs`). Could revisit if other consumers of the validator emerge.

### C. Cache at `load_designs_by_category` (whole result) vs. per-design
Picked: per-design. Rationale: per-design cache survives category switches (user toggles "Ships" → "Complexes" → "Ships" — the ships are still cached). Whole-result cache would invalidate on category change.

### D. Eager `BuildQueueScreen` construction at app startup vs. first-click lazy
Picked: lazy at first click (or in `StrategyBuildQueueManager.__init__` if that runs late enough). Rationale: avoid paying construction cost on game startup if the user never opens the build queue. The first open will still pay 6.9s; only subsequent opens are fast.

### E. Pre-bake panel surfaces (Phase 4b) vs. theme simplification (Phase 4a)
Picked: theme simplification. Rationale: simpler, broader benefit, lower risk. Pre-baking remains a fallback if Phase 2 leaves a measurable first-open cost.

### F. Cache invalidation via DesignLibrary.save_design hook vs. file mtime
Picked: file mtime for Phase 1. Rationale: zero coupling. The save hook is available if mtime later proves problematic.

---

## Risks

- **R1 — Phase 2 reveals subtle pygame_gui state leakage** (focus, drag, modal handling). Mitigation: tests for "open A, hide, open B" + manual smoke test of 5+ open/close cycles. Fallback: revert to scoped pre-baking (4b).
- **R2 — Cache invalidation bug** in Phase 1: a stale-cached design shows green-checked UI even though it's invalid. Mitigation: use mtime (changes on every disk save) + `os.stat` per check. Test: edit design A's file mtime explicitly; reopen; assert it was re-validated.
- **R3 — Theme change visual regression** in Phase 4. Mitigation: visual smoke test of every screen before merging Phase 4. Roll back the theme line if anything looks wrong; ship Phase 4b (scoped object_id) instead.
- **R4 — Test-suite assumes screen rebuilt every open.** If any test relies on `BuildQueueScreen.__init__` being called per click, it breaks under Phase 2. Mitigation: grep test suite for `BuildQueueScreen(` constructions; update assertions where they assume a fresh instance.
- **R5 — Memory growth from surviving screen.** After Phase 2, the screen instance never frees. Estimated ≤ 50 MB. Mitigation: measure after Phase 2 lands; if growth is large, add an explicit `purge_caches()` call on a "leave strategy screen" event.
