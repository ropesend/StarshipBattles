"""PROJ-475 Phase 1 Task 1.3 — ``PlanetInfo.has_build_yard`` projection.

``has_build_yard`` is ``True`` when the colony has a planetary yard (per
``colony_has_planetary_yard``) OR a space shipyard. The planetary-yard check
needs ``registries``, which the DTO ``from_planet`` cannot reach, so the slice
resolves it at projection time (mirroring the ``owner_system_name`` pattern)
and passes it into the DTO, where it is ORed with ``has_space_shipyard``.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

from game.core.hex_math import HexCoord
from game.strategy.facade.dto import PlanetInfo
from game.strategy.facade.slices.planet_slice import PlanetSlice


def _planet(planet_id: int = 1, *, has_space_shipyard: bool = False):
    return SimpleNamespace(
        id=planet_id,
        name="P",
        planet_type=SimpleNamespace(name="TERRESTRIAL"),
        location=HexCoord(0, 0),
        orbit_distance=1,
        owner_id=2,
        has_space_shipyard=has_space_shipyard,
        total_population=0,
        max_population=0,
        populations=[],
        facilities=[],
    )


class TestPlanetInfoHasBuildYardField:
    def test_field_defaults_false(self) -> None:
        info = PlanetInfo.from_planet(_planet())
        assert info.has_build_yard is False

    def test_true_when_space_shipyard(self) -> None:
        info = PlanetInfo.from_planet(_planet(has_space_shipyard=True))
        assert info.has_build_yard is True

    def test_planetary_yard_flag_ors_in(self) -> None:
        info = PlanetInfo.from_planet(_planet(), has_planetary_yard=True)
        assert info.has_build_yard is True


class TestPlanetSliceResolvesBuildYard:
    def test_slice_resolves_planetary_yard_with_registries(self, monkeypatch) -> None:
        planet = _planet(7)
        registries = object()
        session = SimpleNamespace(registries=registries)
        state = SimpleNamespace(
            _session=session,
            get_planet_by_id=Mock(return_value=planet),
        )
        seen = {}

        def fake_yard(colony, regs):
            seen["colony"] = colony
            seen["registries"] = regs
            return True

        monkeypatch.setattr(
            "game.strategy.data.build_queue_source.colony_has_planetary_yard",
            fake_yard,
        )

        info = PlanetSlice(state).get_planet(7)

        assert info.has_build_yard is True
        assert seen["colony"] is planet
        assert seen["registries"] is registries

    def test_slice_false_when_no_yard_and_no_shipyard(self, monkeypatch) -> None:
        planet = _planet(7, has_space_shipyard=False)
        state = SimpleNamespace(
            _session=SimpleNamespace(registries=object()),
            get_planet_by_id=Mock(return_value=planet),
        )
        monkeypatch.setattr(
            "game.strategy.data.build_queue_source.colony_has_planetary_yard",
            lambda colony, regs: False,
        )

        info = PlanetSlice(state).get_planet(7)

        assert info.has_build_yard is False

    def test_slice_degrades_to_false_when_resolver_raises(self, monkeypatch) -> None:
        """PROJ-475 Phase 5 (audit Finding 3b): the planetary-yard resolver
        catches ``(AttributeError, TypeError)`` from stub/bootstrap colonies and
        degrades to ``False`` (the planet then has no build yard unless it has a
        space shipyard) instead of propagating."""
        planet = _planet(7, has_space_shipyard=False)
        state = SimpleNamespace(
            _session=SimpleNamespace(registries=object()),
            get_planet_by_id=Mock(return_value=planet),
        )

        def _boom(colony, regs):
            raise TypeError("bare Mock().facilities is not iterable")

        monkeypatch.setattr(
            "game.strategy.data.build_queue_source.colony_has_planetary_yard",
            _boom,
        )

        info = PlanetSlice(state).get_planet(7)

        assert info.has_build_yard is False
