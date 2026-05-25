# Adding Modifiers

> **Last verified:** 2026-05-23 - Updated `ModifierManager.add_modifier()` restriction-enforcement notes to reflect PROJ-489 consolidation (now enforces `allow_types`, `deny_types`, and `allow_abilities` via delegation to `ModifierService`); previously (2026-05-08) rebalanced against the compact alternate and current modifier code paths.

Compact checklist for adding component-born modifiers. For broader architecture, see `docs/guides/modifier_system.md`.

## Source Files

- `data/modifiers.json` - shipped modifier definitions, top-level `"modifiers"` array.
- `game/simulation/components/component_loader.py` - loads modifier data through `load_modifiers_data()` and `validate_modifier_v2()`.
- `game/simulation/components/modifier_schema.py` - V2 schema validation.
- `game/simulation/components/component_constants.py` - `Modifier` and `ApplicationModifier`.
- `game/simulation/components/modifier_effects.py` - `ModifierEffect` and formula evaluation.
- `game/simulation/components/modifiers.py` - effect application and default stat dict.
- `game/simulation/components/abilities/stat_keys.py` - canonical `StatKey` defaults and `AbilityStatBinding`.
- `game/simulation/services/modifier_service.py` - allowed/mandatory modifier service, strict DI.
- `game/ui/screens/builder/modifier_config.py` - optional custom controls.
- `tests/regression/modifier_ability_snapshots/` and `tests/unit/modifiers/` - main regression and contract tests.

## Add a Modifier

1. Write or extend the failing test first. Use a regression snapshot when changing game data behavior, or a unit test when changing schema/evaluation/stat binding behavior.
2. Add the JSON entry to `data/modifiers.json`.
3. Add UI config only if the default slider is wrong.
4. Run the targeted test, then broader modifier tests if the stat or restriction behavior is shared.

Minimal V2 shape:

```json
{
  "id": "your_modifier_id",
  "name": "Display Name",
  "description": "What this modifier does",
  "param": {
    "name": "Slider Label",
    "type": "linear",
    "min": 1.0,
    "max": 10.0,
    "default": 1.0
  },
  "effects": [
    { "stat": "mass_mult", "formula": "param" },
    { "stat": "damage_mult", "formula": "sqrt(param)" }
  ],
  "restrictions": {
    "allow_abilities": ["ProjectileWeaponAbility", "BeamWeaponAbility"]
  }
}
```

Schema requirements:

- Required by `validate_modifier_v2()`: `id`, non-empty `effects`.
- Required per effect: `stat`, `formula`.
- Optional per effect: `operation`, `target_ability`, `depends_on`.
- Optional modifier fields: `name`, `description`, `param`, `restrictions`.
- If `param` is present, it must include `name`, `type`, `min`, `max`, `default`.
- Shipped data should include `name` and `description`; omit `param` only for fixed-value effects.

## Stat Keys

`StatKey` is the default-stat source of truth for component modifier math.

| Type | Keys | Default |
|---|---|---|
| Multipliers | `mass_mult`, `hp_mult`, `damage_mult`, `range_mult`, `cost_mult`, `thrust_mult`, `turn_mult`, `strategic_mult`, `energy_gen_mult`, `capacity_mult`, `shield_capacity_mult`, `crew_capacity_mult`, `life_support_capacity_mult`, `consumption_mult`, `reload_mult`, `endurance_mult`, `projectile_hp_mult`, `projectile_damage_mult`, `crew_req_mult` | `1.0` |
| Additive | `mass_add`, `arc_add`, `accuracy_add`, `projectile_stealth_level`, `shield_bonus_add` | `0.0` |
| Set | `arc_set` | `None` |
| Container | `properties` | `{}` |

Special mappings and warnings:

- Effect stat `projectile_stealth_add` with `operation: "add"` maps to internal `projectile_stealth_level`.
- Effect stat `facing_angle` with `operation: "set"` writes `stats["properties"]["facing_angle"]`; weapon abilities sync from that property.
- `arc_set` sets firing arc. Any modifier with an `arc_set` effect gets neutral initial value and minimum clamping from the component's base firing arc in `ModifierService`.
- `shield_bonus_add` is a real stat key, but it is mainly used by battle-scoped external stats from `ModifierStack`/strategy effects. Do not confuse those auras with component-born entries in `data/modifiers.json`.
- For new global `*_mult` stats, add a `StatKey` default first. `apply_modifier_effects()` guards global `multiply` and `add_to_mult` operations against missing or non-numeric keys.
- A stat only changes an ability if that ability consumes it through `STAT_BINDINGS` or reads it explicitly with `get_effective_stat()`.
- Strategy-only size/scaling stats (`harvest_rate_mult`, `local_storage_mult`, `production_rate_mult`) are resolved by `game/strategy/services/modifier_resolver.py`, not by `StatKey` or ability `STAT_BINDINGS`. Wire them through that resolver rather than treating them as combat ability stats.

## Operations

- `multiply` - multiply an existing value; this is the default operation.
- `add` - add to an additive stat.
- `add_to_mult` - add a contribution to a multiplier stat, for cases like `rapid_fire` mass scaling.
- `set` - overwrite the current value; last set wins.

Unknown operations log a warning and are ignored. Invalid operations should be caught by schema tests before load.

## Formulas

Modifier formulas normally get only `param` plus safe math names:

```text
param
param ^ 2
2 ^ param
1.0 / param
sqrt(param)
ln(param)
log10(param)
abs(param)
min(a, b)
max(a, b)
```

`^` is treated as power only in the modifier formula context. `ModifierEffectEvaluator.evaluate_modifier(..., stats_context=...)` can accept extra variables, and `depends_on` is schema-valid metadata, but the standard `Modifier.evaluate_effects()` path does not populate dependency variables. Do not add stat-referencing formulas unless you also add the runtime path and tests that provide the context.

Validate formulas at minimum/default/maximum values. Watch for inverse formulas at or near zero and exponentials over large slider ranges.

Sanity-check a definition with the evaluator:

```python
errors = ModifierEffectEvaluator.validate_modifier_definition(mod_def)
if errors:
    raise AssertionError(errors)
```

## Restrictions

Restriction fields recognized by the schema:

- `allow_abilities`: list of ability names. Runtime services treat this as any-match.
- `deny_abilities`: schema-valid and present in data.
- `require_mode`: schema-valid as `"any"` or `"all"`.
- `allow_types` / `deny_types`: runtime-supported legacy/type restrictions used by services and manager code.

Current runtime caveat: `ModifierService.is_modifier_allowed()` and `ComponentService.is_modifier_allowed()` enforce `allow_types`, `deny_types`, and `allow_abilities`; `ModifierManager.add_modifier()` enforces `allow_types`, `deny_types`, AND `allow_abilities` (delegates to `ModifierService.is_modifier_allowed`). `deny_abilities` and `require_mode` are schema-valid but are not consistently enforced by the runtime allowance paths. For new modifiers, prefer positive `allow_abilities` restrictions and add tests before relying on ability-deny or all-match behavior.

Ability names must match the keys/classes the component actually carries. Check `data/components.json` and `game/simulation/components/abilities/` before choosing names.

**Namespace warning.** `allow_abilities` keys are matched against the ability-class names that appear as keys inside each component's `abilities` dict (e.g., `CombatPropulsion`, `ResourceGeneration`, `ManeuveringThruster`, `ProjectileWeaponAbility`, `BeamWeaponAbility`, `SeekerWeaponAbility`, `ResourceConsumption`). Using a category label such as `"Engine"`, `"Generator"`, `"Weapon"`, or `"Thruster"` silently matches zero components, because those strings are not real ability keys anywhere in `data/components.json`. The historical `efficient_engines` row carried exactly that bug (see `Projects/active_projects/PROJ-497/decisions.md` for the resolution).

Example of a silent-zero row (anti-pattern — do NOT do this):

```json
{
  "id": "broken_engine_mod",
  "restrictions": {
    "allow_abilities": ["Engine", "Generator", "Thruster"]
  }
}
```

This will pass schema validation and silently match no components; the modifier becomes inert. Always validate against the ability-key namespace before shipping a row, e.g. via a static scan that joins `data/modifiers.json` with `data/components.json` and asserts every restricted row matches at least one component.

## Targeted Effects

Use `target_ability` when one modifier needs different behavior per ability:

```json
{
  "effects": [
    {
      "stat": "damage_mult",
      "formula": "1.5",
      "target_ability": "ProjectileWeaponAbility"
    },
    {
      "stat": "damage_mult",
      "formula": "1.2",
      "target_ability": "BeamWeaponAbility"
    }
  ]
}
```

Targeted effects write to `component.ability_stats[target_ability]`; global `component.stats` is not modified for that effect. The target string must match `ability.__class__.__name__` for `Ability.get_effective_stat()` to see it.

## Current Invariants

- V2 format only: no Python handler table, no `special` handler, no compatibility shim.
- Load uses strict path constants through `Paths.MODIFIERS_FILE`; do not hardcode repo-local absolute paths.
- `load_modifiers_data()` warns on schema validation failure but still attempts to load. Tests are the real gate.
- `ModifierService(modifier_registry=...)` requires an injected registry; no fallback lookup.
- `get_mandatory_modifiers(component)` currently returns every modifier that passes `is_modifier_allowed()`, and `ensure_mandatory_modifiers()` auto-adds missing ones at initial values.
- `ModifierManager.add_modifier()` replaces an existing modifier with the same ID and enforces `allow_types`, `deny_types`, AND `allow_abilities` (delegates to `ModifierService.is_modifier_allowed`).
- Applied modifiers serialize as `{ "id": "...", "value": ... }` and are re-evaluated from current definitions on load. There is no save-file migration policy for old modifier formats.
- Component-born modifier stats persist on `component.stats` / `component.ability_stats`; battle-scoped auras persist only for the battle on `ship.external_stats`.

## Extension Recipes

Add a normal component modifier:

- Add/extend a failing test under `tests/regression/modifier_ability_snapshots/`.
- Add the JSON entry.
- If the effect uses an existing stat key, no Python code is needed.
- If the UI needs custom stepping or a facing selector, add `MODIFIER_UI_CONFIG["your_modifier_id"]` in `game/ui/screens/builder/modifier_config.py`. Modifiers absent from the dict use `DEFAULT_CONFIG` (linear slider, 0.01 step). Minimal stepped-slider shape:

  ```python
  MODIFIER_UI_CONFIG = {
      "your_modifier_id": {
          "control_type": "linear_stepped",
          "slider_step": 0.1,
          "step_buttons": [
              {"label": "<<", "value": 1.0, "mode": "delta_sub"},
              {"label": "<",  "value": 0.1, "mode": "delta_sub"},
              {"label": ">",  "value": 0.1, "mode": "delta_add"},
              {"label": ">>", "value": 1.0, "mode": "delta_add"},
          ],
      },
  }
  ```

Add a new stat key:

- Add the key and default in `game/simulation/components/abilities/stat_keys.py`.
- Add or update `STAT_BINDINGS` on the consuming ability, or add an explicit `get_effective_stat()` read.
- Add unit tests in `tests/unit/modifiers/test_stat_key.py` and the relevant ability binding test.
- Add regression coverage through a real component.

Add a custom formula dependency:

- First test the desired evaluation contract in `tests/unit/modifiers/test_modifier_effect_evaluator.py`.
- Wire the caller to pass `stats_context`; `depends_on` alone is not runtime behavior.
- Add a component-level regression test proving the composed modifier result.

Add or change restriction behavior:

- Test both schema validation and runtime allowance paths.
- Use `tests/unit/simulation/services/test_modifier_service.py` for service behavior.
- Use UI/component tests if the builder selector is affected.
- Do not assume schema-valid fields are enforced everywhere.

## Tests and Commands

Targeted examples:

```bash
pytest tests/unit/modifiers/test_modifier_json_schema.py -k modifier
pytest tests/unit/modifiers/test_modifier_effect_evaluator.py -k formula
pytest tests/unit/modifiers/test_stat_key.py
pytest tests/unit/simulation/services/test_modifier_service.py -k modifier
pytest tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py -k railgun
pytest tests/regression/modifier_ability_snapshots/test_utility_modifiers.py -k modifier
```

Broader checks:

```bash
pytest tests/unit/modifiers tests/unit/simulation/components tests/unit/simulation/services/test_modifier_service.py
python Tools/test_sharded/test_sharded.py
```

## Final Checklist

- Failing test observed before the data/code change.
- `data/modifiers.json` has unique snake_case `id`.
- Effects use valid formula strings and the right operation.
- New global multiplier stats have `StatKey` defaults.
- Consuming ability has `STAT_BINDINGS` or an explicit stat read.
- Restrictions are tested against the runtime path that will enforce them.
- Targeted effects use exact ability class names.
- UI config is present only when default controls are insufficient.
- Relevant modifier tests pass.
