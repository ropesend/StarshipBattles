# PROJ-345: Closeout Sprint 3 - PROJ-333 critical coverage gaps from review

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-345` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Five PROJ-333 coverage gaps (T3.1 .. T3.5) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting implementation kickoff after PROJ-343 fresh OpenCode review)
**Last Action:** Project scaffolded
**Next Action:** Begin Phase 1
**Blockers:** PROJ-343 must land first (master arc plan stop-point).

## Overview

Five CRITICAL coverage gaps in the PROJ-333 per-turn-engine coverage project. Each pins meaningful production behavior that the prior arc's tests passed without exercising. Pure characterization-test work — NO production refactors. Apparent bugs found during these additions are documented as Observations in [decisions.md](decisions.md), not fixed.

## Goals

- T3.1: `test_max_queue_iterations_limits_inner_loop_to_10` asserts `== 10`, not `<= 10`. A counter proves exact iteration count.
- T3.2: Multi-component auto-disable test exists, pinning that production iterates ALL matching components (Observation 8 of PROJ-333).
- T3.3: `FleetMovementEngine.calculate_next_hex` has direct-coverage tests (currently zero coverage).
- T3.4: `production_spawner` dispatch tests no longer patch out `_load_and_create_ship` / `_create_and_place_facility` / `_spawn_fleet_ship`; minimal real fixtures exercise per-method outputs.
- T3.5: `_log_resource_shortage` and `_apply_resource_consumption` have fleet-context branch coverage (3rd branch was missing).

## Scope

**In:**
- `tests/unit/strategy/engine/test_production_engine_queue.py:293` (T3.1 rewrite)
- `tests/unit/strategy/engine/test_consumable_management_engine/test_characterization.py` (T3.2 add)
- `tests/unit/strategy/engine/test_fleet_movement_engine_calculate_next_hex.py` (T3.3 NEW or extend existing)
- `tests/unit/strategy/engine/test_production_spawner.py:54-101` (T3.4 rewrite)
- `tests/unit/strategy/engine/test_production_engine.py` or test_production_engine_*.py (T3.5 add)

**Out:**
- Any production-code change. If a coverage test fails because production has a bug: capture as Observation; don't fix.

## Key Files (production references)

| Component | File Path |
|-----------|-----------|
| T3.1 production | `game/strategy/engine/production_engine.py` (queue inner-loop) |
| T3.2 production | `game/strategy/engine/consumable_management_engine.py` |
| T3.3 production | `game/strategy/engine/fleet_movement_engine.py` |
| T3.4 production | `game/strategy/engine/production_spawner.py` |
| T3.5 production | `game/strategy/engine/production_engine.py` (`_log_resource_shortage`, `_apply_resource_consumption`) |

## Verification

- [ ] All Phase 1 tasks checked
- [ ] `pytest tests/unit/strategy/engine/ -x -q` — all pass
- [ ] `python Tools/lint_test_files.py` — 0 violations
- [ ] User verified
