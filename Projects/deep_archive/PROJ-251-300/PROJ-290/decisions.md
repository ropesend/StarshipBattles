# PROJ-290: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized | Starting point for Empire Treasury + Uncolonized Habitability UI |
| 2026-04-18 | Treasury populace upkeep: one empire-wide aggregated number (per resource). NOT per-colony. | User confirmed 2026-04-18: "just one number for all colonies". |
| 2026-04-18 | Populace upkeep covers ALL resources in `economy.population_consumption` (organics + metals + radioactives after PROJ-286). User confirmed flexibility for future schema changes. | "prepare for any alteration to the .json data files" — iterate the dict; no hardcoding. |
| 2026-04-18 | Uncolonized habitability section: 0-100 integer score, one line per species, sorted best-fit first | User confirmed 2026-04-18: "calculated value from 0 to 100 where 0 means totally uninhabitable, and 100 should mean everything matches the species preferences". "Order from best fit to worst fit". |
| 2026-04-18 | Species set = `empire.resident_species()` (from PROJ-287): race_ids with count >= 1 anywhere in empire colonies | User confirmed. Excludes extinct species. |
| 2026-04-18 | Hide the Treasury populace-upkeep row when all values are zero | Avoids visual noise in a fresh game with no populations yet. Comes back automatically when populations grow. |
| 2026-04-18 | Score formula: `int(round(score_planet_for_race(planet, race_config) * 100))` | Direct reuse of PROJ-283's habitability formula. Rounded to integer for display. Raw float is available via the helper for any other consumer. |
| 2026-04-18 | Race display name resolution: `race_config.race_name` → `race_config.name` → `race_id` | Consistent with other UI surfaces (e.g. FoodAllocationEditor per PROJ-284 Phase 4). |
| 2026-04-18 | `EmpireEconomySnapshot` gains `total_population_upkeep: Dict[str, float]` field | Minimal change. Existing treasury panel already reads `snapshot.expenses` / `.production`. Adding one field + one row keeps the refactor small. |
| 2026-04-18 | Skip missing-race-config entries silently (save-drift defense) | Same approach as PROJ-285's `planet_habitability_multiplier`. A race file that disappeared mid-game shouldn't crash the UI. |
| 2026-04-18 | Blocked on PROJ-286 + PROJ-287 + PROJ-288 | Hard dependencies. PROJ-286 provides the multi-resource upkeep source. PROJ-287 provides `resident_species()` + race_registry. PROJ-288 provides projector for empire-wide aggregation. |
| 2026-04-18 | PROJ-289 and PROJ-290 can run in parallel ONCE their shared deps (286/287/288) land. Coordinate on planet-report-panel layout changes | Both touch `planet_report_panel.py`. PROJ-289 adds per-species sub-blocks (colonized) + resource grid; PROJ-290 adds uncolonized habitability list. Different branches in the same panel; update in harmony. |
