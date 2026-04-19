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
| 1. Empire-wide populace upkeep aggregator + treasury line | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Uncolonized-planet per-species habitability list (0-100) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Docs + cleanup | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Planning complete; ready to begin Phase 1 (BLOCKED on PROJ-286, 287, 288)
**Last Action:** Project scaffolded.
**Next Action:** After PROJ-286, 287, 288 complete, Phase 1 Task 1.1 — add an empire-wide populace upkeep aggregator that sums `ColonyDemographicView.total_upkeep` across every empire colony, per resource.
**Blockers:**
- **PROJ-286** — multi-resource upkeep is the source value.
- **PROJ-287** — `Empire.resident_species()` drives the uncolonized-habitability iteration order (and registry resolves race_configs).
- **PROJ-288** — `ColonyDemographicView` + `PlanetEconomyProjector` provide the aggregatable data.
**Context for Next Agent:** Two independent UI additions sharing the same underlying data sources. Section 3 (treasury populace line) aggregates multi-resource upkeep across all empire colonies into a single expense row. Section 4 (uncolonized habitability) iterates `empire.resident_species()`, scores each against the viewed planet via `score_planet_for_race`, and renders a 0-100 list sorted best-to-worst. User wants a "calculated value from 0 to 100 where 0 means totally uninhabitable, and 100 should mean everything matches the species preferences" — so the UI multiplies `score_planet_for_race(planet, race) * 100` and rounds.

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
