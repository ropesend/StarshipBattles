# PROJ-FMS-A Phase 4: Fleet `group_kind` + signature_bonus + production normalisation

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Three independent-but-related plumbing changes that finish the foundation:
1. Add a `group_kind` discriminator to `Fleet` with order-validation invariant for non-fleet kinds.
2. Wire vehicle-class `signature_bonus` into `total_defense_score`.
3. Normalise production output across planet and fleet-yard paths.

## Tasks

### 1. Fleet `group_kind`
- [x] Add `group_kind: str = "fleet"` field to `Fleet.__init__` at [`fleet.py:39-93`](../../../game/strategy/data/fleet.py#L39). Valid values: `"fleet"`, `"fighter_group"`, `"satellite_group"`, `"mine_group"`.
- [x] Add `can_strategic_move` property: returns `self.group_kind == "fleet"`.
- [x] **Reject more than just Move/Path** — non-fleet `group_kind`s should reject the full set of fleet-management commands. Add validation rejection in the relevant command handlers in [`game/strategy/engine/handlers/`](../../../game/strategy/engine/handlers/):
  - [`movement.py:87-225`](../../../game/strategy/engine/handlers/movement.py#L87) — `IssueMoveCommand`, `IssueInterceptCommand`, `IssueJoinFleetCommand`, `IssueWarpCommand`
  - [`build.py:26-53`](../../../game/strategy/engine/handlers/build.py#L26) — `IssueBuildOrderCommand` (non-fleet groups cannot have build queues)
  - Any other commands assuming "fleet has crew / movement / build". The validation should check `fleet.can_strategic_move` and the implicit "is a real fleet" semantics; return a clear `ValidationResult` failure.
- [x] Serialize / deserialize `group_kind` through fleet save/load (Fleet's existing serialization delegate).
- [x] DTO: [`fleet_dto.py`](../../../game/strategy/facade/dto/fleet_dto.py) — surface `group_kind` so UI can render deployed groups differently from fleets.
- [x] Make sure [`FleetCapabilityCalculator`](../../../game/strategy/data/fleet_capability_calculator.py) and related delegates don't crash on non-fleet kinds (some capabilities won't apply — e.g., mine groups have no warp drive). Defensive: capabilities that conceptually don't apply (warp, build, recovery, etc.) return False / empty for non-fleet kinds without raising.

### 2. signature_bonus wiring
- [x] Read the vehicle class data (loaded via [`vehicleclasses.json`](../../../data/vehicleclasses.json)) and expose `signature_bonus` on the `Ship` entity (probably via the existing vehicle-class data flow into `Ship.__init__`).
- [x] Extend the defense-score aggregation at [`ship_stats.py:424-444`](../../../game/simulation/entities/ship_stats.py#L424). Current aggregation: `total_defense_score = size_score + maneuver_score + ecm_score`. New: `total_defense_score = size_score + maneuver_score + ecm_score + signature_bonus`. Default `signature_bonus = 0` for non-mine classes — no behavior change for existing ships.
- [x] Verify mine designs see a meaningful boost (~+3 from class bonus on top of the ~+4 from tiny `size_score`).

### 3. Production output normalisation
- [x] Audit [`production_spawner.py:107-117`](../../../game/strategy/engine/production_spawner.py#L107) for the current split: colony-built fighters → staging, satellites → active ship, fleet-built fighters → fleet. Document the current behavior in [`decisions.md`](decisions.md) before changing.

**Note on fleet production model**: fleet production is **one shared fleet queue** whose rate scales with yard count ([`production_engine.py:235-240`](../../../game/strategy/engine/production_engine.py#L235), [`build_queue_source.py:362-383`](../../../game/strategy/data/build_queue_source.py#L362)). There is no per-ship producer concept today. The "producing ship's bay" phrasing must therefore be replaced with a deterministic fleet-level bay-selection rule.

- [x] Replace with unified rule:
  - **Planet-built** fighter/satellite/mine → goes into the producing planet's `Planet.staging_yard` as a `CarriedVehicle`.
  - **Fleet-yard-built** fighter/satellite/mine → fleet-level bay-selection rule:
    1. Try the flagship's `VehicleBay` first (if it has capacity and accepts the vehicle type).
    2. Otherwise, walk `fleet.ships` in canonical order; deposit into the first ship whose `VehicleBay` has capacity and accepts the vehicle type.
    3. If no ship in the fleet has compatible bay capacity, fail the production order with a clear "no bay capacity" error and surface a UI event.
  - Document the chosen rule and rationale in [`decisions.md`](decisions.md).
- [x] Capital ships and other large vehicles continue to spawn as full `ShipInstance` entries — the rule only applies to small craft (fighters/satellites/mines).
- [x] Update any UI surfacing of production output (build-queue completion log, fleet info DTO).

### Tests
- [x] Fleet with `group_kind="fighter_group"` rejects a Move order at validation.
- [x] Fleet with `group_kind="fleet"` accepts Move (no regression).
- [x] Serialize-deserialize a non-fleet group → `group_kind` survives.
- [x] Ship with mine design has `total_defense_score` ≈ original + signature_bonus.
- [x] Build a fighter on a planet → ends up in `staging_yard`. Build on a ship yard → ends up in `VehicleBay`.
- [x] Build a fighter with no available bay → production order fails cleanly.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/strategy -k 'fleet or production or order'`
- Manual: open a save, build a fighter on a planet, observe staging delta; build on a ship yard, observe bay delta.

## Exit criteria
- Non-fleet groups cannot move at strategic layer.
- Mines have a meaningful defensive signature in defense-score calc.
- Production output is consistent across planet and fleet-yard, with bay capacity gating fleet-side builds.
