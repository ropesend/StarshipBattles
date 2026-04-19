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
| 1. H1 — Thread `view` kwarg into PlanetListWindow + BuildQueuePanelFactory | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. M1 — Introduce empire_economy_service.py facade; remove UI→engine direct imports | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. H2 + M2 — Pin projector vs engine drain + CachedRaceRegistry invalidation tests | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. H3 — Narrow `except (AttributeError, Exception)` in `_build_projection_grid` | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Minor sweep (m1, m4-m13, plus typo fixes) | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. Docs + final suite + project close | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Planning complete; ready to begin Phase 1
**Last Action:** Project scaffolded as the sibling of PROJ-291. PROJ-291 fixes the 3 Critical findings from the dual cross-project audit; PROJ-292 picks up the remaining 3 High + 3 Major + 11 Minor findings. Both projects can run in parallel — file overlaps are listed in [manifest.md](manifest.md) and most are sequential append-only doc updates.
**Next Action:** Phase 1 Task 1.1 — write a panel-construction test for `PlanetListWindow` that asserts a colonized planet receives the per-species sub-block (currently it doesn't because `view` is not threaded). Then thread `view = facade.get_colony_demographic_view(planet.id) if planet.owner_id is not None else None` into both `PlanetListWindow` and `BuildQueuePanelFactory`. PlanetSelectionWindow (uncolonized only) intentionally untouched per the impartial-subagent verdict.
**Blockers:** Phase 2 should land AFTER PROJ-291 Phase 1 (C1 fix) because Phase 2 wraps `EmpireEconomyCalculator` in a service facade; if PROJ-291 is mid-flight on the same file there will be merge friction. Phase 1 + Phase 4 + Phase 5 are fully parallel-safe with PROJ-291.
**Context for Next Agent:** Read [findings/INDEX.md](findings/INDEX.md) (links to the dual-audit reports archived in PROJ-291/findings/). The High/Major findings are: H1 = view-kwarg dead in 2 of 3 colonized-context PlanetReportPanel callers (impartial subagent verdict: real UX regression, severity HIGH); H2 = `PlanetEconomyProjector._project_yard_drain` reaches into `_collect_planet_sources` private API with no integration pin; H3 = `except (AttributeError, Exception)` swallow in net-cell colour code; M1 = UI→engine direct import (pre-existing, unchallenged by PROJ-290); M2 = `CachedRaceRegistry` invalidation untested + no mtime fallback. Phase ordering keeps the most user-visible improvement (H1) first.

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
