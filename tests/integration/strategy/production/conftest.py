"""
Shared fixtures for production tests.
"""

import pytest
import tempfile
import os
import json
import shutil
from game.strategy.data.planet import Planet, PlanetType, PlanetaryFacility
from game.core.hex_math import HexCoord
from game.strategy.engine.turn_engine import TurnEngine
from game.strategy.data.empire import Empire


@pytest.fixture
def production_setup(fresh_registries):
    """Create temporary directory and test objects for production tests."""
    # Create temporary directory for test designs
    # DesignLibrary expects designs in empire-specific subfolder: designs/empire_N/
    # Empire ID 0 is used (Empire(0, "Terran", ...))
    temp_dir = tempfile.mkdtemp()
    designs_dir = os.path.join(temp_dir, "designs", "empire_0")
    os.makedirs(designs_dir, exist_ok=True)

    # Create a test ship design
    test_design = {
        "name": "Test Ship",
        "ship_class": "Frigate",
        "vehicle_type": "Ship",
        "layers": {"CORE": [], "INNER": [], "OUTER": [], "ARMOR": []},
        "resources": {"fuel": 0.0, "energy": 0.0, "ammo": 0.0},
        "expected_stats": {
            "max_hp": 100,
            "max_speed": 10,
            "mass": 100.0
        },
        "_metadata": {
            "is_obsolete": False,
            "times_built": 0
        }
    }

    # Write test design files
    for design_id in ["test_ship", "test_ship_0", "test_ship_1", "test_ship_2"]:
        design_path = os.path.join(designs_dir, f"{design_id}.json")
        with open(design_path, 'w') as f:
            json.dump(test_design, f)

    # Create a valid planet manually to satisfy the dataclass
    planet = Planet(
        name="Terran Prime",
        location=HexCoord(0, 0),
        orbit_distance=3,
        mass=5.97e24,
        radius=6371000,
        surface_area=5.1e14,
        density=5515,
        surface_gravity=9.81,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.1,
        magnetic_field=1.0,
        atmosphere={'N2': 78000.0, 'O2': 21000.0},
        planet_type=PlanetType.CONTINENTAL
    )
    planet.owner_id = 0

    empire = Empire(0, "Terran", (0, 0, 255))
    empire.savegame_path = temp_dir  # Use temp directory for designs
    empire.add_colony(planet)

    # Give planet starting stockpile for tick-based production
    # (production engine draws from planet.stockpile, not empire.resource_pool)
    planet.stockpile = {
        "metals": 100000.0,
        "organics": 100000.0,
        "radioactives": 100000.0,
        "Energy": 100000.0,
    }
    planet.max_stockpile = {
        "metals": 1000000.0,
        "organics": 1000000.0,
        "radioactives": 1000000.0,
        "Energy": 1000000.0,
    }

    engine = TurnEngine(registries=fresh_registries)
    empires = [empire]

    yield {
        'temp_dir': temp_dir,
        'designs_dir': designs_dir,
        'planet': planet,
        'empire': empire,
        'engine': engine,
        'empires': empires
    }

    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


def create_shipyard():
    """Create a standard shipyard facility for tests."""
    return PlanetaryFacility(
        instance_id="shipyard_1",
        design_id="shipyard_complex",
        name="Space Shipyard",
        design_data={
            "layers": {
                "CORE": [{
                    "abilities": {"SpaceShipyard": {"value": 1}}
                }]
            }
        },
        is_operational=True
    )
