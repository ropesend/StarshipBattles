# QS Complex Design - Compact Agent Reference

> **Last verified:** 2026-05-08 - Balanced from `docs/guides/qs_complex_design.md`, `AgentCoordination/Scratchpad/reports/guides_qs_complex_design_ALT_compact.md`, and current QS design/code paths.

Compact reference for shipped Quickstart planetary complex designs. For component ability details, use `docs/systems/ability_reference.md`; for production behavior, use `docs/systems/production_system.md`. Do not read `docs/_ignore/`.

## Purpose

QS complexes are shipped JSON design files for planetary facilities. They are not a separate component model, protocol, or runtime base class. The discriminator is:

```json
"vehicle_type": "Planetary Complex"
```

At runtime, a design becomes a `PlanetaryFacility` on a planet. Stat calculation and validation use the normal component, modifier, ability, registry, and `Ship.from_dict(..., registries=...)` pipeline.

## Source Files

| Path | Use |
|---|---|
| `data/designs/qs_*.json` | Shipped QS designs, including complexes and non-complex starter ships |
| `data/components.json` | Component IDs, ability payloads, costs, and `allowed_vehicle_types` |
| `data/modifiers.json` | Modifier IDs used by design component entries |
| `data/design_roles.json` | Role IDs and vehicle-type filters used by design browsing/filtering |
| `data/vehicleclasses.json` | `ship_class` definitions, max mass, hull ID, and layer config |
| `data/vehiclelayers.json` | Layer availability, max layer percentages, and placement restrictions |
| `game/strategy/quickstart_builder.py` | `INITIAL_COMPLEXES`, design copying, homeworld starter spawning |
| `game/strategy/data/planetary_facility.py` | Runtime facility data model, activation state, fuel storage helpers |
| `game/strategy/systems/design_catalog.py` | In-memory per-empire design lookup + UI surface (`search_designs`, `filter_designs`, `save_design` orchestrator) |
| `game/strategy/systems/design_repository.py` | Disk-bound filesystem + JSON persistence; owns `DesignLoadResult` |
| `game/strategy/engine/production_spawner.py` | Facility creation after colony/fleet construction completion |
| `game/strategy/services/component_inspector.py` | Canonical registry-backed ability inspection for design data |
| `game/strategy/services/strategic_ability_scanner.py` | Scoped strategic ability queries and multiplier/rate aggregation |
| `game/strategy/services/system_effects_collector.py` | UI-facing sector/system effect aggregation |

## Runtime Contracts

- `ShipSerializer.from_dict(data, registries=...)` requires registries. Do not rely on global registry lookup from simulation code.
- `PlanetaryFacility` stores the full design dict in `design_data`; component entries normally contain only `id` and `modifiers`.
- Ability checks against facilities must resolve component IDs through the component registry. Directly checking `comp.get("abilities", {})` misses registry-defined abilities in real design files.
- `expected_stats` is a verification snapshot. Loading recalculates stats and logs mismatches; tests and `Tools/validate_designs` also compare against it.
- `vehicle_type` must be exactly `"Planetary Complex"` for complex designs. QS ships and drop pods may share the file shape but are not complexes.
- `ship_class` must match a key in `data/vehicleclasses.json`. For complexes, current classes are `Planetary Complex (Tier 1)` through `Planetary Complex (Tier 11)`.

## Infrastructure

Every functional complex needs these in `layers.CORE`:

| Component ID | Purpose |
|---|---|
| `central_complex_command` | Provides `CommandAndControl`; required for operation |
| `crew_quarters` | Provides `CrewCapacity`; total capacity must cover crew need |
| `life_support` | Provides `LifeSupportCapacity`; total capacity must cover crew need |

Specialized purpose components normally go in `OUTER`. Use `INNER` only when protected placement is intentional. Current `Planetary_Complex` layer rules block Armor classification from `CORE`, `INNER`, and `OUTER`; armor components belong in `ARMOR`.

## JSON Skeleton

Create complex designs at `data/designs/qs_<name>.json`.

```json
{
  "name": "QS My Complex",
  "ship_class": "Planetary Complex (Tier 1)",
  "vehicle_type": "Planetary Complex",
  "theme_id": "Federation",
  "team_id": 0,
  "color": [100, 100, 255],
  "movement_policy": "kite_max",
  "targeting_policy": "standard",
  "design_role": "resource_harvester",
  "layers": {
    "CORE": [
      {
        "id": "central_complex_command",
        "modifiers": [
          {"id": "simple_size_mount", "value": 1.0},
          {"id": "hardened_mount", "value": 1.0},
          {"id": "automation", "value": 0.0}
        ]
      },
      {
        "id": "crew_quarters",
        "modifiers": [
          {"id": "simple_size_mount", "value": 1.0},
          {"id": "hardened_mount", "value": 1.0}
        ]
      },
      {
        "id": "life_support",
        "modifiers": [
          {"id": "simple_size_mount", "value": 1.0},
          {"id": "hardened_mount", "value": 1.0}
        ]
      }
    ],
    "INNER": [],
    "OUTER": [
      {
        "id": "your_specialized_component",
        "modifiers": [
          {"id": "simple_size_mount", "value": 1.0},
          {"id": "hardened_mount", "value": 1.0}
        ]
      }
    ],
    "ARMOR": []
  },
  "resources": {
    "fuel": 0.0,
    "energy": 0.0,
    "ammo": 0.0
  },
  "expected_stats": {
    "max_hp": 0,
    "mass": 0,
    "resource_storage": {},
    "cargo_storage": {},
    "pod_storage_mass": 0.0,
    "resource_consumption_per_hex": {},
    "resource_consumption_per_turn": {},
    "warp_resource_costs": {},
    "strategic_movement": 0,
    "warp_max_tonnage": 0,
    "max_speed": 0,
    "acceleration_rate": 0.0,
    "turn_speed": 0.0,
    "total_thrust": 0
  },
  "_metadata": {
    "is_obsolete": false,
    "times_built": 0
  }
}
```

## Field Rules

Current quickstart tests require `name`, `ship_class`, `vehicle_type`, `layers`, `expected_stats.max_hp`, `expected_stats.mass`, and `_metadata.is_obsolete` / `_metadata.times_built`.

Use these standard QS fields for all new complex designs:

| Field | Rule |
|---|---|
| `name` | Display name |
| `ship_class` | Must match a `data/vehicleclasses.json` key, e.g. `"Planetary Complex (Tier 2)"` |
| `vehicle_type` | Must be `"Planetary Complex"` |
| `theme_id` | Visual theme, commonly `"Federation"` |
| `team_id` | Default team, commonly `0` |
| `color` | RGB array |
| `movement_policy` | Complexes commonly use `"kite_max"` |
| `targeting_policy` | Complexes commonly use `"standard"` |
| `design_role` | Strongly recommended. Loader defaults to `"general_purpose"` when omitted, but that is usually wrong for complexes. Use a role whose `vehicle_type_filter` allows `"Planetary Complex"` |
| `layers` | Include `CORE`, `INNER`, `OUTER`, and `ARMOR` keys; empty layer arrays are allowed |
| `resources` | Initial consumable levels; include `fuel`, `energy`, and `ammo` for QS consistency |
| `expected_stats` | Cached verification data. Keep at least `max_hp` and `mass` accurate |
| `_metadata` | Required by QS tests for shipped designs |

Common complex roles: `resource_harvester`, `production_facility`, `planetary_modifier`, `stellar_protector`, `enrichment_facility`, `resupply_depot`, `construction_accelerator`, `defensive_platform`, `research_facility`.

## Component Entry Rules

Layer entries reference component IDs from `data/components.json`:

```json
{
  "id": "component_id_from_components_json",
  "modifiers": [
    {"id": "modifier_id", "value": 1.0}
  ]
}
```

Rules:

- Every referenced component must exist in `data/components.json`.
- Every component used by a complex must include `"Planetary Complex"` in `allowed_vehicle_types`.
- Do not inline production abilities in shipped design files. Inline ability payloads are supported by helpers for tests/mocks, but real designs should use registry component definitions.
- Use `data/vehiclelayers.json` restrictions. Do not hardcode component type, classification, or ability name lists in code.
- `Component.add_modifier` can trigger formula evaluation. When constructing loaded components, attach the component to its ship before applying modifiers so `ship_class_mass` formulas resolve against the correct class.

Common modifiers:

| Modifier | Effect |
|---|---|
| `simple_size_mount` | Scales component size/output; `1.0` means normal |
| `hardened_mount` | Increases HP at mass cost; `1.0` means normal |
| `automation` | Reduces crew requirement; `0.0` means no automation |

## Tiers And Mass

Stale correction: older guide text said tiers were informational only. Current code treats the full `ship_class` string as a vehicle class key, so each complex tier has a real mass budget and hull definition in `data/vehicleclasses.json`.

| Class | Max Mass | Layer Config |
|---|---:|---|
| `Planetary Complex (Tier 1)` | 1,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 2)` | 2,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 3)` | 4,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 4)` | 8,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 5)` | 16,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 6)` | 32,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 7)` | 64,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 8)` | 128,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 9)` | 256,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 10)` | 512,000 | `Planetary_Complex` |
| `Planetary Complex (Tier 11)` | 1,024,000 | `Planetary_Complex` |

The tier number is still not parsed separately by QS code; the mechanical contract is the complete `ship_class` lookup.

## Strategic Ability Families

Complexes commonly use these component ability families. See `game/simulation/components/abilities/planetary.py` and `docs/systems/ability_reference.md` for exact fields.

| Ability | Typical complex use |
|---|---|
| `SpaceShipyard` / `PlanetaryYard` | Build queues and construction sources |
| `ResourceHarvester` / `LocalStorage` / `StagingYard` | Planetary harvesting and storage |
| `ResourceGeneration` | Facility fuel generation/resupply |
| `ResourceStorage` | Facility fuel/energy/ammo capacity |
| `StrategicResourceGeneration` | Per-turn strategy energy/resource generation |
| `PlanetaryShield` | Activatable planetary defense and energy drain |
| `GeologicStabilizer`, `StellarStabilizer`, `WarpFieldStabilizer` | Superweapon blocking |
| `ResourceHarvestBooster`, `BuildRateBooster` | Scoped harvest/build multipliers |
| `ShieldModifier`, `DamageModifier` | Scoped combat modifiers |
| `AtmosphereModifier`, `WaterModifier`, `GravityModifier`, `RadiationShield` | Terraforming/environment effects |
| `QualityImprovement` | Permanent resource quality improvements |

Scope warning: "system" means the whole star system region; "sector" means one hex. Pick the component ability scope deliberately (`sector`, `system`, `allied_sector`, `enemy_system`, etc.) and test the exact scope. A fleet or planet being in the same system is not the same as being at the target sector.

## Current Initial Complexes

`game/strategy/quickstart_builder.py:INITIAL_COMPLEXES` spawns these on every empire homeworld:

| Design ID | Class | Purpose |
|---|---|---|
| `qs_complex` | Tier 2 | Shipyard / ship construction |
| `qs_metals_complex` | Tier 2 | Metals harvesting |
| `qs_organics_complex` | Tier 2 | Organics harvesting |
| `qs_vapors_complex` | Tier 2 | Vapors harvesting |
| `qs_radioactives_complex` | Tier 2 | Radioactives harvesting |
| `qs_exotics_complex` | Tier 2 | Exotics harvesting |
| `qs_resupply_depot` | Tier 1 | Fuel synthesis and storage |
| `qs_geologic_stabilizer_complex` | Tier 1 | Geologic stabilizer plus energy |

## Other Current Complex Designs

Player-built or non-initial QS complex designs currently include:

| Design ID | Class | Purpose |
|---|---|---|
| `qs_atmosphere_processor_complex` | Tier 1 | Atmosphere terraforming |
| `qs_enrichment_complex` | Tier 3 | Resource quality improvement |
| `qs_stellar_stabilizer_complex` | Tier 2 | Stellar destruction protection |
| `qs_warp_stabilizer_complex` | Tier 2 | Warp point manipulation protection |
| `qs_system_geologic_stabilizer_complex` | Tier 2 | System-scope geologic protection |
| `qs_sector_construction_accelerator_complex` | Tier 1 | Sector build-rate boost |
| `qs_system_construction_accelerator_complex` | Tier 2 | System build-rate boost |
| `qs_sector_shield_projector_complex` | Tier 1 | Sector shield projection |
| `qs_system_shield_projector_complex` | Tier 2 | System shield projection |
| `qs_sector_shield_booster_complex` | Tier 1 | Sector allied shield boost |
| `qs_system_shield_booster_complex` | Tier 2 | System allied shield boost |
| `qs_sector_shield_suppressor_complex` | Tier 1 | Sector enemy shield suppression |
| `qs_system_shield_suppressor_complex` | Tier 2 | System enemy shield suppression |
| `qs_sector_damage_booster_complex` | Tier 1 | Sector allied damage boost |
| `qs_system_damage_booster_complex` | Tier 2 | System allied damage boost |
| `qs_sector_damage_suppressor_complex` | Tier 1 | Sector enemy damage suppression |
| `qs_system_damage_suppressor_complex` | Tier 2 | System enemy damage suppression |
| `qs_gravity_modifier_complex` | Tier 1 | Planet gravity modification |
| `qs_water_modifier_complex` | Tier 1 | Water terraforming |
| `qs_radiation_shield_complex` | Tier 1 | Planet radiation shielding |

## Non-Complex QS Designs

`data/designs/` also contains QS ships, drop pods, and superweapon platforms. They share the design-file shape but are not QS complexes unless `vehicle_type` is `"Planetary Complex"`.

Current non-complex QS files include:

`qs_battleship`, `qs_cargo_freighter`, `qs_carrier`, `qs_colony_drop_pod`, `qs_colony_ship`, `qs_escort`, `qs_frigate_gc`, `qs_general_purpose`, `qs_heavy_cruiser`, `qs_light_combat_escort`, `qs_missile_cruiser`, `qs_planet_destroyer`, `qs_recon_picket`, `qs_sphere_builder`, `qs_star_destroyer`, `qs_warp_gate_closer`, `qs_warp_gate_opener`.

## Add Or Extend A Complex

Follow strict TDD for any behavior change: write or identify the failing test first, run it, then implement. For pure data/docs changes, use the validation command before broad tests.

1. Start from an existing complex in `data/designs/`.
2. Keep `central_complex_command`, enough `crew_quarters`, and enough `life_support` in `CORE`.
3. Add specialized component IDs in `OUTER` unless the protection/placement reason points to another layer.
4. Confirm each specialized component exists in `data/components.json` and allows `"Planetary Complex"`.
5. Confirm component placement fits `data/vehiclelayers.json`.
6. Pick a `ship_class` whose mass budget covers the calculated design mass.
7. Set `design_role` to a role in `data/design_roles.json` that allows `"Planetary Complex"`.
8. Recalculate/update `expected_stats`, at least `max_hp` and `mass`.
9. If the complex should spawn on every homeworld, add its design ID to `INITIAL_COMPLEXES` in `game/strategy/quickstart_builder.py` and test quickstart spawning.
10. If adding a new ability type, update `docs/systems/ability_reference.md` and ability tests.
11. If adding strategy behavior, update the relevant strategy/system docs and the targeted engine/service tests.

## Validation And Tests

Design validation:

```bash
python Tools/validate_designs/validate_designs.py
python Tools/validate_designs/validate_designs.py data/designs/
```

The validator checks component existence, crew housing, life support, layer mass budgets, and `expected_stats.mass` consistency within 0.5.

Targeted test commands:

```bash
pytest tests/unit/quickstart/test_quickstart_designs.py
pytest tests/unit/quickstart/test_quickstart_builder.py
pytest tests/integration/quickstart/test_quickstart_flow.py
```

Use additional focused tests based on behavior touched:

| Change Area | Useful tests |
|---|---|
| Component ability parsing/lookup | `pytest tests/unit/strategy/test_component_inspector.py` |
| Planetary ability classes | `pytest tests/unit/simulation/components/abilities/test_planetary_abilities.py` |
| Activatable facilities/shields/stabilizers | `pytest tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/strategy/engine/test_planet_energy_engine.py` |
| Terraforming modifiers | `pytest tests/unit/strategy/engine/test_atmosphere_engine.py tests/unit/strategy/engine/test_water_engine.py tests/unit/strategy/engine/test_planet_modifier_effect_engine.py` |
| Harvest/build boosters | `pytest tests/unit/strategy/engine/test_harvesting_engine.py` plus production tests near the touched code |
| Combat sector/system effects | `pytest tests/unit/strategy/combat/test_spec_compiler.py tests/integration/strategy/combat/test_suppressor_effects.py` |
| Facility spawning/production | `pytest tests/unit/strategy/engine/test_production_spawner.py tests/unit/strategy/engine/test_production_spawner_staging_yard.py` |

Run the sharded suite when the change touches shared loading, registries, component stats, strategy turn processing, production, or combat effect routing:

```bash
python Tools/test_sharded/test_sharded.py
```

## Warnings

- Do not create compatibility shims for old save/design shapes. Old saves are disposable.
- Do not read `docs/_ignore/`.
- Do not hardcode absolute checkout paths in docs, tooling, skills, or examples.
- Do not duplicate ability scanning logic. Use `component_inspector`, `strategic_ability_scanner`, `ability_iterator`, or `system_effects_collector` depending on scope.
- Do not assume `design_role` is enforced by all loaders. It is optional at load time but should be present on new shipped designs so UI filters and classification stay useful.
- Do not treat complex tier as flavor text. The selected `ship_class` controls vehicle class mass budget and hull.
