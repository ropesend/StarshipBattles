# PROJ-333 — Per-turn Processing Engines Characterization

**Branch:** `feat/03c-phase-aware-execution`
**Source plan:** `~/.claude/plans/noble-stirring-galaxy-agent-a1d0f12996bf6a385.md`
**Predecessor / dependency:** master characterization plan; sequenced after PROJ-332 (`turn_engine.py`).
**Mode:** Plan-only artefacts. No production code, no test code in this project. Phase 1 is the test-writing phase.

---

## Quick Status

| Phase | Scope | Status |
|---|---|---|
| Phase 1 | Author characterization tests for the 5 in-scope per-turn engines | Not started |

This is a characterization-only project. There is no Phase 2.

---

## Overview

The strategy layer's per-turn cycle is driven by five engines that fire on every tick of every turn. Together they constitute ~2,513 LOC of behavior that mutates `Empire`, `Galaxy`, `Planet`, and `Fleet` state on every game tick. Two of the five are alarmingly under-tested:

- `order_processor.py` (910 LOC) — only `test_order_processor_fleet_merge.py` exists. TRANSFER, COLONIZE, LOAD/UNLOAD-cargo, and the BUG-122 instant-orders Phase A/B/C election logic are not pinned.
- `production_engine.py` (666 LOC) — partial coverage in `test_production_refactor.py`, `test_production_repro.py`, `test_production_math.py` covers maths and a refactor smoke test but does not pin the queue-tick state machine.

The other three (`production_spawner.py`, `consumable_management_engine.py`, `fleet_movement_engine.py`) have partial coverage that misses the surface decisions documented in `design.md`.

This project pins behavior. It does not refactor.

---

## Goals

1. Author one characterization test file per production file, splitting `production_engine` and `order_processor` by responsibility so no resulting test file approaches 500 LOC.
2. Pin happy / unhappy / corner cases per the master characterization-plan philosophy.
3. Reuse existing fixtures (`tests/fixtures/`, per-engine `conftest.py` files under `tests/unit/strategy/{consumable_management_engine,fleet_movement_engine}/`).
4. Document apparent bugs as observations in `decisions.md`. Do not fix them in this project.

---

## Scope

**In scope (5 production files):**

- `game/strategy/engine/production_engine.py`
- `game/strategy/engine/production_spawner.py`
- `game/strategy/engine/consumable_management_engine.py`
- `game/strategy/engine/fleet_movement_engine.py`
- `game/strategy/engine/order_processor.py`

**Out of scope:**

- `game/strategy/engine/turn_engine.py` (PROJ-332)
- `game/strategy/engine/action_execution_engine.py`
- `game/strategy/engine/superweapon_order_processor.py`
- `game/strategy/engine/build_order_processor.py`
- Harvesting and atmosphere engines

---

## Success Criteria

- ~50–75 new characterization tests across the 5 engines (estimate **~70**).
- Full sharded test suite green (`python Tools/test_sharded/test_sharded.py`).
- No production-file modifications in `game/strategy/engine/`.
- Apparent bugs surfaced during read-through are catalogued in `decisions.md` Observations section; none are fixed in this project.
- Each new test file is committed individually (one file = one commit).

---

## Sessions Estimate

**~2 sessions** — matches master plan.

- **Session 1:** `production_engine` + `production_spawner` + `consumable_management_engine` + `fleet_movement_engine` (4 files, ~50 tests, mostly extending existing per-engine conftest patterns).
- **Session 2:** `order_processor` split into 3 test modules (COLONIZE, TRANSFER, instant-orders), ~30 tests; the BUG-122 instant-orders Phase A/B/C election is the most fixture-heavy work.
