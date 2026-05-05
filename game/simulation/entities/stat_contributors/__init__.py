"""
Stat contributors — per-domain logic extracted from `ShipStatsCalculator`.

PROJ-360 Phase 2 split the monolithic calculator into one module per stat
domain (movement, defense, weapons, command, launch). The calculator now
*coordinates* the phase order; each contributor module owns the data
aggregation and ship mutation for its domain.

Contributor signatures intentionally mirror the helper signatures the
calculator used pre-refactor (`comp, acc` or `ship, comp, acc`) so the
extraction is mechanical and the golden output is preserved bit-for-bit.

Public surface for downstream consumers should still go through
`ShipStatsCalculator.calculate(ship)`. These modules are an internal
decomposition; they are not a stable API.
"""
from game.simulation.entities.stat_contributors import (
    accumulator,
    command,
    defense,
    launch,
    movement,
    registry,
    weapons,
)
from game.simulation.entities.stat_contributors.accumulator import StatAccumulator

# PROJ-367 Phase 2: seed built-in Phase-3 contributors AFTER the four domain
# modules finish loading. Doing this from within registry.py would trigger
# a circular import — command/defense/launch/movement all import names
# from registry.py.
registry._seed_builtin_contributors()

__all__ = [
    "accumulator",
    "command",
    "defense",
    "launch",
    "movement",
    "registry",
    "weapons",
    "StatAccumulator",
]
