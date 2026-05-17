"""Terraforming engine ABCs (planet-quality, atmosphere, water).

PROJ-422 (TD-09): extracted verbatim from the former
`game/strategy/interfaces/engines.py` monolith. Symbol-preserving;
the public import paths remain
`game.strategy.interfaces.engines.IQualityEngine`,
`game.strategy.interfaces.engines.IAtmosphereEngine`, and
`game.strategy.interfaces.engines.IWaterEngine` via the package
`__init__.py` re-export seam.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


__all__ = ['IQualityEngine', 'IAtmosphereEngine', 'IWaterEngine']


class IQualityEngine(ABC):
    """Abstract interface for per-turn planet-quality improvement.

    PROJ-369 Phase 2: Promoted from locally-constructed to injectable
    via TurnEngineConfig. Runs ONCE per turn during the end-of-turn
    block, after population growth.
    """

    @abstractmethod
    def process_quality_improvement(self, empires: List) -> None:
        """Process planet-quality changes for all empires (once per turn).

        Args:
            empires: List of Empire objects to process.
        """
        pass


class IAtmosphereEngine(ABC):
    """Abstract interface for per-turn atmosphere modification.

    PROJ-369 Phase 2: Promoted from locally-constructed to injectable
    via TurnEngineConfig. Runs ONCE per turn during the end-of-turn
    block, after the quality phase.
    """

    @abstractmethod
    def process_atmosphere(self, empires: List) -> None:
        """Process atmosphere changes for all empires (once per turn).

        Args:
            empires: List of Empire objects to process.
        """
        pass


class IWaterEngine(ABC):
    """Abstract interface for per-turn water-level modification.

    PROJ-369 Phase 2: Promoted from locally-constructed to injectable
    via TurnEngineConfig. Runs ONCE per turn during the end-of-turn
    block, after the atmosphere phase.
    """

    @abstractmethod
    def process_water_modification(self, empires: List) -> None:
        """Process water-level changes for all empires (once per turn).

        Args:
            empires: List of Empire objects to process.
        """
        pass
