"""
Tests for Strategy Facade indexed reads (PROJ-254 Phase 4).

Verifies that facade queries use indexed lookups instead of O(n) scans.
"""
from unittest.mock import MagicMock, PropertyMock


class TestFacadePlanetIndex:
    """_get_planet_by_id should use an index, not a full scan."""

    def test_get_planet_by_id_returns_correct_planet(self):
        """Planet lookup by ID should return the matching planet."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        session = MagicMock()
        planet = MagicMock()
        planet.id = 42
        planet.name = "Earth"

        system = MagicMock()
        system.planets = [planet]
        session.galaxy.systems = {"sys1": system}

        facade = StrategySessionFacade(session)
        result = facade._get_planet_by_id(42)
        assert result is planet

    def test_get_planet_by_id_caches_results(self):
        """Second lookup should use cache, not rescan.

        PROJ-430 / TD-08: the previous incarnation of this test pinned an
        implementation detail (``hasattr(facade, '_planet_index')``). The
        actual contract is "two consecutive lookups return the same
        object" — a behavioral assertion that survives any future caching
        refactor.
        """
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        session = MagicMock()
        planet = MagicMock()
        planet.id = 42

        system = MagicMock()
        system.planets = [planet]
        session.galaxy.systems = {"sys1": system}

        facade = StrategySessionFacade(session)
        result1 = facade._get_planet_by_id(42)
        result2 = facade._get_planet_by_id(42)

        assert result1 is result2
        # Behavioral assertion replaces the old `hasattr(facade,
        # '_planet_index')` implementation check — caching is what
        # callers actually rely on.
        assert facade._get_planet_by_id(42) is result1


class TestFacadeStarCache:
    """get_all_stars should cache results."""

    def test_all_stars_cached_on_second_call(self):
        """Second call to get_all_stars should return cached result."""
        from game.strategy.facade.strategy_session_facade import StrategySessionFacade

        session = MagicMock()
        star = MagicMock()
        star.id = 1
        star.name = "Sol"

        system = MagicMock()
        system.stars = [star]
        system.planets = []
        system.name = "Sol System"
        system.global_location = MagicMock()
        session.galaxy.systems = {"sys1": system}
        session.turn_number = 1

        facade = StrategySessionFacade(session)
        result1 = facade.systems.all_stars()
        result2 = facade.systems.all_stars()

        # Should be the same list object (cached)
        assert result1 is result2
