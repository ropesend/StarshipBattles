"""Polymorphic issuer adapter for FMS order handlers (QA Observation B).

Background — both fleets AND planets can now issue strategic FMS orders
(``LAY_MINES``, ``LAUNCH_FIGHTERS``, ``LAUNCH_SATELLITES``,
``RECOVER_FIGHTERS``, ``RECOVER_SATELLITES``). Previously every order
handler reached directly into ``fleet.ships[i].carried_items``; widening
that contract one handler at a time would duplicate the new
planet-staging-yard branch in five places.

This module introduces :class:`IIssuerAdapter` and two concrete
implementations:

- :class:`FleetShipIssuerAdapter` wraps the existing
  ``(Fleet, ShipInstance)`` shape so order handlers can keep operating
  through one accessor surface. PROJ-431 Phase 1b routes all reads &
  writes through :attr:`ShipInstance.bay_inventory` /
  :meth:`ShipInstance.set_bay_inventory` instead of the legacy
  ``carried_items`` mixed list.
- :class:`PlanetStagingYardIssuerAdapter` wraps a :class:`Planet`'s
  ``staging_yard`` so the same handlers can serve planet-issued FMS
  actions without a parallel handler family. The staging yard is
  out-of-scope for PROJ-431 Phase 1b and remains a dict list for now.

The adapter intentionally exposes the *minimum* set of fields the five
handlers touch today. New ops must extend this surface explicitly so the
contract stays small.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Protocol, runtime_checkable

from game.core.hex_math import HexCoord
from game.strategy.data.bay_inventory import BayInventory, DropPod
from game.strategy.data.carried_vehicle import (
    VALID_VEHICLE_TYPES,
    CarriedVehicle,
)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.planet import Planet
    from game.strategy.data.ship_instance import ShipInstance


@runtime_checkable
class IIssuerAdapter(Protocol):
    """Polymorphic interface for FMS order issuers (fleet ship or planet).

    Implementations expose just the slice of fleet/planet that the five
    FMS order handlers need: a strategic location, an owner, a display
    label, and a pair of carried-vehicle pop / append primitives.
    """

    @property
    def location(self) -> HexCoord:
        """Strategic hex where the issuer resides."""
        ...

    @property
    def owner_id(self) -> int:
        """Empire id that owns the issuer."""
        ...

    @property
    def display_label(self) -> str:
        """Short human-readable label, e.g. ``"Fleet 7"`` / ``"Planet Foo"``."""
        ...

    def pop_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
        count: Optional[int],
    ) -> List[Any]:
        """Pop matching carried vehicles from the issuer's inventory.

        Args:
            vehicle_type: ``"mine"`` / ``"fighter"`` / ``"satellite"``.
            design_id: Specific design or ``None``/``"auto"`` for any.
            count: Number to pop. ``None`` => pop all matching.

        Returns:
            List of popped items (raw dicts as stored in the source list).
            Empty list when nothing matched.
        """
        ...

    def count_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
    ) -> int:
        """Count matching carried vehicles still on the issuer."""
        ...

    def append_carried(self, items: List[Any]) -> int:
        """Append items back to the issuer's inventory.

        Returns the number of items successfully appended (partial
        success is allowed when the planet staging yard reaches its
        ``max_staging_mass`` cap).
        """
        ...

    def append_recovered(self, vehicle: CarriedVehicle) -> bool:
        """Append a recovered vehicle to the issuer (capacity-checked).

        Returns ``True`` when the vehicle was stored. The fleet-ship
        adapter routes through the ship's cargo manager bay-fit logic;
        the planet adapter checks ``max_staging_mass``.
        """
        ...


def _matches(item: Any, vehicle_type: str, design_id: Optional[str]) -> bool:
    """Shared filter predicate used by both adapters.

    Accepts both raw dict items (planet staging yard — pre-Phase-1b
    substrate, still on the legacy mixed-shape list) and typed
    :class:`CarriedVehicle` instances (fleet-ship bay — Phase-1b
    substrate).

    PROJ-431 Phase 1f: the legacy ``CarriedVehicle.from_any(...)``
    discriminator is gone. Replaced with an explicit isinstance check
    plus a dict-shape probe against
    :data:`~game.strategy.data.carried_vehicle.VALID_VEHICLE_TYPES`,
    routing through ``CarriedVehicle.from_dict`` only when the shape
    matches.
    """
    if isinstance(item, CarriedVehicle):
        cv: Optional[CarriedVehicle] = item
    elif isinstance(item, dict) and str(
        item.get("vehicle_type", "")
    ).lower() in VALID_VEHICLE_TYPES:
        cv = CarriedVehicle.from_dict(item)
    else:
        cv = None
    if cv is None or cv.vehicle_type != vehicle_type:
        return False
    if design_id and design_id != "auto":
        if cv.design_id != design_id:
            return False
    return True


def _cv_matches(cv: CarriedVehicle, vehicle_type: str, design_id: Optional[str]) -> bool:
    """Typed predicate for the fleet-ship adapter's bay reads."""
    if cv.vehicle_type != vehicle_type:
        return False
    if design_id and design_id != "auto":
        if cv.design_id != design_id:
            return False
    return True


class FleetShipIssuerAdapter:
    """IIssuerAdapter wrapping a fleet + carrier ship.

    PROJ-431 Phase 1b: reads and writes route through the typed
    :class:`BayInventory` substrate
    (``ship.bay_inventory`` / ``ship.set_bay_inventory(...)``) instead
    of the legacy ``carried_items`` mixed list. ``pop_carried`` still
    returns dict items so the FMS order handlers (out of scope for 1b)
    continue to operate on their existing dict contract; ``append_carried``
    accepts both dict and :class:`CarriedVehicle` inputs so callers can
    migrate independently.
    """

    def __init__(self, fleet: "Fleet", ship: "ShipInstance") -> None:
        self._fleet = fleet
        self._ship = ship

    @property
    def fleet(self) -> "Fleet":
        return self._fleet

    @property
    def ship(self) -> "ShipInstance":
        return self._ship

    @property
    def location(self) -> HexCoord:
        return self._fleet.location

    @property
    def owner_id(self) -> int:
        return int(self._fleet.owner_id)

    @property
    def display_label(self) -> str:
        name = getattr(self._fleet, "display_name", None)
        if name:
            return str(name)
        return f"Fleet {self._fleet.id}"

    def pop_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
        count: Optional[int],
    ) -> List[Any]:
        # PROJ-431 Phase 1c: return typed ``CarriedVehicle`` instances
        # straight from the typed BayInventory.bay slot. The dict-round-
        # trip from Phase 1b is gone — FMS order handlers now consume
        # the typed payload directly. Planet adapter's matching method
        # still yields dicts for the staging-yard substrate (out of
        # scope until 1d).
        current = self._ship.bay_inventory
        popped: List[CarriedVehicle] = []
        remaining_bay: List[CarriedVehicle] = []
        limit = count if (count is not None and count >= 0) else None
        for cv in current.bay:
            if limit is not None and len(popped) >= limit:
                remaining_bay.append(cv)
                continue
            if _cv_matches(cv, vehicle_type, design_id):
                popped.append(cv)
            else:
                remaining_bay.append(cv)
        self._ship.set_bay_inventory(
            BayInventory(bay=remaining_bay, pods=list(current.pods))
        )
        return popped

    def count_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
    ) -> int:
        return sum(
            1 for cv in self._ship.bay_inventory.bay
            if _cv_matches(cv, vehicle_type, design_id)
        )

    def append_carried(self, items: List[Any]) -> int:
        # PROJ-431 Phase 1b: route writes through the typed BayInventory.
        # Items arrive from out-of-scope handlers as dicts (vehicle dicts
        # or pod dicts) or as already-typed CarriedVehicle instances;
        # accept both and route each into the correct typed slot.
        current = self._ship.bay_inventory
        new_bay = list(current.bay)
        new_pods = list(current.pods)
        appended = 0
        for item in items:
            if isinstance(item, CarriedVehicle):
                new_bay.append(item)
                appended += 1
                continue
            if isinstance(item, DropPod):
                new_pods.append(item)
                appended += 1
                continue
            if isinstance(item, dict):
                # PROJ-431 Phase 1f: explicit dict-shape probe replaces
                # the legacy ``CarriedVehicle.from_any`` discriminator.
                vt = str(item.get("vehicle_type", "")).lower()
                if vt in VALID_VEHICLE_TYPES:
                    new_bay.append(CarriedVehicle.from_dict(item))
                    appended += 1
                    continue
                # Drop-pod-shaped dict (or other non-vehicle payload) —
                # preserve in the pods slot.
                new_pods.append(DropPod.from_dict(item))
                appended += 1
        self._ship.set_bay_inventory(BayInventory(bay=new_bay, pods=new_pods))
        return appended

    def append_recovered(self, vehicle: CarriedVehicle) -> bool:
        cargo_mgr = getattr(self._ship, "_cargo_mgr", None)
        if cargo_mgr is None:
            return False
        return bool(cargo_mgr.load_vehicle(vehicle))


class PlanetStagingYardIssuerAdapter:
    """IIssuerAdapter wrapping a planet's staging yard.

    Used when a planet's facility (with ``StrategicMineLayer`` /
    ``StrategicFighterLaunch`` / ``StrategicSatelliteLaunch`` /
    ``RecoverFighters`` / ``RecoverSatellites``) issues an FMS order.

    Pop/append act on :attr:`Planet.staging_yard`. ``append_recovered``
    routes through :meth:`Planet.add_to_staging_yard` so the
    ``max_staging_mass`` cap is honoured.
    """

    def __init__(self, planet: "Planet") -> None:
        self._planet = planet

    @property
    def planet(self) -> "Planet":
        return self._planet

    @property
    def location(self) -> HexCoord:
        # Planet.location is local system coords; FMS orders execute at
        # the planet's global hex. Use the planet's owner's galaxy lookup
        # if the planet exposes a global hex shortcut; otherwise fall
        # back to ``location`` (tests that wrap a free-standing planet
        # set ``location`` directly to the global hex).
        gh = getattr(self._planet, "global_hex", None)
        if gh is not None:
            return gh  # type: ignore[no-any-return]
        return self._planet.location

    @property
    def owner_id(self) -> int:
        return int(self._planet.owner_id) if self._planet.owner_id is not None else -1

    @property
    def display_label(self) -> str:
        name = getattr(self._planet, "name", None)
        if name:
            return f"Planet {name}"
        return f"Planet {getattr(self._planet, 'id', '?')}"

    def pop_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
        count: Optional[int],
    ) -> List[Any]:
        yard = self._planet.staging_yard
        popped: List[Any] = []
        remaining: List[Any] = []
        limit = count if (count is not None and count >= 0) else None
        for item in yard:
            if limit is not None and len(popped) >= limit:
                remaining.append(item)
                continue
            if _matches(item, vehicle_type, design_id):
                popped.append(item)
            else:
                remaining.append(item)
        self._planet._staging_yard = remaining
        return popped

    def count_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
    ) -> int:
        return sum(
            1 for item in self._planet.staging_yard
            if _matches(item, vehicle_type, design_id)
        )

    def append_carried(self, items: List[Any]) -> int:
        """Append items, respecting ``max_staging_mass`` if set.

        Honours partial-success: stops at the first item that would
        overflow capacity and returns the count actually appended.
        """
        appended = 0
        for item in items:
            ok = self._planet.add_to_staging_yard(item)
            if not ok:
                break
            appended += 1
        return appended

    def append_recovered(self, vehicle: CarriedVehicle) -> bool:
        # PROJ-450 Phase 1: pass the typed CarriedVehicle directly;
        # Planet normalises to dict internally.
        return bool(self._planet.add_to_staging_yard(vehicle))


__all__ = [
    "IIssuerAdapter",
    "FleetShipIssuerAdapter",
    "PlanetStagingYardIssuerAdapter",
]
