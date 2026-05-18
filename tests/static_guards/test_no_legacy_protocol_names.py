"""PROJ-436 Phase 6 protocol-surface ratchet.

Phase 6's audit (see ``Projects/active_projects/PROJ-436/decisions.md``
2026-05-18 rows) found that **no** protocol method needed deletion:

* ``IEmpire.resource_pool`` / ``IEmpire.max_storage`` continue to be
  satisfied by the post-Phase-5 ``Empire`` class — the durable
  ``_fleet_resource_pool`` was a concrete-class field, not a
  protocol member, and the surviving ``resource_pool`` is now a pure
  colony aggregation.
* ``IShipInstance.cargo_contents`` is still satisfied by the Phase 3f
  backward-compat ``@property`` over the renamed private dict.
* ``IStockpileHolder`` / ``IStagingYardHolder`` are still satisfied by
  the post-Phase-4 ``Planet`` ``@property``-over-private-field
  implementation; production callers route through ``IPlanetMutator``
  rather than narrowing through these protocols.
* ``IFacility.consumable_levels`` is still satisfied per the Phase 0
  D1 default (facility-internal state, no Container fold-in).

The Phase 5 deletion guard at
``tests/static_guards/test_no_legacy_storage_fields.py`` already pins
absence of the deleted **concrete-class** members
(``Empire._fleet_resource_pool``, the deleted dataclass fields on
``Planet`` / ``ShipInstance``). This module is the **protocol-surface**
ratchet:

* **Positive ratchets** — assert that the surviving protocol members
  stay present on their protocols, so an accidental edit in Phase
  8/10 doesn't drop them silently.
* **Negative ratchets** — assert that the mutator-style methods that
  were deleted from the concrete ``Empire`` class
  (``add_resources`` / ``consume_resources``) never appear on
  ``IEmpire``, and that ``_fleet_resource_pool`` never appears as a
  protocol member.
* **Set-shape ratchets** — assert that the member sets of
  ``IStockpileHolder`` and ``IStagingYardHolder`` are unchanged from
  the post-Phase-4 contract. The Phase 6 brief explicitly offered
  the "leave as-is" option (iii); this test pins that choice.

These tests are explicit ratchets preventing reintroduction or
silent removal of the post-Phase-5 protocol contract.

Model: ``tests/static_guards/test_no_legacy_storage_fields.py``
(PROJ-436 Phase 3/4/5 concrete-class deletion guards).
"""
from __future__ import annotations

from game.core.protocols.strategy_domain import (
    IEmpire,
    IFacility,
    IShipInstance,
)
from game.strategy.data.galaxy_protocols import (
    IStagingYardHolder,
    IStockpileHolder,
)


# ---------------------------------------------------------------------------
# Positive ratchets — surviving members must stay present
# ---------------------------------------------------------------------------


def test_iempire_still_declares_resource_pool() -> None:
    """``IEmpire`` MUST continue to declare ``resource_pool``.

    PROJ-436 Phase 6 positive ratchet. Phase 5 left the protocol
    member intact; the docstring was refreshed to describe the new
    colony-aggregation contract. If a future edit accidentally drops
    the member, this guard fails and forces a deliberate decision.
    """
    members = set(dir(IEmpire))
    assert "resource_pool" in members, (
        "IEmpire.resource_pool was removed from the protocol — "
        "PROJ-436 Phase 6 audit explicitly kept this member. "
        "Removing it requires a new design decision logged in "
        "Projects/active_projects/PROJ-436/decisions.md."
    )


def test_iempire_still_declares_max_storage() -> None:
    """``IEmpire`` MUST continue to declare ``max_storage``.

    PROJ-436 Phase 6 positive ratchet. Set by
    ``EmpireWriteService.replace_max_storage`` via
    ``HarvestingEngine``; read by UI panels. The Phase 6 audit kept
    this member intact.
    """
    members = set(dir(IEmpire))
    assert "max_storage" in members, (
        "IEmpire.max_storage was removed from the protocol — "
        "PROJ-436 Phase 6 audit explicitly kept this member. "
        "Removing it requires a new design decision logged in "
        "Projects/active_projects/PROJ-436/decisions.md."
    )


def test_iship_instance_still_declares_cargo_contents() -> None:
    """``IShipInstance`` MUST continue to declare ``cargo_contents``.

    PROJ-436 Phase 6 positive ratchet. Phase 3f deleted the dataclass
    field; the backward-compat ``@property`` over the renamed private
    dict still satisfies the protocol. Production writers route
    through ``ship._cargo_mgr`` (the manager API landed in Phase 3b)
    but the protocol describes the read surface.
    """
    members = set(dir(IShipInstance))
    assert "cargo_contents" in members, (
        "IShipInstance.cargo_contents was removed from the "
        "protocol — PROJ-436 Phase 6 audit kept this member as a "
        "read-surface declaration. Production writes go through "
        "ship._cargo_mgr; the property is the canonical read path."
    )


def test_ifacility_still_declares_consumable_levels() -> None:
    """``IFacility`` MUST continue to declare ``consumable_levels``.

    PROJ-436 Phase 0 D1 default: ``PlanetaryFacility.consumable_levels``
    stays as facility-internal state (no Container fold-in). The
    Phase 6 audit confirmed this remains the right call.
    """
    members = set(dir(IFacility))
    assert "consumable_levels" in members, (
        "IFacility.consumable_levels was removed from the protocol "
        "— PROJ-436 Phase 0 D1 default keeps PlanetaryFacility "
        "consumables as facility-internal state. Removing this "
        "member requires revisiting D1."
    )


# ---------------------------------------------------------------------------
# Negative ratchets — deleted Empire concrete-class methods MUST NOT creep
# onto the protocol surface
# ---------------------------------------------------------------------------


def test_iempire_does_not_declare_add_resources() -> None:
    """``IEmpire`` MUST NOT declare ``add_resources``.

    PROJ-436 Phase 5 deleted ``Empire.add_resources`` from the
    concrete class (zero production callers). The Phase 6 audit
    confirmed this method was never on the protocol surface — pin
    that it never accidentally appears.
    """
    members = set(dir(IEmpire))
    assert "add_resources" not in members, (
        "IEmpire.add_resources appeared on the protocol — "
        "PROJ-436 Phase 5 deleted Empire.add_resources from the "
        "concrete class. Resource mutation belongs to "
        "IPlanetMutator (per-colony) not IEmpire (empire is a "
        "pure aggregate of its colonies after Phase 5)."
    )


def test_iempire_does_not_declare_consume_resources() -> None:
    """``IEmpire`` MUST NOT declare ``consume_resources``.

    PROJ-436 Phase 5 deleted ``Empire.consume_resources``. Pin
    protocol-surface absence at the same time as the concrete-class
    deletion guard.
    """
    members = set(dir(IEmpire))
    assert "consume_resources" not in members, (
        "IEmpire.consume_resources appeared on the protocol — "
        "PROJ-436 Phase 5 deleted Empire.consume_resources from "
        "the concrete class. Resource mutation belongs to "
        "IPlanetMutator, not IEmpire."
    )


def test_iempire_does_not_declare_fleet_resource_pool() -> None:
    """``IEmpire`` MUST NOT declare ``_fleet_resource_pool`` /
    ``fleet_resource_pool``.

    PROJ-436 Phase 5 deleted ``Empire._fleet_resource_pool``. The
    durable fleet-side pool is gone; ``resource_pool`` walks
    ``self.colonies`` only. This guard pins the protocol surface
    against the same regression.
    """
    members = set(dir(IEmpire))
    assert "_fleet_resource_pool" not in members, (
        "IEmpire._fleet_resource_pool appeared on the protocol — "
        "PROJ-436 Phase 5 deleted this concrete-class field; "
        "fleet construction draws from the build-location's "
        "container, not an empire-level pool."
    )
    assert "fleet_resource_pool" not in members, (
        "IEmpire.fleet_resource_pool appeared on the protocol — "
        "PROJ-436 Phase 5 deleted the empire-level fleet pool."
    )


# ---------------------------------------------------------------------------
# Set-shape ratchets — IStockpileHolder / IStagingYardHolder member sets
# ---------------------------------------------------------------------------


# The post-Phase-4 contract for these two protocols. The Phase 6 brief
# explicitly offered "(iii) leave as-is if the post-Phase-4 implementations
# on Planet already satisfy them transparently" — the audit chose (iii).
# These constants pin that choice.

EXPECTED_ISTOCKPILE_HOLDER_MEMBERS = frozenset(
    {
        "add_to_stockpile",
        "consume_from_stockpile",
        "has_stockpile",
        "get_stockpile",
    }
)

EXPECTED_ISTAGING_YARD_HOLDER_MEMBERS = frozenset(
    {
        "get_staging_mass",
        "add_to_staging_yard",
        "remove_from_staging_yard",
        "max_staging_mass",
    }
)


def _protocol_members(proto: type) -> frozenset[str]:
    """Return the protocol-declared public member names."""
    return frozenset(
        name
        for name in dir(proto)
        if not name.startswith("_")
    )


def test_istockpile_holder_member_set_unchanged() -> None:
    """``IStockpileHolder`` public members MUST match the post-Phase-4
    contract.

    PROJ-436 Phase 6 set-shape ratchet. The phase brief offered
    three options for these protocols — the audit chose option
    (iii) "leave as-is." If a future edit adds or removes a member,
    this guard fails and forces an explicit decision.
    """
    actual = _protocol_members(IStockpileHolder)
    assert actual == EXPECTED_ISTOCKPILE_HOLDER_MEMBERS, (
        f"IStockpileHolder member set drifted from the Phase 6 "
        f"contract. Expected: {sorted(EXPECTED_ISTOCKPILE_HOLDER_MEMBERS)}. "
        f"Got: {sorted(actual)}. If this is intentional, update "
        f"Projects/active_projects/PROJ-436/decisions.md."
    )


def test_istaging_yard_holder_member_set_unchanged() -> None:
    """``IStagingYardHolder`` public members MUST match the post-Phase-4
    contract.

    Same rationale as the IStockpileHolder ratchet.
    """
    actual = _protocol_members(IStagingYardHolder)
    assert actual == EXPECTED_ISTAGING_YARD_HOLDER_MEMBERS, (
        f"IStagingYardHolder member set drifted from the Phase 6 "
        f"contract. Expected: {sorted(EXPECTED_ISTAGING_YARD_HOLDER_MEMBERS)}. "
        f"Got: {sorted(actual)}. If this is intentional, update "
        f"Projects/active_projects/PROJ-436/decisions.md."
    )
