"""Component-lifecycle engine ABC (activation timer ticks).

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import path remains
`game.strategy.interfaces.engines.IComponentActivationEngine` via the
package `__init__.py` re-export seam.

Note: this ABC was previously missing from `engines.__all__`. PROJ-422
closes that drift — `IComponentActivationEngine` is now part of the
package's declared public surface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


__all__ = ['IComponentActivationEngine']


class IComponentActivationEngine(ABC):
    """
    Abstract interface for component activation timer processing.

    Ticks ComponentActivationState timers on planet facilities and fleet ships.
    States in ACTIVATING or DEACTIVATING phase advance by one tick.
    On phase transitions, updates parent entity's active_abilities.
    """

    @abstractmethod
    def process_activation_tick(
        self,
        tick: int,
        empires: List,
    ) -> List:
        """Process one tick of activation timers.

        Args:
            tick: Current tick number (1-100)
            empires: List of Empire objects to process

        Returns:
            List of transition event dicts
        """
        pass
