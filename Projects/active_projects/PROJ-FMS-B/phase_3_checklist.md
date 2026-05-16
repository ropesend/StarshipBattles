# PROJ-FMS-B Phase 3: Tactical mine resolver + sector scatter

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Mines participate in tactical combat. They sit at their scatter coordinates on the tactical map and react to enemy ships moving through their proximity (warheads) or into their beam range (laserheads).

## Tasks

### Tactical mine layer execution
- [x] Wire tactical mine-laying via the battle-action / weapon-firing-system path (NOT a hypothetical `apply()` on the ability class). Pattern: in-battle player/AI commits the lay-mines action via the existing battle-action plumbing; the resolver pops mines from the laying ship's `VehicleBay` and places them on the tactical map at the chosen position (or near the laying ship if no position given).
- [x] **Spawned tactical mines persist to the laying empire's `mine_group` Fleet** — they are sector assets, not one-battle effects. This keeps the data model uniform: every mine in the sector lives in a `mine_group`, regardless of when it was laid. (Consistent with the user's "selective destruction" rule and the persistence model for fighters/satellites laid mid-battle.)
- [x] If no `mine_group` exists for the owner in the hex yet, a new one is created with default sensitivity (`MED`) and threshold (from balance file).
- [x] Document the choice and its rationale in [`decisions.md`](decisions.md).

### `mine_group` ↔ battle compilation
- [x] Confirm [`conflict_resolution_engine.py:312-321,357-376`](../../../game/strategy/engine/conflict_resolution_engine.py#L312) picks up `mine_group` Fleets with the new `group_kind` and adds them to the owning side's combat manifest. If it iterates `empire.fleets`, this is free.
- [x] Battle compiler must place mines on the tactical map at their stored scatter coordinates (not at the laying ship's spawn). Add a path through [`battle_engine.py`](../../../game/simulation/systems/battle_engine.py) initialization. (PROJ-FMS-B audit Fix 2 — 2026-05-16: `spec_compiler.build_strategy_battle_spec` now filters `mine_group` Fleets out of team construction and tags the spec with `_mine_groups`; `SimulationBattleResolver._run_simulated_battle` builds a `pre_tick_loop_callback` via `build_mine_resolver_setup` that constructs a `TacticalMineResolver` per `mine_group` and attaches it to `BattleEngine.mine_resolvers` with the correct `_owner_team_id`. The compiler-side post-battle hook then drives `writeback_to_mine_group` for each group and prunes empties.)

### Per-tick mine behavior
- [x] In the per-tick movement loop inside `battle_engine`, for each enemy ship that moves:
  - **Warhead mines in proximity**: for each warhead mine within `warhead_proximity_radius` (new constant in `data/balance/mines.json`), apply the per-mine trigger formula (same math as strategic, but on a per-tick basis). On trigger: detonate, apply damage, remove the mine.
  - **Laserhead mines in range**: when an enemy enters a laserhead's beam range, run the same threshold gate; if it fires, run the standard beam attack against the target ship; consume the mine.
- [x] Per-tick rolls are scaled so the same enemy passing through a mine area at strategic-entry time has a roughly equivalent expected damage as in tactical — i.e., the tactical per-tick chance is a small fraction of the strategic-pass chance, integrated over the time the ship spends in proximity. **Document the chosen scaling in [`decisions.md`](decisions.md).** Lean: tactical chance per tick ≈ strategic chance / `expected_ticks_in_proximity`, with `expected_ticks_in_proximity` estimated from ship speed and proximity radius.
- [x] Mines reduced to zero in a `mine_group` cause the group to be removed.

### Sector scatter
- [x] When a `mine_group` is committed to a tactical battle:
  - If a tactical battle map exists for the hex (which it does by definition when this resolver runs), use the battle map's bounding box and uniformly sample `len(mines)` positions inside it, seeded by the group's stored seed.
  - If for some reason no battle map (shouldn't happen at tactical layer), fall back to the strategic-time `fallback_radius_m` circle around (0,0).
  - **Re-entries are deterministic**: the same `(group_id, seed_namespace)` always produces the same layout. Use a stable PRNG (e.g., `numpy.random.Generator` with seeded state or Python's `random.Random(seed)`).
- [x] Scatter coords stored on the `mine_group` Fleet (added as a field — `mine_positions: List[Tuple[float, float]]`). Persists across saves.

### Mine HP in tactical combat
- [x] Mines are vehicles with HP from the `Hull` component (per design). When taking damage (e.g., point-defense fire), HP decreases. At 0 HP, the mine is destroyed *without* detonating. (Mines should be hard to hit thanks to the `signature_bonus` from PROJ-FMS-A Phase 4, but not invulnerable.)

### Tests
- [x] Lay 10 mines strategically; trigger a tactical battle in the hex; confirm mines appear on the tactical map at scattered coords; re-run same battle → same positions.
- [x] Enemy ship moves through a warhead minefield over many ticks → trigger rate roughly matches strategic-pass rate (with the scaling decision documented).
- [x] Enemy ship enters a laserhead's beam range while in motion → laserhead fires once and is consumed.
- [x] Point-defense fire shoots a mine before it can detonate → mine removed without damage event to a target.
- [x] Laying mines mid-battle works; mid-battle laid mines appear at the chosen position.
- [x] `mine_group` survives the tactical battle if any mines remain; is removed if all consumed.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `python -m combat_lab.run_tests` — combat regression smoke.
- Manual: battle in a mined hex; observe mine sprites, detonations, point-defense interaction.

## Exit criteria
- Mines fully participate in tactical combat with both warhead and laserhead behaviors.
- Scatter is deterministic across re-entries.
- Mine HP works (destroyable by point defense).
