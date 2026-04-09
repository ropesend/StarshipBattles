"""Tick phase protocol and registry for BattleEngine.

Provides a pluggable tick phase system where each phase of the battle
simulation update is a discrete, registered object with a priority.
BattleEngine.update() delegates to TickPhaseRegistry.execute_all().

PROJ-259: Created to replace hardcoded phase sequence in BattleEngine.update().

Usage:
    registry = TickPhaseRegistry()
    registry.register(AIUpdatePhase())       # priority 100
    registry.register(WeaponPhase())         # priority 200
    registry.register(CollisionPhase())      # priority 300
    registry.register(ProjectilePhase())     # priority 400
    registry.register(PhysicsPhase())        # priority 500

    # In BattleEngine.update():
    registry.execute_all(self)

    # Custom phases can be added without modifying BattleEngine:
    registry.register(EnvironmentalPhase())  # priority 250
"""
import logging
from typing import Any, List, Protocol, runtime_checkable

logger = logging.getLogger(__name__)

__all__ = ['ITickPhase', 'TickPhaseRegistry']


@runtime_checkable
class ITickPhase(Protocol):
    """Protocol for a single phase of the battle engine tick loop.

    Implementations must provide:
        name: Human-readable phase name (for logging/debugging)
        priority: Execution order (lower = earlier). Phases with equal
                  priority execute in registration order.
        execute(engine): Perform the phase's work on the given engine.
    """

    @property
    def name(self) -> str: ...

    @property
    def priority(self) -> int: ...

    def execute(self, engine: Any) -> None: ...


class TickPhaseRegistry:
    """Ordered registry of tick phases, sorted by priority.

    Phases are executed in ascending priority order. Phases with equal
    priority maintain their registration order (stable sort).
    """

    def __init__(self):
        self._phases: List[ITickPhase] = []

    @property
    def phases(self) -> List[ITickPhase]:
        """Return the phases in execution order (sorted by priority)."""
        return list(self._phases)

    def register(self, phase: ITickPhase) -> None:
        """Register a tick phase. Re-sorts by priority (stable)."""
        self._phases.append(phase)
        self._phases.sort(key=lambda p: p.priority)

    def execute_all(self, engine: Any) -> None:
        """Execute all registered phases in priority order."""
        for phase in self._phases:
            phase.execute(engine)
