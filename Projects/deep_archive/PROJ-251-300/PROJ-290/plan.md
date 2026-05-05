# PROJ-290: Empire Treasury + Uncolonized Habitability UI

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-290` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-290 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Empire-wide populace upkeep aggregator + treasury line | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Uncolonized-planet per-species habitability list (0-100) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Docs + cleanup | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL 3 PHASES COMPLETE — ready to close. Awaiting user sign-off.
**Last Action:** All three phases landed. Phase 1: `EmpireEconomySnapshot.total_population_upkeep` field + aggregation via shared `PlanetEconomyProjector`; new "Population Upkeep" expense row in `EmpireTreasuryPanel` hidden when all-zero. Phase 2: `format_uncolonized_habitability_for_empire` helper + extended `format_planet_info` signature with `empire` + `race_registry` keyword-only args; `PlanetReportPanel.__init__/update_planet` threaded to forward the deps; `PlanetListWindow` + `strategy_window_manager` wired to pass `facade.get_race_registry()`. Phase 3: docs updated (`strategy_layer.md §9` new subsection + `production_system.md § Habitability Multiplier` one-liner callout); full sharded suite 15063 tests / 15045 passed / 18 failed (ALL pre-existing — 13 food_allocation_editor PROJ-289-pending + 1 theme flake + 2 tick_mechanics shard flakes + 4 make_minimal_spec pygame-font flakes; 0 PROJ-290 regressions).
**Next Action:** User end-to-end smoke: (a) open Treasury — Population Upkeep row visible with populations, hidden on fresh game; (b) click an uncolonized planet from the Planet List — habitability section lists each resident species at 0-100 sorted desc; (c) click a colonized planet — habitability section NOT shown.
**Blockers:** None. All three dependencies (PROJ-286, 287, 288) at `Awaiting Verification`. PROJ-289 runs in parallel and is still Planning per projects_index.md.
**Deliverables Summary:**
- `EmpireEconomySnapshot.total_population_upkeep: Dict[str, float]` (sparse, empty `{}` for fresh-game / no-populations).
- `EmpireEconomyCalculator(__init__)` now accepts optional `economy_config` + `race_registry`; when both present, aggregates upkeep via `PlanetEconomyProjector.project(colony).upkeep`.
- `EmpireTreasuryPanel._get_expense_rows` conditionally inserts a "Population Upkeep" row BEFORE "Total" when non-zero; values passed pre-negated.
- `game/ui/screens/strategy_detail_fmt.py::format_uncolonized_habitability_for_empire` — new module-level helper.
- `format_planet_info` gains keyword-only `empire` + `race_registry` kwargs; emits habitability section only when `planet.owner_id is None` AND both deps present.
- `PlanetReportPanel` (`__init__` + `update_planet`) both accept and forward `empire` + `race_registry`.
- `PlanetListWindow` takes a new `race_registry=None` kwarg; `strategy_window_manager._open_planet_list_window` + `._open_empire_panel_window` both pull `facade.get_race_registry()` and thread it through.
- Production code paths preserve backward compat — legacy callers that only pass `registries=` keep working; the new features auto-hide.
- Docs: `docs/systems/strategy_layer.md §9 Treasury & Planet Detail UI Integration (PROJ-290)` + callout in `docs/systems/production_system.md § Habitability Multiplier`.

**Known limitations (scope-capped, not PROJ-290's job):**
- `planet_selection_window.py` + `build_queue_panel_factory.py` construction sites for `PlanetReportPanel` were NOT wired with `race_registry`. They default to None → uncolonized habitability section auto-hides in those contexts. Wiring them is a pure pass-through extension if ever needed.
- PROJ-289 keyword-stackability contract: `format_planet_info` signature uses `*, empire=None, race_registry=None`; any PROJ-289 kwargs must also be keyword-only to avoid positional-arg collisions.

## Overview

Add two UI surfaces consuming PROJ-286/287/288 infrastructure:
1. **Empire Treasury populace upkeep line** — new expense row aggregating per-resource population consumption across every empire colony. Feeds into the existing Treasury income/expense tally.
2. **Uncolonized-planet habitability panel** — new section on the planet detail panel shown only when `planet.owner_id is None`. Lists every species in `empire.resident_species()` with a 0-100 habitability score, sorted best-fit first.

## Goals

- `EmpireEconomySnapshot` (existing at `game/strategy/engine/empire_economy_calculator.py`) or a new parallel calculator produces a `total_population_upkeep: Dict[resource_id, float]` aggregated across all empire colonies.
- `EmpireTreasuryPanel` displays a new "Population upkeep" expense row — one cell per resource, signed.
- `PlanetReportPanel` shows an "Uncolonized — habitability for your species" section when the planet is unowned. Lists each `resident_species()` entry with a 0-100 score, sorted descending.
- Per-species list: `f"{race_name}: {score}/100"` (score is an integer).
- Empty-list fallback: if the empire has no `resident_species()` (fresh game start), show an informational message or hide the section.
- Tests cover both aggregation and rendering.

## Scope

**In:**
- `EmpireEconomySnapshot.total_population_upkeep` OR a new field / calculator method.
- `EmpireTreasuryPanel` changes: new row in the expense section.
- Planet report panel uncolonized-habitability section.
- `game/strategy/facade/dto/` — may add a new DTO if the existing Treasury snapshot needs enrichment.
- Tests for aggregation math + UI rendering.

**Out:**
- Tooltips / hover-detail for the uncolonized habitability list (e.g. "why is this planet marginal?"). Nice-to-have; future project.
- Per-colony breakdown of populace upkeep in the Treasury. User wants ONE number.
- Color coding on the 0-100 score (red/yellow/green bands). Could come later; user said "calculated value 0-100" so start with plain numbers.
- Changing the existing treasury layout structure — just adding ONE row.

## Key Files

| Component | File Path |
|-----------|-----------|
| Empire-wide upkeep aggregation | `game/strategy/engine/empire_economy_calculator.py` |
| Treasury panel new row | `game/ui/panels/empire_treasury_panel.py` |
| Uncolonized habitability section | `game/ui/panels/planet_report_panel.py` + `game/ui/screens/strategy_detail_fmt.py` |

## Related Documents
- [design.md](design.md) — Architecture rationale
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-286 | Dependency — multi-resource upkeep values are summed here |
| PROJ-287 | Dependency — `Empire.resident_species()` + `race_registry` drive Section 4 |
| PROJ-288 | Dependency — `ColonyDemographicView.total_upkeep` aggregates; planet-economy projector gives per-resource numbers |
| PROJ-289 | Sibling UI — same underlying data, different panel surfaces. Both must coordinate on layout in the planet report panel |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Manual scenario:
  - [ ] Open Empire → Treasury tab → see "Population upkeep" expense row, signed negative, one cell per resource.
  - [ ] Click an uncolonized planet with 2+ species in the empire → planet detail shows "Habitability for your species:" list; best fit first; 0-100 integer scores.
  - [ ] Click a colonized planet → uncolonized section NOT shown (per-species sub-blocks from PROJ-289 shown instead).
- [ ] User verified end-to-end.
