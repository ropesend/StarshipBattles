# PROJ-292: Audit High + Major Cleanup (PROJ-283..290 Closeout)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-292` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-292 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. H1 — Thread `view` kwarg into PlanetListWindow + BuildQueuePanelFactory | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. M1 — Introduce empire_economy_service.py facade; remove UI→engine direct imports | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. H2 + M2 — Pin projector vs engine drain + CachedRaceRegistry invalidation tests | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. H3 — Narrow `except (AttributeError, Exception)` in `_build_projection_grid` | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Minor sweep (m1, m4-m13, plus typo fixes) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs + final suite + project close | Awaiting User Verification | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-19
**Active Phase:** ALL 6 PHASES CODE + DOCS WORK COMPLETE — awaiting user manual smoke (Phase 6 Task 6.4) + PROJ-283..290 Archive sign-off
**Last Action:** Phase 6 Tasks 6.1–6.3, 6.5, 6.6 complete.
- 6.1 `docs/04_SERVICES.md`: new "Empire Economy Service (PROJ-292 M1)" subsection listing the service, consumers, and future import policy.
- 6.2 `docs/systems/strategy_layer.md` § Planet Report Panel UI: added H1-coverage-completion bullet noting the view-threading backfill into `PlanetListWindow` + `BuildQueuePanelFactory`.
- 6.3 Full sharded suite: **15139 tests | 15138 passed | 1 failed** (the long-standing theme-bleed flake, same as PROJ-291 close). Net +26 tests from PROJ-292. Zero regressions.
- 6.5 `Projects/projects_index.md`: re-fixed the `w# Projects Index` typo (reverted between sessions somehow); marked PROJ-291 + PROJ-292 as `Awaiting Verification` with last-updated=2026-04-19. PROJ-283..290 stay at `Awaiting Verification` until user confirms the consolidated manual smoke in `MANUAL_SMOKE_CHECKLIST.md`.
- 6.6 `validate_phase.py PROJ-292 6` passes for all completed tasks.

Task 6.4 (manual smoke) is deferred to user. The consolidated hand-off lives at [MANUAL_SMOKE_CHECKLIST.md](MANUAL_SMOKE_CHECKLIST.md) — covers every deferred smoke across PROJ-283..292.

**Previous Action:** Phase 5 (Minor sweep) complete. Landed 11 minor-severity fixes: (m17) fixed `w# Projects Index` typo in projects_index.md; (m1) documented kwarg-fallback asymmetry in `PlanetReportPanel.update_planet` docstring; (m4) wrapped `ColonyDemographicView.total_upkeep` in `MappingProxyType` via `__post_init__`; (m5) enforced largest-count-first species sort in the same `__post_init__`; (m6) added `logger.warning` to `StrategySessionFacade._resolve_economy_config` silent fallback; (m7) added tie-break-convention docstring to `format_uncolonized_habitability_for_empire`; (m8) verified `Tools/test_sharded/test_sharded.py` runs `pytest tests/` which includes integration tests; (m9) added `TestProjectionGridAssembly` (3 tests) pinning label count + rect non-overlap for `_build_projection_grid`; (m10) wrote `MANUAL_SMOKE_CHECKLIST.md` aggregating deferred smokes from PROJ-283..292; (m12) verified `population_food_resource` shim fully retired by PROJ-291 (only a history-comment reference remains in the source); (m13) aligned `docs/systems/strategy_layer.md` growth-percentage rendering claim with actual code. Added 5 new tests for m4+m5 DTO invariants in `test_colony_demographic_view.py`. Targeted suite: `pytest tests/unit/ui/ tests/unit/strategy/facade/` → 3687 passed, zero regressions.

**Previous Action:** Phase 4 (H3) complete. Added `TestNetCellColorExceptionHandling` (2 tests) to `tests/unit/ui/panels/test_planet_report_panel.py` — Test 1 (AttributeError swallow) passed pre-fix; Test 2 (RuntimeError propagation) confirmed failing against the pre-fix catch-all. Narrowed the catch at `game/ui/panels/planet_report_panel.py:456` from `except (AttributeError, Exception):` to `except AttributeError:` — real bugs now propagate instead of being silently swallowed by the colour-setter fallback. Targeted regression: `pytest tests/unit/ui/panels/` → 316 passed, zero regressions.

**Previous Action:** Phase 3 (H2 + M2) complete. New integration test `tests/integration/strategy/test_projector_drain_matches_engine.py::TestProjectorMatchesEngineDrain` (3 tests) pins the contract that `PlanetEconomyProjector._project_yard_drain` agrees with `ProductionEngine._process_queue_tick_dynamic` for every resource the queued item actually costs (per-tick drain × 100 == per-turn projection). A scope caveat is documented in the module docstring: the projector projects across ALL `build_rate` resources; the engine only drains the ones the item costs; so the comparison scope is intentionally `set(item.total_cost)`. Added `TestCachedRaceRegistryStaleness` (4 tests) to `tests/unit/strategy/systems/test_race_library.py` pinning the manual-invalidate contract: cache hits persist until `invalidate(race_id)`; targeted invalidation leaves other races cached; `invalidate()` with no arg clears all; None results cache-and-invalidate identically to hits. Per decisions.md Q3 default: the optional `auto_refresh_on_mtime` kwarg was NOT added — PROJ-287's "external file edits require restart" contract stands. Regression suite: `pytest tests/unit/strategy/systems/ tests/integration/strategy/` → 453 passed, 1 skipped, zero regressions.

**Previous Action:** Phase 2 (M1) complete. New service-layer facade [game/strategy/services/empire_economy_service.py](game/strategy/services/empire_economy_service.py) exposes one method (`get_snapshot(empire) -> EmpireEconomySnapshot`) + re-exports the snapshot dataclass. `__all__` explicitly excludes `EmpireEconomyCalculator` so UI code can't reach the engine class via the service. Created test file `tests/unit/strategy/services/test_empire_economy_service.py` (4 tests covering shape equivalence, re-export, __all__ discipline, full-kwarg construction) — all confirmed failing pre-implementation. UI migrations: `empire_treasury_panel.py:19` and `empire_panel_window.py:18` now import from `game.strategy.services.empire_economy_service`; `empire_panel_window._build_treasury_tab` switched from direct `EmpireEconomyCalculator(...).calculate(empire)` to `EmpireEconomyService(...).get_snapshot(empire)`. Verified zero remaining UI→engine-class imports (documented in decisions.md that residual `.commands` / `.game_config` / `.game_session` imports are intentional cross-layer boundaries, not M1's scope). Targeted suite: `pytest tests/unit/ui/ tests/unit/strategy/services/` → 3651 passed, zero regressions.

**Previous Action:** Phase 1 (H1) complete. Added `TestViewThreading` test classes in new files `tests/unit/ui/screens/test_planet_list_window.py` (3 tests) and `tests/unit/ui/screens/test_build_queue_panel_factory.py` (3 tests) — each confirmed failing pre-fix. Added `facade: Optional = None` kwarg to both `PlanetListWindow.__init__` and `BuildQueuePanelFactory.__init__`. Wired the view-resolution at both fix sites: `view = facade.get_colony_demographic_view(planet.id) if planet.owner_id is not None and facade is not None else None`, then threaded `view=view` into `PlanetReportPanel(...)` at both call sites. Updated construction sites: `strategy_window_manager._open_planet_list_window` now passes `facade=facade`; `BuildQueueScreen.__init__` now passes `facade=facade` when constructing the panel factory. Targeted suite: `pytest tests/unit/ui/screens/ tests/unit/ui/panels/` → 2387 passed, zero regressions.
**Next Action:** User-gated.
- **User manual smoke (Phase 6 Task 6.4)**: run through [MANUAL_SMOKE_CHECKLIST.md](MANUAL_SMOKE_CHECKLIST.md). Seven sections cover Treasury, FoodAllocationEditor, multi-species growth, per-species sub-block rendering in all three colonized contexts, uncolonized habitability display, projection grid exception handling, and race registry staleness.
- **Archive sign-off**: after the user confirms the smoke checklist, update `Projects/projects_index.md` — move PROJ-283..290 + PROJ-291 + PROJ-292 from `Awaiting Verification` to `Archived`. Delete `Temp Review Docs/` (optional — findings/ is the durable archive).

**Blockers:** User manual smoke before any PROJ-283..292 row can move to `Archived`.

**Context for Next Agent:** All PROJ-291 + PROJ-292 code + tests + docs are complete. The only remaining work is the user's consolidated manual-smoke sweep. If issues surface during smoke, open a new ticket rather than re-opening PROJ-291/292.

## Overview

Resolve the 3 High + 3 Major + 11 Minor findings from the dual cross-project audit of PROJ-283..290 that aren't gating sign-off. Aimed at long-term codebase health: tighten exception handlers that mask bugs, pin contracts that currently rely on docstrings, and retire technical debt (UI→engine layer violations, untested cache paths, asymmetric API surfaces).

## Goals

- **H1**: `PlanetReportPanel.view` is threaded by EVERY caller that shows colonized planets — `PlanetListWindow` and `BuildQueuePanelFactory`. Per-species sub-block visible in all colonized contexts. PlanetSelectionWindow (uncolonized-only) intentionally untouched.
- **H2**: Integration test pins that `PlanetEconomyProjector.project(planet).yard` agrees with `ProductionEngine._process_queue_tick_dynamic` actual drain for the same planet. Catches future drift if `_collect_planet_sources` refactors.
- **H3**: `_build_projection_grid` net-cell colour code uses `except AttributeError:` only (not the catch-all). Real bugs surface instead of being silently swallowed.
- **M1**: New `game/strategy/services/empire_economy_service.py` facade. UI panels (`empire_treasury_panel.py`, `empire_panel_window.py`) import the service, NOT the engine class. Layer-violation backlog cleared.
- **M2**: New `TestCachedRaceRegistryStaleness` test pins the cache invalidation contract. (Optional: add an mtime fallback to `CachedRaceRegistry.get_race` if user wants defence-in-depth — Phase 3 gathers a user decision.)
- **Minors**: m1 (asymmetric `update_planet` semantics — docstring fix), m4-m13 cleanups (typed `MappingProxyType`, DTO `__post_init__` sort enforcement, doc/code drift on growth-rate formatting, etc.).
- Full sharded suite green except the long-standing flake.

## Scope

**In:**
- `game/ui/screens/planet_list_window.py` + `game/ui/screens/build_queue_panel_factory.py` (view threading).
- `game/strategy/services/empire_economy_service.py` (NEW facade).
- `game/ui/panels/empire_treasury_panel.py` + `game/ui/screens/empire_panel_window.py` (import migration).
- `game/strategy/systems/race_library.py` (cache invalidation test target; possibly add mtime fallback per user decision in Phase 3).
- `game/ui/panels/planet_report_panel.py` (H3 narrow exception, m9 UI assembly tests, m4 `Mapping` → `MappingProxyType` for ColonyDemographicView).
- `game/strategy/facade/dto/colony_demographic_view.py` (m4 + m5 sort enforcement).
- New tests across the affected files.
- Minor doc updates (m1, m13, m17 typo fix).

**Out:**
- All Critical findings (PROJ-291 territory).
- The `IRaceRegistry` protocol surface expansion (m14 — defer until a real consumer needs it).
- Renaming `last_food_ratio` → `last_supply_ratio` (m11) — large blast radius across docs and engine call sites; deferred to a separate cleanup project unless user opts in.
- The long-standing `test_copy_designs_without_themes_preserves_original` flake (m18, predates PROJ-280; out of scope for this audit cycle).

## Key Files

| Component | File Path |
|-----------|-----------|
| H1 fix sites | [game/ui/screens/planet_list_window.py:511](game/ui/screens/planet_list_window.py#L511), [game/ui/screens/build_queue_panel_factory.py:181](game/ui/screens/build_queue_panel_factory.py#L181) |
| H1 reference (correct wiring) | [game/ui/screens/strategy_detail_formatter.py:264](game/ui/screens/strategy_detail_formatter.py#L264) |
| H2 target | [game/strategy/services/planet_economy_projector.py](game/strategy/services/planet_economy_projector.py) (the `_project_yard_drain` method calling `_collect_planet_sources`) |
| H2 pinning test (NEW) | `tests/integration/strategy/test_projector_drain_matches_engine.py` |
| H3 fix site | [game/ui/panels/planet_report_panel.py](game/ui/panels/planet_report_panel.py) (the `_build_projection_grid` net-cell `except (AttributeError, Exception)` block — search for `text_colour`) |
| M1 layer violation sites | [game/ui/panels/empire_treasury_panel.py:19](game/ui/panels/empire_treasury_panel.py#L19), [game/ui/screens/empire_panel_window.py:18](game/ui/screens/empire_panel_window.py#L18) |
| M1 new facade | `game/strategy/services/empire_economy_service.py` (NEW) |
| M2 target | [game/strategy/systems/race_library.py](game/strategy/systems/race_library.py) (`CachedRaceRegistry`) |
| M2 pinning test (NEW) | `tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistryStaleness` |
| Minors home | various (m1 docstring in planet_report_panel.py, m4 Mapping fix in colony_demographic_view.py, m17 typo in projects_index.md, m13 doc drift in strategy_layer.md) |

## Related Documents
- [design.md](design.md) — Architectural rationale (facade shape, view-threading pattern, exception narrowing approach)
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — File manifest for parallel-work safety
- [findings/INDEX.md](findings/INDEX.md) — Cross-references the audit reports archived under PROJ-291/findings/

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-291 | Sibling — PROJ-291 fixes Criticals (gates PROJ-283..290 sign-off); this project cleans up Highs/Majors/Minors. Phase 2 of THIS project (M1 facade) needs PROJ-291 Phase 1 (C1 fix) landed FIRST to avoid merge friction on `empire_economy_calculator.py`. |
| PROJ-283..290 | Source of all findings. Once PROJ-291 + PROJ-292 close, the audit cycle is complete. |
| PROJ-285 | The H1 view-threading fix mirrors how PROJ-285 already wired its registry. |

## Verification
- [ ] All phase checklists complete
- [ ] H1: open a colonized planet from PlanetListWindow → per-species sub-block displays (matches strategy detail panel rendering for the same planet).
- [ ] H1: open a colonized planet from BuildQueuePanel → per-species sub-block displays.
- [ ] H2: `pytest tests/integration/strategy/test_projector_drain_matches_engine.py -v` green.
- [ ] H3: a forced exception in the net-cell colour setter (e.g. mock `text_colour =` to raise `RuntimeError`) propagates instead of being silently swallowed.
- [ ] M1: `grep -rn "from game.strategy.engine" game/ui/` returns ZERO results.
- [ ] M2: `pytest tests/unit/strategy/systems/test_race_library.py::TestCachedRaceRegistryStaleness -v` green.
- [ ] Full sharded suite: `python Tools/test_sharded/test_sharded.py` — same baseline as PROJ-291 close (~15080 tests, ~1 known failure).
- [ ] User verified end-to-end.
