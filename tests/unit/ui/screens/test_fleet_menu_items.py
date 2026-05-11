"""Tests for the pure fleet context-menu item builder (issue #20).

Layer 1 of the issue #20 test plan: capability matrix + shortcut display.
No pygame, no UI — only the pure ``build_menu_items`` function.

The builder takes a fleet (with ``capabilities``), the galaxy (for the
"at a colonisable planet hex" check), and an ``InputMapper``-like object
that returns shortcut display strings, and returns a list of
``FleetMenuItem`` rows in stable display order.
"""
from __future__ import annotations

from types import SimpleNamespace

from game.core.input_actions import InputAction
from game.ui.screens.fleet_menu_items import (
    FleetMenuItem,
    build_menu_items,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _make_capabilities(
    *,
    abilities: set[str] | None = None,
    can_warp: bool = False,
    self_destruct_ships: int = 0,
) -> SimpleNamespace:
    """Build a fake ``fleet.capabilities`` object."""
    abilities = set(abilities or ())

    def has_ability(name: str) -> bool:
        return name in abilities

    def ships_with_ability(name: str) -> list[object]:
        if name == "SelfDestruct":
            return [object() for _ in range(self_destruct_ships)]
        return [object()] if name in abilities else []

    return SimpleNamespace(
        has_ability=has_ability,
        ships_with_ability=ships_with_ability,
        can_use_warp=lambda: can_warp,
    )


def _make_fleet(
    *,
    abilities: set[str] | None = None,
    can_warp: bool = False,
    self_destruct_ships: int = 0,
    location: object = SimpleNamespace(q=0, r=0),
) -> SimpleNamespace:
    return SimpleNamespace(
        capabilities=_make_capabilities(
            abilities=abilities,
            can_warp=can_warp,
            self_destruct_ships=self_destruct_ships,
        ),
        location=location,
    )


def _make_galaxy(unowned_planets_at: list[object] | None = None) -> SimpleNamespace:
    """Galaxy that returns the given planet list at the fleet's location."""
    planets = list(unowned_planets_at or ())

    def get_planets_at_global_hex(_hex: object) -> list[object]:
        return list(planets)

    return SimpleNamespace(get_planets_at_global_hex=get_planets_at_global_hex)


def _planet(*, owner_id: int | None) -> SimpleNamespace:
    return SimpleNamespace(owner_id=owner_id)


def _mapper(canned: dict[InputAction, str] | None = None) -> SimpleNamespace:
    """Fake InputMapper with ``get_display_text`` returning canned strings."""
    canned = canned or {}

    def get_display_text(action: InputAction) -> str:
        return canned.get(action, "")

    return SimpleNamespace(get_display_text=get_display_text)


def _actions(items: list[FleetMenuItem]) -> list[InputAction]:
    return [item.action for item in items]


# ---------------------------------------------------------------------------
# T1-T8: Capability matrix
# ---------------------------------------------------------------------------


class TestCapabilityMatrix:
    """Each fleet shape produces exactly the menu items its capabilities allow."""

    def test_T1_empty_placeholder_fleet_shows_only_move_and_join(self) -> None:
        fleet = _make_fleet()
        items = build_menu_items(fleet, _make_galaxy(), _mapper())
        assert _actions(items) == [InputAction.FLEET_MOVE, InputAction.FLEET_JOIN]

    def test_T2_cargo_plus_warp_shows_cargo_group_and_warp(self) -> None:
        fleet = _make_fleet(abilities={"CargoStorage"}, can_warp=True)
        items = build_menu_items(fleet, _make_galaxy(), _mapper())
        assert _actions(items) == [
            InputAction.FLEET_MOVE,
            InputAction.FLEET_JOIN,
            InputAction.FLEET_TRANSFER,
            InputAction.FLEET_DROP_CARGO,
            InputAction.FLEET_LOAD_CARGO,
            InputAction.FLEET_WARP,
        ]

    def test_T3_colonize_hidden_when_no_unowned_planet_at_hex(self) -> None:
        fleet = _make_fleet(
            abilities={"CargoStorage", "ColonizePlanet"},
            can_warp=True,
        )
        # Galaxy returns no planets at this hex.
        items = build_menu_items(fleet, _make_galaxy(), _mapper())
        assert InputAction.FLEET_COLONIZE not in _actions(items)

    def test_T4_colonize_visible_when_at_unowned_planet_hex(self) -> None:
        fleet = _make_fleet(
            abilities={"CargoStorage", "ColonizePlanet"},
            can_warp=True,
        )
        galaxy = _make_galaxy(unowned_planets_at=[_planet(owner_id=None)])
        items = build_menu_items(fleet, galaxy, _mapper())
        assert InputAction.FLEET_COLONIZE in _actions(items)

    def test_T5_every_superweapon_fleet(self) -> None:
        fleet = _make_fleet(
            abilities={
                "OpenWarpPoint",
                "CloseWarpPoint",
                "DestroyPlanet",
                "DestroyStar",
                "CreateDysonSphere",
                "SelfDestruct",
            },
            self_destruct_ships=2,
        )
        items = build_menu_items(fleet, _make_galaxy(), _mapper())
        assert _actions(items) == [
            InputAction.FLEET_MOVE,
            InputAction.FLEET_JOIN,
            InputAction.FLEET_OPEN_WARP_POINT,
            InputAction.FLEET_CLOSE_WARP_POINT,
            InputAction.FLEET_IMPLODE_PLANET,
            InputAction.FLEET_STELLERATE_STAR,
            InputAction.FLEET_CREATE_DYSON_SPHERE,
            InputAction.FLEET_SELF_DESTRUCT,
        ]

    def test_T6_self_destruct_visible_with_ships(self) -> None:
        fleet = _make_fleet(
            abilities={"SelfDestruct"},
            self_destruct_ships=1,
        )
        items = build_menu_items(fleet, _make_galaxy(), _mapper())
        assert InputAction.FLEET_SELF_DESTRUCT in _actions(items)

    def test_T7_self_destruct_hidden_when_no_ships_have_it(self) -> None:
        # Capability flag claims SelfDestruct but no ship actually has the
        # component — emulates a degenerate fleet. Builder uses
        # ships_with_ability for SelfDestruct, so the row is hidden.
        fleet = _make_fleet(
            abilities=set(),  # has_ability returns False
            self_destruct_ships=0,
        )
        items = build_menu_items(fleet, _make_galaxy(), _mapper())
        assert InputAction.FLEET_SELF_DESTRUCT not in _actions(items)

    def test_T8_colonize_hidden_when_planets_at_hex_are_owned(self) -> None:
        fleet = _make_fleet(abilities={"ColonizePlanet"})
        # Owned planet -> filtered out, no colonisable target here.
        galaxy = _make_galaxy(unowned_planets_at=[_planet(owner_id=42)])
        items = build_menu_items(fleet, galaxy, _mapper())
        assert InputAction.FLEET_COLONIZE not in _actions(items)


# ---------------------------------------------------------------------------
# T9-T11: Shortcut display
# ---------------------------------------------------------------------------


class TestShortcutDisplay:
    def test_T9_shortcuts_carried_through_from_mapper(self) -> None:
        fleet = _make_fleet(abilities={"OpenWarpPoint"})
        mapper = _mapper(
            {
                InputAction.FLEET_MOVE: "M",
                InputAction.FLEET_JOIN: "J",
                InputAction.FLEET_OPEN_WARP_POINT: "Ctrl+W",
            }
        )
        items = build_menu_items(fleet, _make_galaxy(), mapper)
        by_action = {item.action: item.shortcut for item in items}
        assert by_action[InputAction.FLEET_MOVE] == "M"
        assert by_action[InputAction.FLEET_OPEN_WARP_POINT] == "Ctrl+W"

    def test_T10_unbound_action_yields_empty_shortcut_string(self) -> None:
        fleet = _make_fleet()
        mapper = _mapper()  # returns "" for everything
        items = build_menu_items(fleet, _make_galaxy(), mapper)
        # Items still appear; the UI is responsible for hiding the
        # shortcut column when it's empty.
        assert all(item.shortcut == "" for item in items)
        assert _actions(items) == [InputAction.FLEET_MOVE, InputAction.FLEET_JOIN]

    def test_T11_real_input_mapper_loads_default_bindings(self) -> None:
        """Smoke check: the real InputMapper against the production
        defaults file returns a non-empty 'M' for FLEET_MOVE.
        """
        from game.ui.services.input_mapper import InputMapper
        from game.core.paths import Paths

        mapper = InputMapper()
        mapper.load(defaults_path=Paths.DEFAULT_KEYBINDINGS_FILE)
        text = mapper.get_display_text(InputAction.FLEET_MOVE)
        assert text == "M"


# ---------------------------------------------------------------------------
# T12-T13: Ordering / determinism
# ---------------------------------------------------------------------------


class TestOrderingAndStability:
    def test_T12_stable_ordering_independent_of_capability_call_sequence(self) -> None:
        # Build identical fleets in two orderings of capability hashing —
        # builder must return items in the SAME declared order.
        fleet1 = _make_fleet(
            abilities={"CargoStorage", "DestroyPlanet"}, can_warp=True
        )
        fleet2 = _make_fleet(
            abilities={"DestroyPlanet", "CargoStorage"}, can_warp=True
        )
        items1 = build_menu_items(fleet1, _make_galaxy(), _mapper())
        items2 = build_menu_items(fleet2, _make_galaxy(), _mapper())
        assert _actions(items1) == _actions(items2)
        # And: cargo group precedes superweapon group, in declared order.
        actions = _actions(items1)
        assert actions.index(InputAction.FLEET_TRANSFER) < actions.index(
            InputAction.FLEET_IMPLODE_PLANET
        )

    def test_T13_builder_is_deterministic(self) -> None:
        fleet = _make_fleet(abilities={"CargoStorage"})
        galaxy = _make_galaxy()
        mapper = _mapper()
        a = build_menu_items(fleet, galaxy, mapper)
        b = build_menu_items(fleet, galaxy, mapper)
        assert _actions(a) == _actions(b)
        assert [item.label for item in a] == [item.label for item in b]


# ---------------------------------------------------------------------------
# Sanity: returned dataclass shape
# ---------------------------------------------------------------------------


class TestFleetMenuItemShape:
    def test_item_carries_label_action_and_shortcut(self) -> None:
        fleet = _make_fleet()
        mapper = _mapper({InputAction.FLEET_MOVE: "M"})
        items = build_menu_items(fleet, _make_galaxy(), mapper)
        move = next(it for it in items if it.action == InputAction.FLEET_MOVE)
        assert isinstance(move, FleetMenuItem)
        assert move.label == "Move"
        assert move.action == InputAction.FLEET_MOVE
        assert move.shortcut == "M"
