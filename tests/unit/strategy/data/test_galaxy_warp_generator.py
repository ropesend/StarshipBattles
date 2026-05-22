"""FEAT-27: warp generator boundary tests at small N.

Verifies the early-return contract that has been in place since before
FEAT-27 but was never explicitly covered:

- N=0 systems → no warp points generated, no error.
- N=1 system → no warp points generated (no other system to link to).
- N=2 systems → exactly one warp link (one warp point per system).

These tests guard the FEAT-27 invariant that "a single-system galaxy
has no warp lanes" while leaving the multi-system path untouched.
"""
import math
import random
from types import SimpleNamespace

import game.strategy.data.galaxy_warp_generator as warp_mod
from game.core.hex_math import HexCoord
from game.strategy.data.star_system import StarSystem, WarpPoint
from game.strategy.data.galaxy_warp_generator import (
    GalaxyWarpGenerator,
    _roll_warp_type,
)
from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.game_initializer import GameInitializer


def _make_system(name: str, q: int, r: int, region_id=None) -> StarSystem:
    return StarSystem(
        name,
        HexCoord(q, r),
        stars=[SimpleNamespace(radius_hexes=1)],
        region_id=region_id,
    )


def _total_warp_points(galaxy) -> int:
    return sum(len(sys.warp_points) for sys in galaxy.systems.values())


class TestWarpGenerationSmallN:

    def test_n0_yields_no_warp_points(self):
        # GameConfig validator forbids system_count=0, so we drive the
        # underlying generator directly with the public Galaxy API.
        from game.strategy.data.galaxy import Galaxy

        galaxy = Galaxy(radius=2000)
        galaxy.generate_warp_lanes()
        assert _total_warp_points(galaxy) == 0

    def test_n1_yields_no_warp_points(self):
        config = GameConfig(
            system_count=1,
            galaxy_radius=2000,
            galaxy_seed=42,
        )
        galaxy, _empires = GameInitializer.initialize(config)
        assert len(galaxy.systems) == 1
        assert _total_warp_points(galaxy) == 0

    def test_n2_yields_exactly_one_link(self):
        config = GameConfig(
            system_count=2,
            galaxy_radius=2000,
            galaxy_seed=42,
        )
        galaxy, _empires = GameInitializer.initialize(config)
        assert len(galaxy.systems) == 2
        # Two systems linked by exactly one bidirectional warp lane =
        # one warp point per system, total 2.
        assert _total_warp_points(galaxy) == 2

    def test_n2_far_apart_systems_still_link(self):
        """Regression: two N=2 systems many cell-widths apart must link.

        Reproduces the seed-2 isolation: at galaxy_radius=4000 the random
        placement strategy can drop two systems at hex-distance ~4101 with
        no other points in between. The warp MST must still produce exactly
        one bidirectional link.
        """
        from game.strategy.data.galaxy import Galaxy
        from game.strategy.data.star_system import StarSystem
        from game.core.hex_math import HexCoord

        galaxy = Galaxy(radius=4000)
        sys_a = StarSystem(
            "Alpha",
            HexCoord(2844, -2615),
            stars=[SimpleNamespace(radius_hexes=1)],
        )
        sys_b = StarSystem(
            "Beta",
            HexCoord(2029, 1486),
            stars=[SimpleNamespace(radius_hexes=1)],
        )
        galaxy.add_system(sys_a)
        galaxy.add_system(sys_b)

        galaxy.generate_warp_lanes()

        assert len(sys_a.warp_points) == 1
        assert len(sys_b.warp_points) == 1
        assert sys_a.warp_points[0].destination_id == sys_b.name
        assert sys_b.warp_points[0].destination_id == sys_a.name
        assert _total_warp_points(galaxy) == 2

    def test_n2_initialize_seed_2_far_apart_links(self):
        """End-to-end: GameInitializer with the known-bad seed=2 reproducer
        must still produce a connected N=2 galaxy with one warp link.
        """
        config = GameConfig(
            system_count=2,
            galaxy_radius=4000,
            galaxy_seed=2,
        )
        galaxy, _empires = GameInitializer.initialize(config)
        assert len(galaxy.systems) == 2
        assert _total_warp_points(galaxy) == 2
        for sys in galaxy.systems.values():
            assert len(sys.warp_points) >= 1, (
                f"System {sys.name} at {sys.global_location} is isolated"
            )


class TestWarpGeneratorHelpers:
    def test_angle_clear_rejects_existing_warp_line_within_threshold(self):
        generator = GalaxyWarpGenerator()
        system = _make_system("Alpha", 0, 0)

        assert generator._is_angle_clear(system, 0.0)

        system.add_warp_point("Beta", HexCoord(10, 0))

        assert not generator._is_angle_clear(
            system,
            math.radians(10),
            threshold_deg=30,
        )
        assert generator._is_angle_clear(
            system,
            math.radians(60),
            threshold_deg=30,
        )

    def test_apply_mst_edges_links_shortest_noncyclic_edges(self, monkeypatch):
        generator = GalaxyWarpGenerator()
        systems = [
            _make_system("Alpha", 0, 0),
            _make_system("Beta", 10, 0),
            _make_system("Gamma", 20, 0),
        ]
        created = []

        def record_link(sys_a, sys_b, rng):
            created.append((sys_a.name, sys_b.name))

        monkeypatch.setattr(generator, "create_warp_link", record_link)

        generator._apply_mst_edges(
            systems,
            [
                (1, 0, 1),
                (2, 1, 2),
                (3, 0, 2),
            ],
            random.Random(0),
        )

        assert created == [("Alpha", "Beta"), ("Beta", "Gamma")]

    def test_create_warp_link_adds_reciprocal_points_and_skips_duplicates(
        self,
        monkeypatch,
    ):
        generator = GalaxyWarpGenerator()
        alpha = _make_system("Alpha", 0, 0)
        beta = _make_system("Beta", 50, 0)
        monkeypatch.setattr(
            generator,
            "_calculate_warp_distance",
            lambda _system, _rng: 12.0,
        )

        generator.create_warp_link(alpha, beta, random.Random(0))
        generator.create_warp_link(alpha, beta, random.Random(0))

        assert [wp.destination_id for wp in alpha.warp_points] == ["Beta"]
        assert [wp.destination_id for wp in beta.warp_points] == ["Alpha"]
        assert alpha.warp_points[0].location != HexCoord(0, 0)
        assert beta.warp_points[0].location != HexCoord(0, 0)

    def test_roll_warp_type_uses_weight_boundaries(self):
        class FixedRng:
            def __init__(self, pick: int) -> None:
                self.pick = pick

            def randint(self, low: int, high: int) -> int:
                assert (low, high) == (1, 100)
                return self.pick

        assert _roll_warp_type(FixedRng(1)) == "stable"
        assert _roll_warp_type(FixedRng(80)) == "stable"
        assert _roll_warp_type(FixedRng(81)) == "unstable"
        assert _roll_warp_type(FixedRng(90)) == "unstable"
        assert _roll_warp_type(FixedRng(91)) == "dimensional_rift"
        assert _roll_warp_type(FixedRng(97)) == "dimensional_rift"
        assert _roll_warp_type(FixedRng(98)) == "precursor_gateway"
        assert _roll_warp_type(FixedRng(100)) == "precursor_gateway"

    def test_apply_warp_point_intrinsics_rolls_type_and_respects_existing(
        self,
        monkeypatch,
    ):
        system = _make_system("Alpha", 0, 0)
        rolled_point = WarpPoint("Beta", HexCoord(1, 0))
        preset_type_point = WarpPoint("Gamma", HexCoord(2, 0), warp_type="unstable")
        preset_abilities_point = WarpPoint(
            "Delta",
            HexCoord(3, 0),
            intrinsic_abilities={"FuelDrain": {"rate": 0.1}},
        )
        system.warp_points = [
            rolled_point,
            preset_type_point,
            preset_abilities_point,
        ]
        type_templates = {
            "unstable": {"abilities": {"FuelDrain": {"rate": 0.25}}},
        }
        monkeypatch.setattr(
            warp_mod,
            "_load_warp_point_types",
            lambda: type_templates,
        )
        monkeypatch.setattr(warp_mod, "_roll_warp_type", lambda _rng: "unstable")

        import game.strategy.services.ability_sources as ability_sources

        monkeypatch.setattr(
            ability_sources,
            "roll_intrinsic_abilities",
            lambda template, _rng: {"rolled": template},
        )

        warp_mod._apply_warp_point_intrinsic_abilities([system], rng=random.Random(7))

        assert rolled_point.warp_type == "unstable"
        assert rolled_point.intrinsic_abilities == {
            "rolled": {"FuelDrain": {"rate": 0.25}},
        }
        assert preset_type_point.warp_type == "unstable"
        assert preset_type_point.intrinsic_abilities == {}
        assert preset_abilities_point.warp_type == "stable"
        assert preset_abilities_point.intrinsic_abilities == {
            "FuelDrain": {"rate": 0.1},
        }
