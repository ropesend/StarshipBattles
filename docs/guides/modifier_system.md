# Modifier System Compact Reference

> **Last verified:** 2026-05-23 - Updated `ModifierManager.add_modifier()` restriction-enforcement notes to reflect PROJ-489 consolidation (now enforces `allow_types`, `deny_types`, and `allow_abilities` via delegation to `ModifierService`); previously (2026-05-08) compared with the compact alternate and checked live source files.

Modifiers are data-driven stat adjustments. Abilities are behavior classes that consume the adjusted stats.

- Component-born modifiers persist as component state: modifier id plus parameter value.
- Battle-scoped auras flow through `BattleSpec.modifier_stack` and rebuild `ship.external_stats` every battle.
- Strategy production/harvesting scaling can resolve selected modifier effects from design-data entries without materializing a combat component.

## Current Paths

```text
Component-born modifiers
data/modifiers.json
  -> ModifierEffectEvaluator.evaluate_modifier()
  -> list[ModifierEffect]
  -> apply_modifier_effects()
  -> Component.stats / Component.ability_stats
  -> Ability.recalculate()
  -> Ability.get_effective_stat()

Battle-scoped team/global modifiers
spec compiler emits ModifierEntry into ModifierStack
  -> FleetAuraManager.initialize(ships, modifier_stack=stack)
  -> FleetAuraManager._apply_bonuses()
  -> ship.external_stats[stat_key]
  -> Ability.get_effective_stat() for ability-level keys
  -> ShipStatsCalculator._apply_aggregated_stats() for ship-level keys

Strategy design-data size scaling
design component entry with simple_size_mount
  -> game/strategy/services/modifier_resolver.py
  -> resolve_stat_from_size_mount(comp_entry, stat_key, registries)
```

Key invariant: component-born modifier applications persist as id/value pairs; `component.stats` and `component.ability_stats` are component-local runtime state derived from those applications. `ship.external_stats` is battle-scoped composition and must not be serialized as ship state.

## Files

| Path | Role |
|---|---|
| `data/modifiers.json` | Canonical component modifier definitions. `modifiers_v2.json` and v1 backup files are deleted and guarded by tests. |
| `game/simulation/components/modifier_effects.py` | `ModifierEffect`, `ModifierEffectEvaluator`, `ModifierEffect.from_dict()` for replay round-trip. |
| `game/simulation/components/modifiers.py` | `apply_modifier_effects()`, operation stacking, special key mappings, default stat dict. |
| `game/simulation/components/modifier_schema.py` | V2 structural validation. |
| `game/simulation/components/modifier_introspection.py` | UI summaries and tooltips. |
| `game/simulation/components/component_constants.py` | `Modifier` definition object and `ApplicationModifier`. |
| `game/simulation/components/component_stats_calculator.py` | Component recalculation phases and modifier application. |
| `game/simulation/components/modifier_manager.py` | Stateful component modifier list, add/remove/query, effect summaries. |
| `game/simulation/components/abilities/stat_keys.py` | `StatKey`, `AbilityStatBinding`, default stat dictionary source of truth. |
| `game/simulation/components/abilities/base.py` | Ability base class, `STAT_BINDINGS`, `get_effective_stat()`. |
| `game/simulation/combat/modifier_stack.py` | `ModifierEntry`, `ModifierStack`; carried by `BattleSpec`. |
| `game/simulation/combat/fleet_aura_manager.py` | Converts `ModifierStack` entries into `ship.external_stats`. |
| `game/simulation/combat/ability_stat_registry.py` | Shared combat ability class -> external stat key mapping. |
| `game/simulation/entities/ship_stats.py` | Ship-level reads for `shield_bonus_add` and `shield_capacity_mult`. |
| `game/simulation/services/modifier_service.py` | Strict-DI service for UI/application validation, defaults, local min/max. |
| `game/ui/services/component_service.py` | UI-layer facade for component/modifier registry access. |
| `game/ui/screens/builder/modifier_config.py` | Builder UI parameter controls and defaults. |
| `game/strategy/services/modifier_resolver.py` | Strategy-layer size-mount stat resolver. |
| `game/strategy/combat/spec_compiler.py` | Strategy battle public facade (delegates to the assembler). |
| `game/strategy/combat/strategy_modifier_stack_builder.py` | `StrategyModifierStackBuilder` emits the strategy-side `ModifierStack`. |
| `game/ui/screens/battle_setup/spec_compiler.py` | Manual battle setup compiler; emits `ModifierStack`. |

## Modifier Definition

Modifiers use V2 formula definitions in `data/modifiers.json`.

```json
{
  "id": "hardened_mount",
  "name": "Hardened",
  "description": "HP increases as the square of mass multiplier. 2x mass = 4x HP.",
  "param": {
    "name": "Mass Mult",
    "type": "linear",
    "min": 1.0,
    "max": 10.0,
    "default": 1.0
  },
  "effects": [
    {"stat": "mass_mult", "formula": "param"},
    {"stat": "hp_mult", "formula": "param ^ 2"},
    {"stat": "cost_mult", "formula": "param"}
  ],
  "restrictions": {
    "deny_abilities": ["Armor"]
  }
}
```

Effect fields:

- Required by schema: `stat`, `formula`.
- Optional: `operation` (`multiply`, `add`, `add_to_mult`, `set`; default `multiply`), `target_ability`, `depends_on`.
- `target_ability` writes into `component.ability_stats[target_ability]`; untargeted effects write into `component.stats`.

Restrictions caveat: `modifier_schema.py` validates `allow_abilities`, `deny_abilities`, and `require_mode`, but the current runtime service checks only `allow_types`, `deny_types`, and `allow_abilities`. `ModifierManager.add_modifier()` enforces `allow_types`, `deny_types`, AND `allow_abilities` (delegates to `ModifierService.is_modifier_allowed`). Do not assume `deny_abilities` or `require_mode` are enforced without adding tests and implementation.

## ModifierEffect

`ModifierEffect` is the evaluated unit.

```python
@dataclass
class ModifierEffect:
    stat_key: str
    value: float
    operation: str
    target_ability: str | None
    source_modifier_id: str
    source_modifier_name: str
    formula_str: str
    param_value: float
```

Methods:

- `describe() -> str`: display text such as `damage_mult x1.50`.
- `is_targeted() -> bool`: true when `target_ability` is set.
- `to_dict() -> dict`: replay/introspection shape.
- `from_dict(data) -> ModifierEffect`: reconstructs the `to_dict()` form for replay serialization.

## Formula Evaluation

Use `ModifierEffectEvaluator`; do not hand-evaluate formulas.

Supported syntax comes from `FormulaEvaluator.MODIFIER_CONTEXT` plus the safe math namespace:

- `param`
- `param ^ 2` and `2 ^ param` (`^` is translated to power for modifier formulas)
- `1.0 + param * 0.5`
- `1.0 / param`
- `sqrt(param)`, `ln(param)`, `log10(param)`, `abs(param)`
- `min(a, b)`, `max(a, b)`, `round(...)`, and other whitelisted math functions

API:

```python
ModifierEffectEvaluator.evaluate_formula(formula: str, context: dict[str, float]) -> float
ModifierEffectEvaluator.evaluate_modifier(
    mod_def: dict,
    param_value: float,
    stats_context: dict[str, float] | None = None,
) -> list[ModifierEffect]
ModifierEffectEvaluator.validate_formula(formula: str) -> list[str]
ModifierEffectEvaluator.validate_modifier_definition(mod_def: dict) -> list[str]
```

Failure behavior:

- `evaluate_formula()` raises `FormulaException`.
- `evaluate_modifier()` catches `FormulaException`, logs an error, and falls back to the raw `param_value` for that effect.
- `validate_formula()` currently allows only `param` plus safe functions. `evaluate_modifier(..., stats_context=...)` can evaluate formulas that reference prior stats, but loader validation will flag those names unless validation is extended.
- `load_modifiers_data()` logs a warning for schema failures but still loads the modifier when `Modifier(...)` can be constructed.

## Stat Keys

`get_default_stat_multipliers()` delegates to `StatKey.create_default_stats_dict()`. Defaults are:

- Multipliers default to `1.0`: `mass_mult`, `hp_mult`, `damage_mult`, `range_mult`, `cost_mult`, `thrust_mult`, `turn_mult`, `strategic_mult`, `energy_gen_mult`, `capacity_mult`, `shield_capacity_mult`, `crew_capacity_mult`, `life_support_capacity_mult`, `consumption_mult`, `reload_mult`, `endurance_mult`, `projectile_hp_mult`, `projectile_damage_mult`, `crew_req_mult`.
- Additive stats default to `0.0`: `mass_add`, `arc_add`, `accuracy_add`, `projectile_stealth_level`, `shield_bonus_add`.
- Set/override stats default to `None`: `arc_set`.
- `properties` defaults to `{}` for dynamic component properties.

Special mappings in `apply_modifier_effects()`:

- `projectile_stealth_add` with `operation: "add"` maps to internal `projectile_stealth_level`.
- `facing_angle` with `operation: "set"` writes to `stats["properties"]["facing_angle"]`; weapon abilities sync it from component properties.
- Multiplicative and `add_to_mult` global effects are ignored if the target stat is absent or non-numeric.
- Unknown operations log a warning and do not mutate the stat.

Strategy-only size effects currently include `harvest_rate_mult`, `local_storage_mult`, and `production_rate_mult`. They are resolved by `game/strategy/services/modifier_resolver.py`, not by `StatKey` or ability `STAT_BINDINGS`.

## Ability Binding

Abilities consume modifier stats through `STAT_BINDINGS`.

```python
class WeaponAbility(Ability):
    STAT_BINDINGS = [
        AbilityStatBinding(StatKey.DAMAGE_MULT, "damage", "multiply", "_base_damage"),
        AbilityStatBinding(StatKey.RANGE_MULT, "range", "multiply", "_base_range"),
        AbilityStatBinding(StatKey.RELOAD_MULT, "reload_time", "multiply", "_base_reload"),
    ]
```

`Ability.get_effective_stat(stat_key, default)` checks:

1. `component.ability_stats[ability_class_name][stat_key]`
2. `component.stats[stat_key]`
3. `ship.external_stats[stat_key]`, when attached to a ship and the field is a real dict

When both local and external values exist:

- `_mult` keys multiply.
- `_add` keys add.
- Unknown key shapes use the external value as an override.

Current consumers include weapons, shields, propulsion, cargo, resources, crew, and marker capacity. Add a new stat by adding or reusing a `StatKey`, adding `AbilityStatBinding` to the consuming ability, and adding focused tests.

## Stacking

Component-born effects stack inside the accumulated stats dictionary:

- `multiply`: existing value times effect value; missing key becomes effect value.
- `add`: existing value plus effect value; missing key becomes effect value.
- `add_to_mult`: existing value plus effect value; missing key becomes `1.0 + effect value`.
- `set`: overwrite current value.

Targeted effects stack only under `component.ability_stats[target_ability]`. Untargeted effects stack under `component.stats`.

Component recalculation order:

1. Reset/evaluate component and ability formulas.
2. Re-instantiate ability objects from the refreshed ability data.
3. Calculate modifier stats through `apply_modifier_effects()`.
4. Store `component.stats`.
5. Apply mass/HP/cost/properties and call `ability.recalculate()`.

## Battle-Scoped Modifiers

`ModifierStack` is the only current external battle modifier carrier.

```python
@dataclass(frozen=True)
class ModifierEntry:
    source: str
    stack_group: str | None
    effect: ModifierEffect

@dataclass(frozen=True)
class ModifierStack:
    per_team: Mapping[int, tuple[ModifierEntry, ...]]
    global_: tuple[ModifierEntry, ...]
```

`FleetAuraManager.initialize(ships, modifier_stack=stack)` is the current entry point. The legacy `config.team_modifiers` / `config.global_modifiers` branch is gone.

Aggregation rules:

- `per_team[team_id]` applies only to that team.
- `global_` applies to all teams.
- Same `stack_group` takes max; different groups sum.
- `stack_group=None` becomes a unique group, preserving independent contribution.
- `0.0` values are preserved; they can mean a real suppressor such as `damage_mult=0.0`.
- Placeholder entries with empty or `placeholder` stat keys are skipped and logged once per source.
- Unknown external stat keys are logged once per `(stat_key, source)` but still recorded.

Known external stat keys live in `KNOWN_EXTERNAL_STAT_KEYS` in `game/simulation/combat/ability_stat_registry.py`. Compiler-emitted combat abilities currently map through `ABILITY_STAT_REGISTRY`:

- `ShieldProjection` -> `shield_bonus_add` (`add`, `value`)
- `ShieldModifier` -> `shield_capacity_mult` (`multiply`, `multiplier`)
- `DamageModifier` -> `damage_mult` (`multiply`, `multiplier`)
- `ThrustModifier` -> `thrust_mult` (`multiply`, `multiplier`)

Ship-level shield math consumes `(base + shield_bonus_add) * shield_capacity_mult`. Do not read `capacity_mult` for the flat shield bonus path.

## Services and UI

`ModifierService` is strict-DI:

```python
service = ModifierService(modifier_registry=registries.modifiers)
service.is_modifier_allowed("turret_mount", component)
service.ensure_mandatory_modifiers(component)
```

Surface:

- `__init__(modifier_registry: dict[str, Any])`; `None` raises `ValidationException`.
- `is_modifier_allowed(mod_id, component) -> bool`
- `get_mandatory_modifiers(component) -> list`
- `is_modifier_mandatory(mod_id, component) -> bool`
- `get_initial_value(mod_id, component) -> float`
- `ensure_mandatory_modifiers(component) -> None`
- `get_local_min_max(mod_id, component) -> tuple`

Important current behavior:

- `ModifierService.MANDATORY_MODIFIERS` is the single source for the UI ownership constant; do not duplicate it in UI logic.
- `get_mandatory_modifiers()` currently returns every allowed modifier in the registry, not only the four ids in `MANDATORY_MODIFIERS`.
- Special neutral initial values: `simple_size_mount`, `hardened_mount`, and `efficiency_mount` -> `1.0`; `range_mount`, `facing`, and `precision_mount` -> `0.0`.
- Any modifier with an `arc_set` effect defaults to the component base firing arc and clamps local minimum to that base arc.
- `Component.add_modifier()` delegates to `ModifierManager`, which replaces same-id modifiers and recalculates stats. `ModifierManager.add_modifier()` enforces `allow_types`, `deny_types`, AND `allow_abilities` (delegates to `ModifierService.is_modifier_allowed`); `deny_abilities` and `require_mode` are not enforced. Use `ModifierService` or `ComponentService` for UI/application validation of the broader rule set.

`ModifierIntrospection` owns UI summary logic:

```python
ModifierIntrospection.get_modifier_affects(mod_def, component, param_value)
ModifierIntrospection.get_component_modifier_summary(component)
ModifierIntrospection.get_ability_modifier_summary(ability)
ModifierIntrospection.generate_ability_stats_display(ability)
ModifierIntrospection.generate_modifier_tooltip(mod_def, param_value, component)
```

Builder controls live in `MODIFIER_UI_CONFIG`; modifiers not listed use `DEFAULT_CONFIG`.

## Persistence

Component modifiers serialize only application identity and value:

```json
{
  "modifiers": [
    {"id": "hardened_mount", "value": 2.0}
  ]
}
```

On load, component-born effects are re-evaluated from current `data/modifiers.json`.

Do not serialize evaluated component `ModifierEffect` lists as persistent component state. Do not serialize `ship.external_stats` in ship saves or post-battle ship state. Tests inspect `ShipSerializer.to_dict()` to keep `external_stats` out.

Replay serialization is different: `BattleSpec.modifier_stack` is replay data and round-trips through `game/simulation/replay/replay_serialization.py` using `ModifierEffect.to_dict()` / `from_dict()`.

## Extension Recipes

Add a component-born modifier:

1. Add a V2 entry to `data/modifiers.json`.
2. Write the failing test first. Use formula tests for math, snapshot tests for component behavior, and service tests for restriction/default behavior.
3. Use `effects` formulas and validate with `ModifierEffectEvaluator.validate_modifier_definition()` or schema tests.
4. Use `allow_types`, `deny_types`, and `allow_abilities` for currently enforced runtime restrictions. Add implementation/tests before relying on `deny_abilities` or `require_mode`.
5. Add `target_ability` only when the effect must apply to one ability class.
6. Add UI config only when default slider behavior is insufficient.
7. If the modifier affects a new stat, add or confirm `StatKey`, defaults, and `AbilityStatBinding`.
8. If the modifier is strategy-only size scaling, wire/read it through `modifier_resolver.py` rather than pretending it is an ability stat.

Add a new ability-consumed stat:

1. Add a `StatKey` member and confirm `create_default_stats_dict()` default.
2. Add `AbilityStatBinding` on each consuming ability.
3. Add modifier effects using that stat key.
4. Add tests under `tests/unit/modifiers/` and the affected ability/component tests.
5. Verify the ability recalculates via `get_effective_stat()`, not manual stat mutation.

Add a battle-scoped aura/stat:

1. Add or update `ABILITY_STAT_REGISTRY` if emitted by spec compilers.
2. Add the stat key to `KNOWN_EXTERNAL_STAT_KEYS`.
3. Ensure a downstream reader exists: `Ability.get_effective_stat()` for ability-level stats or `ShipStatsCalculator._apply_aggregated_stats()` for ship-level stats.
4. Update both relevant spec compiler paths when needed: strategy and battle setup.
5. Test `ModifierStack -> FleetAuraManager -> external_stats -> reader` end to end.

## Tests and Commands

Targeted tests:

```bash
pytest tests/unit/modifiers/test_modifier_effect_evaluator.py
pytest tests/unit/modifiers/test_formula_validation.py
pytest tests/unit/modifiers/test_modifier_json_schema.py
pytest tests/unit/modifiers/test_multi_ability_effects.py
pytest tests/unit/simulation/services/test_modifier_service.py
pytest tests/unit/simulation/combat/test_fleet_aura_manager_modifier_stack.py
pytest tests/unit/simulation/combat/test_ability_stat_registry.py
pytest tests/unit/simulation/entities/test_ship_external_stats_serialization_guard.py
pytest tests/regression/modifier_ability_snapshots/
pytest tests/unit/strategy/services/test_modifier_resolver.py
```

Broader commands:

```bash
pytest tests/ --testmon
python Tools/test_sharded/test_sharded.py
```

## Invariants

- Simulation code receives registries through DI; do not add global registry lookup inside simulation logic.
- `data/modifiers.json` is the canonical modifier data file.
- Modifier behavior is formula/data driven. Avoid hardcoded ability-name or component-type lists except in shared registries meant to be the source of truth.
- Component-born modifier state persists as id/value pairs, not evaluated effects.
- `ship.external_stats` is transient, reset by `FleetAuraManager.initialize()`, cleared for dead ships, and excluded from ship serialization.
- `ModifierStack` may be serialized as replay spec data; that does not make `external_stats` persistent state.
- Targeted effects write to `component.ability_stats`; untargeted effects write to `component.stats`.
- Abilities consume stats through `STAT_BINDINGS` and `Ability.get_effective_stat()`.
- Formula validation belongs in `ModifierEffectEvaluator` / `modifier_schema.py`.
- UI summaries belong in `ModifierIntrospection`; UI access to registries goes through injected services.
- No save-file migration or compatibility shims for old modifier formats.
