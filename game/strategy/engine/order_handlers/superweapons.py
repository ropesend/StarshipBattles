"""SuperweaponHandlerAdapter -- bridges `SUPERWEAPONS` specs into the
order-handler registry (PROJ-368 Phase 4).

The 5 spec-driven strategic superweapons (IMPLODE_PLANET,
STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT,
CREATE_DYSON_SPHERE) keep their existing implementations on
`SuperweaponOrderProcessor` (PROJ-364 stabilized that path). Each spec
gets a thin adapter here that:

  1. Looks up the matching `process_*` method on the processor.
  2. Calls it with the legacy signature.
  3. Reshapes the returned `SuperweaponResult` to an
     `OrderExecutionResult`.

`SELF_DESTRUCT` is **not** in `SUPERWEAPONS` -- it was lifted to its
own first-class `SelfDestructHandler` in Phase 2.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple
import logging

from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.services.superweapon_registry import (
    SuperweaponSpec,
    SUPERWEAPONS,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.engine.superweapon_order_processor import (
        SuperweaponOrderProcessor,
    )


class SuperweaponHandlerAdapter(BaseOrderHandler):
    """Adapter wrapping a single `SuperweaponOrderProcessor.process_*` method."""

    def __init__(
        self,
        *,
        spec: SuperweaponSpec,
        processor: "SuperweaponOrderProcessor",
    ) -> None:
        super().__init__(event_bus=None)  # adapter does not emit directly
        self._spec = spec
        self._processor = processor

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (self._spec.order_type,)

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        """Forward to `SuperweaponOrderProcessor.process_<order_type_lower>`."""
        method_name = f"process_{self._spec.order_type.name.lower()}"
        method = getattr(self._processor, method_name)
        # Spec-driven processors share a uniform 5-arg signature:
        # (fleet, empire, galaxy, empires, component_registry).
        result = method(fleet, empire, galaxy, empires or [], component_registry)
        return OrderExecutionResult(
            success=result.success,
            fleet_consumed=result.fleet_consumed,
            message=result.message,
        )


def build_superweapon_handlers(
    processor: "SuperweaponOrderProcessor",
) -> List[SuperweaponHandlerAdapter]:
    """Build one `SuperweaponHandlerAdapter` per spec in `SUPERWEAPONS`.

    `SELF_DESTRUCT` is intentionally NOT in `SUPERWEAPONS`; defensive
    skip-guard added so a future accidental addition does not collide
    with `SelfDestructHandler` already registered against
    `OrderType.SELF_DESTRUCT`.
    """
    adapters: List[SuperweaponHandlerAdapter] = []
    for spec in SUPERWEAPONS:
        if spec.order_type == OrderType.SELF_DESTRUCT:
            logger.warning(
                "build_superweapon_handlers: skipping SELF_DESTRUCT in SUPERWEAPONS "
                "(handled by SelfDestructHandler)"
            )
            continue
        adapters.append(SuperweaponHandlerAdapter(spec=spec, processor=processor))
    return adapters
