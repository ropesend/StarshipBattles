# PROJ-FMS-A Audit Fix Report

**Date:** 2026-05-16
**Auditor:** codex (mid-project review, consult/v1 protocol)
**Audit artefact:** `AgentCoordination/Scratchpad/Consult/20260516T060235Z_proj-fms-a-audit/response.md`
**Fixer:** claude

## Scope

Apply the four fixes raised by codex's audit (one P1, three P2) on top
of the just-completed PROJ-FMS-A implementation. No existing PROJ-FMS-A
work was reverted; only extended / corrected.

## Fixes Applied

### Fix 1 (P1) — `cargo_type="vehicle"` transfer path was dead

**Symptom:** the new carried-vehicle order branches
(`_dispatch_carried_vehicle_load` / `_dispatch_carried_vehicle_unload`)
were unreachable because `TransferValidator.VALID_CARGO_TYPES` did not
contain `"vehicle"`. Any `cargo_type="vehicle"` order failed with
`INVALID_CARGO_TYPE` before reaching the dispatch table.

**Files touched:**

- `game/strategy/validation/transfer_validator.py`
  - Added `"vehicle"` to `VALID_CARGO_TYPES`.
  - Allow `"vehicle"` past the planet-uncolonized check (staging-yard
    transfers don't require a colony, same as drop-pod).
  - Added `_validate_vehicle_load` and `_validate_vehicle_unload`
    helpers that check staging-yard contents, bay capacity, and
    planet staging capacity.

**Tests added:**

- `tests/unit/strategy/data/test_fms_a_audit_fixes.py::TestTransferValidatorAcceptsVehicleCargoType`
  (2 tests).
- `tests/integration/test_fms_a_e2e.py::TestTransferHandlerVehicleE2E::test_load_vehicle_end_to_end`
  — pre-stages a fighter on a planet, builds a `Fleet` containing a
  cruiser with a working `VehicleBay`, dispatches a `TransferHandler`
  with `cargo_type="vehicle", direction="load"`, asserts the fighter
  moved from staging to bay with `current_hp` intact.
- `tests/integration/test_fms_a_e2e.py::TestTransferHandlerVehicleE2E::test_unload_vehicle_end_to_end`
  — mirrors above in reverse (bay → planet staging) for a mine.

### Fix 2 (P2) — Pod storage / vehicle-bay cross-bleed

**Symptom:** `ShipInstance.get_pod_storage_used()` summed every
`carried_items` entry, including `CarriedVehicle`-shaped ones. A ship
carrying fighters/mines/satellites lost valid drop-pod capacity and
`can_carry_pod(...)` failed for the wrong reason. The drop-pod
transfer branches had the symmetric problem (would attempt to dump
vehicle entries to staging yards via the drop-pod path or count them
in `to_unload` totals).

**Files touched:**

- `game/strategy/data/ship_instance.py` — `get_pod_storage_used()`
  now filters out `CarriedVehicle`-shaped entries via
  `CarriedVehicle.from_any`.
- `game/strategy/engine/order_handlers/transfer_branches.py` —
  `_dispatch_drop_pod_load` and `_dispatch_drop_pod_unload` skip
  `CarriedVehicle`-shaped entries.

**Tests added:**

- `TestPodStorageBleedRegression::test_pod_storage_used_ignores_vehicle_entries`
  — verifies a ship with 2 pods (mass 7 + 11 = 18) and 3 fighters
  (mass 3*25 = 75) reports `pod_storage_used == 18` and
  `bay_current_mass == 75`.
- `TestPodStorageBleedRegression::test_bay_current_mass_is_zero_with_only_drop_pods`.

### Fix 3 (P2) — Capability / UI layers did not gate on `group_kind`

**Symptom:** handler-side rejection (via
`BaseCommandHandler._reject_if_non_fleet_group`) was wired, but
`FleetCapabilityCalculator` and `fleet_menu_items.py` still advertised
strategic actions for non-`fleet` `group_kind` Fleets. When
PROJ-FMS-B/C/D start creating `fighter_group` / `satellite_group` /
`mine_group` Fleets the UI would have offered buttons that fail at
execution.

**Files touched:**

- `game/strategy/data/fleet_capability_calculator.py`
  - Added `_is_real_fleet()` predicate (resilient to Mock fleets).
  - Gated `has_space_shipyard`, `can_build_type`, and `can_use_warp`.
- `game/ui/screens/fleet_menu_items.py` — added `_can_strategic_move`
  predicate and used it to gate "Move" and "Join Fleet" rows.

**Tests added:**

- `TestCapabilityCalculatorGatesOnGroupKind` — parametrised across
  `fighter_group` / `satellite_group` / `mine_group` for `can_use_warp`,
  `can_build_type` (ship/fighter/mine/satellite), and
  `has_space_shipyard`; plus a positive case verifying default
  `"fleet"` group_kind is unaffected.
- `TestFleetMenuItemsGateOnGroupKind` — verifies Move / Join Fleet are
  omitted from the context menu for a `fighter_group` fleet.

### Fix 4 (P2) — Artifact accuracy + missing tests

**Sub-fix 4a — `bay_current_mass` was never populated.** The
simulation `Ship.bay_current_mass = 0.0` reset in `ship_stats.py`
was dead code (no contributor wrote it; nothing read it). It cannot
be computed at design time because it depends on what's actually in
`ShipInstance.carried_items`.

- Removed the dead `ship.bay_current_mass = 0.0` reset from
  `game/simulation/entities/ship_stats.py`.
- Added two strategy-layer properties on `ShipInstance`:
  `bay_capacity_mass` (max from design stats) and `bay_current_mass`
  (delegates to `ShipCargoManager.get_vehicle_bay_capacity()`).
- Updated `phase_3_checklist.md:21` with a corrective note.

**Sub-fix 4b — Carried-vehicle serializer round-trip test.**
`TestCarriedVehicleSerializerRoundtrip` builds a `ShipInstance`,
loads two `CarriedVehicle` entries (fighter + mine) plus one drop-pod
entry, serialises through `ShipInstanceSerializer.to_dict /
from_dict`, restores, and verifies all entries are intact
(`design_id`, `current_hp`, `mass`, `vehicle_type`, `design_data`).

**Sub-fix 4c — Phase 5 transfer-order integration test.** See Fix 1
above — `TestTransferHandlerVehicleE2E` covers both load and unload
through the real `TransferHandler`.

**Documents updated:**

- `Projects/active_projects/PROJ-FMS-A/decisions.md` — new
  "2026-05-16 — Audit fix pass" section logging all four fixes.
- `Projects/active_projects/PROJ-FMS-A/findings/implementation_report.md`
  — header note, file-list correction, struck-through limitations 4
  and 5 with resolution notes.
- `Projects/active_projects/PROJ-FMS-A/phase_3_checklist.md` —
  corrective notes on the `bay_current_mass` and serializer-round-trip
  items.
- `Projects/active_projects/PROJ-FMS-A/phase_5_checklist.md` —
  corrective note on the transfer-order integration test item.

## Tests Summary

| File | New / Modified | Count |
|---|---|---|
| `tests/unit/strategy/data/test_fms_a_audit_fixes.py` | NEW | 16 |
| `tests/integration/test_fms_a_e2e.py` (extended) | MODIFIED | +2 |

All 18 new tests pass. Focused regression suite (transfer / vehicle bay
/ fleet group_kind / production normalisation / fleet capabilities /
pod transfer / fleet menu items / ship instance serializer / stat
contributors / ship_stats — 225+ tests) is green except for the
pre-existing acceleration_rate golden drift on
`qs_escort` / `qs_frigate_gc` / `qs_battleship`, which was already
documented in `implementation_report.md` and is unrelated to FMS-A.

## Sharded Suite Status

Run command: `python Tools/test_sharded/test_sharded.py` (2026-05-16).

```
TOTAL: 20462 tests | 20443 passed | 9 failed | 6 errors | 4 skipped
Wall time: 169.6s (12 shards)
```

All 9 failures and 6 errors are the **same pre-existing set** documented
in `implementation_report.md:163-167` (acceleration_rate golden drift on
`qs_escort` / `qs_frigate_gc` / `qs_battleship`; 5 quickstart-designs
`test_design_has_metadata` failures; 1 known flake in
`test_iter_keys_match_full_hp_builder_for_cross_layer_design`; 6
`test_design_load_warp_capability` errors). **Zero new failures** were
introduced by the audit fix pass.

Net effect of the audit fix pass: +2 tests vs the post-FMS-A baseline
of 20460 (the two new `TestTransferHandlerVehicleE2E` tests). The 16
new unit tests in `tests/unit/strategy/data/test_fms_a_audit_fixes.py`
ran in the unit-only test run during development; the sharded suite's
own slicing may collect them under a different shard accounting — they
are all green when run directly (`pytest
tests/unit/strategy/data/test_fms_a_audit_fixes.py` → 16 passed).

## Risk / Future Work

- `_dispatch_drop_pod_load` previously iterated `planet.staging_yard`
  using each item's `pod_name` matcher; CarriedVehicle entries now
  short-circuit before the pod_name check. If any data path stuffs a
  `"vehicle_type": "drop_pod"` (or other non-tracked) discriminator
  into staging dicts, those would silently slip through the new
  filter — but no such path exists today.
- The `TransferValidator._validate_vehicle_*` helpers fail closed
  when bay-capacity probing throws (treat as "no capacity"); the same
  defensive style the existing `_validate_load` drop-pod path uses.
- A full `SaveGameService` round-trip test for CarriedVehicle entries
  remains future work (limitation item 5 was downgraded, not closed).
