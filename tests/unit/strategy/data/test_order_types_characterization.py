"""Characterization tests for game/strategy/data/order_types.py.

PROJ-335 Phase 1. Pins the 10-branch ``Order.to_dict`` dispatch ladder,
the three OrderType frozensets, the simple ``from_dict`` round-trip, and
the ``__repr__`` two-form output.

D-007 observations preserved as assertions:

- The HexCoord branch emits ``{q, r}`` with **no** 'type' discriminator
  (asymmetric vs. every other branch).
- ``from_dict`` does not round-trip a HexCoord-emitted dict alone — that
  path requires OrderSerializer for reference resolution. The simple
  ``{type: 'dict', value: …}`` wrapper is the only branch that
  round-trips through ``from_dict`` directly.

Planet/Fleet are stubbed via SimpleNamespace per D-004; the production
``isinstance`` dispatch checks against the real Planet/Fleet classes
imported at runtime, so we substitute monkeypatching to exercise those
branches without dragging in the full domain graph.
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.order_types import (
    ACTION_ORDER_TYPES,
    MOVEMENT_ORDER_TYPES,
    PLANET_ACTION_ORDER_TYPES,
    Order,
    OrderType,
)


# ---------------------------------------------------------------------------
# Stubs and helpers
# ---------------------------------------------------------------------------

class _PlanetStub:
    """Stub class used as the runtime Planet for isinstance dispatch."""

    def __init__(self, planet_id: str = "p1"):
        self.id = planet_id


class _FleetStub:
    """Stub class used as the runtime Fleet for isinstance dispatch."""

    def __init__(self, fleet_id: str = "f1"):
        self.id = fleet_id


@pytest.fixture
def patch_domain_classes(monkeypatch):
    """Patch the runtime imports inside Order.to_dict so isinstance(...)
    matches our stub classes instead of the heavy real Planet/Fleet."""
    import game.strategy.data.fleet as fleet_module
    import game.strategy.data.planet as planet_module

    monkeypatch.setattr(planet_module, "Planet", _PlanetStub)
    monkeypatch.setattr(fleet_module, "Fleet", _FleetStub)


# ---------------------------------------------------------------------------
# Frozenset categorization
# ---------------------------------------------------------------------------

class TestOrderTypeCategorization:
    """The three categorization frozensets."""

    def test_movement_and_action_are_disjoint(self):
        assert MOVEMENT_ORDER_TYPES.isdisjoint(ACTION_ORDER_TYPES)

    def test_planet_action_is_subset_of_action(self):
        assert PLANET_ACTION_ORDER_TYPES.issubset(ACTION_ORDER_TYPES)

    def test_movement_set_size(self):
        # MOVE, WARP, MOVE_TO_FLEET
        assert len(MOVEMENT_ORDER_TYPES) == 3

    def test_planet_action_set_contents(self):
        assert PLANET_ACTION_ORDER_TYPES == frozenset({
            OrderType.ACTIVATE_ABILITY,
            OrderType.DEACTIVATE_ABILITY,
        })


# ---------------------------------------------------------------------------
# to_dict matrix
# ---------------------------------------------------------------------------

class TestToDictMatrix:
    """The 10-branch dispatch ladder. See PROJ-335 design.md."""

    def test_transfer_order_emits_transfer_wrapper(self, patch_domain_classes):
        target = {"direction": "in", "amount": 10}
        data = Order(OrderType.TRANSFER, target).to_dict()

        assert data["target"] == {"type": "transfer", "value": target}
        assert data["type"] == "TRANSFER"

    def test_load_population_emits_transfer_wrapper(self, patch_domain_classes):
        target = {"amount": 5}
        data = Order(OrderType.LOAD_POPULATION, target).to_dict()

        assert data["target"] == {"type": "transfer", "value": target}

    def test_implode_planet_with_planet_emits_planet_ref(
        self, patch_domain_classes
    ):
        planet = _PlanetStub("p42")
        data = Order(OrderType.IMPLODE_PLANET, planet).to_dict()

        assert data["target"] == {"type": "planet_ref", "id": "p42"}

    def test_self_destruct_with_list_emits_ship_id_list(
        self, patch_domain_classes
    ):
        data = Order(OrderType.SELF_DESTRUCT, ["s1", "s2"]).to_dict()

        assert data["target"] == {
            "type": "ship_id_list",
            "value": ["s1", "s2"],
        }

    def test_open_warp_point_with_dict_emits_warp_params(
        self, patch_domain_classes
    ):
        params = {"q": 1, "r": 2}
        data = Order(OrderType.OPEN_WARP_POINT, params).to_dict()

        assert data["target"] == {"type": "warp_params", "value": params}

    def test_close_warp_point_with_dict_emits_warp_params(
        self, patch_domain_classes
    ):
        params = {"q": 0, "r": 0}
        data = Order(OrderType.CLOSE_WARP_POINT, params).to_dict()

        assert data["target"] == {"type": "warp_params", "value": params}

    def test_move_with_hex_coord_emits_q_r_without_type_key(
        self, patch_domain_classes
    ):
        """D-007: HexCoord branch is asymmetric — no 'type' key."""
        data = Order(OrderType.MOVE, HexCoord(1, 2)).to_dict()

        assert data["target"] == {"q": 1, "r": 2}
        assert "type" not in data["target"]

    def test_generic_planet_branch_emits_planet_ref(self, patch_domain_classes):
        """A non-IMPLODE order whose target is a Planet → planet_ref."""
        planet = _PlanetStub("p1")
        data = Order(OrderType.MOVE, planet).to_dict()

        assert data["target"] == {"type": "planet_ref", "id": "p1"}

    def test_generic_fleet_branch_emits_fleet_ref(self, patch_domain_classes):
        fleet = _FleetStub("f1")
        data = Order(OrderType.MOVE_TO_FLEET, fleet).to_dict()

        assert data["target"] == {"type": "fleet_ref", "id": "f1"}

    def test_colonize_with_dict_emits_colonize_params(
        self, patch_domain_classes
    ):
        planet = _PlanetStub("p7")
        target = {"planet": planet, "population": 100, "cargo": {"food": 5}}
        data = Order(OrderType.COLONIZE, target).to_dict()

        assert data["target"] == {
            "type": "colonize_params",
            "planet_id": "p7",
            "population": 100,
            "cargo": {"food": 5},
        }

    def test_catch_all_dict_branch_emits_dict_wrapper(
        self, patch_domain_classes
    ):
        """A MOVE order with arbitrary dict target falls through to the
        catch-all dict branch."""
        target = {"arbitrary": "dict"}
        data = Order(OrderType.MOVE, target).to_dict()

        assert data["target"] == {"type": "dict", "value": target}

    def test_else_branch_stringifies_unknown_target(self, patch_domain_classes):
        """Falls through to the else branch — stringifies via str()."""
        data = Order(OrderType.MOVE, 42).to_dict()

        assert data["target"] == {"type": "raw", "value": "42"}

    def test_target_none_emits_target_none(self, patch_domain_classes):
        data = Order(OrderType.MOVE, None).to_dict()

        assert data["target"] is None


class TestExecutionProgressSerialization:
    """``execution_progress`` is omitted when 0 (clean-saves invariant)."""

    def test_progress_zero_is_omitted(self, patch_domain_classes):
        data = Order(OrderType.MOVE, HexCoord(0, 0)).to_dict()

        assert "execution_progress" not in data

    def test_progress_positive_is_included(self, patch_domain_classes):
        order = Order(OrderType.MOVE, HexCoord(0, 0))
        order.execution_progress = 5

        data = order.to_dict()
        assert data["execution_progress"] == 5


# ---------------------------------------------------------------------------
# from_dict (simple path)
# ---------------------------------------------------------------------------

class TestFromDictSimplePath:
    """``from_dict`` round-trips only the catch-all dict wrapper."""

    def test_unwraps_dict_wrapped_target(self):
        payload = {
            "type": "COLONIZE",
            "target": {"type": "dict", "value": {"foo": "bar"}},
        }
        order = Order.from_dict(payload)

        assert order.type == OrderType.COLONIZE
        assert order.target == {"foo": "bar"}
        assert order.execution_progress == 0  # default when omitted

    def test_preserves_execution_progress(self):
        payload = {
            "type": "MOVE",
            "target": None,
            "execution_progress": 7,
        }
        order = Order.from_dict(payload)

        assert order.execution_progress == 7

    def test_does_not_resolve_hex_coord_branch(self):
        """D-007: HexCoord-emitted dict round-trips as a raw {q, r} dict,
        NOT as a HexCoord. Resolution requires OrderSerializer."""
        payload = {"type": "MOVE", "target": {"q": 1, "r": 2}}
        order = Order.from_dict(payload)

        # Pinned: target is the raw dict, not a HexCoord.
        assert order.target == {"q": 1, "r": 2}
        assert not isinstance(order.target, HexCoord)

    def test_from_dict_unknown_order_type_raises_keyerror(self):
        """MAJ-004 fix (review req_20260504_213455_95a42d): pin
        ``Order.from_dict`` raises ``KeyError`` for unknown OrderType
        names. ``OrderType[data['type']]`` at production line ~159
        is the raise site. Sister classes (SpeciesPopulation,
        PlanetaryFacility, Squadron) all pin equivalent
        missing-key/rejection behaviors; Order was the anomaly until
        this test landed.
        """
        payload = {"type": "NOT_A_REAL_ORDER_TYPE", "target": None}
        with pytest.raises(KeyError) as exc_info:
            Order.from_dict(payload)
        # The KeyError carries the unknown name (Python's enum lookup behavior).
        assert "NOT_A_REAL_ORDER_TYPE" in str(exc_info.value)


# ---------------------------------------------------------------------------
# __repr__
# ---------------------------------------------------------------------------

class TestRepr:
    """Two forms: with and without execution_progress."""

    def test_repr_without_progress(self):
        order = Order(OrderType.MOVE, "x")
        text = repr(order)

        assert text == "Order(MOVE, x)"

    def test_repr_with_progress(self):
        order = Order(OrderType.MOVE, "x")
        order.execution_progress = 3
        text = repr(order)

        assert text == "Order(MOVE, x, progress=3)"
