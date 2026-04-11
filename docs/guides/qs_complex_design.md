# QS Complex Design Guide

> How to create and manage Quickstart (QS) planetary complex designs.
> For component abilities, see [ability_reference.md](../systems/ability_reference.md).
> For the production system, see [production_system.md](../systems/production_system.md).

---

## What Is a QS Complex?

QS (Quickstart) complexes are **JSON design files** for planetary facilities. They use
the standard component/ability system -- there is no special base class or protocol.
The "QS" prefix is a naming convention for template designs provided with the game.

At runtime, a QS complex design becomes a `PlanetaryFacility` instance on a planet,
loaded via `Ship.from_dict()` for stat calculation.

**Key distinction:** `vehicle_type: "Planetary Complex"` is the only discriminator.
The same component system that powers ships, fighters, and satellites also powers complexes.

---

## Required Components

Every functional complex needs these infrastructure components:

| Component | ID | Purpose | Notes |
|-----------|----|---------|-------|
| Command Center | `central_complex_command` | `CommandAndControl` ability | Required for operation |
| Crew Quarters | `crew_quarters` | `CrewCapacity` ability | Scale count to crew needs |
| Life Support | `life_support` | `LifeSupportCapacity` ability | Must cover crew capacity |

These go in the **CORE** layer. The specialized component(s) that define the complex's
purpose typically go in **OUTER** (or **INNER** for protected placement).

---

## JSON Design Structure

**Location:** `data/designs/qs_<name>.json`

```json
{
  "name": "QS My Complex",
  "ship_class": "Planetary Complex (Tier 1)",
  "vehicle_type": "Planetary Complex",
  "theme_id": "Federation",
  "team_id": 0,
  "color": [100, 100, 255],
  "ai_strategy": "standard_ranged",
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

### Field Reference

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Display name |
| `ship_class` | Yes | "Planetary Complex (Tier N)" -- tier is informational |
| `vehicle_type` | Yes | Must be `"Planetary Complex"` |
| `theme_id` | Yes | Visual theme (e.g., "Federation") |
| `team_id` | Yes | Default team (0) |
| `color` | Yes | RGB color array |
| `ai_strategy` | Yes | AI behavior key (standard for complexes: `"standard_ranged"`) |
| `design_role` | Yes | Classification label from `data/design_roles.json`. Common complex roles: `resource_harvester`, `production_facility`, `planetary_modifier`, `stellar_protector`, `enrichment_facility`, `resupply_depot`, `construction_accelerator`, `defensive_platform` |
| `layers` | Yes | Component layout (CORE, INNER, OUTER, ARMOR) |
| `resources` | Yes | Initial resource levels |
| `expected_stats` | Yes | Cached stat snapshot (recalculated at load) |
| `_metadata` | No | Tracking metadata |

### Component Entry Format

Each component in a layer is:

```json
{
  "id": "component_id_from_components_json",
  "modifiers": [
    {"id": "modifier_id", "value": 1.0}
  ]
}
```

Common modifiers:
- `simple_size_mount` -- scales component size/output (1.0 = normal)
- `hardened_mount` -- increases HP at cost of mass (1.0 = normal)
- `automation` -- reduces crew requirement (0.0 = no automation)

Components are referenced by their `id` from `data/components.json`. The component
must have `"Planetary Complex"` in its `allowed_vehicle_types` list.

---

## Tier System

Tiers are informational labels in the `ship_class` field. They indicate relative
complexity and cost:

| Tier | Typical Use |
|------|-------------|
| Tier 1 | Basic facilities: single-purpose harvesters, resupply depots |
| Tier 2 | Advanced facilities: shipyards, stabilizers, exotic harvesters |

Tiers have no mechanical effect -- they are purely for player guidance and UI grouping.

---

## Existing QS Complexes

### Initial Complexes (spawned on game start)

Defined in `game/strategy/quickstart_builder.py:INITIAL_COMPLEXES`:

| Design ID | Purpose | Tier |
|-----------|---------|------|
| `qs_complex` | Shipyard (ship construction) | 2 |
| `qs_metals_complex` | Metals harvesting | 1 |
| `qs_organics_complex` | Organics harvesting | 1 |
| `qs_vapors_complex` | Vapors harvesting | 1 |
| `qs_radioactives_complex` | Radioactives harvesting | 1 |
| `qs_exotics_complex` | Exotics harvesting | 2 |
| `qs_resupply_depot` | Fuel synthesis and storage | 1 |
| `qs_geologic_stabilizer_complex` | Geologic stabilizer + energy | 1 |

These are the starter facilities every empire's home planet receives.

### Additional Complexes (player-built)

| Design ID | Purpose | Tier |
|-----------|---------|------|
| `qs_atmosphere_processor_complex` | Atmosphere terraforming | 1 |
| `qs_enrichment_complex` | Resource quality improvement | 2 |
| `qs_stellar_stabilizer_complex` | Stellar destruction protection | 2 |
| `qs_warp_stabilizer_complex` | Warp point manipulation protection | 2 |
| `qs_system_geologic_stabilizer_complex` | System-wide geologic protection | 2 |
| `qs_sector_construction_accelerator_complex` | Sector build rate boost | -- |
| `qs_system_construction_accelerator_complex` | System build rate boost | -- |
| `qs_system_shield_suppressor_complex` | System shield suppression (enemy) | 2 |
| `qs_system_shield_booster_complex` | System shield boost (allied) | 2 |
| `qs_sector_shield_suppressor_complex` | Sector shield suppression (enemy) | 1 |
| `qs_sector_shield_booster_complex` | Sector shield boost (allied) | 1 |
| `qs_system_damage_suppressor_complex` | System damage suppression (enemy) | 2 |
| `qs_system_damage_booster_complex` | System damage boost (allied) | 2 |
| `qs_sector_damage_suppressor_complex` | Sector damage suppression (enemy) | 1 |
| `qs_sector_damage_booster_complex` | Sector damage boost (allied) | 1 |
| `qs_sector_shield_projector_complex` | Sector shield projection (allied) | 1 |
| `qs_system_shield_projector_complex` | System shield projection (allied) | 2 |
| `qs_gravity_modifier_complex` | Planet gravity modification | 1 |
| `qs_water_modifier_complex` | Planet water terraforming | 1 |
| `qs_radiation_shield_complex` | Planet radiation shielding | 1 |

### Non-Complex QS Designs

The `data/designs/` directory also contains QS ship designs. These follow the same
JSON structure but with `vehicle_type: "Ship"` and combat or logistics components.

**Combat ships** (used by FleetBattleSetupScreen for battle testing):

| Design | Class | Role | Key Loadout |
|--------|-------|------|-------------|
| `qs_light_combat_escort` | Escort | fleet_escort | Beam weapons, PDC, engine, thruster |
| `qs_heavy_cruiser` | Cruiser | line_combatant | Beams, railguns, shields, armor |
| `qs_missile_cruiser` | Cruiser | missile_platform | 6 seeker missiles, PDC, ordnance storage |
| `qs_battleship` | Battleship | line_combatant | Heavy railguns, lasers, shields, heavy armor |

**Logistics/utility ships:** `qs_escort` (unarmed), `qs_general_purpose` (shipyard + colony),
`qs_cargo_freighter` (cargo hauler), `qs_colony_ship`, `qs_colony_drop_pod`,
superweapon platforms (planet/star destroyer, warp gate, sphere builder).

---

## Adding a New QS Complex

### Step 1: Create the JSON Design

Create `data/designs/qs_<name>.json` following the structure above. Use an existing
complex as a template -- copy the infrastructure components (command, crew, life support)
and replace the specialized component(s).

Set the `design_role` field to an appropriate role from `data/design_roles.json`
(must be a role that allows `"Planetary Complex"` in `allowed_vehicle_types`).

Ensure the specialized component exists in `data/components.json` with
`"Planetary Complex"` in `allowed_vehicle_types`.

### Step 2: (Optional) Add to Initial Complexes

If the complex should spawn on every empire's home planet at game start, add its
design ID to `INITIAL_COMPLEXES` in `game/strategy/quickstart_builder.py`.

### Step 3: Validate

The component validation tests in `tests/` automatically check all designs in
`data/designs/` for valid component IDs, required fields, and resource costs.
Run the test suite to verify your design passes validation.

### Step 4: Update Documentation

- Add the new ability to [ability_reference.md](../systems/ability_reference.md) if it uses a new ability type
- Update this guide's complex tables if adding a new QS complex
- Update [strategy_layer.md](../systems/strategy_layer.md) if the complex introduces new strategy engine behavior

---

## Crew Budget

Complexes must house and support their crew. Each component declares crew requirements
via `CrewRequired`, and each `crew_quarters` provides capacity via `CrewCapacity`.
Life support capacity (`LifeSupportCapacity`) must also cover the crew count.

Rule of thumb: check the crew requirement of your specialized component(s) in
`components.json` and add enough `crew_quarters` and `life_support` to cover it.
The `validate-designs` skill can check this automatically.

---

## File Locations

| File | Purpose |
|------|---------|
| `data/designs/qs_*.json` | QS complex design files |
| `data/components.json` | Component registry (IDs, abilities, costs) |
| `game/strategy/quickstart_builder.py` | `INITIAL_COMPLEXES` list, game start spawning |
| `game/strategy/data/planetary_facility.py` | `PlanetaryFacility` dataclass |
| `game/strategy/systems/design_library.py` | Design loading (`load_design_data()`) |
| `game/strategy/engine/production_spawner.py` | Facility spawning on construction completion |
