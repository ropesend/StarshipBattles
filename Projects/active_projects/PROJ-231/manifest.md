# PROJ-231 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/facade/dto/system_dto.py` | Production | Expand StarInfo DTO with all star attributes + system context |
| `game/strategy/facade/strategy_session_facade.py` | Production | Add `get_all_stars()` query method |
| `game/ui/screens/star_list_window.py` | Production | **NEW** — Main UIWindow class |
| `game/ui/screens/star_list_filters.py` | Production | **NEW** — gather, filter, sort logic |
| `game/ui/screens/star_list_filter_manager.py` | Production | **NEW** — Filter state management |
| `game/ui/screens/star_list_sidebar.py` | Production | **NEW** — Sidebar UI builder |
| `game/ui/screens/star_data_source.py` | Production | **NEW** — ITableDataSource implementation |
| `game/ui/screens/star_list_presets.py` | Production | **NEW** — Preset save/load |
| `game/ui/screens/strategy_panel_manager.py` | Production | Add `btn_stars` to StrategyWidgets + top bar |
| `game/ui/screens/strategy_ui.py` | Production | Add `btn_stars` unpack + `open_star_list()` delegation |
| `game/ui/screens/strategy_window_manager.py` | Production | Add `open_star_list()`, navigation callback, window ref |
| `game/ui/screens/strategy_event_router.py` | Production | Route `btn_stars` click, add modal/blocking checks |
| `tests/unit/ui/screens/test_star_list_filters.py` | Test | **NEW** — Unit tests for star filter/sort logic |
| `tests/unit/strategy/facade/test_star_info_dto.py` | Test | **NEW** — Unit tests for enriched StarInfo DTO |
