"""Planetary-scope abilities package (PROJ-382 Phase 5 decomposition).

Originally ``planetary.py`` (~913 LOC). Split into per-responsibility
sub-modules; this ``__init__`` re-exports every Ability so legacy
imports ``from game.simulation.components.abilities.planetary import X``
continue to work without modification.
"""

from .shields import (
    PlanetaryShieldAbility,
    RadiationShieldAbility,
)
from .stabilizers import (
    GeologicStabilizerAbility,
    StellarStabilizerAbility,
    WarpFieldStabilizerAbility,
)
from .resource_modifiers import (
    StrategicResourceGenerationAbility,
    ResourceHarvestBoosterAbility,
    BuildRateBoosterAbility,
)
from .stat_modifiers import (
    ShieldModifierAbility,
    DamageModifierAbility,
    ThrustModifierAbility,
    StrategicSpeedModifierAbility,
)
from .terraforming import (
    AtmosphereModifierAbility,
    QualityImprovementAbility,
    GravityModifierAbility,
    WaterModifierAbility,
)
from .environmental import (
    EnvironmentalDamageAbility,
    FuelDrainAbility,
)

__all__ = [
    "PlanetaryShieldAbility",
    "RadiationShieldAbility",
    "GeologicStabilizerAbility",
    "StellarStabilizerAbility",
    "WarpFieldStabilizerAbility",
    "StrategicResourceGenerationAbility",
    "ResourceHarvestBoosterAbility",
    "BuildRateBoosterAbility",
    "ShieldModifierAbility",
    "DamageModifierAbility",
    "ThrustModifierAbility",
    "StrategicSpeedModifierAbility",
    "AtmosphereModifierAbility",
    "QualityImprovementAbility",
    "GravityModifierAbility",
    "WaterModifierAbility",
    "EnvironmentalDamageAbility",
    "FuelDrainAbility",
]
