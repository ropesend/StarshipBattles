"""
Fleet data class.

OrderSerializer extracted to order_serializer.py (PROJ-210).
"""

import logging
from typing import List, Optional, Tuple, TYPE_CHECKING, Any, Dict

from game.core.hex_math import HexCoord
from game.core.protocols import IPostBattleShip
from game.core.exceptions import PersistenceException
from game.core.error_codes import ErrorCode
from game.core.validation_helpers import require_keys
from game.strategy.data.fleet_battle_adapter import FleetBattleAdapter
from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
from game.strategy.data.fleet_pursuer_tracker import FleetPursuerTracker
from game.strategy.data.fleet_consumable_aggregator import FleetConsumableAggregator
from game.strategy.data.fleet_hierarchy import CombatPolicy
from game.strategy.data.ship_instance import ShipInstance

# PROJ-212: OrderType, Order, and order type sets extracted to order_types.py
# PROJ-238: FleetOrder renamed to Order
from game.strategy.data.order_types import (
    OrderType,
    Order,
    MOVEMENT_ORDER_TYPES,
    ACTION_ORDER_TYPES,
)

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.strategy.data.planet import Planet
    from game.strategy.data.task_force import TaskForce


class Fleet:
    """
    Represents a fleet of ships on the Strategy Map.

    Ships are stored as ShipInstance objects with full state tracking.
    """

    def __init__(
        self,
        fleet_id,
        owner_id,
        location,
        speed=5.0,
        component_registry: Optional[Dict[str, Any]] = None,
        display_name: str = "",
        group_kind: str = "fleet",
    ):
        self.id = fleet_id
        self.owner_id = owner_id  # 0=Player, 1=Enemy, etc
        self.location = location  # HexCoord
        self._component_registry = component_registry
        self.display_name = display_name  # Renamable label; empty = fallback to "Fleet {id}"

        # PROJ-FMS-A Phase 4: discriminator for fleet-vs-deployed-group.
        # Values: "fleet" (real fleet, full Move/Build/Warp surface),
        # "fighter_group" / "satellite_group" / "mine_group" (deployed groups
        # — auto-joinable to combat, but reject strategic movement / build /
        # warp). Enforced at command-validation time in
        # game/strategy/engine/handlers/{movement,build}.py.
        if group_kind not in ("fleet", "fighter_group", "satellite_group", "mine_group"):
            raise ValueError(
                f"Fleet.group_kind={group_kind!r} must be one of "
                f"fleet/fighter_group/satellite_group/mine_group"
            )
        self.group_kind = group_kind

        # PROJ-FMS-B Phase 1: minefield-specific runtime fields populated
        # only for ``group_kind == "mine_group"``. They default to safe
        # values on non-mine groups so consumers can read them
        # unconditionally without ``hasattr`` guards.
        #
        # ``sensitivity``: one of "LOW" / "MED" / "HIGH" — warhead trigger
        #     multiplier (see ``minefield_balance.MinefieldBalance``).
        # ``expected_hit_chance_threshold``: float in [0.0, 1.0] — the
        #     deterministic continuous gate on the laserhead pass.
        # ``mine_positions``: List[Tuple[float, float]] — scatter coords
        #     of the mines in tactical-map units. Populated at strategic
        #     launch time and persisted across saves.
        # ``scatter_seed``: int — stable PRNG seed for the scatter layout
        #     so re-entries / re-loads produce the same layout.
        self.sensitivity: str = "MED"
        self.expected_hit_chance_threshold: float = 0.30
        self.mine_positions: List[Tuple[float, float]] = []
        self.scatter_seed: Optional[int] = None

        # Master ship list (flat, canonical list of all ships in the fleet)
        self.ships: List[ShipInstance] = []

        # Fleet hierarchy: organizational overlay for combat behavior
        # Task forces and squadrons reference ships from self.ships.
        # Ships not assigned to any task force fight with fleet-level defaults.
        self._task_forces: List['TaskForce'] = []
        self.fleet_policy: CombatPolicy = CombatPolicy()

        # Movement & Orders
        self.speed = float(speed)
        self.orders: List[Order] = []
        self.path: List[HexCoord] = []  # Current movement path for the ACTIVE Move order

        # Production (for fleets with space yards)
        self.construction_queue: List[Dict[str, Any]] = []
        # FEAT-17: When True, ProductionEngine skips this fleet's space-yard
        # queue — no cargo draw, no progress increment. Fleet yards share one
        # queue, so this is per-fleet (not per-yard) granularity.
        self.construction_queue_paused: bool = False

        # Delegate for resource aggregation (PROJ-87 Phase 3)
        self._resource_agg = FleetConsumableAggregator(self)

        # Delegate for capability queries (PROJ-87 Phase 4)
        # PROJ-211: Pass component_registry for DI
        self._capabilities = FleetCapabilityCalculator(self, component_registry)

        # Delegate for battle conversion (PROJ-87 Phase 4)
        self._battle = FleetBattleAdapter(self)

        # Delegate for pursuer tracking (PROJ-222)
        self._pursuer_tracker = FleetPursuerTracker(self)

    # --- Fleet Hierarchy ---

    @property
    def can_strategic_move(self) -> bool:
        """PROJ-FMS-A Phase 4: only ``group_kind == "fleet"`` may move.

        Deployed groups (``fighter_group`` / ``satellite_group`` /
        ``mine_group``) reject Move / Intercept / Warp / Build /
        Join-Fleet at command validation time.
        """
        return self.group_kind == "fleet"

    @property
    def task_forces(self) -> List['TaskForce']:
        """Task forces in this fleet (organizational overlay for combat)."""
        return self._task_forces

    def add_task_force(self, task_force: 'TaskForce') -> None:
        """Add a task force to this fleet."""
        if task_force not in self._task_forces:
            self._task_forces.append(task_force)

    def remove_task_force(self, task_force: 'TaskForce') -> bool:
        """Remove a task force. Returns True if found and removed."""
        if task_force in self._task_forces:
            self._task_forces.remove(task_force)
            return True
        return False

    def get_unassigned_ships(self) -> List[ShipInstance]:
        """Ships not assigned to any task force or squadron.

        These are ships in self.ships whose instance_id does not appear
        in any task force's hierarchy.
        """
        assigned_ids = set()
        for tf in self._task_forces:
            for ship in tf.all_ships:
                assigned_ids.add(ship.instance_id)
        return [s for s in self.ships if s.instance_id not in assigned_ids]

    @property
    def name(self) -> str:
        """Renamable display name for the fleet.

        Returns display_name if set, otherwise falls back to "Fleet {id}".
        """
        if self.display_name:
            return self.display_name
        return f"Fleet {self.id}"

    @property
    def composition_summary(self) -> str:
        """Ship composition summary for tooltips.

        Returns a descriptive string based on fleet contents.
        """
        ship_count = len(self.ships)
        if ship_count == 0:
            return "Empty fleet"
        elif ship_count == 1:
            return self.ships[0].name
        else:
            return f"{ship_count} ships"

    @property
    def context_type(self) -> str:
        """Return 'fleet' for BuildContext protocol compliance."""
        return "fleet"

    def add_ship(self, ship: ShipInstance) -> None:
        """Add a ShipInstance to the fleet."""
        self.ships.append(ship)
        self.trigger_speed_recalculation()

    def remove_ship(self, ship: ShipInstance) -> bool:
        """Remove a ship from the fleet. Returns True if found and removed."""
        if ship in self.ships:
            self.ships.remove(ship)
            self.trigger_speed_recalculation()
            return True
        return False

    def trigger_speed_recalculation(self) -> None:
        """
        Trigger fleet speed recalculation based on current ship composition.

        Fleet speed is the minimum of all combat-capable ships' speeds,
        ensuring the fleet moves at the pace of its slowest member.

        This is a public method because external delegates (FleetBattleAdapter)
        need to trigger recalculation after modifying the ship roster.
        """
        # INTENTIONAL LATE IMPORT: Edge operation (only on ship add/remove)
        # See docs/ARCHITECTURE.md "Intentional Late Imports" section
        from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator
        FleetSpeedCalculator.update_fleet_speed(self)

    def get_ship_names(self) -> List[str]:
        """Get names of all ships in the fleet."""
        return [s.name for s in self.ships]

    def get_combat_capable_ships(self) -> List[ShipInstance]:
        """Get ships capable of combat (not destroyed or derelict)."""
        return [s for s in self.ships if s.is_combat_capable()]

    @property
    def capabilities(self) -> 'FleetCapabilityCalculator':
        """Public access to fleet capability queries."""
        return self._capabilities

    @property
    def resources(self) -> 'FleetConsumableAggregator':
        """Public access to fleet resource aggregation."""
        return self._resource_agg

    # --- Cargo Resource Methods (for fleet construction) ---

    def has_cargo_resources(self, costs: Dict[str, float]) -> bool:
        """Check if fleet cargo contains all required resources.

        Aggregates cargo_contents across all ships in the fleet.

        Args:
            costs: Dict mapping resource_type -> required amount.

        Returns:
            True if all resources are available as cargo.
        """
        for resource_type, amount in costs.items():
            total = self._resource_agg.get_fleet_cargo_current(resource_type)
            if total < amount:
                return False
        return True

    def consume_cargo_resource(self, resource_type: str, amount: float) -> bool:
        """Consume resources from fleet cargo (all-or-nothing).

        Unloads the specified amount across fleet ships. If insufficient
        cargo exists, no deduction is made.

        Args:
            resource_type: Resource identifier (e.g., "metals").
            amount: Amount to consume.

        Returns:
            True if successful, False if insufficient.
        """
        total = self._resource_agg.get_fleet_cargo_current(resource_type)
        if total < amount:
            return False
        self._resource_agg.unload_cargo_from_fleet(resource_type, int(round(amount)))
        return True

    def get_cargo_resource(self, resource_type: str) -> float:
        """Get total cargo of a resource type across all fleet ships."""
        return float(self._resource_agg.get_fleet_cargo_current(resource_type))

    @property
    def battle(self) -> 'FleetBattleAdapter':
        """Public access to fleet battle conversion."""
        return self._battle

    @property
    def pursuer_tracker(self) -> 'FleetPursuerTracker':
        """Public access to fleet pursuer tracking (PROJ-222)."""
        return self._pursuer_tracker

    @property
    def is_building(self) -> bool:
        """
        Check if fleet is currently executing a BUILD order.

        Returns True when the current (first) order is BUILD.
        """
        current = self.get_current_order()
        return current is not None and current.type == OrderType.BUILD

    # NOTE: PROJ-210 Phase 2 removed pass-through methods.
    # Use fleet.capabilities.*, fleet.resources.*, fleet.battle.* directly.

    def _unregister_from_target(self, order: Order) -> None:
        """Unregister this fleet from the target fleet's pursuer tracker.

        Called when an order is removed from the queue. Only acts on
        MOVE_TO_FLEET/JOIN_FLEET orders with a Fleet target that has
        a pursuer_tracker. Only unregisters if no remaining orders in
        the queue still target the same fleet (PROJ-222).
        """
        if order.type in (OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET):
            target = order.target
            if hasattr(target, 'pursuer_tracker'):
                # Check if any remaining order still targets this fleet
                still_targeting = any(
                    o.type in (OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET)
                    and o.target is target
                    for o in self.orders
                )
                if not still_targeting:
                    target.pursuer_tracker.remove_pursuer(self)

    def add_order(self, order: Order, index: Optional[int] = None) -> None:
        """Add an order to the queue."""
        if index is None:
            self.orders.append(order)
        else:
            self.orders.insert(index, order)

    def clear_orders(self) -> None:
        """Clear all orders and the current path."""
        # PROJ-222: Unregister from all target fleets before clearing.
        # Collect unique targets first, then unregister (since all orders are being removed,
        # we bypass _unregister_from_target's "still targeting" check).
        targets_to_unregister = set()
        for order in self.orders:
            if hasattr(order, 'type') and order.type in (OrderType.MOVE_TO_FLEET, OrderType.JOIN_FLEET):
                target = order.target
                if hasattr(target, 'pursuer_tracker'):
                    targets_to_unregister.add(target)
        self.orders.clear()
        self.path = []
        for target in targets_to_unregister:
            target.pursuer_tracker.remove_pursuer(self)

    def get_current_order(self) -> Optional[Order]:
        """Get the current (first) order, or None if queue is empty."""
        if not self.orders:
            return None
        return self.orders[0]

    def pop_order(self) -> Optional[Order]:
        """Remove and return the current order, or None if queue is empty."""
        if self.orders:
            finished = self.orders.pop(0)
            self._unregister_from_target(finished)
            self.path = []  # Clear path associated with that order
            return finished
        return None

    def remove_order_at(self, index: int) -> Optional[Order]:
        """Remove and return the order at the given index.

        Clears the path if the active order (index 0) is removed.
        Returns None if the index is out of bounds.
        """
        if index < 0 or index >= len(self.orders):
            return None
        removed = self.orders.pop(index)
        self._unregister_from_target(removed)
        if index == 0:
            self.path = []
        return removed

    def remove_orders_by_type(self, order_type: OrderType) -> List[Order]:
        """Remove all orders of the given type. Returns the removed orders."""
        removed = [o for o in self.orders if o.type == order_type]
        for order in removed:
            self._unregister_from_target(order)
        self.orders = [o for o in self.orders if o.type != order_type]
        return removed

    def remove_orders_by_type_and_target(
        self,
        order_types: frozenset[OrderType],
        target: 'Fleet',
    ) -> List[Order]:
        """Remove all orders matching both an order-type set and a Fleet target.

        Used by BUG-122 fix: when a pursuer is excluded from redirect_pursuers
        (because it would create a self-target cycle), its now-stale pursuit
        orders against the absorbed fleet must be dropped.

        Returns the removed orders.
        """
        removed: List[Order] = []
        remaining: List[Order] = []
        removed_active_order = False
        for index, order in enumerate(self.orders):
            if order.type in order_types and order.target is target:
                removed.append(order)
                removed_active_order = removed_active_order or index == 0
            else:
                remaining.append(order)

        if not removed:
            return []

        self.orders = remaining
        for order in removed:
            self._unregister_from_target(order)
        if removed_active_order:
            self.path = []
        return removed

    def merge_with(self, other_fleet: 'Fleet', event_bus=None) -> None:
        """
        Merge this fleet into other_fleet.
        Transfers all ships and clears this fleet.

        PROJ-222: Before clearing orders, redirects all pursuers of this
        fleet to other_fleet and logs FLEET_JOIN_REDIRECTED events.

        Args:
            other_fleet: Fleet to merge into.
            event_bus: Optional EventBus for structured event logging.
        """
        if not isinstance(other_fleet, Fleet):
            return

        # PROJ-222: Redirect all pursuers to other_fleet BEFORE clearing orders
        # (clear_orders would unregister from targets, but redirect must happen first)
        # BUG-122: Exclude other_fleet from redirect — it must not become a
        # pursuer of itself if it had a JOIN_FLEET order targeting self.
        from game.strategy.data.fleet_pursuer_tracker import PURSUIT_ORDER_TYPES
        from game.strategy.events.event_types import EventType, EventCategory
        # PROJ-382 Phase 2 (Pattern #10): emit only via injected event_bus.
        redirected, excluded = self._pursuer_tracker.redirect_pursuers(
            other_fleet,
            exclude=frozenset({other_fleet}),
        )

        for pursuer, _old_target in redirected:
            if event_bus is not None:
                event_bus.log_event(
                    EventType.FLEET_JOIN_REDIRECTED,
                    category=EventCategory.FLEET_OPERATIONS,
                    empire_id=pursuer.owner_id,
                    message=f"Fleet {pursuer.id} join order redirected from Fleet {self.id} to Fleet {other_fleet.id}",
                    fleet_id=pursuer.id,
                    old_target_id=self.id,
                    new_target_id=other_fleet.id,
                )

        # BUG-122: Drop excluded pursuers' stale orders targeting self and
        # emit FLEET_JOIN_CANCELLED so the player sees why they vanished.
        for pursuer in excluded:
            pursuer.remove_orders_by_type_and_target(PURSUIT_ORDER_TYPES, self)
            logger.warning(
                f"[BUG-122] Fleet {pursuer.id} pursuit orders dropped during merge "
                f"of Fleet {self.id} into Fleet {other_fleet.id}: would have created self-join"
            )
            if event_bus is not None:
                event_bus.log_event(
                    EventType.FLEET_JOIN_CANCELLED,
                    category=EventCategory.FLEET_OPERATIONS,
                    empire_id=pursuer.owner_id,
                    message=f"Fleet {pursuer.id} join order cancelled: would have self-targeted Fleet {other_fleet.id}",
                    fleet_id=pursuer.id,
                    target_fleet_id=self.id,
                    reason="self_target_after_redirect",
                )

        # Transfer ships
        other_fleet.ships.extend(self.ships)
        self.ships.clear()
        self._task_forces.clear()

        # Clear orders (this fleet is effectively gone)
        self.clear_orders()

        # Recalculate speed for the target fleet (new composition)
        other_fleet.trigger_speed_recalculation()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for save game."""
        ships_data = [s.to_dict() for s in self.ships]

        location_data = None
        if isinstance(self.location, HexCoord):
            location_data = {'q': self.location.q, 'r': self.location.r}
        elif isinstance(self.location, tuple):
            location_data = list(self.location)

        data: Dict[str, Any] = {
            'id': self.id,
            'owner_id': self.owner_id,
            'location': location_data,
            'speed': self.speed,
            'display_name': self.display_name,
            'ships': ships_data,
            'orders': [o.to_dict() for o in self.orders],
            'path': [{'q': p.q, 'r': p.r} if isinstance(p, HexCoord) else list(p) if isinstance(p, tuple) else p for p in self.path],
            'construction_queue': self.construction_queue,
            'construction_queue_paused': self.construction_queue_paused,
            # PROJ-FMS-A Phase 4: discriminator for fleet vs deployed group.
            'group_kind': self.group_kind,
        }

        # PROJ-FMS-B Phase 1: serialise minefield runtime state only when
        # populated. Non-mine fleets carry defaults that round-trip as
        # absent fields (keeps existing saves clean).
        if self.group_kind == "mine_group":
            data['sensitivity'] = self.sensitivity
            data['expected_hit_chance_threshold'] = float(
                self.expected_hit_chance_threshold
            )
            if self.mine_positions:
                data['mine_positions'] = [list(p) for p in self.mine_positions]
            if self.scatter_seed is not None:
                data['scatter_seed'] = int(self.scatter_seed)

        # Serialize hierarchy
        if self._task_forces:
            data['task_forces'] = [tf.to_dict() for tf in self._task_forces]

        fleet_policy_data = self.fleet_policy.to_dict()
        if fleet_policy_data:
            data['fleet_policy'] = fleet_policy_data

        return data

    @classmethod
    def from_dict(
        cls,
        data: Dict[str, Any],
        registries: Optional['GameRegistries'] = None
    ) -> 'Fleet':
        """
        Deserialize from save game.

        Args:
            data: Dict with fleet data
            registries: Optional GameRegistries for DI. If provided, ships
                and FleetCapabilityCalculator will use these registries.

        Returns:
            Reconstructed Fleet

        Raises:
            PersistenceException: If required keys missing
        """
        # PROJ-210: Order deserialization delegated to OrderSerializer
        from game.strategy.data.order_serializer import OrderSerializer

        require_keys(data, ['id', 'owner_id'], 'Fleet')

        location = data.get('location')
        if isinstance(location, dict) and 'q' in location and 'r' in location:
            location = HexCoord(location['q'], location['r'])
        elif isinstance(location, list):
            location = HexCoord(location[0], location[1])

        # PROJ-211: Extract component_registry from registries for DI
        component_registry = registries.components if registries else None

        fleet = cls(
            fleet_id=data['id'],
            owner_id=data['owner_id'],
            location=location,
            speed=data.get('speed', 5.0),
            component_registry=component_registry,
            display_name=data.get('display_name', ''),
            # PROJ-FMS-A Phase 4. Defaulted to "fleet" so saves predating
            # this field still deserialise (no migration shim required).
            group_kind=data.get('group_kind', 'fleet'),
        )

        # PROJ-FMS-B Phase 1: restore minefield runtime state. Absent
        # fields fall back to the constructor defaults (MED sensitivity /
        # 0.30 threshold / empty positions / None seed).
        if 'sensitivity' in data:
            fleet.sensitivity = str(data['sensitivity'])
        if 'expected_hit_chance_threshold' in data:
            fleet.expected_hit_chance_threshold = float(
                data['expected_hit_chance_threshold']
            )
        if 'mine_positions' in data:
            fleet.mine_positions = [
                (float(p[0]), float(p[1]))
                for p in data['mine_positions']
                if isinstance(p, (list, tuple)) and len(p) >= 2
            ]
        if 'scatter_seed' in data:
            fleet.scatter_seed = int(data['scatter_seed'])

        # PROJ-251: Strict deserialization — corrupt ships fail the load
        for i, ship_data in enumerate(data.get('ships', [])):
            try:
                ship = ShipInstance.from_dict(ship_data, registries=registries)
                fleet.ships.append(ship)
            except (PersistenceException, KeyError, TypeError, ValueError) as e:
                raise PersistenceException(
                    f"Corrupt ship data at index {i} in fleet '{data.get('id', '?')}'",
                    code=ErrorCode.CORRUPT_DATA.value,
                    context={"fleet_id": data.get('id'), "ship_index": i, "original_error": str(e)}
                ) from e

        # Restore fleet hierarchy
        from game.strategy.data.task_force import TaskForce
        for tf_data in data.get('task_forces', []):
            fleet._task_forces.append(TaskForce.from_dict(tf_data))

        # Restore fleet-level combat policy
        if 'fleet_policy' in data:
            fleet.fleet_policy = CombatPolicy.from_dict(data['fleet_policy'])

        # Restore path
        for p in data.get('path', []):
            if isinstance(p, dict) and 'q' in p and 'r' in p:
                fleet.path.append(HexCoord(p['q'], p['r']))
            elif isinstance(p, list):
                fleet.path.append(HexCoord(p[0], p[1]))
            else:
                fleet.path.append(p)

        # PROJ-210: Restore orders using serializer
        fleet.orders = OrderSerializer.deserialize_orders(
            data.get('orders', []),
            data['id']
        )

        # Restore construction queue
        fleet.construction_queue = data.get('construction_queue', [])
        fleet.construction_queue_paused = data.get('construction_queue_paused', False)

        # PROJ-320 audit: deliberately do NOT call trigger_speed_recalculation
        # here. The saved `speed` field IS the slowest-ship speed at save
        # time; recalculating would require ships with valid get_calculated_stats(),
        # which test fixtures and minimal save formats may not provide.
        # If a real save-format mismatch ever surfaces in production play,
        # fix at the save-format layer, not by recalculating on load.

        return fleet

    def resolve_order_references(self, galaxy: Any, empires: List[Any]) -> None:
        """
        Resolve order target references after deserialization.

        During from_dict(), order targets that reference Fleets or Planets are stored
        as marker dicts (_fleet_ref, _planet_ref). This method resolves those markers
        to actual object references.

        Orders with unresolvable references (deleted fleets/planets) are removed
        with a warning.

        Args:
            galaxy: Galaxy object with get_planet_by_id() method
            empires: List of Empire objects containing all fleets
        """
        # PROJ-210: Delegate to OrderSerializer
        from game.strategy.data.order_serializer import OrderSerializer
        OrderSerializer.resolve_order_references(self, galaxy, empires)

    def __repr__(self):
        ship_count = len(self.ships)
        return f"Fleet({self.id}, Owner:{self.owner_id}, Loc:{self.location}, Ships:{ship_count}, Spd:{self.speed})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Fleet):
            return NotImplemented
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)
