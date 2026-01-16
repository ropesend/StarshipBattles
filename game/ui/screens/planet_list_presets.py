"""Planet list preset management.

Handles saving and loading of filter/column presets for the planet list window.
"""
import os
from game.core.constants import DATA_DIR
from game.core.json_utils import load_json, save_json
from game.core.logger import log_info


class PresetManager:
    """Manages presets for planet list window configuration."""

    PRESET_FILENAME = 'ui_presets.json'

    def __init__(self):
        self.presets = self._load_from_disk()

    def _load_from_disk(self):
        """Load presets from disk."""
        path = os.path.join(DATA_DIR, self.PRESET_FILENAME)
        return load_json(path, default={})

    def save_to_disk(self):
        """Save presets to disk."""
        path = os.path.join(DATA_DIR, self.PRESET_FILENAME)
        save_json(path, self.presets)

    def get_preset_names(self):
        """Get list of preset names."""
        opts = list(self.presets.keys())
        if "Default" not in opts:
            opts.insert(0, "Default")
        return opts

    def save_preset(self, name, state):
        """Save a preset with the given name and state."""
        self.presets[name] = state
        self.save_to_disk()
        log_info(f"Saved Preset: {name}")

    def get_preset(self, name):
        """Get a preset by name, or None if not found."""
        return self.presets.get(name)

    def has_preset(self, name):
        """Check if a preset exists."""
        return name in self.presets


def capture_planet_list_state(columns, txt_name_filter, filter_types, filter_owner, ui_filters):
    """Capture current planet list state for saving as a preset.

    Args:
        columns: List of column definitions
        txt_name_filter: The name filter text entry widget
        filter_types: Dict of planet type filter states
        filter_owner: Dict of owner filter states
        ui_filters: Dict containing slider UI elements

    Returns:
        Dict containing serialized state
    """
    # Columns: order and visibility
    cols_data = []
    for c in columns:
        cols_data.append({'id': c['id'], 'visible': c['visible']})

    # Filters
    filters_data = {
        'name': txt_name_filter.get_text(),
        'types': filter_types.copy(),
        'owner': filter_owner.copy(),
        'ranges': {
            'gravity': [
                ui_filters['gravity']['min'].get_current_value(),
                ui_filters['gravity']['max'].get_current_value()
            ],
            'temp': [
                ui_filters['temp']['min'].get_current_value(),
                ui_filters['temp']['max'].get_current_value()
            ],
            'mass': [
                ui_filters['mass']['min'].get_current_value(),
                ui_filters['mass']['max'].get_current_value()
            ]
        }
    }

    return {
        'columns': cols_data,
        'filters': filters_data
    }


def apply_planet_list_state(state, columns, txt_name_filter, filter_types, ui_filters):
    """Apply a saved state to the planet list.

    Args:
        state: The saved state dict
        columns: List of column definitions (will be modified)
        txt_name_filter: The name filter text entry widget
        filter_types: Dict of planet type filter states (will be modified)
        ui_filters: Dict containing slider and button UI elements

    Returns:
        The reordered columns list
    """
    new_cols = columns

    # Restore Columns
    if 'columns' in state:
        # Reorder columns to match saved order
        saved_order = state['columns']  # List of {id, visible}

        new_cols = []
        # Create map of current columns
        current_map = {c['id']: c for c in columns}

        for item in saved_order:
            cid = item['id']
            if cid in current_map:
                col = current_map[cid]
                col['visible'] = item['visible']
                new_cols.append(col)
                del current_map[cid]

        # Append any remaining new columns (code updates)
        for c in current_map.values():
            new_cols.append(c)

        # Update UI Checkboxes
        for cid, btn in ui_filters.get('columns', {}).items():
            # Find col
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
            if 'gravity' in r:
                ui_filters['gravity']['min'].set_current_value(r['gravity'][0])
                ui_filters['gravity']['max'].set_current_value(r['gravity'][1])
            if 'temp' in r:
                ui_filters['temp']['min'].set_current_value(r['temp'][0])
                ui_filters['temp']['max'].set_current_value(r['temp'][1])
            if 'mass' in r:
                ui_filters['mass']['min'].set_current_value(r['mass'][0])
                ui_filters['mass']['max'].set_current_value(r['mass'][1])

    return new_cols
