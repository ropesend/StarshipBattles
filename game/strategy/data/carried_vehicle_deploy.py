"""PROJ-FMS-D audit Fix 1 — shared CarriedVehicle -> ShipInstance helper.

Consolidates the "materialise a deployed :class:`ShipInstance` from a
:class:`CarriedVehicle`" step that was previously duplicated across:

- :class:`LaunchFightersOrderHandler._carried_vehicle_to_ship_instance`
  (strategic fighter launch path)
- :class:`LaunchSatellitesOrderHandler._carried_vehicle_to_ship_instance`
  (strategic satellite launch path)
- :func:`game.simulation.systems.fighter_reboard._build_overflow_ship_instance`
  (post-battle overflow path)

The third site previously skipped the ``cv.component_states`` restore,
which silently dropped per-component damage state for any
in-battle-launched fighter or satellite that overflowed at battle end
(PROJ-FMS-D codex audit, P1). Centralising the conversion ensures all
three sites preserve the same fields uniformly: HP, component states,
``is_alive`` / ``is_derelict`` flags, and the vehicle-type-aware
instance-id prefix.
"""
from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any, Optional

from game.strategy.data.carried_vehicle import CarriedVehicle
from game.strategy.data.ship_instance import ShipInstance

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


def carried_vehicle_to_ship_instance(
    cv: CarriedVehicle,
    *,
    owner_id: int,
    registries: Optional["GameRegistries"] = None,
) -> ShipInstance:
    """Materialise a deployed :class:`ShipInstance` from a CarriedVehicle.

    Args:
        cv: The CarriedVehicle (fighter or satellite) to deploy.
        owner_id: Empire id the deployed ship belongs to.
        registries: Optional :class:`GameRegistries` for downstream stat
            calculation. Some callers (the overflow path) don't have a
            registries handle; pass ``None`` and they'll be wired by the
            consumer if/when they're needed.

    Returns:
        A :class:`ShipInstance` with:
          * vehicle-type-aware ``instance_id`` prefix
            (``fighter_*`` / ``satellite_*``)
          * ``current_hp`` preserved from the CarriedVehicle
          * ``components`` restored from ``cv.component_states`` when
            present
          * ``is_alive = True`` / ``is_derelict = False``

    Raises:
        Lets :class:`ShipInstance` construction errors propagate so the
        caller can choose to discard the vehicle (the overflow path
        wraps this in a try/except to skip uncleanly-converted vehicles).
    """
    design_data = dict(cv.design_data) if cv.design_data else {}
    design_name = design_data.get("name", cv.design_id)

    vt = (cv.vehicle_type or "fighter").lower()
    instance_prefix = "satellite" if vt == "satellite" else "fighter"

    ship = ShipInstance(
        instance_id=f"{instance_prefix}_{uuid.uuid4().hex[:12]}",
        design_id=cv.design_id,
        name=design_name,
        owner_id=owner_id,
        design_data=design_data,
        current_hp=int(cv.current_hp) if cv.current_hp else None,
    )
    if registries is not None:
        ship.set_registries(registries)
    # Preserve per-component damage state. PROJ-FMS-C audit Fix 2 added
    # this to the strategic-launch path; PROJ-FMS-D audit Fix 1 brings the
    # overflow path into line by routing both through this helper.
    if cv.component_states:
        try:
            ship.components = dict(cv.component_states)
        except Exception:  # Intentional broad catch: test stubs / partial fixtures may treat ``components`` as a property; treat as "damage state not restorable" rather than crash the launch.
            pass
    ship.is_alive = True
    ship.is_derelict = False
    return ship


def carried_vehicle_to_ship_instance_safe(
    cv: Any,
    *,
    owner_id: int,
    registries: Optional["GameRegistries"] = None,
) -> Optional[ShipInstance]:
    """Best-effort wrapper around :func:`carried_vehicle_to_ship_instance`.

    Returns ``None`` instead of raising on construction failure. Used by
    the overflow path in :mod:`fighter_reboard`, which is part of the
    post-battle hook and must not let a single malformed CarriedVehicle
    crash the entire reboard cycle.
    """
    try:
        return carried_vehicle_to_ship_instance(
            cv, owner_id=owner_id, registries=registries,
        )
    except Exception:  # Intentional broad catch: best-effort by contract — see docstring.
        return None


__all__ = [
    "carried_vehicle_to_ship_instance",
    "carried_vehicle_to_ship_instance_safe",
]
