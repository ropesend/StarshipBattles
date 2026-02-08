# PROJ-71: Strategy Layer Hotkey System

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-71` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-71 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Core Data Model + InputMapper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Strategy Screen Integration | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Sub-Window Hotkey Integration | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Keybindings Settings Scene | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Verification & Polish | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 4 - Keybindings Settings Scene
**Last Action:** Completed Phase 3 - Sub-Window Hotkey Integration (25 new tests)
**Next Action:** Begin Phase 4 - Build the full-screen keybinding editor scene
**Blockers:** None
**Context for Next Agent:** Phase 3 complete. InputMapper wired into all sub-windows: FleetOrdersWindow (Ctrl+Z undo, Del clear, tooltips), BuildQueueScreen (ESC close, A add, Del remove, 1-4 categories, tooltips), TransferDialog (Enter confirm, ESC cancel, tooltips), BuildQueueListWindow (ESC close). StrategyUI passes _mapper to all sub-window constructors. StrategyScreen passes input_mapper to BuildQueueScreen in both on_build_yard_click and on_fleet_build_click. Full suite: 6776 passed, 1 pre-existing failure.

## Overview
All keyboard shortcuts in the strategy layer are currently hardcoded. This project creates a centralized, data-driven keybinding system with a JSON defaults file, user override persistence, tooltip hints on buttons, and a full-screen keybinding editor scene. Every button and command in the strategy layer and its sub-screens gets a bindable hotkey.

## Goals
- Replace all hardcoded `event.key == pygame.K_*` checks with a centralized InputMapper
- Create `data/default_keybindings.json` with all default bindings
- Persist user keybinding overrides to `output/settings/keybindings.json`
- Show hotkey hints via tooltips on all strategy layer buttons
- Build a full-screen keybinding editor scene with rebinding, conflict detection, and reset
- Add hotkey support to all sub-windows (Fleet Orders, Build Queue, Transfer Dialog, etc.)

## Scope
**In:**
- Strategy screen top bar buttons (Planets, Empire, Research, Design, Build Queues, Save Game, End Turn)
- Strategy screen navigation (Prev/Next Colony/Fleet)
- Fleet command hotkeys (Move, Join, Colonize, Transfer, Cancel)
- Camera zoom shortcuts (Galaxy view, System view)
- Screenshot shortcuts (F12, F11)
- Global shortcuts (ALT+X exit, F9 profiler)
- Sub-window buttons: Fleet Orders (Undo, Clear), Build Queue (Close, Add, Remove, Categories), Transfer Dialog (Confirm, Cancel)
- Build Queue List Window (Close)
- Detail panel buttons (Colonize, Build Yard, Orders, Fleet Report, Build Fleet)
- Keybinding editor scene (full IScene implementation)

**Out:**
- Design Workshop hotkey integration (future PROJ)
- Battle screen hotkeys (separate scope)
- Wiring the "Controls" button to open the editor (PROJ-72)
- Planet List Window internal column sorting/filter hotkeys (too many dynamic elements)
- Fleet Report Window internal filter hotkeys (same reason)

## Key Files
| Component | File Path |
|-----------|-----------|
| InputAction enum + KeyBinding | `game/core/input_actions.py` (new) |
| InputMapper service | `game/core/input_mapper.py` (new) |
| Default keybindings | `data/default_keybindings.json` (new) |
| Keybindings editor scene | `game/ui/screens/keybindings_scene.py` (new) |
| Path constants | `game/core/paths.py` |
| Game states | `game/core/constants.py` |
| App startup/DI | `game/app.py` |
| Strategy screen coordinator | `game/ui/screens/strategy_screen.py` |
| Strategy input handler | `game/ui/screens/strategy_input_handler.py` |
| Strategy UI (buttons/tooltips) | `game/ui/screens/strategy_ui.py` |
| Fleet orders window | `game/ui/screens/fleet_orders_window.py` |
| Build queue screen | `game/ui/screens/build_queue_screen.py` |
| Transfer dialog | `game/ui/screens/transfer_dialog.py` |
| Build queue list window | `game/ui/screens/build_queue_list_window.py` |
| JSON utilities | `game/core/json_utils.py` (reuse) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12` - baseline 6519)
- [ ] New unit tests for InputAction, KeyBinding, InputMapper
- [ ] Manual verification of all hotkeys in strategy layer
- [ ] Manual verification of keybinding editor (rebind, save, load, reset)
- [ ] Audit passed
- [ ] User verified
