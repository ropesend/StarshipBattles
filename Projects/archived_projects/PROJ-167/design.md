# PROJ-167: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current State
- **370 Python files** in `game/`, ~96K lines
- **51 hardcoded hex color_hint values** across 11 ability files in `game/simulation/components/abilities/`
- **25 unique hex colors** used as ability display hints
- **~200+ hardcoded RGB tuples** across UI panels, renderers, and screens
- **27 test assertions** checking specific color_hint hex values
- **1 existing color file**: `game/ui/colors.py` with UI theme colors (RGB tuples only)

### Architecture Constraint
- `game/simulation/` has ZERO imports from `game/ui/` — this is a hard layer boundary
- Abilities import from `game/core/` (config, constants, logger) — established pattern
- `game/ui/` imports from both `game/core/` and `game/simulation/`
- PROJ-113 moved rendering colors FROM core TO ui — established precedent

### Color Consumer
- Only consumer of `color_hint`: `game/ui/screens/builder/detail_panel.py:144`
- Pattern: `color = row.get('color_hint', '#C8C8C8')` → renders as `<font color='{color}'>`
- Fallback color: `#C8C8C8` (light gray)

## Swarm Findings Summary

### Architecture
Two-file approach respects layer boundaries:
1. **`game/simulation/components/abilities/ui_colors.py`** — 25 `HINT_*` constants (hex strings)
2. **`game/ui/colors.py`** — extend with categorized RGB tuple constants

### Key Patterns to Reuse
- **`game/core/constants.py`**: Flat module-level constants with `__all__` export list
- **`game/ui/colors.py:COLORS` dict**: Grouped by semantic category (bg, border, text, accent)
- **Existing constant naming**: ALL_CAPS with underscores, descriptive names

### Dependencies & Risks
1. **Test assertions checking exact hex values** — 27 assertions in 6 test files need updating to import constants instead of hardcoded strings. Low risk, mechanical change.
2. **No circular import risk** — ability files already import from game.core; new file is within same package.
3. **detail_panel.py hardcoded colors** — `#96FF96` (optional modifier) and `#FFD700` (mandatory modifier) should also move to the ability ui_colors module since they're part of the same display system.

### Opportunities Discovered
- The `resources.py` ability has a runtime color selection pattern (switch on ResourceType) that can use constants elegantly
- Superweapons all share `#FF4444` — one constant eliminates 6 duplications
- detail_panel.py fallback `#C8C8C8` should be a named constant

## Ability Color Palette Reference

| Constant Name | Hex Value | Used By |
|--------------|-----------|---------|
| HINT_DAMAGE | #FF6464 | WeaponAbility, ToHitAttackModifier |
| HINT_RANGE | #FFA500 | WeaponAbility |
| HINT_RELOAD | #FFC864 | WeaponAbility |
| HINT_PROJECTILE_SPEED | #C8C832 | ProjectileWeaponAbility |
| HINT_ACCURACY | #FFFF00 | BeamWeaponAbility, EmissiveArmor, ResourceGeneration(energy) |
| HINT_SHIELD_CAP | #00FFFF | ShieldProjection, ResourceStorage(shield), WarpJump, SpaceShipyardAbility |
| HINT_SHIELD_REGEN | #00C8FF | ShieldRegeneration |
| HINT_EVASION | #64FFFF | ToHitDefenseModifier, ResourceStorage(default) |
| HINT_THRUST | #64FF64 | CombatPropulsion |
| HINT_TURN_SPEED | #64FF96 | ManeuveringThruster |
| HINT_STRATEGIC_MOBILITY | #6496FF | StrategicMovement |
| HINT_WARP_ENERGY | #64C8FF | WarpJump, ResourceConsumption(energy) |
| HINT_CREW_CAP | #96FF96 | CrewCapacity, CommandAndControl, StructuralIntegrity |
| HINT_LIFE_SUPPORT | #96FFFF | LifeSupportCapacity |
| HINT_CREW_REQ | #FF9696 | CrewRequired |
| HINT_FUEL | #FFA500 | ResourceConsumption(fuel) — same as HINT_RANGE |
| HINT_AMMO | #C8C832 | ResourceConsumption(ammo) — same as HINT_PROJECTILE_SPEED |
| HINT_CARGO_PASSENGER | #98FB98 | CargoStorage(passengers) |
| HINT_CARGO_GENERIC | #FFD700 | CargoStorage(generic) |
| HINT_SUPERWEAPON | #FF4444 | All 6 superweapon abilities |
| HINT_COLONIZE | #00FF00 | ColonizePlanet, ResourceHarvester, SpaceShipyard(production) |
| HINT_HARVEST_RATE | #FFFF00 | EmpireStorageAbility — same as HINT_ACCURACY |
| HINT_NEUTRAL | #C8C8C8 | VehicleLaunchAbility (hangar, cycle), detail_panel fallback |
| HINT_DEFAULT | #FFFFFF | WarpJump(max tonnage), ResourceConsumption/Generation(default), SpaceShipyard(mass) |
| HINT_REQUIREMENT | #FFCC66 | RequiresCommandAndControl, RequiresCombatMovement |
| HINT_MODIFIER_OPTIONAL | #96FF96 | detail_panel.py optional modifier — same as HINT_CREW_CAP |
| HINT_MODIFIER_MANDATORY | #FFD700 | detail_panel.py mandatory modifier — same as HINT_CARGO_GENERIC |

### Color Aliasing
Several colors are semantically reused:
- `#FFA500` = HINT_RANGE = HINT_FUEL (orange for "resource cost" / "distance")
- `#C8C832` = HINT_PROJECTILE_SPEED = HINT_AMMO (yellow for "ammunition-related")
- `#FFFF00` = HINT_ACCURACY = HINT_HARVEST_RATE (bright yellow)
- `#00FFFF` = HINT_SHIELD_CAP (cyan for "capacity/capability")
- `#96FF96` = HINT_CREW_CAP = HINT_MODIFIER_OPTIONAL (pale green for "support")
- `#FFD700` = HINT_CARGO_GENERIC = HINT_MODIFIER_MANDATORY (gold)
- `#00FF00` = HINT_COLONIZE (bright green for "production/colonization")

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
