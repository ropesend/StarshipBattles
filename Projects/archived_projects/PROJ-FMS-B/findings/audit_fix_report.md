# PROJ-FMS-B Audit Fix Report

**Date:** 2026-05-16
**Source audit:** `AgentCoordination/Scratchpad/Consult/20260516T071827Z_proj-fms-b-audit/response.md`
**Scope:** Six remediations on top of the original PROJ-FMS-B
implementation (three P1 blockers + three P2 follow-ups). No PROJ-FMS-A
or PROJ-FMS-B work was reverted; this pass is purely additive +
behaviour-correcting.

## Audit summary

Codex's mid-project audit identified that the resolver classes shipped
by PROJ-FMS-B existed but were never wired into the production
game-loop callers:

- The strategic damage path called `MinefieldResolver` without
  `registries`, so every live mine hit silently took the direct-HP
  fallback and bypassed shields / armor / SRA.
- The tactical battle compiler never constructed a
  `TacticalMineResolver`, so mines in a hex were listed as Fleets but
  their tactical behaviour never fired.
- The `RamTargetResolver` had no production caller. The "E2E" ramming
  test instantiated it directly with stub ships; the player-facing
  kamikaze flow was non-functional.
- Three smaller P2 issues: same-hex auto-merge violated the design,
  the per-tick scaling factor was documented as tunable but was a
  hard-coded class constant, and `writeback_to_mine_group` left zombie
  inventory when every mine was consumed.

All six were fixed in a single TDD pass.

## Fixes applied

### Fix 1 (P1) — Strategic damage pipeline now uses the real damage calculator

`game/strategy/engine/turn_phase_registry.py::_derive_moved_fleet_ids`
now threads `engine._registries` into
`MinefieldResolver.resolve_minefield_entry(...)`. Pre-fix the kwarg was
omitted, so `_apply_strategic_damage` always took its `registries is
None` fallback and decremented `ship.current_hp` directly. With the fix,
a shielded enemy entering a mined hex sees its shields absorb damage
through `DamageCalculator.apply_damage` before any HP loss.

**Files touched**
- `game/strategy/engine/turn_phase_registry.py` (parameter rename
  `_engine → engine`, kwarg `registries=...` added to the resolver
  call).

**Tests added**
- `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py::test_derive_moved_fleet_ids_threads_registries_to_minefield_resolver`
- `tests/unit/strategy/engine/test_minefield_resolver.py::test_strategic_damage_routes_through_damage_pipeline_when_registries_given`

### Fix 2 (P1) — Tactical battles get a real mine resolver

Three coordinated changes:

1. **Spec-compiler filtering** — `build_strategy_battle_spec` now
   partitions input fleets via the new
   `_split_mine_groups_from_fleets` helper. Only true combat fleets
   become teams; mine_groups are kept in a `_mine_groups` side-channel
   on the spec (set via `object.__setattr__` because `BattleSpec` is
   frozen). The synthetic mine-carrier ShipInstance no longer
   degenerates into a no-layer "ship" on its own team.

2. **Engine multi-resolver support** — `BattleEngine` now exposes
   `mine_resolvers: List[Any]` alongside the existing
   `mine_resolver: Optional[Any]` (kept for backwards compat with the
   Phase 3 unit tests). `_run_mine_resolver_tick` iterates the list,
   pulling `_owner_team_id` per-resolver so multiple mine_groups
   belonging to different empires can coexist without friendly fire.

3. **Production wiring** — new
   `spec_compiler.build_mine_resolver_setup(mine_groups,
   owner_to_team_id, battle_boundary)` returns a
   `pre_tick_loop_callback` closure that constructs one
   `TacticalMineResolver.from_mine_group` per mine_group, sets its
   `_owner_team_id`, attaches it to `engine.mine_resolvers`, and parks
   it on `mine_group._tactical_resolver` for writeback. The strategy
   adapter (`SimulationBattleResolver._run_simulated_battle`) reads the
   side-channels, builds the closure, and passes it to
   `run_battle(..., pre_tick_loop_callback=...)`. The compiler-side
   post-battle hook (`_build_strategy_post_battle_hook`) was extended
   with a `mine_groups=` kwarg that drives `writeback_to_mine_group`
   for each mine_group and prunes any mine_group whose carrier ended
   the battle with empty inventory.

**Files touched**
- `game/strategy/combat/spec_compiler.py` (new helpers, side-channel,
  post-hook wrapping).
- `game/simulation/systems/battle_engine.py` (`mine_resolvers` field,
  multi-resolver tick).
- `game/strategy/adapters/simulation_adapter.py` (build the setup
  closure; new `_boundary_to_box` helper).

**Tests added**
- `tests/integration/test_fms_b_e2e.py::test_spec_compiler_filters_mine_groups_and_wires_resolver`
- `tests/integration/test_fms_b_e2e.py::test_post_battle_hook_calls_writeback_and_prunes_empty_mine_group`
- `tests/unit/simulation/systems/test_tactical_mine_resolver.py::test_battle_engine_ticks_multiple_mine_resolvers`

### Fix 3 (P1) — Ramming has a production caller

`BattleEngine.__init__` now auto-instantiates a `RamTargetResolver`
attached as `self.ram_resolver`. `BattleEngine.update` calls the new
`_run_ramming_tick` after the standard tick phases on every battle; the
resolver short-circuits on ships without an active `ram_target`, so
battles without ramming pay only a cheap attribute check per tick.

The action surface `BattleEngine.set_ram_target(rammer, target)` and
`BattleEngine.clear_ram_target(rammer)` are the canonical UI / AI
entry points; they delegate to the engine-owned resolver. Designs
without `RamTargetAbility` still get a clean `False` return from
`set_ram_target` (existing resolver semantics).

**Movement-AI integration deferred** — explicit
intercept-and-pursue pathing for `ram_target_id` is still a follow-up
AI pass. The resolver detects hull-radius intersection on the rammer's
existing movement; the pursuit override slots in cleanly without
changes to the resolver.

**Files touched**
- `game/simulation/systems/battle_engine.py` (auto-instantiated
  resolver, per-tick call, action-surface methods).

**Tests added**
- `tests/integration/test_ramming_e2e.py::test_battle_engine_auto_attaches_ram_resolver`
- `tests/integration/test_ramming_e2e.py::test_battle_engine_set_ram_target_rejects_when_no_ram_ability`

### Fix 4 (P2) — Same-hex lays no longer auto-merge

`LayMinesOrderHandler._get_or_create_mine_group` now unconditionally
mints a fresh `mine_group` Fleet per lay action. The function name is
unchanged to keep the diff minimal; behaviourally it has become
`_create_mine_group`. The Phase 1 design intent — multiple mine_groups
per owner per hex, no auto-merge — is now honoured. Players retain
selective control via `MineGroupService.self_destruct` per group.

**Files touched**
- `game/strategy/engine/order_handlers/lay_mines.py`.

**Tests added/updated**
- `tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py::test_same_hex_lays_do_not_auto_merge`
  (renamed/rewritten from the prior coalescing-asserting test).
- `tests/unit/strategy/engine/order_handlers/test_lay_mines_handler.py::test_three_separate_lays_at_same_hex_produce_three_groups`
  (new regression).
- `tests/integration/test_fms_b_e2e.py::test_mixed_warhead_and_laserhead_minefield`
  updated to expect two distinct mine_groups (one warhead-only, one
  laserhead-only) at the same hex.

### Fix 5 (P2) — Per-tick scaling factor is balance-tunable

`MinefieldBalance.tactical` gained `expected_ticks_in_proximity: int =
50`. The loader pulls
`data/balance/mines.json::tactical.expected_ticks_in_proximity` (now
present in the JSON balance file).
`TacticalMineResolver._warhead_per_tick_roll` reads the value via
`getattr(self._balance.tactical, "expected_ticks_in_proximity",
DEFAULT_EXPECTED_TICKS_IN_PROXIMITY)` — preserves the class constant
as the documented fallback default when the resolver is constructed
with a mock balance lacking the field.

**Files touched**
- `game/strategy/engine/minefield_balance.py` (new field + loader
  branch).
- `data/balance/mines.json` (new `expected_ticks_in_proximity: 50`
  entry).
- `game/simulation/systems/tactical_mine_resolver.py` (read from
  balance; class constant kept as default).

**Tests added**
- `tests/unit/simulation/systems/test_tactical_mine_resolver.py::test_expected_ticks_in_proximity_is_balance_tunable`

### Fix 6 (P2) — Writeback clears carrier when all mines consumed

`TacticalMineResolver.writeback_to_mine_group` now unconditionally
assigns `carrier.carried_items = new_items` — including the empty
list. Pre-fix the `if new_items or kept_dicts:` guard skipped the
assignment when every mine was consumed, leaving zombie inventory on
the strategic-layer mine_group and feeding stale entries to the
selective-self-destruct UI. The post-battle hook from Fix 2 then
prunes any mine_group whose carrier ends up empty.

**Files touched**
- `game/simulation/systems/tactical_mine_resolver.py`.

**Tests added**
- `tests/unit/simulation/systems/test_tactical_mine_resolver.py::test_writeback_clears_carrier_when_all_mines_consumed`
- `tests/unit/simulation/systems/test_tactical_mine_resolver.py::test_writeback_clears_carrier_when_all_mines_hp_zero`

## Side effects in existing tests

- `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py`
  was updated so the `_fake_run_battle` mocks accept the new
  `pre_tick_loop_callback` kwarg.
- `tests/integration/test_fms_b_e2e.py::test_mixed_warhead_and_laserhead_minefield`
  was updated for Fix 4 (two mine_groups instead of one).

## Sharded suite status

Full sharded run after the fix pass: see the run captured in the
"Sharded suite status" section of [`implementation_report.md`](implementation_report.md).
The pre-existing baseline failures (`test_ship_stats_golden` ×3 +
`test_iter_keys_match_full_hp_builder_for_cross_layer_design` flake)
remain the only failing tests — no new failures introduced.

## What is NOT in this pass

- Pygame UI bindings for sensitivity radio, threshold slider,
  selective self-destruct modal, and the "set ram target" context
  action. Service-layer / engine-layer contracts are stable and
  tested; the UI layer is the remaining work, intentionally not
  attempted here.
- Explicit intercept-and-pursue movement-AI override for active ram
  targets. Resolver detects hull-radius intersection; pursuit
  behaviour slots in via a follow-up AI pass.
- `StrategicMineLayer` action_time lookup. Still falls through to the
  default action_time; covered by the existing `_ABILITY_LOOKUP_EXEMPT`
  contract-test allowance.
