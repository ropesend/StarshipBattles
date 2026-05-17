# Decomposition Design: strategy_session_facade.py

**Current size:** 928 lines (one class, `StrategySessionFacade`)
**Target post-split:** every resulting module <500 lines
**Pattern:** Facade-Slice composition (extends the existing Facade/Delegate pattern documented in `docs/02_PATTERNS.md` §5).

---

## Current responsibilities

Every public method on `StrategySessionFacade`, grouped by domain, with line ranges and a one-line description.

### A. Construction / lifecycle (lines 53–98)
| Member | Lines | Notes |
|---|---|---|
| `__init__(session)` | 53–67 | Stores `_session`, initialises 5 cache fields (`_planet_index`, `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn`, `_race_registry`). |
| `handle_command(command)` | 73–85 | Universal write entry point. |
| `process_turn()` | 87–98 | Advances the session and **invalidates all three facade-level caches**. |

### B. Command-dispatch helpers (lines 99–253) — 28 methods, all 1-import + 1-call wrappers
All are of the form `dispatch_xxx(**kwargs)` → import `XxxCommand` → `self.handle_command(XxxCommand(**kwargs))`. Logical sub-groups:

| Sub-group | Methods | Lines |
|---|---|---|
| Fleet orders | `dispatch_issue_colonize`, `dispatch_issue_move`, `dispatch_issue_intercept`, `dispatch_issue_join_fleet`, `dispatch_clear_orders`, `dispatch_issue_transfer`, `dispatch_issue_warp`, `dispatch_split_fleet`, `dispatch_delete_order`, `dispatch_reorder_order`, `dispatch_issue_self_destruct` | 100–133, 160–163, 190–193, 205–218 |
| Mission queueing | `dispatch_queue_colonize_mission`, `dispatch_queue_implode_planet_mission`, `dispatch_queue_stellerate_star_mission`, `dispatch_queue_open_warp_point_mission`, `dispatch_queue_close_warp_point_mission`, `dispatch_queue_create_dyson_sphere_mission` | 120–123, 165–188 |
| Superweapons (immediate) | `dispatch_issue_implode_planet`, `dispatch_issue_stellerate_star`, `dispatch_issue_open_warp_point`, `dispatch_issue_close_warp_point`, `dispatch_issue_create_dyson_sphere` | 135–158 |
| Build / construction | `dispatch_issue_build_order`, `dispatch_remove_build_order`, `dispatch_add_to_construction_queue`, `dispatch_remove_from_construction_queue`, `dispatch_reorder_construction_queue` | 195–203, 220–233 |
| Planet orders | `dispatch_issue_planet_order`, `dispatch_clear_planet_orders`, `dispatch_delete_planet_order`, `dispatch_set_atmosphere_target` | 235–253 |

### C. Fleet queries (lines 261–367)
| Method | Lines |
|---|---|
| `_get_fleet_by_id(fleet_id)` | 261–272 |
| `get_fleet(fleet_id)` | 288–300 |
| `_build_fleet_hex_index()` | 302–311 |
| `get_fleets_at_hex(hex_coord)` | 313–330 |
| `get_fleet_path_preview(fleet_id, target_hex)` | 332–350 |
| `get_fleet_path_projection(fleet_id, max_turns)` | 352–367 |
| `get_fleet_remaining_pods(fleet_id)` | 877–898 |

### D. System / star queries (lines 371–475)
| Method | Lines |
|---|---|
| `get_all_systems()` | 371–380 |
| `get_all_stars()` | 382–409 |
| `get_system_at_hex(hex_coord)` | 411–423 |
| `get_system_containing_fleet(fleet_id)` | 425–441 |
| `get_system_near_hex(hex_coord, max_dist)` | 443–475 |
| `get_storm_names_at_hex(hex_coord)` | 912–928 |

### E. Planet queries (lines 479–545)
| Method | Lines |
|---|---|
| `_build_planet_index()` | 479–485 |
| `_get_planet_by_id(planet_id)` | 487–498 |
| `get_planet(planet_id)` | 500–512 |
| `get_planets_at_hex(hex_coord)` | 514–545 |

### F. Empire queries (lines 549–633)
| Method | Lines |
|---|---|
| `_get_empire_by_id(empire_id)` | 274–286 |
| `get_all_empires()` | 549–558 |
| `get_empire(empire_id)` | 560–572 |
| `get_empire_colonies(empire_id)` | 574–586 |
| `get_empire_fleets(empire_id)` | 588–600 |
| `get_empire_build_queues(empire_id)` | 602–616 |
| `get_hex_build_queues(empire_id, hex_coord)` | 618–633 |

### G. Game-state / session queries (lines 637–651, 902–908)
| Method | Lines |
|---|---|
| `get_human_player_ids()` | 637–643 |
| `get_turn_number()` | 645–651 |
| `get_save_path()` | 902–908 |

### H. Colony demographics + economy (lines 655–763)
| Method | Lines |
|---|---|
| `get_colony_demographic_view(planet_id)` | 655–744 (largest single method, ~90 LOC) |
| `_resolve_economy_config()` | 746–763 |

### I. Race registry (lines 767–785)
| Method | Lines |
|---|---|
| `get_race_registry()` | 767–785 |

### J. Event log queries (lines 789–821)
| Method | Lines |
|---|---|
| `get_turn_events(turn=None)` | 789–801 |
| `get_all_events()` | 803–809 |
| `get_events_by_category(category)` | 811–821 |

### K. Validation queries (lines 825–873)
| Method | Lines |
|---|---|
| `can_colonize(fleet_id, planet_id)` | 825–851 |
| `can_move_to(fleet_id, target_hex)` | 853–873 |

---

## Proposed sub-modules

The composer keeps the public name `StrategySessionFacade` and re-exports unchanged. Slices live in `game/strategy/facade/slices/` to keep the existing flat `facade/` layout (where `dto/` already lives) tidy.

| Path | Responsibility | Methods | Est. LOC |
|---|---|---|---|
| `game/strategy/facade/strategy_session_facade.py` | Public composer. `__init__` constructs slices, holds session ref, wires `process_turn` cache-invalidation hooks. All public methods are 1-line forwarders. | All 50+ public methods (forwarders) + `__init__`, `handle_command`, `process_turn` | ~280 |
| `game/strategy/facade/slices/_facade_state.py` | Shared mutable state (caches + session ref) injected into every slice. Holds `_planet_index`, `_all_stars_cache(_turn)`, `_fleets_by_hex_cache(_turn)`, `_race_registry` plus `invalidate_all()`. | `FacadeSessionState` dataclass + invalidation helpers | ~70 |
| `game/strategy/facade/slices/command_dispatch_slice.py` | All 28 `dispatch_*` helpers + `handle_command`. Pure write path. | Section B above + `handle_command` | ~190 |
| `game/strategy/facade/slices/fleet_slice.py` | Fleet reads + fleet-domain validation queries. | `_get_fleet_by_id`, `get_fleet`, `_build_fleet_hex_index`, `get_fleets_at_hex`, `get_fleet_path_preview`, `get_fleet_path_projection`, `get_fleet_remaining_pods`, `can_move_to` | ~180 |
| `game/strategy/facade/slices/planet_slice.py` | Planet reads + planet-domain validation. | `_build_planet_index`, `_get_planet_by_id`, `get_planet`, `get_planets_at_hex`, `can_colonize` | ~120 |
| `game/strategy/facade/slices/system_slice.py` | System / star / storm / map reads. | `get_all_systems`, `get_all_stars`, `get_system_at_hex`, `get_system_containing_fleet`, `get_system_near_hex`, `get_storm_names_at_hex` | ~140 |
| `game/strategy/facade/slices/empire_slice.py` | Empire-scoped reads + build-queue collectors. | `_get_empire_by_id`, `get_all_empires`, `get_empire`, `get_empire_colonies`, `get_empire_fleets`, `get_empire_build_queues`, `get_hex_build_queues` | ~130 |
| `game/strategy/facade/slices/economy_slice.py` | Demographics, economy, race registry. | `get_colony_demographic_view`, `_resolve_economy_config`, `get_race_registry` | ~190 |
| `game/strategy/facade/slices/event_slice.py` | Event-log reads + plain session-state reads. | `get_turn_events`, `get_all_events`, `get_events_by_category`, `get_human_player_ids`, `get_turn_number`, `get_save_path` | ~90 |

Total composed surface: ~1,390 LOC across 9 files; every file <500 LOC; the composer itself sits comfortably under 300.

### Slice base class (recommended)

```python
# slices/_slice_base.py
class FacadeSlice:
    """Base for every slice. Holds the shared session+cache state."""
    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    @property
    def _session(self) -> "GameSession":
        return self._state.session
```

Each concrete slice subclasses `FacadeSlice` and accesses caches via `self._state.planet_index`, etc. This avoids passing 6 constructor args to every slice.

---

## Public API surface

Every method below MUST remain a public method on `StrategySessionFacade` after the split (callers continue to write `facade.method(...)`):

**Commands:** `handle_command`, `process_turn`, plus all 28 `dispatch_*` helpers (full list in section B above).

**Fleet queries:** `get_fleet`, `get_fleets_at_hex`, `get_fleet_path_preview`, `get_fleet_path_projection`, `get_fleet_remaining_pods`.

**System/star/map queries:** `get_all_systems`, `get_all_stars`, `get_system_at_hex`, `get_system_containing_fleet`, `get_system_near_hex`, `get_storm_names_at_hex`.

**Planet queries:** `get_planet`, `get_planets_at_hex`.

**Empire queries:** `get_all_empires`, `get_empire`, `get_empire_colonies`, `get_empire_fleets`, `get_empire_build_queues`, `get_hex_build_queues`.

**Game state:** `get_human_player_ids`, `get_turn_number`, `get_save_path`.

**Demographics / economy / races:** `get_colony_demographic_view`, `get_race_registry`.

**Events:** `get_turn_events`, `get_all_events`, `get_events_by_category`.

**Validation:** `can_colonize`, `can_move_to`.

**Internal helpers consumed by tests** (visible in `test_facade_indices.py`): `_get_fleet_by_id`, `_get_planet_by_id`, `_get_empire_by_id`, `_build_fleet_hex_index`, `_build_planet_index`, `_planet_index`, `_fleets_by_hex_cache`, `_all_stars_cache`. The composer must continue exposing these via property/forwarder so the existing private-name tests keep passing without rewriting.

Total: 53 public methods + ~8 protected attrs/methods asserted by tests.

---

## Caller-update strategy

**Choice:** **Option A — re-export shim / pure composer.**

**Justification:**
- 30 production/test `.py` files import `StrategySessionFacade` directly (149 mentions across all files counting docs/findings/archives, but Python-source imports cap at 30).
- Every UI screen in `game/ui/screens/` and the AI loop assume `facade.method(...)` calling style; the facade is documented in `docs/02_PATTERNS.md` §5 as **the** Facade pattern exemplar — its public surface is a load-bearing contract.
- Slices are an internal implementation detail. Callers MUST NOT learn that `_fleet_slice` / `_planet_slice` exist; that would defeat the facade.
- Tests asserting on private attributes (`_planet_index`, `_fleets_by_hex_cache`, `_all_stars_cache`) — see `tests/unit/strategy/facade/test_facade_indices.py` — must keep working unchanged. The composer exposes these via `@property` forwarders to `FacadeSessionState` fields.

**Migration:** zero call-site edits. Only the implementation directory changes.

---

## Test plan

### Existing tests likely affected (paths)

Direct facade tests:
- `tests/unit/strategy/facade/test_strategy_session_facade.py`
- `tests/unit/strategy/facade/test_facade_dispatch.py`
- `tests/unit/strategy/facade/test_facade_indices.py` (asserts on `_planet_index`, `_fleets_by_hex_cache`, `_all_stars_cache` — composer must preserve these as properties)
- `tests/unit/strategy/facade/test_facade_system_proximity.py`
- `tests/unit/strategy/facade/test_facade_robust_resolution.py`
- `tests/unit/strategy/facade/test_event_queries.py`
- `tests/unit/strategy/facade/test_star_info_dto.py`
- `tests/unit/strategy/facade/test_colony_demographic_view.py`
- `tests/integration/strategy/facade/test_facade_integration.py`
- `tests/integration/strategy/facade/test_facade_init.py`
- `tests/integration/strategy/facade/test_fleet_queries.py`
- `tests/integration/strategy/facade/test_system_queries.py`
- `tests/integration/strategy/facade/test_empire_queries.py`
- `tests/integration/strategy/facade/test_validation_queries.py`
- `tests/integration/colonization/test_planet_specific_colonization.py`
- `tests/integration/ui/test_colonization_facade.py`
- `tests/integration/ui/test_fleet_ops_facade.py`
- `tests/integration/strategy/test_event_log_integration.py`
- `tests/repro_facade_colonies.py`
- `tests/unit/ui/screens/test_event_log_window.py`

All MUST continue passing without modification — that is the principal acceptance gate for the split.

### New per-slice targeted tests

Add `tests/unit/strategy/facade/slices/`:
- `test_command_dispatch_slice.py` — verify each `dispatch_*` constructs the right command with kwargs forwarded verbatim.
- `test_fleet_slice.py` — exercise the slice in isolation against a mock `FacadeSessionState`.
- `test_planet_slice.py` — same.
- `test_system_slice.py` — same.
- `test_empire_slice.py` — same.
- `test_economy_slice.py` — covers `get_colony_demographic_view` (currently the heaviest method) plus `_resolve_economy_config` warning path.
- `test_event_slice.py` — events + plain state reads.

### Composition contract test (new)

`tests/unit/strategy/facade/test_facade_composition.py`:
1. Snapshot the full public method list of `StrategySessionFacade`. Compare against a frozen golden list (the 53 methods + asserted private attrs). Fails if anything is removed or renamed.
2. Assert every documented public method on `StrategySessionFacade` has a corresponding implementation on exactly one slice (no duplication, no orphan).
3. Cache-invalidation contract: call `process_turn()`, assert `_planet_index is None`, `_fleets_by_hex_cache is None`, `_all_stars_cache is None`.

### Workflow

1. Write `test_facade_composition.py` first (RED — class doesn't have slices yet).
2. Extract `_facade_state.py` + `FacadeSlice` base.
3. Extract slices one by one, each with its targeted test file written first. Use TDD: write the slice's test file → run → see it fail → wire the slice → see green.
4. Replace each section of the composer with forwarders one slice at a time.
5. After every extraction: run the full existing `tests/unit/strategy/facade/` + `tests/integration/strategy/facade/` suites. **Zero regressions** allowed.
6. Final: full sharded suite (`python Tools/test_sharded/test_sharded.py`).

---

## Risks

### 1. Slice-to-slice coupling (real, several known cases)
- `can_colonize` (validation) needs both fleet AND planet lookup → today it directly calls `_get_fleet_by_id` + `_get_planet_by_id`. Likewise `can_move_to` needs fleet + session.preview path.
- `get_system_containing_fleet` → needs fleet (FleetSlice) AND system (SystemSlice).
- `get_colony_demographic_view` → needs planet (PlanetSlice) AND race registry (EconomySlice owns it but reaches across).

**Mitigation:** all slices share `FacadeSessionState`. Cross-slice queries call back through the composer's public method (the composer holds slice references, slices hold only `_state`). I.e. `EconomySlice.get_colony_demographic_view` would receive `planet_lookup: Callable[[int], Planet | None]` injected at slice construction — the composer passes its own `_planet_slice._get_planet_by_id` in. This avoids slice-to-slice direct refs while keeping the dependency graph explicit.

Alternative considered: put all `_get_*_by_id` helpers on `FacadeSessionState` itself (since they only need `_session`). This is cleaner for the `_get_X_by_id` family because they don't need any slice state — they just walk session collections. **Recommendation:** put `_get_fleet_by_id`, `_get_planet_by_id` (and its `_planet_index` cache), `_get_empire_by_id` on `FacadeSessionState`. Slices then never reach across. This also matches what tests in `test_facade_indices.py` already assume (the cache fields live "on the facade").

### 2. Delegation overhead
- 53 forwarder methods is a lot of boilerplate. Each is one line of the form `return self._fleet_slice.get_fleet(fleet_id)`. Acceptable but noisy.
- Consider `__getattr__` auto-forwarding: rejected — opaque, breaks IDE autocomplete and type hints, and the existing tests grep for explicit method definitions. Stick with explicit forwarders.
- The 28 `dispatch_*` helpers are themselves thin wrappers. There is a plausible argument for **deleting** them entirely (callers could just do `facade.handle_command(IssueMoveCommand(**kwargs))` directly) but that is **out of scope for PROJ-309** — this is a decomposition project, not an API redesign. Keep them as forwarders to `command_dispatch_slice`.

### 3. Initialization order
- Slices are stateless given a `FacadeSessionState`, so order is irrelevant. Construct `state` first, then construct each slice with `state` injected. Race registry lazy-init lives on `state` (or on the economy slice), not on the composer.

### 4. Tests asserting on private cache attrs
- `test_facade_indices.py` reads `facade._planet_index` directly. The composer must expose these as properties forwarding to `FacadeSessionState`. Mitigated by adding properties; flagged here so the implementer doesn't miss it.

### 5. The `PlanetEconomyProjector` import inside `get_colony_demographic_view`
- Method is 90 LOC and the largest in the file. After moving to `economy_slice.py` it remains 90 LOC; consider extracting `_build_species_views(planet, ...)` and `_aggregate_total_upkeep(planet, ...)` private helpers within the slice. Optional; not strictly required by the LOC target.

---

## Open questions (for cross-review)

1. **Slice dir vs flat `facade/`?** Proposal: `game/strategy/facade/slices/<name>_slice.py`. Alternative: keep flat (`game/strategy/facade/<name>_slice.py`). Vote: subdir is tidier since `facade/dto/` already establishes the "subdir per concern" precedent.

2. **Should `_get_fleet_by_id`, `_get_planet_by_id`, `_get_empire_by_id` move to `FacadeSessionState` or stay on slices?** Proposal: move to `FacadeSessionState` because (a) they're cache-owning, (b) several slices need them, (c) it eliminates slice-to-slice coupling. Risk: `FacadeSessionState` becomes a quasi-base class rather than a pure data holder.

3. **Should the 28 `dispatch_*` helpers be deleted as out-of-scope cleanup?** Proposal: NO — keep them, just move them. Deletion is API churn that belongs in a separate ticket.

4. **Cache invalidation across slices.** Today `process_turn()` clears 3 cache fields. After the split, does `process_turn` live on the composer (and call `state.invalidate_all()`), or on a slice? Proposal: stays on the composer (it's lifecycle, not per-domain), and calls `self._state.invalidate_all()`.

5. **Type hints / `IRaceRegistry` quoting.** The current file uses quoted forward refs and `TYPE_CHECKING`. Slices should follow the same convention; PROJ-311 requires return-type annotations on every new function — confirm the implementer adds them as the slices are extracted.

6. **Docstring for `StrategySessionFacade` after split.** Update class docstring to mention the composition pattern and link to each slice. Update `docs/02_PATTERNS.md` §5 to add a sub-paragraph on Facade-Slice composition. Update `docs/systems/strategy_layer.md` §1 with the new internal layout (Rule 2: docs in same commit).

---

## TD-08 (PROJ-430) target surface (2026-05-17)

PROJ-309 split `StrategySessionFacade` internally into seven slices but kept the *public boundary* flat (68 top-level methods + 8 cache-forwarder property pairs + 1 legacy alias). PROJ-430 / TD-08 collapses the boundary to its target shape:

- **2 top-level callables:** `handle_command(cmd)`, `process_turn(progress_callback=None)`.
- **10 public attributes:** `facade_state` plus 9 grouped namespace accessors (`commands`, `fleets`, `planets`, `systems`, `empires`, `events`, `session_meta`, `economy`, `validation`).

The 36 `dispatch_*` helpers now live under `facade.commands.<verb>` (prefix stripped, registry-driven). The 30 flat read methods (`get_fleet`, `get_planets_at_hex`, `get_turn_number`, `get_race_registry`, etc.) live under the appropriate grouped namespace with their final names (`facade.fleets.get`, `facade.planets.at_hex`, `facade.session_meta.turn_number`, `facade.economy.race_registry`, etc.). The cache-forwarder property pairs (`_planet_index`, `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn`, `_race_registry`) and the `_resolve_economy_config` legacy alias are root-cause deleted; tests that need to inject cache state use the public `FacadeSessionState.seed_*` helpers added in Phase 4.

Sources of truth going forward:
- Active project: [PROJ-430](../../../../active_projects/PROJ-430/plan.md) (project scaffold and per-phase checklists).
- TD-08 source plan: `Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified Problem Remediation Plans/TD-08_facade_api_reduction.md`.
- Doc surface: `docs/systems/strategy_layer.md` §1.

**Architectural invariant set in TD-08:** new facade methods land on a grouped namespace, not on `StrategySessionFacade` directly. The two top-level callables `handle_command` and `process_turn` are the only behavioral entry points that survive at the top level. New domains earn a new grouped namespace; new verbs in an existing domain land on its namespace. This is the source of truth for any future PROJ-309-style facade work — extending the facade is a grouped-namespace decision, not a flat-method decision.
