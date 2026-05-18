"""PROJ-437 Phase 3 substrate — container-driven row builder.

`TransferViewModel.build_row_data_from_containers(source_containers,
target_containers, *, filter_empty=False) -> list[dict]` produces the
row data by walking `Container.contents()` on both sides and
aggregating by `(kind, type_id)`.

Phase-3a scope (this substrate commit): the method ships additively
alongside the legacy `build_row_data(source_obj, target_obj)` DTO
path. The dialog still calls the DTO builder; the cutover that
switches the dialog over (and retires `all_pod_names` /
`_build_pod_rows`) lands in Phase 3b or as part of Phase 4's final
sweep — Phase 3a is risk-isolated substrate.

Row dict shape (unchanged + one additive field):

* ``cargo_key``: same string keys the legacy builder emits
  (``"<resource_id>"`` / ``"passengers_<species>"`` /
  ``"drop_pod:<design_id>"``). Vehicle vs. drop-pod prefix
  differentiation needs `ItemRef.state` to reach the snapshot —
  deferred until ContainerSnapshotInfo grows that channel (PROJ-436
  Phase 9 territory) or Phase 3b reaches into the live Container.
* ``display_name``: resource → `ResourceDefinition.name`; population
  → species_id; item → design_id.
* ``kind``: NEW additive field. ``ContainableKind`` member or
  ``None`` for backward compat with the legacy builder's dicts.
* ``source_amt`` / ``target_amt``: int (matches legacy builder).

Order: resources in catalog order, then population alphabetical,
then items alphabetical by ``cargo_key``.
"""
from __future__ import annotations

from typing import Tuple

import pytest

from game.core.resources import ResourceCatalog
from game.strategy.data.containable import ContainableKind
from game.strategy.data.container import ContainerEntry
from game.strategy.facade.dto import ContainerSnapshotInfo
from game.ui.screens.transfer_view_model import TransferViewModel

_CANONICAL_RESOURCE_IDS = ResourceCatalog.from_json().all_ids()


def _snap(
    *,
    container_id: str = "c",
    owner_kind: str = "fleet",
    owner_id: int = 1,
    label: str = "snap",
    capacity_mass: float = 100.0,
    mass_used: float = 0.0,
    allowed_kinds: frozenset[ContainableKind] | None = None,
    entries: Tuple[ContainerEntry, ...] = (),
) -> ContainerSnapshotInfo:
    return ContainerSnapshotInfo(
        container_id=container_id,
        owner_kind=owner_kind,
        owner_id=owner_id,
        label=label,
        capacity_mass=capacity_mass,
        mass_used=mass_used,
        allowed_kinds=allowed_kinds or frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.ITEM,
            ContainableKind.POPULATION,
        }),
        entries=entries,
    )


def _r(rid: str, qty: float) -> ContainerEntry:
    return ContainerEntry(
        kind=ContainableKind.RESOURCE,
        type_id=rid,
        quantity=qty,
        mass_total=qty,  # mass details immaterial here
    )


def _i(design_id: str, *, mass: float = 1.0) -> ContainerEntry:
    return ContainerEntry(
        kind=ContainableKind.ITEM,
        type_id=design_id,
        quantity=1.0,
        mass_total=mass,
    )


def _p(species: str, count: int) -> ContainerEntry:
    return ContainerEntry(
        kind=ContainableKind.POPULATION,
        type_id=species,
        quantity=float(count),
        mass_total=float(count) * 0.1,
    )


# ---------------------------------------------------------------------------
# Resource rows
# ---------------------------------------------------------------------------


class TestResourceRows:
    def test_resource_rows_emitted_in_catalog_order(self) -> None:
        # Source has metals + fuel; target has metals only. The new
        # builder emits the full canonical resource list (matches the
        # legacy `build_row_data` "always show all 8" UX) so the user
        # can see what's available to load even when empty.
        source = _snap(entries=(_r("metals", 10.0), _r("fuel", 5.0)))
        target = _snap(entries=(_r("metals", 3.0),))

        rows = TransferViewModel.build_row_data_from_containers(
            (source,), (target,),
        )

        resource_rows = [r for r in rows if r["kind"] is ContainableKind.RESOURCE]
        assert [r["cargo_key"] for r in resource_rows] == _CANONICAL_RESOURCE_IDS

        by_key = {r["cargo_key"]: r for r in resource_rows}
        assert by_key["metals"]["source_amt"] == 10
        assert by_key["metals"]["target_amt"] == 3
        assert by_key["fuel"]["source_amt"] == 5
        assert by_key["fuel"]["target_amt"] == 0
        # Other canonical resources unset on both sides.
        assert by_key["organics"]["source_amt"] == 0
        assert by_key["organics"]["target_amt"] == 0

    def test_resource_rows_aggregate_across_snapshots_on_each_side(self) -> None:
        snap_a = _snap(container_id="a", entries=(_r("metals", 10.0),))
        snap_b = _snap(container_id="b", entries=(_r("metals", 4.0),))

        rows = TransferViewModel.build_row_data_from_containers(
            (snap_a, snap_b), (),
        )

        (row,) = [r for r in rows if r["cargo_key"] == "metals"]
        assert row["source_amt"] == 14
        assert row["target_amt"] == 0

    def test_resource_display_name_from_catalog(self) -> None:
        source = _snap(entries=(_r("ammo", 5.0),))

        rows = TransferViewModel.build_row_data_from_containers(
            (source,), (),
        )

        (row,) = [r for r in rows if r["cargo_key"] == "ammo"]
        # Post-PROJ-436 Phase 7 the JSON `name` field is authoritative —
        # "Ammunition" (not the legacy "Ammo" hardcoded label).
        assert row["display_name"] == "Ammunition"


# ---------------------------------------------------------------------------
# Population rows
# ---------------------------------------------------------------------------


class TestPopulationRows:
    def test_population_rows_alpha_sorted_after_resources(self) -> None:
        source = _snap(entries=(_p("zeta", 7), _p("alpha", 3)))
        target = _snap(entries=())

        rows = TransferViewModel.build_row_data_from_containers(
            (source,), (target,),
        )

        pop_rows = [r for r in rows if r["kind"] is ContainableKind.POPULATION]
        assert [r["cargo_key"] for r in pop_rows] == [
            "passengers_alpha",
            "passengers_zeta",
        ]
        assert pop_rows[0]["display_name"] == "alpha"
        assert pop_rows[0]["source_amt"] == 3
        assert pop_rows[1]["source_amt"] == 7

    def test_population_aggregates_across_snapshots(self) -> None:
        snap_a = _snap(container_id="a", entries=(_p("alpha", 3),))
        snap_b = _snap(container_id="b", entries=(_p("alpha", 2),))

        rows = TransferViewModel.build_row_data_from_containers(
            (snap_a, snap_b), (),
        )

        (row,) = [r for r in rows if r["cargo_key"] == "passengers_alpha"]
        assert row["source_amt"] == 5


# ---------------------------------------------------------------------------
# Item rows
# ---------------------------------------------------------------------------


class TestItemRows:
    def test_item_rows_aggregate_by_design_id_and_use_drop_pod_prefix(self) -> None:
        source = _snap(entries=(_i("Marine Pod"), _i("Marine Pod"), _i("Scout Pod")))
        target = _snap(entries=(_i("Marine Pod"),))

        rows = TransferViewModel.build_row_data_from_containers(
            (source,), (target,),
        )

        item_rows = [r for r in rows if r["kind"] is ContainableKind.ITEM]
        assert [r["cargo_key"] for r in item_rows] == [
            "drop_pod:Marine Pod",
            "drop_pod:Scout Pod",
        ]
        marine = next(r for r in item_rows if r["cargo_key"] == "drop_pod:Marine Pod")
        assert marine["source_amt"] == 2
        assert marine["target_amt"] == 1
        assert marine["display_name"] == "Marine Pod"


# ---------------------------------------------------------------------------
# Order: resources → population → items
# ---------------------------------------------------------------------------


def test_overall_row_order_resources_then_population_then_items() -> None:
    source = _snap(entries=(
        _r("metals", 1.0),
        _i("Pod A"),
        _p("alpha", 1),
    ))

    rows = TransferViewModel.build_row_data_from_containers((source,), ())

    kinds_in_order = [r["kind"] for r in rows]
    # Drop the leading resource rows (canonical-order padding may be
    # there too) — focus on the relative ordering of kinds we emit.
    seen_kinds: list[ContainableKind] = []
    for k in kinds_in_order:
        if not seen_kinds or seen_kinds[-1] is not k:
            seen_kinds.append(k)
    assert seen_kinds == [
        ContainableKind.RESOURCE,
        ContainableKind.POPULATION,
        ContainableKind.ITEM,
    ]


# ---------------------------------------------------------------------------
# Filter-empty pass-through
# ---------------------------------------------------------------------------


def test_filter_empty_drops_zero_zero_rows() -> None:
    # Source has only metals; target has only fuel.
    # Resources catalog has all 8 resource ids; the rest are 0/0.
    source = _snap(entries=(_r("metals", 1.0),))
    target = _snap(entries=(_r("fuel", 1.0),))

    rows_all = TransferViewModel.build_row_data_from_containers(
        (source,), (target,), filter_empty=False,
    )
    rows_filtered = TransferViewModel.build_row_data_from_containers(
        (source,), (target,), filter_empty=True,
    )

    # filter_empty=False produces N rows; filter_empty=True keeps only
    # the rows where either side is non-zero.
    visible_keys = {r["cargo_key"] for r in rows_filtered}
    assert visible_keys == {"metals", "fuel"}
    assert len(rows_filtered) < len(rows_all)


# ---------------------------------------------------------------------------
# Empty sides
# ---------------------------------------------------------------------------


def test_empty_both_sides_returns_canonical_resource_rows_all_zero() -> None:
    """No entries anywhere — the canonical resource set still appears
    so the user can see what's available to load. Population and item
    rows omitted (no data → no rows)."""
    rows = TransferViewModel.build_row_data_from_containers((), ())

    resource_rows = [r for r in rows if r["kind"] is ContainableKind.RESOURCE]
    assert {r["cargo_key"] for r in resource_rows} == set(_CANONICAL_RESOURCE_IDS)
    assert all(r["source_amt"] == 0 and r["target_amt"] == 0 for r in resource_rows)

    assert not [r for r in rows if r["kind"] is ContainableKind.POPULATION]
    assert not [r for r in rows if r["kind"] is ContainableKind.ITEM]
