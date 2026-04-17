# PROJ-250: Dual-Source Retreat Config Ambiguity

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-250` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
`_retreat_allowed()` uses OR logic: `mode_handler.can_retreat() or config.allow_retreat`. This means config can enable retreat even when mode handler says no, but the priority is undocumented and surprising. Also, `BattleConfig.isolated` is verified dead code (never read). Fix: document the priority clearly, add tests for the behavior, remove dead field.

## Goals
- Document the explicit priority: config can override mode handler to ENABLE (not disable)
- Add tests proving the priority behavior
- Remove dead `isolated` field from BattleConfig

## Scope
**In Scope:**
- Document `_retreat_allowed()` and `_reinforcements_allowed()` priority logic
- Add docstring to BattleConfig.allow_retreat explaining override behavior
- Remove BattleConfig.isolated (dead code)
- Add unit tests for priority behavior

**Out of Scope:**
- Changing the priority logic itself
- Changing retreat mechanics or UI
- Modifying mode handler implementations

## Current State
**Last Updated:** 2026-04-07 00:00
**Current Phase:** Planning Complete
**Next Action:** Implementation via Continue Project prompt
**Blockers:** None
**Context for Next Agent:** The OR logic is intentional — config.allow_retreat acts as an override to enable retreat in modes that normally don't allow it (e.g., manual battles). This is the correct design, just needs documentation and tests.

## Key Files Reference
| Component | File Path | Line(s) |
|-----------|-----------|---------|
| OR logic | `game/simulation/battle_controller.py` | 399-401 |
| Mode handler can_retreat | `game/simulation/combat/battle_mode_handler.py` | 110, 143, 176, 209 |
| Config field | `game/simulation/battle_config.py` | 65 |
| Dead isolated field | `game/simulation/battle_config.py` | 75 |
| Callers | `game/simulation/battle_controller.py` | 227, 284, 304 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Config can only enable, not disable | Current OR logic is correct. Strategy mode defaults to True via handler. Config provides opt-in for other modes. |
| 2026-04-06 | Remove BattleConfig.isolated | Verified dead code — never read. should_clone_ships() on mode handler is also never called. |

---

## Phases

### Phase 1: Document and Clean Up [Simple]
**Objective:** Clear documentation, remove dead code
**Status:** Not Started
See `phase_1_checklist.md`

### Phase 2: Add Tests [Simple]
**Objective:** Prove priority behavior
**Status:** Not Started
See `phase_2_checklist.md`

---

## Verification Checklist
- [ ] `pytest tests/unit/simulation/ -x` — all pass
- [ ] Strategy battles still allow retreat
- [ ] Manual/Test battles still deny retreat by default
