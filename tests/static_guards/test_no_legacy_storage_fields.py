"""PROJ-436 Phase 3f + Phase 4f + Phase 5 deletion guard.

Locks in the final-state contract for the legacy storage-field
deletions:

* Phase 3f — :class:`ShipInstance` MUST NOT carry ``cargo_contents``
  / ``consumable_levels`` as dataclass fields.
* Phase 4f — :class:`Planet` MUST NOT carry ``stockpile`` /
  ``max_stockpile`` / ``staging_yard`` as dataclass fields.
* Phase 5  — :class:`Empire` MUST NOT carry ``_fleet_resource_pool``
  as an instance attribute. ``Empire.resource_pool`` is now a pure
  aggregation query that walks colony stockpiles only; the fleet-side
  durable storage was always a self-flagged TODO ("temporary storage
  for fleet construction") and is gone.

For ShipInstance / Planet the public attribute names survive as
backward-compatible ``@property`` accessors over renamed private
dataclass fields. Production callers route through stable manager
APIs (the cargo / consumable manager surfaces for ShipInstance, and
``IPlanetMutator`` / the Planet stockpile-helper methods for Planet).

For Empire the durable field is fully deleted — there is no
``_fleet_resource_pool`` (private or public). ``Empire`` is a regular
class rather than a dataclass, so the guard checks the instance
``__dict__`` (``vars(empire)``) of a freshly-constructed instance.

These tests are explicit ratchets preventing reintroduction of any
of the six seams.

Model: ``tests/unit/strategy/data/test_phase_1f_deletion_guard.py``
(PROJ-431 Phase 1f deletion guard for ``carried_items``).
"""
from __future__ import annotations

from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet
from game.strategy.data.ship_instance import ShipInstance


def test_ship_instance_has_no_cargo_contents_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``cargo_contents`` as a dataclass field.

    PROJ-436 Phase 3f deletion guard. Production callers route through
    ``ship._cargo_mgr.set_cargo`` / ``get_all_cargo`` / ``total_cargo_units``
    / ``has_cargo`` (the stable manager API landed in Phase 3b). A
    backward-compatible ``cargo_contents`` property over the cargo
    manager's storage is permitted as a test-fixture compatibility
    shim — the dataclass field is gone.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "cargo_contents" not in fields, (
        f"ShipInstance still has a `cargo_contents` dataclass field "
        f"(PROJ-436 Phase 3f deletion guard). The stable cargo-manager "
        f"API is the canonical access path. Found fields: "
        f"{sorted(fields.keys())}"
    )


def test_ship_instance_has_no_consumable_levels_dataclass_field() -> None:
    """``ShipInstance`` must NOT declare ``consumable_levels`` as a dataclass field.

    PROJ-436 Phase 3f deletion guard. Production callers route through
    ``ship._resource_mgr.set_level`` / ``get_all_levels`` /
    ``get_current_resource`` / ``replace_levels`` (the stable manager
    API landed in Phase 3b). A backward-compatible
    ``consumable_levels`` property over the consumable manager's
    storage is permitted as a test-fixture compatibility shim — the
    dataclass field is gone.
    """
    fields = getattr(ShipInstance, "__dataclass_fields__", {})
    assert "consumable_levels" not in fields, (
        f"ShipInstance still has a `consumable_levels` dataclass field "
        f"(PROJ-436 Phase 3f deletion guard). The stable consumable-"
        f"manager API is the canonical access path. Found fields: "
        f"{sorted(fields.keys())}"
    )


def test_planet_has_no_stockpile_dataclass_field() -> None:
    """``Planet`` must NOT declare ``stockpile`` as a dataclass field.

    PROJ-436 Phase 4f deletion guard. Production writers route through
    ``IPlanetMutator.set_stockpile_amount`` / ``set_max_stockpile`` or
    Planet's own ``add_to_stockpile`` / ``consume_from_stockpile``
    helpers, which write to the private ``_stockpile`` field. A
    backward-compatible ``stockpile`` ``@property`` over the private
    dict is permitted as the read / mutate surface for test fixtures
    and read-only callers — the dataclass field is gone.
    """
    fields = getattr(Planet, "__dataclass_fields__", {})
    assert "stockpile" not in fields, (
        f"Planet still has a `stockpile` dataclass field "
        f"(PROJ-436 Phase 4f deletion guard). The stable Planet "
        f"stockpile-helper / IPlanetMutator API is the canonical "
        f"write path. Found fields: {sorted(fields.keys())}"
    )


def test_planet_has_no_max_stockpile_dataclass_field() -> None:
    """``Planet`` must NOT declare ``max_stockpile`` as a dataclass field.

    PROJ-436 Phase 4f deletion guard. Production writers route through
    ``IPlanetMutator.set_max_stockpile``. A backward-compatible
    ``max_stockpile`` ``@property`` over the private ``_max_stockpile``
    dict is permitted — the dataclass field is gone.
    """
    fields = getattr(Planet, "__dataclass_fields__", {})
    assert "max_stockpile" not in fields, (
        f"Planet still has a `max_stockpile` dataclass field "
        f"(PROJ-436 Phase 4f deletion guard). The stable Planet "
        f"stockpile-helper / IPlanetMutator API is the canonical "
        f"write path. Found fields: {sorted(fields.keys())}"
    )


def test_planet_has_no_staging_yard_dataclass_field() -> None:
    """``Planet`` must NOT declare ``staging_yard`` as a dataclass field.

    PROJ-436 Phase 4f deletion guard. Production writers route through
    ``IPlanetMutator.add_staging_item`` / ``pop_staging_item`` or
    Planet's own ``add_to_staging_yard`` / ``remove_from_staging_yard``
    helpers, which append / pop the private ``_staging_yard`` list. A
    backward-compatible ``staging_yard`` ``@property`` over the
    private list is permitted — the dataclass field is gone.
    """
    fields = getattr(Planet, "__dataclass_fields__", {})
    assert "staging_yard" not in fields, (
        f"Planet still has a `staging_yard` dataclass field "
        f"(PROJ-436 Phase 4f deletion guard). The stable Planet "
        f"staging-helper / IPlanetMutator API is the canonical "
        f"write path. Found fields: {sorted(fields.keys())}"
    )


def _fresh_empire() -> Empire:
    """Construct an Empire with no callers — used by the Phase 5 guard."""
    return Empire(empire_id=1, name="Guard", color=(0, 0, 0))


def test_empire_has_no_fleet_resource_pool_attribute() -> None:
    """``Empire`` must NOT carry ``_fleet_resource_pool`` on a fresh instance.

    PROJ-436 Phase 5 deletion guard. The empire's fleet-side resource
    pool was always a self-flagged TODO ("temporary storage for fleet
    construction") and is fully deleted in Phase 5 — fleet
    construction resources draw from the build-location's container
    (``Planet.stockpile`` for planet construction, fleet cargo for
    fleet construction). ``Empire.resource_pool`` is now a pure
    aggregation query that walks ``self.colonies`` only; there is no
    fleet-side durable summand.

    Empire is a regular class (not a dataclass), so the guard checks
    the instance ``__dict__`` of a freshly-constructed Empire.
    """
    empire = _fresh_empire()
    instance_attrs = sorted(vars(empire).keys())
    assert "_fleet_resource_pool" not in vars(empire), (
        f"Empire still initialises `_fleet_resource_pool` on a fresh "
        f"instance (PROJ-436 Phase 5 deletion guard). The fleet-side "
        f"durable pool is gone; `resource_pool` is a pure aggregation "
        f"of `self.colonies[*].stockpile`. Found instance attrs: "
        f"{instance_attrs}"
    )


def test_empire_resource_pool_is_pure_aggregation_with_no_colonies() -> None:
    """A freshly-constructed empire with no colonies has an empty resource_pool.

    PROJ-436 Phase 5 deletion guard. Before Phase 5 a freshly-
    constructed empire could carry resources via ``_fleet_resource_pool``;
    after Phase 5, ``resource_pool`` is a pure aggregation over
    ``self.colonies[*].stockpile`` and is empty for an empire with no
    colonies. This pins the new contract from the read-side.
    """
    empire = _fresh_empire()
    assert empire.resource_pool == {}, (
        "Empire.resource_pool should aggregate colony stockpiles only; "
        "an empire with no colonies must return an empty dict. Got: "
        f"{empire.resource_pool}"
    )
