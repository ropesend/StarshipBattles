"""PROJ-438 Phase 4: pin the post-PROJ-436 Planet/Fleet/Empire contract.

The Phase 4 audit (see decisions.md row dated 2026-05-18) confirmed that
PROJ-436 has already absorbed every bounded-scope cleanup target:

- **Planet** — ``stockpile``, ``max_stockpile``, ``staging_yard``
  dataclass fields deleted in PROJ-436 Phase 4f; backward-compat
  properties over private fields are in place. 47 declared fields are
  intentionally preserved per PROJ-372 Risk R1 (save-format compat).
- **Empire** — ``_fleet_resource_pool`` durable storage deleted in
  PROJ-436 Phase 5; ``resource_pool`` is now a pure aggregation query.
- **galaxy_protocols.py** — both ``IStockpileHolder`` and
  ``IStagingYardHolder`` were explicitly kept as-is by PROJ-436 Phase 6
  audit (writers go through ``IPlanetMutator``); shape is pinned by
  ``tests/static_guards/test_no_legacy_protocol_names.py``.

Phase 4 therefore produces no production code change. This file
ratchets the post-PROJ-436 contract so any future regression that
re-introduces the legacy durable fields (or removes the backward-compat
properties) surfaces immediately as a Phase 4-named failure.
"""
from __future__ import annotations

from game.strategy.data.empire import Empire
from game.strategy.data.planet import Planet


class TestPlanetPostPROJ436Contract:
    """Pin the post-PROJ-436 Phase 4f shape of Planet."""

    def test_stockpile_is_property_not_dataclass_field(self) -> None:
        """Dataclass field deleted in PROJ-436 Phase 4f. ``stockpile`` is
        now a backward-compatible property over the renamed private
        ``_stockpile`` dict."""
        assert "stockpile" not in Planet.__dataclass_fields__, (
            "Planet.stockpile must not be a dataclass field (deleted in "
            "PROJ-436 Phase 4f)."
        )
        assert isinstance(Planet.__dict__.get("stockpile"), property), (
            "Planet.stockpile must remain a backward-compatible property."
        )

    def test_max_stockpile_is_property_not_dataclass_field(self) -> None:
        assert "max_stockpile" not in Planet.__dataclass_fields__
        assert isinstance(Planet.__dict__.get("max_stockpile"), property)

    def test_staging_yard_is_property_not_dataclass_field(self) -> None:
        assert "staging_yard" not in Planet.__dataclass_fields__
        assert isinstance(Planet.__dict__.get("staging_yard"), property)


class TestEmpirePostPROJ436Contract:
    """Pin the post-PROJ-436 Phase 5 shape of Empire."""

    def test_fleet_resource_pool_is_deleted(self) -> None:
        """PROJ-436 Phase 5 deleted ``Empire._fleet_resource_pool`` durable
        storage. The slot must not be set during ``__init__``."""
        # Construct a bare empire — should not initialise the legacy slot.
        empire = Empire(
            empire_id=99, name="Phase4Audit", color=(0, 0, 0),
        )
        assert not hasattr(empire, "_fleet_resource_pool"), (
            "Empire._fleet_resource_pool must not be reintroduced "
            "(PROJ-436 Phase 5 deletion)."
        )

    def test_resource_pool_is_property_aggregating_colony_stockpiles(self) -> None:
        """PROJ-436 Phase 5: ``resource_pool`` is now a pure aggregation
        property over ``self.colonies[*].stockpile``, not durable state."""
        assert isinstance(Empire.__dict__.get("resource_pool"), property), (
            "Empire.resource_pool must remain a read-only aggregation "
            "property (PROJ-436 Phase 5)."
        )
        empire = Empire(empire_id=100, name="EmptyEmpire", color=(0, 0, 0))
        # No colonies → empty pool.
        pool = empire.resource_pool
        assert isinstance(pool, dict)
        assert pool == {}, (
            "Empty empire must produce empty resource pool "
            "(no durable storage to leak across runs)."
        )


class TestPhase4ScopeCollapseRationale:
    """A one-test marker class documenting that Phase 4 produced no
    production code change. Acts as a discoverable pointer for future
    agents grepping for ``Phase 4`` to find the decisions.md row."""

    def test_phase_4_collapsed_per_decisions(self) -> None:
        """If this test is the only PROJ-438 Phase 4 ratchet you see in
        ship/empire/planet code review, that is by design. The Phase 4
        scope (Planet save-schema breadth / Fleet+Empire persistence-
        facing aggregate behavior / galaxy_protocols.py read contracts)
        was audited and confirmed already absorbed by PROJ-436 Phases 4–6.
        See ``Projects/active_projects/PROJ-438/decisions.md`` row dated
        2026-05-18 for the full rationale."""
        # Pure documentation marker; the assertion is trivial.
        assert True
