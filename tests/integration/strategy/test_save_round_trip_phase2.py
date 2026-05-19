"""PROJ-372 Phase 2: Planet save round-trip equality.

Asserts ``Planet.to_dict() -> from_dict() -> to_dict()`` is a fixed
point on a fully-populated planet. Phase 5 introduces the canonical
full-galaxy round-trip; this is the Phase-2 boundary check.
"""
from __future__ import annotations

from game.core.hex_math import HexCoord
from game.strategy.data.colony_species_config import ColonySpeciesConfig
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.species_population import SpeciesPopulation


def _populated_planet() -> Planet:
    return Planet(
        name="Roundtrip-1",
        location=HexCoord(2, 3),
        orbit_distance=4,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5515.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        atmosphere={"N2": 78000.0, "O2": 21000.0, "Ar": 950.0},
        atmosphere_target={"O2": 21500.0},
        orbit_parent_name="Sol A",
        owner_id=2,
        construction_queue=[{"design_id": "d1", "type": "ship", "turns_remaining": 3}],
        construction_queue_paused=True,
        deposits={"metals": {"quantity": 1000, "quality": 0.7}},
        _stockpile={"metals": 250.0, "fuel": 100.0},
        _max_stockpile={"metals": 5000.0, "fuel": 2000.0},
        _staging_yard=[{"design_id": "fighter1", "design_data": {}, "mass": 50.0, "vehicle_type": "fighter", "name": "F1"}],
        max_staging_mass=500.0,
        populations=[SpeciesPopulation(race_id="human", count=100, happiness=0.6)],
        id=42,
        image_id="planet_5_994.png",
        image_rotation=270.0,
        radius_hexes=2,
        energy=80.0,
        energy_capacity=200.0,
        energy_generation=10.0,
        gravity_target=8.5,
        gravity_original=9.81,
        water_target=0.65,
        radiation_shielding=0.3,
        radiation_shielding_target=0.5,
        species_configs={"human": ColonySpeciesConfig()},
        intrinsic_abilities={"FertileSoil": {"strength": 0.8}},
    )


def test_planet_round_trip_preserves_all_47_fields() -> None:
    p = _populated_planet()
    d1 = p.to_dict()
    p2 = Planet.from_dict(d1)
    d2 = p2.to_dict()
    assert d1 == d2


def test_uncolonized_minimal_planet_round_trip() -> None:
    p = Planet(
        name="Min",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=1e22,
        radius=1e5,
        surface_area=1e10,
        density=3000.0,
        surface_gravity=1.0,
        surface_pressure=0.0,
        surface_temperature=10.0,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
        planet_type=PlanetType.BARREN,
    )
    d1 = p.to_dict()
    p2 = Planet.from_dict(d1)
    assert p2.to_dict() == d1
