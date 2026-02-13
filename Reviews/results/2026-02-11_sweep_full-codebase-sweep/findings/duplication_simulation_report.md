# Sweep Report: Duplication & Fragmentation

**Scope:** `game/simulation/` (all subdirectories)
**Date:** 2026-02-11
**Files Analyzed:** 73 Python files
**Agent:** Sweep Agent - Duplication & Fragmentation

---

## Findings

---

### Phase 1: Structural Duplication

#### CRITICAL: Physics formula duplication between ShipPhysicsMixin and ShipStatsCalculator

`ShipPhysicsMixin.update_physics_movement()` recalculates acceleration and max_speed using the same K_THRUST/K_SPEED formulas already computed in `ShipStatsCalculator._phase_physics_and_limits()`. The runtime physics code re-derives values that should already be on the ship object.

**File A:** `game/simulation/entities/ship_physics.py` (lines 32-33)
```python
current_accel = (current_total_thrust * K_THRUST) / (self.mass * self.mass)
potential_max_speed = (current_total_thrust * K_SPEED) / self.mass
```

**File B:** `game/simulation/entities/ship_stats.py` (lines 228-232)
```python
ship.acceleration_rate = (ship.total_thrust * K_THRUST) / (ship.mass * ship.mass)
ship.max_speed = (ship.total_thrust * K_SPEED) / ship.mass if ship.total_thrust > 0 else 0
```

**Risk:** If the physics formulas are updated in one location but not the other, ships will behave differently in real-time combat (physics mixin) vs design-time stat display (stats calculator). The divergence in denominator handling (no zero-guard in physics mixin) is already a latent bug.

**Recommendation:** Extract the formula into a shared utility function in `physics_constants.py` (which already documents them). Both call sites should delegate to the same function.

---

#### MAJOR: Hull auto-equip code duplicated between Ship.__init__ and Ship.change_class

The hull component creation and attachment logic is copy-pasted between two locations in `ship.py`.

**Location A:** `game/simulation/entities/ship.py` (lines 70-80, `__init__`)
```python
default_hull_id = class_def.get('default_hull_id')
if default_hull_id:
    hull_component = create_component(default_hull_id, registries=self._registries)
    if hull_component:
        self.layers[LayerType.HULL].components.append(hull_component)
        hull_component.layer_assigned = LayerType.HULL
        hull_component.ship = self
```

**Location B:** `game/simulation/entities/ship.py` (lines 437-445, `change_class`)
```python
default_hull_id = class_def.get('default_hull_id')
if default_hull_id:
    hull_component = create_component(default_hull_id, registries=self._registries)
    if hull_component:
        self.layers[LayerType.HULL].components.append(hull_component)
        hull_component.layer_assigned = LayerType.HULL
        hull_component.ship = self
```

**Risk:** If hull initialization logic changes (e.g., adding validation, logging, or additional setup), it must be updated in two places. The `__init__` version has an `else` branch with `log_warning` that the `change_class` version lacks -- evidence of drift already occurring.

**Recommendation:** Extract to a private `_equip_default_hull(class_def)` method.

---

#### MAJOR: Modifier application duplicated between add_component and add_components_bulk

Both methods in `Ship` contain identical modifier service instantiation and mandatory modifier application logic.

**Location A:** `game/simulation/entities/ship.py` (lines 489-494, `add_component`)
```python
from game.simulation.services.modifier_service import ModifierService
service = ModifierService(modifier_registry=self._registries.modifiers)
service.ensure_mandatory_modifiers(component)
```

**Location B:** `game/simulation/entities/ship.py` (lines 534-539, `add_components_bulk`)
```python
from game.simulation.services.modifier_service import ModifierService
service = ModifierService(modifier_registry=self._registries.modifiers)
service.ensure_mandatory_modifiers(new_comp)
```

**Risk:** The late import and service creation is identical. Changes to modifier application (e.g., adding logging, changing the DI pattern, or adding post-processing) must be done in both places.

**Recommendation:** Extract to a private `_apply_mandatory_modifiers(component)` method.

---

#### MAJOR: Superweapon ability classes are nearly identical boilerplate

Six classes in `superweapons.py` (DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct) are structurally identical. Each is ~25 lines with the same class attributes, `__init__`, `get_ui_rows`, and `get_primary_value`. The only difference is the UI label string.

**File:** `game/simulation/components/abilities/superweapons.py` (lines 23-196)

**Pattern repeated 6 times:**
```python
class Xxx(Ability):
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF]
    default_scope = AbilityScope.SELF
    STAT_BINDINGS = []
    def __init__(self, component, data):
        super().__init__(component, data)
    def get_ui_rows(self):
        return [{'label': 'Superweapon', 'value': '<ONLY DIFFERENCE>', 'color_hint': '#FF4444'}]
    def get_primary_value(self):
        return 0.0
```

**Risk:** Low functional risk since these are marker classes, but any change to the superweapon pattern (e.g., adding a cost, adding an execution method) requires editing 6 identical classes.

**Recommendation:** Create a single `SuperweaponAbility` base class with a configurable `display_name` attribute, then derive each concrete class as a one-line subclass or use a factory/registry pattern.

---

#### MAJOR: Turret arc lookup logic duplicated in ModifierService

The arc lookup logic for `turret_mount` is copy-pasted between `get_initial_value` and `get_local_min_max`.

**Location A:** `game/simulation/services/modifier_service.py` (lines 165-176, `get_initial_value`)
```python
base_arc = component.data.get('firing_arc')
if base_arc is None:
    abilities = component.data.get('abilities', {})
    for ab_name in ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility']:
        ab_data = abilities.get(ab_name, {})
        if isinstance(ab_data, dict) and 'firing_arc' in ab_data:
            base_arc = ab_data['firing_arc']
            break
```

**Location B:** `game/simulation/services/modifier_service.py` (lines 219-227, `get_local_min_max`)
```python
base_arc = component.data.get('firing_arc')
if base_arc is None:
    abilities = component.data.get('abilities', {})
    for ab_name in ['ProjectileWeaponAbility', 'BeamWeaponAbility', 'SeekerWeaponAbility', 'WeaponAbility']:
        ab_data = abilities.get(ab_name, {})
        if isinstance(ab_data, dict) and 'firing_arc' in ab_data:
            base_arc = ab_data['firing_arc']
            break
```

**Risk:** If a new weapon ability type is added, both lookup lists must be updated. The fallback value differs between locations (`mod_def.min_val` vs `local_min`), which could cause subtle inconsistencies.

**Recommendation:** Extract to a private `_get_base_firing_arc(component)` method.

---

#### MAJOR: BeamWeaponAbility.get_damage() duplicates WeaponAbility.get_damage()

`BeamWeaponAbility` overrides `get_damage()` with an identical implementation to its parent class `WeaponAbility`.

**Parent:** `game/simulation/components/abilities/weapons.py` (lines 195-212)
```python
def get_damage(self, range_to_target: float = 0) -> float:
    if self.damage_formula:
        from game.simulation.formula_system import safe_evaluate_math_formula
        context = {'range_to_target': range_to_target}
        return max(0.0, safe_evaluate_math_formula(self.damage_formula, context))
    return self.damage
```

**Override:** `game/simulation/components/abilities/weapons.py` (lines 315-321)
```python
def get_damage(self, range_to_target: float = 0) -> float:
    if self.damage_formula:
        from game.simulation.formula_system import safe_evaluate_math_formula
        context = {'range_to_target': range_to_target}
        return max(0.0, safe_evaluate_math_formula(self.damage_formula, context))
    return self.damage
```

**Risk:** Maintenance burden -- any update to the damage formula evaluation must be done in both places. If only one is updated, beam weapons will behave differently from projectile/seeker weapons.

**Recommendation:** Delete `BeamWeaponAbility.get_damage()` entirely; the inherited method is identical.

---

#### MINOR: Ability constructor data-extraction pattern repeated 10+ times

Many ability constructors use the identical pattern to handle both primitive and dict data:

```python
val = data if isinstance(data, (int, float)) else data.get('value', 0)
```

This exact line appears in: CombatPropulsion, ManeuveringThruster, StrategicMovement, ShieldProjection, ShieldRegeneration, ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor, CrewCapacity, LifeSupportCapacity, CrewRequired.

**Files:** `game/simulation/components/abilities/propulsion.py`, `defense.py`, `crew.py`, `resources.py`

**Risk:** Low -- the pattern is simple enough that drift is unlikely. But it adds noise and could be centralized.

**Recommendation:** Add a `_extract_value(data, key='value', default=0)` utility method to the `Ability` base class.

---

#### MINOR: Propulsion sync_data methods are near-identical

`CombatPropulsion.sync_data`, `ManeuveringThruster.sync_data`, and `StrategicMovement.sync_data` follow the same pattern, differing only in attribute names (`base_thrust`/`thrust_force`, `base_turn_rate`/`turn_rate`, `base_movement_points`/`movement_points`).

**File:** `game/simulation/components/abilities/propulsion.py` (lines 21-25, 50-54, 97-101)

**Risk:** Low -- pattern is simple. But if sync logic changes (e.g., adding validation or events), three methods need updating.

**Recommendation:** Consider a template method in `Ability` base class that calls a hook for setting the specific attributes.

---

#### MINOR: ShipValidatorHelper calls validate_design three times independently

Three methods (`check_validity`, `get_validation_warnings`, `get_missing_requirements`) each independently call `get_or_create_validator().validate_design(self._ship)` with no result caching.

**File:** `game/simulation/entities/ship_validator_helper.py` (lines 43, 54, 63)

**Risk:** Performance waste (triple validation), and if called in sequence (which is likely for UI), the ship is validated three times.

**Recommendation:** Cache the validation result and invalidate on stat changes.

---

### Phase 2: Semantic Duplication

#### CRITICAL: Two parallel ability aggregation systems

There are two different systems for aggregating ability values from ship components, serving overlapping purposes:

**System A:** `calculate_ability_totals()` in `ability_aggregator.py` -- Full two-phase aggregation with stacking group support (MAX within group, SUM/MULTIPLY across groups). Used by `ShipStatsCalculator` for design-time stats.

**System B:** `get_total_ability_value()` in `ship_stat_querier.py` (lines 55-78) -- Simple linear iteration that sums `get_primary_value()` from all matching abilities. Used by `ShipPhysicsMixin.update_physics_movement()` for runtime thrust calculation.

```python
# System B (ShipStatQuerier)
total = 0.0
for comp in self._ship.get_all_components():
    if operational_only and not comp.is_operational:
        continue
    for ab in comp.get_abilities(ability_name):
        total += ab.get_primary_value()
return total
```

**Risk:** HIGH. System B ignores stacking groups entirely. If two CombatPropulsion abilities share a stack_group, System A would take MAX within the group (correct), while System B would SUM them (incorrect). This means ships may have different thrust during design preview vs runtime combat.

**Recommendation:** Unify into a single aggregation path. `get_total_ability_value` should delegate to `calculate_ability_totals` (or a shared core) and add the `operational_only` filter as a parameter.

---

#### MAJOR: Two independent formula evaluation systems

The codebase has two separate formula evaluators with overlapping functionality:

**System A:** `formula_system.py` -- General-purpose formula evaluator with `evaluate_math_formula()`. Has full security validation (`DANGEROUS_NAMES`), AST validation, and comprehensive math builtins.

**System B:** `modifier_effects.py` `ModifierEffectEvaluator.evaluate_formula()` -- Modifier-specific formula evaluator. Has a smaller allowed-name set, no security validation, and only basic math functions.

Both use `eval()` with `{"__builtins__": {}}`, both replace `^` with `**`, and both raise `FormulaException`. But their allowed function sets differ, their error handling differs, and their validation approaches differ.

**Risk:** Security inconsistency -- `formula_system.py` explicitly blocks dangerous names while `modifier_effects.py` does not. Capability inconsistency -- formulas that work in one system may fail in the other.

**Recommendation:** Have `ModifierEffectEvaluator.evaluate_formula()` delegate to `evaluate_math_formula()` from `formula_system.py`, passing modifier-specific context.

---

#### MAJOR: Duplicate default stats dictionaries

Two independent sources of truth for default modifier stat values:

**Source A:** `modifiers.py` `get_default_stat_multipliers()` (lines 120-156) -- Returns a dict with all stat keys and their defaults.

**Source B:** `stat_keys.py` `StatKey.create_default_stats_dict()` (lines 86-97) -- Constructs a dict from the StatKey enum with the same defaults.

Both produce the same logical output but via different mechanisms. Any new stat key must be added to both.

**Risk:** If a stat key is added to one but not the other, modifier application will silently use incorrect defaults for that stat.

**Recommendation:** Have `get_default_stat_multipliers()` delegate to `StatKey.create_default_stats_dict()`, or vice versa.

---

#### MINOR: get_total_sensor_score and get_total_ecm_score are near-identical

Both methods in `ShipStatQuerier` (lines 80-106) follow the exact same pattern, differing only in the ability name string (`'ToHitAttackModifier'` vs `'ToHitDefenseModifier'`):

```python
def get_total_sensor_score(self) -> float:
    result = self.get_ability_total('ToHitAttackModifier')
    return float(result) if isinstance(result, (int, float)) else 0.0

def get_total_ecm_score(self) -> float:
    result = self.get_ability_total('ToHitDefenseModifier')
    return float(result) if isinstance(result, (int, float)) else 0.0
```

**Risk:** Minimal, but if the return-type normalization logic changes, both must be updated.

**Recommendation:** Extract to a private `_get_score(ability_name)` method.

---

### Phase 3: Copy-Paste Drift

#### MAJOR: WeaponAbility.__init__ formula parsing repeated three times for damage/range/reload

Three near-identical blocks parse potential formula strings for damage, range, and reload. Each block: (1) extracts raw value from data or component fallback, (2) checks for '=' prefix, (3) evaluates formula or converts to float, (4) stores base value.

**File:** `game/simulation/components/abilities/weapons.py` (lines 50-97)

```python
# Block 1 (damage): lines 50-67
raw_damage = data.get('damage', 0)
if isinstance(raw_damage, str) and raw_damage.startswith('='):
    self.damage_formula = raw_damage[1:]
    self.damage = float(max(0, safe_evaluate_math_formula(...)))
else:
    self.damage_formula = None
    self.damage = float(raw_damage)
self._base_damage = self.damage

# Block 2 (range): lines 69-82 -- identical structure
# Block 3 (reload): lines 84-97 -- identical structure
```

The same triple-repetition occurs in `sync_data()` (lines 126-149).

**Drift observed:** The damage block stores `damage_formula` as an instance variable; the range and reload blocks do not store their formulas (they are evaluated and discarded). This means runtime formula re-evaluation only works for damage, not for range or reload.

**Risk:** If formula support is needed for range/reload at runtime (e.g., range varies with speed), only damage has the infrastructure. The inconsistency is a latent bug if the design intent is uniform formula support.

**Recommendation:** Extract a `_parse_stat(data, key, default, store_formula=False)` helper that returns `(value, base_value, formula)`.

---

#### MAJOR: Missile type checking uses inconsistent dual patterns

Throughout the codebase, missile type checking uses both enum and string comparison simultaneously:

**File:** `game/simulation/entities/projectile.py` (lines 87, 95, 106)
```python
if self.type == AttackType.MISSILE or self.type == 'missile':
```

**File:** `game/simulation/projectile_manager.py` (line 150)
```python
is_missile = (p.type == AttackType.MISSILE) or (p.type == 'missile')
```

This dual check appears 4 times across 2 files. The `Projectile.__init__` already normalizes string types to `AttackType` enum (lines 42-49), so the string fallback should be unnecessary.

**Risk:** If the normalization in `__init__` is ever bypassed (e.g., direct attribute assignment), the string fallback silently masks the bug. If it works correctly, the string check is dead code noise.

**Recommendation:** Remove the string comparison fallbacks. If normalization is reliable, only `AttackType.MISSILE` is needed.

---

#### MINOR: Resource endurance calculations in combat_endurance.py follow identical pattern

Fuel, ammo, and energy endurance calculations in `calculate_combat_endurance()` follow the same pattern with minor variations:

```python
# Fuel (line 106):
ship.fuel_endurance = (max_fuel / effective_fuel) if effective_fuel > 0 else float('inf')

# Ammo (line 109):
ship.ammo_endurance = (max_ammo / ammo_consumption) if ammo_consumption > 0 else float('inf')

# Energy (lines 119-125):
if ship.energy_net < 0:
    ship.energy_endurance = max_energy / abs(ship.energy_net)
else:
    ship.energy_endurance = float('inf')
```

**Drift observed:** Fuel uses `effective_fuel` (fallback to potential), ammo uses raw `ammo_consumption` (no fallback), and energy uses net rate (generation minus consumption). The three calculations are subtly different in a way that may or may not be intentional.

**Risk:** The inconsistency makes it hard to know if the differences are by design (energy is special because it regenerates) or by accident (ammo should also fall back to potential).

**Recommendation:** Document the intentional differences explicitly. Consider a helper function with a `use_fallback` parameter.

---

#### MINOR: apply_modifier_effects partially duplicates _apply_effect_to_dict

`modifiers.py` has a helper function `_apply_effect_to_dict` (lines 15-48) for applying effects to a plain dict. But `apply_modifier_effects` (lines 51-117) re-implements the same operation/stat logic with additional special-case handling for `mass_add`, `arc_add`, `accuracy_add`, `projectile_stealth_level`, `arc_set`, and `facing_angle`.

**File:** `game/simulation/components/modifiers.py`

**Risk:** Updates to operation semantics in `_apply_effect_to_dict` won't automatically apply to the special cases in `apply_modifier_effects`.

**Recommendation:** Refactor `apply_modifier_effects` to delegate to `_apply_effect_to_dict` for the non-targeted, non-special-case path.

---

### Phase 4: Fragmented Implementations

#### MAJOR: Ship stat recalculation scattered across 5 files

The full ship stats calculation pipeline involves:

1. `ship.py` `recalculate_stats()` -- Entry point facade, delegates to calculator
2. `ship_stats.py` `ShipStatsCalculator.calculate()` -- 5-phase pipeline orchestrator
3. `ability_aggregator.py` `calculate_ability_totals()` -- Ability value aggregation
4. `combat_endurance.py` `calculate_combat_endurance()` -- Endurance and DPS calculation
5. `ship_physics.py` `ShipPhysicsMixin.update_physics_movement()` -- Runtime re-derivation of physics stats

The PhysicsBody data flows through all five files, and understanding what stats a ship has requires tracing through all of them. The runtime physics mixin (file 5) re-derives values that file 2 already computed, creating the critical duplication noted in Phase 1.

**Risk:** Modifying any physics formula or stat aggregation requires understanding the full 5-file pipeline. New contributors will not realize that `ship_physics.py` re-derives stats that `ship_stats.py` already set.

**Recommendation:** Document the stat pipeline flow clearly. Eliminate the runtime re-derivation in `ship_physics.py` by using the pre-calculated stats from `ship_stats.py` (with an `operational_only` variant for damaged engines).

---

#### MAJOR: Component data loading spread across 4 files with repeated path resolution

Component and modifier loading logic is split across:

1. `component.py` `load_components_data()` -- Pure function loading component JSON
2. `component.py` `load_modifiers_data()` -- Pure function loading modifier JSON
3. `ship_loader.py` `load_vehicle_classes_data()` -- Pure function loading vehicle class JSON
4. `services/registry_loader.py` -- Orchestrates loading all registries

All three loading functions (1, 2, 3) contain similar file-path resolution patterns:
```python
if not os.path.exists(file_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    abs_path = os.path.join(base_dir, file_path)
    if os.path.exists(abs_path):
        file_path = abs_path
```

**Risk:** If path resolution logic changes (e.g., adding search paths or environment variable support), three functions need updating.

**Recommendation:** Extract the path resolution pattern to a utility in `game/core/paths.py`.

---

#### MINOR: Validation result handling duplicated between validate_addition and validate_design

`ShipDesignValidator` has two methods that follow the same pattern of iterating rules and accumulating results:

**File:** `game/simulation/validation/ship_validator.py` (lines 427-447)

```python
# validate_addition (lines 427-435)
for rule in self.addition_rules:
    res = rule.validate(ship, component, layer_type)
    if not res.is_valid:
        final_result.is_valid = False
        final_result.errors.extend(res.errors)

# validate_design (lines 437-446)
for rule in self.design_rules:
    res = rule.validate(ship)
    if not res.is_valid:
        final_result.is_valid = False
        final_result.errors.extend(res.errors)
    final_result.warnings.extend(res.warnings)
```

**Drift observed:** `validate_addition` does not accumulate warnings, but `validate_design` does. This may be intentional (addition validation doesn't generate warnings) or an omission.

**Risk:** Low -- the methods are short and in the same class. But the warning handling inconsistency should be documented.

---

#### INFO: Persistence layer uses old Ship.from_dict pattern without registries

`ShipIO.load_ship()` in `systems/persistence.py` calls `Ship.from_dict(data)` without passing registries. The current `Ship.from_dict` is a class method that internally uses `RegistryManager`, so this works. But it bypasses the strict DI pattern used everywhere else.

**File:** `game/simulation/systems/persistence.py` (line 92)

**Risk:** If `from_dict` is changed to require explicit registries (which PROJ-50 has done for `ShipSerializer.from_dict`), this call site will break.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 2     |
| MAJOR    | 9     |
| MINOR    | 7     |
| INFO     | 1     |
| **Total**| **19**|

---

## Top 5 Priority Issues

1. **Two parallel ability aggregation systems** (CRITICAL, Phase 2) -- `calculate_ability_totals` vs `get_total_ability_value` produce different results for abilities with stacking groups. This can cause ships to have different stats in design preview vs runtime combat. Fix: unify into a single aggregation path with an `operational_only` parameter.

2. **Physics formula duplication** (CRITICAL, Phase 1) -- `ship_physics.py` re-derives acceleration and max_speed from raw formulas instead of using pre-calculated values from `ship_stats.py`. This creates two sources of truth for the same calculation with divergent zero-guard handling. Fix: extract formulas to shared utility in `physics_constants.py`.

3. **Two independent formula evaluation systems** (MAJOR, Phase 2) -- `formula_system.py` and `modifier_effects.py` have parallel eval-based formula evaluators with different security postures and different allowed function sets. Fix: consolidate `ModifierEffectEvaluator.evaluate_formula()` to delegate to `evaluate_math_formula()`.

4. **Weapon formula parsing triple-repetition with drift** (MAJOR, Phase 3) -- `WeaponAbility.__init__` parses damage/range/reload with three nearly identical blocks, but only damage stores its formula for runtime re-evaluation. Fix: extract to a helper that uniformly handles all three stats.

5. **Hull auto-equip and modifier application duplication in Ship** (MAJOR, Phase 1) -- Two instances of hull auto-equip code (init vs change_class) and two instances of modifier application code (add_component vs add_components_bulk) with evidence of drift. Fix: extract to private helper methods.
