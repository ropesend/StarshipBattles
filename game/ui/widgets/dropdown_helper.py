"""Shared utility for recreating pygame_gui dropdown menus.

pygame_gui's UIDropDownMenu has no API to change the selected option or
options list after creation. The standard workaround is to kill the old
widget and create a new one preserving the rect and container.

This module centralizes that pattern to eliminate duplication across panels.
"""
from typing import List, Optional
from pygame_gui.elements import UIDropDownMenu


def recreate_dropdown(
    old_dropdown,
    options: List[str],
    selected: str,
    manager,
    container=None,
) -> Optional[UIDropDownMenu]:
    """Kill an existing dropdown and create a replacement with new options.

    Args:
        old_dropdown: The UIDropDownMenu to replace. If None, returns None.
        options: New options list. If empty, uses [''] as fallback.
        selected: Value to select. Falls back to first option if not in list.
        manager: pygame_gui UIManager.
        container: Optional override for the container. If None, uses the
            old dropdown's ui_container.

    Returns:
        The newly created UIDropDownMenu, or None if old_dropdown was None.
    """
    if old_dropdown is None:
        return None

    rect = old_dropdown.relative_rect
    target_container = container if container is not None else old_dropdown.ui_container
    old_dropdown.kill()

    if not options:
        options = ['']
        selected = ''
    elif selected not in options:
        selected = options[0]

    return UIDropDownMenu(
        options_list=options,
        starting_option=selected,
        relative_rect=rect,
        manager=manager,
        container=target_container,
    )
