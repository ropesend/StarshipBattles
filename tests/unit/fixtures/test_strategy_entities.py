"""Tests for strategy entity test factories.

Verifies each factory produces valid, fully-populated objects
that can survive to_dict/from_dict round-trips.
"""

import pytest

from tests.fixtures.strategy_entities import (
    create_test_spectrum,
    create_test_star,
    create_test_warp_point,
    create_test_storm,
    create_test_species_population,
    create_test_facility,
    create_test_planet,
    create_test_star_system,
    create_test_race_config,
    create_test_fleet_order,
    create_test_ship_instance,
    create_test_fleet,
    create_test_empire,
    create_test_event,
    create_test_event_log,
    create_test_game_config,
    create_test_player_config,
    create_test_design_metadata,
    create_test_node_state,
    create_test_research_tracker,
)


class TestSpectrumFactory:
    def test_creates_valid_spectrum(self):
        s = create_test_spectrum()
        assert s.gamma_ray >= 0
        assert s.radio >= 0
        assert s.get_total_output() > 0

    def test_override_fields(self):
        s = create_test_spectrum(gamma_ray=99.0)
        assert s.gamma_ray == 99.0

    def test_to_dict_round_trip(self):
        from game.strategy.data.stars import Spectrum
        s = create_test_spectrum()
        d = s.to_dict()
        restored = Spectrum.from_dict(d)
        assert restored == s


class TestStarFactory:
    def test_creates_valid_star(self):
        s = create_test_star()
        assert s.name
        assert s.mass > 0
        assert s.spectrum is not None

    def test_override_name(self):
        s = create_test_star(name="Alpha")
        assert s.name == "Alpha"

    def test_to_dict_round_trip(self):
        from game.strategy.data.stars import Star
        s = create_test_star()
        d = s.to_dict()
        restored = Star.from_dict(d)
        assert restored.name == s.name
        assert restored.mass == s.mass


class TestWarpPointFactory:
    def test_creates_valid_warp_point(self):
        wp = create_test_warp_point()
        assert wp.destination_id
        assert wp.location is not None

    def test_override_destination(self):
        wp = create_test_warp_point(destination_id="SystemX")
        assert wp.destination_id == "SystemX"

    def test_to_dict_round_trip(self):
        from game.strategy.data.galaxy import WarpPoint
        wp = create_test_warp_point()
        d = wp.to_dict()
        restored = WarpPoint.from_dict(d)
        assert restored.destination_id == wp.destination_id


class TestStormAbilitiesFactory:
    """PROJ-300 v2.0 — abilities dict factory."""

    def test_creates_valid_abilities_dict(self):
        from tests.fixtures.strategy_entities import create_test_storm_abilities
        abilities = create_test_storm_abilities()
        assert isinstance(abilities, dict)
        assert "ShieldModifier" in abilities
        assert abilities["ShieldModifier"]["multiplier"] == 0.7


class TestStormFactory:
    def test_creates_valid_storm(self):
        s = create_test_storm()
        assert s.name
        assert s.abilities  # PROJ-300: abilities dict, not effects
        assert len(s.hex_offsets) > 0

    def test_to_dict_round_trip(self):
        from game.strategy.data.storm import Storm
        s = create_test_storm()
        d = s.to_dict()
        restored = Storm.from_dict(d)
        assert restored.name == s.name


class TestSpeciesPopulationFactory:
    def test_creates_valid_population(self):
        p = create_test_species_population()
        assert p.race_id
        assert p.count > 0
        assert 0.0 <= p.happiness <= 1.0

    def test_override_count(self):
        p = create_test_species_population(count=5000)
        assert p.count == 5000


class TestFacilityFactory:
    def test_creates_valid_facility(self):
        f = create_test_facility()
        assert f.instance_id
        assert f.design_id
        assert f.name
        assert f.design_data

    def test_override_name(self):
        f = create_test_facility(name="Starbase Alpha")
        assert f.name == "Starbase Alpha"


class TestPlanetFactory:
    def test_creates_valid_planet(self):
        p = create_test_planet()
        assert p.name
        assert p.mass > 0
        assert p.location is not None

    def test_with_facilities(self):
        p = create_test_planet(has_facilities=True)
        assert len(p.facilities) > 0

    def test_with_population(self):
        p = create_test_planet(has_population=True)
        assert len(p.populations) > 0

    def test_without_optional(self):
        p = create_test_planet(has_facilities=False, has_population=False)
        assert len(p.facilities) == 0
        assert len(p.populations) == 0


class TestStarSystemFactory:
    def test_creates_valid_system(self):
        ss = create_test_star_system()
        assert ss.name
        assert ss.global_location is not None
        assert len(ss.stars) > 0

    def test_with_planets(self):
        ss = create_test_star_system(num_planets=3)
        assert len(ss.planets) == 3

    def test_with_multiple_stars(self):
        ss = create_test_star_system(num_stars=2)
        assert len(ss.stars) == 2


class TestRaceConfigFactory:
    def test_creates_valid_config(self):
        rc = create_test_race_config()
        assert rc.race_id
        assert rc.name

    def test_override_race_id(self):
        rc = create_test_race_config(race_id="custom_race")
        assert rc.race_id == "custom_race"

    def test_to_dict_round_trip(self):
        from game.strategy.data.race_config import RaceConfig
        rc = create_test_race_config()
        d = rc.to_dict()
        restored = RaceConfig.from_dict(d)
        assert restored.race_id == rc.race_id


class TestFleetOrderFactory:
    def test_creates_move_order(self):
        from game.strategy.data.order_types import OrderType
        fo = create_test_fleet_order()
        assert fo.type == OrderType.MOVE
        assert fo.target is not None

    def test_override_type(self):
        from game.strategy.data.order_types import OrderType
        from game.core.hex_math import HexCoord
        fo = create_test_fleet_order(order_type=OrderType.WARP, target=HexCoord(5, 5))
        assert fo.type == OrderType.WARP


class TestShipInstanceFactory:
    def test_creates_valid_ship(self):
        si = create_test_ship_instance()
        assert si.instance_id
        assert si.design_id
        assert si.name
        assert si.is_alive

    def test_with_registries(self, fresh_registries):
        si = create_test_ship_instance(registries=fresh_registries)
        assert si._registries is not None

    def test_to_dict_has_all_fields(self):
        si = create_test_ship_instance()
        d = si.to_dict()
        assert 'instance_id' in d
        assert 'design_id' in d
        assert 'name' in d


class TestFleetFactory:
    def test_creates_valid_fleet(self):
        f = create_test_fleet()
        assert f.id is not None
        assert f.owner_id is not None
        assert f.location is not None

    def test_with_ships(self):
        f = create_test_fleet(num_ships=3)
        assert len(f.ships) == 3

    def test_with_registries(self, fresh_registries):
        f = create_test_fleet(registries=fresh_registries)
        # Fleet should have component_registry set
        assert f._component_registry is not None


class TestEmpireFactory:
    def test_creates_valid_empire(self):
        e = create_test_empire()
        assert e.id is not None
        assert e.name

    def test_with_fleets(self):
        e = create_test_empire(num_fleets=2)
        assert len(e.fleets) == 2

    def test_override_id(self):
        e = create_test_empire(empire_id=5)
        assert e.id == 5


class TestEventFactory:
    def test_creates_valid_event(self):
        e = create_test_event()
        assert e.event_type
        assert e.category
        assert e.message

    def test_to_dict_round_trip(self):
        from game.strategy.events.event_log import Event
        e = create_test_event()
        d = e.to_dict()
        restored = Event.from_dict(d)
        assert restored.event_type == e.event_type


class TestEventLogFactory:
    def test_creates_valid_log(self):
        log = create_test_event_log()
        assert len(log.get_all_events()) > 0

    def test_custom_count(self):
        log = create_test_event_log(num_events=5)
        assert len(log.get_all_events()) == 5


class TestPlayerConfigFactory:
    def test_creates_valid_config(self):
        pc = create_test_player_config()
        assert pc.name
        assert pc.theme

    def test_to_dict_round_trip(self):
        from game.strategy.engine.game_config import PlayerConfig
        pc = create_test_player_config()
        d = pc.to_dict()
        restored = PlayerConfig.from_dict(d)
        assert restored.name == pc.name


class TestGameConfigFactory:
    def test_creates_valid_config(self):
        gc = create_test_game_config()
        assert gc.galaxy_radius > 0
        assert len(gc.players) > 0

    def test_custom_players(self):
        gc = create_test_game_config(num_players=4)
        assert len(gc.players) == 4


class TestDesignMetadataFactory:
    def test_creates_valid_metadata(self):
        dm = create_test_design_metadata()
        assert dm.design_id
        assert dm.name
        assert dm.mass > 0

    def test_to_dict_round_trip(self):
        from game.strategy.data.design_metadata import DesignMetadata
        dm = create_test_design_metadata()
        d = dm.to_dict()
        restored = DesignMetadata.from_dict(d)
        assert restored.design_id == dm.design_id


class TestNodeStateFactory:
    def test_creates_valid_state(self):
        ns = create_test_node_state()
        assert isinstance(ns.current_level, int)
        assert isinstance(ns.current_chance, float)

    def test_to_dict_round_trip(self):
        from game.research.data.research_tracker import NodeState
        ns = create_test_node_state()
        d = ns.to_dict()
        restored = NodeState.from_dict(d)
        assert restored.current_level == ns.current_level


class TestResearchTrackerFactory:
    def test_creates_valid_tracker(self):
        rt = create_test_research_tracker()
        assert rt.session_seed is not None
        assert rt.rp_budget > 0
        assert len(rt.node_states) > 0

    def test_to_dict_round_trip(self):
        from game.research.data.research_tracker import ResearchTracker
        rt = create_test_research_tracker()
        d = rt.to_dict()
        restored = ResearchTracker.from_dict(d)
        assert restored.session_seed == rt.session_seed
        assert len(restored.node_states) == len(rt.node_states)
