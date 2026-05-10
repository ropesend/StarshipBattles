"""Contract test: WorkshopViewModel public API surface (PROJ-309 sub-phase 3.8).

Captures the names of public methods/properties on WorkshopViewModel pre-split
and asserts they remain present post-split. This guards the public seam used by
~5 production callers and 23 test files: every existing call site goes through
``viewmodel.<name>`` exactly as today, even though internals are now decomposed
into ``WorkshopShipOps``, ``WorkshopLayerOps`` and the ``workshop_viewmodel_selection``
helpers.

Pre-split: every name in ``EXPECTED_PUBLIC_API`` is defined on the monolithic
``WorkshopViewModel``. Post-split: the same names are still present (some as
one-line delegators).
"""
from __future__ import annotations

import inspect

from game.ui.screens.workshop_viewmodel import WorkshopViewModel


# Snapshot taken from workshop_viewmodel.py at 873 LOC, before sub-phase 3.8
# decomposition. Sourced by inspecting the source file and grouping by section.
EXPECTED_PUBLIC_API: frozenset[str] = frozenset({
    # Lifecycle / DI guard
    "_require_ship",
    # Ship state property + emitters
    "ship",
    "_emit_ship_updated",
    "notify_ship_changed",
    # Selection state
    "selected_components",
    "primary_selection",
    "select_component",
    "_normalize_selection",
    "_handle_append_selection",
    "_emit_selection_changed",
    "clear_selection",
    # Drag state
    "dragged_item",
    # Available components catalog
    "available_components",
    "refresh_available_components",
    # Hull layer visibility
    "show_hull_layer",
    "toggle_hull_layer",
    # Modifier sync
    "on_modifier_changed",
    "_sync_modifiers_to_selection",
    # Result accessors
    "last_result",
    "last_errors",
    "last_warnings",
    # Ship CRUD via VehicleDesignService
    "create_default_ship",
    "add_component",
    "add_component_bulk",
    "add_component_instance",
    "remove_component",
    "pick_up_component",
    "change_ship_class",
    "validate_design",
    "get_available_components_for_layer",
    "get_ship_summary",
    "clear_design",
    # Ship attribute setters
    "set_ship_name",
    "set_ship_theme",
    "set_ship_movement_policy",
    "set_ship_targeting_policy",
    "set_ship_design_role",
    # Layer resolution + quick-add
    "resolve_target_layer",
    "quick_add_component",
    # Component movement
    "resolve_move_target",
    "move_component",
    "move_component_group",
})


def _public_and_dunder_protected_names(cls: type) -> set[str]:
    """Return names defined on the class (and its bases excluding object) that are
    either public, single-underscore-protected, or dunder. Excludes purely inherited
    builtins from object.
    """
    names: set[str] = set()
    for klass in cls.__mro__:
        if klass is object:
            break
        for name, _member in inspect.getmembers(klass):
            names.add(name)
    return names


class TestWorkshopViewModelPublicAPI:
    """Pin the public + protected API surface of WorkshopViewModel."""

    def test_every_expected_member_present(self) -> None:
        """Every name captured pre-split must still resolve on the class."""
        present = _public_and_dunder_protected_names(WorkshopViewModel)
        missing = EXPECTED_PUBLIC_API - present
        assert not missing, (
            f"WorkshopViewModel is missing public-API members after split: "
            f"{sorted(missing)}"
        )

    def test_select_component_is_callable(self) -> None:
        assert callable(WorkshopViewModel.select_component)

    def test_ship_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.ship, property)

    def test_selected_components_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.selected_components, property)

    def test_primary_selection_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.primary_selection, property)

    def test_dragged_item_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.dragged_item, property)

    def test_available_components_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.available_components, property)

    def test_show_hull_layer_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.show_hull_layer, property)

    def test_last_result_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.last_result, property)

    def test_last_errors_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.last_errors, property)

    def test_last_warnings_is_property(self) -> None:
        assert isinstance(WorkshopViewModel.last_warnings, property)
