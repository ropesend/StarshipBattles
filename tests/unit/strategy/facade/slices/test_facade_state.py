from types import SimpleNamespace
from unittest.mock import Mock

from game.strategy.facade.slices._facade_state import FacadeSessionState


def test_build_planet_index_collects_planets_across_systems() -> None:
    planet_a = SimpleNamespace(id=101)
    planet_b = SimpleNamespace(id=202)
    session = SimpleNamespace(
        galaxy=SimpleNamespace(
            systems={
                "alpha": SimpleNamespace(planets=[planet_a]),
                "beta": SimpleNamespace(planets=[planet_b]),
            }
        )
    )
    state = FacadeSessionState(session)

    assert state.build_planet_index() == {101: planet_a, 202: planet_b}


def test_get_planet_by_id_reuses_cached_index() -> None:
    planet = SimpleNamespace(id=7)
    state = FacadeSessionState(SimpleNamespace())
    state.build_planet_index = Mock(return_value={7: planet})

    assert state.get_planet_by_id(7) is planet
    assert state.get_planet_by_id(999) is None
    state.build_planet_index.assert_called_once_with()


def test_get_fleet_by_id_delegates_to_session_lookup() -> None:
    fleet = SimpleNamespace(id=3)
    session = SimpleNamespace(_get_fleet_by_id=Mock(return_value=fleet))
    state = FacadeSessionState(session)

    assert state.get_fleet_by_id(3) is fleet
    session._get_fleet_by_id.assert_called_once_with(3)


def test_get_empire_by_id_scans_session_empires() -> None:
    empire_a = SimpleNamespace(id=1)
    empire_b = SimpleNamespace(id=2)
    state = FacadeSessionState(SimpleNamespace(empires=[empire_a, empire_b]))

    assert state.get_empire_by_id(2) is empire_b
    assert state.get_empire_by_id(999) is None


def test_get_empire_by_id_uses_lazy_index_built_once() -> None:
    """F-A-031: get_empire_by_id builds the empire-index lazily and reuses it."""
    empire_a = SimpleNamespace(id=1)
    empire_b = SimpleNamespace(id=2)
    empires = [empire_a, empire_b]

    class _ScanCountingEmpires(list):
        scans = 0

        def __iter__(self):
            type(self).scans += 1
            return list.__iter__(self)

    counted = _ScanCountingEmpires(empires)
    state = FacadeSessionState(SimpleNamespace(empires=counted))

    assert state.get_empire_by_id(2) is empire_b
    assert state.get_empire_by_id(1) is empire_a
    assert state.get_empire_by_id(999) is None
    # Only the first call iterates session.empires to build the index;
    # subsequent calls hit the cached dict.
    assert _ScanCountingEmpires.scans == 1
    assert state.empire_index == {1: empire_a, 2: empire_b}


def test_invalidate_all_clears_empire_index() -> None:
    state = FacadeSessionState(SimpleNamespace())
    state.empire_index = {1: object()}
    state.invalidate_all()
    assert state.empire_index is None


def test_invalidate_all_clears_per_turn_caches() -> None:
    state = FacadeSessionState(SimpleNamespace())
    state.planet_index = {1: object()}
    state.all_stars_cache = [object()]
    state.fleets_by_hex_cache = {object(): [object()]}
    state.race_registry = object()

    state.invalidate_all()

    assert state.planet_index is None
    assert state.all_stars_cache is None
    assert state.fleets_by_hex_cache is None
    assert state.race_registry is not None
