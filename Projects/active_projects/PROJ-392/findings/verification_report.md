# PROJ-392 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** Misc orphan wrappers + zero-call-site placeholders
**Batch summary:** 9 verified / 0 rejected / 1 uncertain (included) / 2 INFO (included) / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity |
|---|---|---|---|---|---|---|
| LEG-01-001 | `game/simulation/entities/ship_stats.py:503` | `_priority_sort_key` | `_cmd.priority_sort_key` | 0 | delete (0 call sites — single-PR deletion) | MINOR |
| LEG-01-006 | `game/ui/screens/strategy_renderer.py:217-245` | 3 `_load_*_image` wrappers | `_layer_load_*_image` | ~9 in same file | inline_at_callers_then_delete | MAJOR |
| LEG-01-007 | `game/strategy/quickstart_builder.py:39-45` | 2 `get_quickstart_*_dir` wrappers | `Paths.get_starter_*_dir` | 2 in same file | inline_at_callers_then_delete | MAJOR |
| LEG-01-009 | `game/strategy/services/galaxy_pathfinding_service.py:61-64` | `find_path_deep_space` static | `hex_linedraw` (`game.core.hex_math`) | 7 internal + 1 in `pathfinding.py` | inline_at_callers_then_delete | MAJOR |
| LEG-01-010 | `game/simulation/entities/stat_contributors/command.py:36-38` | `priority_sort_key` | `lookup_crew_priority` (registry) | 1 prod + 1 test | migrate_callers_then_delete | MAJOR |
| LEG-02-007 | `game/ui/screens/race_setup/screen.py:261` | `name_input = None` placeholder | (replaced by Identity panel) | 0 | delete (0 call sites — single-PR deletion) | MINOR |
| LEG-03-014 | `game/ui/screens/empire_build_queue_window.py:589` | `_get_sector_text` instance wrapper | module function `get_sector_text` | 1 | inline_at_callers_then_delete | MINOR |
| LEG-03-025 | `game/ui/panels/battle_panels.py:92` | `self.expanded_ships = self._expanded_ids` alias | `_expanded_ids` (internal) | 0 readers | delete (0 call sites — single-PR deletion) | MINOR |
| LEG-04-006 | `game/ui/screens/new_game_setup_screen.py:701-720` | `validate_save_name`, `generate_default_save_name` static wrappers | `NewGameSetupController` | 2 | migrate_callers_then_delete | MAJOR |

## Rejected

None for this bundle.

## Uncertain (resolved)

| ID | Symbol | Question | User decision |
|---|---|---|---|
| LEG-02-015 | `Game._menu_scene` private property used externally | Rename to public `menu_scene`, or keep the underscore for router-internals consistency? | **Include** — rename to public `menu_scene` |

## INFO (resolved)

| ID | Symbol | User decision |
|---|---|---|
| LEG-03-010 | `get_asset_manager()` 1-line alias to `get_default_asset_manager()` | **Include** — simple find-and-replace |
| LEG-03-016 | `get_crew_required(ship)` wraps private `_get_total_crew_requirement` | **Include** — rename helper to public, register directly |

## Out of Scope

None for this bundle. UNCERTAIN-excluded items (LEG-01-008, LEG-03-012, LEG-03-013) are recorded in the shared [bundling_decisions.md](bundling_decisions.md).
