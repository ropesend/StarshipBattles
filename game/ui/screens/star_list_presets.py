"""Star list preset management.

Handles saving and loading of filter/column presets for the star list window.
Mirrors planet_list_presets.py for stars.

PROJ-231: Star List Panel.
"""
from __future__ import annotations

from typing import Any

from game.ui.screens.planet_list_presets import PresetManager


class StarPresetManager(PresetManager):
    """Manages presets for star list window configuration.

    Uses a separate file from planet presets to avoid collisions.
    """

    PRESET_FILENAME = 'star_ui_presets.json'


def capture_star_list_state(columns, txt_name_filter, filter_types, ui_filters) -> dict[str, Any]:
    """Capture current star list state for saving as a preset.

    Args:
        columns: List of column definitions
        txt_name_filter: The name filter text entry widget
        filter_types: Dict of star type filter states
        ui_filters: Dict containing slider UI elements

    Returns:
        Dict containing serialized state
    """
    cols_data = []
    for c in columns:
        cols_data.append({'id': c['id'], 'visible': c['visible']})

    filters_data = {
        'name': txt_name_filter.get_text(),
        'types': filter_types.copy(),
        'ranges': {},
    }

    # Capture all range slider values
    for range_key in ('mass', 'temperature', 'luminosity', 'age', 'radius_hexes'):
        if range_key in ui_filters:
            filters_data['ranges'][range_key] = [
                ui_filters[range_key]['min'].get_current_value(),
                ui_filters[range_key]['max'].get_current_value(),
            ]

    return {
        'columns': cols_data,
        'filters': filters_data,
    }


def apply_star_list_state(state, columns, txt_name_filter, filter_types, ui_filters) -> list:
    """Apply a saved state to the star list.

    Args:
        state: The saved state dict
        columns: List of column definitions (will be modified)
        txt_name_filter: The name filter text entry widget
        filter_types: Dict of star type filter states (will be modified)
        ui_filters: Dict containing slider and button UI elements

    Returns:
        The reordered columns list
    """
    new_cols = columns

    # Restore Columns
    if 'columns' in state:
        saved_order = state['columns']

        new_cols = []
        current_map = {c['id']: c for c in columns}

        for item in saved_order:
            cid = item['id']
            if cid in current_map:
                col = current_map[cid]
                col['visible'] = item['visible']
                new_cols.append(col)
                del current_map[cid]

        # Append any remaining new columns
        for c in current_map.values():
            new_cols.append(c)

        # Update UI Checkboxes
        for cid, btn in ui_filters.get('columns', {}).items():
            col = next((c for c in new_cols if c['id'] == cid), None)
            if col:
                t = f"[x] {col['title'] or col['id']}" if col['visible'] else f"[ ] {col['title'] or col['id']}"
                btn.set_text(t)

    # Restore Filters
    if 'filters' in state:
        f = state['filters']
        if 'name' in f:
            txt_name_filter.set_text(f['name'])
        if 'types' in f:
            filter_types.clear()
            filter_types.update(f['types'])

        # Update Type Toggles UI
        for t, btn in ui_filters.get('types', {}).items():
            if t in filter_types:
                if filter_types[t]:
                    btn.select()
                    btn.set_text(f"[{t}]")
                else:
                    btn.unselect()
                    btn.set_text(f"{t}")

        if 'ranges' in f:
            r = f['ranges']
            for range_key in ('mass', 'temperature', 'luminosity', 'age', 'radius_hexes'):
                if range_key in r and range_key in ui_filters:
                    ui_filters[range_key]['min'].set_current_value(r[range_key][0])
                    ui_filters[range_key]['max'].set_current_value(r[range_key][1])

    return new_cols
