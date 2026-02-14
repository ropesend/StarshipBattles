# PROJ-138: Warp Point System Selection Dialog

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-138` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-138 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Create SystemSelectionWindow | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Wire into StrategyUI | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-02-13 17:30
**Active Phase:** Plan Approved - Ready for Implementation
**Last Action:** Completed planning, swarm review, and plan refinement
**Next Action:** Begin Phase 1 - Create SystemSelectionWindow class and tests
**Blockers:** None
**Context for Next Agent:** Baseline is 11,906 tests passing. The call chain is fully wired — only the dialog window and its StrategyUI wiring are missing. Follow PlanetSelectionWindow pattern closely.

## Overview
When the "Open Warp Point" order is issued, the player needs to select a target star system. The call chain already exists in `strategy_superweapons.py` — it calls `_show_system_picker()` which tries `self.scene.ui.show_system_picker()`, but that method doesn't exist yet. Currently falls back to auto-selecting the first system. The warp point placement logic (near-end at fleet, far-end at orbit distance from target center) is already implemented in `superweapon_order_processor.py`.

This project implements the actual `SystemSelectionWindow` dialog — a scrollable, alphabetical list of star systems — and wires it into the UI delegation chain.

## Goals
- Provide a user-friendly system selection dialog for the Open Warp Point order
- Display systems alphabetically with hex distances from current system
- Follow existing UI patterns (PlanetSelectionWindow, StrategyWindowManager delegation)

## Scope
**In:**
- New `SystemSelectionWindow` UIWindow subclass
- Alphabetically sorted, scrollable system list with distances
- Confirm + Cancel buttons
- StrategyWindowManager `open_system_selection()` method
- StrategyUI `show_system_picker()` delegate method
- Unit tests for all new code

**Out:**
- Changes to warp point placement logic (already correct)
- Changes to command dispatch chain (already exists)
- Changes to `strategy_superweapons.py` (uses `hasattr` discovery, no changes needed)
- System filtering logic (already handled by `strategy_superweapons.py` lines 190-199)

## Key Files
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Reference dialog pattern | `game/ui/screens/planet_selection_window.py` | `PlanetSelectionWindow` |
| Call site (discovery) | `game/ui/screens/strategy_superweapons.py:379-394` | `_show_system_picker()` |
| Call site (invocation) | `game/ui/screens/strategy_superweapons.py:214` | `handle_open_warp_designation()` |
| Window manager | `game/ui/screens/strategy_window_manager.py` | `StrategyWindowManager` |
| UI delegate | `game/ui/screens/strategy_ui.py` | `StrategyUI` |
| Hex distance | `game/core/hex_math.py:115` | `hex_distance()` |
| Warp placement | `game/strategy/engine/superweapon_order_processor.py:261-275` | `process_open_warp_point()` |
| Existing WM tests | `tests/unit/ui/screens/test_strategy_window_manager.py` | `TestPlanetSelectionPrompt` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` - 11,906 tests pass (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Manual test: Open Warp Point order -> system dialog appears -> select -> confirm -> mission queued

### Final Verification
- [ ] New unit tests: `pytest tests/unit/ui/screens/test_system_selection_window.py tests/unit/ui/screens/test_strategy_window_manager.py -v`
- [ ] Regression: `pytest tests/unit/ui/test_superweapon_operations.py tests/unit/ui/screens/test_strategy_superweapons.py -v`
- [ ] Full suite: `pytest tests/ -n 12`
- [ ] Manual test: Start game, select fleet with Quantum Tunneling Inducer, press Open Warp Point hotkey, click a hex -> dialog appears with alphabetical system list -> select system -> confirm -> mission queued

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
