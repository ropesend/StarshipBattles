# PROJ-289: Planet Report Panel Per-Species + Per-Resource UI

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-289` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-289 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Per-species sub-block in planet info (habitability / happiness / growth) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Per-resource grid expansion (harvest / upkeep / yard / net) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Docs + cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Planning complete; ready to begin Phase 1 (BLOCKED on PROJ-287 + PROJ-288)
**Last Action:** Project scaffolded. Depends on PROJ-287 (race registry facade) and PROJ-288 (`ColonyDemographicView` DTO).
**Next Action:** After PROJ-287 + PROJ-288 complete, Phase 1 Task 1.1 — update `game/ui/screens/strategy_detail_fmt.py::format_planet_info` to render per-species sub-blocks with habitability, happiness, growth rate, food ratio, food allocation.
**Blockers:**
- **PROJ-287** — facade `get_race_registry()` resolves race_names for display.
- **PROJ-288** — `ColonyDemographicView` provides pre-computed per-species + per-resource data; the panel reads this one DTO instead of re-projecting per frame.
- Also PROJ-286 must land for the per-resource grid to show multi-resource upkeep.
**Context for Next Agent:** The planet report panel is at `game/ui/panels/planet_report_panel.py`. The current per-species text is a single HTML line at `game/ui/screens/strategy_detail_fmt.py:129` (inside `format_planet_info`): ` - {race_id}: {count} [+/~/-]`. User-confirmed sub-block layout with 4 metrics per species. The resource grid is built via `_build_resource_grid` at planet_report_panel.py:314; needs to expand from "stockpile / capacity" columns to "harvest / upkeep / yard / net" for every resource (food resources get non-zero upkeep, non-food resources get 0 upkeep). All data pre-computed in `ColonyDemographicView`.

## Overview

Rewrite the per-species text line and the per-resource grid in the planet report panel to consume `ColonyDemographicView` from the facade. Per-species: indented sub-block with habitability, happiness, growth rate, food ratio, food allocation (5 lines per species). Per-resource: full grid with harvest / upkeep / yard / net columns for every resource tracked on the planet.

## Goals

- Per-species sub-block in `format_planet_info`, replacing the single-line per-species layout. Uses `ColonyDemographicView.species` (already sorted largest-first).
- Per-resource grid expanded from 2 columns (current / max) to 4 columns (harvest / upkeep / yard / net) driven by `ColonyDemographicView.resource_projections`. Non-food resources show 0 in the upkeep column; food resources show the combined population upkeep (sum across species).
- Panel reads a single `facade.get_colony_demographic_view(planet_id)` call per update; no ad-hoc engine access.
- Graceful rendering for uncolonized planets (PROJ-290 will add species-habitability list there; PROJ-289 just needs "no per-species sub-blocks, no upkeep column" behavior).
- Tests pin the layout math (number of lines per species, column count, cell formulas).

## Scope

**In:**
- `game/ui/screens/strategy_detail_fmt.py::format_planet_info` — per-species sub-block rewrite.
- `game/ui/panels/planet_report_panel.py::_build_resource_grid` + `_update_resource_grid` — 4-column layout driven by `ColonyDemographicView`.
- `planet_report_panel.update_planet(planet, colony_view)` — accept the view as an additional kwarg (or pull via facade internally).
- Tests for the new rendering via the existing snapshot-style test pattern.

**Out:**
- Uncolonized-planet habitability list (that's PROJ-290).
- Treasury populace upkeep line (PROJ-290).
- Per-species resource allocation (more than food) — `food_allocation` stays a single slider for now; per-resource allocation is a future feature.
- Homeworld-preset changes to the FoodAllocationEditor title (minor; PROJ-289 may update it to use `economy.primary_resource` but it's not the focus).

## Key Files

| Component | File Path |
|-----------|-----------|
| Per-species sub-block | `game/ui/screens/strategy_detail_fmt.py` |
| Per-resource grid | `game/ui/panels/planet_report_panel.py` |
| Facade read | `game/strategy/facade/strategy_session_facade.py` (unchanged — consumer of PROJ-288's method) |

## Related Documents
- [design.md](design.md) — Rendering design + layout sketches
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-286 | Dependency — multi-resource `population_consumption` drives per-resource upkeep column values |
| PROJ-287 | Dependency — `race_registry` resolves race_name for display |
| PROJ-288 | Dependency — `ColonyDemographicView` + `PlanetEconomyProjector` are the data sources |
| PROJ-290 | Sibling — shares the `ColonyDemographicView` / projector; PROJ-289 handles planet report, PROJ-290 handles treasury + uncolonized |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Manual scenario:
  - [ ] Open a colonized planet with 2 species → see 2 indented sub-blocks; each has 4 metric lines.
  - [ ] Species sub-blocks ordered largest-first.
  - [ ] Resource grid shows 4 numeric columns per resource row.
  - [ ] Food resource (organics) row shows non-zero upkeep; metals row shows 10% of organics upkeep; radioactives shows 1%; non-food resources (e.g. vapors, exotics) show 0 upkeep.
  - [ ] Net = harvest - upkeep - yard for every row.
- [ ] User verified end-to-end.
