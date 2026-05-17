# PROJ-430: Facade API reduction (TD-08)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-430` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-430 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Pin the target surface (red contract first) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Introduce grouped accessors | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate UI callers (25 files) | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate tests off legacy cache seams | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Delete the legacy surface (root-cause) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Documentation sync | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Phase 5
**Last Action:** Phase 4 complete — `FacadeSessionState.seed_planet_index` and `seed_race_registry` public helpers added. `test_colony_demographic_view.py` migrated to use them; `test_facade_indices.py` rewritten to assert caching behavior rather than implementation detail. Repo-wide sweep confirms zero remaining `facade._planet_index` / `_race_registry` / etc. writes in code (only in docstrings).
**Next Action:** Phase 5 — root-cause delete the 8 cache-forwarder properties, the 32 flat read-method forwarders, the auto-installer's `dispatch_*` setattr loop, and the `_resolve_economy_config` legacy alias.
**Blockers:** None

## Overview
Reduce `StrategySessionFacade`'s public boundary from a flat, ever-growing surface (68 public methods, including 36 `dispatch_*` helpers, plus 8 writable `_*` cache-forwarder `@property` slots and a `_resolve_economy_config` legacy alias) to a domain-grouped, immutable, test-friendly boundary. End state: 2 top-level callables (`handle_command`, `process_turn`) plus 9 grouped namespace accessors (`facade_state`, `commands`, `fleets`, `systems`, `planets`, `empires`, `events`, `session_meta`, `economy`, `validation`). Zero cache forwarders, zero legacy aliases — tests migrate to a documented `seed_*` helper on `FacadeSessionState`.

## Goals
- Collapse the 68-method flat surface to 2 top-level methods + 9 grouped accessor properties; the ~50 underlying callables move under the appropriate domain group with their final names (e.g. `dispatch_issue_move` → `commands.issue_move`, `get_fleet` → `fleets.get`).
- Delete all 8 cache-forwarder `@property` slots (`_planet_index`, `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn`, `_race_registry` — get + set on each) plus the `_resolve_economy_config` legacy alias. Root-cause delete per AGENTS.md rule 3; no parallel old + new surface.
- Migrate the 3 test files pinning the cache forwarders (`test_strategy_session_facade_public_api.py`, `test_colony_demographic_view.py`, `test_facade_indices.py`) onto a public `seed_*` seam on `FacadeSessionState` before Phase 5's deletion.
- Rewrite the frozen public-API contract test to assert the *target* shape (10 attrs) rather than the current 68-method roster, so the test enforces shape going forward.
- Make new strategy/UI features land inside the appropriate group, not as new top-level methods — group cost becomes visible, shrinks the incentive to bloat the facade.

## Scope
**In:** new grouped namespace dataclasses (`game/strategy/facade/grouped_namespaces.py`); rewrite of `strategy_session_facade.py` to expose group accessors and drop the flat surface, cache forwarders, and `_resolve_economy_config`; rewrite of the public-API contract test; mechanical rename across the 25 UI files surfaced by `rg "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui`; test migration to a new `FacadeSessionState.seed_*` seam; doc sync in `docs/systems/strategy_layer.md` and append to PROJ-309 findings.

**Out:** behavior changes inside any slice (`fleet_slice.py`, `planet_slice.py`, `economy_slice.py`, etc. keep their internal implementations); changes to `command_dispatch_slice.py` *behavior* (only its exposure surface changes); save-file migrations; compat shims or deprecation warnings; new top-level methods; renaming ABCs or DTOs (`FleetInfo`, `PlanetInfo` etc. unchanged); editing `tests/unit/strategy/facade/test_strategy_session_facade.py` beyond surveying for incidental legacy-alias use.

## Dependencies
Hard predecessors: none. Soft predecessors: PROJ-423 (TD-02). TD-02 changes what `StrategySessionFacade` needs to expose, so running this after PROJ-423 prevents churn against a moving facade surface. Specifically, TD-02's "shared bootstrap/rehydration path" lets the `_resolve_economy_config` warning-log fallback (`economy_slice.py:75`) disappear cleanly during Phase 5 instead of being carried forward inside `FacadeEconomyQueries.resolve_config()` as carried-over technical debt. TD-03 is also relevant: if TD-03 reshapes `command_registry.specs_by_facade_helper()`, the new `FacadeCommands` namespace should take the iterable as a constructor parameter (already planned that way) so the registry shape can be swapped without touching `FacadeCommands`.

See [EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) for the 10-plan arc placement (Wave 2: Lifecycle and entity slimming).

## Key Files
| Component | File Path | Type |
|-----------|-----------|------|
| Facade composer (rewrite — shrinks) | `game/strategy/facade/strategy_session_facade.py` | Production |
| Grouped namespace dataclasses (new) | `game/strategy/facade/grouped_namespaces.py` | Production (new) |
| Shared cache holder (`seed_*` helpers added) | `game/strategy/facade/slices/_facade_state.py` | Production |
| Economy slice (`_resolve_economy_config` callee) | `game/strategy/facade/slices/economy_slice.py` | Production |
| Command dispatch slice (host of 36 helpers) | `game/strategy/facade/slices/command_dispatch_slice.py` | Production |
| Frozen public-API contract test (rewrite) | `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | Test |
| Grouped namespace behavior tests (new) | `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` | Test (new) |
| Colony demographic view test (cache-forwarder pin #1) | `tests/unit/strategy/facade/test_colony_demographic_view.py` | Test |
| Facade indices test (cache-forwarder pin #2) | `tests/unit/strategy/facade/test_facade_indices.py` | Test |
| Broader facade tests (survey for legacy-alias use) | `tests/unit/strategy/facade/test_strategy_session_facade.py` | Test |
| Command registry (`specs_by_facade_helper`) | `game/strategy/engine/commands/registry.py` | Production (read-only — feed `FacadeCommands`) |
| Strategy layer doc | `docs/systems/strategy_layer.md` | Docs |
| PROJ-309 facade decomposition findings | `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md` | Docs (append) |
| 25 UI caller files (Phase 3 mechanical rename) | `game/ui/**` (enumerate via `rg "facade\.(dispatch_\|get_\|can_\|get_turn_number\|get_save_path\|get_human_player_ids\|get_race_registry\|get_colony_demographic_view)" game/ui`) | Production |

Full enumeration of touched files (production + tests + docs + the 25 UI callers) lives in [manifest.md](manifest.md).

## Phases

### Phase 1: Pin the target surface (failing tests first)
Rewrite `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` so the contract asserts the *target* shape (`PUBLIC_TOP_LEVEL = {"handle_command", "process_turn"}`, `PUBLIC_GROUP_ACCESSORS = {"facade_state", "commands", "fleets", "systems", "planets", "empires", "events", "session_meta", "economy", "validation"}`) rather than the current 68-method roster. Add `test_no_legacy_flat_methods`, `test_grouped_namespaces_expose_expected_methods` (driven by a `GROUP_CONTRACT` dict), and `test_legacy_cache_attrs_removed`. Drop `PROTECTED_ATTRS`. Author a new file `tests/unit/strategy/facade/test_facade_grouped_namespaces.py` that asserts behavior parity (`facade.fleets.get(123)` returns what `facade.get_fleet(123)` did). Confirm all new assertions are **red** against current `main` — that's the TDD anchor.

### Phase 2: Introduce grouped accessors as the new primary surface
Add a new file `game/strategy/facade/grouped_namespaces.py` containing 8 thin dataclasses: `FacadeCommands` (wraps `CommandDispatchSlice`, strips `dispatch_` prefix using `command_registry.specs_by_facade_helper()` passed in as a constructor parameter so TD-03 reshape is decoupled), `FacadeFleetQueries` (renames `get_fleet`→`get`, `get_fleets_at_hex`→`at_hex`, `get_fleet_path_preview`→`path_preview`, `get_fleet_path_projection`→`path_projection`, `get_fleet_remaining_pods`→`remaining_pods`), and analogues for `FacadePlanetQueries`, `FacadeSystemQueries`, `FacadeEmpireQueries`, `FacadeEventQueries`, `FacadeEconomyQueries`, `FacadeValidation`, `FacadeSessionInfo`. Add the 8 group-accessor `@property` methods on `StrategySessionFacade`; each returns the existing slice (wrapped through the new namespace dataclass where renaming applies). Behavior tests in `test_facade_grouped_namespaces.py` now green. Phase 1's `test_no_legacy_flat_methods` and `test_legacy_cache_attrs_removed` are **still red** by design — they go green in Phase 5.

### Phase 3: Migrate UI callers to the grouped surface
Mechanical rewrite across the 25 UI files surfaced by `rg "facade\.(dispatch_|get_|can_|get_turn_number|get_save_path|get_human_player_ids|get_race_registry|get_colony_demographic_view)" game/ui` — re-enumerate fresh, don't trust the count. Examples: `facade.get_fleet(id)` → `facade.fleets.get(id)`; `facade.dispatch_issue_move(...)` → `facade.commands.issue_move(...)`. One commit per UI screen group. After each commit, run `pytest tests/unit/ui tests/integration -x`. No UI behavior change — pure rename.

### Phase 4: Migrate tests off legacy cache seams
Add public `seed_*` helpers on `FacadeSessionState` (`seed_planet_index`, `seed_race_registry`, etc.) — the `seed_` prefix makes the test-only intent explicit. Rewrite `tests/unit/strategy/facade/test_colony_demographic_view.py` to call `facade.facade_state.seed_planet_index({...})` and `facade.facade_state.seed_race_registry(...)` instead of writing `facade._planet_index` / `facade._race_registry` directly. Rewrite `tests/unit/strategy/facade/test_facade_indices.py`'s `hasattr` assertion to a behavioral assertion (`facade.planets.get(42) is facade.planets.get(42)` — cached identity). Sweep `tests/` for any other writes to legacy cache attrs (`rg "facade\.(_planet_index|_all_stars_cache|_fleets_by_hex_cache|_race_registry)" tests/`). Survey `test_strategy_session_facade.py` for incidental legacy-alias use.

### Phase 5: Delete the legacy surface (root-cause, no shims)
Delete the 8 cache-forwarder `@property` blocks at `strategy_session_facade.py:114-164`. Delete the 32 flat read-method forwarders and the auto-installer's `dispatch_*` setattr loop at `strategy_session_facade.py:448-477` — keep `specs_by_facade_helper()` since `FacadeCommands` now feeds from it. Delete `_resolve_economy_config` (verify zero remaining external callers with `rg "_resolve_economy_config" game/ tests/`). Re-run the full Phase 1 test set: now **green**. Re-run `pytest tests/unit/strategy/facade tests/unit/ui tests/integration/strategy -q`. Final validation: `python Tools/test_sharded/test_sharded.py`.

### Phase 6: Documentation sync
Update `docs/systems/strategy_layer.md` facade-boundary section with the grouped surface and the `seed_*` test-seeding contract on `FacadeSessionState`. Append a new section to `Projects/active_projects/PROJ-309/findings/strategy_session_facade_decomposition.md` recording the post-TD-08 target surface as the new source of truth for future facade work (do not overwrite the historical content). Verify `docs/03_CONVENTIONS.md` does not contradict the new pattern; add a single bullet only if a "use small grouped facades" convention is now stronger. Skip `docs/_ignore/` per AGENTS.md.

## Related Documents
- [TD-08 source plan](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/TD-08_facade_api_reduction.md) — canonical specification (verification findings, file touch plan, per-phase success criteria, weak-LLM guardrails)
- [Strategy tech-debt EXECUTION_ORDER.md](../../../Reviews/results/2026-05-16_strategy-layer-tech-debt-review/Verified%20Problem%20Remediation%20Plans/EXECUTION_ORDER.md) — TD-08 placement (Wave 2, soft dep on TD-02, soft dep on TD-03)
- [design.md](design.md) — distilled architecture analysis and risk register
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list (including all 25 UI callers)

## Verification
Acceptance criteria from the TD-08 plan:
- [ ] `StrategySessionFacade` exposes only `handle_command(...)`, `process_turn(...)`, `facade_state`, and 9 grouped namespace accessors — total target public surface 12 names (down from 68 + 8 cache forwarders + 1 legacy alias).
- [ ] No legacy cache-forwarder properties remain on `StrategySessionFacade` (`_planet_index`, `_all_stars_cache`, `_all_stars_cache_turn`, `_fleets_by_hex_cache`, `_fleets_by_hex_turn`, `_race_registry` — get + set on each, all deleted).
- [ ] `_resolve_economy_config` legacy alias removed; `rg "_resolve_economy_config" game/ tests/` returns zero matches.
- [ ] Top-level `dispatch_*` facade methods are gone; the grouped `commands` namespace is the only command-helper path; all 36 dispatch helpers reachable through `facade.commands.<verb>` with `dispatch_` stripped.
- [ ] 25 UI callers use the grouped surface consistently; `rg "facade\.(dispatch_|get_|can_)" game/ui` returns zero matches against the legacy shape.
- [ ] Tests that previously wrote `_planet_index`, `_all_stars_cache`, `_fleets_by_hex_cache`, or `_race_registry` now go through `FacadeSessionState.seed_*` helpers.
- [ ] Focused facade and UI suites green before the sharded run (`pytest tests/unit/strategy/facade tests/unit/ui tests/integration/strategy -q`).
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] `docs/systems/strategy_layer.md` reflects the grouped surface; PROJ-309 findings appended with post-TD-08 target shape.
