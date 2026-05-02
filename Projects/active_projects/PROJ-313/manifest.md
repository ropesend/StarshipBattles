# PROJ-313 File Manifest

> Generated during /claude-proj-start. Used by /claude-proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| **Phase 1: Foundation** | | |
| `game/ui/screens/strategy_modal_window.py` | Production (NEW) | New base class `StrategyModalWindow(UIWindow)` |
| `game/ui/screens/strategy_window_manager.py` | Production | Add `_modals` list + `register_modal` / `unregister_modal` / `iter_live_modals` |
| `tests/unit/ui/screens/test_strategy_modal_window.py` | Test (NEW) | Base class invariants: register-on-init, deregister-on-kill, GC reaping, idempotent kill, multi-manager isolation |
| **Phase 2: Router OR-bridge** | | |
| `game/ui/screens/strategy_event_router.py` | Production | OR-bridge `has_modal_open` and `_is_blocking_ui_element_at` |
| `tests/unit/ui/screens/test_strategy_event_router.py` | Test | Add OR-bridge invariant tests |
| **Phase 3: Event-listener-only window migrations (6 windows)** | | |
| `game/ui/screens/orders_window.py` | Production | Subclass `StrategyModalWindow`, accept `window_manager` kw |
| `game/ui/screens/transfer_dialog.py` | Production | Same |
| `game/ui/screens/cargo_quick_dialog.py` | Production | Same |
| `game/ui/screens/planet_selection_window.py` | Production | Same |
| `game/ui/screens/system_selection_window.py` | Production | Same |
| `game/ui/screens/fleet_selection_window.py` | Production | Same |
| `game/ui/screens/strategy_window_manager.py` | Production | Drop 6 slot fields |
| `game/ui/screens/strategy_event_router.py` | Production | Drop 6 clauses from each scan + 6 branches from `_handle_window_close` |
| `game/ui/screens/strategy_windows/orders_window_ctrl.py` | Production | Update spawn site to pass `window_manager` |
| `game/ui/screens/strategy_windows/transfer_dialogs.py` | Production | Update 2 spawn sites |
| `game/ui/screens/strategy_windows/selection_prompts.py` | Production | Update 3 spawn sites |
| **Phase 4: Dual-cleanup window migrations (3 windows)** | | |
| `game/ui/screens/empire_build_queue_window.py` | Production | Subclass + drop kill override + drop on_close_callback param |
| `game/ui/screens/event_log_window.py` | Production | Same |
| `game/ui/screens/empire_panel_window.py` | Production | Same — preserve settings_window handling |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | Production | Drop EmpireBuildQueue `_on_closed`, update spawn |
| `game/ui/screens/strategy_windows/event_log_window_ctrl.py` | Production | Drop `_on_closed`, update spawn |
| `game/ui/screens/strategy_windows/empire_panel_ctrl.py` | Production | Drop EmpirePanel `_on_closed` (NOT settings_window's) |
| `game/ui/screens/strategy_window_manager.py` | Production | Drop 3 slot fields |
| `game/ui/screens/strategy_event_router.py` | Production | Drop 3 clauses from each scan + 3 branches |
| **Phase 5: Registrar-callback-only window migrations (5 windows)** | | |
| `game/ui/screens/planet_list_window.py` | Production | Subclass + drop kill override + drop on_close_callback param |
| `game/ui/screens/star_list_window.py` | Production | Same |
| `game/ui/screens/build_queue_list_window.py` | Production | Same |
| `game/ui/screens/fleet_report_window.py` | Production | Same |
| `game/ui/screens/planet_abilities_window.py` | Production | Same — the BUG-121 reference impl, kill override removed |
| `game/ui/screens/strategy_windows/list_windows.py` | Production | Drop PlanetList + StarList `_on_closed`s, update spawns |
| `game/ui/screens/strategy_windows/build_queue_windows.py` | Production | Drop BuildQueueList `_on_closed`, update spawn |
| `game/ui/screens/strategy_windows/fleet_report_ctrl.py` | Production | Drop `_on_closed`, update spawn |
| `game/ui/screens/strategy_windows/planet_abilities_ctrl.py` | Production | Drop `_on_closed`, update spawn |
| `game/ui/screens/strategy_window_manager.py` | Production | Drop 5 slot fields |
| `game/ui/screens/strategy_event_router.py` | Production | Drop 5 clauses from each scan |
| **Phase 6: move_choice promotion** | | |
| `game/ui/screens/strategy_windows/move_choice_dialog.py` | Production | Promote inline UIWindow → MoveChoiceWindow class; update spawn |
| `game/ui/screens/strategy_window_manager.py` | Production | Drop `move_choice_window` slot field |
| `game/ui/screens/strategy_event_router.py` | Production | Drop clause from each scan + branch from `_handle_window_close` |
| **Phase 7: Untracked editor migrations (5 windows)** | | |
| `game/ui/screens/food_allocation_editor.py` | Production | Subclass StrategyModalWindow, accept window_manager kw |
| `game/ui/screens/atmosphere_target_editor.py` | Production | Same |
| `game/ui/screens/gravity_target_editor.py` | Production | Same |
| `game/ui/screens/water_target_editor.py` | Production | Same |
| `game/ui/screens/radiation_shield_editor.py` | Production | Same |
| `game/ui/screens/strategy_event_router.py` | Production | Update 5 spawn sites at lines ~197/234/254/274/294 |
| `tests/integration/ui/test_editor_click_blocking.py` | Test (NEW) | 5 click-blocking regression tests, parametrised across the editors |
| **Phase 8: Demolition + docs** | | |
| `game/ui/screens/strategy_event_router.py` | Production | Delete `_handle_window_close`, collapse scans to one-liners |
| `game/ui/screens/strategy_window_manager.py` | Production | Delete remaining migrated slot fields |
| `tests/unit/ui/screens/test_strategy_window_manager_public_api.py` | Test | Replace `TestModalSlotCleanupContract` with `TestStrategyModalWindowStructuralInvariant` |
| `tests/unit/ui/screens/test_modal_subclass_guard.py` | Test (NEW) | Static guard preventing direct `pygame_gui.UIWindow` subclassing |
| `docs/02_PATTERNS.md` | Doc | Mark Pattern #30 superseded; add Pattern #31; bump count + TOC + `Last verified:` |
| `docs/06_UI_STYLE_GUIDE.md` | Doc | New "Window Management" section pointing at `StrategyModalWindow`; bump `Last verified:` |
| `docs/01_ARCHITECTURE.md` | Doc | UI layer note pointing at the base class; bump `Last verified:` |
| `Projects/projects_index.md` | Tracking | Update PROJ-313 status to Complete on closeout |

## Notes

- `game/ui/screens/strategy_window_manager.py` and `game/ui/screens/strategy_event_router.py` are touched in EVERY phase 1-8. Parallel execution must serialise on these two files. The dual-track router OR-bridge keeps each commit green at 15893 tests.
- The 5 untracked editors (Phase 7) are the click-through-bug fix that motivated the project. Phase 7 is a behaviour-change phase: `has_modal_open()` newly returns True while these editors are open. Audit consumers of `has_modal_open()` before commencing Phase 7 (Task 7.1).
- `settings_window` (the only intentionally non-modal slot) is NOT migrated — it stays as a direct slot on `StrategyWindowManager`. Phase 4's `EmpirePanelWindow` migration must take care to preserve settings_window wiring.
- `_pending_confirmation_dialog` asymmetry is OUT OF SCOPE per user direction — separate ticket.
