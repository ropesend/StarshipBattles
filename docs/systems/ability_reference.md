# Ability Reference

> **Last verified:** 2026-05-16 - Verified against `game/simulation/components/abilities/`, strategic ability services, and the compact ability reference. Current live registry has 72 keys (PROJ-FMS-A added 11 new abilities — `Warhead`, `Laserhead`, `RamTarget`, `VehicleBay`, and the six launch + two recovery skeletons; PROJ-FMS-C audit Fix 1 removed `VehicleLaunch`; QA Observation 5 renamed `CrewRequired` to `RequiresMaintenance` and added `ProvidesMaintenance`).

Compact agent reference for the component ability system. It preserves live registry keys, data shapes, contracts, invariants, extension recipes, warnings, stale-reference corrections, and validation commands while omitting release-note history.

---

## Agent Essentials

- Runtime registry: `game/simulation/components/abilities/__init__.py::ABILITY_REGISTRY`.
- Factory: `create_ability(name, component, data) -> Ability | None`.
- Default-scope helper: `get_ability_default_scope(ability_name) -> str`; compilers and collectors must call this instead of assuming `"self"`.
- Base classes and enums: `game/simulation/components/abilities/base.py`.
- Modifier stat contract: `game/simulation/components/abilities/stat_keys.py`.
- Ability-to-external-stat bridge: `game/simulation/combat/ability_stat_registry.py`.
- Ship-stat extension point: `game/simulation/entities/stat_contributors/registry.py`.
- Strategic source/effect pipeline: `game/strategy/services/ability_iterator.py`, `system_effects_collector.py`, `effect_ability_metadata.py`.
- Design/facility ability inspection must use `game/strategy/services/component_inspector.py`; loaded designs usually store component IDs, with abilities resolved through the component registry.
- Current stale-reference corrections: old counts such as 39, 53, 56, or 60 are obsolete; `PodStorage`, `VehicleStorage`, and `MultiplexTracking` are typed marker abilities, not raw-dict stat reads.
- `PlanetaryShield` and `StrategicResourceGeneration` still inherit the base combat-layer class metadata in live code, but gameplay consumes them as strategic component abilities.

## JSON Data Shapes

Ability data lives under each component's `abilities` mapping in `data/components.json`.

| Shape | Example | Contract |
|---|---|---|
| Boolean marker | `"CommandAndControl": true` | Presence matters; value often ignored. |
| Scalar | `"CombatPropulsion": 1000` | Parsed as the primary numeric value. |
| Dict | `"WarpJump": {"max_tonnage": 5000}` | Preferred shape for named fields, `scope`, `tags`, and `stack_group`. |
| List | `"ResourceConsumption": [{"resource": "fuel", "amount": 1}]` | `AbilityManager` creates/syncs one ability instance per list item. |
| Runtime formula | `"damage": "=20 * (1 - 0.00005 * range_to_target)"` | Weapons only; evaluated with `range_to_target` during combat. |
| Load-time formula | `"max_tonnage": "=ship_class_mass"` | Evaluated during component recalculation with ship context. |

`create_ability` returns `None` for unknown keys. If construction fails because data still contains formula strings that need ship context, it skips silently so the ability can be instantiated after formulas resolve. Other malformed data logs a warning.

## Core APIs And Invariants

### Ability Base Contract

File: `game/simulation/components/abilities/base.py`

```python
layer: AbilityLayer = AbilityLayer.COMBAT
allowed_scopes: list[AbilityScope] = [AbilityScope.SELF]
default_scope: AbilityScope = AbilityScope.SELF
STAT_BINDINGS: list[AbilityStatBinding] = []
```

Instance behavior:

- `scope` comes from dict data `scope`, otherwise from `default_scope`.
- Invalid scope names or unsupported scopes raise `ValidationException`.
- `tags` and `stack_group` are parsed from dict data.
- `sync_data(data)` updates raw data, tags, stack group, scope, and re-runs `_parse_attrs(data)`.
- `get_effective_stat(stat_key, default=...)` composes ability-local `component.ability_stats[class_name]`, component-wide `component.stats`, and read-only `ship.external_stats`.
- `*_mult` values multiply, `*_add` values add, and unknown key shapes prefer the external value when both local and external are present.
- `get_primary_value()` is the numeric value aggregators consume. Marker abilities generally return `0.0` or `1.0`.
- `get_ui_rows()` returns capability scanner/detail-panel rows.

### Formula-Driven Data

Any ability that parses numeric or string fields from `data` must parse them in `_parse_attrs(data)`, not only in `__init__`. The base class calls `_parse_attrs` from both construction and `sync_data`, so formulas re-evaluate correctly when a component is attached to a ship or receives a new ship-class context.

Current production formulas in `data/components.json`:

| Component | Ability | Field | Formula Type |
|---|---|---|---|
| `laser_cannon` | `BeamWeaponAbility` | `damage = "=20 * (1 - 0.00005 * range_to_target)"` | runtime weapon formula |
| `warp_drive` | `WarpJump` | `max_tonnage = "=ship_class_mass"` | load-time ship-class formula |
| `warp_drive` | `ResourceConsumption` | `[0].amount = "=5 * (ship_class_mass ** (2/3))"` | load-time ship-class formula |
| `bridge` | `RequiresMaintenance` | `=ceil(sqrt(ship_class_mass / 1000))` | load-time ship-class formula |
| `central_complex_command` | `RequiresMaintenance` | `=ceil(sqrt(ship_class_mass / 1000))` | load-time ship-class formula |
| `emissive_armor` | `EmissiveArmor` | `value = "=8 * (ship_class_mass / 1000)**(1/3)"` | load-time ship-class formula |
| `shield_regenerating_armor` | `ShieldRegeneratingArmor` | `value = "=5 * (ship_class_mass / 1000)**(1/3)"` | load-time ship-class formula |

Formula warnings:

- Do not silently substitute a default for `ship_class_mass`; unresolved formulas must fail or wait for ship context.
- Attach a component to its ship before adding modifiers or forcing recalculation when the component data references `ship_class_mass`.
- `Component.clone()` preserves `self.ship` when cloning an attached component; palette/template clones remain detached and need a ship assigned before recalculation.
- Weapon damage formulas use `FormulaEvaluator.safe_evaluate` with `range_to_target`; static weapon stats still use normal stat bindings.

### AbilityManager

File: `game/simulation/components/ability_manager.py`

- Owns ability instances and an MRO-based lookup index.
- `instantiate_and_index()` preserves existing instances when possible and calls `sync_data` to keep cooldown/stateful abilities alive while refreshing data-derived fields.
- `get_ability("WeaponAbility")` and `get_abilities("WeaponAbility")` work polymorphically for `ProjectileWeaponAbility`, `BeamWeaponAbility`, and `SeekerWeaponAbility`.
- `has_ability_with_tag("pdc")` is the tag-driven PDC check; avoid hardcoded PDC class-name branches.

### Stacking

Numeric strategic effects use two-phase aggregation:

1. Same `stack_group`: reduce providers with MAX.
2. Different groups: combine groups by effect kind.

Combination rules:

- Rates such as `EnvironmentalDamage` sum across groups.
- Multipliers such as `ShieldModifier`, `DamageModifier`, and `StrategicSpeedModifier` multiply across groups.
- Flat shield bonuses from `ShieldProjection` add across groups.
- Missing `stack_group` makes each provider its own unique group, so those providers combine at phase 2.

Validation areas: `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`, `tests/unit/strategy/services/test_combat_modifier_collector.py`, and `tests/unit/strategy/services/test_effect_ability_metadata.py`.

### Scopes

Enum: `AbilityScope` in `game/simulation/components/abilities/base.py`.

| Scope | Meaning |
|---|---|
| `self` | Owner entity only. |
| `fleet` | Same battle group/fleet. |
| `sector` | One galaxy hex. |
| `allied_sector` | Owner plus allies in one hex. |
| `player_sector` | Owner only in one hex. |
| `enemy_sector` | Non-owner entities in one hex. |
| `system` | Whole star system. |
| `allied_system` | Owner plus allies in the star system. |
| `player_system` | Owner only in the star system. |
| `enemy_system` | Non-owner entities in the star system. |
| `planet` | Planet-wide. |
| `empire` | Owning empire colonies. |
| `allied_empire` | Owning empire plus allies. |

Spatial precision matters: a star system is the radius-50 region around a star; a sector is one `HexCoord`. Orders and validators that target a planet, warp point, fleet, or local effect must validate sector precision when the target is sector-specific.

Owner-aware scopes (`allied_*`, `player_*`, `enemy_*`, `allied_empire`) require a source with `owner_id`. Ownerless sources such as storms, stars, planets, warp points, and system archetypes should use neutral `sector` or `system` scope. The collector skips and logs ownerless sources that declare owner-aware scopes.

## Stat Keys

File: `game/simulation/components/abilities/stat_keys.py`

`AbilityStatBinding(stat_key, attribute_name, operation, base_attribute=None)` supports `multiply`, `add`, and `set`. `base_attribute` defaults to `"_base_{attribute_name}"`.

Multiplicative default `1.0`:

`mass_mult`, `hp_mult`, `damage_mult`, `range_mult`, `cost_mult`, `thrust_mult`, `turn_mult`, `strategic_mult`, `energy_gen_mult`, `capacity_mult`, `shield_capacity_mult`, `crew_capacity_mult`, `life_support_capacity_mult`, `consumption_mult`, `reload_mult`, `endurance_mult`, `projectile_hp_mult`, `projectile_damage_mult`, `crew_req_mult`.

Additive default `0.0`:

`mass_add`, `arc_add`, `accuracy_add`, `projectile_stealth_level`, `shield_bonus_add`.

Set/override default `None`:

`arc_set`.

`shield_bonus_add` is ship-level, not per-ability. It is read by `game/simulation/entities/ship_stats.py` and applied once per ship before external `shield_capacity_mult` scaling.

## Strategic Effect Bridges

### Ability To External Stat Registry

File: `game/simulation/combat/ability_stat_registry.py`

| Ability | External Stat Key | Operation | Value Field |
|---|---|---|---|
| `ShieldProjection` | `shield_bonus_add` | add | `value` |
| `ShieldModifier` | `shield_capacity_mult` | multiply | `multiplier` |
| `DamageModifier` | `damage_mult` | multiply | `multiplier` |
| `ThrustModifier` | `thrust_mult` | multiply | `multiplier` |

`emit_entries_for_ability(...)` returns `(team_id, ModifierEntry)` pairs. `enemy_sector` and `enemy_system` fan out to all non-owner teams; other scopes route to the owner team. Callers should import `OPPONENT_SCOPES` rather than reimplementing enemy-scope routing.

Known external stat keys consumed downstream:

`shield_bonus_add`, `shield_capacity_mult`, `damage_mult`, `thrust_mult`, `turn_mult`, `strategic_mult`, `capacity_mult`, `energy_gen_mult`, `crew_capacity_mult`, `life_support_capacity_mult`.

### Strategic Effect Metadata

File: `game/strategy/services/effect_ability_metadata.py`

This is the current metadata registry for strategic effects. Older references to module-level `SYSTEM_EFFECT_ABILITIES`, `_RATE_ABILITIES`, or collector-local hardcoded lists are stale.

| Ability | Kind | Grouping Field | Activation |
|---|---|---|---|
| `GeologicStabilizer` | multiplier | none | activatable |
| `StellarStabilizer` | multiplier | none | activatable |
| `WarpFieldStabilizer` | multiplier | none | activatable |
| `ResourceHarvestBooster` | multiplier | `resource_type` | passive |
| `QualityImprovement` | multiplier | `resource_type` | passive |
| `BuildRateBooster` | multiplier | none | passive |
| `ShieldModifier` | multiplier | none | per-entry activation fields allowed |
| `DamageModifier` | multiplier | none | per-entry activation fields allowed |
| `ThrustModifier` | multiplier | none | passive |
| `StrategicSpeedModifier` | multiplier | none | passive |
| `EnvironmentalDamage` | rate | `damage_type` | passive |
| `FuelDrain` | rate | none | passive |

Collectors:

- `collect_system_effects(system, empire_id, registries=None)` filters system scopes.
- `collect_sector_effects(system, hex_coord, empire_id, registries=None)` filters sector scopes.
- `aggregate_value_or(effects, ability_name, default, **filters)` reads the aggregate or returns the default.

## Ability Registry Quick Table

Live keys from `ABILITY_REGISTRY`.

| Key | Class | Source | Layer | Default Scope |
|---|---|---|---|---|
| `ColonizePlanet` | `ColonizePlanet` | `colonize.py` | strategic | `self` |
| `ResourceConsumption` | `ResourceConsumption` | `resources.py` | combat | `self` |
| `ResourceStorage` | `ResourceStorage` | `resources.py` | combat | `self` |
| `ResourceGeneration` | `ResourceGeneration` | `resources.py` | combat | `self` |
| `CombatPropulsion` | `CombatPropulsion` | `propulsion.py` | combat | `self` |
| `ManeuveringThruster` | `ManeuveringThruster` | `propulsion.py` | combat | `self` |
| `StrategicMovement` | `StrategicMovement` | `propulsion.py` | strategic | `self` |
| `WarpJump` | `WarpJump` | `propulsion.py` | strategic | `self` |
| `ShieldProjection` | `ShieldProjection` | `defense.py` | both | `self` |
| `ShieldRegeneration` | `ShieldRegeneration` | `defense.py` | combat | `self` |
| `MultiplexTracking` | `MultiplexTrackingAbility` | `markers.py` | combat | `self` |
| `VehicleStorage` | `VehicleStorageAbility` | `markers.py` | combat | `self` |
| `PodStorage` | `PodStorageAbility` | `markers.py` | combat | `self` |
| `WeaponAbility` | `WeaponAbility` | `weapons.py` | combat | `self` |
| `ProjectileWeaponAbility` | `ProjectileWeaponAbility` | `weapons.py` | combat | `self` |
| `BeamWeaponAbility` | `BeamWeaponAbility` | `weapons.py` | combat | `self` |
| `SeekerWeaponAbility` | `SeekerWeaponAbility` | `weapons.py` | combat | `self` |
| `CommandAndControl` | `CommandAndControl` | `markers.py` | combat | `self` |
| `CrewCapacity` | `CrewCapacity` | `crew.py` | combat | `self` |
| `LifeSupportCapacity` | `LifeSupportCapacity` | `crew.py` | combat | `self` |
| `RequiresMaintenance` | `RequiresMaintenance` | `crew.py` | combat | `self` |
| `ProvidesMaintenance` | `ProvidesMaintenance` | `crew.py` | combat | `self` |
| `ToHitAttackModifier` | `ToHitAttackModifier` | `defense.py` | combat | `self` |
| `ToHitDefenseModifier` | `ToHitDefenseModifier` | `defense.py` | combat | `self` |
| `EmissiveArmor` | `EmissiveArmor` | `defense.py` | combat | `self` |
| `ShieldRegeneratingArmor` | `ShieldRegeneratingArmor` | `defense.py` | combat | `self` |
| `Armor` | `Ability` lambda | `__init__.py` | combat marker | `self` |
| `RequiresCommandAndControl` | `RequiresCommandAndControl` | `markers.py` | combat | `self` |
| `RequiresCombatMovement` | `RequiresCombatMovement` | `markers.py` | combat | `self` |
| `StructuralIntegrity` | `StructuralIntegrity` | `markers.py` | combat | `self` |
| `ResourceHarvester` | `ResourceHarvesterAbility` | `harvester.py` | combat metadata; strategic use | `self` |
| `SpaceShipyard` | `SpaceShipyardAbility` | `harvester.py` | combat metadata; strategic use | `self` |
| `PlanetaryYard` | `PlanetaryYardAbility` | `harvester.py` | combat metadata; strategic use | `self` |
| `StagingYard` | `StagingYardAbility` | `harvester.py` | combat metadata; strategic use | `self` |
| `LocalStorage` | `LocalStorageAbility` | `harvester.py` | combat metadata; strategic use | `self` |
| `CargoStorage` | `CargoStorage` | `cargo.py` | strategic | `self` |
| `PlanetaryShield` | `PlanetaryShieldAbility` | `planetary.py` | combat metadata; strategic use | `self` |
| `StrategicResourceGeneration` | `StrategicResourceGenerationAbility` | `planetary.py` | combat metadata; strategic use | `self` |
| `GeologicStabilizer` | `GeologicStabilizerAbility` | `planetary.py` | strategic | `sector` |
| `StellarStabilizer` | `StellarStabilizerAbility` | `planetary.py` | strategic | `system` |
| `WarpFieldStabilizer` | `WarpFieldStabilizerAbility` | `planetary.py` | strategic | `system` |
| `ResourceHarvestBooster` | `ResourceHarvestBoosterAbility` | `planetary.py` | strategic | `planet` |
| `BuildRateBooster` | `BuildRateBoosterAbility` | `planetary.py` | strategic | `sector` |
| `AtmosphereModifier` | `AtmosphereModifierAbility` | `planetary.py` | strategic | `self` |
| `QualityImprovement` | `QualityImprovementAbility` | `planetary.py` | strategic | `self` |
| `ShieldModifier` | `ShieldModifierAbility` | `planetary.py` | strategic | `allied_system` |
| `DamageModifier` | `DamageModifierAbility` | `planetary.py` | strategic | `allied_system` |
| `GravityModifier` | `GravityModifierAbility` | `planetary.py` | strategic | `self` |
| `WaterModifier` | `WaterModifierAbility` | `planetary.py` | strategic | `self` |
| `RadiationShield` | `RadiationShieldAbility` | `planetary.py` | strategic | `self` |
| `ThrustModifier` | `ThrustModifierAbility` | `planetary.py` | strategic | `sector` |
| `StrategicSpeedModifier` | `StrategicSpeedModifierAbility` | `planetary.py` | strategic | `sector` |
| `EnvironmentalDamage` | `EnvironmentalDamageAbility` | `planetary.py` | strategic | `sector` |
| `FuelDrain` | `FuelDrainAbility` | `planetary.py` | strategic | `sector` |
| `DestroyPlanet` | `DestroyPlanet` | `superweapons.py` | strategic | `self` |
| `DestroyStar` | `DestroyStar` | `superweapons.py` | strategic | `self` |
| `OpenWarpPoint` | `OpenWarpPoint` | `superweapons.py` | strategic | `self` |
| `CloseWarpPoint` | `CloseWarpPoint` | `superweapons.py` | strategic | `self` |
| `CreateDysonSphere` | `CreateDysonSphere` | `superweapons.py` | strategic | `self` |
| `SelfDestruct` | `SelfDestruct` | `superweapons.py` | strategic | `self` |

## Ability Details By Family

### Weapons

Source: `game/simulation/components/abilities/weapons.py`.

| Key | Parameters | Stat Bindings | Notes |
|---|---|---|---|
| `WeaponAbility` | `damage` required, `range` required, `reload=1.0`, `firing_arc=360`, `facing_angle=0`, `tags=[]` | `damage_mult -> damage`, `range_mult -> range`, `reload_mult -> reload_time`, `arc_set -> firing_arc`, `arc_add -> firing_arc` | Base weapon; damage/range/reload can be formulas. |
| `ProjectileWeaponAbility` | weapon params plus `projectile_speed=500` | inherits weapon bindings | Unguided projectile. Runtime speed is scaled in firing logic. |
| `BeamWeaponAbility` | weapon params plus `accuracy_falloff=0.001`, `base_accuracy=1.0`, `pdc_valid_targets=["MISSILE", "FIGHTER"]` | inherits weapon bindings plus `accuracy_add -> base_accuracy` | Uses sigmoid hit chance; PDC behavior is tag/target metadata driven. |
| `SeekerWeaponAbility` | weapon params plus `projectile_speed=500`, `endurance=3.0`, `turn_rate=30.0`, `to_hit_defense=0.0`, `projectile_damage=damage`, `projectile_hp=1.0`, `projectile_stealth=0.0` | inherits weapon bindings plus `endurance_mult`, `projectile_damage_mult`, `projectile_hp_mult`, `projectile_stealth_level` | Guided missile; ignores firing arc. If range is absent, derives range from speed and endurance. |

Weapon family dispatch is registry-backed in `game/simulation/combat/weapon_registry.py` and `game/simulation/combat/families/`. Adding a new weapon family should add a family handler and metadata, not central branches in firing, targeting, collision, or projectile manager code.

### Defense And Hit Modifiers

Source: `game/simulation/components/abilities/defense.py`.

| Key | Parameters | Allowed Scopes | Stat Bindings | Notes |
|---|---|---|---|---|
| `ShieldProjection` | scalar or `value`; strategic variants may include `scope`, `energy_drain_rate=0`, `activation_time=0`, `deactivation_time=0` | `self`, `fleet`, `player_sector`, `allied_sector`, `player_system`, `allied_system` | `capacity_mult`, `shield_capacity_mult` both multiply capacity | Combat self shield capacity; strategic scoped flat shield bonus through external stats. |
| `ShieldRegeneration` | scalar or `value` | `self` | `energy_gen_mult -> rate` | Shield regen per second. |
| `ToHitAttackModifier` | scalar or `value`, optional `scope`, `stack_group` | `self`, `fleet`, `system`, `allied_system`, `empire` | none | Static attack score modifier. |
| `ToHitDefenseModifier` | scalar or `value`, optional `scope`, `stack_group` | `self`, `fleet`, `system`, `allied_system`, `empire` | none | Static defense/evasion score modifier. |
| `EmissiveArmor` | scalar or `value` | `self` | none | Integer flat damage ignored per hit. |
| `ShieldRegeneratingArmor` | scalar or `value` | `self` | none | Integer overflow absorption that recharges shields by absorbed amount. |
| `Armor` | any | marker | none | Dummy tag/existence ability. |

Damage pipeline order: shields, emissive armor, shield-regenerating armor, hull.

### Propulsion

Source: `game/simulation/components/abilities/propulsion.py`.

| Key | Parameters | Allowed Scopes | Stat Bindings | Notes |
|---|---|---|---|---|
| `CombatPropulsion` | scalar thrust | `self` | `thrust_mult -> thrust_force` | Tactical thrust. |
| `ManeuveringThruster` | scalar turn rate | `self` | `turn_mult -> turn_rate` | Tactical rotation. |
| `StrategicMovement` | scalar movement points | `self`, `allied_sector`, `allied_system` | `strategic_mult -> movement_points` | Strategy-map mobility; can be scoped as tug/tractor-style support. |
| `WarpJump` | scalar max tonnage, or dict `max_tonnage`, `energy_cost=0` | `self` | none | Warp-capable only when ship mass is within `max_tonnage` and storage can cover warp resource costs. |

Warp checks use `component_inspector.has_warp_capability(ship)` and calculated stats: `mass`, `warp_max_tonnage`, `warp_resource_costs`, `resource_storage`.

### Resources

Source: `game/simulation/components/abilities/resources.py`.

| Key | Parameters | Stat Bindings | Notes |
|---|---|---|---|
| `ResourceConsumption` | `resource`, `amount`, `trigger="constant"`; triggers include `constant`, `activation`, `strategic_per_hex` | `consumption_mult -> amount` | Constant consumption is per second in combat; strategic trigger exposes per-hex cost. |
| `ResourceStorage` | `resource`, `amount` | `capacity_mult -> max_amount` | Adds storage capacity for the resource. |
| `ResourceGeneration` | `resource`, `amount` | `energy_gen_mult -> rate` | Combat per-second generation. |

### Crew, Cargo, Launch, And Markers

Sources: `crew.py`, `cargo.py`, `markers.py`.

| Key | Parameters | Stat Bindings | Notes |
|---|---|---|---|
| `CrewCapacity` | scalar amount or `value` | `crew_capacity_mult -> amount` | Integer crew capacity. |
| `LifeSupportCapacity` | scalar amount or `value` | `life_support_capacity_mult -> amount` | Integer supported crew. |
| `RequiresMaintenance` | scalar amount or `value`/`amount` | `crew_req_mult -> amount` | Per-component maintenance demand (renamed from `CrewRequired` in the QA Observation 5 maintenance abstraction). Also scales by `sqrt(mass_mult)` internally; `mass_mult` is intentionally not a `STAT_BINDINGS` entry. |
| `ProvidesMaintenance` | scalar amount or `value` | `crew_capacity_mult -> amount` | Ship-level maintenance supply. Crew quarters declare it alongside `CrewCapacity`; automated maintenance units declare it standalone. Validator rejects designs where `RequiresMaintenance` total exceeds `ProvidesMaintenance` total. |
| `CargoStorage` | scalar capacity, or dict `cargo_type="generic"`, `capacity` | `capacity_mult -> capacity` | Strategic cargo; `passengers` is used for population transport. |
| `VehicleStorage` | scalar capacity, or dict `capacity` | none | Adds fighter storage capacity. |
| `PodStorage` | scalar mass, or dict `capacity_mass` | none | Adds pod mass capacity; single attribute only. |
| `MultiplexTracking` | scalar slots, or dict `slots` | none | Adds max target slots. |
| `CommandAndControl` | marker | none | Provides command capability and highest crew priority. |
| `RequiresCommandAndControl` | marker | none | Component is non-operational unless another active C&C component exists. |
| `RequiresCombatMovement` | marker | none | Component requires combat propulsion. |
| `StructuralIntegrity` | marker | none | Hull structural marker. |

Crew priority defaults in `CREW_PRIORITY_REGISTRY`: `CommandAndControl=0`, `CombatPropulsion=1`, `ManeuveringThruster=1`, `WeaponAbility=2`, fallback `3`.

### Colonization

Source: `game/simulation/components/abilities/colonize.py`.

`ColonizePlanet` is a strategic self-scope ability. Data is string shorthand such as `"ICE_DWARF"` or dict fields `planet_type` and `action_time=1`. It enables the colonization order flow for matching planet types.

### Harvester, Storage, And Construction

Source: `game/simulation/components/abilities/harvester.py`.

| Key | Parameters | Notes |
|---|---|---|
| `ResourceHarvester` | `resource_type`, `base_harvest_rate=0.0` | Planet resource harvesting source. |
| `LocalStorage` | `resource_type`, `capacity=0.0` | Local colony stockpile capacity; `storage_mult` can affect recalculation. |
| `StagingYard` | scalar mass or dict `capacity_mass` | Planet-side storage for assembled vehicles/items. |
| `PlanetaryYard` | marker | Enables base planetary construction queue. |
| `SpaceShipyard` | `construction_speed_bonus=1.0`, `max_ship_mass=100000`, `production_rates={}` | Enables ship construction at colonies. |

These classes inherit combat default metadata in code, but current gameplay use is strategic/colony construction.

### Planetary And Strategic Abilities

Source: `game/simulation/components/abilities/planetary.py`.

| Key | Parameters | Allowed Scopes | Notes |
|---|---|---|---|
| `PlanetaryShield` | `energy_drain_rate=0`, `activation_time=1`, `deactivation_time=1`, `shield_hp=0`, `shield_regen=0` | code default `self` | Activatable shield marker; blocks planet destroyers when active. |
| `StrategicResourceGeneration` | `resource`, `generation_rate=0` | code default `self` | Strategic per-turn resource generation. |
| `GeologicStabilizer` | `energy_drain_rate=0`, `activation_time=1`, `deactivation_time=1`, `scope` | `planet`, `sector`, `system`; default `sector` | Blocks planet-destroying superweapons in scope when active. |
| `StellarStabilizer` | same activation fields | `sector`, `system`; default `system` | Blocks star destroy and Dyson sphere actions in scope when active. |
| `WarpFieldStabilizer` | same activation fields | `sector`, `system`; default `system` | Blocks open/close warp point actions in scope when active. |
| `ResourceHarvestBooster` | `resource_type`, `multiplier=1.0`, `scope`, `stack_group` | `self`, `planet`, `sector`, `system`, `empire`, `allied_empire`; default `planet` | Multiplies matching resource harvest. |
| `BuildRateBooster` | `multiplier=1.0`, `scope`, `stack_group` | `self`, `planet`, `sector`, `system`, `empire`, `allied_empire`; default `sector` | Multiplies build queue production rates. |
| `AtmosphereModifier` | `modification_rate=0.0` | `self` | Processes atmosphere kg/turn toward target gas composition. Pressure conversion: `Pa_per_kg = gravity / surface_area`. Multiple facilities stack additively. PERMANENT (persists if facility removed). Run once per turn by `AtmosphereEngine`. |
| `QualityImprovement` | `resource_type`, `improvement_rate=0.0` | `self` | Permanent deposit quality increase per turn; caps at quality 100. |
| `GravityModifier` | activation fields | `self` | Target gravity set via `SetGravityTargetCommand`; effect reverts to original on deactivation or facility destruction (NOT permanent). Applied by `PlanetModifierEffectEngine`. |
| `WaterModifier` | `modification_rate=0.0` | `self` | PERMANENT change to planet water coverage; persists if facility removed. Processed once per turn by `WaterEngine`. |
| `RadiationShield` | activation fields, `max_shielding=1.0` | `self` | Artificial radiation shielding while active; reverts to zero on deactivation (NOT permanent). `radiation_shielding` is additive with the planet's natural `magnetic_field` in habitability calculations. |

### Combat Modifiers From Strategic Sources

Source: `planetary.py`; bridge: `ability_stat_registry.py`; collector: `combat_modifier_collector.py`.

| Key | Parameters | Allowed Scopes | External Effect |
|---|---|---|---|
| `ShieldModifier` | `multiplier=1.0`, `scope`, `stack_group`, `energy_drain_rate=0`, `activation_time=0`, `deactivation_time=0` | `self`, `fleet`, sector/system allied/player/enemy variants | Emits `shield_capacity_mult`; default scope `allied_system`. |
| `DamageModifier` | same shape | same scopes | Emits `damage_mult`; default scope `allied_system`. |
| `ThrustModifier` | `multiplier=1.0`, `scope` | storm scopes: `self`, sector/system allied/player/enemy variants | Emits `thrust_mult`. |
| `StrategicSpeedModifier` | `multiplier=1.0`, `scope` | same storm scopes | Read by fleet movement speed calculation through sector effects. |

Activation rule: if ability data carries activation fields, active state is consulted; otherwise the effect is passive/always-on.

### Strategic Environmental Rates

Source: `planetary.py`; collector: `system_effects_collector.py`; consumers include `environmental_hazard_engine.py` and `fleet_movement_engine.py`.

| Key | Parameters | Aggregation | Notes |
|---|---|---|---|
| `EnvironmentalDamage` | `rate=0.0`, `damage_type="environmental"`, `scope` | Same `damage_type` MAX, different types SUM | Per-turn hull damage. `damage_type` is free-form; known values: `plasma`, `radiation`, `thermal`, `environmental`, `warp`, `debris`. Storms typically use `sector` scope; star intrinsics like neutron-star radiation use `system`. Consumed by `environmental_hazard_engine.process_environmental_tick`. |
| `FuelDrain` | `rate=0.0`, `scope` | Single group; rates aggregate via rate rules | Per-turn fuel drain. |

Intrinsic source templates can include `chance` in `[0.0, 1.0]`. `game/strategy/services/ability_sources/intrinsic_roll.py::roll_intrinsic_abilities` removes `chance` from emitted runtime data. Missing `chance` consumes no RNG draw, preserving seeded determinism for registries that do not opt in.

| File | Source Kind |
|---|---|
| `data/planet_types.json` | planet |
| `data/star_types.json` | star |
| `data/warp_point_types.json` | warp_point |
| `data/system_archetypes.json` | system |

Runtime source adapters:

| Source Kind | Adapter |
|---|---|
| facility | `game/strategy/services/ability_sources/facility.py` |
| storm | `game/strategy/services/ability_sources/storm.py` |
| planet | `game/strategy/services/ability_sources/planet_intrinsic.py` |
| star | `game/strategy/services/ability_sources/star.py` |
| warp_point | `game/strategy/services/ability_sources/warp_point.py` |
| system | `game/strategy/services/ability_sources/system_archetype.py` |
| fleet | `game/strategy/services/ability_sources/fleet.py` |

### Superweapons

Source: `game/simulation/components/abilities/superweapons.py`.

All are strategic, self-scope marker abilities. Data is boolean marker or dict with `action_time=1`. They return `0.0` primary value and have no stat bindings.

| Key | Action |
|---|---|
| `DestroyPlanet` | Destroys a single planet. |
| `DestroyStar` | Destroys a star and system contents per strategy engine rules. |
| `OpenWarpPoint` | Creates a warp connection. |
| `CloseWarpPoint` | Closes a warp connection. |
| `CreateDysonSphere` | Builds a Dyson sphere around a star. |
| `SelfDestruct` | Schedules ship destruction. |

## Ship Stat Contributor Registry

File: `game/simulation/entities/stat_contributors/registry.py`.

`STAT_CONTRIBUTOR_REGISTRY.iter_for(comp)` is the unified Phase-3 ship-stat pipeline. Entries bind an ability key to `contributor(ship, comp, accumulator) -> None`.

Default built-ins:

| Domain | Phase Order | Abilities |
|---|---:|---|
| movement | 10 | `CombatPropulsion`, `StrategicMovement`, `WarpJump`, `ManeuveringThruster` |
| defense | 20 | `Armor`, `ShieldProjection`, `ShieldRegeneration` |
| hangar | 40 | `TacticalFighterLaunch`, `TacticalSatelliteLaunch`, `VehicleBay` |
| command | 50 | `MultiplexTracking` |

Registration API:

```python
handle = register_stat_contributor(
    "MyAbility",
    my_contributor,
    policy=RegistrationConflictPolicy.REPLACE_WARN,
    phase_order=99,
)
unregister_stat_contributor(handle)
reset_stat_contributor_registry()
```

Conflict policies:

| Policy | Behavior |
|---|---|
| `REPLACE_WARN` | Default; replaces active entry and logs. |
| `REPLACE_SILENT` | Replaces without log. |
| `APPEND` | Coexists with existing/default entry. |
| `ERROR` | Raises on conflict. |

Default entries cannot be unregistered by handle; reset clears and reseeds defaults. The root test fixture resets this registry around tests.

## Ability Inspection And Registry Lookup

File: `game/strategy/services/component_inspector.py`.

Use these helpers instead of hand-reading `comp.get("abilities", {})`:

- `get_component_abilities(comp_def) -> dict`
- `extract_abilities_from_component(comp, registries) -> dict`
- `iterate_design_components(design_data, component_registry)`
- `ship_has_ability(ship, ability_name, component_registry) -> bool`
- `find_ship_with_ability(fleet_ships, ability_name, component_registry)`
- `count_ability(ship, ability_name, component_registry) -> int`
- `list_ship_abilities(ship, component_registry) -> list[str]`
- `get_ability_list(abilities, ability_name) -> list[dict]`
- `iter_facility_ability_entries(facility, ability_name, registries=None)`
- `has_warp_capability(ship) -> bool`

Reason: facility and ship design data often stores component IDs. The abilities live in the component registry. Inline-only checks silently miss registry-defined abilities.

## Extension Guidance

### Add A New Ability

1. Add or extend a module under `game/simulation/components/abilities/`.
2. Subclass `Ability`, `SimpleMultiplierAbility`, `StaticValueAbility`, or a domain base.
3. Set `layer`, `allowed_scopes`, `default_scope`, and `STAT_BINDINGS`.
4. Parse data-derived attributes in `_parse_attrs(data)` whenever possible.
5. Implement `recalculate()` if stats affect runtime attributes.
6. Implement `get_primary_value()` and concise `get_ui_rows()`.
7. Register the key in `ABILITY_REGISTRY` and export the class from `__all__`.
8. Add focused tests under `tests/unit/simulation/components/abilities/` and integration tests if strategy/combat pipelines consume it.
9. If data-driven content uses the ability, update `data/components.json` and relevant design validation/golden tests.

### Add A New Stat-Bound Ability

- Add any new stat key to `StatKey`.
- Add `AbilityStatBinding` entries on the ability class.
- Ensure defaults match key shape: `*_mult` defaults to `1.0`, `*_add` defaults to `0.0`, set keys default to `None`.
- If ship external stats should affect it, add the key to `KNOWN_EXTERNAL_STAT_KEYS`.

### Add A New Strategic Combat-Effect Ability

1. Add the ability class and registry key.
2. Add an `AbilityStatMapping` to `ABILITY_STAT_REGISTRY`.
3. Add the emitted stat key to `KNOWN_EXTERNAL_STAT_KEYS`.
4. Ensure compilers/collectors call `emit_entries_for_ability`, not local mappings.
5. Add content coverage so registry tests see a real design using the mapping.

### Add A New Strategic System/Sector Effect

1. Add the ability class in `planetary.py` or a new strategic ability module.
2. Add metadata to `EFFECT_ABILITY_METADATA`.
3. Choose `kind`: `rate` uses rate aggregation; `multiplier` uses multiplier aggregation.
4. Set `grouping_key_field` when independent instances need separate display/aggregation groups.
5. Ensure ownerless generated sources use neutral scopes only (`sector`/`system`).
6. Add tests for collector output, aggregation, display naming, and consuming engine behavior.

### Add A New Ship-Stat Contributor

1. Write `def contribute_x(ship, comp, acc) -> None`.
2. Register with `register_stat_contributor("AbilityKey", contribute_x, phase_order=...)`.
3. Use `APPEND` to coexist with built-ins, `REPLACE_*` to override, or `ERROR` for strict tests.
4. Capture the returned handle for cleanup, or rely on `reset_stat_contributor_registry()` in tests.

### Add A New Activatable Planet Ability

- If component data carries `activation_time`, `PlanetAbilitiesController.scan_abilities()` auto-discovers it for the abilities window.
- Add persistent energy handling to `_ACTIVATABLE_ABILITIES` in `game/strategy/engine/planet_energy_engine.py`.
- Add display text to `_ACTIVATABLE_DISPLAY_NAMES` in `game/ui/screens/strategy_detail_fmt.py`.
- If CamelCase humanization is not acceptable, add an override in `ABILITY_DISPLAY_NAME_OVERRIDES` in `game/ui/screens/planet_abilities_controller.py`.
- If it needs a dedicated environment editor, add the editor window, `ENVIRONMENT_EDITORS` entry, event-router method, and window-manager wiring.

## Tests And Validation Pointers

Focused test areas:

- Ability construction/scopes: `tests/unit/simulation/components/abilities/`
- Legacy ability unit coverage: `tests/unit/abilities/`
- Modifier and binding behavior: `tests/unit/modifiers/`
- Formula skip and refresh: `tests/unit/simulation/components/test_create_ability_formula_skip.py`, `tests/integration/test_design_load_warp_capability.py`
- External stat bridge: `tests/unit/simulation/combat/test_ability_stat_registry.py`
- Fleet aura stacking: `tests/unit/simulation/combat/test_fleet_aura_provider_identity.py`
- Ship stat contributors: `tests/unit/simulation/entities/stat_contributors/`, `tests/unit/simulation/entities/test_stat_contributor_extension.py`
- Strategic source adapters: `tests/unit/strategy/services/ability_sources/`
- Strategic effects: `tests/unit/strategy/services/test_effect_ability_metadata.py`, `test_effect_ability_display.py`, `test_ability_iterator.py`, `test_combat_modifier_collector.py`
- Data schemas and intrinsic `chance`: `tests/integration/data/test_intrinsic_registries_coverage.py`
- Strategic ability integration: `tests/integration/test_strategic_abilities.py`
- Combat integration for strategic modifiers: `tests/integration/strategy/combat/test_suppressor_effects.py`, `test_storm_shield_interference.py`

Common commands:

```bash
pytest tests/unit/simulation/components/abilities/
pytest tests/unit/simulation/components/test_create_ability_formula_skip.py
pytest tests/integration/test_design_load_warp_capability.py
pytest tests/unit/simulation/combat/test_ability_stat_registry.py
pytest tests/unit/simulation/entities/stat_contributors/
pytest tests/unit/strategy/services/ability_sources/
pytest tests/unit/strategy/services/test_effect_ability_metadata.py tests/unit/strategy/services/test_ability_iterator.py
pytest tests/integration/test_strategic_abilities.py
python Tools/test_sharded/test_sharded.py
```

## PROJ-FMS-A: Fighters / Mines / Satellites — Foundation abilities

> **Added 2026-05-15** during PROJ-FMS-A. Behavior for launch/recovery/mine
> abilities lands in PROJ-FMS-B/C/D; PROJ-FMS-A only registers them so
> designs validate and the data shapes are pinned.

| Registry key | Class | Layer | File | Notes |
|---|---|---|---|---|
| `Warhead` | `WarheadAbility` | BOTH | `warhead.py` | Single attr `damage`. Always hits when triggered; behavior wired in PROJ-FMS-B. |
| `Laserhead` | `LaserheadAbility(BeamWeaponAbility)` | BOTH | `warhead.py` | Subclass of `BeamWeaponAbility` so MRO + family detection at `weapon_registry.py:78-94` works unchanged. Adds `consume_on_fire` (default true). |
| `RamTarget` | `RamTargetAbility` | COMBAT | `warhead.py` | Marker — combat engine sets `target_id` at runtime. Detonates carried Warheads on collision (PROJ-FMS-B). |
| `VehicleBay` | `VehicleBayAbility` | STRATEGIC | `vehicle_bay.py` | `capacity_mass`, `allowed_types` (defaults to mine/fighter/satellite). Aggregated by `stat_contributors/launch.py::contribute_vehicle_bay` into `ship.bay_capacity_mass`. |
| `StrategicMineLayer` | `StrategicMineLayerAbility` | STRATEGIC | `launch.py` | Skeleton; behavior in PROJ-FMS-B Phase 1 via `OrderType.LAY_MINES`. |
| `StrategicFighterLaunch` | `StrategicFighterLaunchAbility` | STRATEGIC | `launch.py` | Skeleton; behavior in PROJ-FMS-C Phase 1 via `OrderType.LAUNCH_FIGHTERS`. |
| `StrategicSatelliteLaunch` | `StrategicSatelliteLaunchAbility` | STRATEGIC | `launch.py` | Skeleton; behavior in PROJ-FMS-D Phase 1 via `OrderType.LAUNCH_SATELLITES`. |
| `TacticalMineLayer` | `TacticalMineLayerAbility` | COMBAT | `launch.py` | Skeleton; behavior in PROJ-FMS-B Phase 3 (battle-engine hook). |
| `TacticalFighterLaunch` | `TacticalFighterLaunchAbility` | COMBAT | `launch.py` | Skeleton; replaced legacy `VehicleLaunchAbility` (deleted from `markers.py` in PROJ-FMS-C audit Fix 1). |
| `TacticalSatelliteLaunch` | `TacticalSatelliteLaunchAbility` | COMBAT | `launch.py` | Skeleton; PROJ-FMS-D Phase 1. |
| `RecoverFighters` | `RecoverFightersAbility` | STRATEGIC | `recovery.py` | Skeleton; PROJ-FMS-C Phase 3 via `OrderType.RECOVER_FIGHTERS`. |
| `RecoverSatellites` | `RecoverSatellitesAbility` | STRATEGIC | `recovery.py` | Skeleton; PROJ-FMS-D Phase 2 via `OrderType.RECOVER_SATELLITES`. |

Data shape for the six launch skeletons (strategic + tactical):

```json
"StrategicFighterLaunch": {"capacity_per_action": 4, "cycle_time": 15.0}
"TacticalFighterLaunch":  {"capacity_per_action": 2, "cycle_time": 6.0, "launch_rate_tons_per_sec": 8.0}
```

QA-C: `launch_rate_tons_per_sec` is the authoritative tactical-launch
throughput dial. `CarrierAIController` accumulates a per-tick mass
budget (`rate * TICK_RATE`); any carried vehicle whose mass fits the
residual budget is popped and dispatched. Variable-mass fleets launch
at variable rates from the same bay. `capacity_per_action` /
`cycle_time` remain for design-workshop UI headlines; they don't gate
tactical dispatch any more. `launch_rate_mult` (driven by the
`simple_size_mount` modifier) scales both the count headline and the
rate.

Data shape for the two recovery skeletons:

```json
"RecoverFighters": {"recovery_per_action": 4}
```

`recovery_rate_mult` scales `recovery_per_action` via the standard
size-mount path.

Data shape for VehicleBay:

```json
"VehicleBay": {"capacity_mass": 250, "allowed_types": ["mine", "fighter", "satellite"]}
```

QA-C: `bay_capacity_mult` (driven by `simple_size_mount`) scales
`capacity_mass` linearly with the modifier param. The old
`_small / _medium / _large` tier proliferation is gone; the shipped
single component is `vehicle_bay` and consumers pick a `simple_size_mount`
value to dial in the desired capacity.

Reserved `OrderType` enum values (no handlers attached yet, reserved for
the PROJ-FMS-B/C/D handlers): `LAY_MINES`, `LAUNCH_FIGHTERS`,
`LAUNCH_SATELLITES`, `RECOVER_FIGHTERS`, `RECOVER_SATELLITES`.

Fleet discriminator: `Fleet.group_kind` ∈ `{"fleet", "fighter_group",
"satellite_group", "mine_group"}`; non-fleet kinds reject Move /
Intercept / Join / Warp / Build at command validation
(`BaseCommandHandler._reject_if_non_fleet_group`).

`SmallTargetingSensor` (PROJ-FMS-A) is **not** a new ability class — it is
a new component (`small_targeting_sensor` / `small_targeting_sensor_advanced`
in `data/components.json`) that carries the existing `ToHitAttackModifier`
ability. The distinction from `mini_sensor` is that `SmallTargetingSensor`
does **not** carry `RequiresCommandAndControl`, so it stays operational on
crewless mines and other small craft that would fail the C&C gate.

## PROJ-FMS-B — Mines runtime behaviour

PROJ-FMS-B wired runtime behaviour for the abilities skeletoned in
PROJ-FMS-A. See [`docs/systems/minefields.md`](minefields.md) for the
end-to-end system design.

| Registry key | Ability class | Layer | Source file | Behaviour landed in |
|---|---|---|---|---|
| `Warhead` | `WarheadAbility` | BOTH | `abilities/warhead.py` | Detonation routed through `DamageCalculator.apply_damage`; applied by `MinefieldResolver` (strategic), `TacticalMineResolver` (tactical), and `RamTargetResolver` (collision). |
| `Laserhead` | `LaserheadAbility(BeamWeaponAbility)` | BOTH | `abilities/warhead.py` | Continuous expected-hit-chance threshold gate before the standard beam roll; consume-on-fire. |
| `RamTarget` | `RamTargetAbility` | COMBAT | `abilities/warhead.py` | Explicit set-target action; collision detonates every `Warhead` component on the rammer against the target via the damage pipeline; rammer destroyed. |
| `StrategicMineLayer` | `StrategicMineLayerAbility` | STRATEGIC | `abilities/launch.py` | Wired via `OrderType.LAY_MINES` -> `LayMinesOrderHandler`. Pops mines from `VehicleBay` -> creates / extends a `mine_group` Fleet at the target hex. |
| `TacticalMineLayer` | `TacticalMineLayerAbility` | COMBAT | `abilities/launch.py` | Wired via the battle-engine `mine_resolver` hook. Mid-battle-laid mines persist to the laying empire's `mine_group`. |

`LAY_MINES` was moved to the reachable-via-command set in PROJ-FMS-B
Phase 1. `LAUNCH_FIGHTERS` and `RECOVER_FIGHTERS` were moved to the
reachable-via-command set in PROJ-FMS-C Phase 1+3. `LAUNCH_SATELLITES`
and `RECOVER_SATELLITES` followed in PROJ-FMS-D Phase 1+2 — see the
PROJ-FMS-D section below for the full wiring summary.

Mine-group runtime fields on `Fleet` (only meaningful when
`group_kind == "mine_group"`):

- `sensitivity` — `"LOW" | "MED" | "HIGH"` (default `"MED"`).
- `expected_hit_chance_threshold` — float `0.0..1.0` (default
  `0.30` from `data/balance/mines.json::laserhead.default_threshold`).
- `mine_positions` — `List[(float, float)]` scatter coords.
- `scatter_seed` — stable PRNG seed for the scatter layout.

These fields serialise through `Fleet.to_dict` / `Fleet.from_dict`.

## PROJ-FMS-C — Fighters runtime behaviour

PROJ-FMS-C wired runtime behaviour for the fighter abilities skeletoned
in PROJ-FMS-A and added end-of-battle reboard. See
[`docs/systems/fighters.md`](fighters.md) for the full system reference.

| Ability | Class | Layer | File | Behavior |
|---|---|---|---|---|
| `StrategicFighterLaunch` | `StrategicFighterLaunchAbility` | STRATEGIC | `abilities/launch.py` | Wired via `OrderType.LAUNCH_FIGHTERS` -> `LaunchFightersOrderHandler`. Pops fighter `CarriedVehicle`s from `VehicleBay` -> mints a new `fighter_group` Fleet at the target hex with one `ShipInstance` per launched fighter. HP preserved from `CarriedVehicle.current_hp`. |
| `TacticalFighterLaunch` | `TacticalFighterLaunchAbility` | COMBAT | `abilities/launch.py` | Drives the design-instance launch path. `BattleEngine.launch_fighters_in_battle(carrier, [CarriedVehicle, ...])` spawns full design-backed fighters with components / weapons / HP, tags them with `launched_in_battle_id` for end-of-battle reboard. The legacy `VehicleLaunchAbility` class-string spawn path was fully removed in PROJ-FMS-C audit Fix 1 — payloads without `carried_vehicle` are skipped (no fallback). |
| `RecoverFighters` | `RecoverFightersAbility` | STRATEGIC | `abilities/recovery.py` | Wired via `OrderType.RECOVER_FIGHTERS` -> `RecoverFightersOrderHandler`. Pops `ShipInstance`s from the target `fighter_group`, converts each to a `CarriedVehicle` (HP + per-component damage preserved), loads into the recovering carrier's bay. Partial recovery allowed; empty groups pruned from `empire.fleets`. |

`OrderType.LAUNCH_FIGHTERS` and `OrderType.RECOVER_FIGHTERS` were moved
from the reserved-no-command-yet set to the reachable-via-command set in
PROJ-FMS-C Phase 1+3. `LAUNCH_SATELLITES` and `RECOVER_SATELLITES`
remain reserved for PROJ-FMS-D.

End-of-battle reboard semantics (PROJ-FMS-C Phase 3):

- Fighters launched mid-battle (tag `launched_in_battle_id`) auto-
  reboard onto friendly ships with bay space at battle end.
- Overflow spills into a new `fighter_group` at the sector. Pre-existing
  fighter_groups at the sector owned by the same empire MERGE overflow
  rather than fragmenting.
- Dead-on-arrival fighters are discarded.
- Carrier destroyed mid-battle: launched fighters look for any other
  friendly carrier; otherwise overflow to sector.
- Pre-existing fighter_group ships are NOT auto-reboarded — they stay
  in their original group unless explicitly recovered.

The reboard pipeline is hooked into `run_battle` via the spec compiler's
`build_fighter_reboard_setup` `pre_tick_loop_callback`. The strategy
post-battle hook in `_build_strategy_post_battle_hook` calls
`fighter_reboard.apply_reboard(...)` BEFORE `apply_outcome_to_fleets`.

## PROJ-FMS-D — Satellites runtime behaviour

PROJ-FMS-D wired runtime behaviour for the three satellite skeletons in
PROJ-FMS-A. The design intent is "satellites mirror fighters with three
differences": stationary tactical AI, separate ability gates (a
fighter-only carrier cannot recover satellites and vice versa), and
typed bays. See [`docs/systems/satellites.md`](satellites.md) for the
full system reference.

| Ability | Class | Layer | File | Behavior |
|---|---|---|---|---|
| `StrategicSatelliteLaunch` | `StrategicSatelliteLaunchAbility` | STRATEGIC | `abilities/launch.py` | Wired via `OrderType.LAUNCH_SATELLITES` -> `LaunchSatellitesOrderHandler`. Pops satellite `CarriedVehicle`s from `VehicleBay` -> mints a new `satellite_group` Fleet (id namespace 300000+) at the target hex with one deployed `ShipInstance` per launched satellite. HP preserved from `CarriedVehicle.current_hp`. |
| `TacticalSatelliteLaunch` | `TacticalSatelliteLaunchAbility` | COMBAT | `abilities/launch.py` | Drives the in-battle satellite spawn. `BattleEngine.launch_satellites_in_battle(carrier, [CarriedVehicle, ...])` materialises full design-backed satellites with components / weapons / HP, tags them with `launched_in_battle_id` for end-of-battle reboard. Production caller: `CarrierAIController._maybe_launch_satellite_wave` (factory-dispatched). |
| `RecoverSatellites` | `RecoverSatellitesAbility` | STRATEGIC | `abilities/recovery.py` | Wired via `OrderType.RECOVER_SATELLITES` -> `RecoverSatellitesOrderHandler`. Pops `ShipInstance`s from the target `satellite_group`, converts each to a `CarriedVehicle` (HP + per-component damage preserved), loads into the recovering carrier's bay (respecting the bay's `allowed_types` filter). Partial recovery allowed; empty groups pruned. |

`OrderType.LAUNCH_SATELLITES` and `OrderType.RECOVER_SATELLITES` were
moved from the reserved-no-command-yet set to the reachable-via-command
set in PROJ-FMS-D Phase 1+2. All five PROJ-FMS reserved OrderType values
are now wired.

### Bay separation mechanism — `VehicleBay.allowed_types`

`VehicleBayAbility` (PROJ-FMS-A Phase 3) carries an `allowed_types`
list. QA-C ships four pre-configured component variants; capacity is
scaled by `simple_size_mount` rather than baked into named tiers:

- `vehicle_bay` — universal (`["mine", "fighter", "satellite"]`).
- `fighter_bay` — fighter-only (`["fighter"]`).
- `satellite_bay` — satellite-only (`["satellite"]`).
- `mine_bay` — mine-only (`["mine"]`).

`ShipCargoManager.can_accept_vehicle` queries this list per active bay
and refuses to load a vehicle whose `vehicle_type` is not accepted by
any bay. This is the same gate used by both the strategic launch /
recovery handlers and the end-of-battle reboard, so a fighter-only
carrier cannot accidentally pick up satellites no matter the layer.

### Cross-type ability gating

The command specs declare `action_ability_name`:

- `LaunchSatellitesCommandHandler` -> `StrategicSatelliteLaunch`.
- `RecoverSatellitesCommandHandler` -> `RecoverSatellites`.

This closes the same gating loophole the PROJ-FMS-C audit fixed for
fighters: `ActionTimeResolver` looks up the ability on the carrier's
components, so a ship without the appropriate strategic launch /
recovery ability cannot issue the order.

### Stationary tactical AI

`SatelliteAIController` (registered via
`AIControllerFactory.create_for_ship` on `vehicle_type == "Satellite"`)
forces zero throttle / zero turn throttle every tick. It still
acquires the nearest enemy and pulls the trigger so weapons fire, but
the ship never accelerates or rotates under its own power. No movement
policy, no behaviour tree, no avoidance, no kamikaze handling.

### Stat aggregation

`stat_contributors/launch.py::contribute_tactical_satellite_launch`
aggregates into `ship.satellites_per_wave` /
`ship.satellite_launch_cycle` / `ship.satellite_capacity`, kept
distinct from the fighter equivalents so a carrier mounting both bays
shows both stat sets independently.

### End-of-battle reboard — generalised

`fighter_reboard.apply_reboard` (kept under that file name for
backwards-compat) is now vehicle-type aware:

- The CarriedVehicle's `vehicle_type` is read from the spawned Sim
  Ship's `vehicle_type` attribute (`Fighter` -> `"fighter"`,
  `Satellite` -> `"satellite"`).
- Overflow uses the matching `group_kind` (`fighter_group` /
  `satellite_group`) and the matching id namespace (200000+ / 300000+).
- The bay-side `load_vehicle` honours `allowed_types`, so a fighter
  reboard never lands in a satellite-only bay (and vice versa).

The same reboard hook handles fighters and satellites in a single
pass; there is no parallel `satellite_reboard.py`.
