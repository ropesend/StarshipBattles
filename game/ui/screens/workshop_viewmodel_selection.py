"""Selection helpers for ``WorkshopViewModel`` (PROJ-309 sub-phase 3.8).

Pure-ish module-level functions extracted from ``WorkshopViewModel`` so the
viewmodel core stays under 500 LOC. Selection STATE still lives on the
viewmodel (``_selected_components``); these helpers contain only the
algorithms — normalisation, append/toggle/homogeneity, and modifier copy.

Event emission stays on the viewmodel (it owns the event_bus).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

from game.core.constants import LayerType

if TYPE_CHECKING:
    from game.simulation.components.component import Component
    from game.simulation.entities.ship import Ship


def normalize_selection(
    items: List, ship: Optional["Ship"]
) -> List[Tuple[Optional[LayerType], int, "Component"]]:
    """Convert various selection formats to normalised tuples.

    Uses duck typing (``hasattr(item, 'id')``) because selection logic accepts
    both real ``Component`` instances and mock objects in tests.

    Items already in ``(layer, index, comp)`` tuple form are passed through.
    Component-like objects are looked up in ``ship.layers`` to discover their
    (layer, index) coordinates. Templates / dragged components that do not
    appear on the ship are returned as ``(None, -1, comp)``.

    Args:
        items: Iterable of selection candidates: tuples, components, or mocks.
        ship: Current ship (may be ``None``).

    Returns:
        New list of normalised selection tuples.
    """
    norm_selection: List[Tuple[Optional[LayerType], int, "Component"]] = []
    for item in items:
        if isinstance(item, tuple) and len(item) == 3:
            norm_selection.append(item)
        elif hasattr(item, "id"):  # Component-like object
            found = False
            if ship is not None:
                for l_type, l_data in ship.layers.items():
                    try:
                        idx = l_data.components.index(item)
                        norm_selection.append((l_type, idx, item))
                        found = True
                        break
                    except ValueError:
                        continue
            if not found:
                # Template / dragged component
                norm_selection.append((None, -1, item))
    return norm_selection


def apply_append_selection(
    current: List[Tuple[Optional[LayerType], int, "Component"]],
    incoming: List[Tuple[Optional[LayerType], int, "Component"]],
    toggle: bool,
) -> List[Tuple[Optional[LayerType], int, "Component"]]:
    """Compute the new selection list when appending or toggling.

    Rules (preserved verbatim from the monolith):
    - If current is empty, the result is ``incoming``.
    - If ``incoming`` is empty, the result is ``current`` unchanged.
    - Homogeneity: all selected items must share the same component-definition
      ``id``. If ``incoming`` items are a different type, replace the
      selection with ``incoming``.
    - Otherwise, add unique items by object identity. If ``toggle`` is True
      and an item is already in ``current``, remove it.

    Args:
        current: The viewmodel's current selection list.
        incoming: The new (already normalised) items being applied.
        toggle: Ctrl+Click semantics — toggle existing items off.

    Returns:
        A NEW selection list. The caller should assign it back to the
        viewmodel; this function does not mutate the inputs in place.
    """
    if not current:
        return list(incoming)

    if not incoming:
        return list(current)

    # Enforce homogeneity — all selected must be same component type
    current_def_id = current[0][2].id
    matches_type = all(item[2].id == current_def_id for item in incoming)

    if not matches_type:
        return list(incoming)

    # Add/toggle unique items (by object identity)
    result = list(current)
    current_objs = {c[2] for c in result}
    toggled_off = set()
    for item in incoming:
        if item[2] in current_objs:
            if toggle:
                # Toggle OFF: remove by object identity
                result = [x for x in result if x[2] is not item[2]]
                # Update object set so a later duplicate in `incoming` doesn't
                # re-add the same item.
                current_objs = {c[2] for c in result}
                toggled_off.add(item[2])
        elif item[2] not in toggled_off:
            result.append(item)
            current_objs.add(item[2])
    return result


def sync_modifiers_to_selection(
    primary_component: "Component",
    selection: List[Tuple[Optional[LayerType], int, "Component"]],
) -> None:
    """Copy modifiers from ``primary_component`` to all sibling components in
    ``selection`` (skipping the primary itself).

    Mutates the sibling components in place via
    ``builder.modifier_utils.copy_modifiers``. Called by the viewmodel when a
    multi-selection's primary component has had its modifiers edited.

    Args:
        primary_component: The component whose modifiers are the source of truth.
        selection: The current selection list.
    """
    from game.ui.screens.builder.modifier_utils import copy_modifiers

    for item in selection:
        comp = item[2]
        if comp is primary_component:
            continue
        copy_modifiers(primary_component, comp)
