"""PROJ-477 Phase 2 Task 2.4 — facade.spatial namespace tests."""
from unittest.mock import MagicMock

import pytest

from game.core.hex_math import HexCoord
from game.strategy.facade.strategy_session_facade import StrategySessionFacade


class TestFacadeSpatial:
    @pytest.fixture
    def mock_session(self):
        return MagicMock()

    @pytest.fixture
    def facade(self, mock_session):
        return StrategySessionFacade(mock_session)

    def test_spatial_namespace_exposed(self, facade):
        """``facade.spatial`` is wired in the composer."""
        assert facade.spatial is not None

    def test_contents_at_hex_groups_multi_hex_zone(self, facade, mock_session):
        """A multi-hex zone occupying the queried hex (but centered elsewhere)
        is reported — multi-hex membership preserved, distinct from
        ``planets.at_hex`` exact-center semantics."""
        target = HexCoord(7, 7)
        planet = MagicMock()
        planet.name = "Terra"
        dyson = MagicMock()
        dyson.name = "Dyson Alpha"

        mock_session.galaxy.get_planets_at_global_hex.side_effect = (
            lambda h: [planet] if h == target else []
        )
        mock_session.galaxy.get_zones_at_global_hex.side_effect = (
            lambda h: [dyson] if h == target else []
        )
        # Avoid the warp-point branch tripping on the MagicMock galaxy.state.
        mock_session.galaxy.state.global_hex_warp_points = {}

        contents = facade.spatial.contents_at_hex(target)
        assert contents.planet_names == ("Terra",)
        assert contents.zone_names == ("Dyson Alpha",)
        assert contents.hex == target
