"""Save/load helpers for ``Planet``.

The 47 fields, validation, and the order-deserialization path live
here. ``Planet.to_dict`` / ``Planet.from_dict`` are 1-line facades that
call into these helpers.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List

from game.core.hex_math import hex_from_dict, hex_to_dict
from game.core.validation_helpers import (
    require_keys,
    validate_enum,
    validate_non_negative,
    validate_positive,
)

if TYPE_CHECKING:
    from game.strategy.data.planet import Planet, PlanetType


__all__ = ["planet_to_dict", "planet_from_dict_kwargs"]


def planet_to_dict(planet: "Planet") -> Dict[str, Any]:
    """Serialize Planet to dict for save system. Save format unchanged."""
    return {
        "id": planet.id,
        "name": planet.name,
        "location": hex_to_dict(planet.location),
        "orbit_distance": planet.orbit_distance,
        "mass": planet.mass,
        "radius": planet.radius,
        "surface_area": planet.surface_area,
        "density": planet.density,
        "surface_gravity": planet.surface_gravity,
        "surface_pressure": planet.surface_pressure,
        "surface_temperature": planet.surface_temperature,
        "surface_water": planet.surface_water,
        "tectonic_activity": planet.tectonic_activity,
        "magnetic_field": planet.magnetic_field,
        "atmosphere": planet.atmosphere.copy(),
        "planet_type": planet.planet_type.name,
        "orbit_parent_name": planet.orbit_parent_name,
        "owner_id": planet.owner_id,
        "construction_queue": planet.construction_queue.copy(),
        "construction_queue_paused": planet.construction_queue_paused,
        "deposits": {k: v.copy() for k, v in planet.deposits.items()},
        "stockpile": dict(planet._stockpile),
        "max_stockpile": dict(planet._max_stockpile),
        "staging_yard": list(planet._staging_yard),
        "max_staging_mass": planet.max_staging_mass,
        "facilities": [f.to_dict() for f in planet.facilities],
        "populations": [
            {"race_id": p.race_id, "count": p.count, "happiness": p.happiness}
            for p in planet.populations
        ],
        "image_id": planet.image_id,
        "image_rotation": planet.image_rotation,
        "radius_hexes": planet.radius_hexes,
        "energy": planet.energy,
        "energy_capacity": planet.energy_capacity,
        "energy_generation": planet.energy_generation,
        "atmosphere_target": dict(planet.atmosphere_target),
        "gravity_target": planet.gravity_target,
        "gravity_original": planet.gravity_original,
        "water_target": planet.water_target,
        "radiation_shielding": planet.radiation_shielding,
        "radiation_shielding_target": planet.radiation_shielding_target,
        "orders": [o.to_dict() for o in planet.orders],
        "species_configs": {
            race_id: cfg.to_dict()
            for race_id, cfg in planet.species_configs.items()
        },
        "intrinsic_abilities": dict(planet.intrinsic_abilities),
    }


def planet_from_dict_kwargs(data: dict) -> Dict[str, Any]:
    """Validate save data and return kwargs ready for ``Planet(**kwargs)``.

    Raises:
        PersistenceException: required key missing or value invalid.
    """
    from game.core.error_codes import ErrorCode
    from game.core.exceptions import PersistenceException
    from game.core.json_utils import deserialize_list
    from game.strategy.data.colony_species_config import ColonySpeciesConfig
    from game.strategy.data.planet import PlanetType
    from game.strategy.data.planetary_facility import PlanetaryFacility
    from game.strategy.data.species_population import SpeciesPopulation

    require_keys(
        data,
        [
            "name", "location", "orbit_distance", "mass", "radius",
            "surface_area", "density", "surface_gravity", "surface_pressure",
            "surface_temperature", "surface_water", "tectonic_activity",
            "magnetic_field", "planet_type",
        ],
        "Planet",
    )

    planet_type = validate_enum(data["planet_type"], PlanetType, "planet_type", "Planet")

    for fld in ("mass", "radius", "surface_area", "density", "surface_gravity"):
        validate_positive(data[fld], fld, "Planet")
    for fld in ("orbit_distance", "surface_pressure", "surface_water"):
        validate_non_negative(data[fld], fld, "Planet")

    try:
        location = hex_from_dict(data["location"])
    except (KeyError, TypeError) as e:
        raise PersistenceException(
            f"Planet: invalid location data - {type(e).__name__}: {e}",
            code=ErrorCode.CORRUPT_DATA.value,
            context={
                "source": "Planet",
                "field": "location",
                "error_type": type(e).__name__,
                "error": str(e),
            },
        ) from e

    parent_name = f"Planet '{data['name']}'"
    facilities = deserialize_list(
        data.get("facilities", []), PlanetaryFacility.from_dict,
        "facility", parent_name, strict=True,
    )
    populations = deserialize_list(
        data.get("populations", []), SpeciesPopulation.from_dict,
        "population", parent_name, strict=True,
    )

    return dict(
        name=data["name"],
        location=location,
        orbit_distance=data["orbit_distance"],
        mass=data["mass"],
        radius=data["radius"],
        surface_area=data["surface_area"],
        density=data["density"],
        surface_gravity=data["surface_gravity"],
        surface_pressure=data["surface_pressure"],
        surface_temperature=data["surface_temperature"],
        surface_water=data["surface_water"],
        tectonic_activity=data["tectonic_activity"],
        magnetic_field=data["magnetic_field"],
        atmosphere=data.get("atmosphere", {}),
        planet_type=planet_type,
        orbit_parent_name=data.get("orbit_parent_name"),
        owner_id=data.get("owner_id"),
        construction_queue=data.get("construction_queue", []),
        construction_queue_paused=data.get("construction_queue_paused", False),
        deposits=data.get("deposits", {}),
        _stockpile=data.get("stockpile", {}),
        _max_stockpile=data.get("max_stockpile", {}),
        _staging_yard=data.get("staging_yard", []),
        max_staging_mass=data.get("max_staging_mass", 0.0),
        facilities=facilities,
        populations=populations,
        id=data.get("id", -1),
        image_id=data.get("image_id", ""),
        image_rotation=data.get("image_rotation", 0.0),
        radius_hexes=data.get("radius_hexes", 0),
        energy=data.get("energy", 0.0),
        energy_capacity=data.get("energy_capacity", 0.0),
        energy_generation=data.get("energy_generation", 0.0),
        atmosphere_target=data.get("atmosphere_target", {}),
        gravity_target=data.get("gravity_target"),
        gravity_original=data.get("gravity_original"),
        water_target=data.get("water_target"),
        radiation_shielding=data.get("radiation_shielding", 0.0),
        radiation_shielding_target=data.get("radiation_shielding_target"),
        orders=_deserialize_planet_orders(data.get("orders", []), data["name"]),
        species_configs={
            race_id: ColonySpeciesConfig.from_dict(cfg_data)
            for race_id, cfg_data in (data.get("species_configs") or {}).items()
        },
        intrinsic_abilities=dict(data.get("intrinsic_abilities") or {}),
    )


def _deserialize_planet_orders(orders_data: list, planet_name: str = "") -> list:
    """Deserialize planet orders from save data.

    Raises:
        PersistenceException: if any order entry is corrupt.
    """
    from game.core.error_codes import ErrorCode
    from game.core.exceptions import PersistenceException
    from game.strategy.data.order_types import Order as _Order

    source = f"Planet '{planet_name}'" if planet_name else "Planet"

    if not isinstance(orders_data, list):
        raise PersistenceException(
            f"{source}: orders must be a list",
            code=ErrorCode.CORRUPT_DATA.value,
            context={"source": source, "field": "orders"},
        )

    result: List[Any] = []
    for index, item in enumerate(orders_data):
        try:
            result.append(_Order.from_dict(item))
        except (PersistenceException, KeyError, TypeError, ValueError) as e:
            raise PersistenceException(
                f"{source}: corrupt order data at index {index}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={
                    "source": source,
                    "field": "orders",
                    "order_index": index,
                    "original_error": str(e),
                },
            ) from e
    return result
