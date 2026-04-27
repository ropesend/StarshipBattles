# PROJ-300: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

---

## Initial Analysis

### How facilities/components contribute sector effects today

- Components in `data/components.json` declare `abilities` blocks like:
  ```json
  "abilities": {
    "ShieldModifier": {"multiplier": 0.75, "scope": "sector", "stack_group": "..."}
  }
  ```
- [`game/strategy/services/system_effects_collector.py:131-163`](../../../game/strategy/services/system_effects_collector.py) — `collect_sector_effects()` walks planets at the hex, walks operational facilities, walks each component's abilities via `extract_abilities_from_component`, filters by `_SECTOR_SCOPES = {sector, allied_sector, player_sector, enemy_sector}` (lines 35-37), groups by `(ability_name, resource_type)`, and aggregates with `aggregate_multipliers()` (two-phase: MAX within `stack_group`, MULTIPLY across groups).
- Returned effect dict shape: `{ability_name, display_name, group_key, status, resource_type, aggregate_value, providers: [{planet_name, facility_name, component_key, status, is_active, value, ability_data}, ...]}`.
- [`game/ui/panels/system_tree_panel.py:397-410`](../../../game/ui/panels/system_tree_panel.py) `_add_sector_effects()` calls the collector and renders effects with collapsible providers under a "Sector Effects (N)" group.
- Recognized sector-effect ability names today: `ShieldModifier, DamageModifier, ResourceHarvestBooster, BuildRateBooster, QualityImprovement` (registered in `SYSTEM_EFFECT_ABILITIES` dict at `system_effects_collector.py:39-48`).

### How storms work today (the parallel system to dissolve)

- [`data/storms.json`](../../../data/storms.json) defines 5 storm types with hardcoded effect fields: `shield_capacity_mult`, `thrust_mult`, `strategic_mult`, `damage_per_tick`, `fuel_drain_per_tick`.
- [`game/strategy/data/storm.py`](../../../game/strategy/data/storm.py) — `Storm` dataclass with `effects: StormEffect` (a 5-field dataclass at lines 16-63).
- [`game/strategy/services/area_effect_manager.py:42-101`](../../../game/strategy/services/area_effect_manager.py) — `AreaEffectManager.get_effects_at_global_hex()` filters zones to `Storm` instances and aggregates: multiplicative fields stack multiplicatively (no MAX phase), additive fields sum. Returns `EnvironmentalEffects` dataclass.
- Three consumers query EnvironmentalEffects:
  1. [`game/strategy/engine/fleet_movement_engine.py:97-133`](../../../game/strategy/engine/fleet_movement_engine.py) `_get_effective_fleet_speed()` — uses `effects.strategic_mult`.
  2. [`game/strategy/engine/conflict_resolution_engine.py:257`](../../../game/strategy/engine/conflict_resolution_engine.py) `_lookup_environmental_effects()` → [`game/strategy/combat/spec_compiler.py:398-428`](../../../game/strategy/combat/spec_compiler.py) `_entries_from_environmental_effects()` — converts `shield_capacity_mult` to a `ModifierEntry` (uses MAX `stack_group="storm_shield_interference"`). Note: `thrust_mult` is currently *unused* downstream.
  3. [`game/strategy/engine/environmental_hazard_engine.py:78-154`](../../../game/strategy/engine/environmental_hazard_engine.py) `process_environmental_tick()` — applies `damage_per_tick / 100.0` and `fuel_drain_per_tick / 100.0` per tick.
- Storms appear in UI only as map decoration + a separate "Storm: X" detail panel via `strategy_detail_fmt.py:get_label_for_object()`. They are NOT in the Sector panel's "Sector Effects" list.

### Aggregation pattern mismatch

- Existing complex aggregation: two-phase MAX→MULTIPLY (intra-group MAX, inter-group MULTIPLY) via `strategic_ability_scanner.aggregate_multipliers()` at lines 102-143.
- Existing storm aggregation: simple multiplicative (no MAX phase) for multipliers, simple SUM for rates.
- `damage_per_tick` and `fuel_drain_per_tick` are **rates** (not multipliers). The existing `aggregate_multipliers()` only handles multipliers — unification needs a rate aggregator too.

---

## Architecture

### `IAbilitySource` Protocol

Lives in `game/core/protocols.py` alongside the existing `IFleet`, `IPlanet`, etc. protocols. Uses `@runtime_checkable` like the rest.

```python
@runtime_checkable
class IAbilitySource(Protocol):
    """Any entity that contributes abilities to the unified ability collector.

    Sources expose their abilities as a {ability_name: ability_data | [data,...]}
    dict matching the components.json shape. Each ability_data dict carries `scope`
    plus multiplier/rate/etc. Sources also describe where they apply via
    `affects_hex` (hex-scoped) and `affects_system` (system-scoped), and provide
    identity for UI rendering.
    """
    @property
    def source_kind(self) -> str: ...
        # 'facility' | 'storm' | 'planet' | 'star' | 'warp_point' | 'system' | 'fleet'
    @property
    def source_label(self) -> str: ...
        # human-readable: "Ion Storm Alpha", "Geologic Stabilizer (Tarsis IV)"
    @property
    def source_id(self) -> str: ...
        # stable unique id for dedup
    @property
    def owner_id(self) -> Optional[int]: ...
        # None = ownerless (storms; later: stars, warp points, system itself)
    def get_abilities(self) -> Dict[str, Any]: ...
    def affects_hex(self, hex_coord) -> bool: ...
    def affects_system(self, system) -> bool: ...
    def get_activation_state(self, ability_name: str) -> Optional[Any]: ...
        # None = always active. Used for activatable abilities on facilities.
```

The protocol is intentionally narrow. Source-kind idiosyncrasies (facility activation states, owner filtering) live inside source-specific *adapters* so the collector remains uniform.

### Source Adapters

In a new `game/strategy/services/ability_sources/` package. Each adapter is a small dataclass implementing `IAbilitySource`. PROJ-300 ships only two; PROJ-301..305 add the rest.

| Adapter (this project) | Wraps | Notes |
|------------------------|-------|-------|
| `FacilityAbilitySource(facility, planet)` | A planetary facility (one source per facility — abilities come from its component layers via `iter_keyed_components`). | Honors `is_operational`, activation state per ability, planet ownership. |
| `StormAbilitySource(storm)` | A `Storm` entity. | `affects_hex(h) = h in storm.occupied_hexes`. `owner_id = None`. `get_activation_state(_) = None` (always active). |

Adapters live in:
- `game/strategy/services/ability_sources/__init__.py` — re-exports.
- `game/strategy/services/ability_sources/facility.py`
- `game/strategy/services/ability_sources/storm.py`

### Unified Iterator

`game/strategy/services/ability_iterator.py` (new):

```python
def iter_ability_sources_at_hex(
    system, hex_coord, *, include_system_sources=True
) -> Iterable[IAbilitySource]:
    """Yield every ability source whose abilities apply to this hex.

    Includes hex-located sources (storms here; planets/warp points/fleets in
    later projects) AND system-scope sources (facilities; later: stars, system
    archetype) when include_system_sources=True. Callers filter further by
    scope via _SECTOR_SCOPES / _SYSTEM_SCOPES.
    """

def iter_ability_sources_in_system(system) -> Iterable[IAbilitySource]:
    """Yield every ability source within a star system, regardless of hex."""
```

In PROJ-300 the iterator visits only facilities and storms. Each later project adds its own discovery branch (planets, stars, warp points, system, fleets). The iterator uses a small **registry of source providers** (`List[Callable[[StarSystem, HexCoord], Iterable[IAbilitySource]]]`) so future projects register their adapters with one line — no central edit needed.

### Collector Refactor

`system_effects_collector.collect_sector_effects` and `collect_system_effects` become thin wrappers over the iterator:

```python
def collect_sector_effects(system, hex_coord, empire_id, registries=None):
    sources = iter_ability_sources_at_hex(system, hex_coord)
    return _aggregate(sources, _SECTOR_SCOPES, empire_id, registries, hex_coord=hex_coord)

def collect_system_effects(system, empire_id, registries=None):
    sources = iter_ability_sources_in_system(system)
    return _aggregate(sources, _SYSTEM_SCOPES, empire_id, registries, hex_coord=None)
```

`_aggregate()` walks each `IAbilitySource`, calls `get_abilities()`, filters entries by scope, applies owner-aware filtering (sources with `owner_id is None` apply to all empires; owned sources only contribute to the matching empire), groups by `(ability_name, resource_type | damage_type)`, and aggregates per-kind.

Two helper functions live in the same module:
```python
def find_sector_effect(effects, ability_name, **filters) -> Optional[dict]
def aggregate_value_or(effects, ability_name, default, **filters) -> float
```

Used by consumers to read aggregated values out of the effect list.

### Aggregation Extensions

In `game/strategy/services/strategic_ability_scanner.py`:

- Keep `aggregate_multipliers(entries)` — intra-group MAX, inter-group MULTIPLY (default 1.0).
- Add `aggregate_rates(entries)` — intra-group MAX, inter-group **SUM** (default 0.0). Rates physically add across distinct phenomena.
- Mixed-kind groups raise `ValidationException`.

### Effect Dict Shape (Extended)

```python
{
    'ability_name': str,
    'display_name': str,
    'group_key': str,
    'status': str,                          # 'Active' | 'Inactive' | 'Activating (N)' | 'Deactivating (N)'
    'resource_type': Optional[str],         # for parameterized abilities (existing)
    'damage_type': Optional[str],           # NEW (for EnvironmentalDamage)
    'kind': 'multiplier' | 'rate',          # NEW
    'aggregate_value': float,               # interpretation depends on kind
    'providers': [
        {
            'source_kind': str,             # 'facility' | 'storm'
            'source_label': str,            # unified display label
            'source_id': str,
            'owner_id': Optional[int],
            'status': str,
            'is_active': bool,
            'value': float,
            'ability_data': dict,
        }
    ]
}
```

Note: legacy provider fields (`planet_name`, `facility_name`, etc.) are removed — replaced by the universal `source_kind`/`source_label`/`source_id`. UI consumers use only the universal fields.

### New Ability Names

Add to `SYSTEM_EFFECT_ABILITIES` in `system_effects_collector.py` and (where combat-relevant) `ABILITY_STAT_REGISTRY` in `game/simulation/combat/ability_stat_registry.py`:

| Storm field today      | New ability name           | Kind        | Stat key                        |
|------------------------|----------------------------|-------------|---------------------------------|
| `shield_capacity_mult` | `ShieldModifier` (existing)| multiplier  | `shield_capacity_mult`          |
| `thrust_mult`          | `ThrustModifier`           | multiplier  | `thrust_mult` (combat-consumed in PROJ-300 — see §Combat Consumption — ThrustModifier; per D14) |
| `strategic_mult`       | `StrategicSpeedModifier`   | multiplier  | n/a (consumed by movement engine) |
| `damage_per_tick`      | `EnvironmentalDamage`      | rate        | n/a (consumed by hazard engine; carries `damage_type` parameter) |
| `fuel_drain_per_tick`  | `FuelDrain`                | rate        | n/a (consumed by hazard engine) |

### Combat Consumption — ThrustModifier

Per decisions.md D14, `ThrustModifier` is wired end-to-end in this project (no dead data flow). Two changes:

1. **`spec_compiler._entries_from_sector_effects`** emits a `ThrustModifier` entry per provider, mirroring `ShieldModifier` (no shared `stack_group` — overlapping storms multiply naturally).
2. **Combat propulsion stat aggregation** — `game/simulation/combat/ability_stat_registry.py` registers `thrust_mult` so the ship-stats consumer in `game/simulation/entities/ship_combat_engine.py` (or wherever combat propulsion stats are aggregated; confirm in Phase 1 audit) multiplies a ship's effective thrust by the aggregated `thrust_mult` from external modifiers. Symmetrical with `shield_capacity_mult` consumption today.

**Tests** (Phase 6 — alongside the storm-stacking balance test):
- Single storm with `ThrustModifier 0.6` → ship at hex applies `thrust × 0.6` in combat.
- Two overlapping storms with `ThrustModifier 0.6` each → `thrust × 0.36` (multiplicative; matches D6 storm stacking).
- Mix of facility-projected + storm-projected `ThrustModifier` → multiplicative across providers.

### Shared Helpers (used by PROJ-301..304)

Per decisions.md D15, two helpers ship in PROJ-300 so the four sibling projects are pure consumers:

```python
# game/strategy/services/ability_sources/intrinsic_roll.py

def roll_intrinsic_abilities(
    template: Dict[str, Any],
    *,
    rng: random.Random,
) -> Dict[str, Any]:
    """Materialize an instance abilities dict from a registry template.

    For each ability in `template`, copies the ability data verbatim except:
    - any field with shape `{"min": x, "max": y}` is rolled to a scalar via
      `rng.uniform(x, y)` for floats or `rng.randint(x, y)` for ints (decided
      by the values' types).
    - `damage_type`, `scope`, `stack_group`, and other string fields pass through.

    Returns a dict in the same shape as a `Storm.abilities` / facility component
    abilities — ready to drop onto the entity instance and feed to the iterator.
    """

# game/strategy/services/ability_sources/labels.py

def format_intrinsic_source_label(
    *,
    entity_name: str,
    type_name: str,
) -> str:
    """Canonical label for intrinsic ability sources used by PROJ-301..304.

    Format: `"{entity_name} ({type_name})"` — e.g. "Tarsis IV (volcanic)",
    "Sol (G-class)", "Warp Point Alpha (unstable)".

    Adapters with no `entity_name` (system archetypes — the system itself)
    use the system's display name.
    """
```

These are tested in PROJ-300 Phase 3 alongside the protocol/iterator. PROJ-301..304 import and use them; they do NOT reimplement the roll logic or the label format.

### Storm Data Model — `data/storm_types.json` v2.0

```json
{
  "version": "2.0",
  "description": "Storm type definitions. Storms are sector-scope ability sources.",
  "storm_types": {
    "ion_storm": {
      "name": "Ion Storm",
      "description": "Electromagnetic disturbance that disrupts shields and sensors.",
      "size": {"min": 2, "max": 5},
      "image_variants": [1, 2, 3],
      "abilities": {
        "ShieldModifier":         {"multiplier": 0.5, "scope": "sector"},
        "StrategicSpeedModifier": {"multiplier": 0.8, "scope": "sector"}
      }
    },
    "plasma_storm": {
      "name": "Plasma Storm",
      "description": "Superheated plasma ejected from stellar activity.",
      "size": {"min": 3, "max": 7},
      "image_variants": [2, 4, 6],
      "abilities": {
        "ShieldModifier":      {"multiplier": 0.7, "scope": "sector"},
        "EnvironmentalDamage": {"rate": 0.5, "damage_type": "plasma", "scope": "sector"}
      }
    },
    "gravitational_anomaly": {
      "name": "Gravitational Anomaly",
      "description": "Spacetime distortion causing thrust inefficiency.",
      "size": {"min": 2, "max": 4},
      "image_variants": [3, 5],
      "abilities": {
        "ThrustModifier":         {"multiplier": 0.6, "scope": "sector"},
        "StrategicSpeedModifier": {"multiplier": 0.5, "scope": "sector"}
      }
    },
    "radiation_belt": {
      "name": "Radiation Belt",
      "description": "Intense radiation zone causing gradual hull damage.",
      "size": {"min": 4, "max": 10},
      "image_variants": [1, 4, 5],
      "abilities": {
        "EnvironmentalDamage": {"rate": 0.8, "damage_type": "radiation", "scope": "sector"},
        "FuelDrain":           {"rate": 0.1, "scope": "sector"}
      }
    },
    "dark_nebula": {
      "name": "Dark Nebula",
      "description": "Dense gas cloud that slows travel but provides cover.",
      "size": {"min": 5, "max": 10},
      "image_variants": [2, 3, 6],
      "abilities": {
        "StrategicSpeedModifier": {"multiplier": 0.4, "scope": "sector"},
        "ThrustModifier":         {"multiplier": 0.8, "scope": "sector"}
      }
    }
  }
}
```

Notes:
- Multipliers use `multiplier` (matches existing components).
- Rates use `rate` (new convention).
- `scope: "sector"` is mandatory; storms have no system-scope abilities.
- **No `stack_group`** on storm abilities — per [decisions.md](decisions.md), overlapping storms MULTIPLY (preserves current behavior). Each storm is its own ungrouped provider in the aggregator.

### `Storm` Dataclass — Drop `StormEffect`

`game/strategy/data/storm.py`: replace `effects: StormEffect` with `abilities: Dict[str, Any]` (a plain dict matching the components.json `abilities` shape). `to_dict`/`from_dict` carry the dict through verbatim.

`StormGenerator` in `game/strategy/generation/storm_generator.py` reads the new `storm_types.json` and copies the `abilities` dict from the type template into each generated `Storm` instance. Future generation-time rolls (e.g. randomizing `multiplier` within a min/max range) are added in PROJ-301..304 when those source kinds need it.

### Consumer Rewrites

All three legacy consumers query `collect_sector_effects` directly. `EnvironmentalEffects` and `AreaEffectManager` are deleted.

**`fleet_movement_engine.py`** — `_get_effective_fleet_speed`:
```python
effects = collect_sector_effects(system, fleet.location, empire_id=fleet.owner_id, registries=registries)
mult = aggregate_value_or(effects, 'StrategicSpeedModifier', 1.0)
return max(0, int(base_speed * mult))
```
Drop `area_effect_manager` constructor arg.

**`spec_compiler.py`** — replace `_entries_from_environmental_effects` with `_entries_from_sector_effects(sector_effects)`. Walks the effects list; for each combat-relevant ability (`ShieldModifier`, `DamageModifier`, future `ThrustModifier`), calls `emit_entries_for_ability` **per provider** so storms multiply naturally. `build_strategy_battle_spec` parameter `environmental_effects: Any` → `sector_effects: Sequence[dict]`.

**`conflict_resolution_engine.py`** — `_lookup_environmental_effects` → `_lookup_sector_effects`; calls collector.

**`environmental_hazard_engine.py`** — `process_environmental_tick`:
```python
effects = collect_sector_effects(system, fleet.location, empire_id=None, registries=registries)
damage_per_turn = sum(e['aggregate_value'] for e in effects if e['ability_name'] == 'EnvironmentalDamage')
fuel_per_turn   = sum(e['aggregate_value'] for e in effects if e['ability_name'] == 'FuelDrain')
damage_per_tick = damage_per_turn / 100.0   # /100 conversion stays here
fuel_per_tick   = fuel_per_turn   / 100.0
```

The "in_storm" branch becomes "any environmental damage or fuel drain at this hex" — opens the door to facility-projected hazards naturally. (Per decisions.md: facility components MAY project these.)

### What Gets Deleted

- `game/strategy/services/area_effect_manager.py` — entire file (`AreaEffectManager` + `EnvironmentalEffects`).
- `tests/unit/strategy/services/test_area_effect_manager.py` — entire file.
- `StormEffect` dataclass in `game/strategy/data/storm.py`.
- `_entries_from_environmental_effects` in `game/strategy/combat/spec_compiler.py`.
- `area_effect_manager` constructor params, factories, and DI wiring throughout (search `game/context.py` and the strategy session facade).
- `IEnvironmentalHazardEngine`-style references to `AreaEffectManager` (none confirmed; verify during Phase 7).

Old saves are disposable per CLAUDE.md System Migration Policy.

### UI Integration

[`game/ui/panels/system_tree_panel.py`](../../../game/ui/panels/system_tree_panel.py) `_add_sector_effects` already calls the collector — storm effects appear automatically once the iterator includes them. Two changes:

1. `_add_effects_group` rendering uses `provider['source_label']` (new unified field) instead of building `f"{facility_name} ({planet_name})"` directly.
2. `_format_effect_value` adds rate-style formatting: `EnvironmentalDamage` displays as `"-{value:.1f}/turn"`, `FuelDrain` as `"-{value:.1f} fuel/turn"`. Drives off the new `effect['kind'] == 'rate'`.

[`game/ui/screens/strategy_detail_formatter.py`](../../../game/ui/screens/strategy_detail_formatter.py) `_format_storm`: strip the per-effect breakdown; keep storm name, type, description, size in hexes only. Effects show in the Sector Effects list (per decisions.md).

---

## Swarm Findings Summary

This project's design was developed via three parallel Explore agents (storm internals, facility/component sector-effects flow, sector panel UI rendering) and one Plan agent. Findings are summarized below; the master plan in [`~/.claude/plans/i-want-you-to-typed-squid.md`](../../../../../Users/rossr/.claude/plans/i-want-you-to-typed-squid.md) carries the full investigation.

### Architecture
- Two parallel "things at a hex project effects" pipelines exist; framework consolidation produces one path with adapter polymorphism.
- The facility pipeline already implements all the patterns we want (scope filtering, two-phase aggregation, provider-grouped UI). The job is generalizing it to admit storms (and future PROJ-301..305 source kinds).

### Key Patterns to Reuse
- **Layered ability extraction**: `iter_keyed_components` in `game/core/patterns/layer_iterator.py` and `extract_abilities_from_component` in `game/strategy/services/component_inspector.py` — works on any component-shaped data.
- **Two-phase aggregation**: `aggregate_multipliers` in `game/strategy/services/strategic_ability_scanner.py:102-143` — extends naturally with a parallel `aggregate_rates`.
- **ABILITY_STAT_REGISTRY**: existing registry in `game/simulation/combat/ability_stat_registry.py` provides ability-name → stat-key mapping with `emit_entries_for_ability` helper. Reuse for combat-side modifier emission.
- **TypeGuard + Protocol** (`game/core/protocols.py`): pattern to follow for `IAbilitySource`. Already used by `IStorm`, `IFleet`, etc.
- **Spatial zone index**: `Galaxy._global_hex_zones` (`get_zones_at_global_hex`) for storm-at-hex lookup. Continue to use for storm discovery in `iter_ability_sources_at_hex`.

### Dependencies & Risks
1. **Combat shield interference behavior change** — Today's `stack_group="storm_shield_interference"` MAX-groups overlapping storms in combat. Per decisions.md, the new design MULTIPLIES (storms ungrouped). Two ion storms drop from `MAX(0.5, 0.5) = 0.5` to `0.5 * 0.5 = 0.25`. Document; expected user-visible effect on combat balance.
2. **Save format breaks** — `StormEffect` serialization is replaced by `abilities` dict serialization. Old saves are not migrated (per CLAUDE.md). Ensure new save/load roundtrip tests cover the new shape.
3. **DI surgery** — `AreaEffectManager` likely wired into `ApplicationContext` and the strategy session facade. Phase 7 must hunt down every reference. Use `grep -r "AreaEffectManager"`.
4. **Adapter package layering** — Adapters live in `game/strategy/services/`. They import from `game/strategy/data/` (Storm) and `game/core/protocols.py` (IAbilitySource). No upward dependency violations.
5. **Empire scoping for storms** — Storms apply regardless of ownership (`owner_id = None`). Ensure `_aggregate` semantics: `owner_id = None` source → applies to all empire-scoped queries; consumers calling with `empire_id=None` skip planet-owned sources cleanly.

### Opportunities Discovered
- **Future ability projection from facilities**: e.g. an offensive "Plasma Projector" complex with `EnvironmentalDamage scope: enemy_sector`. The unified pipeline supports this naturally — no new code needed once PROJ-300 lands.
- **Cleaner combat path**: Today's spec compiler hardcodes `stack_group="storm_shield_interference"` (line 425). After PROJ-300, the `stack_group` propagates from the ability data — the compiler is data-driven.
- **Performance lever**: Once the iterator is the choke point, per-turn caching of `(hex, empire_id) → effects` becomes a single-place optimization. Defer until measured.

---

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
