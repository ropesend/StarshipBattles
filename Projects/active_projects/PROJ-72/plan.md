# PROJ-72: Strategy Menu Button

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-72` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-72 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create Menu Panel Component | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Wire Up Strategy UI | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Route Menu Actions | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Testing & Verification | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-07
**Active Phase:** Phase 3
**Last Action:** Phase 2 complete - Menu button replaces Save Game, panel management, click-outside/Escape, 24 tests
**Next Action:** Phase 3 - Route menu actions (on_menu_option handler in StrategyScreen, App.py scene callbacks)
**Blockers:** None

## Overview
Add a "Menu" button to the strategy view top bar that opens a dropdown panel with game management options: Save Game (moved from top bar), Load Game, Settings (placeholder), Controls (placeholder), Quit to Main Menu (with confirmation), and Quit Game. This gives players in-game access to all essential game management functions without needing keyboard shortcuts or closing the window.

## Goals
- Replace the standalone "Save Game" button in the top bar with a single "Menu" button
- Provide a dropdown panel with 6 options for game management
- Enable returning to main menu from strategy view (currently impossible without Alt+X)
- Enable loading a different save from within strategy view
- Placeholder entries for Settings and Controls (future features)

## Scope
**In:**
- Menu button replacing Save Game in the top bar
- Dropdown panel component with 6 option buttons
- Save Game action (reuses existing handler)
- Load Game action (opens SaveSelectionWindow from strategy)
- Settings / Controls dummy buttons showing "Coming Soon"
- Quit to Main Menu with confirmation dialog
- Quit Game (exits application)
- Click-outside and Escape to close panel

**Out:**
- Actual Settings or Controls screens (placeholder only)
- Menu button on other screens (battle, workshop, etc.)
- Keyboard shortcut for opening menu
- Save-before-quit logic (auto-save already happens each turn)

## Key Files
| Component | File Path |
|-----------|-----------|
| Menu Panel (NEW) | `game/ui/screens/strategy_menu_panel.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Strategy Screen | `game/ui/screens/strategy_screen.py` |
| App (scene handler) | `game/app.py` |
| Save Selection Window | `game/ui/screens/save_selection_window.py` (reused) |
| UIConfig | `game/core/config.py` (reference only) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ --testmon`)
- [ ] Manual testing: all 6 menu options work correctly
- [ ] Manual testing: panel open/close behavior correct
- [ ] Manual testing: no layout regressions in top bar
- [ ] User verified
