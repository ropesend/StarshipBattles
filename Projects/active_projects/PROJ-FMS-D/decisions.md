# PROJ-FMS-D Decisions Log

Project-local decisions made during satellite implementation. Cross-project decisions live in [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md).

## 2026-05-15 — Project scaffolded

Source: claude/codex inter-agent discussion at `AgentCoordination/Scratchpad/Discussion/20260516T033452Z_fighters-mines-satellites/`.

## Implementation decisions

### 2026-05-16 — Phase 1+2+3 shipped

- **Bay separation mechanism: shared `VehicleBayAbility` with
  `allowed_types`.** PROJ-FMS-A already shipped the typed-bay surface
  with the `allowed_types: List[str]` field. PROJ-FMS-D Phase 1 adds
  data-side variants (`fighter_bay_small`, `satellite_bay_small` /
  `_medium` / `_large`) alongside the existing universal
  `vehicle_bay_*` entries. No new ability class; the bay-side filter
  in `ShipCargoManager.can_accept_vehicle` was already wired by
  PROJ-FMS-A Phase 3.
- **No retro-tag of fighter launch bays.** The shipped
  `fighter_launch_bay_small` component carries `StrategicFighterLaunch`
  / `TacticalFighterLaunch` but NO `VehicleBay` ability. Storage is
  always a separate component (`vehicle_bay_*` for universal,
  `fighter_bay_small` for fighter-only, `satellite_bay_*` for
  satellite-only). The audit-fix-removed legacy `fighter_launch_bay`
  is gone; nothing to retro-tag.
- **`satellite_group` fleet id namespace = 300000+.** mine_group lives
  at 100000+, fighter_group at 200000+, satellite_group at 300000+ so
  every PROJ-FMS unit type's launched-group id is unambiguous on
  inspection.
- **Stationary AI: dedicated `SatelliteAIController` class.** The base
  `AIController` already short-circuits behaviour execution for
  `Satellite`-typed ships at `controller.py:361-363`, but the dedicated
  controller adds: (a) explicit zero-throttle / zero-turn-throttle
  every tick (defensive against state leakage from a prior controller
  swap), (b) no avoidance / formation logic, (c) symmetric shape with
  `FighterAIController` so future per-type AI tuning has a home.
- **Generalised reboard hook rather than parallel module.** The
  PROJ-FMS-C `fighter_reboard.py` module was made vehicle-type aware
  rather than copied. `_ship_to_carried_vehicle` now reads
  `ship.vehicle_type` to classify the CarriedVehicle as `"fighter"` or
  `"satellite"`; `_ensure_overflow_group` is parameterised over
  `vehicle_type` and mints the appropriate group_kind (and id
  namespace). The legacy `_ensure_overflow_fighter_group` symbol is
  kept as a thin alias for PROJ-FMS-C callers / tests. File name
  retained (`fighter_reboard.py`) to keep the audit-fix-pass module
  layout intact; the module docstring was updated.
- **`CarrierAIController` extended, not split.** The same controller
  now drives both fighter and satellite tactical launches via the
  shared `_maybe_launch_wave(ability_name, vehicle_type,
  launch_method_name)` helper. Per-tick cooldown is shared across both
  vehicle types: a carrier mounting both ability sets alternates by
  exhausting one wave's cooldown before launching the other. Factory
  dispatch (`_ship_has_tactical_launch`) accepts either ability.
- **Ability-lookup gating closed for both new OrderTypes.**
  `LaunchSatellitesCommandHandler` declares
  `action_ability_name='StrategicSatelliteLaunch'`;
  `RecoverSatellitesCommandHandler` declares
  `action_ability_name='RecoverSatellites'`. Neither is exempted in
  `_ABILITY_LOOKUP_EXEMPT` in
  `test_command_registry_contract.py`. Same closing-the-loophole shape
  as PROJ-FMS-C audit Fix did for fighters.
- **No new dedicated `SatelliteCarrierAIController`.** The
  PROJ-FMS-C `CarrierAIController` was generalised in place rather
  than split into a fighter-specific and satellite-specific subclass.
  Reason: every wire-up (factory dispatch, engine reference, cooldown
  state) is identical; the only per-type variance is the ability
  name + vehicle_type + launch method, which the new
  `_maybe_launch_wave` helper accepts as parameters. Keeps the class
  count and the AI factory's dispatch table flat.
- **Spawn pattern in tactical combat: carrier-position + random
  offset.** Same as fighter launches — reuses
  `attack_processor.process_launch_attack` unchanged. No
  satellite-specific scatter pattern in this phase; the gameplay
  manual smoke list flagged this as a possible polish item if
  satellites visually overlap too aggressively on the carrier's hex.
- **Two pre-existing baseline failures from the PROJ-FMS-C baseline
  carry over unchanged at PROJ-FMS-D ship time:** the `test_iter_keys_match_full_hp_builder_for_cross_layer_design`
  flake and the 6 `test_design_load_warp_capability` errors (missing
  `FR Frigate GC.json`). No new regressions introduced by PROJ-FMS-D.
  **Resolved 2026-05-16 in a follow-up test-baseline cleanup pass** (see
  section below).

### 2026-05-16 — Audit fix pass

Source: codex mid-project audit at
`AgentCoordination/Scratchpad/Consult/20260516T121544Z_proj-fms-d-audit/response.md`.
Full remediation details live in
[`findings/audit_fix_report.md`](findings/audit_fix_report.md). Key
decisions captured here:

- **Single shared `CarriedVehicle -> ShipInstance` helper.** The
  P1 fix (overflow path dropped per-component damage state) is
  generalised at the source: a new module
  `game/strategy/data/carried_vehicle_deploy.py` exports
  `carried_vehicle_to_ship_instance(...)` and is called from all
  three sites that materialise a deployed `ShipInstance` from a
  `CarriedVehicle` (strategic fighter launch, strategic satellite
  launch, post-battle overflow). The duplicated per-site code was
  the root cause of the audit drift; consolidating into one helper
  prevents a future hand-rolled copy from drifting again.

- **Per-bay typed allocation rule: deterministic first-fit, no
  CarriedVehicle schema change.** The P2 fix
  (`ship_cargo_manager` ship-wide union accepted typed cargo across
  bays) is implemented by enumerating bays in design layer order
  + component-position-within-layer (stable across calls) and
  packing `carried_items` into them first-fit on every load/check.
  Decision: do NOT store a per-CV `bay_index` on the
  `CarriedVehicle` dict. The deterministic enumeration order lets
  a save/load round-trip reconstruct identical bay assignments
  without a schema change, keeping the existing fleet save/load
  path compatible.

- **`get_vehicle_bay_capacity()` derives max from enumerated bays,
  not the cached stat.** The aggregate `bay_capacity_mass` stat (set
  by `stat_contributors/launch.py`) remains for design-time UI
  display, but the cargo manager now sums per-bay capacities
  directly so the value stays consistent with the per-bay
  enforcement path. When registries / design aren't available
  (minimal test fixtures), the cached stat is still used as
  fallback.

- **Sharded suite carry-forward verified post-audit.** Full sharded
  run on 2026-05-16 after the audit-fix pass reports
  `20646 tests | 20627 passed | 9 failed | 6 errors | 4 skipped`
  (vs PROJ-FMS-C baseline `20568 / 20549 / 9 / 6 / 4`). +78 new
  tests, +78 passing, zero new regressions. The 9 failures + 6
  errors are the same pre-existing data-debt set documented in
  PROJ-FMS-C. Receipt: `findings/implementation_report.md`.

### 2026-05-16 — Post-PROJ-FMS test-baseline cleanup pass

Source: QA-driven triage of the 13 failures + 9 errors that were tracked
as "pre-existing baseline" through all four PROJ-FMS projects + the two
QA fix rounds. Both an independent subagent and a codex consult
investigated each failure in parallel and converged on the verdicts.

Outcomes (all four were fixture/snapshot drift, not engine regressions):

- `test_design_has_metadata` (8 fails): relaxed assertion to "if
  `_metadata` is present, must contain `is_obsolete` + `times_built`".
  Matches production code (`DesignMetadata.from_design_file:126-139`)
  which defaults every read with `.get()`. The 8 designs emitted by
  `ShipSerializer.to_dict()` (which writes `_format_version` only) and
  never round-tripped through `DesignLibrary.save_design()` are
  legitimate per the new contract.

- `test_iter_keys_match_full_hp_builder_for_cross_layer_design`
  (1 fail): removed the `('battery', 1)` precondition assertion.
  Commit `2b0562ca0` (2026-05-14) reduced `qs_battleship.json` from
  two batteries to one; the meaningful cross-layer-uniqueness coverage
  already lives in the sibling test
  `test_cross_layer_component_ids_use_ship_wide_instance_index`
  with a synthetic fixture.

- `test_design_load_warp_capability.py` (6 errors): repointed fixture
  path from the deleted `FR Frigate GC.json` to `qs_frigate_gc.json`.
  Fresh recompute showed actual mass is `1999.43` (under the 2000 Frigate
  class limit) — the only thing making it appear over-mass was the stale
  golden snapshot from the same era.

- `test_ship_stats_match_golden` (4 fails for `qs_escort`,
  `qs_frigate_gc`, `qs_battleship`, `qs_carrier`): regenerated
  `tests/unit/simulation/entities/test_ship_stats_golden_snapshot.json`
  via a one-shot helper. Each drift verified arithmetically against the
  live `(thrust * 2500) / mass^2` formula. Engine math
  (`physics_constants.py`, `ship_design_stats.py`) was unchanged by
  PROJ-FMS or the maintenance abstraction.

**Final sharded suite after cleanup**:
`20822 tests | 20818 passed | 0 failed | 0 errors | 4 skipped`.
First fully-green baseline since before the PROJ-FMS sequence began.

> **Round 4 update (2026-05-17):** the four-round QA pass that
> followed (maintenance abstraction, build-queue facade fixes,
> polymorphic IIssuerAdapter + component consolidation, tactical
> launch mass-budget rewrite) added enough new tests to bring the
> current sharded baseline to **20840 / 20840 passed / 0 failed /
> 0 errors / 0 skipped**. The 20822/20818 figure above remains
> accurate at PROJ-FMS-D ship time + audit fix.

## 2026-05-17 — Round 4 follow-up

Banner: the phase decisions above describe PROJ-FMS-D as shipped.
Round 4 QA made substantive cross-cutting changes that supersede
several of the bay / launch / stat decisions; the historical
decisions remain accurate at their snapshot time.

- **Bay separation mechanism consolidated (Obs C):** the per-tier
  `satellite_bay_small / _medium / _large` set was collapsed to a
  single `satellite_bay` whose capacity scales via `simple_size_mount`
  and the new `bay_capacity_mult` stat key; the same consolidation
  ran for `fighter_bay`, `vehicle_bay`, and the new mine-only
  `mine_bay`. The earlier "shared `VehicleBayAbility` with
  `allowed_types`" decision still holds; only the per-tier component
  data was removed.
- **Launch bay collocates recovery (Obs C):** `satellite_launch_bay`
  now ALSO carries `RecoverSatellites`; the standalone
  `satellite_recovery_bay_small` was deleted. Same change ran for
  fighters (`fighter_launch_bay` now carries `RecoverFighters`;
  `fighter_recovery_bay_small` deleted).
- **CarrierAIController rewrite (Obs C):** the shared
  `_maybe_launch_wave(ability_name, vehicle_type, launch_method_name)`
  helper was rewritten from a count-per-cycle + cooldown model to a
  per-tick mass-tons/sec budget. Carrier-side ship-stat fields
  renamed (`satellites_per_wave` / `satellite_launch_cycle` →
  single `satellite_launch_rate_tons_per_sec`; same for fighters).
  The "alternating per-tick cooldown" mental model is gone — each
  vehicle type accumulates its own budget independently.
- **Polymorphic order issuer (Obs B):** `IssueLaunchSatellitesCommand`
  and `IssueRecoverSatellitesCommand` gained an optional `planet_id`
  alongside `fleet_id` (exactly one set), and `count` is now
  `Optional[int] = None` (None = ALL matching). The
  `LaunchSatellitesOrderHandler` and `RecoverSatellitesOrderHandler`
  operate on `IIssuerAdapter`
  (`game/strategy/engine/issuer_adapter.py`) so a planet facility
  with `StrategicSatelliteLaunch` / `RecoverSatellites` can act via
  the same handler.
