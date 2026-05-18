# PROJ-444 Phase 4: LOC-ceiling extractions

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-444 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phase 3 complete (wrapper retirement frees up Planet's interface for cleaner serialization split)
**Objective:** Mechanical responsibility-based file splits for two data-layer files over the 500-LOC ceiling: `fleet.py` (677 LOC) and `planet_gen.py` (610 LOC). `ship_instance.py` (839 LOC) is explicitly out of scope per its findings entry — that's a dedicated future project.

**Cross-bucket file-ownership rule:** Only `game/strategy/data/` files touched. Pure refactor — no behavior change. Run sharded suite after each split to confirm zero regressions.

**Source-of-truth findings:** [`findings/bucket_a_data_facade_scan.md`](findings/bucket_a_data_facade_scan.md) — F-A-008, F-A-009. F-A-007 (ship_instance.py) is documented but explicitly deferred.

---

## Tasks

### Task 4.1: F-A-008 — Extract Fleet.to_dict/from_dict into fleet_serde.py [Medium]
**File:** Create `game/strategy/data/fleet_serde.py`; edit `game/strategy/data/fleet.py:1`
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py tests/integration/save_load/ -v`

- [ ] Read `planet_serde.py` as the extraction template (PROJ-372 precedent)
- [ ] Identify extractable surface in `fleet.py`: `Fleet.to_dict` (~70 LOC), `Fleet.from_dict` (~70 LOC), the `resolve_order_references` already-delegating-to-OrderSerializer method (~10 LOC if it's still useful in the data class)
- [ ] **GREEN — create fleet_serde.py**: New module with `fleet_to_dict(fleet: Fleet) -> dict` and `fleet_from_dict(data: dict) -> Fleet` free functions (or classmethods on a `FleetSerde` class — match the planet_serde.py convention exactly). Move the bodies; update imports.
- [ ] **GREEN — keep fleet.py thin delegators OR remove**: If callers always invoke through `fleet.to_dict()` / `Fleet.from_dict(...)`, keep one-line delegators on the class that route to the new module. If callers can use the free functions directly, migrate them and delete the class methods.
- [ ] Run targeted tests after each step
- [ ] Verify `fleet.py` is now under 540 LOC (target: ~535-540 with the extraction; the original ~677 minus ~140 of serde)

### Task 4.2: F-A-009 — Split planet_gen.py by sub-concern [Medium]
**File:** `game/strategy/data/planet_gen.py:1` (610 LOC)
**Tests:** `pytest tests/unit/strategy/data/test_planet_gen.py tests/integration/galaxy_gen/ -v`

- [ ] Read planet_gen.py in full to identify cohesive sub-concerns. Most likely splits:
  - Atmosphere generation (atmosphere type, pressure, composition)
  - Surface conditions (temperature, gravity, water level, radiation)
  - Orbital arrangement (distance, eccentricity, parent system)
- [ ] If a clean axis exists, split into `planet_gen_atmosphere.py`, `planet_gen_surface.py`, `planet_gen_orbits.py` (or whatever the actual cohesive groups are). Top-level `planet_gen.py` becomes a thin orchestrator + re-export.
- [ ] If no clean axis exists: stop, document the finding in decisions.md, and defer the split. Don't force a bad split.
- [ ] Run targeted + sharded tests after the split to confirm galaxy generation still produces deterministic output (use seed-based regression test)

### Task 4.3: F-A-007 status check — confirm ship_instance.py deferral still holds [Simple]
**File:** `game/strategy/data/ship_instance.py:1` (839 LOC)

- [ ] After Phase 3 wrapper retirement: rerun `wc -l game/strategy/data/ship_instance.py`. If retired property shim clusters dropped the LOC enough to be under 500: update [decisions.md](decisions.md) noting the ceiling is now met. If still over (likely): confirm the deferral note in plan.md is still accurate and note in decisions.md that a dedicated "ShipInstance shim retirement" follow-up project remains open.
- [ ] No code change in this task; this is a measurement + documentation update.

---

## Phase Completion Checklist

- [ ] Tasks 4.1 + 4.2 complete (or 4.2 explicitly deferred with rationale)
- [ ] `fleet.py` under 540 LOC
- [ ] `planet_gen.py` either under 500 LOC OR explicitly deferred with rationale
- [ ] `ship_instance.py` status documented in decisions.md
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-444 4` — PASSED
- [ ] Update status to `Complete`; plan.md phase table all rows Complete; Current State → "Project complete — awaiting verification"
- [ ] No save-load regressions (seed-based galaxy gen + save/load round-trip tests green)

## Notes

- Pure refactor phase. No behavior changes; no new findings expected to surface. If something does surface during the extraction (lying docstring, dead branch, etc.), log it to `discovered_issues/log.jsonl` — do NOT fix inline.
- After this phase, PROJ-444 is verification-ready.
