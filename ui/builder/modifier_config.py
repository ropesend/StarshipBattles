"""
Configuration for Component Modifier UI elements.
Defines layout, buttons, and ranges for specific modifiers.
"""

MODIFIER_UI_CONFIG = {
    'simple_size': {
        'control_type': 'linear_stepped',
        'step_buttons': [
            {'label': '<<', 'value': 100, 'mode': 'snap_floor'},
            {'label': '<', 'value': 10, 'mode': 'snap_floor'},
            {'label': '<', 'value': 1, 'mode': 'delta_sub'},
            # Slider
            {'label': '>', 'value': 1, 'mode': 'delta_add'},
            {'label': '>', 'value': 10, 'mode': 'snap_ceil'},
            {'label': '>>', 'value': 100, 'mode': 'snap_ceil'}
        ],
        'slider_step': 0.1,
    },
    'simple_size_mount': { # Handle alias if needed
        'control_type': 'linear_stepped',
        'step_buttons': [
            {'label': '<<', 'value': 100, 'mode': 'snap_floor'},
            {'label': '<', 'value': 10, 'mode': 'snap_floor'},
            {'label': '<', 'value': 1, 'mode': 'delta_sub'},
            # Slider
            {'label': '>', 'value': 1, 'mode': 'delta_add'},
            {'label': '>', 'value': 10, 'mode': 'snap_ceil'},
            {'label': '>>', 'value': 100, 'mode': 'snap_ceil'}
        ],
        'slider_step': 0.1,
        'smart_floor': True # Special rule for size <= 100
    },
    'turret_mount': {
        'control_type': 'linear_stepped',
        'step_buttons': [
            {'label': '<<', 'value': 90, 'mode': 'snap_floor'},
            {'label': '<', 'value': 15, 'mode': 'snap_floor'},
            {'label': '<', 'value': 1, 'mode': 'delta_sub'},
            # Slider
            {'label': '>', 'value': 1, 'mode': 'delta_add'},
            {'label': '>', 'value': 15, 'mode': 'snap_ceil'},
            {'label': '>>', 'value': 90, 'mode': 'snap_ceil'}
        ],
        'slider_step': 1.0,
    },
    'facing': {
        'control_type': 'facing_selector',
        'presets': [0, 90, 180, 270],
        'step_buttons': [
             {'label': '<<', 'value': 90, 'mode': 'snap_floor'},
             {'label': '<', 'value': 15, 'mode': 'snap_floor'},
             {'label': '<', 'value': 1, 'mode': 'delta_sub'},
             # Slider
             {'label': '>', 'value': 1, 'mode': 'delta_add'},
             {'label': '>', 'value': 15, 'mode': 'snap_ceil'},
             {'label': '>>', 'value': 90, 'mode': 'snap_ceil'}
        ],
        'slider_step': 1.0,
    },
    'range_mount': {
        'control_type': 'linear_stepped',
        'step_buttons': [
             {'label': '<<', 'value': 1.0, 'mode': 'delta_sub'},
             {'label': '<', 'value': 0.1, 'mode': 'delta_sub'},
             # Slider
             {'label': '>', 'value': 0.1, 'mode': 'delta_add'},
             {'label': '>>', 'value': 1.0, 'mode': 'delta_add'}
        ],
        'slider_step': 0.01,
    }
}

# Default configuration for modifiers not explicitly listed
DEFAULT_CONFIG = {
    'control_type': 'linear',
    'step_buttons': [ # Default simple steps
         {'label': '<<', 'value': 1.0, 'mode': 'delta_sub'},
         {'label': '<', 'value': 0.1, 'mode': 'delta_sub'},
         # Slider
         {'label': '>', 'value': 0.1, 'mode': 'delta_add'},
         {'label': '>>', 'value': 1.0, 'mode': 'delta_add'}
    ],
    'slider_step': 0.01
}
