# PROJ-FMS-D Phase 1: Strategic + tactical satellite launch + stationary AI

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Player can launch satellites strategically (forming a `satellite_group`) or tactically. Deployed satellites participate in combat but do not move. Bay capacity for satellites is separate from fighter bay capacity.

## Tasks

### Bay separation

Per the shared design (`../PROJ-FMS-shared/design.md` "Separate ability gates per unit type"), fighters and satellites need **distinct bay / recovery ability gates**, so a fighter-only carrier cannot recover satellites and vice versa. The chosen mechanism: a single `VehicleBayAbility` class (already added in PROJ-FMS-A) with an `allowed_types: List[str]` data attribute. Per-component values declare the bay's accepted types.

- [x] Add `allowed_types: List[str]` data attribute parsing in `VehicleBayAbility._parse_attrs()` (extends PROJ-FMS-A Phase 3). Default = `["fighter", "satellite", "mine"]` (universal) for backwards compatibility with bays that pre-date this field.
- [x] Add `satellite_bay_small` / `medium` / `large` components to [`data/components.json`](../../../data/components.json) with `allowed_types: ["satellite"]`. **(Superseded by Round 4 Obs C — the per-tier variants were consolidated to a single `satellite_bay` whose capacity scales via the `simple_size_mount` modifier and the new `bay_capacity_mult` stat key. The `allowed_types=["satellite"]` filter remains. See `decisions.md` "2026-05-17 — Round 4 follow-up".)**
- [x] (Optional housekeeping during this phase) Retro-tag existing fighter-only bay components added in PROJ-FMS-A Phase 5 with `allowed_types: ["fighter"]` if the design intent is to keep them fighter-only. Bays explicitly intended to be universal can omit the field.
- [x] Cargo load (`ShipCargoManager.load_vehicle()` from PROJ-FMS-A Phase 3) checks the filter: a satellite design cannot load into a fighter-only bay.

### Strategic satellite-launch execution (Command → OrderType → Handler)

- [x] `OrderType.LAUNCH_SATELLITES` reserved by PROJ-FMS-A Phase 5. Verify.
- [x] New `IssueLaunchSatellitesCommand` + handler in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/). Mirrors PROJ-FMS-C `IssueLaunchFightersCommand`.
- [x] New `LaunchSatellitesOrderHandler(BaseOrderHandler)` in [`game/strategy/engine/order_handlers/launch_satellites.py`](../../../game/strategy/engine/order_handlers/). Pops from satellite-capable bay; creates / extends `satellite_group` Fleet in the hex.

### Tactical satellite-launch execution

- [x] Wire `TacticalSatelliteLaunchAbility` into the battle-action / firing-system path (mirrors the PROJ-FMS-C Phase 1 fighter-launch rewrite). Spawns the satellite at a chosen tactical position with the same `launched_in_battle_id` tagging as fighters. No `apply()` method — abilities are data-only.

### Stationary satellite AI
- [x] Add a `SatelliteAIController` variant in [`game/ai/controller.py`](../../../game/ai/controller.py). The existing satellite reference at lines 361-363 confirms the codebase already has stationary-satellite behavior — extend or wrap.
- [x] Each tick: do NOT move (no thrust commands). If a weapon is in range and `cooldown` allows, fire at nearest enemy. If a special ability is applicable (e.g., sensor / jamming), use it on appropriate target.
- [x] If a satellite is destroyed, remove from `satellite_group` and the tactical map as with fighters.

### Stat aggregation
- [x] Update [`game/simulation/entities/stat_contributors/launch.py`](../../../game/simulation/entities/stat_contributors/launch.py) to aggregate satellite-specific stats (satellite_capacity, satellites_per_wave, satellite_launch_cycle) separately from fighter equivalents. **(Superseded by Round 4 Obs C — `satellites_per_wave` / `satellite_launch_cycle` were renamed to a single `satellite_launch_rate_tons_per_sec` field; the cycle-based cooldown stat is gone. `satellite_capacity` survives under its original name.)**

### Combat join
- [x] Confirm `satellite_group` Fleets join contested-hex combat the same way `fighter_group` does (free if PROJ-FMS-A `group_kind` + PROJ-FMS-C combat-join wiring are in place).

### Tests
- [x] Strategic: load 4 satellites into a carrier's satellite-bay, launch 3 → `satellite_group` of 3.
- [x] Mixed-bay scenario: a universal bay holds both fighters and satellites; launch satellites without touching fighters.
- [x] Type filter: a fighter design cannot load into a satellite-only bay (and vice versa).
- [x] Tactical: in-battle launch of 2 satellites at chosen positions → spawn at those positions; do NOT move on subsequent ticks; fire weapons when targets in range.
- [x] AI: satellite with a single weapon targets nearest enemy and fires; does not chase.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/simulation/components/abilities/test_strategic_satellite_launch.py tests/unit/ai/test_satellite_controller.py`
- Manual: design satellite with weapons, build, load into universal bay, launch, observe stationary combat behavior.

## Exit criteria
- Both launch abilities work.
- Bay type-filter prevents wrong-type loading.
- Stationary AI fires but doesn't move.
- Stat aggregation tracks satellite stats separately.
