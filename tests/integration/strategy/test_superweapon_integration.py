"""
Integration tests for PROJ-102: Strategic Superweapons and Special Orders.

End-to-end tests covering full superweapon workflows:
- Implode Planet
- Stellerate Star
- Open Warp Point
- Close Warp Point
- Create Dyson Sphere
- Self-Destruct

Also includes save/load round-trip tests for all superweapon order types.
"""

import pytest
from unittest.mock import MagicMock, PropertyMock

from game.core.hex_math import HexCoord, hex_distance
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.order_types import Order, OrderType
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.star_system import StarSystem, WarpPoint
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.spectrum import Spectrum
from game.strategy.data.stars import Star, StarType
from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor


# =============================================================================
# Fixtures
# =============================================================================


# PROJ-368 Phase 4: SELF_DESTRUCT was lifted from SuperweaponOrderProcessor
# to SelfDestructHandler. Tests that called process_self_destruct now route
# through the handler with the same arguments and field shape.
def _lift_self_destruct(processor, fleet, empire, galaxy):
    from game.strategy.engine.order_handlers.self_destruct import SelfDestructHandler
    handler = SelfDestructHandler(event_bus=getattr(processor, "_event_bus", None))
    return handler.execute_action_order(fleet, empire, galaxy)


class MockShipInstance:
    """Mock ShipInstance for testing superweapon abilities."""

    _id_counter = 0

    def __init__(self, name: str, design_data: dict = None):
        MockShipInstance._id_counter += 1
        self.id = MockShipInstance._id_counter
        self.name = name
        self.design_data = design_data or {'layers': {}}

    def is_combat_capable(self) -> bool:
        return True

    def get_calculated_stats(self) -> dict:
        return {'strategic_movement': 50}


@pytest.fixture
def component_registry():
    """Registry with superweapon component definitions."""
    return {
        'planet_imploder': {
            'id': 'planet_imploder',
            'abilities': {'DestroyPlanet': {}}
        },
        'stellerator': {
            'id': 'stellerator',
            'abilities': {'DestroyStar': {}}
        },
        'qti': {
            'id': 'qti',
            'abilities': {'OpenWarpPoint': {}}
        },
        'qtd': {
            'id': 'qtd',
            'abilities': {'CloseWarpPoint': {}}
        },
        'dsc': {
            'id': 'dsc',
            'abilities': {'CreateDysonSphere': {}}
        },
        'sdd': {
            'id': 'sdd',
            'abilities': {'SelfDestruct': {}}
        },
    }


def create_test_spectrum() -> Spectrum:
    """Create a minimal spectrum for testing."""
    return Spectrum(
        gamma_ray=0.0,
        xray=0.0,
        ultraviolet=1.0,
        blue=1.0,
        green=1.0,
        red=1.0,
        infrared=1.0,
        microwave=0.0,
        radio=0.0
    )


def create_test_galaxy_with_system(system_name: str = "Test System",
                                    system_location: HexCoord = HexCoord(0, 0)) -> Galaxy:
    """Create a minimal Galaxy with one system for testing."""
    galaxy = Galaxy(radius=100)

    # Create star (dataclass with required fields)
    star = Star(
        name=f"{system_name} Star",
        mass=1.0,
        radius_hexes=1,
        temperature=5778.0,
        luminosity=1.0,
        spectrum=create_test_spectrum(),
        star_type=StarType.MAIN_SEQUENCE,
        color=(255, 255, 200),
        age=4.6e9,
        location=HexCoord(0, 0)
    )

    # Create system
    system = StarSystem(system_name, system_location, stars=[star])
    galaxy.add_system(system)

    return galaxy


def add_planet_to_system(galaxy: Galaxy, system: StarSystem,
                          planet_name: str,
                          local_location: HexCoord = HexCoord(3, 0)) -> Planet:
    """Add a planet to a system and register it."""
    planet = Planet(
        name=planet_name,
        location=local_location,
        orbit_distance=3,
        mass=1e24,
        radius=6e6,
        surface_area=5e14,
        density=5500,
        surface_gravity=9.8,
        surface_pressure=101325,
        surface_temperature=288,
        surface_water=0.7,
        tectonic_activity=0.5,
        magnetic_field=1.0,
        planet_type=PlanetType.CONTINENTAL,
        image_id="test.png"
    )
    system.planets.append(planet)
    galaxy.register_planet(system, planet)
    return planet


# =============================================================================
# Task 9.1: Integration Tests - Full Superweapon Flows
# =============================================================================

class TestImplodePlanetIntegration:
    """End-to-end tests for Implode Planet superweapon."""

    def test_implode_planet_full_flow(self, component_registry):
        """Test full flow: issue order -> process -> planet destroyed, ship consumed."""
        # Setup galaxy with system and planet
        galaxy = create_test_galaxy_with_system("Alpha", HexCoord(0, 0))
        system = galaxy.name_map["Alpha"]
        planet = add_planet_to_system(galaxy, system, "Target Planet", HexCoord(3, 0))
        planet_global_hex = system.global_location + planet.location

        # Create fleet with Planet Imploder ship at planet location
        imploder_ship = MockShipInstance("Imploder", {
            'layers': {'HULL': [{'id': 'planet_imploder'}]}
        })
        escort_ship = MockShipInstance("Escort", {
            'layers': {'HULL': [{'id': 'basic_engine'}]}
        })

        fleet = Fleet(1, 1, planet_global_hex)
        fleet.ships.append(imploder_ship)
        fleet.ships.append(escort_ship)

        # Issue IMPLODE_PLANET order
        fleet.orders.append(Order(OrderType.IMPLODE_PLANET, planet))

        # Create empire
        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        # Verify planet exists before
        assert planet in system.planets
        assert planet.id in galaxy.planets_by_id

        # Process the superweapon order
        processor = SuperweaponOrderProcessor()
        result = processor.process_implode_planet(
            fleet, empire, galaxy, [empire], component_registry
        )

        # Verify result
        assert result.success is True
        assert "destroyed" in result.message.lower()

        # Verify planet removed
        assert planet not in system.planets
        assert planet.id not in galaxy.planets_by_id

        # Verify ship preserved, escort remains
        assert imploder_ship in fleet.ships
        assert escort_ship in fleet.ships
        assert len(fleet.ships) == 2

        # Verify order popped
        assert len(fleet.orders) == 0


class TestStellerateStarIntegration:
    """End-to-end tests for Stellerate Star superweapon."""

    def test_stellerate_star_full_flow(self, component_registry):
        """Test full flow: issue order -> star destroyed, ALL fleets destroyed (suicide)."""
        # Setup galaxy with system, planet, and stars
        galaxy = create_test_galaxy_with_system("Beta", HexCoord(10, 10))
        system = galaxy.name_map["Beta"]
        planet = add_planet_to_system(galaxy, system, "Doomed Planet", HexCoord(4, 0))

        # Create stellerator fleet at system center
        stellerator_ship = MockShipInstance("Stellerator", {
            'layers': {'HULL': [{'id': 'stellerator'}]}
        })

        actor_fleet = Fleet(1, 1, HexCoord(10, 10))  # At system center
        actor_fleet.ships.append(stellerator_ship)

        # Create another fleet in same system (should also be destroyed)
        innocent_ship = MockShipInstance("Bystander", {})
        bystander_fleet = Fleet(2, 2, HexCoord(10, 10))
        bystander_fleet.ships.append(innocent_ship)

        # Create empires
        player_empire = Empire(1, "Player", (255, 0, 0))
        player_empire.fleets.append(actor_fleet)

        enemy_empire = Empire(2, "Enemy", (0, 0, 255))
        enemy_empire.fleets.append(bystander_fleet)

        all_empires = [player_empire, enemy_empire]

        # Issue STELLERATE_STAR order
        actor_fleet.orders.append(Order(OrderType.STELLERATE_STAR, None))

        # Verify initial state
        assert len(system.stars) == 1
        assert planet in system.planets
        assert actor_fleet in player_empire.fleets
        assert bystander_fleet in enemy_empire.fleets

        # Process the superweapon order
        processor = SuperweaponOrderProcessor()
        result = processor.process_stellerate_star(
            actor_fleet, player_empire, galaxy, all_empires, component_registry
        )

        # Verify result
        assert result.success is True
        assert result.fleet_consumed is True

        # Verify star removed
        assert len(system.stars) == 0

        # Verify planet removed
        assert planet not in system.planets

        # Verify BOTH fleets destroyed (suicide weapon kills everyone in system)
        assert actor_fleet not in player_empire.fleets
        assert bystander_fleet not in enemy_empire.fleets


class TestOpenWarpPointIntegration:
    """End-to-end tests for Open Warp Point superweapon."""

    def test_open_warp_point_full_flow(self, component_registry):
        """Test full flow: create warp link between two systems, ship consumed."""
        # Setup galaxy with two systems (no warp link initially)
        galaxy = create_test_galaxy_with_system("Gamma", HexCoord(0, 0))

        # Add second system
        star2 = Star(
            name="Delta Star",
            mass=0.8,
            radius_hexes=1,
            temperature=4500.0,
            luminosity=0.5,
            spectrum=create_test_spectrum(),
            star_type=StarType.RED_DWARF,
            color=(255, 150, 100),
            age=5e9,
            location=HexCoord(0, 0)
        )
        system2 = StarSystem("Delta", HexCoord(50, 50), stars=[star2])
        galaxy.add_system(system2)

        system1 = galaxy.name_map["Gamma"]

        # Verify no warp points initially
        assert len(system1.warp_points) == 0
        assert len(system2.warp_points) == 0

        # Create QTI fleet at system 1
        qti_ship = MockShipInstance("QTI Ship", {
            'layers': {'HULL': [{'id': 'qti'}]}
        })

        fleet = Fleet(1, 1, HexCoord(0, 0))  # At system 1
        fleet.ships.append(qti_ship)

        # Issue OPEN_WARP_POINT order
        warp_params = {'target_system_name': 'Delta'}
        fleet.orders.append(Order(OrderType.OPEN_WARP_POINT, warp_params))

        # Create empire
        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        # Process the superweapon order
        processor = SuperweaponOrderProcessor()
        result = processor.process_open_warp_point(
            fleet, empire, galaxy, component_registry=component_registry
        )

        # Verify result
        assert result.success is True
        assert "warp point opened" in result.message.lower()

        # Verify warp points created in BOTH systems
        assert len(system1.warp_points) == 1
        assert len(system2.warp_points) == 1

        # Verify warp destinations are correct
        assert system1.warp_points[0].destination_id == "Delta"
        assert system2.warp_points[0].destination_id == "Gamma"

        # Verify ship preserved
        assert qti_ship in fleet.ships
        assert len(fleet.ships) == 1


class TestCloseWarpPointIntegration:
    """End-to-end tests for Close Warp Point superweapon."""

    def test_close_warp_point_full_flow(self, component_registry):
        """Test full flow: warp points removed from BOTH systems, ship preserved."""
        # Setup galaxy with two linked systems
        galaxy = create_test_galaxy_with_system("Epsilon", HexCoord(0, 0))

        star2 = Star(
            name="Zeta Star",
            mass=0.5,
            radius_hexes=1,
            temperature=3500.0,
            luminosity=0.1,
            spectrum=create_test_spectrum(),
            star_type=StarType.RED_DWARF,
            color=(255, 100, 50),
            age=6e9,
            location=HexCoord(0, 0)
        )
        system2 = StarSystem("Zeta", HexCoord(30, 30), stars=[star2])
        galaxy.add_system(system2)

        system1 = galaxy.name_map["Epsilon"]

        # Create bidirectional warp link
        system1.warp_points.append(WarpPoint("Zeta", HexCoord(6, 0)))
        system2.warp_points.append(WarpPoint("Epsilon", HexCoord(-6, 0)))

        # Verify warp points exist
        assert len(system1.warp_points) == 1
        assert len(system2.warp_points) == 1

        # Create QTD fleet at system 1 warp point
        qtd_ship = MockShipInstance("QTD Ship", {
            'layers': {'HULL': [{'id': 'qtd'}]}
        })

        warp_global_hex = system1.global_location + system1.warp_points[0].location
        fleet = Fleet(1, 1, warp_global_hex)
        fleet.ships.append(qtd_ship)

        # Issue CLOSE_WARP_POINT order
        fleet.orders.append(Order(OrderType.CLOSE_WARP_POINT, {'destination_id': 'Zeta', 'target_hex': {'q': warp_global_hex.q, 'r': warp_global_hex.r}}))

        # Create empire
        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        # Process the superweapon order
        processor = SuperweaponOrderProcessor()
        result = processor.process_close_warp_point(
            fleet, empire, galaxy, component_registry=component_registry
        )

        # Verify result
        assert result.success is True
        assert "closed" in result.message.lower()

        # Verify warp points removed from BOTH systems
        assert len(system1.warp_points) == 0
        assert len(system2.warp_points) == 0

        # Verify ship preserved (not consumed)
        assert qtd_ship in fleet.ships
        assert len(fleet.ships) == 1


class TestCreateDysonSphereIntegration:
    """End-to-end tests for Create Dyson Sphere superweapon."""

    def test_create_dyson_sphere_full_flow(self, component_registry):
        """Test full flow: star removed, nearby planets destroyed, Dyson Sphere created."""
        # Setup galaxy with system and planets at various distances
        galaxy = create_test_galaxy_with_system("Eta", HexCoord(0, 0))
        system = galaxy.name_map["Eta"]

        # Add planets at different distances from star (at 0,0)
        near_planet = add_planet_to_system(galaxy, system, "Near Planet", HexCoord(5, 0))  # Within 9 hexes
        far_planet = add_planet_to_system(galaxy, system, "Far Planet", HexCoord(12, 0))  # Beyond 9 hexes

        # Verify initial state
        assert len(system.stars) == 1
        assert len(system.planets) == 2
        assert near_planet in system.planets
        assert far_planet in system.planets

        # Create DSC fleet at system
        dsc_ship = MockShipInstance("DSC Ship", {
            'layers': {'HULL': [{'id': 'dsc'}]}
        })

        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.append(dsc_ship)

        # Issue CREATE_DYSON_SPHERE order
        fleet.orders.append(Order(OrderType.CREATE_DYSON_SPHERE, None))

        # Create empire
        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        # Process the superweapon order
        processor = SuperweaponOrderProcessor()
        result = processor.process_create_dyson_sphere(
            fleet, empire, galaxy, [empire], component_registry
        )

        # Verify result
        assert result.success is True
        assert "dyson sphere" in result.message.lower()

        # Verify star removed
        assert len(system.stars) == 0

        # Verify near planet removed (within 9 hexes)
        assert near_planet not in system.planets

        # Verify far planet preserved (beyond 9 hexes)
        assert far_planet in system.planets

        # Verify Dyson Sphere created
        dyson_spheres = [p for p in system.planets if p.planet_type == PlanetType.DYSON_SPHERE]
        assert len(dyson_spheres) == 1

        dyson = dyson_spheres[0]
        assert dyson.location == HexCoord(0, 0)  # At system center
        assert dyson.owner_id is None  # Colonizable (no owner)

        # Verify ship preserved
        assert dsc_ship in fleet.ships
        assert len(fleet.ships) == 1


class TestSelfDestructIntegration:
    """End-to-end tests for Self-Destruct superweapon."""

    def test_self_destruct_full_flow(self, component_registry):
        """Test full flow: selected ships destroyed, others remain."""
        # Create fleet with 3 ships
        sdd_ship_1 = MockShipInstance("SDD Ship 1", {
            'layers': {'HULL': [{'id': 'sdd'}]}
        })
        sdd_ship_2 = MockShipInstance("SDD Ship 2", {
            'layers': {'HULL': [{'id': 'sdd'}]}
        })
        normal_ship = MockShipInstance("Normal Ship", {
            'layers': {'HULL': [{'id': 'basic_engine'}]}
        })

        fleet = Fleet(1, 1, HexCoord(0, 0))
        fleet.ships.extend([sdd_ship_1, sdd_ship_2, normal_ship])

        # Issue SELF_DESTRUCT order for the 2 SDD ships
        ship_ids = [sdd_ship_1.id, sdd_ship_2.id]
        fleet.orders.append(Order(OrderType.SELF_DESTRUCT, ship_ids))

        # Create empire
        empire = Empire(1, "Player", (255, 0, 0))
        empire.fleets.append(fleet)

        # Verify initial state
        assert len(fleet.ships) == 3

        # Process the superweapon order
        galaxy = Galaxy(radius=100)
        processor = SuperweaponOrderProcessor()
        result = _lift_self_destruct(processor, fleet, empire, galaxy)

        # Verify result
        assert result.success is True
        assert "2 ships self-destructed" in result.message

        # Verify correct ships destroyed
        assert sdd_ship_1 not in fleet.ships
        assert sdd_ship_2 not in fleet.ships
        assert normal_ship in fleet.ships

        # Verify fleet still exists (has remaining ship)
        assert len(fleet.ships) == 1

        # Verify order popped
        assert len(fleet.orders) == 0


# =============================================================================
# Task 9.2: Save/Load Round-Trip Tests
# =============================================================================

class TestSuperweaponOrderSerialization:
    """Test save/load round-trips for superweapon orders."""

    def test_implode_planet_order_round_trip(self):
        """Test Fleet with IMPLODE_PLANET order: to_dict -> from_dict -> order preserved."""
        from game.strategy.data.planet import Planet

        # Create a mock planet with ID (use spec=Planet for isinstance check)
        planet = MagicMock(spec=Planet)
        planet.id = 42

        # Create fleet with order
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.orders.append(Order(OrderType.IMPLODE_PLANET, planet))

        # Serialize
        order_data = fleet.orders[0].to_dict()

        # Verify serialization
        assert order_data['type'] == 'IMPLODE_PLANET'
        assert order_data['target']['type'] == 'planet_ref'
        assert order_data['target']['id'] == 42

    def test_self_destruct_order_round_trip(self):
        """Test Fleet with SELF_DESTRUCT order (ship ID list): round-trip."""
        # Create fleet with self-destruct order
        ship_ids = [101, 102, 103]
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.orders.append(Order(OrderType.SELF_DESTRUCT, ship_ids))

        # Serialize
        order_data = fleet.orders[0].to_dict()

        # Verify serialization
        assert order_data['type'] == 'SELF_DESTRUCT'
        assert order_data['target']['type'] == 'ship_id_list'
        assert order_data['target']['value'] == [101, 102, 103]

    def test_open_warp_point_order_round_trip(self):
        """Test Fleet with OPEN_WARP_POINT order (dict target): round-trip."""
        # Create fleet with open warp point order
        warp_params = {'target_system_name': 'Alpha Centauri'}
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.orders.append(Order(OrderType.OPEN_WARP_POINT, warp_params))

        # Serialize
        order_data = fleet.orders[0].to_dict()

        # Verify serialization
        assert order_data['type'] == 'OPEN_WARP_POINT'
        assert order_data['target']['type'] == 'warp_params'
        assert order_data['target']['value'] == {'target_system_name': 'Alpha Centauri'}

    def test_stellerate_star_order_round_trip(self):
        """Test Fleet with STELLERATE_STAR order: round-trip."""
        # Create fleet with stellerate order
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.orders.append(Order(OrderType.STELLERATE_STAR, None))

        # Serialize
        order_data = fleet.orders[0].to_dict()

        # Verify serialization
        assert order_data['type'] == 'STELLERATE_STAR'
        assert order_data['target'] is None

    def test_create_dyson_sphere_order_round_trip(self):
        """Test Fleet with CREATE_DYSON_SPHERE order: round-trip."""
        # Create fleet with create dyson sphere order
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.orders.append(Order(OrderType.CREATE_DYSON_SPHERE, None))

        # Serialize
        order_data = fleet.orders[0].to_dict()

        # Verify serialization
        assert order_data['type'] == 'CREATE_DYSON_SPHERE'
        assert order_data['target'] is None

    def test_close_warp_point_order_round_trip(self):
        """Test Fleet with CLOSE_WARP_POINT order: round-trip."""
        # Create fleet with close warp point order
        fleet = Fleet(1, 1, HexCoord(5, 5))
        fleet.orders.append(Order(OrderType.CLOSE_WARP_POINT, {'destination_id': 'Target System', 'target_hex': {'q': 5, 'r': 5}}))

        # Serialize
        order_data = fleet.orders[0].to_dict()

        # Verify serialization
        assert order_data['type'] == 'CLOSE_WARP_POINT'
        assert order_data['target']['type'] == 'warp_params'
        assert order_data['target']['value']['destination_id'] == 'Target System'
        assert order_data['target']['value']['target_hex'] == {'q': 5, 'r': 5}
