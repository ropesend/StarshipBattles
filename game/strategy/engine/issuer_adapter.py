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
  through one accessor surface.
- :class:`PlanetStagingYardIssuerAdapter` wraps a :class:`Planet`'s
  ``staging_yard`` so the same handlers can serve planet-issued FMS
  actions without a parallel handler family.

The adapter intentionally exposes the *minimum* set of fields the five
handlers touch today. New ops must extend this surface explicitly so the
contract stays small.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, List, Optional, Protocol, runtime_checkable

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle

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
    """Shared filter predicate used by both adapters."""
    cv = CarriedVehicle.from_any(item)
    if cv is None or cv.vehicle_type != vehicle_type:
        return False
    if design_id and design_id != "auto":
        if cv.design_id != design_id:
            return False
    return True


class FleetShipIssuerAdapter:
    """IIssuerAdapter wrapping a fleet + carrier ship.

    Mirrors the legacy contract of the FMS order handlers: pop / append
    against ``ship.carried_items``; location/owner/label from the fleet.
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
        target = self._ship.carried_items
        popped: List[Any] = []
        remaining: List[Any] = []
        limit = count if (count is not None and count >= 0) else None
        for item in target:
            if limit is not None and len(popped) >= limit:
                remaining.append(item)
                continue
            if _matches(item, vehicle_type, design_id):
                popped.append(item)
            else:
                remaining.append(item)
        self._ship.carried_items = remaining
        return popped

    def count_carried(
        self,
        vehicle_type: str,
        design_id: Optional[str],
    ) -> int:
        return sum(
            1 for item in self._ship.carried_items
            if _matches(item, vehicle_type, design_id)
        )

    def append_carried(self, items: List[Any]) -> int:
        for item in items:
            self._ship.carried_items.append(item)
        return len(items)

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
        self._planet.staging_yard = remaining
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
        return bool(self._planet.add_to_staging_yard(vehicle.to_dict()))


__all__ = [
    "IIssuerAdapter",
    "FleetShipIssuerAdapter",
    "PlanetStagingYardIssuerAdapter",
]
