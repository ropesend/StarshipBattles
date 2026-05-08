# Component System - Compact Agent Reference

> **Last verified:** 2026-05-08 - Balanced from `docs/guides/component_system.md`, `AgentCoordination/Scratchpad/reports/guides_component_system_ALT_compact.md`, and current component/ability source files.

## Purpose

Ships, stations, planetary complexes, facilities, and some environmental sources are built from data-driven components. A component owns ability instances, modifier state, resource/activation checks, HP/status, formula-derived stats, and its assigned ship layer.

Primary data:
- `data/components.json` - component definitions and ability payloads.
- `data/modifiers.json` - modifier definitions.
- `data/vehiclelayers.json` - vehicle layer availability and placement rules.

Primary code:
- `game/simulation/components/component.py` - `Component` facade and public API.
- `game/simulation/components/ability_manager.py` - ability creation, indexing, and lookup.
- `game/simulation/components/modifier_manager.py` - applied modifiers.
- `game/simulation/components/component_stats_calculator.py` - formula evaluation and component stat recalculation.
- `game/simulation/components/component_health_manager.py` - HP, active/damaged/destroyed state.
- `game/simulation/components/component_resource_manager.py` - resource costs and activation checks.
- `game/simulation/components/abilities/` - ability classes, `ABILITY_REGISTRY`, and `get_ability_default_scope`.
- `game/simulation/entities/stat_contributors/` - ship stat contribution registry and built-in contributors.
- `game/strategy/services/component_inspector.py` - canonical strategy/facility design ability inspection.

## Lifecycle

```
data/components.json
  -> RegistryLoader / RegistryManager
  -> Component(data, registries=...)
  -> ability instances created from data["abilities"]
  -> ship.add_component(component, layer)
  -> component.ship set, layer assigned, stats recalculated with ship context
  -> update() each combat tick
  -> take_damage() updates HP/status/is_active
  -> recalculate_stats() after modifiers, context changes, attach, or clone flows
```

Current public contracts:
- `Component(data, *, registries)` requires registry injection and raises `ValidationException` if `registries is None`.
- `component.get_abilities(name) -> list[Ability]`.
- `component.get_ability(name) -> Ability | None`.
- `component.has_ability(name) -> bool`.
- `component.recalculate_stats(context: dict | None = None) -> None`.
- `component.update() -> None` runs ability updates; non-activation failures mark the component non-operational.
- `component.take_damage(amount: float) -> bool`.
- `component.clone() -> Component` deep-copies component data and copies `self.ship` when cloning an attached component.

`Component` deep-copies input data because ability payloads and modifiers contain nested mutable structures. Do not share registry definition dictionaries as live mutable component state.

## Registry And DI

Components and ships use registry injection, not hidden globals inside simulation code.

```python
from game.core.registry import get_default_registry_provider
from game.simulation.components.component import Component

provider = get_default_registry_provider()
comp_data = provider.get_components()["laser_mk1"]
component = Component(comp_data, registries=provider)
```

Simulation-layer code should use injected registries already present on objects, usually `component._registries` or `ship._registries`. Tests should use `TestRegistryProvider`, `GameRegistries`, or fixture-provided registries instead of production global state.

## Ability Model

Abilities are behavior objects created from `component.data["abilities"]`. Registry keys live in `game/simulation/components/abilities/__init__.py::ABILITY_REGISTRY`; at verification it contains 60 keys. The registry is the source of truth, not an ability count copied into docs.

Current families include:
- Base/value helpers: `Ability`, `SimpleMultiplierAbility`, `StaticValueAbility`.
- Weapons: `WeaponAbility`, `ProjectileWeaponAbility`, `BeamWeaponAbility`, `SeekerWeaponAbility`.
- Propulsion: `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `WarpJump`.
- Defense/armor: `ShieldProjection`, `ShieldRegeneration`, `ToHitAttackModifier`, `ToHitDefenseModifier`, `EmissiveArmor`, `ShieldRegeneratingArmor`, `Armor`.
- Crew/markers/storage: `CrewCapacity`, `LifeSupportCapacity`, `CrewRequired`, `CommandAndControl`, `RequiresCommandAndControl`, `RequiresCombatMovement`, `StructuralIntegrity`, `MultiplexTracking`, `VehicleLaunch`, `VehicleStorage`, `PodStorage`.
- Resources/cargo/production: `ResourceConsumption`, `ResourceStorage`, `ResourceGeneration`, `CargoStorage`, `ResourceHarvester`, `SpaceShipyard`, `PlanetaryYard`, `StagingYard`, `LocalStorage`.
- Colonization/superweapons: `ColonizePlanet`, `DestroyPlanet`, `DestroyStar`, `OpenWarpPoint`, `CloseWarpPoint`, `CreateDysonSphere`, `SelfDestruct`.
- Strategic/environmental: `PlanetaryShield`, `StrategicResourceGeneration`, `GeologicStabilizer`, `StellarStabilizer`, `WarpFieldStabilizer`, `ResourceHarvestBooster`, `BuildRateBooster`, `AtmosphereModifier`, `QualityImprovement`, `ShieldModifier`, `DamageModifier`, `GravityModifier`, `WaterModifier`, `RadiationShield`, `ThrustModifier`, `StrategicSpeedModifier`, `EnvironmentalDamage`, `FuelDrain`.

Ability lookup is by registry key:

```python
if component.has_ability("BeamWeaponAbility"):
    weapon = component.get_ability("BeamWeaponAbility")
```

Do not infer behavior from `component.type`, component name, or hardcoded class-name lists.

## Ability Layer, Scope, And Defaults

Definitions live in `game/simulation/components/abilities/base.py`.

`AbilityLayer`:
- `COMBAT` - tactical battle simulation.
- `STRATEGIC` - strategy map/turn systems.
- `BOTH` - both layers.

`AbilityScope` values:
- `self`, `fleet`, `sector`, `allied_sector`, `system`, `allied_system`.
- `planet`, `empire`, `allied_empire`.
- `enemy_sector`, `enemy_system`, `player_sector`, `player_system`.

Each ability class declares `allowed_scopes` and `default_scope`. Compiler, collector, and strategy routing code must call `get_ability_default_scope(ability_name)` from `game/simulation/components/abilities/__init__.py` when JSON omits `scope`; do not hardcode `"self"`.

Terminology matters: a system is the star-system region; a sector is one hex. Fleet/location validation for ability targets should use sector precision when the target is a specific hex, planet, or warp point.

## Strategic Abilities

Strategic abilities operate on the turn/strategy layer, not the per-tick combat loop. `ResourceGeneration` is combat-time generation; `StrategicResourceGeneration` is per-turn strategy generation. A component may have both.

Common strategic payload fields:
- `PlanetaryShield`: `energy_drain_rate`, `activation_time`, `deactivation_time`.
- `StrategicResourceGeneration`: `resource`, `generation_rate`.
- `GeologicStabilizer`: `energy_drain_rate`, `activation_time`, `deactivation_time`, `scope`.
- `StellarStabilizer`: `energy_drain_rate`, `activation_time`, `deactivation_time`, `scope`.
- `WarpFieldStabilizer`: `energy_drain_rate`, `activation_time`, `deactivation_time`, `scope`.
- `ShieldModifier` / `DamageModifier`: `multiplier`, `scope`, `energy_drain_rate`, `activation_time`, `deactivation_time`.
- `GravityModifier`: `energy_drain_rate`, `activation_time`, `deactivation_time`.
- `WaterModifier` / `AtmosphereModifier`: `modification_rate`.
- `RadiationShield`: `energy_drain_rate`, `activation_time`, `deactivation_time`, `max_shielding`.
- `ResourceHarvestBooster`: `resource_type`, `multiplier`, `scope`, `stack_group`.
- `BuildRateBooster`: `multiplier`, `scope`, `stack_group`.
- `QualityImprovement`: `resource_type`, `improvement_rate`.
- `ThrustModifier` / `StrategicSpeedModifier`: `multiplier`, `scope`.
- `EnvironmentalDamage`: `rate`, `damage_type`, `scope`.
- `FuelDrain`: `rate`, `scope`.

Strategy/facility scans must resolve component IDs through the component registry. Facility and design data commonly store components as IDs or `{"id": ...}` references, not inline abilities.

Use helpers from `game/strategy/services/component_inspector.py`:
- `extract_abilities_from_component(comp, registries)`.
- `iterate_design_components(design_data, component_registry)`.
- `iter_facility_ability_entries(facility, ability_name, registries)`.
- `ship_has_ability(ship, ability_name, component_registry)`.
- `get_ability_list(abilities, ability_name)`.
- `has_warp_capability(ship)`.

Anti-pattern:

```python
for comp in facility.design_data["layers"]["CORE"]:
    if "PlanetaryShield" in comp.get("abilities", {}):
        ...
```

Correct pattern:

```python
from game.strategy.services.component_inspector import iter_facility_ability_entries

for comp, entry in iter_facility_ability_entries(facility, "PlanetaryShield", registries):
    drain = entry.get("energy_drain_rate", 0)
```

## Stat Bindings, Modifiers, And External Stats

Abilities declare consumed modifier stats with `STAT_BINDINGS`, a list of `AbilityStatBinding` entries from `game/simulation/components/abilities/stat_keys.py`.

```python
STAT_BINDINGS = [
    AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply", "_base_damage"),
]
```

Operations:
- `add` - adds to base value.
- `multiply` - multiplies base value.
- `set` - overrides value.

`Ability.get_effective_stat(stat_key)` checks ability-specific stats, component-level stats, then read-only battle external stats from `ship.external_stats`. `_mult` keys multiply local and external values; `_add` keys sum them; unknown key shapes prefer the external value.

`SimpleMultiplierAbility` fits one numeric value modified by one multiplier. Subclasses set `stat_key`, `value_attr`, `base_attr`, `ui_label`, `ui_format`, `ui_color`, and optional `int_result`.

`StaticValueAbility` fits one parsed value with no modifier bindings.

Ship-level stat contributions use `game/simulation/entities/stat_contributors/registry.py`. If a new ability changes aggregate ship stats, register a contributor with `register_stat_contributor(ability_name, contributor, policy=...)` and capture the returned `RegistrationHandle` for cleanup. Built-in contributors are default entries with phase ordering: movement `10`, defense `20`, hangar `40`, command `50`; modder entries default to `99`.

Keep `game/simulation/combat/ability_stat_registry.py` separate from the stat contributor registry: the former emits battle modifier/external-stat entries; the latter contributes ship stats during `ShipStatsCalculator`.

## Stacking And Aggregation

`Ability.stack_group` is parsed from ability payloads. Current aggregation rules:
- General numeric ability aggregation: same `stack_group` uses MAX; different groups SUM. Abilities without `stack_group` each form their own group.
- Strategic multiplier aggregation via `aggregate_multipliers`: same group MAX; different groups MULTIPLY.
- Strategic rate aggregation via `aggregate_rates`: same group MAX; different groups SUM.

Examples: duplicate sensors in the same group keep the best value; plasma damage plus radiation damage sum because they are distinct phenomena; two radiation entries in the same group use the worse rate.

## Formula Evaluation

Component fields and ability payloads may contain formula strings beginning with `=`.

Formula context is resolved from:
1. Explicit `context` passed to `Component.recalculate_stats(context)`.
2. `component.ship.max_mass_budget` when the component is attached to a ship.

If a formula references `ship_class_mass` and no context or attached ship is available, evaluation raises `FormulaException`. Do not restore silent defaults.

Attachment order matters:
- If a component has ship-class formulas and modifiers will trigger recalculation, attach it to the ship before adding modifiers.
- `Component.clone()` copies the `ship` reference for attached sources, so live component clones can recalculate with the same ship context.
- Detached palette/template clones remain detached; workshop code must set `clone.ship = workshop_ship` before recalculation when formulas need ship context.
- Runtime weapon formulas that reference variables such as `range_to_target`, `target_mass`, or `target_speed` are preserved for runtime evaluation rather than eagerly resolved during component recalculation.

`create_ability()` skips ability construction when data still contains unevaluated formula strings at registry-load time. The ability is instantiated or synced later after formulas resolve with context.

## Ability Attribute Refresh

`Ability` uses a template-method refresh contract:
- Subclasses parse data-derived attributes in `_parse_attrs(data)`.
- `Ability.__init__` calls `_parse_attrs(data)`.
- `Ability.sync_data(data)` also calls `_parse_attrs(data)`.

This keeps formula-derived attributes current across recalculations while preserving runtime state such as cooldowns. New ability classes that parse fields from data should override `_parse_attrs`, not duplicate parsing in both `__init__` and `sync_data`.

Known formula-sensitive production abilities include `WarpJump`, `EmissiveArmor`, `ShieldRegeneratingArmor`, `CrewRequired`, and `ResourceConsumption`.

## Modifier Flow

```
Workshop edit
  -> ModifierEditorPanel._on_row_change()
  -> component.add_modifier/remove_modifier or modifier value update
  -> component.recalculate_stats()
  -> viewmodel.on_modifier_changed()
  -> multi-selection sync if applicable
  -> viewmodel.notify_ship_changed()
  -> ship.recalculate_stats()
  -> SHIP_UPDATED event
  -> UI panels refresh
```

Key files:
- `game/simulation/components/modifier_manager.py`.
- `game/simulation/services/modifier_service.py`.
- `game/simulation/components/modifier_introspection.py`.
- `docs/guides/modifier_system.md`.
- `docs/guides/adding_modifiers.md`.

## Ship Layers

`LayerType` is defined in `game/core/constants.py`.

| Layer | Value | Purpose |
|---|---:|---|
| `HULL` | 0 | innermost chassis/hull |
| `CORE` | 1 | bridge, reactors, crew support |
| `INNER` | 2 | engines, storage, internal systems |
| `OUTER` | 3 | weapons, shields, sensors |
| `ARMOR` | 4 | outer armor |

Layer availability and placement restrictions are data-driven by `data/vehiclelayers.json`. Current vehicle templates block components with `major_classification: "Armor"` from `CORE`, `INNER`, and `OUTER`; armor components belong in `LayerType.ARMOR`.

## Component JSON Shape

Components live in the top-level `"components"` array in `data/components.json`.

```json
{
  "id": "railgun",
  "name": "Railgun",
  "type": "ProjectileWeaponAbility",
  "mass": 100,
  "hp": 150,
  "allowed_vehicle_types": ["Ship", "Satellite", "Planetary Complex"],
  "sprite_index": 4,
  "major_classification": "Weapon",
  "abilities": {
    "CrewRequired": 5,
    "ResourceConsumption": [
      {"resource": "ammo", "amount": 1, "trigger": "activation"}
    ],
    "ProjectileWeaponAbility": {
      "damage": "=40 - (0.01 * range_to_target)",
      "range": 2400,
      "reload": 2.0,
      "projectile_speed": 20000,
      "firing_arc": 1
    }
  },
  "construction_cost": {
    "metals": 80
  }
}
```

Ability payload formats:
- Dict: full parameters, e.g. `{"damage": 100, "range": 5000}`.
- Primitive: shorthand single value, e.g. `"CrewRequired": 5` or marker `true`.
- List: multiple entries for abilities that can appear more than once.
- Formula: string starting with `=`, evaluated during recalculation or preserved for runtime weapon variables.

## Extension Recipes

Adding or changing a component:
1. Add or update data in `data/components.json`.
2. Use existing ability registry keys where possible.
3. Update `data/vehiclelayers.json` only when placement behavior changes.
4. Write or update the failing test first.
5. Validate starter designs if shipped designs are affected.

Adding a new ability:
1. Add the ability class under `game/simulation/components/abilities/`.
2. Register its key in `ABILITY_REGISTRY` and export it from the package.
3. Choose `AbilityLayer`, `allowed_scopes`, and `default_scope`.
4. Declare `STAT_BINDINGS` if modifiers affect it.
5. Parse data in `_parse_attrs(data)`.
6. Prefer `SimpleMultiplierAbility` or `StaticValueAbility` when their contracts fit.
7. Add stat-contributor registration if it affects aggregate ship stats.
8. Add focused tests and update ability docs/reference if the public ability set changes.

Adding strategic/facility logic:
1. Scan design/facility components through `component_inspector` helpers.
2. Resolve component IDs through registries; do not require inline abilities.
3. Respect ability scope defaults through `get_ability_default_scope`.
4. Keep system and sector semantics distinct.

Adding modifier behavior:
1. Add modifier data in `data/modifiers.json`.
2. Bind target stats through `AbilityStatBinding` or component stat keys.
3. Use `ModifierService` for validation and `modifier_introspection` for UI/explainability.
4. Avoid hardcoded ability/type lists; prefer stat bindings, tags, registry metadata, or protocols.

## Invariants And Warnings

- Component construction requires registries.
- Simulation must not import Strategy/UI or resolve production registries through global lookup.
- Strategy/facility ability checks must use registry-backed lookup.
- Ability keys are registry keys; component `type` is not an ability-dispatch contract.
- Missing formula context must fail loudly with `FormulaException`.
- `_parse_attrs` is the canonical refresh hook for data-derived ability fields.
- Abilities preserve runtime state across `sync_data`; do not recreate stateful cooldowns unless intended.
- Modifiers recalculate component stats; ship/design-level changes then recalculate ship stats.
- Vehicle layer restrictions are data-driven.
- Armor currently belongs in `LayerType.ARMOR`.
- No compatibility shims or migrations for old component/save formats.

## Useful Tests And Commands

Targeted tests:
- `pytest tests/unit/simulation/components`
- `pytest tests/unit/simulation/components/abilities`
- `pytest tests/unit/modifiers`
- `pytest tests/unit/strategy/test_component_inspector.py`
- `pytest tests/integration/test_design_load_warp_capability.py`
- `pytest tests/integration/test_strategic_abilities.py`
- `pytest tests/unit/simulation/entities/stat_contributors`

Data validation:
- `python Tools/validate_designs/validate_designs.py`

Repo-wide:
- `pytest tests/ --testmon`
- `python Tools/test_sharded/test_sharded.py`

## Related References

- `docs/systems/ability_reference.md` - ability catalog, formula-sensitive abilities, stacking details, and stat bindings.
- `docs/guides/adding_abilities.md` - new ability workflow.
- `docs/guides/modifier_system.md` - modifier system details.
- `docs/guides/adding_modifiers.md` - new modifier workflow.
- `docs/systems/combat_simulation.md` - combat/battle integration.
- `docs/02_PATTERNS.md` - registry DI, two-phase ability aggregation, ability-stat registry, and stat contributor registry.
