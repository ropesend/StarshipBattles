# PROJ-FMS-B Implementation Report

**Status:** All 5 phases shipped (2026-05-16). An audit fix pass
followed the same day — see [`audit_fix_report.md`](audit_fix_report.md)
for the six remediations applied on top of this baseline (3 P1 wiring
gaps + 3 P2 follow-ups). The original "known follow-ups" section below
listed item #1 as a deferral, but codex's audit re-classified it as a P1
blocker — the fix pass closed it along with two other P1s.
**Scope:** Mines end-to-end — strategic laying via order pipeline,
strategic-entry damage (warhead + laserhead passes), tactical-layer
per-tick mine behaviour, sector scatter, sensitivity / threshold /
self-destruct service, and explicit-target ramming.
**Pre-existing baseline:** 20462 tests / 20443 passed / 9 failed / 6
errors / 4 skipped (PROJ-FMS-A post-audit).

## Per-phase summary

### Phase 1 — Strategic mine laying

- New balance file `data/balance/mines.json` with warhead trigger
  constants, sensitivity multipliers, scatter constants, laserhead
  threshold default, and tactical constants.
- New `Paths.MINES_BALANCE_FILE` + `Paths.BALANCE_DIR`.
- New `game/strategy/engine/minefield_balance.py` with frozen
  dataclasses + cached loader (`load_minefield_balance`).
- New `game/strategy/engine/minefield_resolver.py` with the warhead
  pass (`P_trigger_pass = 1 - (1 - p_trigger)^N`) and the laserhead
  pass (continuous threshold gate before the standard beam roll).
  Damage routed through `DamageCalculator.apply_damage` when
  registries available, falling back to direct HP decrement.
- New `IssueLayMinesCommand` + `LayMinesCommandHandler` in
  `game/strategy/engine/commands/` and `handlers/`.
- New `LayMinesOrderHandler` in
  `game/strategy/engine/order_handlers/lay_mines.py`. Pops mines
  from carrier `VehicleBay`, creates/extends a `mine_group` Fleet
  at the target hex, populates `mine_positions` deterministically.
- `Fleet` extended with `sensitivity`, `expected_hit_chance_threshold`,
  `mine_positions`, `scatter_seed`; serialised through `to_dict` /
  `from_dict` (only when populated).
- `OrderType.LAY_MINES` moved from "reserved" to "reachable via
  command" in the contract test.
- Resolver wired into the turn engine via `_derive_moved_fleet_ids`
  post-hook on the `movement_apply` phase — runs after movement
  apply, before combat. Destroyed-by-mines fleets are pruned from
  conflict-resolution input.

### Phase 2 — Warhead detonation + Laserhead beam behaviour

- Damage-pipeline integration in `_apply_strategic_damage`: tries
  `ShipInstance.to_ship()` + `DamageCalculator.apply_damage` first,
  falls back to direct HP decrement on test fixtures / missing
  registries.
- Laserhead pass fully implemented in `_resolve_laserhead_pass`:
  per-mine continuous threshold gate using sigmoid of
  `(base_accuracy + sensor_bonus) - (falloff*distance +
  defense_score)`. Below threshold => skip (no consume). Above =>
  standard beam roll + consume-on-fire.
- Per-ship interleaving documented: warhead pass -> laserhead pass
  -> next ship.

### Phase 3 — Tactical mine resolver + sector scatter

- New `game/simulation/systems/tactical_mine_resolver.py` with
  `TacticalMineEntity` + `TacticalMineResolver`. Per-tick mine
  behaviour: warhead proximity rolls + laserhead range/threshold
  rolls. Mines destroyed by external damage (HP <= 0) are pruned
  without detonating.
- `TacticalMineResolver.from_mine_group(mg, battle_boundary=...)`
  scatters mines uniformly inside the battle box using the
  mine_group's stored seed. Re-entries deterministic.
- Per-tick scaling: `per_tick_chance = strategic_p / 50` (50 =
  `DEFAULT_EXPECTED_TICKS_IN_PROXIMITY`), with a min-chance floor.
- `BattleEngine.mine_resolver` hook added; `update()` calls the
  resolver after standard tick phases when wired. Bypassed
  entirely when None (zero impact on battles without mines).
- `writeback_to_mine_group(mg)` persists consumed-inventory
  deltas to the strategic mine_group at battle end.

### Phase 4 — Sensitivity / threshold / self-destruct / ramming

- New `game/strategy/services/mine_group_service.py::MineGroupService`
  with `set_sensitivity`, `set_threshold`, `get_mine_counts_by_design`,
  `self_destruct`. Validates labels, clamps overcounts, prunes
  empty groups from `empire.fleets`, re-syncs `mine_positions`
  list length.
- New `game/simulation/combat/ram_target_resolver.py::RamTargetResolver`
  with `set_ram_target`, `clear_ram_target`,
  `process_ramming_tick`. Ability lookup by class name to avoid
  cross-layer cycles. Each warhead on the rammer applied as a
  separate damage pipeline call. Rammer destroyed regardless of
  damage outcome. Target-dies-before-collision clears the target
  cleanly.
- UI screen binding is intentionally minimal — `MineGroupService`
  and `RamTargetResolver` are the contract UI screens will call.

### Phase 5 — Tests, balance, docs

- New `tests/integration/test_fms_b_e2e.py` (5 tests): lay-mines
  order chain -> enemy enters -> damage applied; self-destruct;
  friendly skip; mixed warhead/laserhead group; insufficient-mines
  clean failure.
- New `tests/integration/test_ramming_e2e.py` (3 tests): kamikaze
  fighter rams frigate; target-dies-before-collision clears; no
  RamTarget => inert payload.
- New `tests/integration/test_fms_b_statistical_balance.py` (4
  tests, 1000 trials each): destroyer @ MED rate matches
  analytical, dread > destroyer, never-100% invariant, always-
  positive invariant.
- New `docs/systems/minefields.md` describing the full system
  end-to-end + balance constants + file map + test map.
- Updated `docs/systems/ability_reference.md` with a PROJ-FMS-B
  section pinning runtime behaviour of `Warhead`, `Laserhead`,
  `RamTarget`, `StrategicMineLayer`, `TacticalMineLayer`.

## Tests added

| File | New / modified | Count |
|---|---|---|
| `tests/unit/strategy/engine/test_minefield_resolver.py` | NEW | 16 |
| `tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py` | NEW | 6 |
| `tests/unit/simulation/systems/test_tactical_mine_resolver.py` | NEW | 9 |
| `tests/unit/strategy/services/test_mine_group_service.py` | NEW | 10 |
| `tests/unit/simulation/combat/test_ram_target_resolver.py` | NEW | 7 |
| `tests/integration/test_fms_b_e2e.py` | NEW | 5 |
| `tests/integration/test_ramming_e2e.py` | NEW | 3 |
| `tests/integration/test_fms_b_statistical_balance.py` | NEW | 4 |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | MODIFIED | (LAY_MINES moved to reachable + ACTION_ORDER_TYPES extended) |
| `tests/unit/strategy/engine/test_command_registry_seeding.py` | MODIFIED | (count bumped 35 -> 36) |
| `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | MODIFIED | (added `dispatch_issue_lay_mines`) |

**Total: 60 new tests across 8 new test files, 3 modified test
files.**

## Sharded suite status

Run command: `python Tools/test_sharded/test_sharded.py` (2026-05-16).

```
TOTAL: 20525 tests | 20506 passed | 9 failed | 6 errors | 4 skipped
Wall time: 169.8s (12 shards)
```

Compared to the PROJ-FMS-A post-audit baseline:

- **Test count: 20462 -> 20525 (+63 tests).**
- **Passed: 20443 -> 20506 (+63 passing).**
- **Failed: 9 -> 9 (same pre-existing).**
- **Errors: 6 -> 6 (same pre-existing).**
- **Skipped: 4 -> 4 (unchanged).**
- **Zero new failures from PROJ-FMS-B.**

All 9 failures + 6 errors are the **same pre-existing set** documented
in `Projects/active_projects/PROJ-FMS-A/findings/implementation_report.md`:

- 3 `test_ship_stats_golden::acceleration_rate` (qs_escort,
  qs_frigate_gc, qs_battleship).
- 5 `test_quickstart_designs::test_design_has_metadata`.
- 1 `test_ship_instance_damage::test_iter_keys_match_full_hp_builder_for_cross_layer_design`
  (known flake).
- 6 `test_design_load_warp_capability` errors.

## Decisions captured

See `Projects/active_projects/PROJ-FMS-B/decisions.md`. Five phase
sections cover:

1. Sign convention on `size_score` for the trigger formula.
2. Log-space `P_trigger_pass` evaluation for the asymptote
   invariant.
3. `mine_group` synthetic-carrier ship choice (vs parallel mines
   list on Fleet).
4. Same-hex mine_group coalescing.
5. Scatter seeding (`sha1(...)[:8]`) + battle-map-bounded scatter
   at first tactical entry.
6. Damage-pipeline integration with fallback.
7. Per-tick scaling factor (`expected_ticks_in_proximity = 50`).
8. Multi-warhead application semantics: sum for strategic
   detonation, separate-hit for ramming.
9. `RamTargetResolver` class-name lookup to avoid cross-layer
   imports.

## Known limitations / things for codex consult to scrutinise

1. ~~**Battle-spec compiler does not yet wire `BattleEngine.mine_resolver`
   automatically.**~~ **CLOSED 2026-05-16 by audit Fix 2** — was
   misclassified as a deferral in the original report; codex audit
   re-classified as P1 blocker. The spec compiler now filters
   `mine_group` fleets out of team construction, tags the spec with
   `_mine_groups`, and the production caller
   (`SimulationBattleResolver`) attaches `TacticalMineResolver`
   instances to `BattleEngine.mine_resolvers` via the
   `pre_tick_loop_callback`. The compiler-side post-battle hook calls
   `writeback_to_mine_group` for each group and prunes empties. See
   [`audit_fix_report.md`](audit_fix_report.md) for the full
   write-up.
2. **No pygame UI binding.** `MineGroupService` and
   `RamTargetResolver` are tested at the service layer, but the
   sensitivity radio, threshold slider, selective self-destruct
   modal, and "set ram target" context action are not yet wired
   into pygame screens. Service contracts are stable; UI binding
   is the next user-visible follow-up.
3. **`mine_resolver._owner_team_id` is set by the compiler, not
   automatically.** The resolver knows which mines belong to which
   empire (via `mine_entity.owner_id`), but needs to be told which
   battle team_id is "us" to filter `enemy_ships`. The compiler
   provides this in the upstream wiring.
4. **`_apply_strategic_damage` damage-pipeline path is best-effort.**
   When `registries` is None or the ship's `design_data` is partial,
   it falls back to direct HP decrement. Production flows should
   always pass registries; tests deliberately do not.
5. **Per-tick scaling factor is coarse-grained.** `DEFAULT_EXPECTED_TICKS_IN_PROXIMITY
   = 50` is a single global constant. Real playtest data may want
   to parametrise by ship speed (faster ship => fewer ticks in
   proximity => higher per-tick chance).
6. **`LAY_MINES` action_time fallback.** Added to
   `_ABILITY_LOOKUP_EXEMPT` in the contract test; the action falls
   through to the default action_time. A dedicated
   `StrategicMineLayer` action_time lookup would let
   `capacity_per_action` + `cycle_time` from the ability data drive
   the actual lay-rate.
7. **Synthetic mine_carrier ShipInstance.** The mine_group's
   single carrier ShipInstance uses `design_id = "mine_carrier_synthetic"`
   and an empty `design_data`. If `Fleet.from_dict` strictness
   changes in a future audit, this synthetic stub may need a
   `_metadata` block to survive deserialization.
8. **Friendly-fire rule.** The shared design says "hard rule —
   friendly fire not enabled". The strategic resolver enforces
   this via empire ownership; the tactical resolver enforces it
   via the `_owner_team_id` filter. Verified in unit + integration
   tests.

## File list — every file touched

### Data

- `data/balance/mines.json` — NEW. Warhead / sensitivity / scatter /
  laserhead / tactical constants.

### Production code

- `game/core/paths.py` — added `BALANCE_DIR` + `MINES_BALANCE_FILE`.
- `game/strategy/engine/minefield_balance.py` — NEW.
- `game/strategy/engine/minefield_resolver.py` — NEW.
- `game/strategy/engine/order_handlers/lay_mines.py` — NEW.
- `game/strategy/engine/handlers/lay_mines.py` — NEW.
- `game/strategy/engine/order_handlers/registry_factory.py` —
  registered `LayMinesOrderHandler`.
- `game/strategy/engine/commands/__init__.py` — added
  `IssueLayMinesCommand`.
- `game/strategy/engine/commands/registry.py` — added `lay_mines`
  to the handler-module list in `seed_default_commands`.
- `game/strategy/engine/turn_phase_registry.py` — extended
  `_derive_moved_fleet_ids` post-hook to invoke the minefield
  resolver after movement_apply.
- `game/strategy/data/fleet.py` — added `sensitivity`,
  `expected_hit_chance_threshold`, `mine_positions`,
  `scatter_seed` fields + serialisation.
- `game/strategy/data/order_types.py` — added `LAY_MINES` to
  `ACTION_ORDER_TYPES`.
- `game/strategy/services/mine_group_service.py` — NEW.
- `game/simulation/systems/tactical_mine_resolver.py` — NEW.
- `game/simulation/systems/battle_engine.py` — added
  `mine_resolver` attribute + `_run_mine_resolver_tick()` hook.
- `game/simulation/combat/ram_target_resolver.py` — NEW.

### Tests

- `tests/unit/strategy/engine/test_minefield_resolver.py` — NEW
  (16 tests).
- `tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py`
  — NEW (6 tests).
- `tests/unit/simulation/systems/test_tactical_mine_resolver.py`
  — NEW (9 tests).
- `tests/unit/strategy/services/test_mine_group_service.py` — NEW
  (10 tests).
- `tests/unit/simulation/combat/test_ram_target_resolver.py` —
  NEW (7 tests).
- `tests/integration/test_fms_b_e2e.py` — NEW (5 tests).
- `tests/integration/test_ramming_e2e.py` — NEW (3 tests).
- `tests/integration/test_fms_b_statistical_balance.py` — NEW
  (4 tests).
- `tests/unit/strategy/engine/test_command_registry_contract.py`
  — moved `LAY_MINES` to reachable set; extended `ACTION_ORDER_TYPES`
  + `_ABILITY_LOOKUP_EXEMPT`.
- `tests/unit/strategy/engine/test_command_registry_seeding.py`
  — count 35 -> 36.
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
  — added `dispatch_issue_lay_mines` to public methods.

### Docs / project

- `docs/systems/minefields.md` — NEW. System reference.
- `docs/systems/ability_reference.md` — PROJ-FMS-B section added.
- `Projects/active_projects/PROJ-FMS-B/decisions.md` — five phase
  sections + known-limitations.
- `Projects/active_projects/PROJ-FMS-B/plan.md` — Quick Status +
  Current State updated.
- `Projects/active_projects/PROJ-FMS-B/phase_{1..5}_checklist.md` —
  all `[x]`.
- `Projects/active_projects/PROJ-FMS-B/findings/implementation_report.md`
  — this file, NEW.
