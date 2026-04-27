"""Ability source adapters for the unified IAbilitySource framework (PROJ-300).

Each adapter wraps a concrete entity (Facility, Storm, Planet, Star, etc.)
and exposes its abilities through the `IAbilitySource` protocol. The unified
`ability_iterator` yields adapters from a registered list of providers; the
`system_effects_collector` walks the iterator and aggregates per-scope.

PROJ-300 ships:
- FacilityAbilitySource — wraps a planetary facility's components
- StormAbilitySource — wraps a Storm entity

PROJ-301..305 add their own adapters (planet intrinsic, star, warp point,
system archetype, fleet) by importing `register_source_provider` from
`ability_iterator` and registering one new provider function.

**Adapter rule (post-PROJ-306):** adapters that touch ship/component data
take `registry_provider` (or equivalent) via constructor injection. Never
call `get_default_registry_provider()` or any module-level registry getter
from inside an adapter — see PROJ-300 design.md task 4.5.
"""

from .facility import FacilityAbilitySource
from .storm import StormAbilitySource
from .planet_intrinsic import PlanetIntrinsicAbilitySource  # PROJ-301
from .star import StarAbilitySource  # PROJ-302
from .warp_point import WarpPointAbilitySource  # PROJ-303
from .system_archetype import SystemAbilitySource  # PROJ-304
from .intrinsic_roll import roll_intrinsic_abilities
from .labels import format_intrinsic_source_label

__all__ = [
    'FacilityAbilitySource',
    'StormAbilitySource',
    'PlanetIntrinsicAbilitySource',
    'StarAbilitySource',
    'WarpPointAbilitySource',
    'SystemAbilitySource',
    'roll_intrinsic_abilities',
    'format_intrinsic_source_label',
]
