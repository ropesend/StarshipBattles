# Visibility And Scanning Design Notes

This document records the current agreed design direction for visibility, detection, sensors, scanning, scan blocking, ghost contacts, and player-facing enemy contacts.

It is a planning document only. Implementation should occur later through the existing `Projects/` system.

## Current Agreement Summary

The current design direction is:

1. Visibility is ability-driven.
2. Visibility is channel-based and extensible.
3. Detection and scanning are separate systems.
4. Ship detection is resolved per ship, not per fleet.
5. Enemy-visible objects should generally be represented as contacts, not raw enemy fleets.
6. Ships can hide inside fleets; the player should infer uncertainty, not be told there are hidden ships.
7. Cloaking, stealth, scan blocking, jamming, and environmental effects are never absolute.
8. Activity can alter detectability.
9. Damage can alter detectability.
10. Environments should affect visibility/scanning through abilities.
11. Component-level scanning is binary: exact component/status information is either available or not.
12. Planets and warp points use special object-specific detection logic, but still fit into the broader detection/scanning model.
13. The whole model should be data-driven and extensible.

## Core Principle

The visibility system should not hardcode specific component names such as crystalline armor, scattering armor, cloaking devices, scanners, or jammers. Instead, components should contribute visibility-related abilities, scanner abilities, and scan-blocking abilities.

The same ability system should support:

- Hull size.
- Armor properties.
- Reactor output.
- Shields.
- Weapons fire.
- Warp activation.
- Movement.
- Toggleable abilities.
- Active scanners.
- Active jammers.
- Environmental effects.
- Damage-related emissions.
- Psychic crew signatures.

## Detection Versus Scanning

Detection and scanning answer different questions.

| System | Question | Result |
|---|---|---|
| Detection / visibility | Does the observer know this object exists? | Contact or no contact. |
| Identification / classification | How much non-component detail does the observer know? | Unknown contact, size class, owner, design name, etc. |
| Component scanning | Can the observer see exact components and component status? | Yes/no for exact component/status display. |

Component scanning should be binary. If the scan succeeds, show exact component list and status. If it fails, do not show component internals.

## Visibility Channels

Visibility should be divided into extensible channels. These should ideally be registry-defined IDs, similar in spirit to the existing resource system, so new channels can be added by data or mods while invalid IDs can still be detected.

Initial suggested channels:

| Channel | Meaning / Examples |
|---|---|
| `optical` | Visual/radar-like profile, hull reflectivity, armor surface effects. |
| `thermal` | Heat from engines, reactors, weapons, damage, life support. |
| `radiation` | Reactor leakage, shields, weapons, high-energy systems. |
| `gravitic` | Mass, warp drive effects, large hulls, artificial gravity. |
| `subspace` | Warp/subspace drive emissions and exotic FTL effects. |
| `psychic` | Biological crew/passengers, psionic systems, psychic weapons. |

No sensor type should be universally best. Different sensors should detect different channels. A fleet might be invisible to optical sensors but obvious to gravitic or psychic sensors under the right conditions.

Examples:

- A crewed ship may emit psychic signature from crew/life aboard.
- An AI-controlled ship with no crew may have no psychic detectability unless it carries psychic components or passengers.
- A fleet may remain hidden until it warps, creating a gravitic/subspace spike.
- A ship firing a high-energy weapon may emit a large thermal/radiation/optical event.

## Visibility Abilities

A general visibility-related ability should be attachable to components, hulls, temporary states, environmental effects, and active/toggleable abilities.

Possible ability family names:

- `VisibilityEmitterAbility`
- `VisibilityModifierAbility`
- `TemporaryVisibilityEventAbility`
- `EnvironmentalVisibilityAbility`

The exact class names can change during implementation, but the design intent is that visibility effects are contributed by abilities rather than by hardcoded component-specific rules.

Suggested fields:

| Field | Purpose |
|---|---|
| `channels` | One or more affected visibility channels. |
| `operation` | Add, multiply, set minimum, set maximum, etc. |
| `value` | Numeric modifier. |
| `scope` | Self, ship, fleet, sector, system, etc. |
| `state` | Passive, active, triggered, damaged, destroyed, etc. |
| `duration` | For temporary activity or damage spikes. |
| `damage_scaling` | Rule for how component damage affects the modifier. |

## Examples Of Visibility Abilities

### Hull Size

Hull size should not require separate hardcoded logic for ships. The hull component can carry visibility abilities.

Example:

```text
Large Battleship Hull:
- optical add 80
- gravitic add 40
```

### Crystalline Armor

Crystalline armor should increase visibility through abilities.

Example:

```text
Crystalline Armor:
- optical add 20
- radiation add 10
```

### Scattering Armor

Scattering armor should reduce visibility through abilities.

Example:

```text
Scattering Armor:
- optical multiply 0.75
- radiation multiply 0.90
```

### Cloaking Device

A cloaking device should generally reduce visibility, but never make detection impossible.

Example:

```text
Cloaking Device active:
- optical multiply 0.25
- thermal multiply 0.45
- radiation multiply 0.60
```

### Warp Drive Activation

Warp activation should create a major temporary signature spike.

Example:

```text
Warp Drive activated:
- gravitic add 200 for a short duration
- subspace add 300 for a short duration
```

A fleet may remain hidden until it warps, at which point the warp signature can reveal at least some contacts.

## Activity-Based Visibility

Activities should affect visibility through temporary or active abilities.

Possible activities:

| Activity | Possible Visibility Effect |
|---|---|
| Normal movement | Small thermal/gravitic increase. |
| High-speed movement | Larger thermal/gravitic increase. |
| Warp activation | Major gravitic/subspace spike. |
| Firing laser/beam weapons | Optical/thermal/radiation spike. |
| Firing missiles | Thermal launch plume, perhaps lower radiation. |
| Firing psychic weapon | Psychic spike. |
| Active scanning | Sensor-channel emission, making the scanner ship easier to detect. |
| Active jamming | Increased emissions, increased scan resistance. |
| Shields active | Energy/radiation visibility increase. |
| Getting hit | Thermal/radiation/optical spike. |

Getting hit should be especially visible. The hit may reveal the location/contact of the target or attacker depending on the event and sensor model, but it should not automatically reveal full component details.

## Damage-Scaled Visibility

Visibility abilities should be able to define how their effect changes with damage.

Possible damage-scaling modes:

| Mode | Meaning |
|---|---|
| `constant` | Modifier is unchanged by damage. |
| `reduced_when_damaged` | Component effect weakens as it is damaged. Useful for cloaks/stealth systems. |
| `increased_when_damaged` | Damaged component leaks more heat/radiation/etc. Useful for reactors. |
| `disabled_when_destroyed` | Effect disappears when destroyed. |
| `spikes_when_hit` | Temporary event generated when the component is hit. |
| `custom_curve` | Data-defined curve. |

Examples:

- A damaged cloaking device should provide less visibility reduction.
- A damaged reactor may leak radiation/thermal signature.
- Armor being hit may create a temporary thermal/optical/radiation spike.

## Environmental Visibility

Environment should also be ability-based. Sector, system, or larger-scope effects can hide or expose ships by modifying signatures, sensor effectiveness, or background noise.

Environmental effects should support at least two concepts:

1. Modify emitted signatures.
2. Modify sensors/background noise.

Examples:

```text
Nebula sector:
- optical signatures multiply 0.4
- radiation signatures multiply 0.7
- thermal signatures multiply 0.8
```

```text
Pulsar system:
- radiation background noise add 100
- radiation sensor effectiveness multiply 0.5
- optical exposure add 20
```

```text
Psychic storm:
- psychic background noise add 200
- psychic sensor effectiveness multiply 0.2
```

## Sensor Abilities

Sensors should be ability-driven and channel-aware.

Possible ability family names:

- `SensorAbility`
- `PassiveSensorAbility`
- `ActiveSensorAbility`

A sensor ability should define:

| Field | Purpose |
|---|---|
| `channels` | Which visibility channels the sensor can detect. |
| `strength` | Base detection strength. |
| `range` | Effective range or range curve. |
| `mode` | Passive or active. |
| `active_visibility_cost` | Signature emitted when actively scanning. |
| `environment_modifiers` | Optional interactions with environment. |

Passive sensors should usually be weaker but not increase own detectability.

Active sensors should be toggleable, stronger, and make the scanning ship/fleet more detectable through visibility abilities.

Important: Active scanner emissions should be generated by the specific ship/component using the active sensor. That may reveal that ship while other ships in the same fleet remain separately resolved.

## Scanning And Scan Blocking

Scanning is separate from detection.

Possible ability family names:

- `ScannerAbility`
- `ScanBlockingAbility`
- `ActiveScannerJammerAbility`

Scanner abilities determine whether component-level information can be viewed.

Scan-blocking abilities oppose this.

Active scanner jammers are an important tradeoff: when active, they should make a ship more detectable but harder to scan.

Example:

```text
Active Scanner Jammer:
Visibility effect while active:
- radiation add 80
- subspace add 40

Scan-blocking effect while active:
- component scan resistance add 150
```

No scan-blocking effect should be absolute. A sufficiently strong or specialized scanner should be able to overcome it.

## Component Scanning Rule

Component scanning should be exact and binary.

Example conceptual formula:

```text
can_view_components = scanner_strength_at_range >= target_scan_resistance
```

If true:

- Show exact components.
- Show exact component status/stats, if the scanner has the required ability.

If false:

- Show no component internals.

It should be possible for high-end scanner tech to reveal precise component stats and component health/status.

Scanner ability and sensor/detection ability should be independent, though many components may provide both.

## Detection Pipeline

For each observing empire:

```text
1. Collect sensor sources:
   - owned ships
   - owned colonies
   - owned satellites
   - owned sensor stations
   - future allied/shared sensors if allowed

2. Collect candidate objects:
   - enemy ships individually
   - planets
   - warp points
   - deployed groups
   - relevant phenomena

3. For each candidate object:
   - build emitted visibility profile by channel
   - apply component abilities
   - apply activity abilities
   - apply damage scaling
   - apply environment modifiers

4. For each observing sensor:
   - compare sensor strength by channel against target signatures, range, and environmental noise
   - determine whether target is detected

5. If detected:
   - create or update current contact
   - update empire intel memory

6. If no longer detected but remembered:
   - emit a remembered/ghost contact
```

## Per-Ship Detection, Not Fleet Detection

Ship detection should be resolved per ship. A fleet should not have a single visibility value.

A fleet with easily seen ships and hard-to-see ships may appear to the opponent as only the easily seen ships.

The player should not be told that there are undetected ships. Hidden ships should be inferred from uncertainty, behavior, or later discovery.

Fleet-level effects may still exist, but they should modify per-ship calculations rather than replacing them.

Example:

```text
Stealth Field Generator:
- scope: fleet
- optical multiply 0.8
```

This helps each ship in the fleet, but every ship is still detected or not detected independently.

## Enemy Contacts Instead Of Enemy Fleets

Enemy-visible forces should generally be represented as contacts rather than raw fleet objects.

Reason: multiple fleets can exist in the same sector, and only some ships from each fleet may be visible. Presenting an enemy fleet object may reveal too much structure.

Recommended concept:

```text
SectorContact:
- sector_hex
- observer_empire_id
- detected_ship_contacts[]
- detected_planet_contacts[]
- detected_warp_point_contacts[]
- detected_deployed_group_contacts[]
- remembered_contacts[]
```

Recommended ship contact fields:

```text
ShipContact:
- contact_id
- last_seen_turn
- last_seen_tick
- location
- owner_id, if known
- empire_name, if known
- ship_id, if identified
- fleet_id, usually hidden or unknown
- size_class, if known
- design_name, if identified
- component_status, if scanned
```

Owned fleets can still display as actual fleets. Enemy forces should be displayed as contacts unless/until the design specifically allows fleet identity to be known.

## Contact Identity Levels

Enemy ship IDs should not automatically be known just because a ship was detected.

Possible identity levels:

| Level | Meaning |
|---|---|
| Unknown contact | Something was detected, but no persistent object identity is known. |
| Tracked contact | The same contact is being tracked while continuously visible. |
| Identified ship | Persistent ship identity/design is known. |
| Scanned ship | Components/status are known. |

This prevents free information leakage when a similar ship is detected later.

## Planets

Agreed direction:

- Planet detection should be based on planet size.
- Planet size/class can be known once detected.
- Colony presence should require appropriate sensors/scanners.
- Colony details should require stronger scanning.
- Exact stockpiles/build queues should probably not be visible without espionage, conquest, or explicit future mechanics.

Possible model:

```text
Planet detection:
- size only

Colony detection:
- sensor/scanner dependent

Colony detail:
- scanner dependent
```

## Warp Points

Warp points should have variable detectability.

Agreed direction:

- Some warp points are easy to see.
- Some warp points are hard to see.
- Warp points can be created and destroyed.
- Future mechanics may allow warp points to be altered.

Possible warp-point visibility traits:

| Warp Point Type / State | Visibility |
|---|---|
| Massive stable warp point | Easy to detect. |
| Normal warp point | Detectable with standard sensors nearby. |
| Weak/natural hidden warp point | Hard to detect. |
| Artificial stealth warp point | Very hard to detect. |
| Recently created/opened warp point | Temporary high signature. |
| Collapsing/unstable warp point | High signature, possibly dangerous. |

Warp points should behave like objects with signatures and visibility abilities where practical.

## No Absolute Detection Or Scan Blocking

No detectability or scanability effect should be absolute. This includes:

- Cloaking.
- Scattering armor.
- Scanner jamming.
- Scan blocking.
- Environmental concealment.
- Psychic invisibility.

All effects should be data-driven modifiers that can be overcome by appropriate sensor/scanner strength, range, channel choice, or future specialized tech.

## Determinism Recommendation

Detection and scanning should ideally be deterministic rather than random.

The player may experience uncertainty because they do not know what they failed to detect, but the server/session should be able to compute visibility from stable state, range, abilities, activity, damage, and environment.

Avoid per-turn random rolls for whether something is visible unless a future design intentionally adds uncertainty as a separate mechanic.

## Open Implementation Questions

These questions remain for later detailed design before implementation:

1. Should visibility channels be stored in a registry file, and what should that schema look like?
2. Should detection produce tiered results such as contact/classified/identified based on margin above threshold?
3. What are the exact formulas for channel signatures, sensor strength, range penalty, and environmental noise?
4. How should active sensor toggles be represented in orders and turn processing?
5. How long should activity spikes last: ticks, subturns, full turns, or configurable durations?
6. How should remembered contacts degrade or become uncertain over time?
7. Which component status fields are visible after a successful scan?
8. Should scan blocking have channels/categories, or should there initially be one component-scan resistance value?
9. Should allied sensor sharing exist, and if so, when?
10. How should combat events update intel memory for involved and uninvolved empires?

## Future Project Slices

When implementation begins, use the existing `Projects/` system. Possible project slices:

1. Add visibility-channel registry and validation.
2. Add visibility ability schema and aggregation service.
3. Add sensor ability schema and detection resolver.
4. Add scanner and scan-blocking ability schema.
5. Add per-ship detection and enemy contact DTOs.
6. Add activity/damage visibility events.
7. Add environmental visibility effects.
8. Add planet and warp-point detection integration.
9. Add intel memory and ghost contacts.
10. Convert the strategy UI from enemy fleets to contacts.
