"""PROJ-359: Weapon family handler modules.

Each module in this package implements a `WeaponHandler` for one
`WeaponFamily` and registers itself with `WEAPON_REGISTRY` on import.

The firing system imports this package; importing this `__init__` triggers
all family registrations. Adding a new family is one new module + an import
here.
"""
from game.simulation.combat.families import beam  # noqa: F401  (registers BEAM)
from game.simulation.combat.families import projectile  # noqa: F401  (registers PROJECTILE)
from game.simulation.combat.families import seeker  # noqa: F401  (registers SEEKER)
