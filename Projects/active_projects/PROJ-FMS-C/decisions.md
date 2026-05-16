# PROJ-FMS-C Decisions Log

Project-local decisions made during fighter implementation. Cross-project
decisions live in [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md).

## 2026-05-15 — Project scaffolded

Source: claude/codex inter-agent discussion at
`AgentCoordination/Scratchpad/Discussion/20260516T033452Z_fighters-mines-satellites/`.

## 2026-05-16 — Implementation decisions

### Phase 1 — Strategic + tactical fighter launch

- **No auto-merge across same-hex launches.** Each
  `IssueLaunchFightersCommand` mints its own `fighter_group` Fleet
  (fleet_id namespace starts at 200000 to keep it distinct from
  PROJ-FMS-B's mine_group range at 100000). Mirrors PROJ-FMS-B audit
  Fix 4 — the player can recover individual groups via the strategic
  `RECOVER_FIGHTERS` action.
- **Mixed-design groups supported via design filter.** The order
  payload carries `fighter_design_id`; the handler pops only matching
  CarriedVehicles. Using `"auto"` matches any fighter in the bay.
  The resulting group can still hold fighters of multiple designs if
  successive launch actions pump different designs in.
- **HP preservation through the strategic→deployed transition.** Each
  popped CarriedVehicle's `current_hp` flows directly into the new
  `ShipInstance.current_hp`. `component_states` is also carried
  through when present so per-component damage state survives.
- **`fighter_group` deployed ShipInstances do NOT carry
  `launched_in_battle_id`.** That tag is set only by tactical mid-
  battle launches (the engine assigns it at spawn time in
  `process_launch_attack`). The Phase 3 reboard hook uses the
  presence/absence of the tag to distinguish "launched THIS battle"
  from "pre-existing fighter_group fighter that just happens to be
  participating".
- **Tactical launch action surface = `BattleEngine.launch_fighters_in_battle`.**
  The legacy `VehicleLaunchAbility` weapon-firing-system path (auto-
  launch when a target exists) is kept with a deprecation warning;
  the new path is an explicit action call from the player/AI UI.
  Mid-battle launches always go through the design-instance payload
  (`AttackType.LAUNCH` with `carried_vehicle` field) so spawned
  fighters have full components / weapons / HP.
- **Legacy `VehicleLaunchAbility` deprecation strategy.** Kept in
  place; the class-string spawn path in `process_launch_attack`
  logs a deprecation warning on every use. Removal is a follow-up
  housekeeping pass after no shipped quickstart designs reference it.
  This is the choice the design.md "decisions deferred to
  implementation" section flagged.
- **Stat-contributor extension is additive.** The
  `contribute_vehicle_launch` contributor at
  `stat_contributors/launch.py:29` reads the new
  `TacticalFighterLaunchAbility` shape (capacity_per_action /
  cycle_time) in addition to the legacy `VehicleLaunchAbility`.
  Both contribute to the same per-ship `fighters_per_wave` /
  `launch_cycle` fields so downstream consumers don't need to
  branch.

### Phase 2 — Combat join + fighter AI

- **Spec compiler treats `fighter_group` as a real combat fleet.**
  Unlike `mine_group`s (which are filtered out into a side-channel
  for the TacticalMineResolver), fighter_groups carry real-ship-
  bearing `ShipInstance`s. The existing `fleets_by_owner` grouping in
  `build_strategy_battle_spec` merges fighter_groups into the owner's
  team automatically — no special filtering required.
- **Spawn cluster pattern: defer to FormationResolver.** The compiler
  passes the fighter_group's ships through the standard formation
  pipeline (one TaskForce per fleet, one squadron per task force).
  No fighter-specific clustering — that's a Phase 4+ visual polish
  task. The owner-side entry vector from `resolve_team_entry_vectors`
  places the whole owner team consistently.
- **`FighterAIController` is its own class, not a policy alias.** The
  full `AIController` policy machinery (retreat thresholds, sniper /
  brawler / anti-fighter policy trees, formation logic) is overkill
  for fragile single-purpose combat entities. The controller does
  one thing: target the nearest live enemy, turn, thrust, fire.
- **Kamikaze handling: defer movement to `RamTargetResolver`.** When
  the fighter's `RamTargetAbility` has a target_id set, the
  controller short-circuits its own movement update so the engine's
  `_run_ramming_tick` can drive intercept-and-pursue without
  conflicting input. The controller still pulls the trigger so any
  non-ram weapons fire on the ram target en route.
- **`AIControllerFactory` dispatches on `vehicle_type`.** Fighters
  (`vehicle_type == "Fighter"`) get `FighterAIController`; all other
  ship types get the full `AIController`. Test stubs without a
  `vehicle_type` attribute default to "Ship" (full controller).

### Phase 3 — Recovery + end-of-battle reboard

- **Recovery is a strategic action only.** The
  `IssueRecoverFightersCommand` queues a `RECOVER_FIGHTERS` order on
  the recovering fleet; the handler resolves "any fighter_group at
  the recovering fleet's hex owned by the same empire" when the
  command omits a specific `fighter_group_id`. No tactical-layer
  recovery action — at battle end the engine's reboard hook does
  it for tagged in-battle launches; strategic recovery is the
  surface for ALL OTHER cases.
- **Partial recovery is allowed.** If the carrier's bay can only fit
  N of M requested fighters, recover N and leave M-N in the
  fighter_group. The handler still reports success when recovery > 0.
- **Empty source group pruned from `empire.fleets`.** When a
  RECOVER_FIGHTERS action drains the source group, the handler
  removes the empty fleet from `empire.fleets`. Mirrors the
  PROJ-FMS-B mine_group prune-on-empty behavior.
- **End-of-battle reboard runs BEFORE `apply_outcome_to_fleets`.**
  Order matters: reboarded fighters need to land in their carriers
  before the post-battle hook prunes any empty fleets (a pre-existing
  fighter_group at the same hex might end the battle empty and would
  otherwise be pruned before overflow could merge into it). The
  post-battle hook calls `apply_reboard` first, then
  `apply_outcome_to_fleets`.
- **Overflow merge policy.** When the carrier's bay is full at battle
  end, the overflow fighter spills into a NEW `fighter_group` at the
  sector — UNLESS a pre-existing fighter_group at the same hex owned
  by the same empire is already there. In that case, overflow MERGES
  into the pre-existing group rather than fragmenting. Closes the
  loop with the strategic recovery action: a player can recover the
  merged group in a single action.
- **Engine reference passed via shared list side-channel.** The
  post-battle hook closes over a `engine_ref: List[Any]` that the
  pre_tick_loop_callback (built by `build_fighter_reboard_setup`)
  appends to at battle start. This keeps `BattleSpec` frozen and
  follows the same pattern PROJ-FMS-B used for mine_groups
  (`_tactical_resolver` parked on each mine_group Fleet). Unit tests
  that bypass the wiring see `engine_ref == []` and the hook skips
  the reboard step cleanly.
- **Pre-tick callback composition.** `run_battle` accepts exactly
  one `pre_tick_loop_callback`. Mine resolver setup AND fighter
  reboard setup both need to install state on the engine before the
  first tick, so the simulation adapter composes them sequentially
  via a thin `_compose_setup_callbacks` helper.
- **Reboard discards dead fighters.** A tagged fighter that hits 0 HP
  mid-battle is treated as destroyed — the reboard summary increments
  `discarded` rather than trying to recover a corpse. Matches the
  combat-unit destruction semantics in `apply_outcome_to_fleets`.
- **Carrier-destroyed-mid-battle handling is implicit.** The reboard
  walk uses `_candidate_alive(candidate)` which gates on
  `is_alive` AND `is_derelict == False`. A dead carrier is skipped;
  the walk continues to the next friendly ship. If no live friendly
  has bay space, overflow fires.

### Phase 4 — Tests + docs

- **Integration tests use stub carriers + minimal real fighter designs.**
  The full-stack flow with `Galaxy` / `Empire` / `TurnEngine` is
  outside the unit-integration scope; the integration tests pin the
  handler-to-resolver-to-reboard contract using stubs that expose
  just the surface the production code reads. The full E2E path
  (UI → command → order → handler → battle → reboard → save/load)
  remains a manual hand-verification task.
- **No statistical tests for fighter AI.** Unlike mines (which have
  probabilistic trigger formulas), fighter AI is deterministic
  ("target nearest") given the same spatial grid contents. No
  statistical test needed; behavior is pinned by unit tests.
- **Hand verification deferred to the manual smoke checklist.** Full
  in-game E2E (load save, design fighter, build, launch, fight,
  recover, save/load) is documented in
  `phase_4_checklist.md` as a manual task. Pending automated UI
  test infrastructure to drive pygame screens headless.

## 2026-05-16 — Audit fix pass

Source: codex mid-project audit response at
`AgentCoordination/Scratchpad/Consult/20260516T083518Z_proj-fms-c-audit/response.md`.

### Fix 1 (P1) — Tactical fighter launch now has a real production caller

**Audit finding.** `BattleEngine.launch_fighters_in_battle()` existed but
was only invoked from tests. The shipped quickstart carrier
`data/designs/qs_carrier.json` still mounted the legacy
`fighter_launch_bay` component (`VehicleLaunchAbility` + class-string
spawn), and `weapon_firing_system._process_hangar_launch` still
auto-launched via that legacy path. The "replace auto-launch with
explicit design-instance action" claim was false in production.

**Decision.** Per CLAUDE.md Rule 3 (root-cause, no shims):

1. **New `CarrierAIController` (game/ai/carrier_controller.py).** A
   :class:`AIController` subclass that — in addition to the base
   movement/targeting/weapon-firing behaviour — runs a per-tick
   auto-launch check. When the ship has a
   `TacticalFighterLaunchAbility` component, loaded fighter
   `CarriedVehicle`s, an enemy in launch radius, and the cooldown is
   ready, it calls `BattleEngine.launch_fighters_in_battle(...)`. This
   is the "AI action" path the user explicitly asked for ("explicit
   player/AI action" rather than weapon-system auto-launch). The
   factory dispatch (`AIControllerFactory.create_for_ship`) checks for
   `TacticalFighterLaunchAbility` on the ship's components and returns
   a `CarrierAIController` instead of the standard `AIController`.
   `BattleEngine.__init__` calls the new
   `AIControllerFactory.set_engine(self)` so the factory can thread
   the engine into each `CarrierAIController` it builds.
2. **`qs_carrier.json` migrated** off the legacy `fighter_launch_bay`
   to 2× `fighter_launch_bay_small` (`TacticalFighterLaunch` +
   `StrategicFighterLaunch`) on OUTER, plus a `vehicle_bay_medium` on
   INNER (provides `VehicleBay.capacity_mass = 750` for design-instance
   storage). One of the two small launch bays gets deactivated by the
   OUTER mass-budget cap, so the carrier ships with 1 active tactical
   launch bay + 1 active strategic launch bay. Stats were re-snapshot:
   mass 6807 → 6467, max_hp 19802 → 19602, max_speed 4.407 → 4.639,
   turn_speed 16.025 → 17.305, acceleration 0.0647 → 0.0717.
3. **Legacy `VehicleLaunchAbility` REMOVED.** The class itself is
   deleted from `game/simulation/components/abilities/markers.py`, its
   registration is removed from `abilities/__init__.py`, the
   `fighter_launch_bay` entry is deleted from `data/components.json`,
   and `data/stats_sections.json` is updated to use
   `TacticalFighterLaunch` / `StrategicFighterLaunch` for the Fighter
   Support visibility check. Per Rule 3, this is full removal — not a
   deprecation-warning compatibility shim.
4. **Legacy auto-launch path removed**: `weapon_firing_system._process_hangar_launch`
   is deleted from `game/simulation/combat/weapon_firing_system.py`,
   along with the `VehicleLaunch` branch in `fire_weapons`. The legacy
   `fighter_class`-string branch in `attack_processor.process_launch_attack`
   is gone; payloads without `carried_vehicle` are skipped (the legacy
   "deprecation warning + parallel path" approach the original subagent
   left is replaced by full removal).
5. **Stat contributor `launch.py` simplified** to only the
   `TacticalFighterLaunch` shape. The registry key changed from
   `VehicleLaunch` to `TacticalFighterLaunch`. `VehicleStorage` still
   feeds `fighter_capacity` when co-located with a tactical launch
   ability — gating shape preserved.
6. **`DesignRole.CARRIER` classification** keyed on
   `{"TacticalFighterLaunch", "StrategicFighterLaunch"}` instead of
   `{"VehicleLaunch"}`.
7. **Production-path integration test added** at
   `tests/integration/test_fms_c_carrier_ai_launch.py` (3 tests):
   factory dispatches a tactical-launch-capable ship to
   `CarrierAIController`; one AI tick with carrier + enemy + loaded
   `CarriedVehicle` invokes `engine.launch_fighters_in_battle`; no
   enemy → no launch.

### Fix 2 (P2) — In-battle launch/reboard loop now preserves component damage state

**Audit finding.** Strategic recovery preserves `ship.components` end-to-
end via `RecoverFightersOrderHandler` + `LaunchFightersOrderHandler`,
but the in-battle launch/reboard loop only carried `current_hp`. A
fighter damaged in battle and reboarded would be silently fully-
repaired by the bay round-trip.

**Fix.**
- `fighter_reboard._ship_to_carried_vehicle` now reads `ship.components`
  into `CarriedVehicle.component_states`.
- `attack_processor._spawn_from_carried_vehicle` now applies
  `cv.component_states` to the spawned ship's `components` map.
- New test file `tests/unit/simulation/systems/test_fighter_reboard_component_state.py`
  (3 tests) pins the asymmetric directions plus an end-to-end round
  trip (damage in battle → reboard → re-launch → identical per-
  component HP).

### Inline risk — Ability gating loophole closed

**Audit finding.** `LAUNCH_FIGHTERS` and `RECOVER_FIGHTERS` were
exempted from the ability-lookup contract in
`test_command_registry_contract.py`. `ActionTimeResolver` fell through
to `action_time = 1` regardless of whether the issuing ship actually
had `StrategicFighterLaunchAbility` / `RecoverFightersAbility`.

**Fix.**
- `LaunchFightersCommandHandler` now declares
  `action_ability_name='StrategicFighterLaunch'` in its `@command_spec`.
- `RecoverFightersCommandHandler` now declares
  `action_ability_name='RecoverFighters'`.
- Both order types are REMOVED from `_ABILITY_LOOKUP_EXEMPT` in
  `test_command_registry_contract.py`; the static `ORDER_TO_ABILITY_MAP`
  test pins their values. The contract test now actively rejects any
  future attempt to re-exempt them.

### Test migration

Tests that exercised the legacy `VehicleLaunchAbility` / `Ship`-
constructor LAUNCH path were migrated to the design-instance shape:
- `tests/unit/simulation/systems/test_battle_engine_tick.py::TestFighterLaunchProcessing`
  (5 tests rewritten) + `TestDictBasedAttackProcessing::test_dict_launch_attack_processed`
  + `TestLoggerIntegration::test_fighter_launch_logged`.
- `tests/unit/simulation/systems/test_fighter_launch_init.py` (3 tests
  rewritten — `test_fighter_has_event_bus_set` now asserts
  `set_event_bus` was called with `engine.combat_events` rather than
  reaching into the inner `combat_engine._event_bus`).
- `tests/unit/simulation/entities/stat_contributors/test_launch.py`
  (rewritten to drive `TacticalFighterLaunch` shapes).
- `tests/unit/simulation/entities/test_ship_stats.py`
  (`_HangarComponent` stub keyed on `TacticalFighterLaunch`).
- `tests/unit/simulation/components/abilities/test_markers.py` —
  `TestVehicleLaunchAbility` class removed; coverage is now in
  `test_tactical_fighter_launch.py`.
- `tests/unit/simulation/combat/test_weapon_firing_system.py` —
  `TestHangarLaunch` and `TestHangarLaunchEdgeCases` removed; auto-
  launch path is gone.
- `tests/unit/entities/test_abilities.py` /
  `test_ability_interface.py` — legacy `VehicleLaunchAbility` tests
  removed.
- `tests/unit/modifiers/test_defense_marker_bindings.py` —
  `TestVehicleLaunchBindings` removed.
- `tests/unit/strategy/data/test_design_role.py` —
  `test_carrier_detected_by_vehicle_launch` renamed and rewritten to
  use `TacticalFighterLaunch`.
- `tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py::TestLegacyFighterClassLaunchDeprecated`
  replaced by `TestLegacyFighterClassLaunchRemoved` — the legacy
  payload now drops cleanly with no spawn.
- `tests/unit/simulation/entities/test_ship_stats_golden.py` —
  `test_carrier_design_exercises_typed_vehicle_abilities` now asserts
  the new launch fields (`fighters_per_wave`, `launch_cycle`,
  `bay_capacity_mass`); `qs_carrier` snapshot regenerated.

### What is NOT in this pass

- Pygame UI bindings for player-facing fighter launch / recover
  actions. The facade dispatch helpers and engine action surface are
  fully production-reachable via the AI path; the player-facing UI
  binding is a follow-up.
- Auto-launch decision-tree tuning. `CarrierAIController` uses a
  simple "any enemy in launch radius + cooldown ready" trigger. Wave-
  size tuning, target priorities (escort vs intercept), and combat-
  state-aware launch holds are follow-up AI work.
