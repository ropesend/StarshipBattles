# PROJ-248: Weapon Cache Mutable Return

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-248` to see what to do next
> - Open the phase checklist file for your current phase

## Overview
`get_weapon_components_cached()` returns `self._weapons_cache` directly — a mutable list reference. Any caller that modifies the returned list corrupts the cache silently. The fix exists in the same file: `get_all_components()` returns `list(self._components_cache)`. Apply the same defensive copy pattern.

## Goals
- Return defensive copy from `get_weapon_components_cached()`
- Update test that asserts identity (`is`) to assert equality (`==`)
- Add test proving mutation doesn't affect cache

## Scope
**In Scope:** One-line production fix, two test updates

**Out of Scope:** Cache invalidation logic, other cache methods

## Current State
**Last Updated:** 2026-04-06 23:50
**Current Phase:** Planning Complete
**Next Action:** Implementation via Continue Project prompt
**Blockers:** None
**Context for Next Agent:** This is a one-line fix. Change `return self._weapons_cache` to `return list(self._weapons_cache)` at line 239 of ship_component_manager.py. Then update the identity test at line 254 of the test file.

## Key Files Reference
| Component | File Path | Line(s) |
|-----------|-----------|---------|
| Mutable return | `game/simulation/components/ship_component_manager.py` | 239 |
| Defensive copy pattern | `game/simulation/components/ship_component_manager.py` | 188 |
| Identity test to update | `tests/unit/simulation/entities/test_ship_component_manager.py` | 254 |
| Cache test class | `tests/unit/simulation/entities/test_ship_component_manager.py` | 212-280 |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Defensive copy via list() | Matches existing pattern at line 188. O(k) where k=weapon count (typically 1-4). |

---

## Phases

### Phase 1: Fix and Update Tests [Simple]
**Objective:** Return defensive copy, prove mutation safety
**Status:** Not Started
See `phase_1_checklist.md`

---

## Verification Checklist
- [ ] `pytest tests/unit/simulation/entities/test_ship_component_manager.py -x` — all pass
- [ ] `python -m simulation_tests.run_tests --fast` — all pass
