"""LayMinesOrderHandler — PROJ-FMS-B Phase 1.

Executes ``OrderType.LAY_MINES`` orders: pops N mines from the issuing
ship's :class:`VehicleBay` and creates / extends a ``mine_group`` Fleet
for the owner at the target hex.

Strategic-flow contract mirrors :class:`ColonizeHandler`:

    Command -> OrderType.LAY_MINES -> LayMinesOrderHandler

Order ``target`` payload is a dict::

    {
        'ship_instance_id': str,    # The carrier ship in the issuing fleet
        'mine_design_id': str,      # Specific design to lay
        'count': int,               # How many to lay
        'target_hex': HexCoord,     # Where to lay (default = fleet.location)
    }
"""
from __future__ import annotations

import logging
import random
from typing import Any, Dict, List, Optional, TYPE_CHECKING, Tuple

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import OrderType
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
    # Use Python's stable str -> int hash via hashlib for determinism
    # across runs (built-in hash() is salted between processes).
    import hashlib

    digest = hashlib.sha1(payload.encode("utf-8")).digest()
    # Take first 8 bytes as unsigned int — plenty for a PRNG seed.
    return int.from_bytes(digest[:8], "big", signed=False)


def _scatter_positions(
    count: int,
    seed: int,
    fallback_radius_m: float,
) -> List[Tuple[float, float]]:
    """Uniformly sample ``count`` positions inside a fallback circle.

    Used at strategic launch time when no tactical battle map exists yet.
    The same seed always produces the same layout (see Phase 3 for the
    battle-map-bounded variant).
    """
    rng = random.Random(seed)
    positions: List[Tuple[float, float]] = []
    for _ in range(count):
        # Uniform sample in a circle via the standard radius-sqrt trick.
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
    # Execution
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
        mine_design_id = payload.get("mine_design_id")
        count = int(payload.get("count", 0))
        target_hex = payload.get("target_hex") or fleet.location

        if not ship_instance_id or not mine_design_id or count <= 0:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message="LAY_MINES order requires ship_instance_id, mine_design_id, count > 0",
            )

        # Locate the carrier ship in the fleet.
        carrier = self._find_ship(fleet, ship_instance_id)
        if carrier is None:
            fleet.pop_order()
            return OrderExecutionResult(
                success=False, message=f"Ship {ship_instance_id} not in fleet"
            )

        # Pop N matching mines from the carrier's VehicleBay.
        popped = self._pop_mines(carrier, mine_design_id, count)
        if len(popped) < count:
            # Put any popped mines back — fail cleanly without partial consumption.
            for m in popped:
                carrier.carried_items.append(m)
            fleet.pop_order()
            return OrderExecutionResult(
                success=False,
                message=(
                    f"Insufficient mines: requested {count} of design "
                    f"{mine_design_id!r}, available "
                    f"{self._count_matching_mines(carrier, mine_design_id)}"
                ),
            )

        # Locate or create a mine_group Fleet for this owner at the target hex.
        mine_group = self._get_or_create_mine_group(
            empire=empire,
            target_hex=target_hex,
            current_turn=self._extract_turn(galaxy),
        )

        # Append the mines into the mine_group's carrier (mine_group has
        # one synthetic carrier whose ``carried_items`` IS the inventory).
        if not mine_group.ships:
            self._seed_mine_group_carrier(mine_group, empire=empire)
        # Always append at index 0 (mine_group has exactly one ship-ID slot).
        for mine in popped:
            mine_group.ships[0].carried_items.append(mine)

        # Update / extend the scatter positions.
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

        fleet.pop_order()

        logger.info(
            "LayMinesOrderHandler: %s laid %d %s mines at %s "
            "(group_id=%s, total=%d)",
            empire.name if hasattr(empire, "name") else f"Empire {empire.id}",
            len(popped),
            mine_design_id,
            target_hex,
            mine_group.id,
            len(mine_group.ships[0].carried_items) if mine_group.ships else 0,
        )
        # Use a generic-but-existing event type. Mine-specific event
        # types can be added in a later refactor; for now use the
        # generic FACILITY_ACTIVATED to surface the action in the log.
        try:
            self._emit_event(
                EventType.FACILITY_ACTIVATED,
                category=EventCategory.FLEET_OPERATIONS,
                empire_id=empire.id,
                message=(
                    f"Laid {len(popped)} {mine_design_id} mines at {target_hex} "
                    f"(group {mine_group.id})"
                ),
                fleet_id=fleet.id,
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
    def _pop_mines(
        carrier: "ShipInstance",
        mine_design_id: str,
        count: int,
    ) -> List[Dict[str, Any]]:
        """Pop up to ``count`` matching mines from ``carrier.carried_items``."""
        popped: List[Dict[str, Any]] = []
        remaining_items: List[Dict[str, Any]] = []
        for item in carrier.carried_items:
            if len(popped) >= count:
                remaining_items.append(item)
                continue
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "mine":
                remaining_items.append(item)
                continue
            if cv.design_id != mine_design_id:
                remaining_items.append(item)
                continue
            popped.append(item)
        carrier.carried_items = remaining_items
        return popped

    @staticmethod
    def _count_matching_mines(carrier: "ShipInstance", mine_design_id: str) -> int:
        n = 0
        for item in carrier.carried_items:
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != "mine":
                continue
            if cv.design_id == mine_design_id:
                n += 1
        return n

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
        its own mine_group — same-hex lays do NOT auto-merge. The
        shared design specifies "Multiple groups per owner per hex
        permitted; no auto-merge" and the Phase 1 checklist agrees.
        The player can selectively destroy individual groups via the
        :class:`MineGroupService.self_destruct` action (Fix 4 in
        PROJ-FMS-A and Phase 4's selective self-destruct still work).
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
        # Defaults from balance:
        group.sensitivity = "MED"
        group.expected_hit_chance_threshold = float(
            self._balance.laserhead.default_threshold
        )
        empire.fleets.append(group)
        return group

    @staticmethod
    def _mint_fleet_id(empire: "Empire") -> int:
        """Allocate a non-colliding fleet id for a new mine_group."""
        existing = {f.id for f in empire.fleets if isinstance(f.id, int)}
        # Start from 100000 so we don't collide with player-built fleet ids.
        candidate = 100000
        while candidate in existing:
            candidate += 1
        return candidate

    @staticmethod
    def _seed_mine_group_carrier(mine_group: Fleet, empire: "Empire") -> None:
        """Ensure the mine_group has its single synthetic carrier ship.

        The carrier is a placeholder ShipInstance whose ``carried_items``
        list IS the minefield's inventory. It is never a real combatant —
        the conflict-resolution engine treats mine_groups as
        non-combat-capable.
        """
        from game.strategy.data.ship_instance import ShipInstance

        carrier = ShipInstance(
            instance_id=f"mine_carrier_{mine_group.id}",
            design_id="mine_carrier_synthetic",
            name=f"Minefield {mine_group.id} Carrier",
            owner_id=empire.id,
            design_data={"name": "Mine Carrier", "vehicle_class": "Mine"},
            current_hp=0,
        )
        # PROJ-FMS-A audit fix 4a: carrier is a strategy-layer-only
        # placeholder, marked non-combat to keep conflict resolution sane.
        carrier.is_alive = True
        carrier.is_derelict = False
        mine_group.ships.append(carrier)


__all__ = ["LayMinesOrderHandler"]
