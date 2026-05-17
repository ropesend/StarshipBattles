# TD-08: Reduce the StrategySessionFacade public boundary

**Status:** VERIFIED — the actual surface is wider than the report claims, and the cache-forwarder pin-points are confirmed in tests.

## Verification Findings

The TD-08 entry in `report.md` cited "53 public methods, 28 `dispatch_*` helpers, cache-forwarding properties kept for legacy tests." Direct measurement against `game/strategy/facade/strategy_session_facade.py` and the frozen public-API contract in `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` shows the problem is **larger** than reported:

| Metric | Report | Actual (2026-05-16) | Source of truth |
|--------|--------|---------------------|------------------|
| Total public methods (incl. dispatch helpers) | 53 | **68** | `PUBLIC_METHODS` frozenset, public-api contract test |
| `dispatch_*` helpers | 28 | **36** | `rg "facade_helper_name\s*=\s*'dispatch_"` across `game/strategy/engine/`; matches the frozen `PUBLIC_METHODS` dispatch entries (36) |
| Non-dispatch public methods | 25 | **32** | 68 - 36 |
| Cache-forwarding properties (read+write) | "for legacy tests" | **5 distinct fields, 8 properties** | `strategy_session_facade.py:115-164` |

### Cache forwarders kept "for legacy tests"

`strategy_session_facade.py:114-164` keeps **five** writable cache slots as read/write `@property` forwarders onto `FacadeSessionState`:

1. `_planet_index` (getter + setter)
2. `_all_stars_cache` (getter + setter)
3. `_all_stars_cache_turn` (getter + setter)
4. `_fleets_by_hex_cache` (getter + setter)
5. `_fleets_by_hex_turn` (getter + setter)
6. `_race_registry` (getter + setter)

Plus two internal helpers that the same `# preserved for legacy tests` block frames as "callable" rather than data: `_build_planet_index`, `_build_fleet_hex_index`, `_get_fleet_by_id`, `_get_planet_by_id`, `_get_empire_by_id`. The block comment at `strategy_session_facade.py:114-117` explicitly labels these as "preserved for legacy tests." The same intent is documented in `game/strategy/facade/slices/_facade_state.py:44` ("when they assign `facade._planet_index = {...}`").

There is **also** a `_resolve_economy_config` method at `strategy_session_facade.py:372-374` whose docstring marks it `(legacy alias)`, and a `# pragma: no cover — internal helper` marker. It forwards to `EconomySlice.resolve_economy_config()` and is callable from outside; the warning log path in `game/strategy/facade/slices/economy_slice.py:75` confirms it is the legacy resolution path for sessions missing `economy_config`.

### Tests that pin the cache forwarders

`rg` against `tests/` for the six cache-field names yields these pin-points (only the strategy-facade-level ones count for TD-08; UI-screen and turn-engine matches are unrelated members of unrelated classes):

1. **`tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`** — the frozen contract: `PROTECTED_ATTRS = {"_planet_index", "_fleets_by_hex_cache", "_all_stars_cache", "_race_registry"}` (lines 127-132). `TestProtectedSurface.test_protected_attrs_settable_on_instance` (lines 192-214) asserts each of those is **settable on a fresh instance** and **round-trips** — that is the test that locks the writable @property into place. The docstring at line 194 explicitly says "Tests like `test_colony_demographic_view.py` assign directly to `facade._planet_index` and `facade._race_registry`."

2. **`tests/unit/strategy/facade/test_colony_demographic_view.py`** — the "downstream test" the public-api docstring referred to. `_facade_for(...)` at lines 82-103 builds a facade and then writes `facade._planet_index = {planet.id: planet}` and `facade._race_registry = race_registry` (lines 95, 98). A second test (line 125) sets `facade._planet_index = {}` to force a "missing planet" branch. This file is the active caller of the legacy writable surface — it is what makes the contract un-droppable today.

3. **`tests/unit/strategy/facade/test_facade_indices.py`** — line 46 asserts `hasattr(facade, '_planet_index')` after a `_get_planet_by_id` call, pinning the readable forwarder.

No production code under `game/` reaches into `facade._planet_index`, `facade._all_stars_cache`, `facade._fleets_by_hex_cache`, or `facade._race_registry`. The 25 UI files that touch `facade._<something>` (per the earlier `rg facade\._` scan) all consume the *callable* protected helpers (`_get_planet_by_id`, etc.), not the cache fields. **The whole point of the cache forwarders is now exactly what the report claims: test compatibility, nothing else.**

### Verdict

**VERIFIED.** The facade boundary is at least as wide as the report claims (in fact wider, 68 vs 53; 36 vs 28). The cache forwarders are kept solely to satisfy three test files; production code does not depend on them. The boundary is also incentivising further growth — the frozen contract was last expanded for PROJ-FMS-B/C/D (lines 60-64) and PROJ-382 (line 107), each of which **added** a public method rather than collapsing onto a smaller stable shape.

---

## Affected Code

### Facade (primary)
- `game/strategy/facade/strategy_session_facade.py` — the composer; will become smaller after the API-reduction pass.
- `game/strategy/facade/slices/_facade_state.py` — shared cache holder; keep, but it stops being a backing store for the @property forwarders.
- `game/strategy/facade/slices/command_dispatch_slice.py` — host of the 36 dispatch helpers; behavior preserved, only the *exposure surface* changes.
- `game/strategy/facade/slices/{fleet,planet,system,empire,economy,event}_slice.py` — already organised by feature domain; the public boundary should re-export their methods through grouped accessors rather than 32 flat top-level names.
- `game/strategy/engine/commands/registry.py:258-267` (`specs_by_facade_helper`) — feeds the auto-installer in `_install_dispatch_forwarders`.

### Tests pinning the legacy surface
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` — the frozen contract test (must be rewritten to assert a *target* surface, not the current one).
- `tests/unit/strategy/facade/test_colony_demographic_view.py` — sets `_planet_index` and `_race_registry` directly; must be migrated to a public seam (factory helper or DI in the slice constructor) before the cache forwarders can be removed.
- `tests/unit/strategy/facade/test_facade_indices.py` — `hasattr(facade, '_planet_index')` assertion; rewrite to assert *behavior* (second call returns the same object) instead of *implementation* (the index field exists).
- `tests/unit/strategy/facade/test_strategy_session_facade.py` — broader facade tests; survey for incidental use of legacy aliases.

### UI callers (target audience of the slimmed API)
All 25 files surfaced by `rg "facade\.(get_|can_|handle_command|process_turn|dispatch_)" game/ui/`. None of them touch the cache forwarders or `_resolve_economy_config`; they are good citizens already and need only:
- one mechanical rename per direct dispatch call (e.g. `facade.dispatch_issue_move(...)` → `facade.commands.issue_move(...)`) if the dispatch helpers move under a grouped namespace.
- The mechanical rename can be deferred behind a single-step shim removal at the end of the migration if necessary, but no UI behavioural change is required.

### Docs to update
- `docs/systems/strategy_layer.md` — the facade boundary section.
- `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md` (referenced from the frozen contract docstring) — record the post-TD-08 target surface so future facade work uses it as the source of truth.

---

## Goal / End State

The facade evolves from "53→68 flat methods plus eight writable legacy-test shims" to a **domain-grouped, immutable, test-friendly boundary**. Concretely:

### Target public surface (single instance access points)

```
StrategySessionFacade
├── handle_command(cmd)                       # the only write entry point
├── process_turn(progress_callback=None)      # session lifecycle
├── facade_state                              # already public — kept
├── commands       -> FacadeCommands          # grouped dispatch (36 helpers move here)
├── fleets         -> FacadeFleetQueries      # 5 fleet read methods
├── systems        -> FacadeSystemQueries     # 6 star/system/storm read methods
├── planets        -> FacadePlanetQueries     # 2 planet read methods
├── empires        -> FacadeEmpireQueries     # 6 empire read methods
├── events         -> FacadeEventQueries      # 3 event read methods
├── session_meta   -> FacadeSessionInfo       # turn number, save path, human IDs
├── economy        -> FacadeEconomyQueries    # demographics + registries + race registry
└── validation     -> FacadeValidation        # can_colonize, can_move_to
```

Each group object is the *existing* slice instance, re-exported. The flat top-level names (`get_fleet`, `dispatch_issue_move`, etc.) become **deprecated aliases** during migration and are deleted at the end.

### Minimum API surface goals

- **Top-level callable methods:** 2 (`handle_command`, `process_turn`). Everything else is namespaced.
- **Top-level public attributes:** 9 (`facade_state` + 8 grouped accessors).
- **Total public callables reachable through the namespaces:** still ~50 — the goal is **shape, not count**: feature additions land inside the appropriate group, not on the top class.
- **Cache forwarders:** zero. `_planet_index`, `_all_stars_cache`, `_fleets_by_hex_cache`, `_race_registry`, and their `*_turn` siblings stop being a writable boundary; tests use a documented seeding helper instead.
- **Legacy aliases:** zero. `_resolve_economy_config` is replaced by `economy.resolve_config()` (renamed without leading underscore) or deleted if no external callers remain after migration.

### Why grouped accessors instead of yet another flat shrink

The previous pass (PROJ-309 sub-phase 3.7, see file docstring lines 7-15) already did the *internal* split. The remaining problem is that the public boundary is still flat, so:

- Tests have nothing to assert on besides a hand-maintained list of 68 names.
- Each new strategy/UI feature adds one more top-level method because that's the established pattern.
- Grouping makes the *cost* of a new top-level entry visible: it has to be either a new group or a method on an existing group with a clear domain owner.

This is consistent with what the report's "payoff approach" suggested: *"group read/write surfaces by feature domain."*

---

## Execution Preconditions

Before implementation begins:

1. Freeze the public-surface baseline with the current contract tests. Do not
   trust counts in comments or this document.
   ```text
   pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py -q
   ```
2. Re-enumerate the current UI callers before editing:
   ```text
   rg -n "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui
   ```
3. Confirm whether external TD-02 and TD-03 have already landed:
   - TD-02 affects the economy-config fallback seam.
   - TD-03 affects the metadata source behind `specs_by_facade_helper()`.
   If either is still moving, do not start this plan in parallel.
4. Pick one file for the new grouped namespace adapters and keep it stable.
   Recommended file: `game/strategy/facade/grouped_namespaces.py`.

## Concrete File Touch Plan

### Phase 1

- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
- New file: `tests/unit/strategy/facade/test_facade_grouped_namespaces.py`

### Phase 2

- `game/strategy/facade/strategy_session_facade.py`
- New file: `game/strategy/facade/grouped_namespaces.py`

### Phase 3

- All UI files returned by the Phase-0 grep
- No strategy-engine files should need behavioral changes here; this phase is
  caller migration only

### Phase 4

- `tests/unit/strategy/facade/test_colony_demographic_view.py`
- `tests/unit/strategy/facade/test_facade_indices.py`
- `game/strategy/facade/slices/_facade_state.py`
- `tests/unit/strategy/facade/test_strategy_session_facade.py` if it still
  references legacy cache seams

### Phase 5

- `game/strategy/facade/strategy_session_facade.py`
- `game/strategy/facade/slices/command_dispatch_slice.py` only if the flat
  helper installer logic is still embedded there
- Any remaining UI/test callers surfaced by grep after Phase 4

### Phase 6

- `docs/systems/strategy_layer.md`
- `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md`
- `docs/03_CONVENTIONS.md` only if a new grouped-facade rule is added

## Weak-LLM Guardrails

- Do not start with a repo-wide rename. First create the grouped surface, then migrate callers, then delete the flat surface.
- Treat cache-forwarder removal as a test migration problem. Move tests off those attributes before deleting them.
- Do not keep both the full flat API and the grouped API indefinitely. The grouped API is transitional only until callers are migrated.
- Keep `handle_command(...)` and `process_turn(...)` as the only top-level behavioral entry points. Do not add new top-level facade methods during the migration.
- Prefer grep-driven, mechanical caller rewrites in Phase 3. A weak LLM should not be inventing new per-file API shapes.

---

## Remediation Plan

Strict TDD per `AGENTS.md`/`CLAUDE.md`. Each phase begins with the failing test that pins the *target* shape, then refactors until it passes.

### Phase 1 — Pin the target surface (failing tests first)

1. Rewrite `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`:
   - Replace `PUBLIC_METHODS` (68 entries) with `PUBLIC_TOP_LEVEL = {"handle_command", "process_turn"}` and `PUBLIC_GROUP_ACCESSORS = {"facade_state", "commands", "fleets", "systems", "planets", "empires", "events", "session_meta", "economy", "validation"}`.
   - Add a `test_no_legacy_flat_methods` test that asserts none of the 36 `dispatch_*` names and none of the 32 flat read methods exist as top-level attributes anymore.
   - Add a `test_grouped_namespaces_expose_expected_methods` test that walks each group accessor and asserts the per-group method list (sourced from a `GROUP_CONTRACT` dict in the test).
   - Drop `PROTECTED_ATTRS`; replace with `test_legacy_cache_attrs_removed` that asserts `_planet_index`, `_all_stars_cache`, `_fleets_by_hex_cache`, `_race_registry` are **not** settable on the instance.
   - Confirm all four new tests **fail** against the current facade — that's the TDD red.

2. Add a new file `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` that verifies behavior through the new surface (e.g. `facade.fleets.get(123)` returns the same `FleetInfo` the old `facade.get_fleet(123)` did). Use existing fixtures.

3. Run focused test set, confirm reds.

### Phase 2 — Introduce grouped accessors as the new primary surface

1. Add the eight group accessor `@property` methods on `StrategySessionFacade`. Each returns its existing slice. For groups that need a smaller verb surface than the slice exposes today (e.g. `commands.issue_move` instead of slice's `dispatch_issue_move`), introduce a thin **GroupNamespace** dataclass that wraps the slice and exposes only the intended verbs with their final names.
   - `FacadeCommands` wraps `CommandDispatchSlice` and exposes verbs like `issue_move`, `issue_colonize`, etc. — name = `dispatch_*` with the `dispatch_` prefix stripped. Mapping is mechanical via `command_registry.specs_by_facade_helper()`.
   - `FacadeFleetQueries` wraps `FleetSlice` and renames `get_fleet` → `get`, `get_fleets_at_hex` → `at_hex`, `get_fleet_path_preview` → `path_preview`, `get_fleet_path_projection` → `path_projection`, `get_fleet_remaining_pods` → `remaining_pods`. (Removing the redundant `fleet`/`fleets` prefix is the actual API shrink — callers say `facade.fleets.path_preview(...)`.)
   - Similar for `FacadePlanetQueries`, `FacadeSystemQueries`, `FacadeEmpireQueries`, `FacadeEventQueries`, `FacadeEconomyQueries`, `FacadeValidation`, `FacadeSessionInfo`.
2. Behavior tests in `test_facade_grouped_namespaces.py` should now go green.

### Phase 3 — Migrate UI callers to the grouped surface

1. Mechanical rewrite across the 25 UI files surfaced earlier:
   - `facade.get_fleet(id)` → `facade.fleets.get(id)` etc.
   - `facade.dispatch_issue_move(...)` → `facade.commands.issue_move(...)` etc.
2. Use one commit per UI screen group to keep diffs reviewable.
3. Run the UI/integration test slices (`pytest tests/unit/ui tests/integration -x`) after each commit.

### Phase 4 — Migrate tests off `_planet_index` / `_race_registry`

1. In `tests/unit/strategy/facade/test_colony_demographic_view.py`, replace the direct writes:
   - `facade._planet_index = {...}` becomes `facade.facade_state.seed_planet_index({...})` (new public helper on `FacadeSessionState` — `seed_*` makes the test-only intent explicit).
   - `facade._race_registry = ...` becomes `facade.facade_state.seed_race_registry(...)` (or pass the registry through the slice/economy constructor — preferred if it can be done without refactor sprawl).
2. In `tests/unit/strategy/facade/test_facade_indices.py`, replace `assert hasattr(facade, '_planet_index')` with a behavioral assertion: `assert facade.planets.get(42) is facade.planets.get(42)` (cached identity).
3. Sweep for any other test file that still writes to a legacy cache attr (none remain in `game/`; verify with `rg "facade\.(_planet_index|_all_stars_cache|_fleets_by_hex_cache|_race_registry)" tests/`).

### Phase 5 — Remove the legacy surface (root-cause delete, no shims)

1. Delete the eight cache-forwarder `@property` blocks at `strategy_session_facade.py:114-164`.
2. Delete the 32 flat read-method forwarders and the auto-installer's `dispatch_*` setattr loop at `strategy_session_facade.py:448-477`. (Keep the registry's `specs_by_facade_helper()` — it now feeds `FacadeCommands` instead.)
3. Delete `_resolve_economy_config` (legacy alias). Verify zero remaining external callers with `rg "_resolve_economy_config" game/ tests/`.
4. Re-run the full Phase 1 test set: should now be **green** (legacy surface removed, grouped surface present).
5. Re-run the focused-test suite plus `pytest tests/unit/strategy/facade tests/unit/ui tests/integration/strategy -q`.
6. Run the canonical sharded suite from `CLAUDE.md`: `python Tools/test_sharded/test_sharded.py`.

### Phase 6 — Documentation

1. Update `docs/systems/strategy_layer.md` "facade boundary" section with the grouped surface and the test-seeding contract on `FacadeSessionState`.
2. Update `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md` so the historical decomposition record references the post-TD-08 target shape (don't overwrite the historical content; append a new section).
3. Verify `docs/03_CONVENTIONS.md` does not contradict the new pattern; if a "use small grouped facades" convention is now stronger, add a single bullet.

No save-file migrations, no compat shims, no deprecation warnings — per `CLAUDE.md` rule 3, the old surface is deleted in Phase 5 and all callers are updated in Phase 3-4 first.

---

## Test Strategy

- **Phase 1 (red, before code):** four new public-API contract tests; one new grouped-namespace behavior test file. All four must fail against current `main` so we know we're driving with the failing test, not retrofitting.
- **Behavior parity (Phase 2-3):** the grouped namespace tests assert each new accessor returns the same result the old top-level method would have. Run `tests/unit/strategy/facade` plus the existing facade contract suite to catch behavioral drift.
- **UI regression (Phase 3):** after each UI commit, run `pytest tests/unit/ui tests/integration/ui -x`. The UI/integration shards in the test_sharded harness already cover the strategy screens; rely on those rather than building a new UI-level facade test from scratch.
- **Cache-seeding migration (Phase 4):** the rewritten `test_colony_demographic_view.py` and `test_facade_indices.py` should pass before and after Phase 5's deletion — i.e. the seeding helper is the migration path itself. If a test only passes by adding the seeding helper, it proves the helper covers the previously direct-write seam.
- **Final validation:** full `python Tools/test_sharded/test_sharded.py` after Phase 5, before docs.
- **Static check:** add a `rg`-based smoke test (or a guard in `test_strategy_session_facade_public_api.py`) that `rg "facade\._(planet_index|all_stars_cache|fleets_by_hex_cache|race_registry)" tests/` returns zero matches outside the seeding helper file. This makes the no-legacy-cache rule self-enforcing.

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| UI mechanical rewrite misses a call site, causing a runtime `AttributeError` on a rarely-visited screen | Medium | Medium | `rg "facade\.(dispatch_|get_|can_)"` across `game/ui` is exhaustive; the auto-installer already enumerates dispatch helpers via the registry, so the rename list is generable from the registry rather than typed by hand. Run the full UI shard before merging. |
| `test_colony_demographic_view.py` was written against an implementation detail; rewriting its seeding may quietly relax coverage | Low | Medium | The behavioral assertions (what `get_colony_demographic_view` returns) stay intact; only the *seeding mechanism* changes. Diff the test before/after to confirm no `assert` lines were dropped. |
| A third-party test or external script depends on `facade.dispatch_*` (e.g. AI playtest harnesses, replay tools) | Low | Low | `rg` across the repo; if found, migrate the same way as UI callers. No external SDK is published. |
| The grouped accessors create unexpected import cycles via slice re-exports | Low | Low | Slices already exist with stable imports; the new `Facade*Queries` namespaces are thin dataclasses with no new modules outside `game/strategy/facade/`. |
| Renaming `dispatch_X` to `commands.X` (stripping prefix) collides with an existing top-level method | Low | Low | Mechanical check via `rg "def issue_|def queue_|def split_|def delete_|def reorder_|def add_to_|def remove_from_|def clear_|def set_atmosphere"` on the slice — none of these collide with non-command members today. |
| Hidden test depending on `facade._all_stars_cache_turn` (the only forwarder without a paired contract assertion) | Low | Low | Already searched — zero matches in `tests/` for that name. |

The dominant risk is the **UI regression surface**. Mitigated by phase ordering: UI rewrite is Phase 3 (callers updated before the legacy surface is deleted in Phase 5), so a missed callsite produces a deterministic test failure rather than a latent runtime bug.

---

## Dependencies / Order

### Coupling to TD-02

TD-02 (`GameSession` is still both session model and composition root) is **soft-coupled** to TD-08:
- The facade's `_resolve_economy_config` legacy alias exists because `GameSession` does not always populate `economy_config` cleanly during rehydration (`game/strategy/facade/slices/economy_slice.py:75` warning is the smoking gun). If TD-02 ships first, the alias may be deletable in Phase 5 without any other change. If TD-08 ships first, Phase 5 keeps the warning-log fallback inside `FacadeEconomyQueries.resolve_config()` until TD-02 lands.
- **Recommended order:** ship TD-08 **after** TD-02's "shared bootstrap/rehydration path" lands, so the legacy fallback genuinely disappears. If TD-02 is not on the near roadmap, TD-08 can ship independently and leave the fallback inside the new grouped accessor as documented technical debt to clean up alongside TD-02.

### Coupling to TD-03

TD-03 (command/order metadata in multiple truth surfaces) is **hard-coupled** to TD-08 in one specific way:
- The auto-installer at `strategy_session_facade.py:448-477` uses `command_registry.specs_by_facade_helper()`. The new `FacadeCommands` namespace in Phase 2 uses the same registry call. If TD-03 reshapes the registry's spec API (e.g. introduces an `OrderMetadataView`), `FacadeCommands` needs to be re-pointed at it.
- **Recommended order:** TD-03 first, then TD-08. If TD-08 is scheduled first, structure `FacadeCommands` to take the iterable of `(helper_name, command_cls)` pairs as a constructor parameter rather than importing the registry directly, so the TD-03 reshape can swap in a new source without touching `FacadeCommands`.

### Coupling to other TDs

- **TD-06 (`ShipInstance` overload):** none. ShipInstance does not flow through the facade boundary; queries return `FleetInfo`/`PlanetInfo` DTOs.
- **TD-01, TD-04, TD-05, TD-07, TD-09, TD-10:** independent.

### Wave-level placement

The report's roadmap (lines 285-310) puts TD-08 in **Wave 2: Lifecycle and entity slimming**, alongside TD-02 and TD-06, after the Wave 1 architecture cleanup (TD-01/TD-03/TD-05). That ordering is consistent with the dependencies above — keep it.

---

### Ordering conclusion for this owned set

- Do **not** start TD-08 until the external TD-02 and TD-03 prerequisites are
  stable enough that the executor will not be chasing moving targets.
- Relative to the other owned plans, TD-08 does **not** depend on TD-07, TD-09,
  or TD-10. The constraint is external, not internal.
- If you must place it in a linear owned-only queue, run it **after TD-09 and
  TD-07**, and before TD-10 only if the same roadmap wants a cleaner
  UI/strategy seam before the larger deployable-substrate refactor.

---

## Acceptance Criteria

- [ ] `StrategySessionFacade` exposes only the grouped namespace accessors plus `handle_command(...)`, `process_turn(...)`, and `facade_state`.
- [ ] No legacy cache-forwarder properties remain on `StrategySessionFacade`.
- [ ] UI callers use the grouped surface consistently.
- [ ] Tests that previously wrote `_planet_index`, `_all_stars_cache`, `_fleets_by_hex_cache`, or `_race_registry` now go through an explicit supported path.
- [ ] The top-level `dispatch_*` facade methods are gone, and the grouped commands surface is the only command-helper path.
- [ ] Focused facade and UI suites are green before the sharded run.
- [ ] `python Tools/test_sharded/test_sharded.py` is green.

---

## Estimated Scope

Calibrated to LLM time per `CLAUDE.md` "Estimate in LLM time, not human time":

| Phase | Work | Estimate |
|-------|------|----------|
| 1 | Rewrite contract test + new namespace test | a few minutes |
| 2 | Add grouped accessors + `Facade*` namespace dataclasses (~8 small classes, mechanical) | under 10 minutes |
| 3 | Mechanical rename across 25 UI files; verify per-shard | 15-20 minutes including test runs |
| 4 | Migrate `test_colony_demographic_view.py` + `test_facade_indices.py` + add `seed_*` helpers on `FacadeSessionState` | under 10 minutes |
| 5 | Delete the legacy surface; re-run full sharded suite | a few minutes editing + the sharded suite's wall-clock runtime (legitimate bottleneck — minutes, not seconds) |
| 6 | Doc updates (one section in `strategy_layer.md`, one append in PROJ-309 findings, optional conventions bullet) | a few minutes |

**Total wall-clock for the agent:** roughly 45-60 minutes of work, dominated by the sharded-suite runs in Phases 3 and 5 (those are the real bottleneck — pure editing is well under 20 minutes).

This is single-pass work; do not sequence it across multiple "rounds" — the entire backlog is one pass at LLM scale.
