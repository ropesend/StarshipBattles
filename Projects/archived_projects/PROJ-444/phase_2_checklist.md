# PROJ-444 Phase 2: Container-substrate residue cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-444 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** Phase 1 complete (recommended but not strictly required — Phase 2 findings are independent of Phase 1 polish)
**Objective:** Close out the small invariant gaps + missing-functionality residue from the PROJ-436 Container substrate work (Phases 1-12). Most tasks have cross-bucket coordination points with PROJ-445; coordinate via decisions.md, do not edit PROJ-445-owned files.

**Cross-bucket file-ownership rule:** Only edit `game/strategy/data/`, `game/strategy/facade/`, `tests/{unit,integration}/strategy/{data,facade}/`, `tests/integration/save_load/`. Coordinate (but do not edit) PROJ-445-owned files: `game/strategy/engine/production_engine.py`, `game/strategy/engine/order_handlers/transfer_branches.py`.

**Source-of-truth findings:** [`findings/bucket_a_data_facade_scan.md`](findings/bucket_a_data_facade_scan.md) — full text for F-A-010, F-A-012, F-A-013, F-A-014, F-A-028, F-A-029. Also read the cross-coupled DI entries DI-2026-05-18-001 (transfer + planet-FMS) and DI-2026-05-18-006 (Fleet rounding) in `AgentCoordination/discovered_issues/log.jsonl`.

---

## Tasks

### Task 2.1: F-A-012 — Replace PlanetaryFacility hardcoded "fuel" API with generic consumable API [Medium]
**File:** `game/strategy/data/planetary_facility.py:32` (the `consumable_levels` field) + `:136-193` (the `get_fuel_storage` / `add_fuel` / `withdraw_fuel` / `get_max_fuel_storage` methods)
**Tests:** `pytest tests/unit/strategy/data/test_planetary_facility.py -v`

- [x] Read PROJ-436 Phase 0 D1 default (decisions.md row 39 in `Projects/active_projects/PROJ-436/decisions.md`) — confirm "keep as internal state until a concrete transfer use case justifies fold-in" is still the operative direction
- [x] **RED**: Add tests that exercise a non-fuel resource through the new generic API: `test_add_consumable_organics_increases_level`, `test_withdraw_consumable_radioactives_decreases_level`, `test_get_consumable_storage_returns_zero_for_unknown_resource`. These FAIL because the API is `"fuel"`-only today.
- [x] **GREEN — generic API**: Add `add_consumable(resource_id: str, amount: float) -> None`, `withdraw_consumable(resource_id: str, amount: float) -> float`, `get_consumable_storage(resource_id: str) -> float`, `get_max_consumable_storage(resource_id: str) -> float`. The max-capacity lookup should iterate `ResourceCatalog.from_json().all_ids()` for known resources; unknown resource IDs raise `ValueError`.
- [x] **GREEN — fuel-API wrappers**: Convert the four `*_fuel` methods to thin delegators calling `*_consumable("fuel", ...)`. Mark them as deprecated in docstrings; do NOT delete the wrappers in this phase — caller migration is out of Phase 2 scope unless trivial.
- [x] Run `git grep -n "add_fuel\|withdraw_fuel\|get_fuel_storage\|get_max_fuel_storage"` to count callers. If <5, migrate them and delete the wrappers in this phase. If ≥5, leave the wrappers and log a follow-up in decisions.md.
- [x] Run targeted tests.
- [x] Note: The Container fold-in itself (D1 option (a)) is still deferred — that's not in scope here.

### Task 2.2: F-A-014 — Fix PlanetSlice mass-cap proxy [Simple]
**File:** `game/strategy/facade/slices/planet_slice.py:155-180` (`_planet_stockpile_snapshot` helper)
**Tests:** `pytest tests/unit/strategy/facade/slices/test_planet_slice.py -v`

- [x] Read existing helper. Current line: `capacity_mass = float(sum(max_stockpile.values()))` — sums quantities as if they were mass.
- [x] Read the correct pattern at `game/strategy/data/bay_inventory.py:200-205` (`total_resource_mass` multiplies each amount by `ResourceCatalog.get_mass_per_unit`).
- [x] **RED**: Add `test_planet_stockpile_snapshot_uses_per_resource_mass`. Construct a planet with `max_stockpile = {"vapors": 1000, "fuel": 500}` (both very lightweight per `data/resources.json`). Assert `capacity_mass` is `1000 * mass_per_unit("vapors") + 500 * mass_per_unit("fuel")` ≈ `1.05`, NOT `1500`.
- [x] **GREEN**: Replace the `sum(max_stockpile.values())` line with `sum(amount * ResourceCatalog.from_json().get_mass_per_unit(rid) for rid, amount in max_stockpile.items())`. Keep the `inf` fallback for the no-caps-set branch.
- [x] Run targeted tests.

### Task 2.3: F-A-010 + DI-2026-05-18-006 — Fleet.consume_cargo_resource rounding fix [Medium]
**File:** `game/strategy/data/fleet.py:262` (`consume_cargo_resource`) + `:245` (`has_cargo_resources` — the affordability check)
**Tests:** `pytest tests/unit/strategy/data/test_fleet.py -v` + `pytest tests/integration/production/ -k fleet -v`

- [x] Read DI-2026-05-18-006 in `AgentCoordination/discovered_issues/log.jsonl` for the full backstory
- [x] Read PROJ-436 Phase 12 decisions.md in `Projects/active_projects/PROJ-436/decisions.md` — confirm Option C (engine-side diff truth-up) is the shipped Phase 12 outcome
- [x] **Decision**: Pick Option A (widen `_resource_agg.unload_cargo_from_fleet` to float, propagate through the integer-typed cargo store widening) OR Option B (round in `has_cargo_resources` to match consumption semantics). Document the decision in [decisions.md](decisions.md). Option B is cheaper (~5 LOC); Option A is more correct (~30 LOC + cargo-store touchpoints).
- [x] **RED**: Add a test reproducing DI-006: fractional per-step fleet costs that round to 0 (requested 0.1 against cargo=1) — currently affordability PASSES, consume actually charges 0, queue stalls without RESOURCE_SHORTAGE. The test asserts EITHER (a) the affordability check now returns False, OR (b) a RESOURCE_SHORTAGE event is emitted when actually-consumed < requested.
- [x] **GREEN**: Implement the chosen option. If Option A, widen the cargo store typing through `_resource_agg.unload_cargo_from_fleet`; if Option B, change `Fleet.has_cargo_resources` to compare against `int(round(amount))` matching the consumption rounding.
- [x] Update `discovered_issues/log.jsonl` to mark DI-2026-05-18-006 as `resolved` (status field).
- [x] Coordinate with PROJ-445 F-B-019: that finding tightens the `IProductionResourceSource.production_consume_resource` Protocol docstring contract. PROJ-445's agent owns the Protocol docstring edit; you own the implementer-side fix here. Communicate via decisions.md if you need them to sequence the Protocol update first.

### Task 2.4: F-A-013 + DI-2026-05-18-001 (snapshot half) — Tighten _ship_container_snapshot capacity model [Small]
**File:** `game/strategy/facade/slices/fleet_slice.py:165-193` (`_ship_container_snapshot` helper)
**Tests:** `pytest tests/unit/strategy/facade/slices/test_fleet_slice.py -v`

- [x] Read PROJ-437 Phase 1a documented residual in `Projects/active_projects/PROJ-437/decisions.md` (row 39 area)
- [x] Read DI-2026-05-18-001 in `discovered_issues/log.jsonl` — this is the fleet-to-fleet drop_pod/vehicle silent no-op
- [x] Read the current behavior at the snapshot site: `capacity_mass=inf` projection means it can legally report `mass_used > capacity_mass`
- [x] **Coordinate with PROJ-445 Phase 2** on F-B-003 + DI-001 fix: PROJ-445 adds public `ship.can_carry_pod` / `ship.load_vehicle` / `ship.unload_vehicle` delegators and adds the missing fleet-to-fleet dispatch branch in `_dispatch_fleet_to_fleet`. The snapshot tightening here should match what those engine handlers enforce (real `bay_inventory` capacity instead of `inf`).
- [x] **RED**: Add `test_ship_container_snapshot_capacity_matches_bay_inventory`. The test builds a ship with a 50-mass bay (10/50 used), takes the snapshot, asserts `mass_used == 10` AND `capacity_mass == 50` (not `inf`).
- [x] **GREEN**: Update `_ship_container_snapshot` to project the bay's real `capacity_mass` from `ship._cargo_mgr.get_vehicle_bay_capacity()` instead of `inf`. Drop the comment at lines 180-182 saying "Phase 2 validation decides how to treat the uncapped case."
- [x] Run targeted tests.

### Task 2.5: F-A-028 — Replace 5 conditional skips in test_facade_integration with deterministic fixtures [Small]
**File:** `tests/integration/strategy/facade/test_facade_integration.py:158, 184, 226, 325, 346`
**Tests:** `pytest tests/integration/strategy/facade/test_facade_integration.py -v`

- [x] Read each of the 5 skip call sites — they skip when procedural galaxy gen doesn't yield (a) an uncolonized planet, (b) a home colony, (c) an enemy fleet, etc.
- [x] Build deterministic fixture builders that explicitly inject:
  - One uncolonized planet (use the `_build_galaxy_fixture` pattern if it already exists in this test module or in a sibling fixture file)
  - One home colony with known owner
  - One enemy fleet at known coordinates with known empire
- [x] Replace each `pytest.skip(...)` call site with the deterministic fixture; delete the skip
- [x] Confirm each test runs deterministically (run 10× in a row, all pass)

### Task 2.6: F-A-029 — Replace 2 conditional skips in test_resupply_persistence [Simple]
**File:** `tests/integration/save_load/test_resupply_persistence.py:234, 283`
**Tests:** `pytest tests/integration/save_load/test_resupply_persistence.py -v`

- [x] Same recipe as Task 2.5 — inject a colony explicitly + a fleet with ships explicitly
- [x] Replace both `pytest.skip(...)` with the deterministic fixtures
- [x] Confirm deterministic pass

---

## Phase Completion Checklist

- [x] All 6 task groups complete
- [x] DI-2026-05-18-006 marked `resolved` in `discovered_issues/log.jsonl` (coordinate the marker with PROJ-445 if F-B-019 is also closed)
- [x] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [x] Run `python Projects/scripts/validate_phase.py PROJ-444 2` — PASSED
- [x] Update status to `Complete`; update plan.md phase table + Current State to point at Phase 3
- [x] decisions.md updated with: Option A vs Option B choice for F-A-010; PlanetaryFacility wrapper-deletion decision; any new findings spotted (logged to discovered_issues/log.jsonl)

## Coordination Touchpoints

- **PROJ-445 F-B-002 + F-B-003 + DI-2026-05-18-001 (engine handler half)**: PROJ-445 adds `ShipInstance` public delegators and the fleet-to-fleet branch. Task 2.4 here aligns the facade snapshot to what the new engine path enforces. Communicate sequencing via decisions.md.
- **PROJ-445 F-B-019**: PROJ-445 owns the Protocol docstring tightening on `IProductionResourceSource.production_consume_resource`. Task 2.3 here is the implementer fix site. Ideally land in the same week.
- **PROJ-445 F-B-013 + your Phase 3**: The staging-yard substrate change is a STRUCTURAL JOINT-PHASE in Phase 3. Do NOT touch `Planet._staging_yard` or `Planet.add_to_staging_yard` in Phase 2.

## Notes / Deferrals

- Wrapper retirement (F-A-002/003/004/005) is Phase 3.
- `Empire.resource_pool` profiling (F-A-011) is Phase 3.
- LOC extractions (F-A-008/009) is Phase 4.
