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
| 1. Per-species sub-block in planet info (habitability / happiness / growth) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Per-resource grid expansion (harvest / upkeep / yard / net) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Docs + cleanup | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** ALL 3 PHASES COMPLETE — awaiting user sign-off
**Last Action:** Phase 3 done. Updated `docs/systems/strategy_layer.md` with a "### Planet report panel UI surface (PROJ-289)" subsection at the end of §9 documenting the per-species sub-block layout, projection grid sign convention, happiness-category thresholds, the pure helpers (`_projection_grid_rows` + `_net_cell_color`), and the backward-compat fallback. Ran the full sharded suite: 15077 tests / 15063 passed / 14 failed in 138.7s — failures all pre-existing (13 PROJ-286 test debt in `test_food_allocation_editor.py` + 1 long-standing theme-bleed flake in `test_quickstart_builder.py`), neither a PROJ-289 regression. Net new across the project = 36 tests. Manual UI smoke (Task 3.3) deferred to user — headless agent can't launch pygame, and the Phase 2 layout-calibration note already flags potential vertical overflow at 5-8 active resources for user verification. `Projects/projects_index.md` PROJ-289 row advanced to "Awaiting Verification".
**Last Action (Phase 2 history):** Phase 2 done. Added two pure helpers to `game/ui/panels/planet_report_panel.py`: `_projection_grid_rows(view) -> List[tuple]` (header + per-resource cell-text rows; sign convention: harvest as-is, upkeep + yard rendered as drains via negation, net as-is) and `_net_cell_color(net) -> RGB` (HP_HEALTHY positive / HP_CRITICAL negative / TEXT_LIGHT zero — reuses existing colour palette for visual consistency). 11 new tests in `TestProjectionGridRows` + `TestNetCellColor` cover all sign + zero / multi-resource / empty-view cases. Wired the helpers into a new `_build_projection_grid` method that constructs the 5-cell header row + 1 row per resource as `UILabel` widgets in `self.resource_panel`, then appends a compact stockpile summary line below. `_build_resource_grid` now branches: `self.view is not None` → call `_build_projection_grid`; otherwise → keep the legacy stockpile grid unchanged (preserves backward compat for the 4 PlanetReportPanel callers that don't yet pass a view). Net-cell colour applied via `cell.text_colour = color; cell.rebuild()` inside a defensive try/except (pygame_gui colour-setter support varies; sign prefix already conveys sign). Combined PROJ-289 affected suite: 142/142 green.
**Last Action (Phase 1 history):** Phase 1 done. Verified the three blocker projects (PROJ-286/287/288) had landed before starting. Added `format_signed_float(value, decimals=1)` helper to `game/ui/utils/formatters.py` (handles `-0.0` quirk) + 8 new tests. Added `_happiness_category(happiness)` (Content >= 1.5, Settled >= 0.5, Unhappy below) to `game/ui/screens/strategy_detail_fmt.py` + 8 new tests. Extended `format_planet_info(planet, view=None)` with the per-species sub-block rendering when `view` is supplied; legacy single-line layout preserved when view is None (backward compat for tests + non-facade callers). Added `view` kwarg to both `PlanetReportPanel.__init__` AND `PlanetReportPanel.update_planet`, threaded through to `format_planet_info`. Wired the facade call from `game/ui/screens/strategy_detail_formatter.py::_show_planet_report` — `view = facade.get_colony_demographic_view(obj.id)` when `obj.owner_id is not None` and the scene exposes a facade. 9 new tests in `TestPerSpeciesSubBlock` cover legacy fallback, single + multi-species rendering, all metric formats, negative growth, ordering preservation, and category-label edge cases. Combined targeted suite (UI tests excluding the pre-existing `test_food_allocation_editor.py` PROJ-286 debt): **2377/2377 green**.
**Next Action:** None — hand back to user for sign-off, manual UI smoke (per Phase 3 Task 3.3 deferred), and to close PROJ-289 out in `projects_index.md`. PROJ-290 (Treasury + Uncolonized Habitability UI) is the last consumer in this DAG and is unblocked.
**Blockers:** None. All Phase 1-3 deliverables in place.
**Context for Next Agent:** The current resource grid is built via `_build_resource_grid` (around line 314 of `planet_report_panel.py`) and updated via `_update_resource_grid`. Phase 2 keeps the grid-construction idiom but rewrites the cells to show harvest/upkeep/yard/net using `format_signed_float`. Per design.md decision, a compact stockpile summary line stays BELOW the grid (single line, all resources) so per-turn current/max signal isn't lost. Resource colour helpers in `game/ui/colors.py` give the green/red tinting for Net column. The `view` kwarg is already plumbed into the panel (Phase 1) — Phase 2 just consumes `self.view.resource_projections` in `_update_resource_grid`.

**Phase 1 implementation notes for Phase 2's author:**
- `format_signed_float(value, decimals=1)` is now in `game/ui/utils/formatters.py` — use it for the per-cell harvest/upkeep/yard/net rendering.
- `view.resource_projections` is `Tuple[ResourceProjection, ...]`; each `ResourceProjection` has `resource_id`, `harvest`, `upkeep`, `yard`, `net` (frozen dataclass).
- Per design.md § "Resource grid rewrite" decisions: header row = (Resource, Harvest, Upkeep, Yard, Net); data rows = one per resource in projections; net cell colour = green positive / red negative / default zero.
- PROJ-288's `PlanetEconomyProjector` returns `{}` (empty dict → empty tuple) for empty queues + no harvesters + no upkeep — Phase 2 needs to handle "view exists but resource_projections is empty" gracefully (just render header row + the stockpile summary).
- The `_resource_grid_items: List` field on the panel tracks UI elements that need `.kill()` on rebuild — keep that pattern when restructuring the grid cells.

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
