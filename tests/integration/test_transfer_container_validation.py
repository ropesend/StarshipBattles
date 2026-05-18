"""PROJ-436 Phase 7 integration tests.

End-to-end gates for the registry-driven cargo-type validation
contract that replaces the deleted ``TransferValidator.VALID_CARGO_TYPES``
hardcoded whitelist.

Pins:

* Every resource ID in ``data/resources.json`` is accepted as a valid
  cargo type without any validator update — this is the whole point
  of moving the whitelist behind ``ResourceCatalog``.
* The three categorical sentinels (``"passengers"`` / ``"drop_pod"`` /
  ``"vehicle"``) are accepted as before.
* Unknown cargo types are rejected with ``INVALID_CARGO_TYPE``.
* The :class:`Container.accepts` substrate composes correctly with the
  resource catalog: a container with a resource-kind policy accepts a
  ``ResourceContainable`` for any catalog-known resource_id.

These tests run in the canonical sharded suite (no
``tests/unit/strategy/data/`` ``norecursedirs`` hiding).
"""
from __future__ import annotations

import pytest

from game.core.hex_math import HexCoord
from game.core.resources import ResourceCatalog
from game.strategy.data.container import Container, ContainerPolicy
from game.strategy.data.containable import ContainableKind, ResourceContainable
from game.strategy.data.fleet import Fleet
from game.strategy.validation.transfer_validator import TransferValidator


@pytest.fixture(scope="module")
def catalog() -> ResourceCatalog:
    """Resolve the canonical ResourceCatalog once per module."""
    return ResourceCatalog.from_json()


class TestRegistryDrivenCargoTypeValidation:
    """The cargo-type gate consults ``ResourceCatalog`` + sentinels."""

    def test_every_catalog_resource_is_an_accepted_cargo_type(
        self, catalog: ResourceCatalog
    ) -> None:
        """Each resource declared in ``data/resources.json`` is a
        valid cargo type — no whitelist update needed when a new
        resource lands in the JSON.
        """
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        for resource_id in catalog.all_ids():
            result = TransferValidator.validate(
                galaxy=None,
                fleet=fleet,
                target=fleet,
                cargo_type=resource_id,
                direction="load",
                amount=1,
                skip_location_check=True,
            )
            assert result.error_code != "INVALID_CARGO_TYPE", (
                f"Resource {resource_id!r} from data/resources.json "
                f"was rejected by TransferValidator (PROJ-436 Phase 7 "
                f"regression)"
            )

    @pytest.mark.parametrize(
        "sentinel", ["passengers", "drop_pod", "vehicle"],
    )
    def test_categorical_sentinels_accepted(self, sentinel: str) -> None:
        """``passengers`` / ``drop_pod`` / ``vehicle`` are the three
        non-resource categorical cargo types and remain accepted.
        """
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        result = TransferValidator.validate(
            galaxy=None,
            fleet=fleet,
            target=fleet,
            cargo_type=sentinel,
            direction="load",
            amount=1,
            skip_location_check=True,
        )
        assert result.error_code != "INVALID_CARGO_TYPE"

    @pytest.mark.parametrize(
        "bogus", ["dilithium", "antimatter", "not_a_real_cargo", ""],
    )
    def test_unknown_cargo_type_rejected(self, bogus: str) -> None:
        """Unknown cargo types fall through both the resource catalog
        and the sentinel set, yielding ``INVALID_CARGO_TYPE``.
        """
        fleet = Fleet(fleet_id=1, owner_id=0, location=HexCoord(0, 0))
        result = TransferValidator.validate(
            galaxy=None,
            fleet=fleet,
            target=fleet,
            cargo_type=bogus,
            direction="load",
            amount=1,
            skip_location_check=True,
        )
        assert not result.is_valid
        assert result.error_code == "INVALID_CARGO_TYPE"


class TestContainerAcceptsResourceCatalogIntegration:
    """The ``Container.accepts`` substrate composes with the catalog.

    A container policy that admits resources accepts any catalog-known
    ``ResourceContainable``. This pins the link between the Phase 0
    Container substrate and the Phase 7 validation contract.
    """

    def test_resource_container_accepts_every_catalog_resource(
        self, catalog: ResourceCatalog
    ) -> None:
        container = Container(
            capacity_mass=1_000_000.0,
            policy=ContainerPolicy(
                allowed_kinds=frozenset({ContainableKind.RESOURCE})
            ),
        )
        for resource_id in catalog.all_ids():
            assert container.accepts(
                ResourceContainable(resource_id=resource_id)
            ), (
                f"Container.accepts rejected catalog-known resource "
                f"{resource_id!r} (PROJ-436 Phase 7 integration gap)"
            )

    def test_resource_container_with_allowlist_filters_by_type_id(self) -> None:
        """``ContainerPolicy.allowed_type_ids`` filters to a specific
        resource set — used by per-resource specialty components
        (e.g. ``metals_silo`` with ``allowed_type_ids={"metals"}``).
        """
        container = Container(
            capacity_mass=100_000.0,
            policy=ContainerPolicy(
                allowed_kinds=frozenset({ContainableKind.RESOURCE}),
                allowed_type_ids=frozenset({"metals"}),
            ),
        )
        assert container.accepts(ResourceContainable(resource_id="metals"))
        assert not container.accepts(ResourceContainable(resource_id="fuel"))
