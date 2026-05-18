# PROJ-FMS-C Implementation Report

**Status:** All 4 phases shipped (2026-05-16); audit fix pass applied
the same day (2026-05-16) — see Audit Fix Pass section below and
[`audit_fix_report.md`](audit_fix_report.md).
**Scope:** Fighters end-to-end — design → bay → strategic launch →
contested-hex tactical combat → strategic recovery, plus mid-battle
launches that auto-reboard at battle end with overflow into sector
fighter_groups, plus a minimal "target nearest enemy" fighter AI.
**Pre-existing baseline:** 20525 tests / 20506 passed / 9 failed / 6
errors / 4 skipped (PROJ-FMS-B post-audit; verified against
`Projects/active_projects/PROJ-FMS-B/findings/implementation_report.md:139`).

## Per-phase deliverables

### Phase 1 — Strategic + tactical fighter launch (design-instance based)

- New `IssueLaunchFightersCommand` DTO at
  `game/strategy/engine/commands/__init__.py` plus
  `LaunchFightersCommandHandler` at
  `game/strategy/engine/handlers/launch_fighters.py`.
- New `LaunchFightersOrderHandler` at
  `game/strategy/engine/order_handlers/launch_fighters.py`. Mints a
  fresh `fighter_group` Fleet per launch action (no auto-merge,
  mirrors PROJ-FMS-B Fix 4). Materialises a deployed `ShipInstance`
  per popped `CarriedVehicle`; HP and per-component damage state
  preserved through the transition.
- Tactical launch design-instance path: extended
  `attack_processor.process_launch_attack` to accept a
  `carried_vehicle` payload that drives a full
  `ShipSerializer.from_dict` spawn (full components / weapons / HP).
  Legacy `fighter_class`-string path retained with a per-call
  deprecation warning.
- New `BattleEngine.launch_fighters_in_battle(carrier,
  [CarriedVehicle, ...])` action surface. Each launched fighter is
  tagged with `launched_in_battle_id` for end-of-battle reboard.
- Stat-contributor `contribute_vehicle_launch` extended to also read
  `TacticalFighterLaunchAbility` (capacity_per_action / cycle_time)
  alongside the legacy `VehicleLaunchAbility`. **Superseded twice:**
  (a) audit Fix 1 simplified the contributor to
  `TacticalFighterLaunch` only (legacy class deleted); (b) Round 4
  renamed the per-ship fields from `fighters_per_wave` /
  `launch_cycle` to a single `fighter_launch_rate_tons_per_sec` (the
  cycle-based cooldown stat is gone). See decisions.md "2026-05-17 —
  Round 4 follow-up".
- `OrderType.LAUNCH_FIGHTERS` moved from
  "reserved-no-command-yet" to the reachable-via-command set in
  `test_command_registry_contract.py`. `ACTION_ORDER_TYPES` extended.
  Command registry seeding count bumped 36 → 38 (with Phase 3's
  `RECOVER_FIGHTERS`).
- Registered `LaunchFightersOrderHandler` in
  `order_handlers/registry_factory.py::create_default_order_handler_registry`.

### Phase 2 — Combat join + fighter AI

- Added `FighterAIController` at `game/ai/fighter_controller.py`.
  Minimal "target nearest enemy" loop: spatial-grid scan → set target
  → turn + thrust + pull trigger. Kamikaze fighters (with
  `RamTargetAbility.target_id`) defer movement to the engine's
  `RamTargetResolver` (PROJ-FMS-B Phase 4).
- `AIControllerFactory.create_for_ship` now dispatches on
  `ship.vehicle_type`: `"Fighter"` → `FighterAIController`; everything
  else → standard `AIController`.
- Verified `_split_mine_groups_from_fleets` only filters
  `mine_group`s. `fighter_group`s flow through the normal
  `fleets_by_owner` grouping in `build_strategy_battle_spec` and
  merge onto the owner's team automatically.

### Phase 3 — Recovery + end-of-battle reboard

- New `IssueRecoverFightersCommand` DTO and
  `RecoverFightersCommandHandler` at
  `game/strategy/engine/handlers/recover_fighters.py`.
- New `RecoverFightersOrderHandler` at
  `game/strategy/engine/order_handlers/recover_fighters.py`. Pops
  ShipInstances from the source `fighter_group`, converts each back
  to a `CarriedVehicle` preserving HP and per-component damage state,
  loads into the recovering carrier's bay via
  `ShipCargoManager.load_vehicle`. Partial recovery allowed; empty
  groups pruned from `empire.fleets`. Registered in
  `order_handlers/registry_factory.py`.
- `OrderType.RECOVER_FIGHTERS` moved into the reachable-via-command
  set and `ACTION_ORDER_TYPES`. Command registry count 37 → 38.
- New `game/simulation/systems/fighter_reboard.py` with
  `ReboardTracker` + `apply_reboard(engine, fleets, empires)`.
  Reboard policy:
  - In-battle-launched survivors → friendly ships with bay space.
  - Overflow → new `fighter_group` at the sector, OR merges into a
    pre-existing same-empire fighter_group at the same hex.
  - Dead-on-arrival → discarded.
  - Carrier-destroyed-mid-battle → finds another live friendly
    carrier; otherwise overflow.
- `attack_processor.process_launch_attack` registers each spawned
  in-battle fighter on the engine's `reboard_tracker`.
- `spec_compiler.build_fighter_reboard_setup(participating_fleets,
  engine_ref=...)` returns a `pre_tick_loop_callback` that installs
  the tracker on the engine and parks the engine on the spec's
  shared `_engine_ref` list. The strategy post-battle hook reads
  `_engine_ref[0]` and calls `apply_reboard` BEFORE
  `apply_outcome_to_fleets` so reboarded fighters land before
  empty-fleet pruning.
- `SimulationBattleResolver._run_simulated_battle` composes
  `mine_resolver_setup` + `reboard_setup` into a single
  `pre_tick_loop_callback` via the new `_compose_setup_callbacks`
  helper.

### Phase 4 — Integration tests + E2E + docs

- New `tests/integration/test_fms_c_e2e.py` (3 tests): strategic
  launch → strategic recover round trip with HP preservation, partial
  recovery, and combat-join contract pinning.
- New `tests/integration/test_fms_c_launch_in_battle_e2e.py` (3
  tests): mid-battle launch + reboard, mid-battle launch + overflow,
  dead-fighter discard.
- New `docs/systems/fighters.md` describing the full system end-to-
  end + file map + test map.
- Updated `docs/systems/ability_reference.md` with a PROJ-FMS-C
  section pinning the runtime behaviour of
  `StrategicFighterLaunchAbility`, `TacticalFighterLaunchAbility`,
  `RecoverFightersAbility`. Updated the "reserved enum values still
  pending" line to reflect FMS-C completion.
- Updated `docs/README.md` systems table + doc map to include
  fighters.md.

## Tests added

| File | Count | Phase |
|---|---|---|
| `tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py` | 8 | 1 |
| `tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py` | 4 | 1 |
| `tests/unit/strategy/combat/test_fighter_group_combat_join.py` | 3 | 2 |
| `tests/unit/ai/test_fighter_controller.py` | 5 | 2 |
| `tests/unit/strategy/engine/order_handlers/test_recover_fighters_handler.py` | 7 | 3 |
| `tests/unit/simulation/systems/test_fighter_reboard.py` | 6 | 3 |
| `tests/integration/test_fms_c_e2e.py` | 3 | 4 |
| `tests/integration/test_fms_c_launch_in_battle_e2e.py` | 3 | 4 |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | MODIFIED | 1+3 |
| `tests/unit/strategy/engine/test_command_registry_seeding.py` | MODIFIED | 1+3 |
| `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` | MODIFIED | 1+3 |

**Total: 39 new tests across 8 new test files, 3 modified test files.**

## Sharded suite status

Run command: `python Tools/test_sharded/test_sharded.py` (2026-05-16,
post audit-fix pass).

```
TOTAL: 20568 tests | 20549 passed | 9 failed | 6 errors | 4 skipped
Wall time: 164.1s (12 shards)
```

Compared to the PROJ-FMS-B post-audit baseline (20525 / 20506):

- **Test count: 20525 → 20568 (+43 net).** The audit-fix pass added
  ~30 new tests (5 carrier-controller, 3 carrier-AI integration,
  3 component-state round trip, 1 storage-without-tactical-launch,
  plus migrations) and removed ~20 tests pinning the deleted
  `VehicleLaunchAbility` surface.
- **Passed: 20506 → 20549 (+43 passing).**
- **Failed: 9 → 9 (same pre-existing).**
- **Errors: 6 → 6 (same pre-existing).**
- **Skipped: 4 → 4 (unchanged).**
- **Zero new failures from PROJ-FMS-C, including the audit-fix pass.**

All 9 failures + 6 errors are the **same pre-existing set** documented
in `Projects/active_projects/PROJ-FMS-B/findings/implementation_report.md`:

- 3 `test_ship_stats_golden::acceleration_rate` (qs_escort,
  qs_frigate_gc, qs_battleship).
- 5 `test_quickstart_designs::test_design_has_metadata`.
- 1 `test_ship_instance_damage::test_iter_keys_match_full_hp_builder_for_cross_layer_design`
  (known flake).
- 6 `test_design_load_warp_capability` errors.

## Decisions captured

See `Projects/active_projects/PROJ-FMS-C/decisions.md`. Four phase
sections cover:

1. No-auto-merge for same-hex launches (mirrors PROJ-FMS-B Fix 4);
   fighter_group id namespace at 200000+.
2. HP preservation strategy; mixed-design groups via design filter.
3. `launched_in_battle_id` tag semantics — set only by tactical
   launches; not present on strategic-launch ShipInstances.
4. Tactical launch action surface = explicit
   `BattleEngine.launch_fighters_in_battle`; legacy
   `VehicleLaunchAbility` path kept with deprecation warning.
5. Stat-contributor extension is additive — reads both new and
   legacy ability shapes into the same per-ship fields.
6. `FighterAIController` is its own class (not a policy alias);
   dispatches on `vehicle_type`.
7. Kamikaze handling defers movement to `RamTargetResolver` while
   still pulling the trigger for non-ram weapons.
8. Recovery is strategic-action-only; tactical reboard is the
   end-of-battle hook for tagged launches.
9. Overflow merges into a pre-existing same-empire fighter_group at
   the same hex.
10. Engine reference passed via shared list side-channel — mirrors
    PROJ-FMS-B's mine_group `_tactical_resolver` parking pattern.
11. Pre-tick callback composition via `_compose_setup_callbacks` so
    mine resolver + reboard setup coexist on the same `run_battle`
    kwarg slot.

## Production wiring inventory

This section explicitly enumerates every production caller that was
wired vs not wired, per the audit-lesson rule from PROJ-FMS-B.

> **Historical pre-audit snapshot (2026-05-16 reconciliation):** The
> tables below reflect the state at the end of the PROJ-FMS-C
> implementation phases. The subsequent audit-fix pass (see
> [`audit_fix_report.md`](audit_fix_report.md) Fix 1) **removed** the
> legacy `VehicleLaunchAbility` deprecation path entirely and
> **shipped** a production `CarrierAIController` for carrier-side
> auto-launch decisions. Treat the "Legacy `VehicleLaunchAbility`
> deprecation warning" YES row and the "Auto-launch AI ... follow-up"
> bullet as superseded — the post-audit architecture is design-instance
> only, with `CarrierAIController` driving carrier launch timing via
> `AIControllerFactory.create_for_ship`.

### Wired into production game-loop callers

| Caller | Path | Wired? |
|---|---|---|
| `TurnEngine` → `ActionExecutionEngine` → `OrderHandlerRegistry` | `create_default_order_handler_registry` registers both `LaunchFightersOrderHandler` and `RecoverFightersOrderHandler` | YES |
| Command registry → strategy facade dispatch | `seed_default_commands` imports `handlers.launch_fighters` and `handlers.recover_fighters`; both `register(registry)` calls fire | YES |
| `IssueLaunchFightersCommand` → `LaunchFightersCommandHandler` → `OrderType.LAUNCH_FIGHTERS` order | metadata-only `@command_spec` attaches `__command_spec_kwargs__`; module's `register()` adds the spec; facade resolves `dispatch_issue_launch_fighters` automatically via the dispatch helper resolver | YES |
| `IssueRecoverFightersCommand` → `RecoverFightersCommandHandler` → `OrderType.RECOVER_FIGHTERS` order | same | YES |
| Spec compiler → `fighter_group` translation onto owner's team | natural pass-through via `_split_mine_groups_from_fleets` (only filters mine_groups) + `fleets_by_owner` grouping | YES |
| Battle engine → `FighterAIController` | `AIControllerFactory.create_for_ship` dispatches on `ship.vehicle_type == "Fighter"` | YES |
| Mid-battle launch → in-battle ship tagging → reboard tracker | `BattleEngine.launch_fighters_in_battle` + `attack_processor.process_launch_attack` set `launched_in_battle_id` AND register on `engine.reboard_tracker` when present | YES |
| End-of-battle reboard | `SimulationBattleResolver._run_simulated_battle` builds `build_fighter_reboard_setup` callback and composes it with mine_resolver_setup; `_build_strategy_post_battle_hook` reads the engine via the shared `_engine_ref` list and calls `apply_reboard` before `apply_outcome_to_fleets` | YES |
| Legacy `VehicleLaunchAbility` deprecation warning | `attack_processor.process_launch_attack` logs once per legacy launch | YES |

### NOT wired (deferred / not in scope)

- **Pygame UI binding for `IssueLaunchFightersCommand` and
  `IssueRecoverFightersCommand`.** The facade `dispatch_*` helpers
  are reachable on `CommandDispatchSlice` (verified by the contract
  test), but no Pygame screen / panel renders launch/recover action
  buttons or carries the in-battle "Launch wave" action surface.
  Same deferred shape as PROJ-FMS-B's sensitivity / threshold UI.
- **Mid-battle tactical launch UI** (in-battle "Launch fighter wave"
  action button on the carrier ship's panel). Production code path
  exists (`BattleEngine.launch_fighters_in_battle`); UI binding is a
  follow-up.
- **Auto-launch AI** (an AI player deciding when to mid-battle-launch
  a wave of fighters from a carrier). Action surface exists; AI
  decision logic is a follow-up — fighter AI for the LAUNCHED
  fighters is in place (`FighterAIController`), but the AI for the
  CARRIER deciding when to launch is not.
- **Save/load round-trip for `launched_in_battle_id`.** The tag is
  ephemeral (set at spawn, cleared by reboard); persistence is not
  needed because the reboard hook fires at end-of-battle, BEFORE the
  save layer touches the post-battle state. If the game crashes
  mid-battle the next session would lose the tag, but the
  fighter_group fleet ID is the persistence layer.

## Known limitations / things for codex consult

1. **No mass-from-stats fallback for newly-launched fighters' bay
   storage.** When a CarriedVehicle is created from a deployed
   ShipInstance during reboard, the mass field is read from
   `expected_stats.mass` (via `ShipSerializer.to_dict`). For
   minimal test stubs this falls back to 0.0, which lets unlimited
   reboard packing happen on stubs. Production designs always carry
   `expected_stats.mass`, so this is test-fixture-only.
2. **Reboard tracker installation is gated on having any participating
   fleet.** `build_fighter_reboard_setup` returns `None` when
   `participating_fleets` is empty (e.g. the "sole survivor"
   shortcut in `SimulationBattleResolver.resolve_battle` short-
   circuits before this point anyway).
3. **`engine.reboard_tracker` is the implicit "Phase 3 wired" flag.**
   When the spec compiler doesn't run (Combat Lab, direct battle-
   setup callers), the tracker is None and `attack_processor.process_launch_attack`
   silently skips the registration. This is intentional — those
   callers don't have an empire/fleet to reboard to.
4. **No statistical balance tests for fighter AI.** Fighter AI is
   deterministic given the same spatial grid contents; no flaky
   binomial bounds to pin.
5. **Three pre-existing baseline failures unrelated to FMS-C:**
   `test_ship_stats_golden::acceleration_rate` on qs_escort,
   qs_frigate_gc, qs_battleship. Same drift documented in
   PROJ-FMS-A and PROJ-FMS-B reports.

## File list — every file touched

### Production code

- `game/strategy/engine/commands/__init__.py` — added
  `IssueLaunchFightersCommand` and `IssueRecoverFightersCommand` DTOs.
- `game/strategy/engine/commands/registry.py` — added `launch_fighters`
  and `recover_fighters` to the seed module list.
- `game/strategy/engine/handlers/launch_fighters.py` — NEW
  (`LaunchFightersCommandHandler`).
- `game/strategy/engine/handlers/recover_fighters.py` — NEW
  (`RecoverFightersCommandHandler`).
- `game/strategy/engine/order_handlers/launch_fighters.py` — NEW
  (`LaunchFightersOrderHandler`).
- `game/strategy/engine/order_handlers/recover_fighters.py` — NEW
  (`RecoverFightersOrderHandler`).
- `game/strategy/engine/order_handlers/registry_factory.py` —
  registered both new order handlers.
- `game/strategy/data/order_types.py` — added `LAUNCH_FIGHTERS` and
  `RECOVER_FIGHTERS` to `ACTION_ORDER_TYPES`.
- `game/strategy/combat/spec_compiler.py` — added
  `build_fighter_reboard_setup` + threaded `engine_ref` /
  `_engine_ref` / `_combat_fleets` side-channels through the post-
  battle hook + spec.
- `game/strategy/adapters/simulation_adapter.py` — built reboard
  setup callback; composed mine + reboard setups via
  `_compose_setup_callbacks`.
- `game/simulation/systems/attack_processor.py` — replaced
  class-string spawn with design-instance dispatch; added
  `_spawn_from_carried_vehicle`; tagged spawned ships with
  `launched_in_battle_id`; registered on `engine.reboard_tracker`;
  legacy deprecation warning.
- `game/simulation/systems/battle_engine.py` — added
  `BattleEngine.launch_fighters_in_battle(...)` action surface.
- `game/simulation/systems/fighter_reboard.py` — NEW
  (`ReboardTracker`, `apply_reboard`, helpers).
- `game/simulation/entities/stat_contributors/launch.py` — extended
  `contribute_vehicle_launch` to also read
  `TacticalFighterLaunchAbility`.
- `game/ai/fighter_controller.py` — NEW (`FighterAIController`).
- `game/ai/ai_factory.py` — `AIControllerFactory.create_for_ship`
  dispatches `Fighter` vehicle_type to `FighterAIController`.

### Tests

- `tests/unit/strategy/engine/order_handlers/test_launch_fighters_handler.py` — NEW (8 tests).
- `tests/unit/strategy/engine/order_handlers/test_recover_fighters_handler.py` — NEW (7 tests).
- `tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py` — NEW (4 tests).
- `tests/unit/simulation/systems/test_fighter_reboard.py` — NEW (6 tests).
- `tests/unit/strategy/combat/test_fighter_group_combat_join.py` — NEW (3 tests).
- `tests/unit/ai/test_fighter_controller.py` — NEW (5 tests).
- `tests/integration/test_fms_c_e2e.py` — NEW (3 tests).
- `tests/integration/test_fms_c_launch_in_battle_e2e.py` — NEW (3 tests).
- `tests/unit/strategy/engine/test_command_registry_contract.py` —
  `LAUNCH_FIGHTERS` + `RECOVER_FIGHTERS` moved to reachable +
  `ACTION_ORDER_TYPES` extended + `_ABILITY_LOOKUP_EXEMPT` extended.
- `tests/unit/strategy/engine/test_command_registry_seeding.py` —
  count 36 → 38.
- `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` —
  added `dispatch_issue_launch_fighters` and
  `dispatch_issue_recover_fighters`.

### Docs / project

- `docs/systems/fighters.md` — NEW. End-to-end system reference.
- `docs/systems/ability_reference.md` — PROJ-FMS-C section appended;
  reserved-OrderType note updated.
- `docs/README.md` — systems table + doc map updated with
  fighters.md.
- `Projects/active_projects/PROJ-FMS-C/decisions.md` — four phase
  sections + production-wiring inventory.
- `Projects/active_projects/PROJ-FMS-C/plan.md` — Quick Status table
  + Current State updated.
- `Projects/active_projects/PROJ-FMS-C/phase_{1..4}_checklist.md` —
  all `[x]`.
- `Projects/active_projects/PROJ-FMS-C/findings/implementation_report.md` —
  this file, NEW.

## Audit fix pass (2026-05-16)

Codex audited PROJ-FMS-C the same day the original implementation
shipped. Findings: one P1 (tactical fighter launch had no production
caller; shipped carrier still mounted the legacy `VehicleLaunch`
component) and two P2s (in-battle reboard lost per-component damage
state; project artifacts overstated completion). All three were
addressed in a single TDD pass — see
[`audit_fix_report.md`](audit_fix_report.md) for the full diff and
[`../decisions.md`](../decisions.md) "2026-05-16 — Audit fix pass"
section for decision rationale.

Headline changes:
- `CarrierAIController` (new) is now the production caller for
  `BattleEngine.launch_fighters_in_battle`. The factory dispatches
  ships with `TacticalFighterLaunchAbility` to it; the BattleEngine
  threads `self` into the factory via `set_engine`.
- `qs_carrier.json` migrated off the legacy `fighter_launch_bay`
  (`VehicleLaunchAbility`) to `fighter_launch_bay_small` +
  `vehicle_bay_medium`. Stats are intentionally different — golden
  snapshot regenerated.
- The legacy `VehicleLaunchAbility` class, the `VehicleLaunch`
  registration, the `fighter_launch_bay` component entry, the
  `_process_hangar_launch` auto-launch path, and the
  `fighter_class`-string spawn branch in `attack_processor` are all
  fully removed. No deprecation shims (Rule 3).
- In-battle launch/reboard loop preserves `ComponentState` end-to-end.
- `LAUNCH_FIGHTERS` / `RECOVER_FIGHTERS` ability-lookup gating closed:
  `action_ability_name` declared on the command specs and removed from
  the contract-test exempt set.

## Known limitations

After the audit fix pass, the project ships a backend-complete,
production-AI-driven fighter system. Items that remain follow-up:

1. **No pygame UI binding for player-facing launch/recover.** The
   facade dispatch helpers (`dispatch_issue_launch_fighters`,
   `dispatch_issue_recover_fighters`) and engine action surface
   (`BattleEngine.launch_fighters_in_battle`) are production-reachable
   via the AI path, but no Pygame screen renders an explicit
   player-action button. Same deferred shape as PROJ-FMS-B's
   sensitivity / threshold UI.
2. **Carrier auto-launch policy is naive.** `CarrierAIController` uses
   "any enemy in launch radius + cooldown ready" as the trigger. Wave-
   size tuning, escort vs intercept target priorities, combat-state-
   aware launch holds — all follow-up AI work.
3. **In-game manual smoke verification was deferred.** The
   integration tests cover the AI launch + reboard + damage state
   contracts in isolation; no human has played through "design fighter
   → build → launch from carrier in tactical battle → reboard →
   recover via strategic action → save/load" end-to-end. Marked as
   manual follow-up.
4. **No mass-from-stats fallback for newly-launched fighters' bay
   storage.** When a CarriedVehicle is created from a deployed
   ShipInstance during reboard, the mass field is read from
   `expected_stats.mass` (via `ShipSerializer.to_dict`). For minimal
   test stubs this falls back to 0.0, which lets unlimited reboard
   packing happen on stubs. Production designs always carry
   `expected_stats.mass`, so this is test-fixture-only.
5. **Three pre-existing baseline failures unrelated to FMS-C:**
   `test_ship_stats_golden::acceleration_rate` on qs_escort,
   qs_frigate_gc, qs_battleship. Documented in PROJ-FMS-A and
   PROJ-FMS-B reports as the same drift.

## Postscript (2026-05-17 final state)

The sharded-suite numbers earlier in this report (20525 / 20506,
etc.) are accurate at PROJ-FMS-C ship time. The final clean baseline
after all four FMS projects + four QA rounds + the PROJ-FMS-D
test-baseline cleanup pass is **20840 / 20840 passed / 0 failed /
0 errors / 0 skipped** — see `PROJ-FMS-D/decisions.md`
"Post-PROJ-FMS test-baseline cleanup pass". Intermediate baselines
quoted in A/B/D implementation reports (20460, 20525, 20646) are
likewise correct at their respective snapshot times.

Round 4 follow-up notes specific to PROJ-FMS-C are in
`PROJ-FMS-C/decisions.md` "2026-05-17 — Round 4 follow-up":
tactical-launch rewritten from count-per-cycle/cooldown to
mass-tons/sec budget; bay components consolidated
(`fighter_launch_bay` now also carries `RecoverFighters`); FMS
commands polymorphic via `IIssuerAdapter` (Pattern #40).
