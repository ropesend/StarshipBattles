# PROJ-308 File Manifest

## Files

### EDIT (per Phase 1 triage)
| File | Type | Notes |
|------|------|-------|
| `game/core/event_logging.py` | Production | 2 sites (lines 53, 87) — likely justify (event handler error logging is fire-and-forget) |
| `game/core/roles.py` | Production | 1 site (line 233) — likely justify (role invalidation callback) |
| `game/ui/services/tkinter_utils.py` | Production | 1 site (line 100) — already commented; verify quality |
| `game/ui/panels/system_tree_panel.py` | Production | 2 sites (lines 393, 408) |
| `game/simulation/combat/telemetry.py` | Production | 1 site (line 312) — telemetry must never break host (justify) |
| `game/simulation/combat/combat_events.py` | Production | 1 site (line 161) — combat event handler error |
| `game/ui/panels/build_queue_controller.py` | Production | 1 site (line 217) |
| `game/ui/screens/food_allocation_editor.py` | Production | 1 site (line 109) |
| `game/ui/screens/battle_setup/controller.py` | Production | 1 site (line 56) |
| `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` | Production | 1 site (line 190) |
| `game/ui/screens/builder/stats_config.py` | Production | 1 site (line 241) |
| `game/ui/screens/species_selector_mixin.py` | Production | 1 site (line 124) |
| `game/ui/screens/strategy_detail_fmt.py` | Production | 2 sites (lines 319, 417) |
| `game/ui/screens/strategy_event_router.py` | Production | 4 sites (lines 215, 317, 329, 360) — UI event router (likely justify) |
| `game/ui/screens/strategy_fleet_command_router.py` | Production | 1 site (line 259) |
| `game/ui/screens/strategy_window_manager.py` | Production | 1 site (line 592) |
| `game/ui/screens/transfer_dialog.py` | Production | 1 site (line 426) |
| `game/ui/screens/workshop_data_reloader.py` | Production | 1 site (line 23) — already commented; verify quality |

### EDIT (convention enforcement)
| File | Type | Notes |
|------|------|-------|
| `CLAUDE.md` | Instructions | Strengthen "Specific exceptions over broad catches" rule with comment requirement |
| `docs/05_ERROR_HANDLING.md` | Docs | Add §Broad Catches section |

### NEW
| File | Type | Notes |
|------|------|-------|
| `Projects/active_projects/PROJ-308/findings/triage.md` | Project artifact | Phase 1 deliverable |

### EXPLICITLY EXCLUDED
- `tests/` directory broad-except clauses
- `Tools/` directory (handled in PROJ-297)
- `Reviews/` directory (handled in PROJ-297)
