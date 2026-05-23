# PROJ-455: Planet-FMS engine-mediated behavioural coverage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-455` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-455 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** legacy serial-on-main (matches PROJ-443/444 standing preference; no worktrees).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. End-to-end fixture construction (planet + facility + FMS bay + queued order + deployed groups) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `test_process_planet_action_tick_end_to_end` parametrised across 5 FMS order types | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Mark DI-2026-05-18-001 ActionExecutionEngine half `resolved` in log.jsonl | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Project complete; merged to main at 92e6fa5d2
**Last Action:** PROJ-455 closed: merged `group-c` into `main` at SHA `92e6fa5d2` (merge commit "Merge group-c through PROJ-455 (end of project)"). Rebase of `group-c` on `main` was a no-op (no other groups had pushed since PROJ-452 merge). Codex end-of-project audit landed at `consults/20260519T141330Z_end-of-project-audit/response.md` with verdict "Ready to merge" — no verified production issues.
**Next Action:** Advance to PROJ-458 (position 3 of 4 in Group C's serial order).
**2026-05-19 cross-group resolution (final):** Bookkeeping fix G3-C applied — Scope section's "In" block tightened so `tests/integration/test_fms_planet_lay_mines.py` is now an explicit **READ-ONLY precedent** (the file belongs to PROJ-450 in Group A's staging-yard substrate migration). The earlier loose plan-text mentioning an optional `_planet_fms_fixtures.py` extraction is now CLOSED; copy needed scaffolding into the new test file rather than refactoring the precedent file. Group C execution-context block added to Dependencies.

## Overview

The still-open ActionExecutionEngine half of DI-2026-05-18-001 — "Behavioral E2E coverage gap for planet-FMS through `ActionExecutionEngine._process_planet_action_tick`. The engine-mediated dispatch path that runs planet FMS recovery/launch orders through OrderProcessor.get_handler → handler.execute_for_issuer is currently protected by structural / inspect-based tests plus unit-level handler tests, but no behavioral test drives the full engine tick path." (verbatim from `discovered_issues/log.jsonl` DI-2026-05-18-001).

Archived PROJ-445 Phase 1 closed half this gap by adding `tests/integration/test_fms_planet_lay_mines.py` (parametrised across all 5 planet-FMS order types) — but that test drives `_execute_planet_action` **directly**, bypassing `_process_planet_action_tick`'s order-progression / action-time-resolution logic. The full engine-mediated chain remains uncovered:

```
process_action_ticks(empires, galaxy, tick, component_registry, all_empires)
  → loop over empire.fleets (fleet branch — already covered elsewhere)
  → loop over empire.colonies
    → _process_planet_action_tick(planet, empire, tick, component_registry)   ← UNTESTED END-TO-END
      → planet.get_current_order()
      → order.type in order_metadata.planet_fms_action_order_types check
      → order.execution_progress += 1
      → ActionTimeResolver.resolve_action_time(planet, order, component_registry)
      → if progress >= action_time: _execute_planet_action(...)
        → _order_processor.get_handler(order.type)
        → PlanetStagingYardIssuerAdapter(planet)
        → handler.execute_for_issuer(issuer=..., order_owner=..., empire=..., galaxy=None, registries=...)
```

PROJ-455 closes this end-to-end gap.

## Goals

- Construct one shared end-to-end fixture that builds a complete `process_action_ticks` driving context: 1 empire, 1 owned planet with operational facility carrying the FMS bay, queued FMS order via typed command path, deployed groups present where the order type requires them.
- Add `test_process_planet_action_tick_end_to_end` parametrised across all 5 entries in `order_metadata.planet_fms_action_order_types` (LAY_MINES, LAUNCH_FIGHTERS, LAUNCH_SATELLITES, RECOVER_FIGHTERS, RECOVER_SATELLITES). Each parametrise case drives the full `process_action_ticks → ... → handler.execute_for_issuer` chain through one tick.
- Assert on observable post-conditions: order queue advanced, `execution_progress` incremented (or order popped on completion), deployed group state transitioned correctly (mines created / fighters launched / satellites recovered / etc.), no exception propagation, `ActionTickResult` returned with the expected fields populated.
- Mark DI-2026-05-18-001 (ActionExecutionEngine half) `resolved` in `log.jsonl` with a `resolution_note` pointing at the new test file.

## Scope

**In (this project owns these files):**
- One new test file: `tests/integration/test_process_planet_action_tick_end_to_end.py` (or similar name; pick the location that mirrors the existing `tests/integration/test_fms_planet_lay_mines.py` convention).
- Shared fixture helpers inside the NEW test file ONLY. Copy-paste any reusable scaffolding from `test_fms_planet_lay_mines.py` rather than extracting a sibling module — see the read-only call-out below.
- `AgentCoordination/discovered_issues/log.jsonl` (Phase 3 — status update only).

**READ-ONLY precedent (do NOT modify) — cross-group collision resolution:**
- `tests/integration/test_fms_planet_lay_mines.py` is READ-ONLY for PROJ-455. This file is the precedent that PROJ-455 builds on — the existing test drives `_execute_planet_action` directly. PROJ-455 escalates by adding new integration tests at `tests/integration/test_process_planet_action_tick_end_to_end.py` that drive the full `process_action_ticks` chain. Do NOT modify `test_fms_planet_lay_mines.py`; that file belongs to PROJ-450 (Group A, substrate migration). The earlier plan text suggested an optional `_planet_fms_fixtures.py` extraction — that path is now CLOSED: copy needed scaffolding into the new test file rather than refactoring the precedent file.

**Out (PROJ-452 owns):** any catalog-driven resource-surface work.

**Out (PROJ-453 owns):** annotation polish and stale docstrings in `game/strategy/engine/`.

**Out (PROJ-454 owns):** `effect_ability_metadata.py` retirement, `component_inspector.py` retirement, OrderProcessor facade unwinding.

**Out of scope entirely:**
- Production-code changes to `ActionExecutionEngine`. The finding explicitly tags this as a **coverage gap**, not a behaviour bug — the production path already works (verified by the parametrised handler test in `test_fms_planet_lay_mines.py`). PROJ-455 only adds the engine-mediated test.
- Any work on the fleet branch of `process_action_ticks`. The fleet branch has separate coverage already; PROJ-455 stays focused on the planet branch.
- Re-doing PROJ-445 Phase 1's `test_fms_planet_lay_mines.py` (still in the suite; do not delete or replace it).

## Findings Summary

Full report: [findings/PROJ-455_findings.md](findings/PROJ-455_findings.md). One entry.

| Finding | Severity | File:Line (current) | Source |
|---------|----------|---------------------|--------|
| DI-2026-05-18-001 (ActionExecutionEngine half) — Behavioural E2E coverage gap for planet-FMS via `_process_planet_action_tick` | medium | `game/strategy/engine/action_execution_engine.py:245-297` | DI log |

This is the **still-open** half of DI-001. The other half (transfer half) was closed by archived PROJ-445 Phase 2 (`_dispatch_fleet_to_fleet` drop_pod/vehicle branch). The DI log entry has separate `"id": "DI-2026-05-18-001"` for each half — see Phase 3 of this checklist for the status-update procedure.

## Key Files

| Component | File Path | Role in this project |
|-----------|-----------|----------------------|
| Engine entry point | `game/strategy/engine/action_execution_engine.py:81-132` (`process_action_ticks`) | Test-driven through this method |
| Planet tick handler | `game/strategy/engine/action_execution_engine.py:245-297` (`_process_planet_action_tick`) | Primary subject of new tests |
| Planet action dispatch | `game/strategy/engine/action_execution_engine.py:299-329` (`_execute_planet_action`) | Already structurally tested; PROJ-455 adds the upstream test |
| Planet-FMS handler set | `game/strategy/engine/commands/registry.py:312-325` (`planet_fms_action_order_types`) | 5 OrderTypes to parametrise across |
| Issuer adapter | `game/strategy/engine/issuer_adapter.py` (`PlanetStagingYardIssuerAdapter`) | Read-only — fixture builds planets the adapter understands |
| Existing precedent | `tests/integration/test_fms_planet_lay_mines.py` | Adapt the `_StubPlanet` + scenario builders for end-to-end use |
| Action-time resolver | `game/strategy/services/action_time_resolver.py` | Read-only — fixture must produce planets whose `action_time` resolves correctly |

Full enumeration in [manifest.md](manifest.md).

## Phase Breakdown

### Phase 1: End-to-end fixture construction [Simple-Medium]

Phase 1 is the **bulk of the project's work**. Constructing a fixture that drives the full `process_action_ticks` chain end-to-end requires more shape than the `_execute_planet_action`-direct-call precedent in `test_fms_planet_lay_mines.py`. The fixture needs to satisfy these additional constraints that the direct-call test bypasses:

1. **`Empire`-like shape** with both `fleets` (can be empty) and `colonies` (list containing our test planet). Currently `test_fms_planet_lay_mines.py` uses a `SimpleNamespace` with `fleets=[]` and `colonies=[planet]`; that base is reusable.
2. **`Planet`-like shape** that satisfies `_process_planet_action_tick`'s preconditions:
   - `get_current_order()` returns the queued FMS order
   - `pop_order()` works (called by `_execute_planet_action` after handler dispatch)
   - `add_order(order)` for fixture setup
   - `staging_yard: list` with the matching item kind (mine/fighter/satellite dict) for launch/lay orders
   - `add_to_staging_yard(item)` for fixture setup
   - `max_staging_mass: float` (set to 0 = unlimited; the existing stub follows this)
   - `id: int`, `owner_id: int`, `location: HexCoord`, `global_hex: HexCoord`
   - `orders: list` (the existing stub field)
3. **`ActionTimeResolver`** must return a finite `action_time`. Either inject a mock resolver via the `ActionExecutionEngine(order_processor=..., action_time_resolver=...)` constructor parameter (preferred — keeps the test deterministic), or supply a planet whose component layout the static `ActionTimeResolver.resolve_action_time` can resolve.
4. **`order.execution_progress`** must start at 0; the test asserts it goes to 1 after one tick (if `action_time > 1`) or that the order pops (if `action_time == 1`).
5. **`OrderProcessor`** must be the real one (we want to exercise the real dispatch chain). The default `OrderProcessor()` constructor works without an `event_bus`.
6. **`deployed_groups`** on the empire for the recovery-flow scenarios. Same shape as the existing `_build_recover_fighters_scenario` / `_build_recover_satellites_scenario` in the precedent file.

Phase 1's deliverable is the fixture module / helpers plus a single smoke test that drives one full `process_action_ticks` call against a LAY_MINES scenario (the simplest of the 5).

### Phase 2: Parametrised end-to-end test across all 5 FMS order types [Medium]

Add `test_process_planet_action_tick_end_to_end` parametrised across the 5 entries in `order_metadata.planet_fms_action_order_types`. Each parametrise case:

- Builds the planet + empire fixture with the appropriate `_build_*_scenario` (LAY_MINES, LAUNCH_FIGHTERS, LAUNCH_SATELLITES, RECOVER_FIGHTERS, RECOVER_SATELLITES).
- Calls `engine.process_action_ticks(empires=[empire], galaxy=None, tick=1, component_registry=None)`.
- Asserts (a) no exception, (b) the order queue advanced (either `execution_progress > 0` or order popped), (c) the deployed group / staging yard state transitioned in the expected direction (mines created, fighters launched, satellites recovered, etc.), (d) the returned `List[ActionTickResult]` contains exactly one record for the planet with the expected `order_type`.

Add a sibling guard test `test_planet_fms_e2e_parametrise_matches_registry_view` (mirroring the existing `test_planet_fms_order_types_match_registry_view` in `test_fms_planet_lay_mines.py`) so the parametrise list can't drift from `order_metadata.planet_fms_action_order_types`.

### Phase 3: Mark DI-001 (ActionExecutionEngine half) `resolved` in log.jsonl [Simple]

Update `AgentCoordination/discovered_issues/log.jsonl`. The current log has two entries with `"id": "DI-2026-05-18-001"`:
- Line 1 (the ActionExecutionEngine half — open in this project)
- Line 3 (the transfer half — already `"status": "resolved"` per archived PROJ-445 Phase 2)

Phase 3 sets `"status": "resolved"` on line 1 with a `resolution_note` pointing at the new test file and PROJ-455 Phase 2.

## Related Documents

- [design.md](design.md) — architecture rationale + relationship with archived PROJ-445 Phase 1
- [decisions.md](decisions.md) — decisions log
- [findings/PROJ-455_findings.md](findings/PROJ-455_findings.md) — DI-001 ActionExecutionEngine half full text
- [`AgentCoordination/discovered_issues/log.jsonl`](../../../AgentCoordination/discovered_issues/log.jsonl) — source DI entry
- [`AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md`](../../../AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md) — Codex r4 redesign that produced this project (job #7)
- [`tests/integration/test_fms_planet_lay_mines.py`](../../../tests/integration/test_fms_planet_lay_mines.py) — precedent test for the `_StubPlanet` shape and scenario builders to reuse
- [`Projects/archived_projects/PROJ-445/plan.md`](../../archived_projects/PROJ-445/plan.md) — PROJ-445 Phase 1 (closed the other coverage half)

## Dependencies & Sibling Projects

### Group C execution context (coordinator-assigned 2026-05-19)

**Group C serial order: PROJ-452 → PROJ-455 → PROJ-458 → PROJ-460.**

This is **PROJ-455 — position 2 of 4** in Group C. The run agent reaches this project only after PROJ-452 completes (all phases + codex audit + any audit-driven extra phases). When this project is complete, advance to PROJ-458.

Groups A (PROJ-449/451/450/459) and B (PROJ-456/454/457) run in parallel branches. Coordinator confirmed no hard cross-group blockers. **`tests/integration/test_fms_planet_lay_mines.py` is READ-ONLY for PROJ-455** — see the Scope section's READ-ONLY precedent block above; that file belongs to PROJ-450 (Group A, substrate migration). See `Projects/active_projects/GroupC_execution_prompt.txt` for the run agent's full execution contract.

### Other-project relationships

| Project | Group | Status | Relationship |
|---------|-------|--------|--------------|
| PROJ-452 (catalog-driven resource surfaces) | C (prev) | Active | Disjoint file set; serial predecessor in Group C |
| PROJ-453 (engine + services surface polish) | B | Active | Disjoint test file set — runs in parallel |
| PROJ-454 (engine + services obsolete-surface retirement) | B | Active | Possible read-only dependency on `OrderProcessor` (PROJ-454 Phase 3 unwinds the facade reshape; PROJ-455 only invokes `OrderProcessor.get_handler` which PROJ-454 does not touch). No write conflict. |
| PROJ-450 (typed staging-yard substrate) | A | Active | Owns `tests/integration/test_fms_planet_lay_mines.py` (PROJ-455 treats as READ-ONLY precedent). |

No hard predecessor. The new test file is isolated; no production-code shared writes with any sibling.

## Verification

- [ ] All three phase checklists complete
- [ ] DI-2026-05-18-001 ActionExecutionEngine half marked `resolved` in `log.jsonl`
- [ ] `pytest tests/integration/test_process_planet_action_tick_end_to_end.py -v` green (5 parametrise cases + 1 registry-view guard)
- [ ] `pytest tests/integration/test_fms_planet_lay_mines.py -v` still green (PROJ-445 Phase 1 precedent test — must not regress)
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Audit passed (Codex end-of-project consult per the standing workflow)
- [ ] User verified
