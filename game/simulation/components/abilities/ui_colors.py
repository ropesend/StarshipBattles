"""Centralized color constants for ability UI display hints (PROJ-167).

These hex color strings are used in ability get_ui_rows() methods to provide
semantic color hints for UI rendering. The UI layer uses these hints to colorize
ability information in component detail panels.

Color categories:
- Weapons & Offense: Red/orange/yellow tones for damage-related values
- Defense & Shields: Cyan/blue tones for protective capabilities
- Propulsion: Green/blue tones for movement values
- Crew & Support: Pale green/cyan for crew-related values
- Cargo & Resources: Gold/green for storage and production
- Special: Distinct colors for superweapons and requirements
- Neutral/Default: Gray/white fallbacks
"""

# Weapons & Offense
HINT_DAMAGE = '#FF6464'           # Red — damage values, targeting offense
HINT_RANGE = '#FFA500'            # Orange — weapon range, fuel consumption
HINT_RELOAD = '#FFC864'           # Gold — reload time
HINT_PROJECTILE_SPEED = '#C8C832' # Dirty yellow — projectile speed, ammo consumption
HINT_ACCURACY = '#FFFF00'         # Bright yellow — beam accuracy, damage ignore, energy gen, harvest rate

# Defense & Shields
HINT_SHIELD_CAP = '#00FFFF'       # Cyan — shield capacity, warp capable, construction bonus
HINT_SHIELD_REGEN = '#00C8FF'     # Deep sky blue — shield regeneration
HINT_EVASION = '#64FFFF'          # Light cyan — evasion, default resource storage

# Propulsion
HINT_THRUST = '#64FF64'           # Light green — combat thrust
HINT_TURN_SPEED = '#64FF96'       # Mint green — maneuver/turn speed
HINT_STRATEGIC_MOBILITY = '#6496FF' # Slate blue — strategic movement
HINT_WARP_ENERGY = '#64C8FF'      # Light blue — warp energy, energy consumption

# Crew & Support
HINT_CREW_CAP = '#96FF96'         # Pale green — crew capacity, command, structural integrity, optional modifier
HINT_LIFE_SUPPORT = '#96FFFF'     # Pale cyan — life support capacity
HINT_CREW_REQ = '#FF9696'         # Pale red — crew requirement

# Cargo & Resources
HINT_CARGO_PASSENGER = '#98FB98'  # Pale green (web) — passenger cargo
HINT_CARGO_GENERIC = '#FFD700'    # Gold — generic cargo, mandatory modifier
HINT_COLONIZE = '#00FF00'         # Bright green — colonization, resource harvesting, production

# Special
HINT_SUPERWEAPON = '#FF4444'      # Dark red — all superweapon abilities
HINT_REQUIREMENT = '#FFCC66'      # Tan/light orange — requires C&C, requires propulsion

# Neutral / Default
HINT_NEUTRAL = '#C8C8C8'          # Light gray — hangar, cycle time, fallback
HINT_DEFAULT = '#FFFFFF'          # White — max tonnage, default resource types


__all__ = [
    # Weapons & Offense
    'HINT_DAMAGE',
    'HINT_RANGE',
    'HINT_RELOAD',
    'HINT_PROJECTILE_SPEED',
    'HINT_ACCURACY',
    # Defense & Shields
    'HINT_SHIELD_CAP',
    'HINT_SHIELD_REGEN',
    'HINT_EVASION',
    # Propulsion
    'HINT_THRUST',
    'HINT_TURN_SPEED',
    'HINT_STRATEGIC_MOBILITY',
    'HINT_WARP_ENERGY',
    # Crew & Support
    'HINT_CREW_CAP',
    'HINT_LIFE_SUPPORT',
    'HINT_CREW_REQ',
    # Cargo & Resources
    'HINT_CARGO_PASSENGER',
    'HINT_CARGO_GENERIC',
    'HINT_COLONIZE',
    # Special
    'HINT_SUPERWEAPON',
    'HINT_REQUIREMENT',
    # Neutral / Default
    'HINT_NEUTRAL',
    'HINT_DEFAULT',
]
