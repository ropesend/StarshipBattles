"""
Test factories for strategy-layer entities.

Each factory creates a fully-populated instance suitable for round-trip
serialization testing. All factories accept keyword overrides and optional
registries parameter where DI is needed.

Usage:
    from tests.fixtures.strategy_entities import create_test_planet, create_test_fleet
    planet = create_test_planet(name="Mars", has_facilities=True)
    fleet = create_test_fleet(num_ships=3, registries=fresh_registries)
"""

from typing import Any, Dict, Optional, TYPE_CHECKING

from game.core.hex_math import HexCoord
from game.strategy.data.stars import Spectrum, Star, StarType
from game.strategy.data.storm import Storm, StormEffect
from game.strategy.data.galaxy import WarpPoint, StarSystem
from game.strategy.data.species_population import SpeciesPopulation
from game.strategy.data.planetary_facility import PlanetaryFacility
from game.strategy.data.planet import Planet, PlanetType
from game.strategy.data.order_types import OrderType, Order
from game.core.component_state import ComponentState, component_state_key
from game.strategy.data.ship_instance import ShipInstance
from game.strategy.data.fleet import Fleet
from game.strategy.data.empire import Empire
from game.strategy.data.race_config import RaceConfig
from game.strategy.data.design_metadata import DesignMetadata
from game.strategy.events.event_log import Event, EventLog
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.research.data.research_tracker import NodeState, ResearchTracker

if TYPE_CHECKING:
    from game.core.registry import GameRegistries


# =============================================================================
# Leaf Types (no nested serializable children)
# =============================================================================

def create_test_spectrum(**overrides) -> Spectrum:
    """Create a Spectrum with all 9 bands populated."""
    defaults = dict(
        gamma_ray=1.5e-47,
        xray=3.2e-30,
        ultraviolet=1.8e-15,
        blue=4.2e-7,
        green=5.1e-7,
        red=3.8e-7,
        infrared=2.1e-7,
        microwave=8.5e-12,
        radio=1.2e-18,
    )
    defaults.update(overrides)
    return Spectrum(**defaults)


def create_test_star(**overrides) -> Star:
    """Create a Star with spectrum and all physics fields."""
    defaults = dict(
        name="TestStar",
        mass=1.0,
        radius_hexes=2,
        temperature=5778.0,
        luminosity=1.0,
        spectrum=create_test_spectrum(),
        star_type=StarType.MAIN_SEQUENCE,
        color=(255, 220, 180),
        age=4.6e9,
        location=HexCoord(0, 0),
    )
    defaults.update(overrides)
    return Star(**defaults)


def create_test_warp_point(**overrides) -> WarpPoint:
    """Create a WarpPoint with destination and location."""
    defaults = dict(
        destination_id="OtherSystem",
        location=HexCoord(5, -3),
    )
    defaults.update(overrides)
    return WarpPoint(**defaults)


def create_test_storm_effect(**overrides) -> StormEffect:
    """Create a StormEffect with non-default values."""
    defaults = dict(
        shield_capacity_mult=0.7,
        thrust_mult=0.8,
        strategic_mult=0.9,
        damage_per_tick=2.5,
        fuel_drain_per_tick=1.0,
    )
    defaults.update(overrides)
    return StormEffect(**defaults)


def create_test_storm(**overrides) -> Storm:
    """Create a Storm with effects and hex offsets."""
    defaults = dict(
        name="Ion Storm Alpha",
        storm_type="ion_storm",
        location=HexCoord(3, -2),
        hex_offsets=frozenset({HexCoord(0, 0), HexCoord(1, 0), HexCoord(0, 1)}),
        effects=create_test_storm_effect(),
        image_variant=2,
        intensity=0.75,
    )
    defaults.update(overrides)
    return Storm(**defaults)


def create_test_species_population(**overrides) -> SpeciesPopulation:
    """Create a SpeciesPopulation."""
    defaults = dict(
        race_id="test_race",
        count=1000,
        happiness=0.7,
    )
    defaults.update(overrides)
    return SpeciesPopulation(**defaults)


def create_test_facility(**overrides) -> PlanetaryFacility:
    """Create a PlanetaryFacility with design data."""
    defaults = dict(
        instance_id="fac_001",
        design_id="orbital_station",
        name="Orbital Station",
        design_data={
            "name": "Orbital Station",
            "ship_class": "OrbitalComplex",
            "vehicle_type": "Planetary Complex",
            "layers": {"core": {"components": []}},
        },
        is_operational=True,
        construction_queue=[],
        consumable_levels={"fuel": 50.0, "energy": 100.0},
    )
    defaults.update(overrides)
    return PlanetaryFacility(**defaults)


def create_test_planet(
    has_facilities: bool = True,
    has_population: bool = True,
    **overrides,
) -> Planet:
    """Create a Planet with optional facilities and population."""
    defaults = dict(
        name="TestPlanet",
        location=HexCoord(2, -1),
        orbit_distance=3,
        mass=5.97e24,
        radius=6.371e6,
        surface_area=5.1e14,
        density=5514.0,
        surface_gravity=9.81,
        surface_pressure=101325.0,
        surface_temperature=288.0,
        surface_water=0.71,
        tectonic_activity=0.6,
        magnetic_field=1.0,
        atmosphere={"nitrogen": 0.78, "oxygen": 0.21, "carbon_dioxide": 0.01},
        planet_type=PlanetType.CONTINENTAL,
        orbit_parent_name="TestStar",
        owner_id=0,
        deposits={"minerals": {"amount": 500, "quality": 0.8}},
        id=1,
        image_id="planet_continental_01",
        image_rotation=45.0,
        radius_hexes=1,
    )
    if has_facilities:
        defaults["facilities"] = [create_test_facility()]
    else:
        defaults["facilities"] = []

    if has_population:
        defaults["populations"] = [create_test_species_population()]
    else:
        defaults["populations"] = []

    defaults.update(overrides)
    return Planet(**defaults)


def create_test_star_system(
    num_planets: int = 2,
    num_stars: int = 1,
    **overrides,
) -> StarSystem:
    """Create a StarSystem with stars, planets, and optional storms/warp points."""
    name = overrides.pop("name", "TestSystem")
    global_location = overrides.pop("global_location", HexCoord(10, -5))
    stars = overrides.pop("stars", None)
    region_id = overrides.pop("region_id", 1)

    if stars is None:
        stars = [
            create_test_star(name=f"{name}_Star{i+1}", location=HexCoord(0, 0))
            for i in range(num_stars)
        ]

    system = StarSystem(name=name, global_location=global_location, stars=stars, region_id=region_id)

    planets = overrides.pop("planets", None)
    if planets is None:
        for i in range(num_planets):
            system.planets.append(
                create_test_planet(
                    name=f"{name}_Planet{i+1}",
                    id=i + 1,
                    location=HexCoord(i + 2, 0),
                    orbit_distance=i + 2,
                    has_facilities=(i == 0),
                    has_population=(i == 0),
                )
            )
    else:
        system.planets = planets

    # Add a warp point
    warp_points = overrides.pop("warp_points", None)
    if warp_points is not None:
        system.warp_points = warp_points
    else:
        system.warp_points.append(create_test_warp_point())

    storms = overrides.pop("storms", None)
    if storms is not None:
        system.storms = storms

    return system


def create_test_race_config(**overrides) -> RaceConfig:
    """Create a RaceConfig with all fields populated.

    PROJ-283 Phase 4: legacy environment fields (`gravity_ideal`,
    `atmosphere_preferences`, `aptitude_happiness`, etc.) deleted;
    `__post_init__` backfills `preferences` from `FACTOR_REGISTRY` defaults.
    """
    defaults = dict(
        race_id="test_race",
        name="Testarians",
        faction_name="Test Empire",
        race_name="Testarian",
        race_name_plural="Testarians",
        government_type="Democracy",
        government_organization="Senate",
        leader_title="President",
        leader_name="Test Leader",
        physical_type="Humanoid",
        society_type="Industrial",
        flag_id="flag_test",
        portrait_id="portrait_test",
        theme_id="Federation",
        homeworld_type="CONTINENTAL",
        aptitude_strength=55,
        aptitude_intelligence=60,
        aptitude_constitution=50,
        aptitude_dexterity=45,
        aptitude_tolerance_other_species=50,
        aptitude_cooperation=55,
        aptitude_conflict_tolerance=40,
        base_reproduction_rate=0.03,
        base_happiness=0.5,
        bio_description="A test species.",
        socio_description="A test society.",
        created_date="2026-01-01T00:00:00",
        modified_date="2026-01-01T00:00:00",
    )
    defaults.update(overrides)
    return RaceConfig(**defaults)


def create_test_fleet_order(
    order_type: OrderType = OrderType.MOVE,
    target: Any = None,
    **overrides,
) -> Order:
    """Create a Order with default MOVE type."""
    if target is None:
        target = HexCoord(5, -3)
    order = Order(order_type=order_type, target=target)
    for key, value in overrides.items():
        setattr(order, key, value)
    return order


def create_test_ship_instance(
    registries: Optional['GameRegistries'] = None,
    **overrides,
) -> ShipInstance:
    """Create a ShipInstance with all fields populated."""
    defaults = dict(
        instance_id="ship_001",
        design_id="test_escort",
        name="USS Test",
        owner_id=0,
        design_data={
            "name": "Test Escort",
            "ship_class": "Escort",
            "vehicle_type": "Ship",
            "theme_id": "Federation",
            "expected_stats": {"mass": 100, "max_hp": 200},
            "layers": {"hull": {"components": []}},
        },
        current_hp=180,
        components={
            component_state_key("laser_1", 0): ComponentState(
                component_id="laser_1", instance_index=0, current_hp=5.0,
            ),
        },
        consumable_levels={"fuel": 80.0, "energy": 50.0},
        component_toggles={"shield_1": True, "cloak_1": False},
        cargo_contents={"minerals": 10},
        is_alive=True,
        is_derelict=False,
        experience=3,
        kills=1,
        battles_survived=2,
        serial=1,
    )
    defaults.update(overrides)
    instance = ShipInstance(**defaults)
    if registries is not None:
        instance.set_registries(registries)
    return instance


def create_test_fleet(
    fleet_id: int = 1,
    num_ships: int = 2,
    registries: Optional['GameRegistries'] = None,
    **overrides,
) -> Fleet:
    """Create a Fleet with ships and orders."""
    owner_id = overrides.pop("owner_id", 0)
    location = overrides.pop("location", HexCoord(10, -5))
    speed = overrides.pop("speed", 5.0)

    component_registry = None
    if registries is not None:
        component_registry = registries.components

    fleet = Fleet(
        fleet_id=fleet_id,
        owner_id=owner_id,
        location=location,
        speed=speed,
        component_registry=component_registry,
    )

    for i in range(num_ships):
        ship = create_test_ship_instance(
            instance_id=f"ship_{fleet_id}_{i+1}",
            name=f"Ship {i+1}",
            owner_id=owner_id,
            serial=i + 1,
            registries=registries,
        )
        fleet.ships.append(ship)

    # Add a default MOVE order
    fleet.orders.append(create_test_fleet_order())

    for key, value in overrides.items():
        setattr(fleet, key, value)

    return fleet


def create_test_empire(
    empire_id: int = 0,
    num_fleets: int = 1,
    registries: Optional['GameRegistries'] = None,
    **overrides,
) -> Empire:
    """Create an Empire with fleets and economy."""
    name = overrides.pop("name", "Test Empire")
    color = overrides.pop("color", (0, 100, 255))
    theme_path = overrides.pop("theme_path", None)
    empire_theme_id = overrides.pop("empire_theme_id", "Federation")
    flag_id = overrides.pop("flag_id", "flag_test")
    portrait_id = overrides.pop("portrait_id", "portrait_test")
    race_config = overrides.pop("race_config", create_test_race_config())

    empire = Empire(
        empire_id=empire_id,
        name=name,
        color=color,
        theme_path=theme_path,
        empire_theme_id=empire_theme_id,
        flag_id=flag_id,
        portrait_id=portrait_id,
        race_config=race_config,
    )

    for i in range(num_fleets):
        fleet = create_test_fleet(
            fleet_id=1000 + i,
            owner_id=empire_id,
            registries=registries,
        )
        empire.fleets.append(fleet)

    # Economy
    empire.resource_pool = overrides.pop("resource_pool", {"fuel": 500.0, "minerals": 300.0, "energy": 200.0})
    empire.max_storage = overrides.pop("max_storage", {"fuel": 1000.0, "minerals": 1000.0, "energy": 1000.0})
    empire.built_ship_designs = overrides.pop("built_ship_designs", {"test_escort", "test_frigate"})
    empire._design_serial_counters = overrides.pop("_design_serial_counters", {"test_escort": 5, "test_frigate": 3})

    for key, value in overrides.items():
        setattr(empire, key, value)

    return empire


def create_test_event(**overrides) -> Event:
    """Create a game Event."""
    defaults = dict(
        event_type="ship_built",
        category="production",
        turn=1,
        empire_id=0,
        message="USS Test was built at TestPlanet",
        details={"design_id": "test_escort", "planet_id": 1},
    )
    defaults.update(overrides)
    return Event(**defaults)


def create_test_event_log(num_events: int = 3, **overrides) -> EventLog:
    """Create an EventLog with multiple events."""
    log = EventLog()
    categories = ["production", "combat", "colonies"]
    event_types = ["ship_built", "combat_resolved", "colony_founded"]
    for i in range(num_events):
        log.append(create_test_event(
            event_type=event_types[i % len(event_types)],
            category=categories[i % len(categories)],
            turn=i + 1,
            message=f"Event {i+1}",
        ))
    return log


def create_test_player_config(**overrides) -> PlayerConfig:
    """Create a PlayerConfig."""
    defaults = dict(
        name="Terran Command",
        theme="Federation",
        color=(0, 100, 255),
        is_human=True,
        race_id="test_race",
        flag_id="flag_test",
        portrait_id="portrait_test",
    )
    defaults.update(overrides)
    return PlayerConfig(**defaults)


def create_test_game_config(num_players: int = 2, **overrides) -> GameConfig:
    """Create a GameConfig with player configs."""
    players = overrides.pop("players", None)
    if players is None:
        themes = ["Federation", "Atlantians", "Romulans", "Klingons"]
        colors = [(0, 100, 255), (0, 200, 150), (0, 180, 0), (255, 50, 50)]
        players = [
            create_test_player_config(
                name=f"Empire {i+1}",
                theme=themes[i % len(themes)],
                color=colors[i % len(colors)],
                is_human=(i == 0),
            )
            for i in range(num_players)
        ]

    defaults = dict(
        galaxy_radius=4000,
        system_count=25,
        galaxy_type="random",
        galaxy_seed=42,
        save_name="test_save",
        players=players,
    )
    defaults.update(overrides)
    return GameConfig(**defaults)


def create_test_design_metadata(**overrides) -> DesignMetadata:
    """Create a DesignMetadata."""
    defaults = dict(
        design_id="test_escort",
        name="Test Escort",
        ship_class="Escort",
        vehicle_type="Ship",
        mass=100.0,
        combat_power=25.0,
        construction_cost={"minerals": 50, "energy": 30},
        created_date="2026-01-01T00:00:00",
        last_modified="2026-01-15T00:00:00",
        is_obsolete=False,
        times_built=5,
        theme_id="Federation",
    )
    defaults.update(overrides)
    return DesignMetadata(**defaults)


def create_test_node_state(**overrides) -> NodeState:
    """Create a NodeState for research."""
    defaults = dict(
        current_level=2,
        current_chance=0.35,
        rp_allocation=50,
    )
    defaults.update(overrides)
    return NodeState(**defaults)


def create_test_research_tracker(**overrides) -> ResearchTracker:
    """Create a ResearchTracker with node states."""
    session_seed = overrides.pop("session_seed", 12345)
    tracker = ResearchTracker(session_seed=session_seed)
    tracker.rp_budget = overrides.pop("rp_budget", 200)
    tracker.turn_number = overrides.pop("turn_number", 5)
    tracker.auto_spread_enabled = overrides.pop("auto_spread_enabled", True)

    node_states = overrides.pop("node_states", None)
    if node_states is None:
        tracker.node_states = {
            "weapons_1": create_test_node_state(current_level=3, rp_allocation=80),
            "shields_1": create_test_node_state(current_level=1, rp_allocation=40),
            "engines_1": create_test_node_state(current_level=2, rp_allocation=60),
        }
    else:
        tracker.node_states = node_states

    for key, value in overrides.items():
        setattr(tracker, key, value)

    return tracker
