# PROJ-292 File Manifest

> Used for parallel-execution conflict detection with PROJ-291.
> Update if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/planet_list_window.py | Production (MODIFY) | H1 — thread `view = facade.get_colony_demographic_view(planet.id)` into PlanetReportPanel construction at line 511 |
| game/ui/screens/build_queue_panel_factory.py | Production (MODIFY) | H1 — same pattern at line 181. BuildQueuePanel only shows colonized planets so this is high-value |
| game/strategy/services/empire_economy_service.py | Production (NEW) | M1 — service-layer facade exposing read-only `get_snapshot(empire) -> EmpireEconomySnapshot` over the engine-layer calculator |
| game/ui/panels/empire_treasury_panel.py | Production (MODIFY) | M1 — replace `from game.strategy.engine.empire_economy_calculator import EmpireEconomySnapshot` (line 19) with import from `game.strategy.services.empire_economy_service` |
| game/ui/screens/empire_panel_window.py | Production (MODIFY) | M1 — same import migration as line 18; ensure callers use `EmpireEconomyService.get_snapshot(empire)` instead of `EmpireEconomyCalculator(...).calculate(empire)` |
| game/ui/panels/planet_report_panel.py | Production (MODIFY) | H3 — narrow `except (AttributeError, Exception)` to `except AttributeError` (search for `text_colour` and the colour-setter try-block). m1 — document the asymmetric `update_planet` kwarg-fallback contract in the docstring |
| game/strategy/systems/race_library.py | Production (MODIFY) | M2 — optional add `auto_refresh_on_mtime: bool = False` kwarg to `CachedRaceRegistry.__init__` if user opts in (Phase 3 Task 3.3 decides) |
| game/strategy/facade/dto/colony_demographic_view.py | Production (MODIFY) | m4 — wrap `total_upkeep` with `MappingProxyType` in `__post_init__`; m5 — re-sort `species` largest-first in `__post_init__` |
| game/strategy/facade/strategy_session_facade.py | Production (MODIFY) | m6 — add `logger.warning("session has no economy_config; falling back to default")` in `_resolve_economy_config` |
| game/ui/screens/strategy_detail_fmt.py | Production (MODIFY) | m7 — document tie-break in `format_uncolonized_habitability_for_empire` docstring (no behaviour change unless user wants insertion-order) |
| Tools/test_sharded/test_sharded.py | Tool (MODIFY conditional) | m8 — verify `tests/integration/` is included in the sharded run; if not, add it |
| Projects/projects_index.md | Documentation (MODIFY) | m17 — delete the stray `w` from line 1 |
| docs/systems/strategy_layer.md | Documentation (MODIFY) | m13 — re-grep for `format_signed_float(rate * 100, 1)` and align docs to actual code; document the H1 view-threading completion |
| docs/04_SERVICES.md | Documentation (MODIFY) | M1 — add EmpireEconomyService to the service catalogue |
| Projects/active_projects/PROJ-292/MANUAL_SMOKE_CHECKLIST.md | Documentation (NEW) | m10 — single durable hand-off doc for the deferred manual UI smokes accumulated across PROJ-283..292 |
| tests/integration/strategy/test_projector_drain_matches_engine.py | Test (NEW) | H2 — integration test pinning that projector's yard-drain matches `ProductionEngine` actual drain for the same planet |
| tests/unit/strategy/systems/test_race_library.py | Test (MODIFY) | M2 — add `TestCachedRaceRegistryStaleness` class — pins the cache invalidation contract |
| tests/unit/strategy/services/test_empire_economy_service.py | Test (NEW) | M1 — tests the new facade's `get_snapshot` returns the same snapshot the engine-layer calculator would |
| tests/unit/ui/panels/test_planet_report_panel.py | Test (MODIFY) | H3 — test that mocking `cell.text_colour =` to raise `RuntimeError` propagates (not swallowed). m9 — UI assembly test asserting label count + no overlapping rects |
| tests/unit/ui/screens/test_planet_list_window.py | Test (MODIFY/NEW) | H1 — test that constructing PlanetListWindow + selecting a colonized planet causes `view = facade.get_colony_demographic_view(planet.id)` to be threaded into `PlanetReportPanel` |
| tests/unit/ui/screens/test_build_queue_panel_factory.py | Test (MODIFY/NEW) | H1 — same pattern |

## Cross-project file overlap with PROJ-291

| File | This project | PROJ-291 phase | Sequencing |
|------|--------------|---------------|-----------|
| game/strategy/engine/empire_economy_calculator.py | Wrapped by `empire_economy_service.py` (M1) — NOT modified directly | Phase 1 (C1 — 1-line fix to `total_expenses` aggregation) | **Sequential — PROJ-291 Phase 1 lands first.** PROJ-292 Phase 2 wraps the post-fix calculator |
| docs/systems/strategy_layer.md | Append-only doc updates (m13, H1 completion) | Phase 4 Task 4.3 (C3 retrofit doc note) | Sequential — both append; no merge conflict if order respected |
| docs/04_SERVICES.md | Append-only (M1 service entry) | Phase 4 Task 4.3 (race-registry consumer expansion) | Sequential — both append |
| Projects/projects_index.md | Status update (m17 typo fix) | Phase 4 Task 4.6 (PROJ-283..290 → Archived; PROJ-291 → Awaiting Verification) | Sequential — last writer wins; PROJ-292 m17 typo fix can land independently |
