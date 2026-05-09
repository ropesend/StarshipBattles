# PROJ-392 Implementation Review

**Review date:** 2026-05-09  
**Reviewer:** Codex  
**Verdict:** **Fail - not audit-clean**

PROJ-392 passes the project audit-readiness script and most wrapper-removal goals appear implemented, but Task 2.9 left a production New Game setup path calling a static wrapper that was deleted. Focused tests are green, which makes this a coverage gap rather than a false positive.

## Validation Result

`python Projects/scripts/validate_audit_ready.py PROJ-392` passed.

Notable warning:
- `Projects/projects_index.md:14` still lists PROJ-392 as `Planning` even though the project plan marks all phases complete.

Phase validation:
- `python Projects/scripts/validate_phase.py PROJ-392 1` passed with 1 warning: Task 1.1 has empty Notes.
- `python Projects/scripts/validate_phase.py PROJ-392 2` passed with 10 warnings: every Phase 2 task has empty Notes.

## Tests And Checks Run

- `pytest tests/ -k new_game_setup` -> 102 passed.
- `pytest tests/unit/strategy/services/test_galaxy_pathfinding_service.py tests/unit/strategy/pathfinding/test_basic_paths.py tests/unit/strategy/pathfinding/test_edge_cases.py tests/unit/strategy/data/test_pathfinding_shim_scope.py` -> 52 passed.
- Focused Phase 2 bundle:
  `pytest tests/unit/ui/screens/test_strategy_renderer.py tests/unit/ui/screens/test_strategy_renderer_animation.py tests/unit/ui/screens/test_strategy_renderer_public_api.py tests/unit/quickstart/test_quickstart_builder.py tests/unit/quickstart/test_quickstart_races.py tests/unit/quickstart/test_quickstart_designs.py tests/unit/strategy/test_quickstart_builder.py tests/unit/simulation/entities/stat_contributors/test_command.py tests/unit/simulation/entities/stat_contributors/test_registry.py tests/unit/ui/screens/test_empire_build_queue_window.py tests/unit/ui/screens/test_empire_build_queue_formatter.py tests/unit/ui/screens/builder/test_stat_getters.py tests/unit/ui/screens/test_strategy_menu_actions.py tests/unit/test_app_public_api.py tests/unit/test_app_delegators.py` -> 717 passed.
- Phase 1 focused suite:
  `pytest tests/unit/ui/test_battle_panels.py tests/unit/ui/test_battle_panels_extended.py tests/unit/ui/test_battle_panels_characterization.py tests/fixtures/test_race_setup_ui_builders.py` -> 69 passed.
- Static probe:
  `hasattr(NewGameSetupScreen, "generate_default_save_name") == False`;
  `hasattr(NewGameSetupScreen, "validate_save_name") == False`;
  `hasattr(NewGameSetupController, "generate_default_save_name") == True`.
- Targeted `rg` checks for deleted wrapper definitions and residual legacy symbol text.

I did not rerun the full sharded suite. The project plan records a prior full sharded run with baseline-preserving unrelated failures, and focused review tests were more practical for this pass.

## Plan Goals Vs Actual Implementation

Phase 1 goals are functionally met:
- `_priority_sort_key` was removed from `game/simulation/entities/ship_stats.py`.
- `RaceSetupScreen.name_input` placeholder removal appears complete for the target screen.
- `ShipStatsPanel.expanded_ships` alias was removed, with tests migrated to `_expanded_ids`.

Phase 2 goals are mostly met:
- Strategy renderer image-load wrappers are gone.
- Quickstart builder path wrappers are gone from production.
- `GalaxyPathfindingService.find_path_deep_space` was removed and internal service logic now calls `hex_linedraw` directly.
- `priority_sort_key` wrapper was removed and code uses `lookup_crew_priority`.
- `Game.menu_scene` is now the public app-level property used by app handlers.
- `get_asset_manager()` alias is gone.
- `_get_sector_text` instance wrapper is gone.
- `_get_total_crew_requirement` is now public `get_total_crew_requirement`; the dispatch key remains stable for JSON layouts.
- **Task 2.9 is incomplete in production:** `NewGameSetupScreen._create_ui()` still calls the deleted `self.generate_default_save_name()` wrapper.

## Literal Checklist Execution

The checklists are fully checked, but several checked verification claims do not match the current repository:

- `phase_2_checklist.md:90-93` claims the NewGame setup wrapper callers were identified/migrated. `game/ui/screens/new_game_setup_screen.py:348` is still an unmigrated production caller.
- `phase_2_checklist.md:39` claims `grep -rn "find_path_deep_space" .` returns zero hits. It does not, and should not: `game/strategy/data/pathfinding.py:40-42` still defines the free-function shim, and `tests/unit/strategy/data/test_pathfinding_shim_scope.py:1-20` says this shim is deliberately pinned.
- `phase_2_checklist.md:84` claims `_get_total_crew_requirement|get_crew_required` returns zero hits. The function rename was done, but the legacy JSON dispatch key remains intentionally present in `game/ui/screens/builder/stat_getters.py:38-43` and `game/ui/screens/builder/stat_getters.py:394-397`, and data files still use `"get_crew_required"`.
- `phase_2_checklist.md:48` claims `priority_sort_key` has zero hits under `game/`. The wrapper definition is gone, but `game/simulation/entities/stat_contributors/command.py:13-15` still mentions the deleted private helper in a historical docstring.
- `phase_2_checklist.md:57` claims `\._menu_scene` has zero hits under `game/ tests/`. `game/screen_router.py:99-103` and later router internals still use `_menu_scene`. This is probably acceptable because the task was about the app-level public property, but the checklist assertion was overbroad.

## Findings

### High: New Game setup still calls a deleted screen static wrapper

**Evidence:** `game/ui/screens/new_game_setup_screen.py:348`, `game/ui/screens/new_game_setup_screen.py:701-706`, `game/ui/screens/new_game_setup_ui_builder.py:37-38`.

Task 2.9 deleted `NewGameSetupScreen.generate_default_save_name`, and the screen now explicitly documents that callers should use `NewGameSetupController.generate_default_save_name(...)` directly. However, the production UI creation path still runs:

```python
self.save_name_input.set_text(self.generate_default_save_name())
```

`NewGameSetupUiBuilder.build()` calls `screen._create_ui()`, so a normal production construction path reaches that call after `UIWindow` initialization. The static probe confirms `NewGameSetupScreen` no longer has `generate_default_save_name`, while the controller does. This will raise `AttributeError` when the live New Game setup UI reaches the save-name initialization path. The focused `new_game_setup` suite passing indicates the tests do not cover production widget construction after this wrapper deletion.

Required fix: change the call to `NewGameSetupController.generate_default_save_name()` or route through an injected controller method, and add coverage that exercises `_create_ui()` or the production builder path far enough to catch missing screen static wrappers.

### Low: Pathfinding deletion checklist conflicts with the pinned pathfinding shim

**Evidence:** `Projects/active_projects/PROJ-392/phase_2_checklist.md:36-39`, `game/strategy/data/pathfinding.py:40-42`, `tests/unit/strategy/data/test_pathfinding_shim_scope.py:1-20`.

The actual code change removed `GalaxyPathfindingService.find_path_deep_space`, which matches the narrow implementation goal. The checklist's zero-hit verification is wrong because the free-function shim is intentionally retained and guarded by PROJ-377. This is not a code failure, but it means the literal checklist cannot be trusted as written.

### Low: Checklist zero-hit assertions miss required data/API strings

**Evidence:** `Projects/active_projects/PROJ-392/phase_2_checklist.md:80-84`, `game/ui/screens/builder/stat_getters.py:38-43`, `game/ui/screens/builder/stat_getters.py:394-397`, `data/stats_layout.json:284`, `data/stats_sections.json:274`.

The wrapper function `get_crew_required(ship)` is gone, but the JSON getter key `get_crew_required` remains the stable data contract and maps to `get_total_crew_requirement`. That implementation looks correct, but the checklist's "zero hits" criterion was too broad and would have pushed the project toward a data-contract break if followed literally.

### Low: Project administrative state is stale

**Evidence:** `Projects/projects_index.md:14`, phase validation warnings.

`validate_audit_ready.py` passes, but the project index still says `Planning`, and all completed tasks have empty Notes warnings. This does not block runtime behavior, but it weakens the project audit trail.

## Plan Gaps And Missed Assumptions

- The plan assumed there were only two `NewGameSetupScreen.validate_save_name` / `generate_default_save_name` callers, likely tests. It missed the unqualified instance call in `NewGameSetupScreen._create_ui()`.
- The plan treated symbol-level grep zero hits as a universal success criterion. That was not appropriate for names that survive as pinned shims, JSON dispatch keys, historical docstrings, or internals outside the target class.
- The pathfinding task did not account for PROJ-377's pinned shim contract before asking for zero `find_path_deep_space` hits.
- The stat getter task did not distinguish removing a Python wrapper function from preserving a JSON layout getter key.

## Residual Risks

- Full sharded regression was not rerun during this review; I relied on focused tests plus the project's recorded prior sharded baseline.
- UI construction tests are still too mock-heavy to catch missing production-only screen methods. The New Game issue is direct evidence of that blind spot.
- Several verification checkboxes rely on grep wording that would be easy for future agents to over-interpret.

