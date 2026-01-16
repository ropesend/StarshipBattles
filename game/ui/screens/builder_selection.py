"""Selection management for the ship builder.

This module handles component selection logic including multi-select,
append, toggle, and homogeneity enforcement.
"""


def normalize_selection(new_selection, ship):
    """Normalize selection items to (layer, index, component) tuples.

    Args:
        new_selection: List of selection items (tuples or components)
        ship: The ship object to search for components

    Returns:
        List of normalized (layer_type, index, component) tuples
    """
    norm_selection = []
    for item in new_selection:
        if isinstance(item, tuple) and len(item) == 3:
            norm_selection.append(item)
        elif hasattr(item, 'id'):  # It's a component
            # Find it in ship
            found = False
            for l_type, l_data in ship.layers.items():
                try:
                    idx = l_data['components'].index(item)
                    norm_selection.append((l_type, idx, item))
                    found = True
                    break
                except ValueError:
                    continue
            if not found:
                # Maybe it's a template (dragged)
                norm_selection.append((None, -1, item))
    return norm_selection


def process_selection_change(current_selection, new_selection, ship, append=False, toggle=False):
    """Process a selection change and return the new selection list.

    Args:
        current_selection: Current list of selected components (layer, idx, comp tuples)
        new_selection: New selection (single item, list, or None)
        ship: The ship object for component lookup
        append: If True, add to existing selection instead of replacing
        toggle: If True, toggle selection state of existing items (Ctrl+Click)

    Returns:
        Tuple of (new_selection_list, was_replaced) where was_replaced indicates
        if the selection was replaced rather than appended
    """
    if new_selection is None:
        if not append:
            return [], False
        return current_selection, False

    if not isinstance(new_selection, list):
        new_selection = [new_selection]

    norm_selection = normalize_selection(new_selection, ship)

    was_replaced = False

    if append:
        # Enforce Homogeneity
        # Check if new items match the type (definition ID) of existing selection
        if current_selection and norm_selection:
            # Get definition ID of currently selected items (assuming they are homogeneous)
            current_def_id = current_selection[0][2].id

            # Check if all new items match this ID
            matches_type = all(item[2].id == current_def_id for item in norm_selection)

            if not matches_type:
                # User clicked a different type. Standard behavior: Replace selection.
                was_replaced = True
                return norm_selection, was_replaced
            else:
                # Add unique items (Uniqueness based on OBJECT IDENTITY, not Def ID)
                result = list(current_selection)
                current_objs = {c[2] for c in current_selection}

                for item in norm_selection:
                    if item[2] in current_objs:
                        if toggle:
                            # Toggle OFF
                            result = [x for x in result if x[2] is not item[2]]
                        # else: Ensure selected (do nothing if already there)
                    else:
                        result.append(item)

                return result, False
        else:
            # Nothing currently selected, just set to new selection
            return norm_selection, False
    else:
        return norm_selection, False


def get_primary_selection(selected_components):
    """Get the primary (last) selected component.

    Args:
        selected_components: List of selected component tuples

    Returns:
        The last selected component tuple, or None if empty
    """
    return selected_components[-1] if selected_components else None
