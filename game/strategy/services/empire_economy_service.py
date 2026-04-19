"""Service-layer facade over `EmpireEconomyCalculator` (PROJ-292 M1).

UI panels must not import from `game.strategy.engine.*` directly per
[docs/01_ARCHITECTURE.md § Layer Rules](../../../docs/01_ARCHITECTURE.md). This
facade exposes the read surface — the calculator stays in the engine
layer. UI code consumes `EmpireEconomyService.get_snapshot(empire)` to
obtain an `EmpireEconomySnapshot`; it never touches the calculator
class directly.

The `EmpireEconomySnapshot` dataclass is re-exported here so UI code
that needs the type annotation doesn't need to reach into the engine
module. The engine-layer calculator itself is intentionally NOT in
`__all__` — it's an implementation detail.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from game.strategy.engine.empire_economy_calculator import (
    EmpireEconomyCalculator,
    EmpireEconomySnapshot,
)

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.core.registry import GameRegistries
    from game.strategy.config.economy_config import EconomyConfig
    from game.strategy.data.empire import Empire


class EmpireEconomyService:
    """Read-only snapshot service over `EmpireEconomyCalculator`.

    One method: `get_snapshot(empire) -> EmpireEconomySnapshot`. The
    service owns a calculator instance and forwards every call to it.
    Construction kwargs mirror the calculator's so callers migrate with
    identical argument shape.
    """

    def __init__(
        self,
        *,
        registries: "GameRegistries",
        economy_config: Optional["EconomyConfig"] = None,
        race_registry: Optional["IRaceRegistry"] = None,
    ) -> None:
        """Initialise the service.

        Args:
            registries: `GameRegistries` for resolving component abilities
                (required — no fallback).
            economy_config: Optional `EconomyConfig` driving per-resource
                population upkeep aggregation. When None, upkeep
                aggregation is skipped (treasury row auto-hides).
            race_registry: Optional `IRaceRegistry` used by the
                calculator's habitability-multiplier path. When None,
                upkeep aggregation is skipped (see `EmpireEconomyCalculator`).
        """
        self._calculator = EmpireEconomyCalculator(
            registries=registries,
            economy_config=economy_config,
            race_registry=race_registry,
        )

    def get_snapshot(self, empire: "Empire") -> EmpireEconomySnapshot:
        """Return a fresh `EmpireEconomySnapshot` for the given empire."""
        return self._calculator.calculate(empire)


__all__ = ["EmpireEconomyService", "EmpireEconomySnapshot"]
