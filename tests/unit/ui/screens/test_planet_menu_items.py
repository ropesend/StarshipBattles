"""Tests for the pure planet context-menu item builder (QA Observation B).

The builder takes a planet (with ``facilities`` and ``owner_id``), the
galaxy (for the same-hex group lookup used by Recover rows), and a
``{action_name: Callable}`` callbacks dict. It returns a list of
``PlanetMenuItem`` rows in stable display order.
"""
from __future__ import annotations

from types import SimpleNamespace
from typing import Callable

import pytest

from game.ui.screens.planet_menu_items import (
    PlanetMenuItem,
    build_menu_items,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _facility(abilities: set[str]) -> SimpleNamespace:
    """Stub facility exposing ``abilities`` through ``FacilityAbilitySource``.

    The real source pulls from ``facility.components.<comp>.abilities``;
    here we monkey-patch a thin shape recognised by the builder via
    ``FacilityAbilitySource(facility, planet).get_abilities()``. To keep
    the unit test isolated, we instead use the module-level helper the
    builder exposes (``_facility_has_ability``) by stubbing the planet's
    ``facilities`` list and stubbing the ability check with a patched
    helper. See ``_patch_helper`` below.
    """
    return SimpleNamespace(
        is_operational=True,
        abilities=set(abilities),
    )


def _planet(
    *,
    facility_abilities: set[str] | None = None,
    owner_id: int = 1,
    planet_id: int = 7,
    location: object = SimpleNamespace(q=0, r=0),
    global_hex: object | None = None,
) -> SimpleNamespace:
    fac = _facility(facility_abilities or set())
    return SimpleNamespace(
        id=planet_id,
        owner_id=owner_id,
        location=location,
        global_hex=global_hex,
        facilities=[fac],
        name=f"Planet{planet_id}",
    )


def _galaxy_with_groups(
    *,
    groups: list[tuple[str, int, object]] | None = None,
) -> SimpleNamespace:
    by_empire: dict[int, list[SimpleNamespace]] = {}
    for kind, oid, loc in groups or ():
        by_empire.setdefault(oid, []).append(
            SimpleNamespace(group_kind=kind, owner_id=oid, location=loc, id=0)
        )
    empires = [
        SimpleNamespace(id=oid, fleets=fs) for oid, fs in by_empire.items()
    ]
    return SimpleNamespace(empires=empires, systems=[])


def _all_callbacks() -> tuple[dict[str, Callable[[], None]], dict[str, int]]:
    calls: dict[str, int] = {}

    def make(name: str) -> Callable[[], None]:
        def _cb() -> None:
            calls[name] = calls.get(name, 0) + 1
        return _cb

    return (
        {
            "lay_mines": make("lay_mines"),
            "launch_fighters": make("launch_fighters"),
            "launch_satellites": make("launch_satellites"),
            "recover_fighters": make("recover_fighters"),
            "recover_satellites": make("recover_satellites"),
        },
        calls,
    )


@pytest.fixture(autouse=True)
def _patch_ability_helper(monkeypatch: pytest.MonkeyPatch) -> None:
    """Replace ``_facility_has_ability`` to read directly from the stub
    facility's ``abilities`` set, bypassing the real registry-driven
    ``FacilityAbilitySource`` path.
    """
    import game.ui.screens.planet_menu_items as mod

    def fake_has(planet: object, ability_name: str) -> bool:
        for fac in getattr(planet, "facilities", []) or []:
            if not getattr(fac, "is_operational", True):
                continue
            if ability_name in getattr(fac, "abilities", set()):
                return True
        return False

    monkeypatch.setattr(mod, "_facility_has_ability", fake_has)


# ---------------------------------------------------------------------------
# Capability matrix
# ---------------------------------------------------------------------------


class TestPlanetMenuCapabilityMatrix:
    def test_lay_mines_visible_with_layer_facility(self) -> None:
        planet = _planet(facility_abilities={"StrategicMineLayer"})
        cbs, _ = _all_callbacks()
        items = build_menu_items(planet, _galaxy_with_groups(), cbs)
        assert "Lay Mines" in [it.label for it in items]

    def test_lay_mines_hidden_without_facility_ability(self) -> None:
        planet = _planet(facility_abilities=set())
        cbs, _ = _all_callbacks()
        items = build_menu_items(planet, _galaxy_with_groups(), cbs)
        assert "Lay Mines" not in [it.label for it in items]

    def test_launch_fighters_visible_with_facility(self) -> None:
        planet = _planet(facility_abilities={"StrategicFighterLaunch"})
        cbs, _ = _all_callbacks()
        items = build_menu_items(planet, _galaxy_with_groups(), cbs)
        assert "Launch Fighters" in [it.label for it in items]

    def test_launch_satellites_visible_with_facility(self) -> None:
        planet = _planet(facility_abilities={"StrategicSatelliteLaunch"})
        cbs, _ = _all_callbacks()
        items = build_menu_items(planet, _galaxy_with_groups(), cbs)
        assert "Launch Satellites" in [it.label for it in items]

    def test_recover_fighters_requires_both_facility_and_matching_group(self) -> None:
        loc = SimpleNamespace(q=5, r=3)
        planet = _planet(
            facility_abilities={"RecoverFighters"},
            owner_id=11,
            location=loc,
            global_hex=loc,
        )
        # No group present -> hidden.
        cbs, _ = _all_callbacks()
        items = build_menu_items(planet, _galaxy_with_groups(), cbs)
        assert "Recover Fighters" not in [it.label for it in items]

        # Add matching group at hex -> visible.
        galaxy = _galaxy_with_groups(
            groups=[("fighter_group", 11, loc)],
        )
        items = build_menu_items(planet, galaxy, cbs)
        assert "Recover Fighters" in [it.label for it in items]

    def test_recover_satellites_requires_both_facility_and_matching_group(self) -> None:
        loc = SimpleNamespace(q=1, r=1)
        planet = _planet(
            facility_abilities={"RecoverSatellites"},
            owner_id=4,
            location=loc,
            global_hex=loc,
        )
        cbs, _ = _all_callbacks()
        galaxy_empty = _galaxy_with_groups()
        items = build_menu_items(planet, galaxy_empty, cbs)
        assert "Recover Satellites" not in [it.label for it in items]

        galaxy_with = _galaxy_with_groups(
            groups=[("satellite_group", 4, loc)],
        )
        items = build_menu_items(planet, galaxy_with, cbs)
        assert "Recover Satellites" in [it.label for it in items]

    def test_recover_hidden_when_group_owned_by_other_empire(self) -> None:
        loc = SimpleNamespace(q=2, r=2)
        planet = _planet(
            facility_abilities={"RecoverFighters"},
            owner_id=7,
            location=loc,
            global_hex=loc,
        )
        # Fighter group at hex but owned by enemy empire 99.
        galaxy = _galaxy_with_groups(
            groups=[("fighter_group", 99, loc)],
        )
        cbs, _ = _all_callbacks()
        items = build_menu_items(planet, galaxy, cbs)
        assert "Recover Fighters" not in [it.label for it in items]

    def test_callback_invoked_when_visible_row_triggered(self) -> None:
        planet = _planet(facility_abilities={"StrategicMineLayer"})
        cbs, calls = _all_callbacks()
        items = build_menu_items(planet, _galaxy_with_groups(), cbs)
        lay = next(it for it in items if it.label == "Lay Mines")
        assert isinstance(lay, PlanetMenuItem)
        lay.callback()
        assert calls.get("lay_mines") == 1

    def test_row_omitted_when_callback_missing(self) -> None:
        """If the user passes a callbacks dict missing a key, that row
        is omitted even when its capability gate would pass.
        """
        planet = _planet(facility_abilities={"StrategicMineLayer"})
        items = build_menu_items(planet, _galaxy_with_groups(), {})
        assert items == []
