# PROJ-464 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/ui/screens/strategy_screen.py | Production | Narrow 15 delegate properties (Phase 1.1) |
| game/ui/screens/strategy_renderer.py | Production | Renderer-scene Protocol seam for 13 props (Phase 1.2) |
| game/ui/screens/battle_screen.py | Production | Narrow delegate properties (Phase 1.3) |
| game/ui/screens/planet_list_filters.py | Production | Narrow 7 filter functions (Phase 1.4) |
| game/ui/screens/star_list_filters.py | Production | Narrow 6 filter functions (Phase 1.4) |
| game/ui/screens/builder/left_panel.py | Production | Narrow get_add_count (Phase 1.5) |
| game/ui/screens/builder/modifier_logic.py | Production | Narrow calculate_snap_value (Phase 1.5) |
| game/ui/screens/builder/weapons_viewmodel.py | Production | Narrow hovered_weapon/calc_damage_at_range (Phase 1.5) |
| game/ui/components/table/column_manager.py | Production | Tighten _columns value type (Phase 1.5) |
| game/ui/assets/ship_theme_manager.py | Production | Type expected; remove index ignore (Phase 1.6) |
| game/ui/panels/race_theme_gallery.py | Production | Fix override return type; remove ignore (Phase 1.6) |
| game/app_bootstrap.py | Production | Add _replay_combat_lab_fallback return (Phase 1.7) |
| game/ui/screens/atmosphere_target_editor.py | Production | Add _button_handlers return (Phase 1.7) |
| game/ui/screens/radiation_shield_editor.py | Production | Add _button_handlers return (Phase 1.7) |
| game/ui/screens/water_target_editor.py | Production | Add _button_handlers return (Phase 1.7) |
| game/ui/screens/test_lab/details/validation.py | Production | Add _phase_color return (Phase 1.7) |
| game/ui/screens/transfer_mass_preview.py | Production | Add _get_catalog return (Phase 1.7) |
| game/core/profiling.py | Production | Fix save_history implicit Optional (Phase 1.8; Shard-03 UI-context finding) |
| game/core/resources.py | Production | Fix implicit Optional (Phase 1.8; Shard-03 UI-context finding) |
| game/ui/renderer/sprites.py | Production | Fix implicit Optional (Phase 1.8) |
| game/ui/screens/builder/stat_getters.py | Production | Bulk-narrow ~40 display getters (Phase 2.1) |
| game/ui/screens/builder/stat_rows_dynamic.py | Production | Bulk-narrow 23 functions (Phase 2.1) |
| game/ui/pygame_gui_patch.py | Production | Add _to_tuple return type (Phase 2.2) |
| game/app.py | Production | Top-level strict migration; scene proxies stay Any (Phase 3.1) |
| game/run_loop.py | Production | Top-level strict migration (Phase 3.1) |
| game/screen_router.py | Production | Top-level strict migration (Phase 3.1) |
| game/ui/ (mypy config) | Production | Adopt --strict; pygame_gui handling (Phase 3.2) |
