# Ability Reference

> Comprehensive catalog of all component abilities available in the game.
> Source: `game/simulation/components/abilities/`
> Registry: `ABILITY_REGISTRY` in `abilities/__init__.py`

---

## How to Read This Document

Each ability entry lists:
- **Registry Key** — the string used in `components.json` to attach the ability
- **Class** — the Python class that implements it
- **Source File** — location under `game/simulation/components/abilities/`
- **Layer** — COMBAT (default) or STRATEGIC
- **Data Format** — how to specify values in JSON (scalar, dict, or boolean)
- **Required/Optional Values** — parameters the ability expects
- **Stat Bindings** — modifier stats that affect the ability at runtime

Data format conventions:
- **Scalar**: `100` or `5.0` — a single numeric value
- **Dict**: `{"damage": 100, "range": 5000}` — named parameters
- **Boolean**: `true` — marker presence
- **Formula**: `"=50 + range_to_target * 0.1"` — runtime-evaluated expression (weapons only)

---

## Stacking Rules

All numeric abilities follow a two-phase aggregation model when multiple
components provide the same ability:

### Phase 1: Intra-Group MAX
Components with the same `stack_group` value are reduced to their **maximum**.
Redundant components in the same group provide no additional benefit.

Example: Two sensors with `stack_group: "sensors_a"` and values [1.0, 0.5] → result is 1.0.

### Phase 2: Inter-Group SUM  
After intra-group reduction, values from **different** groups are **summed**.
Diverse components from different groups stack additively.

Example: Sensor group_a (1.0) + Sensor group_b (0.5) → total 1.5.

### No Stack Group
Components without an explicit `stack_group` each form their own group
(keyed by the component object). Multiple such components SUM together.

### Validation
Stacking behavior is validated by simulation tests:
- Same-group MAX: EMISSIVE-003, SRA-004, TOHIT-ATK-002, TOHIT-DEF-002
- Different-group SUM: EMISSIVE-004, SRA-005, TOHIT-ATK-003, TOHIT-DEF-003
- Three-component same-group: EMISSIVE-006
- Mixed positive + negative: TOHIT-ATK-005

---

## Scope Reference

Scopes control which entities an ability affects. Defined in `AbilityScope` enum
(`game/simulation/components/abilities/base.py`). Each ability declares `allowed_scopes`
(valid scopes) and `default_scope` (used when JSON omits `scope`).

| Scope | Value | Description |
|-------|-------|-------------|
| SELF | `"self"` | Only the owner entity |
| FLEET | `"fleet"` | All ships in the same battle group |
| SECTOR | `"sector"` | All entities in the same hex |
| ALLIED_SECTOR | `"allied_sector"` | Allied entities in the same hex (owner + allies) |
| SYSTEM | `"system"` | All entities in the star system |
| ALLIED_SYSTEM | `"allied_system"` | Allied entities in the star system (owner + allies) |
| PLANET | `"planet"` | Planet-wide effect |
| EMPIRE | `"empire"` | All colonies belonging to the owning player |
| ALLIED_EMPIRE | `"allied_empire"` | All colonies of the owning player and their allies |
| ENEMY_SECTOR | `"enemy_sector"` | Enemy entities in the same hex (not owned by the player) |
| ENEMY_SYSTEM | `"enemy_system"` | Enemy entities in the star system (not owned by the player) |
| PLAYER_SECTOR | `"player_sector"` | Only the player's own entities in the same hex (excludes allies) |
| PLAYER_SYSTEM | `"player_system"` | Only the player's own entities in the star system (excludes allies) |

**Key distinction:** `PLAYER_*` scopes are strictly owner-only. `ALLIED_*` scopes include the owner and their allies. `ENEMY_*` scopes target only entities not owned by the player.

---

## Weapons

### WeaponAbility

| Field | Value |
|-------|-------|
| Registry Key | `WeaponAbility` |
| Class | `WeaponAbility` |
| Source | `weapons.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Generic weapon base. Supports damage formulas, firing arcs, and reload cycles.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `damage` | float or formula | Yes | — | Base weapon damage per shot |
| `range` | float or formula | Yes | — | Maximum engagement range (px) |
| `reload` | float | No | 1.0 | Reload time in seconds |
| `firing_arc` | float | No | 360 | Firing arc in degrees |
| `facing_angle` | float | No | 0 | Angle offset from ship facing |
| `tags` | list | No | [] | Classification tags |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| DAMAGE_MULT | damage | multiply |
| RANGE_MULT | range | multiply |
| RELOAD_MULT | reload_time | multiply |
| ARC_SET | firing_arc | set (override) |
| ARC_ADD | firing_arc | add |

---

### BeamWeaponAbility

| Field | Value |
|-------|-------|
| Registry Key | `BeamWeaponAbility` |
| Class | `BeamWeaponAbility` |
| Source | `weapons.py` |
| Layer | COMBAT |
| Base Class | `WeaponAbility` |

Beam weapon with accuracy falloff over distance. Hit chance uses logistic/sigmoid function.

**Data Format:** Dict (all WeaponAbility parameters plus below)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `accuracy_falloff` | float | No | 0.001 | Accuracy penalty per unit distance |
| `base_accuracy` | float | No | 1.0 | Base accuracy (0.0-1.0 or percentage) |

**Additional Stat Bindings (extends WeaponAbility):**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| ACCURACY_ADD | base_accuracy | add |

---

### ProjectileWeaponAbility

| Field | Value |
|-------|-------|
| Registry Key | `ProjectileWeaponAbility` |
| Class | `ProjectileWeaponAbility` |
| Source | `weapons.py` |
| Layer | COMBAT |
| Base Class | `WeaponAbility` |

Projectile-based weapon (bullets, railgun rounds, unguided missiles).

**Data Format:** Dict (all WeaponAbility parameters plus below)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `projectile_speed` | float | No | 500 | Speed of projectile (divided by PROJECTILE_SPEED_SCALE=100 at runtime) |

---

### SeekerWeaponAbility

| Field | Value |
|-------|-------|
| Registry Key | `SeekerWeaponAbility` |
| Class | `SeekerWeaponAbility` |
| Source | `weapons.py` |
| Layer | COMBAT |
| Base Class | `WeaponAbility` |

Guided seeking missile with tracking, HP, and stealth properties. Fires omni-directionally (ignores firing arc for launch).

**Data Format:** Dict (all WeaponAbility parameters plus below)

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `projectile_speed` | float | No | 500 | Missile flight speed |
| `endurance` | float | No | 3.0 | Flight duration in seconds |
| `turn_rate` | float | No | 30.0 | Turning speed (degrees/sec) |
| `to_hit_defense` | float | No | 0 | Defensive modifier for the missile |
| `projectile_damage` | float | Yes | — | Warhead explosion damage |
| `projectile_hp` | float | No | 1.0 | Missile durability (HP) |
| `projectile_stealth` | float | No | 0.0 | Stealth level |

**Additional Stat Bindings (extends WeaponAbility):**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| ENDURANCE_MULT | endurance | multiply |
| PROJECTILE_DAMAGE_MULT | projectile_damage | multiply |
| PROJECTILE_HP_MULT | projectile_hp | multiply |
| PROJECTILE_STEALTH_LEVEL | projectile_stealth | add |

---

## Defense

### ShieldProjection

| Field | Value |
|-------|-------|
| Registry Key | `ShieldProjection` |
| Class | `ShieldProjection` |
| Source | `defense.py` |
| Layer | COMBAT |
| Base Class | `SimpleMultiplierAbility` |

Provides shield capacity (HP pool).

**Data Format:** Scalar (shield HP)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Shield capacity in HP |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CAPACITY_MULT | capacity | multiply |
| SHIELD_CAPACITY_MULT | capacity | multiply (stacked) |

---

### ShieldRegeneration

| Field | Value |
|-------|-------|
| Registry Key | `ShieldRegeneration` |
| Class | `ShieldRegeneration` |
| Source | `defense.py` |
| Layer | COMBAT |
| Base Class | `SimpleMultiplierAbility` |

Regenerates shields per second.

**Data Format:** Scalar (regen rate)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Shield regeneration rate per second |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| ENERGY_GEN_MULT | rate | multiply |

---

### ToHitAttackModifier

| Field | Value |
|-------|-------|
| Registry Key | `ToHitAttackModifier` |
| Class | `ToHitAttackModifier` |
| Source | `defense.py` |
| Layer | COMBAT |
| Base Class | `StaticValueAbility` |

Provides sensor/targeting attack bonus for to-hit calculations.
Supports fleet/system/allied_system/empire scope — a single component can provide
a to-hit bonus to all friendly ships in the battle group or star system.

**Data Format:** Dict with value and optional scope

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Attack bonus (+) or penalty (-) |
| scope | string | No | `"self"` (default), `"fleet"`, `"system"`, `"allied_system"`, or `"empire"` |
| stack_group | string | No | Stacking group (same group = MAX, different = SUM) |

**Scope:** `self` (default), `fleet`, `system`, `allied_system`, `empire`

**Example:** `{"ToHitAttackModifier": {"value": 2.0, "scope": "fleet", "stack_group": "FleetSensor"}}`

**Stat Bindings:** None (static value, not modified)

**Validation Tests:** TOHIT-ATK-001 to 005 (self scope), TOHIT-ATK-FLEET-001 to 004 (fleet scope)

---

### ToHitDefenseModifier

| Field | Value |
|-------|-------|
| Registry Key | `ToHitDefenseModifier` |
| Class | `ToHitDefenseModifier` |
| Source | `defense.py` |
| Layer | COMBAT |
| Base Class | `StaticValueAbility` |

Provides evasion/defense bonus for to-hit calculations.
Supports fleet/system/allied_system/empire scope — a single component can provide
an evasion bonus to all friendly ships in the battle group or star system.

**Data Format:** Dict with value and optional scope

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Defense bonus (+) or penalty (-) |
| scope | string | No | `"self"` (default), `"fleet"`, `"system"`, `"allied_system"`, or `"empire"` |
| stack_group | string | No | Stacking group (same group = MAX, different = SUM) |

**Scope:** `self` (default), `fleet`, `system`, `allied_system`, `empire`

**Stat Bindings:** None (static value, not modified)

---

### EmissiveArmor

| Field | Value |
|-------|-------|
| Registry Key | `EmissiveArmor` |
| Class | `EmissiveArmor` |
| Source | `defense.py` |
| Layer | COMBAT |
| Base Class | `StaticValueAbility` |

Flat damage reduction per hit (damage ignored). Damage pipeline: Shields → EmissiveArmor → ShieldRegeneratingArmor → Hull.

**Data Format:** Scalar (integer, damage points ignored)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | int | Yes | Damage points ignored per hit |

**Stat Bindings:** None (static value, not modified)

---

### ShieldRegeneratingArmor

| Field | Value |
|-------|-------|
| Registry Key | `ShieldRegeneratingArmor` |
| Class | `ShieldRegeneratingArmor` |
| Source | `defense.py` |
| Layer | COMBAT |
| Base Class | `StaticValueAbility` |

Absorbs overflow damage (after shields and emissive armor) and recharges shields by the absorbed amount. Damage pipeline: Shields → EmissiveArmor → ShieldRegeneratingArmor → Hull. Only aggregates from active (non-destroyed) armor components.

**Data Format:** Scalar (integer, absorption capacity per hit)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | int | Yes | Damage absorption capacity per hit |

**Stat Bindings:** None (static value, not modified)

---

### Armor

| Field | Value |
|-------|-------|
| Registry Key | `Armor` |
| Class | `Ability` (lambda) |
| Source | `__init__.py` |
| Layer | COMBAT |

Dummy ability for armor tag/existence checks. No functional behavior.

**Data Format:** Any (ignored)

---

## Propulsion

### CombatPropulsion

| Field | Value |
|-------|-------|
| Registry Key | `CombatPropulsion` |
| Class | `CombatPropulsion` |
| Source | `propulsion.py` |
| Layer | COMBAT |
| Base Class | `SimpleMultiplierAbility` |

Provides thrust for combat maneuvering. Ship speed = `(thrust * 25) / mass` px/tick.

**Data Format:** Scalar (thrust in Newtons)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Thrust force in Newtons |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| THRUST_MULT | thrust_force | multiply |

---

### ManeuveringThruster

| Field | Value |
|-------|-------|
| Registry Key | `ManeuveringThruster` |
| Class | `ManeuveringThruster` |
| Source | `propulsion.py` |
| Layer | COMBAT |
| Base Class | `SimpleMultiplierAbility` |

Provides rotation/turn speed for combat maneuvering. Turn speed = `(raw * 25000) / mass^1.5` degrees per 100 ticks.

**Data Format:** Scalar (rotation degrees/sec)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Raw rotation rate |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| TURN_MULT | turn_rate | multiply |

---

### StrategicMovement

| Field | Value |
|-------|-------|
| Registry Key | `StrategicMovement` |
| Class | `StrategicMovement` |
| Source | `propulsion.py` |
| Layer | STRATEGIC |
| Base Class | `SimpleMultiplierAbility` |
| Allowed Scopes | SELF, ALLIED_SECTOR, ALLIED_SYSTEM |

Provides strategic map movement points for interstellar travel.

**Data Format:** Scalar (movement points)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | float | Yes | Movement points per turn |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| STRATEGIC_MULT | movement_points | multiply |

---

### WarpJump

| Field | Value |
|-------|-------|
| Registry Key | `WarpJump` |
| Class | `WarpJump` |
| Source | `propulsion.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Binary capability for warp transit between star systems.

**Data Format:** Scalar or Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `max_tonnage` | float | Yes | — | Maximum ship mass for warp transit |
| `energy_cost` | float | No | 0 | Energy consumed per jump |

Scalar format: `5000` is interpreted as `max_tonnage = 5000`.

**Stat Bindings:** None

---

## Resources

### ResourceConsumption

| Field | Value |
|-------|-------|
| Registry Key | `ResourceConsumption` |
| Class | `ResourceConsumption` |
| Source | `resources.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Consumes resources (fuel, ammo, energy) based on a trigger type.

**Data Format:** Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resource` | string | Yes | Resource type to consume (fuel, ammo, energy) |
| `amount` | float | Yes | Consumption amount per trigger |
| `trigger` | string | Yes | `"constant"` (per-tick), `"activation"` (per-use), `"strategic_per_hex"` (per-hex movement), or `"per_turn"` (per-turn strategic cost) |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CONSUMPTION_MULT | amount | multiply |

---

### ResourceStorage

| Field | Value |
|-------|-------|
| Registry Key | `ResourceStorage` |
| Class | `ResourceStorage` |
| Source | `resources.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Stores resources with capacity limits.

**Data Format:** Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resource` | string | Yes | Resource type to store |
| `amount` | float | Yes | Storage capacity |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CAPACITY_MULT | max_amount | multiply |

---

### ResourceGeneration

| Field | Value |
|-------|-------|
| Registry Key | `ResourceGeneration` |
| Class | `ResourceGeneration` |
| Source | `resources.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Generates resources (energy, fuel) per second.

**Data Format:** Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resource` | string | Yes | Resource type generated |
| `amount` | float | Yes | Generation rate per second |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| ENERGY_GEN_MULT | rate | multiply |

---

## Crew

### CrewCapacity

| Field | Value |
|-------|-------|
| Registry Key | `CrewCapacity` |
| Class | `CrewCapacity` |
| Source | `crew.py` |
| Layer | COMBAT |
| Base Class | `SimpleMultiplierAbility` |

Provides crew quarters capacity.

**Data Format:** Scalar (integer, crew count)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | int | Yes | Number of crew housed |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CREW_CAPACITY_MULT | amount | multiply |

---

### LifeSupportCapacity

| Field | Value |
|-------|-------|
| Registry Key | `LifeSupportCapacity` |
| Class | `LifeSupportCapacity` |
| Source | `crew.py` |
| Layer | COMBAT |
| Base Class | `SimpleMultiplierAbility` |

Provides life support capacity for crew.

**Data Format:** Scalar (integer, support units)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | int | Yes | Life support capacity |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| LIFE_SUPPORT_CAPACITY_MULT | amount | multiply |

---

### CrewRequired

| Field | Value |
|-------|-------|
| Registry Key | `CrewRequired` |
| Class | `CrewRequired` |
| Source | `crew.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Specifies crew required to operate the component. Also scales with mass via sqrt scaling (custom, not via STAT_BINDINGS).

**Data Format:** Scalar (integer, crew count)

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| value | int | Yes | Crew members required to operate |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CREW_REQ_MULT | amount | multiply |

---

## Cargo

### CargoStorage

| Field | Value |
|-------|-------|
| Registry Key | `CargoStorage` |
| Class | `CargoStorage` |
| Source | `cargo.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Cargo transport capability for passengers or generic goods.

**Data Format:** Scalar or Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `cargo_type` | string | No | `"generic"` | `"passengers"` or `"generic"` |
| `capacity` | float | No | 0 | Cargo capacity |

Scalar format: `5000` is interpreted as generic cargo with capacity 5000.

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CAPACITY_MULT | capacity | multiply |

---

### PodStorage

| Field | Value |
|-------|-------|
| Registry Key | `PodStorage` |
| Class | `PodStorageAbility` |
| Source | `cargo.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Ship-side mass-based pod storage. Provides capacity for carrying discrete items (drop pods, fighters) as `carried_items`.

**Data Format:** Scalar or Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `capacity_mass` | float | Yes | Mass capacity for carried items |

Scalar format: `5000` is interpreted as `capacity_mass = 5000`.

**Stat Bindings:** None

---

## Markers / Special

### VehicleLaunch

| Field | Value |
|-------|-------|
| Registry Key | `VehicleLaunch` |
| Class | `VehicleLaunchAbility` |
| Source | `markers.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Fighter hangar bay. Stores and launches fighters on a cycle timer.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `fighter_class` | string | No | `"Fighter (Small)"` | Fighter type name |
| `capacity` | int | No | 0 | Hangar capacity |
| `cycle_time` | float | No | 5.0 | Seconds between launches |

**Stat Bindings:**

| StatKey | Attribute | Operation |
|---------|-----------|-----------|
| CAPACITY_MULT | capacity | multiply |

---

### CommandAndControl

| Field | Value |
|-------|-------|
| Registry Key | `CommandAndControl` |
| Class | `CommandAndControl` |
| Source | `markers.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Marker — component provides command capability (bridge, CIC).

**Data Format:** Boolean (`true`)

**Stat Bindings:** None

---

### RequiresCommandAndControl

| Field | Value |
|-------|-------|
| Registry Key | `RequiresCommandAndControl` |
| Class | `RequiresCommandAndControl` |
| Source | `markers.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Per-component requirement — component requires an operational `CommandAndControl`
provider on the ship to function. Checked each tick via `update()`: if no active
C&C component exists on the ship, this component becomes non-operational (its stats
don't contribute, weapons won't fire).

**Applied to:** All combat-relevant production components (weapons, shields, engines,
thrusters, sensors, ECM, generators, hangars, repair bays — 24 components total).
NOT applied to passive components (armor, storage, crew quarters, life support).

**Data Format:** Boolean (`true`)

**Stat Bindings:** None (operational check via `update()` return value)

---

### RequiresCombatMovement

| Field | Value |
|-------|-------|
| Registry Key | `RequiresCombatMovement` |
| Class | `RequiresCombatMovement` |
| Source | `markers.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Marker — component requires combat propulsion to operate.

**Data Format:** Boolean (`true`)

**Stat Bindings:** None

---

### StructuralIntegrity

| Field | Value |
|-------|-------|
| Registry Key | `StructuralIntegrity` |
| Class | `StructuralIntegrity` |
| Source | `markers.py` |
| Layer | COMBAT |
| Base Class | `Ability` |

Marker — hull provides structural integrity for the ship.

**Data Format:** Boolean (`true`)

**Stat Bindings:** None

---

## Colonization

### ColonizePlanet

| Field | Value |
|-------|-------|
| Registry Key | `ColonizePlanet` |
| Class | `ColonizePlanet` |
| Source | `colonize.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Marks a ship component as providing colonization capability for a planet type.

**Phase 3 Colonization Flow (Drop Pod system):**
1. Drop pods are designed in the workshop and built at colonies (see Drop Pod section in `resource_system.md`)
2. Colony ship loads drop pods from the planet staging yard into `ship.carried_items`
3. Drop pods are **universal** -- any drop pod works on any planet type
4. `ColonizeValidator` checks `ship.carried_items` for entries with `vehicle_type='drop_pod'`
5. `OrderProcessor._deploy_drop_pod()` removes the pod from `carried_items` and creates a `PlanetaryFacility` using the pod's full `design_data`
6. Colony ship stays in fleet (not consumed)

**Stat Bindings:** None

---

## Harvester & Storage

### ResourceHarvester

| Field | Value |
|-------|-------|
| Registry Key | `ResourceHarvester` |
| Class | `ResourceHarvesterAbility` |
| Source | `harvester.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Enables resource harvesting on planets.

**Data Format:** Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resource_type` | string | Yes | Type of resource harvested |
| `base_harvest_rate` | float | Yes | Resources per turn |

**Stat Bindings:** None

**Size mount scaling:** `base_harvest_rate` is multiplied by the component's `simple_size_mount` value at runtime by `HarvestingEngine` (via `modifier_resolver.resolve_size_multiplier()`). At size 0.2, a harvester with rate 100 harvests at 20/turn.

---

### LocalStorage

| Field | Value |
|-------|-------|
| Registry Key | `LocalStorage` |
| Class | `LocalStorageAbility` |
| Source | `harvester.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Local colony resource storage capacity.

**Data Format:** Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `resource_type` | string | Yes | Resource type stored |
| `capacity` | float | Yes | Storage capacity |

**Stat Bindings:** Uses `storage_mult` modifier

**Size mount scaling:** `capacity` is multiplied by the component's `simple_size_mount` value at runtime by `HarvestingEngine._collect_storage_from_facility()`. At size 0.2, a 10000 capacity vault stores 2000.

---

### StagingYard

| Field | Value |
|-------|-------|
| Registry Key | `StagingYard` |
| Class | `StagingYardAbility` |
| Source | `harvester.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Planet-side storage for constructed items (fighters, drop pods). Each instance adds
mass capacity. Multiple staging yard facilities stack additively.

**Data Format:** Scalar or Dict

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `capacity_mass` | float | Yes | Mass capacity for stored vehicles |

Scalar format: `5000` is interpreted as `capacity_mass = 5000`.

**Stat Bindings:** None

---

### PlanetaryYard

| Field | Value |
|-------|-------|
| Registry Key | `PlanetaryYard` |
| Class | `PlanetaryYardAbility` |
| Source | `harvester.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Marker ability -- required for a colony's base construction queue. A colony must
have at least one operational facility with this ability to build complexes. The
starter facility (deployed from a drop pod during colonization) provides this.

**Data Format:** Boolean (`true`)

**Stat Bindings:** None

---

### SpaceShipyard

| Field | Value |
|-------|-------|
| Registry Key | `SpaceShipyard` |
| Class | `SpaceShipyardAbility` |
| Source | `harvester.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Enables ship construction at colonies.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `construction_speed_bonus` | float | No | 1.0 | Construction speed multiplier |
| `max_ship_mass` | float | No | 100000 | Maximum constructible ship mass |
| `production_rates` | dict | No | — | Per-type production rates |

**Stat Bindings:** None

---

## Planetary

### PlanetaryShield

| Field | Value |
|-------|-------|
| Registry Key | `PlanetaryShield` |
| Class | `PlanetaryShieldAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Planetary shield protection against superweapons. Toggled via generic `ACTIVATE_ABILITY`/`DEACTIVATE_ABILITY` orders. The `shield_active` field was removed; shield state is tracked in `planet.active_abilities['PlanetaryShield']`.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `energy_drain_rate` | float | No | 0 | Energy per turn while active |
| `activation_time` | int | No | 1 | Ticks to activate |
| `deactivation_time` | int | No | 1 | Ticks to deactivate |
| `shield_hp` | float | No | 0 | Combat shield HP (placeholder) |
| `shield_regen` | float | No | 0 | Combat regen (placeholder) |

**Stat Bindings:** None

---

### StrategicResourceGeneration

| Field | Value |
|-------|-------|
| Registry Key | `StrategicResourceGeneration` |
| Class | `StrategicResourceGenerationAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Generates resources per turn on the strategy layer. Each instance generates a specific resource type at a given rate per turn (spread across 100 ticks). Works on any entity with facilities (planets, space stations, ships). Separate from combat `ResourceGeneration` which operates per second.

Replaces the old `PlanetaryEnergyGenerator` (PROJ-238). Old `PlanetaryEnergyStorage` was also removed — reuse combat `ResourceStorage` instead.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `resource` | string | Yes | `""` | Resource type identifier (e.g. from resources.json) |
| `generation_rate` | float | No | 0.0 | Amount produced per turn |

**Stat Bindings:** None

---

### GeologicStabilizer

| Field | Value |
|-------|-------|
| Registry Key | `GeologicStabilizer` |
| Class | `GeologicStabilizerAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Prevents planet-destroying superweapons (IMPLODE_PLANET) within scope. Requires energy and manual activation — only provides protection when in the ACTIVE phase (checked via `require_active=True` in the scanner).

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `energy_drain_rate` | float | No | 0.0 | Energy per turn while active |
| `activation_time` | int | No | 1 | Ticks to activate |
| `deactivation_time` | int | No | 1 | Ticks to deactivate |
| `scope` | string | No | `"sector"` | Protection range: planet, sector, system |

**Allowed Scopes:** PLANET, SECTOR, SYSTEM

**Stat Bindings:** None

**Size mount scaling:** Production rates from `production_rates.json` are multiplied by the PlanetaryYard component's `simple_size_mount` value at runtime.

---

### StellarStabilizer

| Field | Value |
|-------|-------|
| Registry Key | `StellarStabilizer` |
| Class | `StellarStabilizerAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Prevents star-destroying superweapons (STELLERATE_STAR) and Dyson Sphere construction (CREATE_DYSON_SPHERE) within scope. Requires energy and manual activation — only provides protection when in the ACTIVE phase.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `energy_drain_rate` | float | No | 0.0 | Energy per turn while active |
| `activation_time` | int | No | 1 | Ticks to activate |
| `deactivation_time` | int | No | 1 | Ticks to deactivate |
| `scope` | string | No | `"system"` | Protection range: sector, system |

**Allowed Scopes:** SECTOR, SYSTEM

**Stat Bindings:** None

---

### WarpFieldStabilizer

| Field | Value |
|-------|-------|
| Registry Key | `WarpFieldStabilizer` |
| Class | `WarpFieldStabilizerAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Prevents warp point creation (OPEN_WARP_POINT) and destruction (CLOSE_WARP_POINT) within scope. Requires energy and manual activation — only provides protection when in the ACTIVE phase.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `energy_drain_rate` | float | No | 0.0 | Energy per turn while active |
| `activation_time` | int | No | 1 | Ticks to activate |
| `deactivation_time` | int | No | 1 | Ticks to deactivate |
| `scope` | string | No | `"system"` | Protection range: sector, system |

**Allowed Scopes:** SECTOR, SYSTEM

**Stat Bindings:** None

---

### ResourceHarvestBooster

| Field | Value |
|-------|-------|
| Registry Key | `ResourceHarvestBooster` |
| Class | `ResourceHarvestBoosterAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Increases resource harvesting rate for a specific resource within scope. Multiplies `base_harvest_rate` of matching ResourceHarvester abilities.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `resource_type` | string | No | `""` | Resource to boost (e.g., "metals") |
| `multiplier` | float | No | 1.0 | Harvest rate multiplier (e.g., 1.5 for 50% boost) |
| `scope` | string | No | `"planet"` | Effect range |
| `stack_group` | string | No | None | Stacking group (intra-group MAX, inter-group MULTIPLY) |

**Allowed Scopes:** SELF, PLANET, SECTOR, SYSTEM, EMPIRE, ALLIED_EMPIRE

**Stat Bindings:** None

---

### BuildRateBooster

| Field | Value |
|-------|-------|
| Registry Key | `BuildRateBooster` |
| Class | `BuildRateBoosterAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Increases construction/production rate within scope. Multiplies all build queue production rates.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `multiplier` | float | No | 1.0 | Build rate multiplier (e.g., 1.25 for 25% faster) |
| `scope` | string | No | `"sector"` | Effect range |
| `stack_group` | string | No | None | Stacking group |

**Allowed Scopes:** SELF, PLANET, SECTOR, SYSTEM, EMPIRE, ALLIED_EMPIRE

**Stat Bindings:** None

---

### AtmosphereModifier

| Field | Value |
|-------|-------|
| Registry Key | `AtmosphereModifier` |
| Class | `AtmosphereModifierAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Modifies a planet's atmosphere toward target gas compositions. Slowly adds or removes atmospheric gases each turn. The rate is in kg of gas that can be processed per turn; conversion to pressure change depends on the planet's surface area and gravity (`Pa_per_kg = gravity / surface_area`). Multiple facilities on the same planet stack their rates additively.

Processed once per turn (not per tick) by `AtmosphereEngine`, after the 100-tick loop. See the [Atmosphere Modification Pipeline](strategy_layer.md#atmosphere-modification-pipeline) section in strategy_layer.md for the full processing algorithm.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `modification_rate` | float | No | 0.0 | kg of atmosphere added/removed per turn |

**Allowed Scopes:** SELF only

**Stat Bindings:** None

---

### QualityImprovement

| Field | Value |
|-------|-------|
| Registry Key | `QualityImprovement` |
| Class | `QualityImprovementAbility` |
| Source | `planetary.py` |
| Layer | STRATEGIC |
| Base Class | `Ability` |

Permanently improves resource deposit quality on a planet. Each turn, adds `improvement_rate` to the quality value of the specified resource. The change is permanent — persists even if the facility is later removed. Quality caps at 100.

**Data Format:** Dict

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `resource_type` | string | No | `""` | Which resource to improve (e.g., "metals") |
| `improvement_rate` | float | No | 0.0 | Quality increase per turn |

**Allowed Scopes:** SELF only

**Stat Bindings:** None

---

## Superweapons

All superweapons share the same structure: boolean or dict with optional `action_time`. All are STRATEGIC layer, SELF scope only.

### DestroyPlanet

| Field | Value |
|-------|-------|
| Registry Key | `DestroyPlanet` |
| Class | `DestroyPlanet` |
| Source | `superweapons.py` |

Planet Imploder. Destroys a single planet.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action_time` | int | No | 1 | Ticks to execute |

---

### DestroyStar

| Field | Value |
|-------|-------|
| Registry Key | `DestroyStar` |
| Class | `DestroyStar` |
| Source | `superweapons.py` |

Stellerator. Destroys a star and everything in the system (ships, planets).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action_time` | int | No | 1 | Ticks to execute |

---

### OpenWarpPoint

| Field | Value |
|-------|-------|
| Registry Key | `OpenWarpPoint` |
| Class | `OpenWarpPoint` |
| Source | `superweapons.py` |

Warp Point Creator. Creates a new warp connection between star systems.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action_time` | int | No | 1 | Ticks to execute |

---

### CloseWarpPoint

| Field | Value |
|-------|-------|
| Registry Key | `CloseWarpPoint` |
| Class | `CloseWarpPoint` |
| Source | `superweapons.py` |

Warp Point Closer. Permanently closes a warp point.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action_time` | int | No | 1 | Ticks to execute |

---

### CreateDysonSphere

| Field | Value |
|-------|-------|
| Registry Key | `CreateDysonSphere` |
| Class | `CreateDysonSphere` |
| Source | `superweapons.py` |

Dyson Sphere Constructor. Builds a megastructure around a star.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action_time` | int | No | 1 | Ticks to execute |

---

### SelfDestruct

| Field | Value |
|-------|-------|
| Registry Key | `SelfDestruct` |
| Class | `SelfDestruct` |
| Source | `superweapons.py` |

Self-Destruct Device. Schedules ship for destruction.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `action_time` | int | No | 1 | Ticks to execute |

---

## Quick Reference: Registry Key to Class

| Registry Key | Class | Category |
|---|---|---|
| `WeaponAbility` | WeaponAbility | Weapons |
| `BeamWeaponAbility` | BeamWeaponAbility | Weapons |
| `ProjectileWeaponAbility` | ProjectileWeaponAbility | Weapons |
| `SeekerWeaponAbility` | SeekerWeaponAbility | Weapons |
| `ShieldProjection` | ShieldProjection | Defense |
| `ShieldRegeneration` | ShieldRegeneration | Defense |
| `ToHitAttackModifier` | ToHitAttackModifier | Defense |
| `ToHitDefenseModifier` | ToHitDefenseModifier | Defense |
| `EmissiveArmor` | EmissiveArmor | Defense |
| `ShieldRegeneratingArmor` | ShieldRegeneratingArmor | Defense |
| `Armor` | Ability (lambda) | Defense |
| `CombatPropulsion` | CombatPropulsion | Propulsion |
| `ManeuveringThruster` | ManeuveringThruster | Propulsion |
| `StrategicMovement` | StrategicMovement | Propulsion |
| `WarpJump` | WarpJump | Propulsion |
| `ResourceConsumption` | ResourceConsumption | Resources |
| `ResourceStorage` | ResourceStorage | Resources |
| `ResourceGeneration` | ResourceGeneration | Resources |
| `CrewCapacity` | CrewCapacity | Crew |
| `LifeSupportCapacity` | LifeSupportCapacity | Crew |
| `CrewRequired` | CrewRequired | Crew |
| `CargoStorage` | CargoStorage | Cargo |
| `PodStorage` | PodStorageAbility | Cargo |
| `VehicleLaunch` | VehicleLaunchAbility | Markers |
| `CommandAndControl` | CommandAndControl | Markers |
| `RequiresCommandAndControl` | RequiresCommandAndControl | Markers |
| `RequiresCombatMovement` | RequiresCombatMovement | Markers |
| `StructuralIntegrity` | StructuralIntegrity | Markers |
| `ColonizePlanet` | ColonizePlanet | Colonization |
| `ResourceHarvester` | ResourceHarvesterAbility | Harvester |
| `LocalStorage` | LocalStorageAbility | Harvester |
| `StagingYard` | StagingYardAbility | Harvester |
| `PlanetaryYard` | PlanetaryYardAbility | Harvester |
| `SpaceShipyard` | SpaceShipyardAbility | Harvester |
| `PlanetaryShield` | PlanetaryShieldAbility | Planetary |
| `StrategicResourceGeneration` | StrategicResourceGenerationAbility | Planetary |
| `GeologicStabilizer` | GeologicStabilizerAbility | Planetary |
| `StellarStabilizer` | StellarStabilizerAbility | Planetary |
| `WarpFieldStabilizer` | WarpFieldStabilizerAbility | Planetary |
| `ResourceHarvestBooster` | ResourceHarvestBoosterAbility | Planetary |
| `BuildRateBooster` | BuildRateBoosterAbility | Planetary |
| `AtmosphereModifier` | AtmosphereModifierAbility | Planetary |
| `QualityImprovement` | QualityImprovementAbility | Planetary |
| `DestroyPlanet` | DestroyPlanet | Superweapons |
| `DestroyStar` | DestroyStar | Superweapons |
| `OpenWarpPoint` | OpenWarpPoint | Superweapons |
| `CloseWarpPoint` | CloseWarpPoint | Superweapons |
| `CreateDysonSphere` | CreateDysonSphere | Superweapons |
| `SelfDestruct` | SelfDestruct | Superweapons |

---

## Stat Key Reference

All modifier stat keys that affect abilities at runtime.

### Multiplicative (default 1.0)

| StatKey | Typical Consumers |
|---------|-------------------|
| MASS_MULT | Component mass |
| HP_MULT | Component HP |
| DAMAGE_MULT | WeaponAbility |
| RANGE_MULT | WeaponAbility |
| COST_MULT | Component cost |
| THRUST_MULT | CombatPropulsion |
| TURN_MULT | ManeuveringThruster |
| STRATEGIC_MULT | StrategicMovement |
| ENERGY_GEN_MULT | ResourceGeneration, ShieldRegeneration |
| CAPACITY_MULT | ResourceStorage, ShieldProjection, CargoStorage, VehicleLaunch |
| SHIELD_CAPACITY_MULT | ShieldProjection (stacked with CAPACITY_MULT) |
| CREW_CAPACITY_MULT | CrewCapacity |
| LIFE_SUPPORT_CAPACITY_MULT | LifeSupportCapacity |
| CONSUMPTION_MULT | ResourceConsumption |
| RELOAD_MULT | WeaponAbility |
| ENDURANCE_MULT | SeekerWeaponAbility |
| PROJECTILE_HP_MULT | SeekerWeaponAbility |
| PROJECTILE_DAMAGE_MULT | SeekerWeaponAbility |
| CREW_REQ_MULT | CrewRequired |

### Additive (default 0.0)

| StatKey | Typical Consumers |
|---------|-------------------|
| MASS_ADD | Component mass |
| ARC_ADD | WeaponAbility firing arc |
| ACCURACY_ADD | BeamWeaponAbility base accuracy |
| PROJECTILE_STEALTH_LEVEL | SeekerWeaponAbility stealth |

### Set/Override (default None)

| StatKey | Typical Consumers |
|---------|-------------------|
| ARC_SET | WeaponAbility firing arc (overrides base value) |
