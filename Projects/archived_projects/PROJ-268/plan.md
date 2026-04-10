# PROJ-268: FleetAuraManager Ship Removal Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-268` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-268 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Add `unregister_ship()` and Wire into `remove_ship()` | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-04-10
**Current Phase:** Complete
**Last Action:** Phase 1 complete. Added `unregister_ship()` to `FleetAuraManager` and wired it into `BattleEngine.remove_ship()`. 6 unit tests written and passing. Full suite: 14185 passed.
**Next Action:** Project complete — ready for archive.
**Blockers:** None
**Context for Next Agent:** All work done. One pre-existing failure in `test_build_order_command_handler.py` (unrelated import error for `create_auto_load_population_order`) — not introduced by this project.

## Overview
`BattleEngine.remove_ship()` does not call any `FleetAuraManager` method when a ship is removed from battle. When a ship providing fleet-scope abilities retreats (removed but still alive), its `AuraProvider` entries remain in `FleetAuraManager._providers` and its bonuses continue contributing to teammates via `_recalculate()`.

PROJ-243 added `register_ship()` for the add path but did not address the symmetric removal. This ticket adds `unregister_ship()` to `FleetAuraManager` and calls it from `BattleEngine.remove_ship()`.

## Goals
- **Aura cleanup on removal:** When a ship is removed from battle, its `AuraProvider` entries are removed from `FleetAuraManager._providers`
- **Bonus recalculation:** After removal, `_recalculate()` is called so remaining ships no longer receive bonuses from the removed ship
- **Test coverage:** Unit tests proving unregistration works correctly

## Scope
**In Scope:**
- `game/simulation/combat/fleet_aura_manager.py` — add `unregister_ship()` method
- `game/simulation/systems/battle_engine.py` — call `unregister_ship()` from `remove_ship()`
- Unit tests for the new method

**Out of Scope:**
- Any changes to `register_ship()` or `_recalculate()` internals
- UI changes
- Fingerprint cache optimization (minor, separate concern)

## Key Files Reference
| Component | File Path | Class/Function | Key Lines |
|-----------|-----------|----------------|-----------|
| Fleet aura manager | `game/simulation/combat/fleet_aura_manager.py` | `FleetAuraManager` | `register_ship()`: 121-135, `_providers`: set in `_scan_ship()` |
| Battle engine | `game/simulation/systems/battle_engine.py` | `BattleEngine.remove_ship()` | ~383-409 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-10 | Ticket created from PROJ-243 review | Symmetric counterpart to `register_ship()` — retreated ships should not provide fleet bonuses. |

## Related
- **PROJ-243** — Mid-Battle Ship Addition Fix (parent project that added `register_ship()`)
