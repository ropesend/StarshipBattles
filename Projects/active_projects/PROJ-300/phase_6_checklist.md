# Phase 6: Migrate consumers off `AreaEffectManager`

**Status:** Not Started
**Objective:** Rewrite the three consumers (movement engine, environmental hazard engine, combat spec compiler) to query `collect_sector_effects` directly. After this phase, no production code references `AreaEffectManager` or `EnvironmentalEffects` — Phase 7 deletes them.

Each sub-phase is independent and can be committed separately, but all three must land before pushing (because Phase 5 left `area_effect_manager.py` broken when `StormEffect` was deleted).

---

## Tasks

### Task 6.1: Migrate `fleet_movement_engine` [Medium]
**File:** `game/strategy/engine/fleet_movement_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_movement_engine.py` (or whichever file covers `_get_effective_fleet_speed`)

- [ ] Failing test first: `test_fleet_in_dark_nebula_has_strategic_speed_modifier_applied` — fixture creates a galaxy with a single dark_nebula storm at the fleet's hex; assert `_get_effective_fleet_speed` returns `int(base_speed * 0.4)`.
- [ ] Failing test: `test_fleet_outside_storm_has_unmodified_speed`.
- [ ] Failing test: `test_fleet_in_overlapping_ion_and_dark_nebula_multiplies_modifiers` — `0.8 * 0.4 = 0.32` (overlapping multiply).
- [ ] Locate `_get_effective_fleet_speed` (around lines 97-133). Replace the `area_effect_manager.get_effects_at_global_hex(...)` call with:
  ```python
  effects = collect_sector_effects(system, fleet.location, empire_id=fleet.owner_id, registries=registries)
  mult = aggregate_value_or(effects, 'StrategicSpeedModifier', 1.0)
  return max(0, int(base_speed * mult))
  ```
- [ ] Find `system` for the fleet — `galaxy.get_system_at_location(fleet.location)` or similar. If no system contains the hex, treat as no effects (`mult=1.0`).
- [ ] Drop the `area_effect_manager` constructor parameter from `FleetMovementEngine.__init__`. Update all instantiation sites (likely `game/context.py` and the strategy session facade — grep `FleetMovementEngine(`).
- [ ] Run tests — green.

**Notes:**

### Task 6.2: Migrate `environmental_hazard_engine` [Medium]
**File:** `game/strategy/engine/environmental_hazard_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_environmental_hazard_engine.py`, `tests/integration/strategy/test_turn_storms.py`

- [ ] Failing tests first:
  - [ ] `test_fleet_in_radiation_belt_takes_per_tick_damage` — assert hull damage = `(0.8 / 100.0) * tick_count`.
  - [ ] `test_fleet_in_radiation_belt_drains_fuel` — fuel consumed = `(0.1 / 100.0) * tick_count`.
  - [ ] `test_fleet_in_overlapping_ion_and_plasma_storm_takes_only_plasma_damage` — ion has no `EnvironmentalDamage`; plasma has `rate=0.5, damage_type=plasma`. Assert sum = 0.5 / turn.
  - [ ] `test_fleet_in_overlapping_plasma_and_radiation_storms_sums_damage_per_damage_type` — plasma (0.5 plasma) + radiation (0.8 radiation) = 1.3 / turn (different damage_types are different rows; total damage to fleet sums across rows).
- [ ] In `process_environmental_tick`:
  ```python
  for fleet in empires_fleets:
      effects = collect_sector_effects(system_for_fleet, fleet.location, empire_id=None, registries=registries)
      damage_per_turn = sum(e['aggregate_value'] for e in effects if e['ability_name'] == 'EnvironmentalDamage')
      fuel_per_turn   = sum(e['aggregate_value'] for e in effects if e['ability_name'] == 'FuelDrain')
      damage_per_tick = damage_per_turn / 100.0
      fuel_per_tick   = fuel_per_turn   / 100.0
      if damage_per_tick > 0: _apply_damage(fleet, damage_per_tick)
      if fuel_per_tick   > 0: _drain_fuel(fleet, fuel_per_tick)
      # EnvironmentalEvent recording: storm_name list — derive from effect providers
      ...
  ```
- [ ] Drop `area_effect_manager` constructor arg.
- [ ] Update `EnvironmentalEvent` construction. Today's `EnvironmentalEvent` carries `storm_name` — derive from `[p['source_label'] for p in effects[i]['providers']]` joined or as a list. Keep API-compatible if possible.
- [ ] Run tests — green.

**Notes:** Use `empire_id=None` so storms (ownerless) are picked up; the empire-aware planet-scoped path doesn't need to apply here (storms damage everyone equally).

### Task 6.3: Migrate `spec_compiler` + `conflict_resolution_engine` [Complex]
**File:** `game/strategy/combat/spec_compiler.py`, `game/strategy/engine/conflict_resolution_engine.py`, `game/strategy/adapters/simulation_adapter.py`
**Tests:** `pytest tests/unit/strategy/combat/ tests/unit/strategy/conflict_resolution/ tests/unit/strategy/adapters/`, `tests/integration/strategy/combat/test_storm_shield_interference.py`

- [ ] Failing tests first:
  - [ ] `test_entries_from_sector_effects_emits_shield_modifier_per_provider` — two ion storms = two `ModifierEntry`s in the global stack, each with `multiplier=0.5`. (No shared stack_group; storms multiply.)
  - [ ] `test_entries_from_sector_effects_handles_facility_shieldmodifier` — the same code path works for facility-projected `ShieldModifier` (clean-sheet generality).
  - [ ] `test_combat_in_two_overlapping_ion_storms_applies_025x_shields` — integration test confirming the multiply behavior.
- [ ] Replace `_entries_from_environmental_effects` with `_entries_from_sector_effects(sector_effects: Sequence[dict]) -> List[ModifierEntry]`:
  ```python
  def _entries_from_sector_effects(sector_effects):
      entries = []
      for effect in sector_effects:
          ability = effect['ability_name']
          if ability not in {'ShieldModifier', 'DamageModifier', 'ThrustModifier'}:  # ThrustModifier wired in PROJ-300 per D14
              continue
          for provider in effect['providers']:
              if not provider['is_active']:
                  continue
              ad = provider['ability_data']
              mult = ad.get('multiplier', 1.0)
              if mult == 1.0:
                  continue
              team_entries = emit_entries_for_ability(
                  ability,
                  mult,
                  scope="self",
                  owner_team=0, num_teams=1,
                  source=f"sector:{provider['source_kind']}",
                  source_modifier_id=provider['source_id'],
                  source_modifier_name=provider['source_label'],
                  stack_group=ad.get('stack_group'),  # propagates from data; storms have None
              )
              entries.extend(entry for _, entry in team_entries)
      return entries
  ```
- [ ] In `build_strategy_battle_spec`: change parameter `environmental_effects: Any = None` → `sector_effects: Sequence[dict] = ()`.
- [ ] In `conflict_resolution_engine._lookup_environmental_effects` → rename to `_lookup_sector_effects(self, location)`:
  ```python
  def _lookup_sector_effects(self, location):
      system = self._galaxy.get_system_at_location(location)
      if system is None:
          return []
      return collect_sector_effects(system, location, empire_id=None, registries=self._registries)
  ```
- [ ] Update `simulation_adapter.resolve_battle` parameter `environmental_effects` → `sector_effects`.
- [ ] Run all combat/conflict-resolution tests — green.

**Notes:** Confirm `emit_entries_for_ability` accepts `stack_group=None` — if storms emit None and facilities emit a string, the combat aggregator treats Nones as ungrouped (multiply across them). This matches the user-decided MULTIPLY behavior.

### Task 6.4: Wire `ThrustModifier` combat consumption [Medium] *(added 2026-04-27, decisions.md D14)*
**Files:** `game/simulation/combat/ability_stat_registry.py`, the combat propulsion stat aggregator (Phase 1 audit identifies the exact site — likely in `game/simulation/entities/ship_combat_engine.py` or a propulsion-stats helper).
**Tests:** `tests/integration/strategy/combat/test_storm_thrust_modifier.py` (NEW)

- [ ] Failing tests first:
  - [ ] `test_single_storm_thrust_modifier_applies_in_combat` — ship in `gravitational_anomaly` (`ThrustModifier 0.6`) gets `effective_thrust = base_thrust * 0.6`.
  - [ ] `test_overlapping_thrust_modifiers_multiply` — two storms each with `ThrustModifier 0.6` → ship at hex gets `0.36 × thrust`.
  - [ ] `test_facility_projected_thrust_modifier` — a facility component with `ThrustModifier scope: enemy_sector` reduces enemy ship thrust at the hex.
  - [ ] `test_no_storms_no_thrust_change` — control: ship in clear hex has unmodified thrust.
- [ ] In `ABILITY_STAT_REGISTRY`, register `ThrustModifier` → `thrust_mult` so storm/facility-emitted entries flow into the combat stat stack.
- [ ] In the combat propulsion stat aggregator, multiply effective thrust by aggregated `thrust_mult` from external modifiers (symmetrical with `shield_capacity_mult` consumption today).
- [ ] Run tests — green.

**Notes:** This task closes out D14 (no more dead-data-flow). Treat `ThrustModifier` symmetrically with `ShieldModifier` for the rest of the project — wherever one is mentioned, the other should be too.

### Task 6.5: Storm-stacking balance regression test [Simple] *(added 2026-04-27, decisions.md D18)*
**File:** `tests/integration/strategy/test_overlapping_storm_combat.py` (NEW)

- [ ] Failing test first: `test_two_overlapping_ion_storms_apply_025x_shields_in_combat` — multiplicative stacking, NOT MAX.
- [ ] Failing test: `test_three_overlapping_ion_storms_apply_0125x_shields` — confirms the multiply scales correctly past two.
- [ ] Failing test: `test_single_ion_storm_applies_05x_shields` — single-storm baseline.
- [ ] Comment at top of file references decisions.md D6 + D18 documenting the deliberate behavior change from the legacy MAX behavior.
- [ ] Run — green.

**Notes:** Test exists explicitly to lock in the MAX→MULTIPLY change so a future contributor doesn't accidentally reintroduce shared `stack_group="storm_shield_interference"`.

---

## Phase Completion Checklist
- [ ] All tasks complete
- [ ] All consumer-related tests green
- [ ] No production code references `AreaEffectManager` or `EnvironmentalEffects` (verify with grep)
- [ ] **NOTE: `pytest tests/ --testmon` may still fail because the old `area_effect_manager.py` file still exists and may be importable but broken; Phase 7 cleans this up.**
- [ ] D14 ThrustModifier consumption tests green (Task 6.4).
- [ ] D18 storm-stacking balance regression test green (Task 6.5).
- [ ] Update status to `Complete`
- [ ] Update plan.md
