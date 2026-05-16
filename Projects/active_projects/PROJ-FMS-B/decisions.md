# PROJ-FMS-B Decisions Log

Project-local decisions made during mine implementation. Cross-project decisions live in [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md).

## 2026-05-15 — Project scaffolded

Source: claude/codex inter-agent discussion at `AgentCoordination/Scratchpad/Discussion/20260516T033452Z_fighters-mines-satellites/`.

## 2026-05-16 — Implementation decisions

### Phase 1 — Strategic mine laying

- **Trigger formula sign convention.** The shared design's
  ``p_trigger = sensitivity * sigmoid(k_size * size_score - k_eva *
  maneuver_score - bias)`` uses a "bigger ship => higher p_trigger"
  intuition, but the codebase's `size_score` (at
  `ship_stats.py:443`) is a *defense* term (negative for bigger
  ships). The resolver therefore feeds the negated value:
  `bulk_score = -size_score`. Equivalent intent, sign-corrected for
  the existing stat aggregator. Documented in
  `minefield_resolver.py::_compute_p_trigger_from_scores`.
- **Asymptote-preserving math.** `1 - (1 - p) ** N` underflows to
  exactly `1.0` for IEEE-754 doubles once N gets large enough.
  The resolver computes `P_trigger_pass = 1 - exp(N * log(1-p))`
  with the survival probability floored just above zero, so the
  "never 100%" invariant holds for arbitrarily-large N.
- **`mine_group` carrier ship.** Mines on a `mine_group` Fleet live
  in the `carried_items` list of a single synthetic carrier
  ShipInstance (`instance_id = "mine_carrier_{group_id}"`). The
  carrier is non-combat-capable; it exists only as a container that
  reuses the existing Fleet/ShipInstance serialization pipeline.
  Alternative considered: adding a parallel "mines" list on Fleet.
  Rejected because it would duplicate the entire carried-items
  save/load machinery.
- **Multiple mine_groups per owner per hex.** Allowed by the design.
  For Phase 1 simplicity, same-hex lay orders coalesce into the
  first matching mine_group; the player can split via Phase 4's
  selective self-destruct + re-lay flow. No auto-merge for
  cross-hex mine_groups.
- **Scatter seed.** Built from
  `sha1("{seed_namespace}|{owner_id}|{q}|{r}|{launch_turn}")[:8]`
  for save-portable determinism. Stable across Python processes
  (Python's built-in `hash()` is salted between processes, which
  the design explicitly warns against).
- **Scatter at strategic launch time.** Without a tactical battle
  map yet, mines are scattered uniformly inside a fallback circle
  of radius `data/balance/mines.json::scatter.fallback_radius_m`.
  Phase 3 replaces the layout with a battle-map-bounded scatter on
  first tactical-battle entry, using the same stored seed.
- **Damage-pipeline integration.** The strategic resolver tries
  the full `DamageCalculator.apply_damage` pipeline first
  (materialising a transient sim Ship via
  `ShipInstance.to_ship()`). When that fails (test fixtures with
  partial design data; registries unavailable), it falls back to
  direct `ship.current_hp` decrement — the same pragmatic strategy
  `environmental_hazard_engine` uses.
- **Detonation order across multiple entering ships.** Per-ship
  interleaved: warhead pass → laserhead pass → next ship. Matches
  the user's "ship enters → field reacts" intuition. Documented in
  `MinefieldResolver.resolve_minefield_entry`.

### Phase 2 — Warhead detonation + Laserhead beam

- **Warhead application.** Single mine = single `Warhead` ability
  in the common case, but the data model supports multiple. The
  strategic resolver applies the **sum** of all `Warhead.damage`
  values on the chosen mine in one damage-pipeline call. The
  ramming resolver applies each warhead's damage as a **separate**
  pipeline call (mirrors the shared design's "each warhead's
  damage applied as a separate hit" wording for ramming).
- **Laserhead distance assumption (strategic).** The strategic
  layer has no positional model for mines vs ships, so the
  resolver assumes laserheads fire at half their max range —
  the "average distance a moving ship sees". The tactical
  resolver uses the real Euclidean distance.
- **Shields/armor honoured.** The strategic resolver routes
  damage through `DamageCalculator.apply_damage`, so shields,
  emissive armor, and SRA all consume mine damage exactly as
  they would in tactical combat (when registries are wired). The
  fallback direct-HP path is used only for tests with stub ships.

### Phase 3 — Tactical mine resolver + scatter

- **Per-tick scaling factor.** Per-tick warhead trigger chance =
  ``strategic_p_trigger / expected_ticks_in_proximity``, where
  ``expected_ticks_in_proximity = 50`` (a coarse-grained estimate
  derived from typical ship speeds and the 600 m default
  proximity radius). Tunable; see
  `TacticalMineResolver.DEFAULT_EXPECTED_TICKS_IN_PROXIMITY` and
  `data/balance/mines.json::tactical.per_tick_scaling`. Documented
  rationale: integrated over the time a ship spends in proximity,
  the expected number of triggers approximates the strategic
  per-pass trigger chance.
- **Proximity radius.** `warhead_proximity_radius = 600.0` m
  (balance file). Mines outside this radius do not roll. Tunable
  via the balance file without code changes.
- **Mid-battle-laid mines persist to the strategic mine_group.**
  Following the shared design's "every mine in the sector lives
  in a `mine_group`" rule. The `TacticalMineResolver` writes
  consumed-inventory deltas back via
  `writeback_to_mine_group(mine_group)` at battle end.
- **Cooldown to prevent per-tick spam.** A mine that fails its
  per-tick roll sits on a 1-tick cooldown before the next attempt.
  Cheap insurance against an unmoving ship eating dozens of rolls
  per second.
- **Battle-engine hook.** Added a `BattleEngine.mine_resolver`
  attribute. When `None`, battles run exactly as before. When
  set, `update()` calls `_run_mine_resolver_tick()` after the
  standard tick phases. The hook bypasses `tick_phase` plumbing
  to avoid coupling test ticks to the mine system. (Superseded
  2026-05-16 by audit Fix 2 — `mine_resolvers: List` is the
  production slot; the singular `mine_resolver` is a
  backwards-compat alias retained for the Phase 3 unit tests.)
- **Mine HP.** Mines participate in tactical combat with hull HP
  from their `StructuralIntegrity` component (sum across all hull
  components on the design). Reduced to 0 HP without detonating
  (e.g. by point-defense fire) -> mine pruned from the resolver's
  active list without firing.

### Phase 4 — Sensitivity / threshold / self-destruct / ramming

- **`MineGroupService`** in `game/strategy/services/` is the
  single seam for player operations on `mine_group` Fleets.
  Validates sensitivity labels (LOW/MED/HIGH only), threshold
  range ([0.0, 1.0]), and clamps self-destruct overcounts. UI
  screens (a follow-up) call into these methods rather than
  mutating Fleet state directly. Tested at the service layer; UI
  binding is intentionally minimal for this project pass.
- **`RamTargetResolver`** lives in `game/simulation/combat/` and
  encapsulates all ramming logic. Lookup is by ability *class
  name* (`type(ability).__name__ == "RamTargetAbility"`) rather
  than `isinstance` checks, so the resolver does not need to
  import the ability class (avoids cross-layer cycles when used
  from tests with stub abilities).
- **Multiple warheads on rammer.** Each warhead's damage applied
  as a separate `DamageCalculator.apply_damage` call. Matches the
  shared design's "every Warhead on the rammer detonates against
  it via the damage pipeline (each warhead's `damage` applied as
  a separate hit)" wording.
- **No collision auto-detonation without `RamTargetAbility`.** A
  ship carrying Warhead components but no RamTarget ability is
  inert payload — collisions do nothing. `set_ram_target` returns
  False when the rammer lacks the ability; the per-tick tick
  skips it entirely.

### Phase 5 — Tests, balance, docs

- **Statistical tests at 1000 trials.** Per the checklist; gives
  ~3% absolute tolerance for binomial trigger-rate comparisons
  vs the analytical `P_trigger_pass`. Generous bounds chosen so
  the test isn't flaky on CI without compromising the invariant
  (bigger ships trigger more — measured 1.1x lower bound).
- **Test stubs over heavyweight ShipInstance.** Phase 5 E2E
  uses minimal `_StubShip` / `_StubCarrier` instances exposing
  the strategy-layer surface the resolver actually reads
  (`instance_id`, `carried_items`, `is_alive`, `current_hp`,
  `get_calculated_stats()`). Keeps the integration tests fast
  and focused; the full ShipInstance graph already has dedicated
  unit coverage elsewhere.
- **Documentation.** New `docs/systems/minefields.md` describes
  the full system end-to-end. `docs/systems/ability_reference.md`
  has a PROJ-FMS-B section pinning the runtime behaviour of
  Warhead / Laserhead / RamTarget / StrategicMineLayer /
  TacticalMineLayer.

## 2026-05-16 — Audit fix pass

Source: codex audit response at
`AgentCoordination/Scratchpad/Consult/20260516T071827Z_proj-fms-b-audit/response.md`.
Six findings remediated in a TDD pass (three P1 blockers + three P2
follow-ups). All fixes preserved the previously-shipped PROJ-FMS-B
implementation — no reverts.

### Fix 1 (P1) — Strategic damage pipeline now uses real shields/armor
- **Symptom**: `_derive_moved_fleet_ids` in `turn_phase_registry.py` was
  invoking `MinefieldResolver.resolve_minefield_entry(...)` without
  `registries`, so `_apply_strategic_damage` always took its direct-HP
  fallback. Live strategic mine hits silently bypassed shields,
  emissive armor, and SRA.
- **Fix**: Threaded `engine._registries` through the post-exec hook.
  Renamed the hook's first parameter from `_engine` to `engine` to
  reflect actual use. The descriptor-shape tests that pass
  `engine=None` keep working because `getattr(None, '_registries',
  None) is None` and the resolver falls back gracefully.
- **Test coverage**: New
  `test_derive_moved_fleet_ids_threads_registries_to_minefield_resolver`
  (descriptor wiring) and
  `test_strategic_damage_routes_through_damage_pipeline_when_registries_given`
  (verifies the resolver invokes `DamageCalculator.apply_damage` and a
  shielded target absorbs damage in shields before HP).

### Fix 2 (P1) — Tactical battles wire mine resolvers at battle setup
- **Symptom**: `BattleEngine.mine_resolver` was opt-in and `None` by
  default; the strategic battle-spec compiler never constructed a
  `TacticalMineResolver`, never set `_owner_team_id`, and never called
  `writeback_to_mine_group()`. The post-battle hook didn't even
  reference mine_groups.
- **Fix**:
  1. Added `_split_mine_groups_from_fleets(fleets)` helper in
     `spec_compiler.py` so the team-construction path operates only on
     real combat fleets. Synthetic mine-carrier ShipInstances no
     longer become degenerate ShipSpecs on their own team.
  2. Extended `BattleEngine` with a `mine_resolvers: List[Any]`
     parallel attribute (the existing `mine_resolver` singular slot
     stays as a backwards-compat alias for the Phase 3 unit tests).
     `BattleEngine._run_mine_resolver_tick` now iterates the full list,
     picking the right `_owner_team_id` per resolver — so multiple
     mine_groups belonging to different empires can coexist in the
     same battle without friendly-firing each other.
  3. Added `build_mine_resolver_setup(mine_groups, owner_to_team_id,
     battle_boundary)` in `spec_compiler.py` returning a
     `pre_tick_loop_callback` closure that constructs one
     `TacticalMineResolver.from_mine_group` per mine_group, seeds its
     `_owner_team_id`, and parks the resolver on the mine_group
     (`mg._tactical_resolver`) for writeback. The spec compiler tags
     the frozen `BattleSpec` with `_mine_groups` + `_owner_to_team_id`
     side-channels via `object.__setattr__` so the production caller
     (`SimulationBattleResolver._run_simulated_battle`) can build the
     setup closure and pass it to `run_battle(...,
     pre_tick_loop_callback=...)`.
  4. The compiler-side post-battle hook now closes over the
     mine_groups and calls `writeback_to_mine_group` for each — then
     prunes mine_groups whose carrier ended the battle empty from
     their owning empire's fleets list.
- **Decision — synthetic-carrier filtering**: the mine_group's
  synthetic carrier ShipInstance carries no real layers/components and
  is non-combat-capable by design. Translating it into a `ShipSpec`
  would yield a degenerate ship on its own team. The audit fix routes
  mine participation exclusively through `TacticalMineResolver`,
  keeping the "mines are battlefield hazards, not combatants" rule
  intact.
- **Decision — multiple resolvers vs single**: chose the
  parallel-list refactor (`mine_resolvers`) over funneling every
  mine_group's mines into a single resolver. Mines must filter enemies
  by their owner's team_id; one resolver per owner is the cleanest way
  to keep friendly-fire off.
- **Test coverage**: new
  `test_spec_compiler_filters_mine_groups_and_wires_resolver` and
  `test_post_battle_hook_calls_writeback_and_prunes_empty_mine_group`
  in `tests/integration/test_fms_b_e2e.py`;
  `test_battle_engine_ticks_multiple_mine_resolvers` in
  `tests/unit/simulation/systems/test_tactical_mine_resolver.py`.

### Fix 3 (P1) — Ramming has a production caller
- **Symptom**: `RamTargetResolver` existed but `BattleEngine.update()`
  never invoked it. The "E2E" ramming test only instantiated the
  resolver directly with stub ships. Player-facing kamikaze flow was
  non-functional.
- **Fix**: `BattleEngine.__init__` now auto-instantiates a
  `RamTargetResolver` on every engine and exposes
  `BattleEngine.ram_resolver`. The new `_run_ramming_tick` method runs
  unconditionally each tick (after the standard tick phases) — the
  resolver short-circuits on ships without an active `ram_target`, so
  battles without ramming pay only a per-tick attribute check. New
  `BattleEngine.set_ram_target(rammer, target)` /
  `clear_ram_target(rammer)` methods are the canonical UI / AI action
  surface; they route through the engine-owned resolver.
- **Decision — auto-instantiate vs opt-in**: ramming is intrinsic to
  every ship that mounts `RamTargetAbility`, so making the resolver a
  ship-level capability (rather than an opt-in attribute) keeps the
  contract honest. Cost is one per-tick attribute check; negligible.
- **Decision — movement-AI integration**: the explicit
  intercept-and-pursue pathing override on `ram_target_id` is still
  deferred to a follow-up AI pass. Current behavior relies on the
  rammer's existing movement reaching collision range; the resolver
  detects hull-radius intersection and detonates. The plumbing is in
  place to slot the pursuit override later without re-wiring the
  resolver.
- **Test coverage**: `test_battle_engine_auto_attaches_ram_resolver`
  and `test_battle_engine_set_ram_target_rejects_when_no_ram_ability`
  in `tests/integration/test_ramming_e2e.py`.

### Fix 4 (P2) — Same-hex lays no longer auto-merge
- **Symptom**: `_get_or_create_mine_group()` returned the first
  matching `mine_group` for the owner at the hex, silently coalescing
  per-action lays. Phase 1 checklist explicitly says "no auto-merge",
  and the shared design says "Multiple groups per owner per hex
  permitted".
- **Fix**: `_get_or_create_mine_group()` always mints a fresh
  `mine_group` Fleet (kept the function name for callers; the rename
  is mechanical and would inflate the diff). Each `IssueLayMinesCommand`
  produces its own group with a unique fleet_id.
- **Test coverage**: `test_same_hex_lays_do_not_auto_merge` and
  `test_three_separate_lays_at_same_hex_produce_three_groups` (new) in
  `test_lay_mines_handler.py`. The pre-existing
  `test_extending_mine_group_at_same_hex` was updated to assert the
  new no-auto-merge behaviour; the e2e
  `test_mixed_warhead_and_laserhead_minefield` was likewise updated
  to expect two mine_groups at the hex.

### Fix 5 (P2) — Per-tick scaling factor is balance-tunable
- **Symptom**: `TacticalMineResolver.DEFAULT_EXPECTED_TICKS_IN_PROXIMITY = 50`
  was a hard-coded class constant. The balance file claimed
  tunability but only loaded the `per_tick_scaling` label string.
- **Fix**: Added
  `TacticalConstants.expected_ticks_in_proximity: int = 50` and
  loaded it from `data/balance/mines.json::tactical.expected_ticks_in_proximity`.
  `TacticalMineResolver._warhead_per_tick_roll` now reads the value
  from the balance object (`self._balance.tactical.expected_ticks_in_proximity`)
  via `getattr(..., DEFAULT_EXPECTED_TICKS_IN_PROXIMITY)` so a
  resolver constructed with a partial mock balance still works.
- **Test coverage**:
  `test_expected_ticks_in_proximity_is_balance_tunable` in
  `test_tactical_mine_resolver.py` — verifies a 100× smaller divisor
  produces a substantially higher per-tick trigger rate.

### Fix 6 (P2) — Writeback clears carrier when every mine is consumed
- **Symptom**: `writeback_to_mine_group` only assigned `carrier.carried_items
  = new_items` when `new_items or kept_dicts` was truthy. A battle that
  consumed every mine left the original inventory intact, polluting
  the strategic-layer mine count and the selective-self-destruct UI.
- **Fix**: Unconditionally assign `carrier.carried_items = new_items`.
  Empty list is the right answer for fully-consumed battles. The
  compiler-side post-battle hook (Fix 2) then prunes the empty
  mine_group from its empire's fleets list.
- **Test coverage**: `test_writeback_clears_carrier_when_all_mines_consumed`
  and `test_writeback_clears_carrier_when_all_mines_hp_zero` in
  `test_tactical_mine_resolver.py`.

### Known limitations / things for codex consult

- ~~**Tactical-side full `battle_engine` integration.**~~ **Resolved
  2026-05-16 in audit Fix 2** (see "2026-05-16 — Audit fix pass"
  below). The spec compiler now auto-wires
  `TacticalMineResolver`s via `build_mine_resolver_setup` per
  contested-hex `mine_group`, threads them through the
  `pre_tick_loop_callback`, and the post-battle hook calls
  `writeback_to_mine_group` for each. The original 5-step plan
  below is retained for historical context.

  1. Detect contested-hex `mine_group` Fleets in
     `game/strategy/combat/spec_compiler.py` (or the equivalent
     post-PROJ-275 location).
  2. Build a `TacticalMineResolver.from_mine_group(mg,
     battle_boundary=spec.boundary.bounds)` per mine_group.
  3. Set `battle_engine.mine_resolver` before `start_teams()`.
  4. Set `mine_resolver._owner_team_id` so the resolver knows
     which team_id is "friendly".
  5. Call `writeback_to_mine_group(mg)` in the post-battle hook.
- **UI screens.** Sensitivity radio, threshold slider, selective
  self-destruct modal, and "set ram target" context action are
  intentionally minimal — service-layer is tested but pygame
  binding is deferred. The `MineGroupService` and
  `RamTargetResolver` are the contract UI screens will call.
- **`LAY_MINES` action_time.** Added to `_ABILITY_LOOKUP_EXEMPT`
  in the contract test; the action falls through to the default
  action_time. A dedicated `StrategicMineLayer` action_time
  lookup would let the player tune lay speed via component
  upgrades — left as a balance follow-up.
- **No mid-battle self-destruct UI.** The `MineGroupService`
  works at both strategic and tactical layers (it mutates the
  mine_group's inventory directly), but no in-battle UI calls
  it. Strategic between-turn self-destruct works end-to-end.
- **Per-tick scaling tuning.** `DEFAULT_EXPECTED_TICKS_IN_PROXIMITY = 50`
  is a coarse estimate. Real playtest data may want to
  parametrise this by ship speed (faster ship => fewer ticks in
  proximity => higher per-tick chance).
