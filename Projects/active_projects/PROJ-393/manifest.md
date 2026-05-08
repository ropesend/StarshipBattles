# PROJ-393 File Manifest

## Files

| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/simulation/combat/formation.py` | Production | Edit | LEG-03-002 — delete legacy snap comment at line 357 (keep code) |
| `game/strategy/combat/spec_compiler.py` | Production | Edit | LEG-03-003 — delete legacy comment at line 462 |
| `game/strategy/systems/save_game_service.py` | Production | Edit | LEG-02-005 — delete historical `# legacy` comment at line 68 |
| `game/context.py` | Production | Edit | LEG-02-017 — update/remove stale `# PROJ-258` comment at line 13 |
| `game/run_loop.py` | Production | Edit | LEG-02-002 — delete legacy `handle_input` branch at line 205 |
| `game/ui/research/research_scene.py` | Production | Edit | LEG-02-002 — implement `IScene.handle_event` |
| `game/ui/screens/galaxy_test/screen.py` | Production | Edit | LEG-02-002 — implement `IScene.handle_event` |
| `game/strategy/validation/planet_order_validator.py` | Production | Edit | LEG-03-004 + LEG-03-005 — delete activate (66-75) + deactivate (113-125) fallbacks |
| `game/ui/panels/build_queue_drag_handler.py` | Production | Edit | LEG-03-006 — delete test-fallback branch (lines 210-212) |
| `game/ui/screens/empire_build_queue_window.py` | Production | Edit | LEG-03-007 — delete test-fallback branch (lines 428-429) |
| `game/strategy/engine/planet_action_engine.py` | Production | Edit | LEG-02-003 — delete `'PlanetaryShield'` hardcoded fallback (line 366) |
| `game/strategy/engine/commands/__init__.py` | Production | Edit | LEG-02-004 — delete `fleet_id` field on 3 command classes |
| `game/ui/screens/strategy_detail_fmt.py` | Production | Edit | LEG-02-006 — delete `view is None` branch (lines 254-256) |
| `game/ui/screens/build_queue_helpers.py` | Production | Edit | LEG-02-013 — replace module-level `ResourceCatalog.from_json()` |
| `game/ui/screens/strategy_ui.py` | Production | Edit | LEG-02-013 — same |
| `game/ui/screens/battle_screen.py` | Production | Edit | LEG-03-023 — delete 6 Combat Lab instance vars (lines 117-125) |
| `game/ui/renderer/sprites.py` | Production | Edit | LEG-03-024 — confirm-then-delete `_LEGACY_PATTERN` (line 14) |
| `game/strategy/engine/order_handlers/transfer_branches.py` | Production | Edit | LEG-04-004 — delete `populations[0]` Legacy/Default fallback (lines 107-108) |
