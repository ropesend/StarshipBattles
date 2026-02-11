# PROJ-100: Cargo Transfer Orders Overhaul

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-100` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-100 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. T Key Input Mode + Keybinding Standardization | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Transfer Dialog Size Fix | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Drop/Load Quick Commands | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Tests for Drop/Load | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Planning Complete - Ready for Implementation
**Last Action:** Plan approved. All phase checklists created.
**Next Action:** Begin Phase 1 - Change T key to input mode pattern
**Blockers:** None
**Context for Next Agent:** Baseline is 7648 tests passing. The T key currently opens the transfer dialog immediately; we need to change it to an input-mode-then-click pattern like M/J/C. Phase 1 also standardizes keybindings (screen openers → Shift+Key, fleet commands → plain key).

## Overview
Overhaul the cargo transfer order system to improve usability: (1) Change T key to use input-mode-then-click pattern for hex selection before opening the transfer dialog, (2) Fix transfer dialog clipping by increasing window size, (3) Add Drop (D) and Load (L) quick commands with simplified cargo dialogs, (4) Standardize keybindings so screen/menu openers use Shift+Key and fleet commands use plain keys.

## Goals
- T key enters TRANSFER input mode; player clicks hex, then dialog opens with fleet + hex contents
- Transfer dialog large enough to not clip UI elements
- D key enters DROP_CARGO mode for quick cargo unloading
- L key enters LOAD_CARGO mode for quick cargo loading
- Consistent keybinding convention: plain keys = fleet commands, Shift+Key = screen openers

## Scope
**In:**
- T key flow change to input-mode-then-click
- Transfer dialog size increase (600x500 → 750x600)
- New D/L commands with CargoQuickDialog
- Keybinding standardization (P/E/R/D/B → Shift+P/E/R/D/B)
- New InputAction enums for FLEET_DROP_CARGO, FLEET_LOAD_CARGO
- Tests for all changes

**Out:**
- Fleet-to-fleet transfers (not supported by backend)
- New cargo types beyond "passengers"
- Changes to transfer order execution logic (FleetOrderProcessor)
- Changes to TransferValidator or TransferCommandHandler

## Key Files
| Component | File Path |
|-----------|-----------|
| Input handler | `game/ui/screens/strategy_input_handler.py` |
| Window manager | `game/ui/screens/strategy_window_manager.py` |
| Strategy UI | `game/ui/screens/strategy_ui.py` |
| Transfer dialog | `game/ui/screens/transfer_dialog.py` |
| Input actions enum | `game/core/input_actions.py` |
| Default keybindings | `data/default_keybindings.json` |
| CargoQuickDialog (NEW) | `game/ui/screens/cargo_quick_dialog.py` |
| Transfer command | `game/strategy/engine/commands.py` (reuse as-is) |
| Transfer handler | `game/strategy/engine/command_handlers.py` (no changes) |
| Transfer processor | `game/strategy/engine/fleet_order_processor.py` (no changes) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing (`pytest tests/ -n 12`)
- [ ] Manual test: T key → click hex → dialog opens at clicked hex
- [ ] Manual test: D key → click hex → quick drop dialog
- [ ] Manual test: L key → click hex → quick load dialog
- [ ] Manual test: Shift+P/E/R/D/B open screens, plain D/L work for fleet
- [ ] Audit passed
- [ ] User verified
