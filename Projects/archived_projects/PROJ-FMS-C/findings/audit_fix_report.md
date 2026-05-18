# PROJ-FMS-C Audit Fix Report

**Date:** 2026-05-16
**Source audit:** `AgentCoordination/Scratchpad/Consult/20260516T083518Z_proj-fms-c-audit/response.md`
**Scope:** Three remediations on top of the original PROJ-FMS-C
implementation (one P1 blocker + two P2 follow-ups), plus one inline
risk fix. No PROJ-FMS-A, PROJ-FMS-B, or PROJ-FMS-C work was reverted;
this pass is purely additive + behaviour-correcting.

## Audit summary

Codex's mid-project audit identified that PROJ-FMS-C's new tactical
fighter launch action surface existed but was never wired into any
production caller — the shipped quickstart carrier still mounted the
legacy `VehicleLaunch` component, and the weapon-firing-system auto-
launch path was the only way for fighters to actually launch in
battle. The new `BattleEngine.launch_fighters_in_battle` was reachable
only from tests. The P2 follow-ups identified missing per-component
damage state in the in-battle reboard round trip and overstated
completion language in project artifacts.

All three (P1 + 2× P2) plus an inline risk (ability-lookup gating
loophole on `LAUNCH_FIGHTERS` / `RECOVER_FIGHTERS`) were fixed in a
single TDD pass.

## Fixes applied

### Fix 1 (P1) — Tactical fighter launch has a real production caller

**Was.** `BattleEngine.launch_fighters_in_battle()` existed at
`game/simulation/systems/battle_engine.py:492-531` but no production
code path called it; `git grep -n "launch_fighters_in_battle("` found
the definition + the integration test only. The shipped carrier
`data/designs/qs_carrier.json` still mounted the legacy
`fighter_launch_bay` (`VehicleLaunchAbility` + class-string spawn),
and `weapon_firing_system._process_hangar_launch` still auto-launched
on every tick when a target was visible.

**Fix.** Per CLAUDE.md Rule 3 (root-cause, no compatibility shims):

1. **New `CarrierAIController` at `game/ai/carrier_controller.py`.**
   Subclasses `AIController` so the carrier keeps full ship-AI
   behaviour. Per-tick `update()` runs base behaviour first, then
   checks for `TacticalFighterLaunchAbility` + loaded fighter
   `CarriedVehicle`s + enemy in launch radius + cooldown ready, and
   calls `engine.launch_fighters_in_battle(carrier, [cv, ...])`.
   Pops up to `capacity_per_action` CVs from the carrier's
   `carried_items` per wave. Cooldown is tick-based on the ability's
   `cycle_time` (at 60 Hz default).

2. **Factory dispatch.** `AIControllerFactory.create_for_ship` now
   walks the ship's components looking for `TacticalFighterLaunch`;
   when present + `set_engine` was called, returns a
   `CarrierAIController` instead of a vanilla `AIController`.
   `BattleEngine.__init__` calls `self._ai_factory.set_engine(self)`
   (via `getattr`, optional — test mocks without that surface skip
   cleanly).

3. **`qs_carrier.json` migrated.** OUTER layer: 2×
   `fighter_launch_bay` (each mass 500 + VehicleLaunch) → 2×
   `fighter_launch_bay_small` (each mass 80, TacticalFighterLaunch +
   StrategicFighterLaunch). INNER layer: added `vehicle_bay_medium`
   (mass 500, `VehicleBay.capacity_mass = 750`). One of the two
   small launch bays gets deactivated by the OUTER mass-budget cap
   (`max_mass_pct: 0.5` on Capital_Standard); the carrier ships with
   1 active tactical bay + 1 active strategic bay. Stats:
   mass 6807 → 6467, max_hp 19802 → 19602, max_speed 4.407 → 4.639,
   turn_speed 16.025 → 17.305, acceleration 0.0647 → 0.0717.
   Golden snapshot regenerated for `qs_carrier`.

4. **Legacy `VehicleLaunchAbility` class REMOVED.**
   - `game/simulation/components/abilities/markers.py` — class
     deleted (was 53 lines: `_parse_attrs`, `recalculate`, `update`,
     `try_launch`, `get_ui_rows`, `get_primary_value` plus stat
     binding).
   - `game/simulation/components/abilities/__init__.py` — removed
     from imports, ability registration dict (`"VehicleLaunch":
     VehicleLaunchAbility`), and `__all__`.
   - `data/components.json` — `fighter_launch_bay` component entry
     deleted (was the only consumer).
   - `data/stats_sections.json` — `fightersupport` visibility check
     keyed on `["TacticalFighterLaunch", "StrategicFighterLaunch"]`.
   - `game/strategy/data/design_role.py::_CARRIER_ABILITIES` updated.

5. **Legacy auto-launch / spawn path REMOVED.**
   - `game/simulation/combat/weapon_firing_system.py` —
     `_process_hangar_launch` method deleted, `VehicleLaunch` branch
     removed from `fire_weapons`.
   - `game/simulation/systems/attack_processor.py` — legacy
     `fighter_class`-string spawn branch deleted from
     `process_launch_attack`. Payloads without `carried_vehicle` are
     now logged + skipped. The `Ship` direct import was moved to
     `TYPE_CHECKING`.

6. **Stat contributor simplified.**
   `game/simulation/entities/stat_contributors/launch.py::contribute_vehicle_launch`
   now reads only `TacticalFighterLaunch` + co-located `VehicleStorage`.
   `game/simulation/entities/stat_contributors/registry.py` registration
   key changed from `"VehicleLaunch"` to `"TacticalFighterLaunch"`.

**Files touched** (Fix 1 production code):
- NEW: `game/ai/carrier_controller.py`
- `game/ai/ai_factory.py` — added `set_engine`, carrier-dispatch logic
- `game/simulation/systems/battle_engine.py` — calls
  `self._ai_factory.set_engine(self)` in `__init__`
- `game/simulation/systems/attack_processor.py` — legacy branch removal
- `game/simulation/combat/weapon_firing_system.py` — hangar-launch
  path removal
- `game/simulation/components/abilities/markers.py` —
  `VehicleLaunchAbility` deletion
- `game/simulation/components/abilities/__init__.py` — registration
  deletion
- `game/simulation/entities/stat_contributors/launch.py` — legacy
  branch removal
- `game/simulation/entities/stat_contributors/registry.py` — key
  rename
- `game/strategy/data/design_role.py` — `_CARRIER_ABILITIES` update
- `data/components.json` — `fighter_launch_bay` deleted
- `data/designs/qs_carrier.json` — migrated
- `data/stats_sections.json` — visibility check updated
- `tests/unit/simulation/entities/test_ship_stats_golden_snapshot.json` —
  `qs_carrier` slot regenerated

**Tests added** (Fix 1):
- `tests/unit/ai/test_carrier_controller.py` — 5 tests:
  launches-when-ready, no-enemy → no-launch, no-cargo → no-launch,
  cooldown-between-waves, legacy-VehicleLaunch-only → no-launch.
- `tests/integration/test_fms_c_carrier_ai_launch.py` — 3 tests:
  factory-dispatches-CarrierAIController, AI-tick-drives-engine-launch,
  no-enemy-no-launch — exercises the production AI factory wiring,
  not just the controller in isolation.

### Fix 2 (P2) — Per-component damage state preserved through in-battle reboard

**Was.** Strategic recovery preserves `ship.components` end-to-end via
`RecoverFightersOrderHandler` (captures into
`CarriedVehicle.component_states`) and `LaunchFightersOrderHandler`
(restores from it). The in-battle launch/reboard loop did not:
- `fighter_reboard._ship_to_carried_vehicle` only captured
  `design_data`, `mass`, `current_hp`.
- `attack_processor._spawn_from_carried_vehicle` only restored
  `current_hp`.

A fighter damaged in battle and reboarded would be silently fully-
repaired by the bay round-trip.

**Fix.**
- `fighter_reboard._ship_to_carried_vehicle` now reads
  `getattr(ship, "components", None)` and writes it into
  `CarriedVehicle.component_states`.
- `attack_processor._spawn_from_carried_vehicle` now applies
  `cv.component_states` to the spawned ship's `components` map
  (after the HP restore), in a try/except so minimal stubs that
  treat `components` as a property don't break the launch.

**Files touched** (Fix 2):
- `game/simulation/systems/fighter_reboard.py`
- `game/simulation/systems/attack_processor.py`

**Tests added** (Fix 2):
- `tests/unit/simulation/systems/test_fighter_reboard_component_state.py` —
  3 tests: capture-on-reboard, restore-on-launch, end-to-end
  damage-survives-round-trip.

### Inline risk — Ability gating loophole closed

**Was.** `tests/unit/strategy/engine/test_command_registry_contract.py`
exempted `LAUNCH_FIGHTERS` / `RECOVER_FIGHTERS` from the ability-
lookup contract; `ActionTimeResolver` fell through to default
`action_time = 1` regardless of which ship issued the order. Once UI
wiring lands, any ship could issue these orders.

**Fix.**
- `LaunchFightersCommandHandler` `@command_spec` declares
  `action_ability_name='StrategicFighterLaunch'`.
- `RecoverFightersCommandHandler` `@command_spec` declares
  `action_ability_name='RecoverFighters'`.
- Both order types REMOVED from `_ABILITY_LOOKUP_EXEMPT` in the
  contract test; the static `ORDER_TO_ABILITY_MAP` value pin asserts
  the new mappings explicitly. A future re-exemption is a deliberate
  regression that surfaces here.

**Files touched**:
- `game/strategy/engine/handlers/launch_fighters.py`
- `game/strategy/engine/handlers/recover_fighters.py`
- `tests/unit/strategy/engine/test_command_registry_contract.py`

### Fix 3 (P2) — Project artifacts corrected

After Fix 1 + Fix 2 land, the "all phases shipped" language becomes
accurate for the backend; the report and decisions log have been
updated to reflect the audit-fix pass, the corrected baseline
citation, and an explicit Known Limitations section (no pygame UI
binding, carrier-AI is naive, manual-smoke verification deferred).

The PROJ-FMS-B baseline cited in the original report (20525 / 20506
passed) is correct — verified against
`Projects/active_projects/PROJ-FMS-B/findings/implementation_report.md:139`.
Codex's `20536 / 20517` number does not appear in the tracked repo
artifacts; treating the report's `20525 / 20506` as canonical.

## Test migration

Tests that exercised the legacy `VehicleLaunchAbility` / `Ship`-
constructor LAUNCH path were rewritten or removed:

- `tests/unit/simulation/systems/test_battle_engine_tick.py` —
  `TestFighterLaunchProcessing` (5 tests) rewritten to use
  `_spawn_from_carried_vehicle` mock pattern;
  `TestDictBasedAttackProcessing::test_dict_launch_attack_processed`
  + `TestLoggerIntegration::test_fighter_launch_logged` migrated to
  the same pattern.
- `tests/unit/simulation/systems/test_fighter_launch_init.py` —
  fixture migrated to design-instance payload, mock fighter +
  `ShipSerializer.from_dict` patch. `test_fighter_has_event_bus_set`
  reformulated to assert `set_event_bus` was called with
  `engine.combat_events` rather than reaching into the inner
  `combat_engine._event_bus` attribute.
- `tests/unit/simulation/entities/stat_contributors/test_launch.py` —
  rewritten to drive `TacticalFighterLaunch` shapes; removed
  `test_size_cap_takes_max_not_sum` (the new ability has no
  `max_launch_mass` field). Added `test_storage_without_tactical_launch_is_ignored`
  to pin the gating behaviour.
- `tests/unit/simulation/entities/test_ship_stats.py` — `_HangarComponent`
  stub keyed on `TacticalFighterLaunch`.
- `tests/unit/simulation/components/abilities/test_markers.py` —
  `TestVehicleLaunchAbility` class removed; replacement coverage
  lives in `test_tactical_fighter_launch.py` (PROJ-FMS-A Phase 5).
- `tests/unit/simulation/combat/test_weapon_firing_system.py` —
  `TestHangarLaunch` (1 test) and `TestHangarLaunchEdgeCases` (3
  tests) removed; the auto-launch path is gone.
- `tests/unit/entities/test_abilities.py` +
  `tests/unit/entities/test_ability_interface.py` — legacy
  `VehicleLaunchAbility` tests + import removed.
- `tests/unit/modifiers/test_defense_marker_bindings.py` —
  `TestVehicleLaunchBindings` removed.
- `tests/unit/strategy/data/test_design_role.py` —
  `test_carrier_detected_by_vehicle_launch` renamed to
  `test_carrier_detected_by_tactical_fighter_launch`, fixture updated
  to use `TacticalFighterLaunch`.
- `tests/unit/simulation/components/abilities/test_tactical_fighter_launch.py` —
  `TestLegacyFighterClassLaunchDeprecated` replaced by
  `TestLegacyFighterClassLaunchRemoved`: the legacy payload now drops
  cleanly with no spawn.
- `tests/unit/simulation/entities/test_ship_stats_golden.py` —
  `test_carrier_design_exercises_typed_vehicle_abilities` now asserts
  the new launch fields (`fighters_per_wave`, `launch_cycle`,
  `bay_capacity_mass`).

## Sharded suite status

See the "Sharded suite status" section of [`implementation_report.md`](implementation_report.md)
after the audit-fix pass. Pre-existing baseline failures unchanged:
3× `test_ship_stats_golden::acceleration_rate`, 5×
`test_quickstart_designs::test_design_has_metadata`, 1×
`test_iter_keys_match_full_hp_builder_for_cross_layer_design` flake,
6× `test_design_load_warp_capability` errors — all carried over from
the PROJ-FMS-B baseline.

## What is NOT in this pass

- Pygame UI bindings for player-facing fighter launch / recover
  actions. Facade dispatch helpers and engine action surface are
  production-reachable via the AI path; UI binding is a follow-up.
- Carrier auto-launch policy tuning (wave-size targets, escort vs
  intercept priorities, combat-state-aware holds).
- Manual in-game smoke verification of the full
  design → bay → launch → fight → reboard → recover → save/load loop.
