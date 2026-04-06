# PROJ-247: Ship ID Mapping Fragility

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-247` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
`battle_controller.py` uses `id(ship)` (Python memory address) as dictionary keys across 26 call sites in 4 files. Python's `id()` can be reused after GC. Ship.id is also `str(id(self))` — same fragility. Replace Ship.id with `str(uuid.uuid4())` and update all `_ship_id_map` usages.

## Goals
- Ship.id is a stable UUID4 string, not a memory address
- `_ship_id_map` keys use `ship.id` (stable string) instead of `id(ship)` (fragile int)
- Ship identity survives save/load round-trips

## Scope
**In Scope:**
- Change `Ship.__init__` to use uuid4 for `self.id`
- Replace all `id(ship)` usages in battle_controller.py (12 sites)
- Replace all `id(ship)` usages in retreat_manager.py (4 sites)
- Replace all `id(ship)` usages in battle_state.py (6 sites)
- Update `_ship_id_map` type from `Dict[int, str]` to `Dict[str, str]`
- Update test fixtures
- Verify callers of `ship.id` (AI, strategy, UI) still work with UUID strings

**Out of Scope:**
- Changing retreat system logic
- Modifying save file format (UUID is still a string)

## Current State
**Last Updated:** 2026-04-06 23:45
**Current Phase:** Planning Complete
**Next Action:** Implementation via Continue Project prompt
**Blockers:** None
**Context for Next Agent:** Ship.id is used in ~20 places across game/ (AI caching, strategy fleets, UI panels, superweapon processing). All use it as an opaque string key — switching from str(id(self)) to str(uuid4()) should be transparent. The _ship_id_map pattern in battle_controller is the primary fragility target.

## Key Files Reference
| Component | File Path | Sites |
|-----------|-----------|-------|
| Ship.id definition | `game/simulation/entities/ship.py:78` | 1 |
| Battle controller map | `game/simulation/battle_controller.py` | 12 (lines 78,103,168,199,201,313,322,366,383,459,480,621) |
| Retreat manager | `game/simulation/managers/retreat_manager.py` | 4 (lines 86,127,247,265) |
| Battle state | `game/simulation/battle_state.py` | 6 (lines 500,505,684,685,688,695) |
| AI target cache | `game/ai/target_evaluator.py:262` | Uses ship.id as dict key |
| Strategy fleet | `game/strategy/data/fleet.py:88` | Uses ship.id in display |
| UI panels | `game/ui/panels/battle_panels.py:82` | Returns ship.id |
| Retreat test fixture | `tests/unit/simulation/managers/test_retreat_manager.py:51` | Uses id() in fixture |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Replace Ship.id with uuid4 | Single identity field, no backward compat shim needed. All callers use it as opaque string. |

---

## Phases

### Phase 1: Change Ship.id to UUID4 [Simple]
**Objective:** Ship identity is stable across GC and save/load
**Status:** Not Started
See `phase_1_checklist.md`

### Phase 2: Replace id() in Battle Controller and Managers [Medium]
**Objective:** _ship_id_map uses ship.id instead of id(ship)
**Status:** Not Started
See `phase_2_checklist.md`

### Phase 3: Update Tests [Simple]
**Objective:** All test fixtures use stable ship IDs
**Status:** Not Started
See `phase_3_checklist.md`

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Read `docs/` foundation docs
- [ ] Run full test suite: `pytest tests/` — all pass

### After Each Phase
- [ ] `pytest tests/ --testmon` — all pass
- [ ] `python -m simulation_tests.run_tests --fast` — all pass

### Final Verification
- [ ] Save/load round-trip preserves ship identity
- [ ] AI target caching works with UUID strings
- [ ] Run full test suite: `pytest tests/`
