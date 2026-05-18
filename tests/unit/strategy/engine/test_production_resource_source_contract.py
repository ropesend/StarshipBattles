"""PROJ-445 Phase 2 (F-B-019 + DI-2026-05-18-007) — affordability /
consumption symmetry ratchet for ``IProductionResourceSource``
implementers.

The :meth:`IProductionResourceSource.production_consume_resource` Protocol
contract requires that any call returning ``True`` from
:meth:`production_has_resources` for ``{resource: amount}`` in the same
engine tick MUST be followed by a successful
``production_consume_resource(resource, amount) -> True``. Implementers
that perform rounding (integer-typed sources like ``Fleet``) MUST do so
symmetrically across both methods so the affordability precondition can
never disagree with the consumption commit.

Without this ratchet, the engine can read ``has_resources -> True``,
attempt to charge, and silently receive ``False`` from the implementer
— the failure mode behind DI-2026-05-18-006 / 007. This file pins the
contract on every concrete implementer in production
(``Planet``, ``Fleet``) so the next implementer added against the
Protocol cannot drift.
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.fleet import Fleet
from game.strategy.data.planet import Planet
from game.strategy.engine.production_engine import IProductionResourceSource


def _make_minimal_planet() -> Planet:
    """Smallest viable Planet for production-contract testing."""
    return Planet(
        name="P",
        location=HexCoord(0, 0),
        orbit_distance=1,
        mass=1.0,
        radius=1.0,
        surface_area=1.0,
        density=1.0,
        surface_gravity=1.0,
        surface_pressure=0.0,
        surface_temperature=300.0,
        surface_water=0.0,
        tectonic_activity=0.0,
        magnetic_field=0.0,
    )


def _make_empty_fleet() -> Fleet:
    return Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))


# ---------------------------------------------------------------------------
# Protocol-level structural check
# ---------------------------------------------------------------------------


def test_planet_satisfies_iproduction_resource_source_protocol() -> None:
    """Sanity guard: Planet still exposes the three Protocol methods."""
    assert isinstance(_make_minimal_planet(), IProductionResourceSource)


def test_fleet_satisfies_iproduction_resource_source_protocol() -> None:
    """Sanity guard: Fleet still exposes the three Protocol methods."""
    assert isinstance(_make_empty_fleet(), IProductionResourceSource)


# ---------------------------------------------------------------------------
# Affordability / consumption symmetry on Planet
# ---------------------------------------------------------------------------


def test_planet_has_implies_consume_for_whole_amount() -> None:
    """Planet uses float stockpile; ``consume`` is exact and trivially
    honors the contract for any (resource, amount) it can afford."""
    planet = _make_minimal_planet()
    planet._stockpile["metals"] = 10.0
    cost = {"metals": 3.0}

    assert planet.production_has_resources(cost) is True
    assert planet.production_consume_resource("metals", 3.0) is True


def test_planet_has_implies_consume_for_fractional_amount() -> None:
    """Float stockpile: a fractional charge still honors the contract."""
    planet = _make_minimal_planet()
    planet._stockpile["metals"] = 5.0
    cost = {"metals": 0.1}

    assert planet.production_has_resources(cost) is True
    assert planet.production_consume_resource("metals", 0.1) is True


def test_planet_missing_returns_false_symmetrically() -> None:
    """When the source can't afford the cost, both checks return False
    (the symmetric ``False -> False`` branch of the contract)."""
    planet = _make_minimal_planet()
    cost = {"metals": 1.0}

    assert planet.production_has_resources(cost) is False
    assert planet.production_consume_resource("metals", 1.0) is False


# ---------------------------------------------------------------------------
# Affordability / consumption symmetry on Fleet
# ---------------------------------------------------------------------------


def test_fleet_empty_returns_false_symmetrically() -> None:
    """Empty-fleet baseline: no cargo, so both methods agree on ``False``.

    PROJ-445 Phase 2 (F-B-019): paired with PROJ-444 F-A-010, which
    is the structural fix site for Fleet rounding. As of 2026-05-18
    Fleet routes both ``has`` and ``consume`` through identical
    ``total < amount`` comparisons (``has_cargo_resources`` and
    ``consume_cargo_resource`` in ``fleet.py``) so the symmetric
    False branch holds. If PROJ-444 F-A-010 changes the rounding
    policy, the SUFFICIENT path here may need a fleet-with-cargo
    fixture — that fixture is non-trivial (requires real ships +
    ``_resource_agg`` distribution) and is deferred to the joint
    PROJ-444 F-A-010 ship-rounding work.
    """
    fleet = _make_empty_fleet()
    cost = {"metals": 1.0}

    assert fleet.production_has_resources(cost) is False
    assert fleet.production_consume_resource("metals", 1.0) is False


# ---------------------------------------------------------------------------
# Cross-implementer contract sweep
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "source_factory,resource,amount,prep",
    [
        (_make_minimal_planet, "metals", 3.0,
         lambda s: s._stockpile.__setitem__("metals", 10.0)),
        (_make_minimal_planet, "metals", 0.5,
         lambda s: s._stockpile.__setitem__("metals", 1.0)),
    ],
)
def test_production_has_resources_implies_consume_succeeds(
    source_factory, resource, amount, prep
) -> None:
    """For each IProductionResourceSource implementer in production: if
    ``production_has_resources`` returns True for ``{resource: amount}``,
    then ``production_consume_resource(resource, amount)`` MUST return
    True. The Fleet implementer's fractional/rounding edge cases are
    deferred to PROJ-444 F-A-010's ship-rounding ratchet — this file
    locks the float-substrate Planet path now and the joint work picks
    up the integer-substrate Fleet path."""
    source = source_factory()
    prep(source)

    assert source.production_has_resources({resource: amount}) is True, (
        "Test prep failed to leave the source affordable."
    )
    assert source.production_consume_resource(resource, amount) is True, (
        f"{type(source).__name__}.production_consume_resource returned False "
        f"after production_has_resources({{{resource!r}: {amount}}}) returned "
        f"True — affordability/consumption contract violated."
    )
