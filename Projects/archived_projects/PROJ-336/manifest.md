# PROJ-336 — File Manifest

## Production files (in scope, READ-ONLY for this project)

| File | LOC | Existing coverage | New test file |
|---|---:|---|---|
| `game/strategy/services/fleet_navigation_service.py` | 759 | ~74 unit tests in `tests/unit/strategy/fleet_navigation/` (5 files); `test_fleet_navigation_action_timing.py` (591 LOC); `test_fleet_navigation_mutual_pursuit.py` (174 LOC); 3 integration files | `tests/unit/strategy/services/test_fleet_navigation_gaps.py` (NEW — **gap-fill only**) |
| `game/strategy/services/system_destroyer.py` | 179 | 1 integration file (`test_system_destruction.py`, 203 LOC, happy-path only) | `tests/unit/strategy/services/test_system_destroyer.py` (NEW) |
| `game/strategy/services/fleet_cargo_projector.py` | 64 | None | `tests/unit/strategy/services/test_fleet_cargo_projector.py` (NEW) |
| `game/strategy/services/stabilizer_registry.py` | 119 | 1 integration file (`test_stabilizer_blocks_superweapon.py`, 340 LOC) | `tests/unit/strategy/services/test_stabilizer_registry.py` (NEW) |

## Cross-project file overlap

Per master plan §"File-overlap matrix": zero overlap with PROJ-331..335, 337..340.
Confirmed: no other project touches `game/strategy/services/` files in the
above set.

## Production-side imports the new tests will mock or stub

| Import | Source | Mock strategy |
|---|---|---|
| `find_hybrid_path`, `strip_start_hex`, `calculate_intercept_point` | `game.strategy.data.pathfinding` | Use real implementations on a small synthetic galaxy where possible; `monkeypatch` only when isolating control flow (e.g. forcing `find_hybrid_path` to return `None`). |
| `find_abilities_in_scope` | `game.strategy.services.strategic_ability_scanner` | `monkeypatch` to a stub returning `True`/`False` per (scope, empire, ability_name) — see Decision D-005. |
| `ActionTimeResolver.resolve_action_time` | `game.strategy.services.action_time_resolver` | Already exercised heavily by `test_fleet_navigation_action_timing.py`; mock with `monkeypatch` for the 1-2 gap tests touching `_get_action_time_for_projection`. |
| `Galaxy._global_hex_warp_points`, `Galaxy.get_system_by_name` | `game.strategy.data.galaxy` | Build minimal real `Galaxy` + 2 `StarSystem` + 2 `WarpPoint` for `_resolve_warp_exit` corner cases. |

## Tooling

- pytest (markers per existing strategy-services convention; no new marker needed)
- `Tools/lint_test_files.py` for repo-standard test linting
- No new fixtures expected; existing `tests/fixtures/` covers what's needed (mock_planet, etc.)
