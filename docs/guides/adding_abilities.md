# Adding New Abilities

> **Last verified:** 2026-05-08 - Compact rewrite checked against the original guide, current source contracts, and current registry extension points.

Compact agent reference for adding component abilities. For the full current catalog of registry keys, parameters, and bindings, see `docs/systems/ability_reference.md`.

## Purpose

Abilities are component behavior classes. They:

1. Parse component JSON data into typed runtime attributes.
2. Declare modifier/stat integration through `STAT_BINDINGS`.
3. Expose gameplay behavior such as weapons, shields, movement, storage, crew, activation, or strategic effects.
4. Provide UI rows and primary values for scanners, detail panels, and stat aggregation.

The ability class itself is only one part of the contract. Depending on behavior, you may also need stat-contributor registration, combat modifier mapping, weapon-family registration, strategic effect metadata, activation UI wiring, and tests.

## Fast Path

1. Write or identify the failing test first and run it to confirm failure.
2. Add the ability class under `game/simulation/components/abilities/` in the category module that matches its behavior.
3. Register it in `game/simulation/components/abilities/__init__.py` via `ABILITY_REGISTRY` and `__all__`.
4. Declare `STAT_BINDINGS` with `StatKey` values if component modifiers affect ability attributes.
5. If the ability contributes to ship stats, add or extend a `STAT_CONTRIBUTOR_REGISTRY` contributor.
6. If the ability projects combat modifiers through `ModifierStack`, add `ABILITY_STAT_REGISTRY` and `KNOWN_EXTERNAL_STAT_KEYS` entries.
7. If it is a new weapon family, register a weapon handler and family metadata.
8. If it is strategic, add the appropriate activation, effect-metadata, combat-collector, or editor wiring.
9. Add focused tests, then run the affected command set.

## Data And Lifecycle Invariants

Component ability data lives in `data/components.json` under the component's `abilities` mapping. Supported shapes:

```json
{
  "abilities": {
    "CombatPropulsion": 1500,
    "BeamWeaponAbility": {"damage": 50, "range": 2400, "reload": 1.5},
    "ResourceConsumption": [
      {"resource": "energy", "amount": 1, "trigger": "activation"}
    ],
    "CommandAndControl": true
  }
}
```

Important invariants:

- Parse data-derived attributes in `_parse_attrs(data)`, not `__init__()`. The base `Ability` calls `_parse_attrs()` from construction and `sync_data()`, so formula-backed values refresh after the component attaches to a ship.
- `create_ability()` skips unevaluated formula data silently during registry load. The ability is instantiated later when formulas resolve with ship context.
- Use `get_effective_stat()` for modifier-aware values. Do not read `component.stats` directly in new recalculate logic.
- Abilities read combined stat values but must not mutate `component.stats`.
- `AbilityManager` preserves existing ability instances and calls `sync_data()` during recalculation to keep runtime state such as cooldowns.
- Component ability lookup is polymorphic. `comp.get_ability("WeaponAbility")` can return `BeamWeaponAbility`, `ProjectileWeaponAbility`, or another subclass.
- Facility and complex designs often store component IDs, not inline abilities. Strategy code must use registry-backed helpers in `game/strategy/services/component_inspector.py`.

## Choose The Base Class

| Base | Use when |
| --- | --- |
| `SimpleMultiplierAbility` | One numeric value controlled by one multiplier stat. |
| `StaticValueAbility` | One static numeric value with no modifier bindings. |
| `Ability` | Multiple stats, custom formulas, marker behavior, activation, strategic behavior, or custom update/on-activation logic. |

Use modern annotations in new code (`list[...]`, `dict[...]`, `X | None`). Some existing ability modules still use legacy `List` and `Dict`; do not expand that style when touching code.

## Simple Multiplier Pattern

Use this for the common "one base value, one multiplier" case.

```python
from .base import SimpleMultiplierAbility
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_THRUST


class ThrusterAbility(SimpleMultiplierAbility):
    """Provides thrust force for combat movement."""

    stat_key = "thrust_mult"
    value_attr = "thrust_force"
    base_attr = "base_thrust"
    ui_label = "Thrust"
    ui_format = "{:.0f} N"
    ui_color = HINT_THRUST
    int_result = False

    STAT_BINDINGS: list[AbilityStatBinding] = [
        AbilityStatBinding(
            StatKey.THRUST_MULT,
            "thrust_force",
            "multiply",
            "base_thrust",
        ),
    ]
```

`SimpleMultiplierAbility` provides `_parse_attrs()`, `recalculate()`, `get_ui_rows()`, and `get_primary_value()`. It validates required class attributes at subclass creation.

Current examples: `CombatPropulsion`, `ManeuveringThruster`, `StrategicMovement`, `ShieldProjection`, `ShieldRegeneration`, `CrewCapacity`, `LifeSupportCapacity`.

## Static Value Pattern

Use `StaticValueAbility` for numeric abilities that aggregate but do not consume modifier stats.

```python
from .base import StaticValueAbility
from .ui_colors import HINT_DAMAGE


class SensorJamming(StaticValueAbility):
    """Static jamming score."""

    ui_label = "Jamming"
    ui_color = HINT_DAMAGE
    ui_format = "{:.1f}"
```

It supplies `_parse_attrs()`, no-op `recalculate()`, UI rows, and primary value. Current examples include to-hit modifiers and static armor-style abilities.

## Raw Ability Pattern

Use raw `Ability` for multiple attributes or nonstandard calculations.

```python
from typing import Any

from .base import Ability
from .stat_keys import AbilityStatBinding, StatKey
from .ui_colors import HINT_DAMAGE


class CustomAbility(Ability):
    """Example ability with two modifier-aware stats."""

    STAT_BINDINGS: list[AbilityStatBinding] = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply", "_base_damage"),
        AbilityStatBinding(StatKey.RANGE_MULT, "range", "multiply", "_base_range"),
    ]

    def _parse_attrs(self, data: Any) -> None:
        if isinstance(data, dict):
            self.damage = float(data.get("damage", 0))
            self.range = float(data.get("range", 0))
        else:
            self.damage = self._parse_primary_value(data)
            self.range = 0.0

        self._base_damage = self.damage
        self._base_range = self.range

    def recalculate(self) -> None:
        self.damage = self._base_damage * self.get_effective_stat("damage_mult", 1.0)
        self.range = self._base_range * self.get_effective_stat("range_mult", 1.0)

    def get_ui_rows(self) -> list[dict[str, object]]:
        return [
            {"label": "Damage", "value": f"{self.damage:.0f}", "color_hint": HINT_DAMAGE},
        ]

    def get_primary_value(self) -> float:
        return self.damage
```

Current examples: `WeaponAbility`, `ResourceConsumption`, `RequiresMaintenance`, `WarpJump`, `EmissiveArmor`, strategic planetary abilities.

## Marker Abilities

Marker abilities usually extend `Ability`, declare no bindings, and return a simple UI row or marker value.

```python
class CommandAndControl(Ability):
    """Marks component as providing ship command capability."""

    STAT_BINDINGS: list[AbilityStatBinding] = []

    def get_ui_rows(self) -> list[dict[str, object]]:
        return [{"label": "Command", "value": "Active", "color_hint": HINT_CREW_CAP}]

    def get_primary_value(self) -> float:
        return 1.0
```

Do not override `__init__()` unless the base lifecycle is genuinely insufficient. Base `Ability.__init__()` already handles `component`, `data`, tags, `stack_group`, scope parsing, and `_parse_attrs()`.

## Registration

Edit `game/simulation/components/abilities/__init__.py`.

```python
from .propulsion import ThrusterAbility

ABILITY_REGISTRY = {
    # ...
    "ThrusterAbility": ThrusterAbility,
}

__all__ = [
    # ...
    "ThrusterAbility",
]
```

The registry key is the JSON ability key:

```json
{
  "abilities": {
    "ThrusterAbility": 1500
  }
}
```

New code should import from the package:

```python
from game.simulation.components.abilities import CombatPropulsion, WeaponAbility
```

## STAT_BINDINGS Contract

`STAT_BINDINGS` describe which modifier stats the ability consumes.

```python
AbilityStatBinding(
    stat_key=StatKey.DAMAGE_MULT,
    attribute_name="damage",
    operation="multiply",
    base_attribute="_base_damage",
)
```

Operations:

| Operation | Effect |
| --- | --- |
| `multiply` | `attribute = base_attr * stat_value` |
| `add` | `attribute = base_attr + stat_value` |
| `set` | `attribute = stat_value` |

Use `StatKey` enum members in bindings, not raw strings. Runtime lookup reads string values such as `"damage_mult"` through `get_effective_stat()`.

Current stat keys in `game/simulation/components/abilities/stat_keys.py`:

- Multiplicative: `MASS_MULT`, `HP_MULT`, `DAMAGE_MULT`, `RANGE_MULT`, `COST_MULT`, `THRUST_MULT`, `TURN_MULT`, `STRATEGIC_MULT`, `ENERGY_GEN_MULT`, `CAPACITY_MULT`, `SHIELD_CAPACITY_MULT`, `CREW_CAPACITY_MULT`, `LIFE_SUPPORT_CAPACITY_MULT`, `CONSUMPTION_MULT`, `RELOAD_MULT`, `ENDURANCE_MULT`, `PROJECTILE_HP_MULT`, `PROJECTILE_DAMAGE_MULT`, `CREW_REQ_MULT`.
- Additive: `MASS_ADD`, `ARC_ADD`, `ACCURACY_ADD`, `PROJECTILE_STEALTH_LEVEL`, `SHIELD_BONUS_ADD`.
- Set/override: `ARC_SET`.

`SHIELD_BONUS_ADD` is ship-level, not per-ability. It is consumed once per ship by `game/simulation/entities/ship_stats.py::_apply_aggregated_stats`.

## get_effective_stat() Invariant

`Ability.get_effective_stat(stat_key, default)` composes local component stats and external battle stats:

1. Targeted local lookup: `component.ability_stats[ClassName][stat_key]`.
2. Component-wide fallback: `component.stats[stat_key]`.
3. External lookup: `ship.external_stats[stat_key]`, populated from `BattleSpec.modifier_stack`.
4. Composition:
   - `_mult` keys multiply local and external values.
   - `_add` keys add local and external values.
   - unknown key shapes use the external value when both are present.
5. Defaults:
   - `_mult`: `1.0`
   - `_add`: `0.0`
   - other keys: `None` unless an explicit default is supplied.

Targeted modifiers specify `target_ability`, for example `"WeaponAbility"`. Global modifiers omit `target_ability`.

## Ship Stat Contributors

`STAT_BINDINGS` only lets modifiers change ability attributes. It does not automatically make a new ability affect derived ship stats.

If the ability contributes to ship stats during `ShipStatsCalculator._phase_stats_aggregation`, register a contributor in `game/simulation/entities/stat_contributors/registry.py`:

```python
from game.simulation.entities.stat_contributors.accumulator import StatAccumulator
from game.simulation.entities.stat_contributors.registry import register_stat_contributor


def contribute_my_ability(ship, comp, acc: StatAccumulator) -> None:
    ability = comp.get_ability("MyAbility")
    if ability is None:
        return
    acc.thrust += ability.get_primary_value()


handle = register_stat_contributor("MyAbility", contribute_my_ability)
```

Contributor contract:

- Built-ins and extensions share `STAT_CONTRIBUTOR_REGISTRY`.
- Contributors receive `(ship, comp, acc)` and mutate `StatAccumulator`.
- `StatAccumulator` has typed scalar fields such as `thrust`, `strategic_movement`, `turn_speed`, `max_shields`, `shield_regen`, `warp_max_tonnage`, `pod_storage_mass`, and map fields such as `resource_storage`, `resource_generation`, `cargo_storage`, and `warp_resource_costs`.
- Default phase order is movement 10, defense 20, hangar 40, command 50; modder entries default to 99.
- Capture the `RegistrationHandle` and unregister with `unregister_stat_contributor(handle)` in tests or temporary code.
- Use `register_crew_priority("MyAbility", priority=N)` only when the ability should participate in crew-allocation priority.

Useful tests:

- `tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py`
- `tests/unit/simulation/entities/test_stat_contributor_extension.py`

## Combat Modifier Projection

If a strategic or external source should project a stat into battle through `ModifierStack`, use `game/simulation/combat/ability_stat_registry.py`.

Current mapped abilities:

| Ability | External stat key | Operation | Value field |
| --- | --- | --- | --- |
| `ShieldProjection` | `shield_bonus_add` | `add` | `value` |
| `ShieldModifier` | `shield_capacity_mult` | `multiply` | `multiplier` |
| `DamageModifier` | `damage_mult` | `multiply` | `multiplier` |
| `ThrustModifier` | `thrust_mult` | `multiply` | `multiplier` |

Adding a combat-projected ability usually requires:

1. Add an `AbilityStatMapping` to `ABILITY_STAT_REGISTRY`.
2. Add the emitted stat key to `KNOWN_EXTERNAL_STAT_KEYS`.
3. Ensure a downstream reader exists: `get_effective_stat()` for ability-level keys, or `ship_stats.py::_apply_aggregated_stats` for ship-level keys.
4. Add source collection or routing where the effect enters battle.

Current routing surfaces:

- Battle Setup complex toggles walk `ABILITY_STAT_REGISTRY` for non-`self` scoped abilities in `game/ui/screens/battle_setup/spec_compiler.py`.
- Strategy sector effects are converted in `game/strategy/combat/strategy_modifier_stack_builder.py::StrategyModifierStackBuilder.entries_from_sector_effects`.
- Fleet-combat aggregate modifiers are represented by `FleetCombatModifiers` and translated by `StrategyModifierStackBuilder.entries_from_fleet_combat_modifiers`.
- Legacy placeholder stat emission is gone. Do not reintroduce placeholder keys or compiler-local duplicate mappings.

Enemy scopes are routed by `OPPONENT_SCOPES = {"enemy_sector", "enemy_system"}`. Adding another enemy scope requires extending that constant and tests.

Useful tests:

- `tests/unit/simulation/combat/test_ability_stat_registry.py`
- `tests/integration/strategy/test_overlapping_storm_combat.py`

## Weapon Family Extension

Adding a weapon variant inside an existing family usually means a new ability data shape or handler logic in the relevant family module. Adding a genuinely new weapon family uses the registry path.

Current files:

| File | Purpose |
| --- | --- |
| `game/simulation/combat/attack_contract.py` | `WeaponFamily`, `AttackRequest`, `BeamResolution`, `ProjectileResolution`, `NoAttack`, `WeaponHandler`, `FAMILY_METADATA` |
| `game/simulation/combat/weapon_registry.py` | `WeaponRegistry`, `WEAPON_REGISTRY`, `detect_family()` |
| `game/simulation/combat/families/` | One handler module per family |

Recipe for a new family:

1. Add a `WeaponFamily` enum member.
2. Add `FAMILY_METADATA` if targeting or context policy differs.
3. Implement a `WeaponHandler.fire(request) -> AttackResolution` module under `game/simulation/combat/families/`.
4. Register the handler with `WEAPON_REGISTRY.register(...)` at module import.
5. Import the module in `game/simulation/combat/families/__init__.py`.
6. Update `detect_family()` only if family detection needs a new component predicate.

Do not add new string-class dispatch branches to `weapon_firing_system.py`, `targeting_system.py`, `collision.py`, or `projectile_manager.py`. The registry exists to keep those central files stable.

Useful test: `tests/unit/simulation/combat/test_weapon_registry.py`.

## Layer And Scope

Abilities declare active game layer and allowed scopes.

```python
from .base import Ability, AbilityLayer, AbilityScope


class MyStrategicAbility(Ability):
    layer = AbilityLayer.STRATEGIC
    allowed_scopes = [AbilityScope.SELF, AbilityScope.ALLIED_SECTOR]
    default_scope = AbilityScope.SELF
```

Layers: `COMBAT`, `STRATEGIC`, `BOTH`.

Scopes: `SELF`, `FLEET`, `SECTOR`, `ALLIED_SECTOR`, `PLAYER_SECTOR`, `ENEMY_SECTOR`, `SYSTEM`, `ALLIED_SYSTEM`, `PLAYER_SYSTEM`, `ENEMY_SYSTEM`, `PLANET`, `EMPIRE`, `ALLIED_EMPIRE`.

Component JSON can override scope:

```json
{
  "abilities": {
    "StrategicMovement": {"value": 100, "scope": "allied_sector"}
  }
}
```

Use spatial terms precisely: a star system is a radius-50 region; a sector is one hex.

## Strategic Ability Extension

Strategic abilities often cross several systems. Add only the surfaces the ability actually needs.

### Activatable Abilities

Activatable component data carries `activation_time` and usually `deactivation_time` plus `energy_drain_rate`.

Current activation flow:

1. `PlanetAbilitiesController.scan_abilities()` in `game/ui/screens/planet_abilities_controller.py` discovers any ability whose data dict carries `activation_time`.
2. `ACTIVATE_ABILITY` / `DEACTIVATE_ABILITY` orders carry `ability_name`, `facility_instance_id`, and `component_key`.
3. `ActionTimeResolver` reads `activation_time` or `deactivation_time` from component ability data.
4. `PlanetActionEngine` writes `ComponentActivationState`.
5. `ComponentActivationEngine` advances activation/deactivation timers.
6. `PlanetEnergyEngine` drains energy from `ComponentActivationState.energy_drain_rate` while states are activating, active, or deactivating.

Display surfaces:

- Add to `ABILITY_DISPLAY_NAME_OVERRIDES` in `planet_abilities_controller.py` only if CamelCase humanization gives the wrong label.
- Add to `_ACTIVATABLE_DISPLAY_NAMES` in `game/ui/screens/strategy_detail_fmt.py` if the planet/system detail panel should show status.
- Add to `game/ui/screens/builder/stat_rows_dynamic.py` if the design workshop needs a dedicated stat row for the ability.

Do not treat `planet_energy_engine._ACTIVATABLE_ABILITIES` as the discovery surface. The current scanner and activation order path are data-driven.

### System And Sector Effect Display

Stale reference correction: `SYSTEM_EFFECT_ABILITIES` no longer lives in `system_effects_collector.py`.

Add new system/sector effect ability metadata in `game/strategy/services/effect_ability_metadata.py` via `EFFECT_ABILITY_METADATA`.

`EffectAbilityMetadata` controls:

- ability name
- display name, or data-derived display name
- kind: `rate` or `multiplier`
- activatable metadata
- grouping field such as `resource_type` or `damage_type`
- owner-aware scopes
- value field and fallback field

`system_effects_collector.py` filters by scope using `_SYSTEM_SCOPES` and `_SECTOR_SCOPES`, then uses the metadata and display helpers. Add tests in `tests/unit/strategy/services/test_effect_ability_metadata.py` and affected collector tests.

### Strategic Combat Effects

If the strategic ability modifies combat stats, make sure both source collection and battle emission are covered:

- `game/strategy/services/combat_modifier_collector.py` collects active facility effects for strategy combat. Activatable effects should use active-state filtering.
- `game/strategy/combat/strategy_modifier_stack_builder.py` emits sector-effect entries into `ModifierStack` for the strategy spec compiler / assembler.
- `game/simulation/combat/ability_stat_registry.py` maps ability name to stat key and operation.

Battle Setup complex toggles already use the same ability-stat registry path for non-self scoped complex abilities.

### Planet Property Editors And Engines

For abilities that modify planet properties:

1. Add or extend the relevant engine, such as `planet_modifier_effect_engine.py`, `water_engine.py`, `atmosphere_engine.py`, or `quality_engine.py`.
2. Add an editor window if the player sets a target value. Follow existing gravity/atmosphere/water/radiation editor patterns.
3. Add `(ability_key, label)` to `ENVIRONMENT_EDITORS` in `game/ui/screens/planet_abilities_controller.py` if it needs a dedicated editor button.
4. Add an `_open_*_editor()` method to `game/ui/screens/strategy_event_router.py`.
5. Wire the editor in `game/ui/screens/strategy_window_manager.py:_open_planet_editor()`.

`ENVIRONMENT_EDITORS` is a closed UI routing list for dedicated environment editor windows, not a behavior gate for all strategic abilities.

## Ship Layers And Ability Access

`LayerType` lives in `game/core/constants.py`.

| Layer | Value | Meaning |
| --- | ---: | --- |
| `HULL` | 0 | innermost chassis layer |
| `CORE` | 1 | bridge, reactors, crew quarters |
| `INNER` | 2 | engines, storage |
| `OUTER` | 3 | shields, sensors, weapons |
| `ARMOR` | 4 | outermost armor layer |

Vehicle-specific layer restrictions come from `data/vehiclelayers.json`, not the enum. Current templates reserve `major_classification: "Armor"` for `LayerType.ARMOR`; non-armor layers use `block_classification:Armor`.

Component ability APIs:

| API | Returns |
| --- | --- |
| `comp.has_ability("Name")` | `bool` |
| `comp.get_ability("Name")` | first matching ability or `None` |
| `comp.get_abilities("Name")` | `list[Ability]` |
| `comp.has_pdc_ability()` | tag-based PDC check |

## File Map

| File | Purpose |
| --- | --- |
| `game/simulation/components/abilities/base.py` | `Ability`, `SimpleMultiplierAbility`, `StaticValueAbility`, layer/scope support |
| `game/simulation/components/abilities/__init__.py` | `ABILITY_REGISTRY`, `create_ability()`, package exports |
| `game/simulation/components/abilities/stat_keys.py` | `StatKey`, `AbilityStatBinding` |
| `game/simulation/components/abilities/ui_colors.py` | UI color hints |
| `game/simulation/components/ability_manager.py` | instantiation, `sync_data()`, MRO-indexed lookup |
| `game/simulation/entities/stat_contributors/registry.py` | ship-stat contribution extension registry |
| `game/simulation/entities/stat_contributors/accumulator.py` | typed `StatAccumulator` |
| `game/simulation/combat/ability_stat_registry.py` | external combat stat projection registry |
| `game/simulation/combat/weapon_registry.py` | weapon family dispatch registry |
| `game/simulation/combat/attack_contract.py` | typed attack request/resolution contract |
| `game/strategy/services/effect_ability_metadata.py` | strategic system/sector effect metadata |
| `game/strategy/services/system_effects_collector.py` | system/sector effect aggregation |
| `game/strategy/services/combat_modifier_collector.py` | strategy combat modifier collection |
| `game/ui/screens/planet_abilities_controller.py` | activation scan and environment editor routing |
| `game/ui/screens/strategy_detail_fmt.py` | detail-panel activatable display names |
| `data/components.json` | component ability declarations |
| `data/vehiclelayers.json` | layer restrictions |

Ability category modules:

- `weapons.py`
- `defense.py`
- `propulsion.py`
- `crew.py`
- `resources.py`
- `markers.py`
- `planetary.py`
- `superweapons.py`
- `colonize.py`
- `harvester.py`
- `cargo.py`

## Tests And Commands

Follow strict TDD: failing test first, implementation second.

Minimum focused coverage:

- Ability class parsing and `_parse_attrs()` refresh, especially formula-driven data.
- `STAT_BINDINGS` and modifier interaction.
- Ship stat contribution if the ability affects derived stats.
- Ability-stat registry mapping if the ability emits battle `ModifierStack` entries.
- Strategic effect metadata and collector behavior if the ability appears in system/sector UI.
- Activation scan and detail display if the ability is activatable.
- Combat Lab scenarios for combat mechanics, especially stacking behavior.

Useful targeted tests:

```bash
pytest tests/unit/simulation/components/test_create_ability_formula_skip.py
pytest tests/unit/simulation/combat/test_ability_stat_registry.py
pytest tests/unit/simulation/combat/test_weapon_registry.py
pytest tests/unit/simulation/entities/stat_contributors/test_registry_pipeline.py
pytest tests/unit/simulation/entities/test_stat_contributor_extension.py
pytest tests/unit/strategy/services/test_effect_ability_metadata.py
pytest tests/unit/ui/screens/test_planet_abilities_controller_scanner.py
python -m combat_lab.run_tests --fast
python Tools/test_sharded/test_sharded.py
```

Use `python -m combat_lab.run_tests <TEST_ID>` for a single Combat Lab scenario.

## Checklist

- [ ] Failing test written or identified and run.
- [ ] Ability class created in the correct `game/simulation/components/abilities/` module.
- [ ] Data-derived attributes parsed in `_parse_attrs()`, not `__init__()`.
- [ ] `STAT_BINDINGS` use valid `StatKey` enum members.
- [ ] Base attributes referenced by bindings are initialized before `recalculate()`.
- [ ] `recalculate()` uses `get_effective_stat()` unless inherited.
- [ ] UI rows use constants from `ui_colors.py`.
- [ ] `get_primary_value()` returns the aggregation value when relevant.
- [ ] Ability registered in `ABILITY_REGISTRY`.
- [ ] Ability added to `__all__`.
- [ ] Component JSON uses the exact registry key.
- [ ] Ship-stat contributor added if derived ship stats need the ability.
- [ ] Ability-stat registry and known external key updated if battle external stats need it.
- [ ] Weapon family registry updated if this is a new family.
- [ ] Strategic effect metadata added if the system/sector UI should aggregate it.
- [ ] Activation, detail display, editor routing, and planet engines updated when applicable.
- [ ] Targeted tests pass.
- [ ] Broader suite or sharded runner used when blast radius warrants it.

## Failure Triage

Ability loads as `None`: verify `ABILITY_REGISTRY` key matches component JSON. If data contains unevaluated formula strings at registry-load time, `None` can be expected until ship-context recalculation.

`SimpleMultiplierAbility` raises at class definition: set `stat_key`, `value_attr`, `base_attr`, and `ui_label`.

`AttributeError` in `recalculate()`: initialize the base attribute named by the binding's `base_attribute`.

Modifiers have no effect: confirm the modifier emits the same `StatKey.value` that `get_effective_stat()` reads and that the ability is recalculated.

Ship stats do not change: add a `STAT_CONTRIBUTOR_REGISTRY` contributor. `STAT_BINDINGS` alone does not aggregate ship-level stats.

External combat modifiers warn or silently do nothing: ensure `ABILITY_STAT_REGISTRY` maps the ability, `KNOWN_EXTERNAL_STAT_KEYS` includes the stat key, and a downstream reader consumes that key.

System or sector effects missing from UI: add `EFFECT_ABILITY_METADATA`; do not add stale `SYSTEM_EFFECT_ABILITIES` constants.

Activatable ability missing from Planet Abilities UI: ensure ability data is a dict carrying `activation_time`, and add only display overrides when the generated label is wrong.

Strategic facility ability not found: use registry-backed component inspection helpers. Facility `design_data` usually stores component IDs, not inline ability dicts.
