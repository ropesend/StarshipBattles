"""LayMinesOrderHandler — PROJ-FMS-B Phase 1 + QA Observation B.

Executes ``OrderType.LAY_MINES`` orders.

QA Observation B refactor: the action is now polymorphic across two
issuer kinds via :class:`IIssuerAdapter`:

  * Fleet-issued: the order's ``ship_instance_id`` selects a carrier
    ship in the issuing fleet; the adapter wraps that ``(fleet, ship)``
    pair and the mines come from ``ship.carried_items``.
  * Planet-issued: the engine builds a
    :class:`PlanetStagingYardIssuerAdapter` and the mines come from
    ``planet.staging_yard``.

The two code paths share :meth:`_run_with_issuer` below; the public
``execute_action_order(fleet, ...)`` entry kept for engine/registry
compatibility builds the fleet adapter from the order payload.

Order ``target`` payload is a dict::

    {
        'ship_instance_id': str,    # Carrier ship (fleet-issued path); None
                                    # / absent for planet-issued.
        'mine_design_id': str,      # Specific design to lay
        'count': int,               # How many to lay
        'target_hex': HexCoord,     # Where to lay (default = issuer.location)
    }
"""
from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
from game.strategy.engine.issuer_adapter import (
    FleetShipIssuerAdapter,
    IIssuerAdapter,
)
from game.strategy.engine.minefield_balance import (
    MinefieldBalance,
    load_minefield_balance,
)
from game.strategy.engine.order_handlers.base import (
    BaseOrderHandler,
    OrderExecutionResult,
)
from game.strategy.events.event_types import EventCategory, EventType

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.strategy.data.empire import Empire
    from game.strategy.data.galaxy import Galaxy
    from game.strategy.data.ship_instance import ShipInstance


# ---------------------------------------------------------------------------
# Scatter PRNG seeding helpers
# ---------------------------------------------------------------------------


def _stable_scatter_seed(
    seed_namespace: str,
    owner_id: int,
    hex_coord: HexCoord,
    launch_turn: int,
) -> int:
    """Build a stable, save-portable seed for the scatter PRNG."""
    payload = f"{seed_namespace}|{owner_id}|{hex_coord.q}|{hex_coord.r}|{launch_turn}"
    import hashlib

    digest = hashlib.sha1(payload.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False)


def _scatter_positions(
    count: int,
    seed: int,
    fallback_radius_m: float,
) -> List[Tuple[float, float]]:
    """Uniformly sample ``count`` positions inside a fallback circle."""
    rng = random.Random(seed)
    positions: List[Tuple[float, float]] = []
    for _ in range(count):
        u = rng.random()
        theta = rng.random() * 2.0 * 3.141592653589793
        r = fallback_radius_m * (u ** 0.5)
        positions.append((r * _cos(theta), r * _sin(theta)))
    return positions


def _cos(x: float) -> float:
    import math

    return math.cos(x)


def _sin(x: float) -> float:
    import math

    return math.sin(x)


# ---------------------------------------------------------------------------
# Handler
# ---------------------------------------------------------------------------


class LayMinesOrderHandler(BaseOrderHandler):
    """Handler for :data:`OrderType.LAY_MINES`."""

    def __init__(
        self,
        *,
        event_bus: Optional[Any] = None,
        planet_mutator: Optional[Any] = None,
        ship_mutator: Optional[Any] = None,
        balance: Optional[MinefieldBalance] = None,
    ) -> None:
        super().__init__(
            event_bus=event_bus,
            planet_mutator=planet_mutator,
            ship_mutator=ship_mutator,
        )
        self._balance = balance if balance is not None else load_minefield_balance()

    @property
    def supported_order_types(self) -> Tuple[OrderType, ...]:
        return (OrderType.LAY_MINES,)

    # ------------------------------------------------------------------
    # Execution — fleet entry point (engine-facing)
    # ------------------------------------------------------------------

    def execute_action_order(
        self,
        fleet: Fleet,
        empire: "Empire",
        galaxy: "Galaxy",
        component_registry: Optional[Dict[str, Any]] = None,
        empires: Optional[List["Empire"]] = None,
    ) -> OrderExecutionResult:
        order = fleet.get_current_order()
        if not order or order.type != OrderType.LAY_MINES:
            return OrderExecutionResult(success=False, message="Not a LAY_MINES order")

        payload = order.target
        if not isinstance(payload, dict):
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message="LAY_MINES order missing payload"
            )

        ship_instance_id = payload.get("ship_instance_id")
        carrier = self._find_ship(fleet, ship_instance_id) if ship_instance_id else None
        if carrier is None:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message=f"Ship {ship_instance_id} not in fleet"
            )

        issuer = FleetShipIssuerAdapter(fleet, carrier)
        return self._run_with_issuer(
            issuer=issuer,
            order_owner=fleet,
            empire=empire,
            galaxy=galaxy,
            payload=payload,
        )

    # ------------------------------------------------------------------
    # Polymorphic core
    # ------------------------------------------------------------------

    def execute_for_issuer(
        self,
        *,
        issuer: IIssuerAdapter,
        order_owner: Any,
        empire: "Empire",
        galaxy: "Galaxy",
    ) -> OrderExecutionResult:
        """Run the handler against any IIssuerAdapter (planet or fleet).

        ``order_owner`` is the entity whose ``orders`` queue holds the
        active order — usually the same as the wrapped fleet/planet.
        """
        order = order_owner.get_current_order()
        if not order or order.type != OrderType.LAY_MINES:
            return OrderExecutionResult(success=False, message="Not a LAY_MINES order")
        payload = order.target
        if not isinstance(payload, dict):
            order_owner.pop_order()
            return OrderExecutionResult(
                success=False, message="LAY_MINES order missing payload"
            )
        return self._run_with_issuer(
            issuer=issuer,
            order_owner=order_owner,
            empire=empire,
            galaxy=galaxy,
            payload=payload,
        )

    def _run_with_issuer(
        self,
        *,
        issuer: IIssuerAdapter,
        order_owner: Any,
        empire: "Empire",
        galaxy: "Galaxy",
        payload: Dict[str, Any],
    ) -> OrderExecutionResult:
        mine_design_id = payload.get("mine_design_id")
        count_raw = payload.get("count", 0)
        try:
            count = int(count_raw) if count_raw is not None else 0
        except (TypeError, ValueError):
            count = 0
        target_hex = payload.get("target_hex") or issuer.location

        if count <= 0:
            order_owner.pop_order()
            return OrderExecutionResult(
                success=False,
                message="LAY_MINES order requires count > 0",
            )
        # Normalise: an empty / falsy / "auto" design_id means "any mine"
        # so the handler's pop loop accepts any mine vehicle type.
        effective_design = mine_design_id if (mine_design_id and mine_design_id != "auto") else None

        # Try to pop exactly `count` matching mines.
        popped = issuer.pop_carried("mine", effective_design, count)
        if len(popped) < count:
            # Put back; fail cleanly with no partial consumption.
            issuer.append_carried(popped)
            order_owner.pop_order()
            available = issuer.count_carried("mine", effective_design)
            return OrderExecutionResult(
                success=False,
                message=(
                    f"Insufficient mines: requested {count} of design "
                    f"{mine_design_id!r}, available {available}"
                ),
            )

        mine_group = self._get_or_create_mine_group(
            empire=empire,
            target_hex=target_hex,
            current_turn=self._extract_turn(galaxy),
        )
        if not mine_group.ships:
            self._seed_mine_group_carrier(mine_group, empire=empire)
        for mine in popped:
            mine_group.ships[0].carried_items.append(mine)

        existing_count = len(mine_group.mine_positions)
        new_total = existing_count + len(popped)
        if mine_group.scatter_seed is None:
            mine_group.scatter_seed = _stable_scatter_seed(
                seed_namespace=self._balance.scatter.seed_namespace,
                owner_id=empire.id,
                hex_coord=target_hex,
                launch_turn=self._extract_turn(galaxy),
            )
        mine_group.mine_positions = _scatter_positions(
            count=new_total,
            seed=mine_group.scatter_seed,
            fallback_radius_m=self._balance.scatter.fallback_radius_m,
        )

        order_owner.pop_order()

        logger.info(
            "LayMinesOrderHandler: %s laid %d %s mines at %s (group_id=%s, total=%d)",
            issuer.display_label,
            len(popped),
            mine_design_id,
            target_hex,
            mine_group.id,
            len(mine_group.ships[0].carried_items) if mine_group.ships else 0,
        )
        try:
            self._emit_event(
                EventType.FACILITY_ACTIVATED,
                category=EventCategory.FLEET_OPERATIONS,
                empire_id=empire.id,
                message=(
                    f"Laid {len(popped)} {mine_design_id} mines at {target_hex} "
                    f"from {issuer.display_label} (group {mine_group.id})"
                ),
                location_hex=[target_hex.q, target_hex.r],
            )
        except Exception:  # Intentional broad catch: event-bus emission is best-effort; missing event types in older bus configurations must not break the lay-mines action.
            pass

        return OrderExecutionResult(success=True, message="Mines laid")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_ship(fleet: Fleet, ship_instance_id: str) -> Optional["ShipInstance"]:
        for ship in fleet.ships:
            if str(ship.instance_id) == str(ship_instance_id):
                return ship
        return None

    @staticmethod
    def _extract_turn(galaxy: Any) -> int:
        """Best-effort extraction of current turn for seeding."""
        for attr in ("current_turn", "turn", "turn_number"):
            t = getattr(galaxy, attr, None)
            if isinstance(t, int):
                return t
        return 0

    def _get_or_create_mine_group(
        self,
        empire: "Empire",
        target_hex: HexCoord,
        current_turn: int,
    ) -> Fleet:
        """Create a fresh ``mine_group`` Fleet for this lay action.

        PROJ-FMS-B audit Fix 4: each ``IssueLayMinesCommand`` produces
        its own mine_group — same-hex lays do NOT auto-merge.
        """
        new_id = self._mint_fleet_id(empire)
        group = Fleet(
            fleet_id=new_id,
            owner_id=empire.id,
            location=target_hex,
            speed=0.0,
            display_name=f"Minefield {new_id}",
            group_kind="mine_group",
        )
        group.sensitivity = "MED"
        group.expected_hit_chance_threshold = float(
            self._balance.laserhead.default_threshold
        )
        empire.fleets.append(group)
        return group

    @staticmethod
    def _mint_fleet_id(empire: "Empire") -> int:
        existing = {f.id for f in empire.fleets if isinstance(f.id, int)}
        candidate = 100000
        while candidate in existing:
            candidate += 1
        return candidate

    @staticmethod
    def _seed_mine_group_carrier(mine_group: Fleet, empire: "Empire") -> None:
        """Ensure the mine_group has its single synthetic carrier ship."""
        from game.strategy.data.ship_instance import ShipInstance

        carrier = ShipInstance(
            instance_id=f"mine_carrier_{mine_group.id}",
            design_id="mine_carrier_synthetic",
            name=f"Minefield {mine_group.id} Carrier",
            owner_id=empire.id,
            design_data={"name": "Mine Carrier", "vehicle_class": "Mine"},
            current_hp=0,
        )
        carrier.is_alive = True
        carrier.is_derelict = False
        mine_group.ships.append(carrier)


__all__ = ["LayMinesOrderHandler"]
