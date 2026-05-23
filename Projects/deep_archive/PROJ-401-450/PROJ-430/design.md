# PROJ-430: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.
>
> **Canonical source:** [TD-08_facade_api_reduction.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-08_facade_api_reduction.md). This file distills that plan; if the two diverge, the TD plan wins.

## Verification Evidence (already verified before scaffold)

The report originally cited "53 public methods, 28 `dispatch_*` helpers, cache-forwarding properties kept for legacy tests." Direct measurement against `strategy_session_facade.py` and the frozen public-API contract showed the problem is **larger** than reported:

| Metric | Report | Actual (2026-05-16) | Source of truth |
|---|---|---|---|
| Total public methods (incl. dispatch helpers) | 53 | **68** | `PUBLIC_METHODS` frozenset in `test_strategy_session_facade_public_api.py` |
| `dispatch_*` helpers | 28 | **36** | `rg "facade_helper_name\s*=\s*'dispatch_"` across `game/strategy/engine/`; matches the 36 dispatch entries in `PUBLIC_METHODS` |
| Non-dispatch public methods | 25 | **32** | 68 − 36 |
| Cache-forwarding properties (read+write) | "for legacy tests" | **6 distinct fields, 12 get+set property halves** | `strategy_session_facade.py:115-164` |
| Legacy aliases | (not enumerated) | **`_resolve_economy_config`** (`strategy_session_facade.py:372-374`, docstring "legacy alias") | Direct inspection |

The cache forwarders at `strategy_session_facade.py:114-164` are: `_planet_index`, `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn`, `_race_registry` — each kept as a get+set `@property` pair forwarding onto `FacadeSessionState`. The block comment at `strategy_session_facade.py:114-117` explicitly labels these "preserved for legacy tests." The same intent appears in `slices/_facade_state.py:44` ("when they assign `facade._planet_index = {...}`").

**Verdict:** the facade boundary is at least as wide as the report claimed (in fact wider, 68 vs 53; 36 vs 28). The cache forwarders are kept *solely* to satisfy three test files; production code does not depend on them. The boundary also incentivises further growth — the frozen contract was last expanded for PROJ-FMS-B/C/D and PROJ-382, each of which **added** a public method rather than collapsing onto a smaller stable shape.

### Tests that pin the cache forwarders (3 files)

1. **`tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`** — the frozen contract: `PROTECTED_ATTRS = {"_planet_index", "_fleets_by_hex_cache", "_all_stars_cache", "_race_registry"}` (lines 127-132). `TestProtectedSurface.test_protected_attrs_settable_on_instance` (lines 192-214) asserts each is settable on a fresh instance and round-trips — that's what locks the writable `@property` into place.
2. **`tests/unit/strategy/facade/test_colony_demographic_view.py`** — `_facade_for(...)` at lines 82-103 writes `facade._planet_index = {planet.id: planet}` and `facade._race_registry = race_registry` (lines 95, 98). A second test (line 125) sets `facade._planet_index = {}` to force a "missing planet" branch.
3. **`tests/unit/strategy/facade/test_facade_indices.py`** — line 46 asserts `hasattr(facade, '_planet_index')` after a `_get_planet_by_id` call, pinning the readable forwarder.

No production code under `game/` reaches into `facade._planet_index`, `facade._all_stars_cache`, `facade._fleets_by_hex_cache`, or `facade._race_registry`. The 25 UI files that touch `facade._<something>` consume the *callable* protected helpers (`_get_planet_by_id` etc.), not the cache fields.

## Goal / End State (target architecture)

```
StrategySessionFacade
├── handle_command(cmd)                       # the only write entry point (top-level callable)
├── process_turn(progress_callback=None)      # session lifecycle (top-level callable)
├── facade_state                              # already public — kept
├── commands       -> FacadeCommands          # grouped dispatch (36 helpers move here, dispatch_ prefix stripped)
├── fleets         -> FacadeFleetQueries      # 5 fleet read methods, fleet/fleets prefix stripped
├── systems        -> FacadeSystemQueries     # 6 star/system/storm read methods
├── planets        -> FacadePlanetQueries     # 2 planet read methods
├── empires        -> FacadeEmpireQueries     # 6 empire read methods
├── events         -> FacadeEventQueries      # 3 event read methods
├── session_meta   -> FacadeSessionInfo       # turn number, save path, human IDs
├── economy        -> FacadeEconomyQueries    # demographics + registries + race registry + resolve_config()
└── validation     -> FacadeValidation        # can_colonize, can_move_to
```

### Minimum API surface goals

- **Top-level callable methods:** 2 (`handle_command`, `process_turn`).
- **Top-level public attributes:** 10 (`facade_state` + 9 grouped accessors).
- **Total public callables reachable through the namespaces:** still ~50 — the goal is **shape, not count**: feature additions land inside the appropriate group, not on the top class.
- **Cache forwarders:** zero. The 6 underscore-prefixed fields stop being a writable boundary; tests use `FacadeSessionState.seed_*` helpers instead.
- **Legacy aliases:** zero. `_resolve_economy_config` is replaced by `economy.resolve_config()` (renamed, no underscore prefix) or deleted if no external callers remain after migration.

### Why grouped accessors instead of yet another flat shrink

The previous pass (PROJ-309 sub-phase 3.7) already did the *internal* split. The remaining problem is that the public boundary is still flat, so:
- Tests have nothing to assert on besides a hand-maintained list of 68 names.
- Each new strategy/UI feature adds one more top-level method because that's the established pattern.
- Grouping makes the *cost* of a new top-level entry visible: it has to be either a new group or a method on an existing group with a clear domain owner.

This matches the report's "payoff approach": *"group read/write surfaces by feature domain."*

## Architecture Analysis

### The new `grouped_namespaces.py` file

A single new file at `game/strategy/facade/grouped_namespaces.py` hosts 8 thin dataclasses that wrap existing slice instances. They are wrappers, not replacements — the slice is still the implementation; the namespace dataclass just:
1. Exposes only the intended public verbs (drops redundant prefixes, leaves out internal helpers).
2. Renames methods to their final form (`dispatch_issue_move` -> `issue_move`, `get_fleet` -> `get`, etc.).
3. Provides a stable surface the facade can re-export through a `@property` getter.

For `FacadeCommands`, the constructor takes the iterable of `(helper_name, command_cls)` pairs as a parameter rather than importing `command_registry` directly — this decouples the namespace from TD-03's potential reshape of `specs_by_facade_helper()`.

### Cache-forwarder removal path

The cache forwarders cannot be deleted before their test pin-points are migrated, because the contract test (`test_strategy_session_facade_public_api.py`) and the two consumer tests (`test_colony_demographic_view.py`, `test_facade_indices.py`) would go red and block the deletion. The phased ordering is therefore:

1. Phase 1: rewrite the contract test to assert the *target* shape. The legacy-cache assertion flips from "must be settable" to "must not be settable" — that assertion stays red until Phase 5's deletion lands.
2. Phase 4: add `FacadeSessionState.seed_planet_index(...)`, `seed_race_registry(...)` public helpers; rewrite the two consumer tests to call them. After Phase 4, no test reads or writes `facade._planet_index` / `facade._race_registry` etc.
3. Phase 5: delete the property forwarders. The Phase 1 assertion goes green.

The `seed_` prefix is intentional: it makes the test-only intent visible at the call site so the helper is not mistaken for production seeding. The alternative (passing the registry through the slice/economy constructor as DI) is preferred where it can be done without refactor sprawl — to be assessed in Phase 4 task-by-task.

### Hard rule (architectural invariant)

After TD-08:
- New facade methods land on a group namespace, not on `StrategySessionFacade` directly.
- The two top-level callables `handle_command` and `process_turn` are the only behavioral entry points that survive at the top level.
- Cache state on `FacadeSessionState` is private to the slices; tests use the `seed_*` public seam.

## Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| UI mechanical rewrite misses a call site, causing a runtime `AttributeError` on a rarely-visited screen | Medium | `rg` across `game/ui` is exhaustive; the auto-installer enumerates dispatch helpers via the registry, so the rename list is generable rather than typed. UI shard before merging. Phase ordering (UI rewrite in Phase 3, legacy deletion in Phase 5) guarantees deterministic test failure not latent runtime bug. |
| `test_colony_demographic_view.py` was written against an implementation detail; rewriting seeding may quietly relax coverage | Low | The behavioral assertions (what `get_colony_demographic_view` returns) stay intact; only the *seeding mechanism* changes. Diff the test before/after to confirm no `assert` lines were dropped. |
| A third-party test or external script depends on `facade.dispatch_*` (e.g. AI playtest harnesses, replay tools) | Low | `rg` across the repo before Phase 5; if found, migrate the same way as UI callers. No external SDK published. |
| Grouped accessors create unexpected import cycles via slice re-exports | Low | Slices already exist with stable imports; the new `Facade*Queries` namespaces are thin dataclasses with no new modules outside `game/strategy/facade/`. |
| Renaming `dispatch_X` to `commands.X` (stripping prefix) collides with an existing top-level method on the dispatch slice | Low | Mechanical check via `rg "def issue_\|def queue_\|def split_\|def delete_\|def reorder_\|def add_to_\|def remove_from_\|def clear_\|def set_atmosphere"` on the slice — none collide today. |
| Hidden test depends on `facade._all_stars_cache_turn` (the only forwarder without a paired contract assertion) | Low | Already searched — zero matches in `tests/` for that name. |
| TD-02 lands between Phase 1 and Phase 5, changing what `economy_config` looks like during rehydration | Medium | Soft-dependency on PROJ-423 (TD-02) — recommended order is TD-02 first. If TD-08 ships first, keep the warning-log fallback inside `FacadeEconomyQueries.resolve_config()` as documented carried debt until TD-02 lands; delete then. |
| TD-03 reshapes `command_registry.specs_by_facade_helper()` | Medium | `FacadeCommands` takes the iterable of `(helper_name, command_cls)` pairs as a constructor parameter, so the registry shape can be swapped without touching the namespace. |

The dominant risk is the **UI regression surface**. Mitigated by phase ordering: UI rewrite is Phase 3 (callers updated before the legacy surface is deleted in Phase 5), so a missed callsite produces a deterministic test failure rather than a latent runtime bug.

## Cross-Plan Coupling (per EXECUTION_ORDER.md)

- **Soft preference: TD-02 -> TD-08 (PROJ-423 -> PROJ-430).** TD-02's shared bootstrap/rehydration path is what lets the `_resolve_economy_config` warning-log fallback (`economy_slice.py:75`) genuinely disappear during Phase 5. If TD-08 ships first, the fallback survives inside `FacadeEconomyQueries.resolve_config()` as documented carried debt.
- **Soft preference: TD-03 -> TD-08.** TD-03 (command/order metadata in multiple truth surfaces) reshapes the registry's spec API. `FacadeCommands` is structured to consume an iterable, not the registry directly, to make this swap safe.
- **No hard prerequisites.** Other owned TDs (TD-04, TD-06, TD-07, TD-09, TD-10) are independent.
- **Out of scope for TD-08 (deliberate):** internal slice refactors (`fleet_slice.py` etc.), DTO renames (`FleetInfo`, `PlanetInfo`), compat shims or deprecation warnings, save-file migrations, new top-level facade methods.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
