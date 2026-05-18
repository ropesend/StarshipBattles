"""PROJ-437 Phase 2: mass-remaining preview math.

Locks `TransferViewModel.compute_mass_preview(source_containers,
target_containers, pending_transfers) -> MassPreview` — the pure-
Python read surface the dialog refreshes after every pending mutation
(per OD3 (a) per-input granularity).

Phase 2 covers resources + population. ITEM-kind cargo keys
(``drop_pod:<name>``, ``vehicle:<name>``) are intentionally treated as
mass-neutral until Phase 3 mixed-content folds them in.
"""
from __future__ import annotations

from typing import Tuple

import pytest

from game.strategy.data.containable import ContainableKind
from game.strategy.data.container import ContainerEntry
from game.strategy.facade.dto import ContainerSnapshotInfo
from game.ui.screens.transfer_view_model import (
    MassPreview,
    TransferViewModel,
)


# ---------------------------------------------------------------------------
# Snapshot helpers
# ---------------------------------------------------------------------------


def _resource_snap(
    *,
    label: str = "snap",
    capacity_mass: float = 100.0,
    mass_used: float = 0.0,
    entries: Tuple[ContainerEntry, ...] = (),
    owner_kind: str = "fleet",
    owner_id: int = 1,
    container_id: str = "c",
) -> ContainerSnapshotInfo:
    return ContainerSnapshotInfo(
        container_id=container_id,
        owner_kind=owner_kind,
        owner_id=owner_id,
        label=label,
        capacity_mass=capacity_mass,
        mass_used=mass_used,
        allowed_kinds=frozenset({
            ContainableKind.RESOURCE,
            ContainableKind.POPULATION,
        }),
        entries=entries,
    )


def _resource_entry(rid: str, qty: float, mass_per_unit: float) -> ContainerEntry:
    return ContainerEntry(
        kind=ContainableKind.RESOURCE,
        type_id=rid,
        quantity=qty,
        mass_total=qty * mass_per_unit,
    )


def _population_entry(species: str, count: int, mass_per_unit: float = 0.1) -> ContainerEntry:
    return ContainerEntry(
        kind=ContainableKind.POPULATION,
        type_id=species,
        quantity=float(count),
        mass_total=float(count) * mass_per_unit,
    )


# ---------------------------------------------------------------------------
# Empty / no-op cases
# ---------------------------------------------------------------------------


class TestComputeMassPreviewBaseCases:
    def test_empty_containers_and_pending_returns_zero_remaining(self) -> None:
        preview = TransferViewModel.compute_mass_preview((), (), {})

        assert preview.source_mass_remaining_after == 0.0
        assert preview.target_mass_remaining_after == 0.0
        assert preview.target_over_capacity is False

    def test_empty_pending_returns_current_state(self) -> None:
        source = _resource_snap(
            capacity_mass=200.0,
            mass_used=50.0,
            entries=(_resource_entry("metals", 50.0, 1.0),),
        )
        target = _resource_snap(
            capacity_mass=300.0,
            mass_used=20.0,
            entries=(_resource_entry("metals", 20.0, 1.0),),
        )

        preview = TransferViewModel.compute_mass_preview((source,), (target,), {})

        assert preview.source_mass_remaining_after == pytest.approx(150.0)
        assert preview.target_mass_remaining_after == pytest.approx(280.0)
        assert preview.source_capacity_mass == pytest.approx(200.0)
        assert preview.target_capacity_mass == pytest.approx(300.0)


# ---------------------------------------------------------------------------
# Resource pending math
# ---------------------------------------------------------------------------


class TestResourcePendingMath:
    def test_positive_pending_moves_mass_target_to_source(self) -> None:
        """LOAD arrow click ('>0') flows mass target → source."""
        # Use a resource with mass_per_unit = 1.0 so the math is clear.
        # Use 'metals' which has mass_per_unit=0.01 per data/resources.json
        # — adjust expected values accordingly.
        source = _resource_snap(capacity_mass=100.0, mass_used=0.0)
        target = _resource_snap(
            capacity_mass=100.0,
            mass_used=1.0,  # 100 metals * 0.01 = 1 ton
            entries=(_resource_entry("metals", 100.0, 0.01),),
        )

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"metals": 50},
        )

        # 50 metals * 0.01 = 0.5 tons. Source gains 0.5; target loses 0.5.
        assert preview.source_mass_remaining_after == pytest.approx(99.5)
        assert preview.target_mass_remaining_after == pytest.approx(99.5)

    def test_negative_pending_moves_mass_source_to_target(self) -> None:
        """DROP arrow click ('<0') flows mass source → target."""
        source = _resource_snap(
            capacity_mass=100.0,
            mass_used=1.0,
            entries=(_resource_entry("metals", 100.0, 0.01),),
        )
        target = _resource_snap(capacity_mass=100.0, mass_used=0.0)

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"metals": -40},
        )

        # 40 metals * 0.01 = 0.4 tons. Source loses 0.4; target gains 0.4.
        assert preview.source_mass_remaining_after == pytest.approx(99.4)
        assert preview.target_mass_remaining_after == pytest.approx(99.6)

    def test_unknown_resource_key_treated_as_zero_mass(self) -> None:
        """Unknown cargo keys are mass-neutral — the preview stays
        usable even if the catalog drifts; Phase 5 consult catches
        legitimately bad keys."""
        source = _resource_snap(capacity_mass=10.0, mass_used=0.0)
        target = _resource_snap(capacity_mass=10.0, mass_used=0.0)

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"unknown_made_up_resource": 100},
        )

        assert preview.source_mass_remaining_after == pytest.approx(10.0)
        assert preview.target_mass_remaining_after == pytest.approx(10.0)


# ---------------------------------------------------------------------------
# Population pending math
# ---------------------------------------------------------------------------


class TestPopulationPendingMath:
    def test_passengers_species_keys_use_default_mass_per_unit(self) -> None:
        """``passengers_<species>`` keys use 0.1 tons/individual."""
        source = _resource_snap(capacity_mass=50.0, mass_used=0.0)
        target = _resource_snap(
            capacity_mass=50.0,
            mass_used=1.0,
            entries=(_population_entry("alpha", 10),),
        )

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"passengers_alpha": 5},
        )

        # 5 individuals * 0.1 ton = 0.5 tons.
        assert preview.source_mass_remaining_after == pytest.approx(49.5)
        assert preview.target_mass_remaining_after == pytest.approx(49.5)

    def test_bare_passengers_key_uses_default_mass(self) -> None:
        """Legacy fleet-side ``passengers`` aggregate uses the same
        default mass."""
        source = _resource_snap(capacity_mass=50.0, mass_used=0.0)
        target = _resource_snap(capacity_mass=50.0, mass_used=1.0)

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"passengers": 3},
        )

        assert preview.source_mass_remaining_after == pytest.approx(49.7)


# ---------------------------------------------------------------------------
# MAX sentinels
# ---------------------------------------------------------------------------


class TestMaxSentinelResolution:
    def test_max_load_resolves_to_target_current_amount(self) -> None:
        """MAX_LOAD = 'load all available from target' — preview moves
        the full target amount to source."""
        source = _resource_snap(capacity_mass=100.0, mass_used=0.0)
        target = _resource_snap(
            capacity_mass=100.0,
            mass_used=2.5,
            entries=(_resource_entry("metals", 250.0, 0.01),),
        )

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,),
            {"metals": TransferViewModel.MAX_LOAD},
        )

        # All 250 metals move target → source. 250 * 0.01 = 2.5 tons.
        assert preview.source_mass_remaining_after == pytest.approx(97.5)
        assert preview.target_mass_remaining_after == pytest.approx(100.0)

    def test_max_drop_resolves_to_source_current_amount(self) -> None:
        """MAX_DROP = 'drop all available from source to target'."""
        source = _resource_snap(
            capacity_mass=100.0,
            mass_used=1.5,
            entries=(_resource_entry("fuel", 15000.0, 0.0001),),
        )
        target = _resource_snap(capacity_mass=100.0, mass_used=0.0)

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,),
            {"fuel": TransferViewModel.MAX_DROP},
        )

        # All 15000 fuel * 0.0001 = 1.5 tons moves source → target.
        assert preview.source_mass_remaining_after == pytest.approx(100.0)
        assert preview.target_mass_remaining_after == pytest.approx(98.5)


# ---------------------------------------------------------------------------
# Capacity overflow flag
# ---------------------------------------------------------------------------


class TestCapacityOverflowFlag:
    def test_target_over_capacity_when_load_exceeds_remaining(self) -> None:
        """When pending math drives target's projected mass above
        capacity, the flag flips so the renderer can style accordingly."""
        source = _resource_snap(
            capacity_mass=100.0,
            mass_used=10.0,
            entries=(_resource_entry("metals", 1000.0, 0.01),),
        )
        # Target with only 0.5 tons remaining.
        target = _resource_snap(
            capacity_mass=1.0,
            mass_used=0.5,
            entries=(_resource_entry("metals", 50.0, 0.01),),
        )

        # Drop 200 metals (2 tons) into target — far exceeds remaining.
        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"metals": -200},
        )

        assert preview.target_over_capacity is True

    def test_infinite_capacity_never_over(self) -> None:
        source = _resource_snap(capacity_mass=float("inf"), mass_used=0.0)
        target = _resource_snap(capacity_mass=float("inf"), mass_used=0.0)

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,), {"metals": 1000000},
        )

        assert preview.target_over_capacity is False


# ---------------------------------------------------------------------------
# Items (Phase 3) — currently mass-neutral
# ---------------------------------------------------------------------------


class TestItemPendingIsMassNeutralInPhase2:
    def test_drop_pod_keys_do_not_change_mass_preview(self) -> None:
        """ITEM-kind cargo keys (drop_pod:, vehicle:) are skipped by the
        Phase 2 mass preview — Phase 3 folds them in alongside the
        mixed-content row builder."""
        source = _resource_snap(
            capacity_mass=100.0,
            mass_used=10.0,
            entries=(
                ContainerEntry(
                    kind=ContainableKind.ITEM,
                    type_id="Marine Pod",
                    quantity=1.0,
                    mass_total=10.0,
                ),
            ),
        )
        target = _resource_snap(capacity_mass=100.0, mass_used=0.0)

        preview = TransferViewModel.compute_mass_preview(
            (source,), (target,),
            {"drop_pod:Marine Pod": -1, "vehicle:qs_mine": 1},
        )

        # No mass change either side.
        assert preview.source_mass_remaining_after == pytest.approx(90.0)
        assert preview.target_mass_remaining_after == pytest.approx(100.0)


# ---------------------------------------------------------------------------
# MassPreview dataclass
# ---------------------------------------------------------------------------


def test_mass_preview_is_immutable() -> None:
    preview = MassPreview(
        source_mass_remaining_after=1.0,
        target_mass_remaining_after=2.0,
        source_capacity_mass=3.0,
        target_capacity_mass=4.0,
        target_over_capacity=False,
    )
    with pytest.raises((AttributeError, Exception)):
        preview.source_capacity_mass = 99.0  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Format helper (renderer side)
# ---------------------------------------------------------------------------


class TestFormatRemainingText:
    """The renderer's ``_format_remaining_text`` is pure string —
    testable without pygame."""

    def test_finite_capacity_shows_x_over_y(self) -> None:
        from game.ui.screens.transfer_grid_renderer import (
            _format_remaining_text,
        )

        result = _format_remaining_text(
            "Source", 42.3, 200.0, over_capacity=False,
        )

        assert result == "Source: 42.3 / 200.0t"

    def test_infinite_capacity_collapses_to_em_dash(self) -> None:
        from game.ui.screens.transfer_grid_renderer import (
            _format_remaining_text,
        )

        result = _format_remaining_text(
            "Target", 0.0, float("inf"), over_capacity=False,
        )

        assert result == "Target: —"

    def test_over_capacity_shows_explicit_marker(self) -> None:
        from game.ui.screens.transfer_grid_renderer import (
            _format_remaining_text,
        )

        result = _format_remaining_text(
            "Target", -5.0, 100.0, over_capacity=True,
        )

        assert result == "Target: OVER (cap 100.0t)"
