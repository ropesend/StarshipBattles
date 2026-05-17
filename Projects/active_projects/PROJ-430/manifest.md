# PROJ-430 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.
>
> Derived from [TD-08_facade_api_reduction.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-08_facade_api_reduction.md) §"Concrete File Touch Plan".

## Files

### Production — added

| File | Type | Notes |
|------|------|-------|
| `game/strategy/facade/grouped_namespaces.py` | Production (new) | New file hosting 8 thin dataclasses: `FacadeCommands`, `FacadeFleetQueries`, `FacadePlanetQueries`, `FacadeSystemQueries`, `FacadeEmpireQueries`, `FacadeEventQueries`, `FacadeEconomyQueries`, `FacadeValidation`, `FacadeSessionInfo`. Each wraps an existing slice and exposes the renamed verbs (strips `dispatch_`, `get_`, and the redundant fleet/fleets prefix). `FacadeCommands` takes `(helper_name, command_cls)` iterable as a constructor parameter so it is decoupled from TD-03 registry reshape. |

### Production — modified

| File | Type | Notes |
|------|------|-------|
| `game/strategy/facade/strategy_session_facade.py` | Production (rewrite — shrinks substantially) | Phase 2: add 8 `@property` accessors returning the new namespace dataclasses. Phase 5: delete the 8 cache-forwarder property blocks (lines 114-164), the 32 flat read-method forwarders, the auto-installer's `dispatch_*` setattr loop (lines 448-477), and `_resolve_economy_config` (lines 372-374). Keep `handle_command(...)`, `process_turn(...)`, `facade_state` at the top level. End state: 2 top-level callables + 10 public attributes (`facade_state` + 9 grouped accessors). |
| `game/strategy/facade/slices/_facade_state.py` | Production | Phase 4: add `seed_planet_index(...)`, `seed_race_registry(...)`, and any other `seed_*` helpers needed to migrate the 3 cache-forwarder-dependent test files. Public seam — the `seed_` prefix makes test-only intent explicit. |
| `game/strategy/facade/slices/economy_slice.py` | Production | Phase 2/5: `FacadeEconomyQueries.resolve_config()` (new public method, no underscore) absorbs the call site. The warning-log fallback at line 75 survives here as documented carried debt **only if** TD-02 has not landed; otherwise it disappears in Phase 5. |
| `game/strategy/facade/slices/command_dispatch_slice.py` | Production | Phase 5: only if the flat helper installer logic is still embedded here, remove it. The slice's underlying dispatch methods are unchanged — only the exposure surface (via `FacadeCommands`) changes. |

### Production — NOT touched (verified)

| File | Type | Notes |
|------|------|-------|
| `game/strategy/engine/commands/registry.py` | Production | `specs_by_facade_helper()` is **read** by `FacadeCommands` (passed as constructor parameter) — not modified. If TD-03 reshapes this API, only the iterable source changes, not `FacadeCommands` itself. |
| `game/strategy/facade/slices/{fleet,planet,system,empire,event}_slice.py` | Production | Already organised by feature domain. Their internal methods are wrapped by the new namespace dataclasses; no slice-internal behavior changes. |

### Test — added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` | Test (new) | Phase 1 (red), green after Phase 2. Behavior parity: `facade.fleets.get(123)` returns the same `FleetInfo` that `facade.get_fleet(123)` did. One small test per group accessor; uses existing fixtures. |

### Test — modified

| File | Type | Notes |
|------|------|-------|
| `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | Test (rewrite) | Phase 1: replace `PUBLIC_METHODS` (68 entries) with `PUBLIC_TOP_LEVEL = {"handle_command", "process_turn"}` and `PUBLIC_GROUP_ACCESSORS = {"facade_state", "commands", "fleets", "systems", "planets", "empires", "events", "session_meta", "economy", "validation"}`. Add `test_no_legacy_flat_methods`, `test_grouped_namespaces_expose_expected_methods` (driven by `GROUP_CONTRACT` dict), `test_legacy_cache_attrs_removed`. Drop `PROTECTED_ATTRS`. All four new assertions must be **red** against current `main` (Phase 1 TDD anchor). Green after Phase 5. |
| `tests/unit/strategy/facade/test_colony_demographic_view.py` | Test | Phase 4: rewrite `_facade_for(...)` (lines 82-103) to call `facade.facade_state.seed_planet_index({...})` and `facade.facade_state.seed_race_registry(...)` instead of writing `facade._planet_index` / `facade._race_registry` directly. Rewrite line 125's `facade._planet_index = {}` similarly. Constructor DI through the economy slice is preferred where feasible; assess in Phase 4. **Behavioral assertions on `get_colony_demographic_view` return value stay intact** — diff before/after must show no `assert` lines dropped. |
| `tests/unit/strategy/facade/test_facade_indices.py` | Test | Phase 4: rewrite line 46's `assert hasattr(facade, '_planet_index')` to a behavioral assertion: `assert facade.planets.get(42) is facade.planets.get(42)` (cached identity). The test now pins behavior (caching contract), not implementation (the index field name). |
| `tests/unit/strategy/facade/test_strategy_session_facade.py` | Test | Phase 4 survey only — scan for incidental use of legacy aliases (`facade._resolve_economy_config(...)`, top-level `dispatch_*` calls, top-level `get_*` calls). Migrate each occurrence to the grouped surface. |

### Production — UI callers (Phase 3 mechanical rename, 25 files)

The full list is generated freshly in Phase 3 via:

```
rg -n "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui
```

Per the TD-08 plan, the verification step counted **25** files. The Phase 3 checklist re-runs the grep before editing — do not trust the count from a stale list. All 25 files receive purely mechanical renames:

| Pattern | Old form | New form |
|---|---|---|
| Dispatch helpers | `facade.dispatch_issue_move(...)` | `facade.commands.issue_move(...)` |
| Fleet getters | `facade.get_fleet(id)` | `facade.fleets.get(id)` |
| Fleet getters | `facade.get_fleets_at_hex(...)` | `facade.fleets.at_hex(...)` |
| Fleet getters | `facade.get_fleet_path_preview(...)` | `facade.fleets.path_preview(...)` |
| Fleet getters | `facade.get_fleet_path_projection(...)` | `facade.fleets.path_projection(...)` |
| Fleet getters | `facade.get_fleet_remaining_pods(...)` | `facade.fleets.remaining_pods(...)` |
| Planet getters | `facade.get_planet(id)` | `facade.planets.get(id)` |
| System/star getters | `facade.get_star(...)` etc. | `facade.systems.<verb>(...)` |
| Empire getters | `facade.get_empire(id)` etc. | `facade.empires.<verb>(...)` |
| Event getters | `facade.get_event(...)` etc. | `facade.events.<verb>(...)` |
| Session info | `facade.get_turn_number()` | `facade.session_meta.turn_number` (or `.turn_number()` — decide in Phase 2 design) |
| Session info | `facade.get_save_path()` | `facade.session_meta.save_path` |
| Session info | `facade.get_human_player_ids()` | `facade.session_meta.human_player_ids` |
| Economy | `facade.get_race_registry()` | `facade.economy.race_registry` |
| Economy | `facade.get_colony_demographic_view(...)` | `facade.economy.colony_demographic_view(...)` |
| Validation | `facade.can_colonize(...)` | `facade.validation.can_colonize(...)` |
| Validation | `facade.can_move_to(...)` | `facade.validation.can_move_to(...)` |

One commit per UI screen group; `pytest tests/unit/ui tests/integration -x` after each.

### Docs — modified (Phase 6)

| File | Type | Notes |
|------|------|-------|
| `docs/systems/strategy_layer.md` | Docs | Update the "facade boundary" section: describe the grouped surface (10 attrs), the `seed_*` test-seeding contract on `FacadeSessionState`, and the architectural invariant that new methods land inside a group. |
| `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md` | Docs (append) | Append a new section recording the post-TD-08 target surface as the source of truth for future facade work. Do **not** overwrite the historical content — append only. |
| `docs/03_CONVENTIONS.md` | Docs (conditional) | Add a single bullet only if a "use small grouped facades" convention is now stronger than what the doc currently captures. Skip if existing language covers it. |

(`docs/_ignore/` is the user's scratch space — leave it alone per AGENTS.md.)

## Estimated touch totals

- Production added: **1** file (`grouped_namespaces.py`).
- Production modified: **4** files (`strategy_session_facade.py`, `_facade_state.py`, `economy_slice.py`, possibly `command_dispatch_slice.py`).
- UI callers renamed: **25** files (Phase 3).
- Tests added: **1** file (`test_facade_grouped_namespaces.py`).
- Tests modified: **4** files (`test_strategy_session_facade_public_api.py` rewrite, `test_colony_demographic_view.py`, `test_facade_indices.py`, `test_strategy_session_facade.py` survey).
- Docs: **2** files updated, **1** conditional bullet.

Roughly **37** files in total. The bulk (25) is mechanical UI rename in Phase 3.
