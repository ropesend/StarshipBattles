"""FEAT-27: warp generator boundary tests at small N.

Verifies the early-return contract that has been in place since before
FEAT-27 but was never explicitly covered:

- N=0 systems → no warp points generated, no error.
- N=1 system → no warp points generated (no other system to link to).
- N=2 systems → exactly one warp link (one warp point per system).

These tests guard the FEAT-27 invariant that "a single-system galaxy
has no warp lanes" while leaving the multi-system path untouched.
"""
import random

from game.strategy.engine.game_config import GameConfig
from game.strategy.engine.game_initializer import GameInitializer


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
