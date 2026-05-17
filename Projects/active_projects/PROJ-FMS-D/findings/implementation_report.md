# PROJ-FMS-D Implementation Report

**Date:** 2026-05-16
**Scope:** Satellites end-to-end (strategic + tactical launch, stationary
AI, recovery / reboard, cross-type isolation), plus the audit-fix pass
that landed on top of the initial implementation.

## Summary

Phase 1 (strategic + tactical satellite launch + stationary AI),
Phase 2 (recovery + end-of-battle reboard for satellites), and Phase 3
(integration tests + cross-type isolation) shipped together in a single
multi-phase pass. Satellites mirror fighters with three documented
differences: stationary tactical AI, separate ability gate, and the
``satellite_group`` fleet id namespace (300000+).

A codex mid-project audit at
`AgentCoordination/Scratchpad/Consult/20260516T121544Z_proj-fms-d-audit/response.md`
identified one P1 blocker plus two P2 follow-ups in shared FMS-C/D
infrastructure. Those were corrected in the audit-fix pass on the same
day (2026-05-16); see [`audit_fix_report.md`](audit_fix_report.md) for
details.

## Phase-by-phase deliverables

### Phase 1 — Strategic + tactical satellite launch + stationary AI

- New strategic order handler at
  `game/strategy/engine/order_handlers/launch_satellites.py`
  (`LaunchSatellitesOrderHandler`). Pops typed satellite CVs from the
  carrier's bay, mints a fresh `satellite_group` Fleet in the
  300000+ id namespace, materialises each CV into a deployed
  `ShipInstance` (now via the shared
  `carried_vehicle_to_ship_instance` helper added in the audit-fix
  pass — see [`audit_fix_report.md`](audit_fix_report.md)).
- Command handler at `game/strategy/engine/handlers/launch_satellites.py`
  with `@command_spec(action_ability_name='StrategicSatelliteLaunch')`,
  removed from `_ABILITY_LOOKUP_EXEMPT` in the contract test (same
  shape as PROJ-FMS-C audit Fix for fighters).
- Stationary tactical AI at `game/ai/satellite_controller.py`
  (`SatelliteAIController`) — explicit zero throttle / zero turn each
  tick (defensive against state leakage from controller swaps), no
  avoidance / formation logic, symmetric shape to
  `FighterAIController`.
- `AIControllerFactory` dispatches `vehicle_type == "Satellite"` to
  `SatelliteAIController`, and the carrier-capable predicate accepts
  either tactical launch ability.
- `CarrierAIController` generalised in place (no separate subclass) via
  the shared `_maybe_launch_wave(ability_name, vehicle_type,
  launch_method_name)` helper so the same controller drives both
  fighter and satellite tactical launches.
- Data: `satellite_bay_small` (300 mass / satellite-only),
  `satellite_bay_medium` (800), `satellite_bay_large` (2100), and
  matching `fighter_bay_small` for clean cross-type pairing in tests.
  **Superseded by Round 4 Obs C:** the per-tier
  `satellite_bay_small/medium/large` set was collapsed to a single
  `satellite_bay` (and `fighter_bay_small` to `fighter_bay`) whose
  capacity scales via the `simple_size_mount` modifier and the new
  `bay_capacity_mult` stat key. A new mine-only `mine_bay` was added
  in the same pass. See `decisions.md` "2026-05-17 — Round 4 follow-up".
- `OrderType.LAUNCH_SATELLITES` added to `ACTION_ORDER_TYPES`; spec
  compiler passes `satellite_group` fleets through (filter excludes
  only `mine_group`).

### Phase 2 — Recovery (separate ability gate from fighters)

- New strategic order handler at
  `game/strategy/engine/order_handlers/recover_satellites.py`
  (`RecoverSatellitesOrderHandler`) — captures `ship.components` into
  `CarriedVehicle.component_states` on recovery, parallel to the
  fighter handler.
- Command handler at
  `game/strategy/engine/handlers/recover_satellites.py` with
  `@command_spec(action_ability_name='RecoverSatellites')`, also
  removed from `_ABILITY_LOOKUP_EXEMPT`.
- `RecoverSatellitesAbility` (separate ability class from
  `RecoverFightersAbility`) — a fighter-only carrier cannot recover
  satellites and vice versa.
- `fighter_reboard.py` generalised to handle both vehicle types
  rather than copied to a sibling module: `_ship_to_carried_vehicle`
  dispatches on `ship.vehicle_type`, `_ensure_overflow_group` is
  parameterised over `vehicle_type` and selects `fighter_group` vs
  `satellite_group` accordingly. The legacy
  `_ensure_overflow_fighter_group` symbol is retained as a
  backwards-compat alias.

### Phase 3 — Integration tests + cross-type isolation

- `tests/integration/test_fms_d_e2e.py` — strategic launch +
  recovery round trip for satellites.
- `tests/integration/test_fms_d_launch_in_battle_e2e.py` — tactical
  launch through the battle engine + reboard.
- `tests/integration/test_fms_cd_isolation.py` — cross-type isolation
  (fighter-only carrier refuses satellites, satellite-only carrier
  refuses fighters, mixed-bay carrier isolates per-type capacity, etc).
  The mixed-bay-carrier test was strengthened in the audit-fix pass
  to use a real `ShipInstance` with separate fighter-only +
  satellite-only bays (see [`audit_fix_report.md`](audit_fix_report.md)).
- Five new ship designs added to the data library
  (`data/designs/qs_*`) demonstrating typed-bay variants.

## Shared FMS-C/D infrastructure touched

The following modules were generalised across fighter + satellite
flows in this project (NOT copied to satellite-specific siblings):

- `game/simulation/systems/fighter_reboard.py` — dispatches on
  `cv.vehicle_type` to pick overflow group kind and id namespace.
- `game/ai/carrier_controller.py` — `_maybe_launch_wave(ability_name,
  vehicle_type, launch_method_name)` parameterised over both vehicle
  types.
- `game/ai/ai_factory.py` — carrier-capable predicate accepts either
  `TacticalFighterLaunch` or `TacticalSatelliteLaunch`.
- `game/strategy/data/ship_cargo_manager.py` — now enforces per-bay
  typed allocation (audit Fix 2; see
  [`audit_fix_report.md`](audit_fix_report.md)).
- `game/strategy/data/carried_vehicle_deploy.py` (new) — shared helper
  for materialising a deployed `ShipInstance` from a `CarriedVehicle`,
  consolidating logic previously duplicated across three call sites
  (audit Fix 1; see [`audit_fix_report.md`](audit_fix_report.md)).

## Tests added

| Test file | New tests |
|-----------|-----------|
| `tests/unit/simulation/systems/test_satellite_reboard.py` | 5 |
| `tests/unit/simulation/systems/test_fighter_reboard_overflow_component_state.py` (audit fix) | 3 |
| `tests/unit/strategy/data/test_ship_cargo_manager_per_bay.py` (audit fix) | 6 |
| `tests/unit/strategy/engine/order_handlers/test_launch_satellites_handler.py` | 8 |
| `tests/unit/strategy/engine/order_handlers/test_recover_satellites_handler.py` | 8 |
| `tests/unit/strategy/engine/handlers/test_launch_satellites_command_handler.py` | 4 |
| `tests/unit/strategy/engine/handlers/test_recover_satellites_command_handler.py` | 4 |
| `tests/unit/ai/test_satellite_controller.py` | 4 |
| `tests/integration/test_fms_d_e2e.py` | 4 |
| `tests/integration/test_fms_d_launch_in_battle_e2e.py` | 3 |
| `tests/integration/test_fms_cd_isolation.py` | 5 |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | MODIFIED |
| `tests/unit/strategy/engine/test_command_registry_seeding.py` | MODIFIED |
| `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | MODIFIED |

## Sharded suite status

Run command: `python Tools/test_sharded/test_sharded.py` (2026-05-16,
post audit-fix pass).

```
TOTAL: 20646 tests | 20627 passed | 9 failed | 6 errors | 4 skipped
Wall time: 138.5s (12 shards)
```

Compared to the PROJ-FMS-C post-audit baseline (20568 / 20549 / 9 / 6 / 4):

- **Test count: 20568 → 20646 (+78 net).** PROJ-FMS-D Phases 1–3 add
  ~63 new tests (satellite reboard, satellite controller, satellite
  handlers, cross-type isolation, FMS-D e2e + in-battle e2e), plus
  the audit-fix pass adds 9 tests (overflow component-state and
  per-bay typed allocation) and the existing fms_cd_isolation gained
  the mixed-bay carrier scenario.
- **Passed: 20549 → 20627 (+78 passing).**
- **Failed: 9 → 9 (same pre-existing).**
- **Errors: 6 → 6 (same pre-existing).**
- **Skipped: 4 → 4 (unchanged).**
- **Zero new failures from PROJ-FMS-D or the audit-fix pass.**

All 9 failures + 6 errors are the **same pre-existing set** documented
in `Projects/active_projects/PROJ-FMS-C/findings/implementation_report.md`:

- 3 `test_ship_stats_golden::acceleration_rate` (qs_escort,
  qs_frigate_gc, qs_battleship).
- 5 `test_quickstart_designs::test_design_has_metadata` (the same
  five quickstart designs lacking a `_metadata` block in their
  design json — pre-existing data debt).
- 1 `test_iter_keys_match_full_hp_builder_for_cross_layer_design`
  flake (PROJ-FMS-C decisions.md identifies it as a flake).
- 6 `test_design_load_warp_capability` errors (missing
  `FR Frigate GC.json` fixture — pre-existing).

## Known limitations

- ~~No pygame UI binding for player-facing satellite launch / recover
  actions. Facade dispatch helpers and the strategic command surface
  are production-reachable via the AI path (CarrierAIController);
  pygame UI binding is a follow-up.~~ **Partially closed by Round 4
  (Obs B):** the fleet right-click menu and the new planet right-click
  menu now expose Launch Satellites / Recover Satellites rows (plus
  the Lay Mines / Launch Fighters / Recover Fighters peers) via
  `game/ui/screens/planet_menu_items.py`,
  `game/ui/screens/planet_context_menu.py`, and the shared
  `game/ui/screens/fms_menu_callbacks.py`.
- Carrier auto-launch policy is naive: the
  `_maybe_launch_wave` helper fires whenever an enemy is within
  launch radius + cooldown is ready. No wave-size targeting,
  escort-vs-intercept priorities, or combat-state-aware holds.
- Manual in-game smoke verification of the full
  design → bay → launch → fight → reboard → recover → save/load loop
  is deferred; the integration tests cover each leg in isolation +
  the FMS-D e2e tests stitch them together programmatically.

## Postscript (2026-05-17 final state)

The sharded-suite numbers earlier in this report (20646 / 20627, etc.)
are an accurate snapshot at PROJ-FMS-D ship time. The final clean
baseline after the dedicated test-baseline cleanup pass plus the
four QA rounds is **20840 / 20840 passed / 0 failed / 0 errors /
0 skipped** — see `decisions.md` "Post-PROJ-FMS test-baseline
cleanup pass" and "2026-05-17 — Round 4 follow-up". Intermediate
baselines quoted in A/B/C implementation reports (20460, 20525,
20568) are likewise correct at their respective snapshot times.
