# PROJ-411: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Problem

Five strategy-layer panels — Galactic Planet Registry, Galactic Star Registry, Empire Overview, Build Queue (per yard), Event Log — take "remarkably long" to open even on turn 1 of a minimal 2-system / 1-planet-each game. Phase A/B investigation identified six independent contributors. Phase 1 lands fixes for all of them as a coherent set; Phase 2 addresses any remaining hotspots that surface in the Phase 1 Scalene profile; Phase 3 locks the wins in.

## Hot Path Inventory

### 1. Pygame_gui rounded-panel rasterization (biggest single shared cost)
All five target windows inherit from `StrategyModalWindow(UIWindow)` without setting `object_id="@fast_panel"`. They use the default rounded-rectangle panel shape, which `data/builder_theme.json:72-82` confirms is rendered with the expensive shape pipeline. `game/ui/screens/build_queue_panel_factory.py` already uses `@fast_panel` at 8 sites — reportedly ~3 s aggregate savings per Build Queue open. None of `planet_list_window.py`, `star_list_window.py`, `empire_panel_window.py`, `event_log_window.py`, `build_queue_screen.py` opt in today.

### 2. `DesignLibrary.scan_designs()` re-scans on every open
`game/strategy/systems/design_library.py:140-182` does glob + JSON parse for ~47 files. Called from 12 production sites (5 UI, 5 engine, 2 build setup). 1.2 s wall-clock per call in the QA log. No cache today. `DesignLibrary` is constructed fresh per click at `strategy_build_queue_manager.py:196`.

### 3. `gather_planets()` / `gather_stars()` walk full galaxy on every open
`game/ui/screens/planet_list_filters.py:33-63` and `game/ui/screens/star_list_filters.py:15-43`. Both walk `galaxy.systems.values() → s.planets/s.stars` and attach 6 `_cached_*` attributes per entity on every open. Galaxy state is per-turn-static.

### 4. Empire Overview synchronous asset I/O on open path
`game/ui/panels/empire_treasury_panel.py:322-344` (`load_resource_icons()` — pygame.image.load + convert_alpha + smoothscale per resource) called at `empire_panel_window.py:142` after the bypass guard. `game/ui/screens/empire_panel_window.py:333-349` (`_render_portrait_flag_row` — synchronous portrait/flag load) runs when Population tab is selected. Race assets have **zero caching** today.

### 5. `EmpireEconomyService.get_snapshot()` reruns on every Treasury tab switch
`game/ui/screens/empire_panel_window.py:254`. Not cached between tab toggles.

### 6. Event Log `list(events)` full copy on every open
`game/ui/screens/event_log_window.py:115` — `self.all_events = list(events)`. Source list is already per-turn-stable from `facade.get_all_events()`.

### Plus: Zero `profile_action()` instrumentation
None of the five panel classes wrap any code in `profile_action()` / `profile_block()` today. Phase 1 adds 12 spans at specific call sites identified by the Performance Analyst.

## Solution Approach

### Established patterns reused

| New work | Existing pattern | Reference file |
|---|---|---|
| Per-turn `DesignLibrary` cache | `FacadeSessionState` lazy-init + per-turn invalidate skeleton | `game/strategy/facade/slices/_facade_state.py:46-98` |
| Per-turn `gather_planets`/`gather_stars` cache | Same `FacadeSessionState` skeleton | `_facade_state.py:46-98` |
| Per-turn `EmpireEconomyService` snapshot cache | Same `FacadeSessionState` skeleton | `_facade_state.py:46-98` |
| Empire Overview lazy resource icons | Lazy-icon-on-render with `_icon_cache` dict | `game/ui/screens/planet_data_source.py:64-94` |
| Empire Overview lazy portrait/flag | Tab-deferred load via existing `_show_tab()` callback shape | `empire_panel_window.py:209-232` |
| `@fast_panel` opt-in | Existing theme entry + Build Queue factory precedent | `data/builder_theme.json:72-82`; `build_queue_panel_factory.py:214` |
| `profile_action()` spans | `@profile_action("Panel: ...")` decorator | `screen_router.py:22` |
| `profile_block()` for nested ranges | `with profile_block(...)` ctx mgr | `workshop_data_reloader.py:113` |
| DesignLibrary write-through invalidation | Explicit `.pop()` on write | `ship_instance.py::invalidate_stats_cache` style |

### Where new state lives

**`FacadeSessionState` gets four new fields** (per Architecture Analyst's recommendation; rejects naive Pattern #11 module-level reuse, which is for immutable assets):

```python
# game/strategy/facade/slices/_facade_state.py
class FacadeSessionState:
    def __init__(self, session: "GameSession") -> None:
        # existing fields...
        self.planet_index: Optional[dict] = None
        self.all_stars_cache: Optional[List["StarInfo"]] = None
        self.fleets_by_hex_cache: Optional[dict] = None
        # NEW (PROJ-411):
        self.designs_by_empire: dict[int, list["DesignMetadata"]] = {}
        self.planets_for_empire_cache: dict[int, list["Planet"]] = {}
        self.stars_cache_new: Optional[list] = None      # raw star list, distinct from all_stars_cache StarInfo DTO list
        self.empire_economy_snapshot: dict[int, "EmpireEconomySnapshot"] = {}

    def invalidate_all(self) -> None:
        # existing clears...
        # NEW (PROJ-411):
        self.designs_by_empire.clear()
        self.planets_for_empire_cache.clear()
        self.stars_cache_new = None
        self.empire_economy_snapshot.clear()
```

**Empire Overview lazy state:** instance attributes `_resource_icons_loaded: bool`, `_population_assets_loaded: bool`. Populated on first render of each tab; reused on subsequent renders.

### Save-write invalidation

`DesignLibrary.save_design()` at line 184+ writes JSON to disk. Phase 1 adds an explicit per-empire invalidation:

```python
def save_design(self, ship, design_name: str, ...) -> Tuple[bool, str]:
    # ... existing write logic ...
    save_json(filepath, design_data)
    # NEW (PROJ-411): drop cached metadata for this empire so next scan rebuilds
    if self._facade_state is not None:
        self._facade_state.designs_by_empire.pop(self.empire_id, None)
    return True, "Saved"
```

This requires threading `_facade_state` into `DesignLibrary`. Two options examined:

- **Option A (chosen):** `DesignLibrary` accepts optional `facade_state: FacadeSessionState | None` constructor parameter. UI-side callers pass it; engine-side callers don't (they don't need the cache since each engine call is per-turn anyway, and they're called inside the turn loop). Dependency Mapper confirmed `DesignLibrary` is constructed fresh per call at every site — passing one more kwarg has zero ripple at call sites that don't care.
- **Option B (rejected):** Inject a callback (`on_save_design: Callable[[int], None]`) and let callers decide. More flexible but adds a runtime indirection for a single use case.

### LOC budget compliance

Three files are already over the 500-LOC ceiling: `planet_list_window.py` (737), `empire_panel_window.py` (572), `build_queue_screen.py` (877). Phase 1 edits in those files are capped at **≤15 LOC each** per Architecture Analyst's guidance:

- `@fast_panel` opt-in: one keyword in `super().__init__(...)`. Within budget.
- `profile_action()` decorators on existing methods: one line per span.
- Cache-lookup logic: lives in collaborator files (`planet_list_filters.py`, `star_list_filters.py`, `empire_treasury_panel.py`, `empire_economy_service.py`, `event_log_data_source.py`, `_facade_state.py`) which have headroom.

## Cache Invalidation Map

| Cache | Created by | Invalidated by |
|---|---|---|
| `designs_by_empire[empire_id]` | First `scan_designs(empire_id)` per turn | `FacadeSessionState.invalidate_all()` (per turn); `DesignLibrary.save_design()` (write-through `.pop()`) |
| `planets_for_empire_cache[empire_id]` | First `gather_planets(galaxy, empire)` per turn per empire | `FacadeSessionState.invalidate_all()` per turn |
| `stars_cache_new` | First `gather_stars(galaxy)` per turn | `FacadeSessionState.invalidate_all()` per turn |
| `empire_economy_snapshot[empire_id]` | First `get_snapshot(empire)` per turn per empire | `FacadeSessionState.invalidate_all()` per turn |
| Empire Overview `_resource_icons` | First Treasury-tab render | Window `kill()` (per-window-instance) |
| Empire Overview portraits/flags | First Population-tab render | Window `kill()` (per-window-instance) |

**Load Game lifecycle:** `SaveGameService.load_game()` constructs a new `GameSession` → new `FacadeSessionState`. Caches start empty. No additional hook needed.

**Mods at startup:** Mod designs are loaded by `RegistryLoader` before any turn starts, so the first per-turn cache build sees them.

## Swarm Findings Summary

### Architecture
- All proposed imports legal under the layer model.
- DesignLibrary cache home: `FacadeSessionState`, not module-level singleton.
- 3 of 5 window files over 500-LOC ceiling — edits there capped at ≤15 LOC; heavier code goes in collaborators.

### Dependency Map
- `scan_designs()` has 12 production call sites — cache benefits all of them.
- `DesignLibrary.save_design()` requires explicit invalidation in the same method.
- `FacadeSessionState.invalidate_all()` is the established per-turn hook.
- Race assets currently uncached at any layer; portrait/flag is a load-on-every-render.

### Key Patterns to Reuse
- **`FacadeSessionState` skeleton** (`_facade_state.py:46-98`): lazy-init dict + `invalidate_all()` per turn.
- **Lazy-icon-on-render** (`planet_data_source.py:64-94`): cache key → cache lookup → load on miss → store → return.
- **`@profile_action("Panel: ...")` decorator** (`screen_router.py:22`): label format "Panel: <operation>".
- **`@fast_panel` opt-in** (`build_queue_panel_factory.py:214`): pass `object_id` in widget construction.
- **Explicit-pop invalidation on write** (`ship_instance.py::invalidate_stats_cache`): mirror in `save_design()`.

### Dependencies & Risks
1. **Issue #17 sequencing.** Land Issue #17 (Build Queue stale rows, `status:in-progress`) before PROJ-411 Phase 1 begins. Mitigation: explicit prerequisite in Current State; Phase 1 doesn't start until #17 merges.
2. **Empire Overview first-Population-click freeze.** Lazy load moves freeze, doesn't eliminate. Mitigation: Phase 2 evaluates an idle-time prefetch if Phase 1 profile shows the click exceeds 50 ms.
3. **Double-tab-click race.** Mitigation: idempotent `_population_assets_loaded` flag check at start of `_render_portrait_flag_row`.
4. **Wall-clock test variance.** Mitigation: count-based assertions are the regression gates; wall-clock benchmarks print measured value and fail only on >2× regression.
5. **Existing test compatibility.** 2 unit tests + 1 modify-between-scan test under `tests/unit/strategy/design_library/` will need updates as part of Phase 1.
6. **No rollback flag.** Decision: declined per CLAUDE.md Rule 3. Rollback by PR revert if needed.

### Anti-Patterns Identified (Avoid)
- Module-level singletons not reset across tests.
- Builders that re-construct widgets every refresh instead of updating data sources.
- Sync I/O on UI thread without justifying comment.
- Repeated `os.path.exists` / `pygame.image.load` in render loops.

### Opportunities Discovered
- `@fast_panel` rollout to all 5 panels — likely the single biggest open-time win available, applies in Phase 1.
- `EmpireEconomyService` cache — benefits not just open, but also every Treasury tab toggle.
- Per-turn `gather_*` caches — also useful for any non-Phase-1 features that re-walk galaxy.
- Extending `TestRowPoolReuseGuard` to Planet/Star/Event Log virtual tables (Phase 3) — improves test coverage of the PROJ-373 perf lock.

## Open Questions for Phase 2 (deferred — Scalene-evidence-driven)

To be answered by Phase 1's profiling output, not pre-decided:

1. Does `compute_planet_effect_keys()` (`planet_list_filters.py:133-146`) show up as a hotspot? If yes, can it be turn-cached too?
2. Is the Empire Overview first-Population-click freeze > 50 ms? If yes, design an idle prefetch.
3. Does `BuildQueueRowCollector.collect()` show up after the DesignLibrary cache lands? If yes, separate fix.
4. Does Event Log's `_recompute_filtered()` show up? If yes, incremental filter update.
5. Does `EmpireEconomyService.get_snapshot()` show meaningful cost on first build even after caching? If yes, micro-optimise the snapshot construction.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
