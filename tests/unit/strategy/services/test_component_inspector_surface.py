"""PROJ-433 Phase 0: pin the public surface of ``component_inspector``.

Snapshot test that asserts the exact ``__all__`` set exported by
``game.strategy.services.component_inspector``. This is a drift gate for
Phase 1's split — if the mechanical move accidentally drops or renames a
public name, this test fails before any caller does.

Also verifies that every name in ``__all__`` is actually importable from
the module, so an entry in ``__all__`` cannot silently shadow a missing
symbol.
"""
from __future__ import annotations

import importlib


EXPECTED_PUBLIC_SURFACE: frozenset[str] = frozenset(
    {
        # Surface A — ability iteration
        "get_component_abilities",
        "extract_abilities_from_component",
        "get_component_type",
        "get_component_threshold",
        "iterate_design_components",
        "iter_facility_ability_entries",
        "ship_has_ability",
        "find_ship_with_ability",
        "count_ability",
        "list_ship_abilities",
        "get_ability_list",
        "has_warp_capability",
        # Surface B — layer view (PROJ-425 Phase 2 additions)
        "iter_components_by_layer",
        "damaged_components_by_layer",
        "count_damaged_components",
        "lookup_design_max_hp",
    }
)


def test_component_inspector_all_matches_expected_surface() -> None:
    module = importlib.import_module(
        "game.strategy.services.component_inspector"
    )
    assert hasattr(module, "__all__"), (
        "component_inspector must declare __all__ to pin its public surface"
    )
    assert frozenset(module.__all__) == EXPECTED_PUBLIC_SURFACE, (
        "component_inspector.__all__ drift detected — PROJ-433 split must "
        "preserve every name in EXPECTED_PUBLIC_SURFACE"
    )


def test_every_name_in_all_is_importable() -> None:
    module = importlib.import_module(
        "game.strategy.services.component_inspector"
    )
    missing = [name for name in module.__all__ if not hasattr(module, name)]
    assert not missing, (
        f"component_inspector.__all__ lists names that are not importable: "
        f"{missing}"
    )


def test_every_name_in_all_is_callable() -> None:
    """Every public surface entry is a callable function (no constants slipped in)."""
    module = importlib.import_module(
        "game.strategy.services.component_inspector"
    )
    non_callable = [
        name for name in module.__all__ if not callable(getattr(module, name))
    ]
    assert not non_callable, (
        f"component_inspector public surface must be all callables; "
        f"non-callables found: {non_callable}"
    )
