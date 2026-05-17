"""PROJ-431 Phase 2 — `DeployedGroup` family.

A `DeployedGroup` is an empire-owned, hex-located, non-fleet collection
of design-backed deployable vehicles (mines, fighters, satellites). It
sits as a **sibling** of `Fleet` — NOT a subclass — so the fleet-action
surface (Move / Warp / Build / etc.) is structurally unreachable on
deployed groups. The runtime type IS the model; no `group_kind`
discriminator string.

This module ships the abstract base + the first concrete subclass:

- :class:`DeployedGroup` — identity (`id`, `owner_id`, `location`,
  `display_name`) + serialise/deserialise contract.
- :class:`MineGroup`     — strategic minefield container. Owns mines,
  scatter positions, sensitivity, threshold.

Subsequent phases will add `FighterWing` and `SatelliteConstellation`
(see PROJ-431 Phase 3). Both share the abstract base.

PROJ-431 Phase 2 — save schema version bumped to 4.1.0 to accommodate
the new ``Empire.deployed_groups`` collection. Saves are disposable
per CLAUDE.md "old saves are disposable" — no migration shim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from game.core.hex_math import HexCoord
from game.strategy.data.carried_vehicle import CarriedVehicle


__all__ = [
    "DeployedGroup",
    "MineGroup",
    "FighterWing",
    "SatelliteConstellation",
]


# ---------------------------------------------------------------------------
# Registry of concrete DeployedGroup subclasses (populated at class-def time)
# Used by ``DeployedGroup.from_dict`` for polymorphic deserialisation.
# ---------------------------------------------------------------------------

_TYPE_REGISTRY: Dict[str, type] = {}


def _register_type(type_name: str):
    def deco(cls):
        _TYPE_REGISTRY[type_name] = cls
        cls._type_name = type_name  # type: ignore[attr-defined]
        return cls
    return deco


# ---------------------------------------------------------------------------
# Abstract base
# ---------------------------------------------------------------------------


class DeployedGroup:
    """Abstract base for empire-owned, hex-located deployable groups.

    Subclasses MUST register via :func:`_register_type` so the
    polymorphic deserialiser can route ``from_dict`` calls to the
    correct concrete class.

    The base intentionally exposes a NARROW surface compared to
    :class:`~game.strategy.data.fleet.Fleet`: identity + location only.
    No `orders`, `path`, `task_forces`, `construction_queue`. Adding a
    Move/Warp/Build handler to deployed groups is a structural error,
    not a runtime guard — the methods simply do not exist.
    """

    _type_name: str = "deployed_group"

    def __init__(
        self,
        *,
        group_id: Any,
        owner_id: int,
        location: HexCoord,
        display_name: str = "",
    ) -> None:
        self.id = group_id
        self.owner_id = owner_id
        self.location = location
        self.display_name = display_name

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    @property
    def name(self) -> str:
        """Renamable display name. Falls back to a type-tagged default."""
        if self.display_name:
            return self.display_name
        return f"{self._type_name} {self.id}"

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Subclass-extensible base serialisation.

        Concrete subclasses call ``super().to_dict()`` and extend with
        their own fields. The ``type`` key drives :meth:`from_dict`'s
        dispatch.
        """
        location_data: Any
        if isinstance(self.location, HexCoord):
            location_data = {"q": self.location.q, "r": self.location.r}
        elif isinstance(self.location, tuple):
            location_data = list(self.location)
        else:
            location_data = self.location
        return {
            "type": self._type_name,
            "id": self.id,
            "owner_id": self.owner_id,
            "location": location_data,
            "display_name": self.display_name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DeployedGroup":
        """Polymorphic deserialiser — dispatches on the ``type`` field."""
        type_name = data.get("type")
        if type_name is None:
            raise ValueError(
                "DeployedGroup.from_dict: missing 'type' discriminator"
            )
        target = _TYPE_REGISTRY.get(type_name)
        if target is None:
            raise ValueError(
                f"DeployedGroup.from_dict: unknown type {type_name!r}; "
                f"known: {sorted(_TYPE_REGISTRY)}"
            )
        # Concrete subclasses implement ``_from_dict_payload`` to read
        # their own fields off the dict. The base resolves identity.
        return target._from_dict_payload(data)

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "DeployedGroup":
        raise NotImplementedError(
            f"{cls.__name__}._from_dict_payload must be implemented"
        )

    @staticmethod
    def _decode_location(value: Any) -> HexCoord:
        if isinstance(value, HexCoord):
            return value
        if isinstance(value, dict) and "q" in value and "r" in value:
            return HexCoord(int(value["q"]), int(value["r"]))
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            return HexCoord(int(value[0]), int(value[1]))
        raise ValueError(
            f"DeployedGroup: cannot decode location {value!r}"
        )

    # ------------------------------------------------------------------
    # Equality is identity-based on (type, id)
    # ------------------------------------------------------------------

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DeployedGroup):
            return NotImplemented
        return type(self) is type(other) and self.id == other.id

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.id))

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}({self.id}, owner={self.owner_id}, "
            f"loc={self.location})"
        )


# ---------------------------------------------------------------------------
# MineGroup
# ---------------------------------------------------------------------------


@_register_type("mine_group")
class MineGroup(DeployedGroup):
    """Strategic minefield — sibling of :class:`Fleet`, NOT a Fleet.

    Replaces the synthetic mine-carrier ``ShipInstance`` pattern. Mines
    live directly on ``self.mines`` as :class:`CarriedVehicle` entries.
    No fake ship, no zero-HP carrier; the carrier's only job was to keep
    the serializer/DTO surface usable and that job is now obsolete.

    Attributes:
        id: Group identity (typically minted in the 100k+ range to
            avoid clashing with real Fleet ids).
        owner_id: Empire id.
        location: HexCoord of the field.
        display_name: User-facing renamable label.
        mines: Mine inventory, homogeneous ``list[CarriedVehicle]``.
        sensitivity: ``"LOW"`` / ``"MED"`` / ``"HIGH"`` — warhead
            trigger multiplier.
        expected_hit_chance_threshold: ``[0.0, 1.0]`` — deterministic
            laserhead gate.
        mine_positions: scatter coordinates in tactical-map units.
        scatter_seed: stable PRNG seed for re-entries / re-loads.
    """

    def __init__(
        self,
        *,
        group_id: Any,
        owner_id: int,
        location: HexCoord,
        display_name: str = "",
        sensitivity: str = "MED",
        expected_hit_chance_threshold: float = 0.30,
    ) -> None:
        super().__init__(
            group_id=group_id,
            owner_id=owner_id,
            location=location,
            display_name=display_name,
        )
        self.mines: List[CarriedVehicle] = []
        self.sensitivity: str = sensitivity
        self.expected_hit_chance_threshold: float = float(
            expected_hit_chance_threshold
        )
        self.mine_positions: List[Tuple[float, float]] = []
        self.scatter_seed: Optional[int] = None

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["sensitivity"] = self.sensitivity
        data["expected_hit_chance_threshold"] = float(
            self.expected_hit_chance_threshold
        )
        data["mines"] = [m.to_dict() for m in self.mines]
        if self.mine_positions:
            data["mine_positions"] = [list(p) for p in self.mine_positions]
        if self.scatter_seed is not None:
            data["scatter_seed"] = int(self.scatter_seed)
        return data

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "MineGroup":
        mg = cls(
            group_id=data["id"],
            owner_id=int(data["owner_id"]),
            location=cls._decode_location(data["location"]),
            display_name=str(data.get("display_name", "") or ""),
            sensitivity=str(data.get("sensitivity", "MED")),
            expected_hit_chance_threshold=float(
                data.get("expected_hit_chance_threshold", 0.30)
            ),
        )
        for mine_data in data.get("mines", []) or []:
            if isinstance(mine_data, CarriedVehicle):
                mg.mines.append(mine_data)
            elif isinstance(mine_data, dict):
                mg.mines.append(CarriedVehicle.from_dict(mine_data))
        positions = data.get("mine_positions")
        if positions:
            mg.mine_positions = [
                (float(p[0]), float(p[1]))
                for p in positions
                if isinstance(p, (list, tuple)) and len(p) >= 2
            ]
        if data.get("scatter_seed") is not None:
            mg.scatter_seed = int(data["scatter_seed"])
        return mg


# ---------------------------------------------------------------------------
# FighterWing (PROJ-431 Phase 3)
# ---------------------------------------------------------------------------


class _ShipBearingDeployedGroup(DeployedGroup):
    """Mixin-style base for deployed groups that carry materialised ships.

    Provides the minimal ``Fleet``-like surface (``remove_ship``) so the
    PROJ-269 post-battle hook can prune destroyed ships from
    ``FighterWing`` / ``SatelliteConstellation`` containers via the
    same :class:`IFleetMutator` plumbing it uses for real Fleets.

    The class itself is NOT registered with ``_TYPE_REGISTRY`` — only
    concrete subclasses (FighterWing, SatelliteConstellation) are.
    """

    ships: List[Any]

    def remove_ship(self, ship: Any) -> bool:
        if ship in self.ships:
            self.ships.remove(ship)
            return True
        return False


@_register_type("fighter_wing")
class FighterWing(_ShipBearingDeployedGroup):
    """Deployed-fighter group — sibling of :class:`Fleet`, NOT a Fleet.

    Replaces the previous ``Fleet(group_kind="fighter_group")`` synthetic
    fleet pattern. Fighters launched into the strategic layer (either via
    :class:`LaunchFightersOrderHandler` or as battle overflow) live here
    as real :class:`ShipInstance` entries on ``self.ships``. The fleet-
    action surface (Move / Warp / Build / Join) is structurally
    unreachable on this type — no string discriminator, no guard.

    Attributes:
        ships: Deployed fighter roster, ``list[ShipInstance]``. Unlike
            :class:`MineGroup` (which holds :class:`CarriedVehicle`s),
            fighter wings hold materialised ships so they can participate
            in battle directly.
    """

    def __init__(
        self,
        *,
        group_id: Any,
        owner_id: int,
        location: HexCoord,
        display_name: str = "",
    ) -> None:
        super().__init__(
            group_id=group_id,
            owner_id=owner_id,
            location=location,
            display_name=display_name,
        )
        # Late-import-avoidance: typed only via comment, list-typed at runtime.
        self.ships: List[Any] = []

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["ships"] = [s.to_dict() for s in self.ships]
        return data

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "FighterWing":
        from game.strategy.data.ship_instance import ShipInstance

        wing = cls(
            group_id=data["id"],
            owner_id=int(data["owner_id"]),
            location=cls._decode_location(data["location"]),
            display_name=str(data.get("display_name", "") or ""),
        )
        for ship_data in data.get("ships", []) or []:
            if isinstance(ship_data, ShipInstance):
                wing.ships.append(ship_data)
            elif isinstance(ship_data, dict):
                wing.ships.append(ShipInstance.from_dict(ship_data))
        return wing


# ---------------------------------------------------------------------------
# SatelliteConstellation (PROJ-431 Phase 3)
# ---------------------------------------------------------------------------


@_register_type("satellite_constellation")
class SatelliteConstellation(_ShipBearingDeployedGroup):
    """Deployed-satellite group — sibling of :class:`Fleet`, NOT a Fleet.

    Mirror of :class:`FighterWing` for the satellite family. Replaces
    the previous ``Fleet(group_kind="satellite_group")`` synthetic
    fleet. Satellites launched into the strategic layer live here as
    real :class:`ShipInstance` entries on ``self.ships``.
    """

    def __init__(
        self,
        *,
        group_id: Any,
        owner_id: int,
        location: HexCoord,
        display_name: str = "",
    ) -> None:
        super().__init__(
            group_id=group_id,
            owner_id=owner_id,
            location=location,
            display_name=display_name,
        )
        self.ships: List[Any] = []

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data["ships"] = [s.to_dict() for s in self.ships]
        return data

    @classmethod
    def _from_dict_payload(cls, data: Dict[str, Any]) -> "SatelliteConstellation":
        from game.strategy.data.ship_instance import ShipInstance

        c = cls(
            group_id=data["id"],
            owner_id=int(data["owner_id"]),
            location=cls._decode_location(data["location"]),
            display_name=str(data.get("display_name", "") or ""),
        )
        for ship_data in data.get("ships", []) or []:
            if isinstance(ship_data, ShipInstance):
                c.ships.append(ship_data)
            elif isinstance(ship_data, dict):
                c.ships.append(ShipInstance.from_dict(ship_data))
        return c
