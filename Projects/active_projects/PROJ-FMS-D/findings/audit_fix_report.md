# PROJ-FMS-D Audit Fix Report

**Date:** 2026-05-16
**Source audit:** `AgentCoordination/Scratchpad/Consult/20260516T121544Z_proj-fms-d-audit/response.md`
**Scope:** Three remediations on top of the original PROJ-FMS-D
implementation (one P1 blocker + two P2 follow-ups). The P1 + first P2
sit in shared FMS-C/D infrastructure, so both fighter and satellite
flows benefit. No PROJ-FMS-A/B/C/D production work was reverted; this
pass is purely additive + behaviour-correcting.

## Audit summary

Codex's mid-project PROJ-FMS-D audit found:

- **P1** Overflow path in `fighter_reboard._build_overflow_ship_instance`
  dropped per-component damage state because it rebuilt the overflow
  `ShipInstance` from `design_data + current_hp` only and never
  reapplied `cv.component_states`. Affected both fighters AND
  satellites — any in-battle-launched vehicle that overflowed at
  battle end silently lost its damage state.
- **P2** `ship_cargo_manager` enforced typed-bay filtering as a
  ship-wide UNION, not as real per-bay allocation. A mixed-bay
  carrier (fighter-only + satellite-only bays) wrongly accepted
  either vehicle type up to the SUM of all bay capacities.
- **P2** Missing PROJ-FMS-D implementation report + stale baseline
  claim in `decisions.md` (no fresh sharded-suite receipt for the
  FMS-D tree).

## Fixes applied

### Fix 1 (P1) — Overflow path preserves per-component damage state

**Was.** `fighter_reboard._build_overflow_ship_instance` constructed
the overflow `ShipInstance` directly from `cv.design_id +
cv.design_data + cv.current_hp` and ignored `cv.component_states`. The
PROJ-FMS-C audit-fix pass had taught `_ship_to_carried_vehicle` to
capture `ship.components` into `cv.component_states`, and had also
taught `LaunchFightersOrderHandler._carried_vehicle_to_ship_instance`
to reapply them at strategic launch — but the overflow site never got
the same treatment, so the round-trip contract in
`phase_2_checklist.md:18-28` and `phase_3_checklist.md:28-35` was
broken: any fighter or satellite that overflowed into a new sector
group silently came back fully repaired.

**Fix.**

1. **New shared helper module** at
   `game/strategy/data/carried_vehicle_deploy.py`. Exports
   `carried_vehicle_to_ship_instance(cv, *, owner_id, registries)` and
   a `_safe` wrapper. The helper:
   - Picks the instance-id prefix from `cv.vehicle_type`
     (`fighter_*` vs `satellite_*`).
   - Preserves `cv.current_hp`.
   - Restores `cv.component_states` onto `ship.components` when
     present.
   - Sets `is_alive = True`, `is_derelict = False`.
   - Wires registries when supplied.

2. **All three call sites consolidated.**
   - `fighter_reboard._build_overflow_ship_instance` now delegates to
     `carried_vehicle_to_ship_instance_safe(cv, owner_id=...)`. This
     was the only site missing component-state restore, and the fix
     also makes the satellite overflow path land with a
     `satellite_*` instance-id (matching the strategic launch
     handler's convention).
   - `LaunchFightersOrderHandler._carried_vehicle_to_ship_instance`
     now delegates to the shared helper.
   - `LaunchSatellitesOrderHandler._carried_vehicle_to_ship_instance`
     now delegates to the shared helper.

3. **Side cleanup**: removed now-unused `uuid` import from
   `fighter_reboard.py`, `launch_fighters.py`, and
   `launch_satellites.py`.

**Files touched (Fix 1 production code).**
- NEW: `game/strategy/data/carried_vehicle_deploy.py`
- `game/simulation/systems/fighter_reboard.py` —
  `_build_overflow_ship_instance` rewritten as a thin wrapper.
- `game/strategy/engine/order_handlers/launch_fighters.py` —
  `_carried_vehicle_to_ship_instance` rewritten as a thin wrapper.
- `game/strategy/engine/order_handlers/launch_satellites.py` —
  `_carried_vehicle_to_ship_instance` rewritten as a thin wrapper.

**Tests added (Fix 1).**
- NEW: `tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py`
  with 3 tests:
  - `test_fighter_overflow_preserves_component_states` — damages a
    fighter, overflows it at battle end, inspects the overflow
    `ShipInstance.components` to verify the damage state survives.
  - `test_satellite_overflow_preserves_component_states` — same
    contract for satellites.
  - `test_overflow_no_components_is_fine` — empty `component_states`
    still overflows cleanly (no crash on stubs with no per-component
    data).

### Fix 2 (P2) — Per-bay typed capacity allocation

**Was.** `ShipCargoManager._allowed_vehicle_types()` unioned every
active bay's `allowed_types`; `can_accept_vehicle()` only checked the
aggregate `bay_capacity_mass`; `load_vehicle()` blindly appended to a
flat list. A carrier with one fighter-only bay (capacity 250) plus one
satellite-only bay (capacity 300) would accept 550 mass of fighters
because the union accepted fighters and the aggregate covered the sum.
The cited isolation test exercised only a universal bay, so this gap
slipped through.

**Fix.**

1. **New `_BaySlot` dataclass** internal to `ship_cargo_manager.py`
   capturing one bay's `index`, `allowed_types` (frozenset),
   `capacity_mass`, and live `current_mass`.

2. **`_enumerate_bays()` helper** walks the design (via
   `Ship.from_dict + recalculate_stats`) and returns one `_BaySlot`
   per active `VehicleBayAbility` in deterministic order (layer
   iteration + component-position-within-layer). The order is
   stable across calls so a save/load round-trip reproduces
   identical bay assignments without storing a per-CV bay index.

3. **`_assign_carried_to_bays(bays)`** packs existing
   `carried_items` into the enumerated bays using first-fit (in
   `carried_items` order), mutating each `_BaySlot.current_mass` so
   downstream checks see live remaining capacity.

4. **`can_accept_vehicle(vehicle)`** now returns True iff at least
   one bay accepts the vehicle's type AND has remaining capacity ≥
   `vehicle.mass` — no longer a ship-wide union + aggregate check.

5. **`load_vehicle(vehicle)`** walks bays in enumeration order and
   places the vehicle in the first accepting bay with sufficient
   remaining capacity. Fails fast (no append) if no bay qualifies.

6. **`get_vehicle_bay_capacity()`** now sums capacity from the
   enumerated bays (so the value stays consistent with the per-bay
   enforcement path); the cached `bay_capacity_mass` stat is still
   used as a fallback when registries / design aren't available
   (test fixtures with minimal stub designs).

7. **`_allowed_vehicle_types()` retained** as a backwards-compatible
   helper that unions every bay's allowed_types, but it is no longer
   the gating check. Inspection-only at this point.

**Files touched (Fix 2 production code).**
- `game/strategy/data/ship_cargo_manager.py` — restructured per-bay
  allocation with `_BaySlot` dataclass + helpers.

**Tests added (Fix 2).**
- NEW: `tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py`
  with 6 tests across three classes:
  - `TestMixedBayCarrier::test_fighter_only_bay_does_not_accept_satellite_within_its_capacity`
  - `TestMixedBayCarrier::test_satellite_only_bay_does_not_accept_fighter_within_its_capacity`
  - `TestMixedBayCarrier::test_each_type_fills_its_own_bay_independently`
  - `TestMixedBayCarrier::test_unload_returns_capacity_to_the_correct_bay`
  - `TestUniversalBay::test_universal_bay_accepts_both_types_to_aggregate_cap`
  - `TestSingleTypedBay::test_fighter_only_carrier_rejects_satellite`
- MODIFIED `tests/integration/test_fms_cd_isolation.py` —
  added `test_mixed_bay_carrier_isolates_per_type_capacity` that
  builds a real `ShipInstance` carrier with one `fighter_bay_small`
  + one `satellite_bay_small` and verifies cross-type capacity
  isolation (previously the test file used only a stubbed cargo
  manager, which didn't exercise the production cargo-manager
  enforcement at all).

### Fix 3 (P2) — Project artifacts corrected

- NEW: `Projects/active_projects/PROJ-FMS-D/findings/implementation_report.md`
  documenting all three FMS-D phases + the audit-fix pass, with a
  real sharded-suite receipt (20646 / 20627 / 9 / 6 / 4 — see below).
- This file (`audit_fix_report.md`) created to mirror the
  PROJ-FMS-C audit-fix structure.
- `decisions.md` gained a `2026-05-16 — Audit fix pass` section
  documenting the placement rule (deterministic first-fit, stable
  across save/load) and the shared-helper decision (one helper
  module, three call sites).
- `plan.md` Current State note unchanged in intent but now
  references the just-created implementation report.

## Sharded suite status (post audit-fix pass)

Run command: `python Tools/test_sharded/test_sharded.py` (2026-05-16,
post audit-fix pass).

```
TOTAL: 20646 tests | 20627 passed | 9 failed | 6 errors | 4 skipped
Wall time: 138.5s (12 shards)
```

Carry-forward (vs PROJ-FMS-C audit baseline 20568 / 20549 / 9 / 6 / 4):
+78 total / +78 passing / same 9 failed + 6 errors + 4 skipped. All
failures + errors are pre-existing data-debt items (`acceleration_rate`
golden divergence on 3 designs, 5 missing `_metadata` blocks in
quickstart designs, missing `FR Frigate GC.json` test fixture, and the
known `test_iter_keys_match_full_hp_builder_for_cross_layer_design`
cross-layer-design flake). Zero new failures from PROJ-FMS-D or the
audit-fix pass.

## What is NOT in this pass

- Pygame UI bindings for player-facing satellite launch / recover
  actions (same gap as PROJ-FMS-C fighters).
- Carrier auto-launch policy tuning.
- Manual in-game smoke verification of the full
  design → bay → launch → fight → reboard → recover → save/load loop.
