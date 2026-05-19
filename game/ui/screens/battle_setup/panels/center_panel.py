"""PROJ-282 Phase 4: center-panel renderer for `FleetBattleSetupScreen`.

Builds the center panel: fleet hierarchy (TaskForce → Squadron → ships),
policy dropdowns for the selected TF/SQ, per-ship policy dropdowns for a
selected ship, and the unassigned-ships section. Largest panel by
line-count.
"""
from __future__ import annotations

import pygame
from pygame_gui.elements import UIPanel, UIButton, UILabel, UIDropDownMenu


def build(screen, x: int, width: int, height: int) -> None:
    """Build the center panel. Mutates `screen` with pygame_gui handles."""
    from game.ui.screens.battle_setup.constants import (
        _TARGETING_OPTIONS,
        _MOVEMENT_OPTIONS,
        _BATTLE_ROLE_OPTIONS,
    )

    panel = UIPanel(
        relative_rect=pygame.Rect(x, 0, width, height),
        manager=screen._ui_manager, object_id='#center_panel'
    )
    y = 10

    side = screen.state.get_side(screen.view_model.active_side)
    fleet = (
        side.fleets[screen.view_model.active_fleet_index]
        if screen.view_model.active_fleet_index < len(side.fleets) else None
    )

    fleet_name = getattr(fleet, '_battle_setup_name', "No Fleet") if fleet else "No Fleet"
    UILabel(pygame.Rect(10, y, width - 20, 28), f"Fleet: {fleet_name}",
            manager=screen._ui_manager, container=panel)
    y += 32

    if not fleet:
        return

    # Fleet battle role
    UILabel(pygame.Rect(10, y, 80, 22), "Deploy:",
            manager=screen._ui_manager, container=panel)
    role_names = [name for _, name in _BATTLE_ROLE_OPTIONS]
    current_role = fleet.task_forces[0].battle_role if fleet.task_forces else None
    if current_role is None:
        current_role_name = "Main Body"
    else:
        current_role_name = next(
            (n for r, n in _BATTLE_ROLE_OPTIONS if r == current_role), "Main Body"
        )
    screen._fleet_role_dropdown = UIDropDownMenu(
        role_names, current_role_name,
        pygame.Rect(90, y, 160, 26),
        manager=screen._ui_manager, container=panel
    )
    y += 32

    # Target indicator — where new ships will go
    target_desc = "Unassigned (fleet level)"
    if screen.view_model.selected_tf_index is not None and screen.view_model.selected_tf_index < len(fleet.task_forces):
        tf = fleet.task_forces[screen.view_model.selected_tf_index]
        if screen.view_model.selected_sq_index is not None and screen.view_model.selected_sq_index < len(tf.squadrons):
            sq = tf.squadrons[screen.view_model.selected_sq_index]
            target_desc = f"SQ: {sq.name} in TF: {tf.name}"
        else:
            target_desc = f"TF: {tf.name} (lone ship)"

    UILabel(pygame.Rect(10, y, width - 20, 22),
            f"Add ships to: {target_desc}",
            manager=screen._ui_manager, container=panel)
    y += 25

    # Task forces section
    UILabel(pygame.Rect(10, y, width - 20, 22), "Task Forces (click to select target):",
            manager=screen._ui_manager, container=panel)
    y += 25

    screen._tf_buttons = []
    screen._tf_dup_buttons = []
    for ti, tf in enumerate(fleet.task_forces):
        # Task force header — highlight if selected
        is_tf_selected = (
            screen.view_model.selected_tf_index == ti and screen.view_model.selected_sq_index is None
        )
        marker = ">> " if is_tf_selected else "   "
        tf_label = f"{marker}TF: {tf.name} ({len(tf.all_ships)} ships)"
        btn = UIButton(
            pygame.Rect(10, y, width - 90, 26), tf_label,
            manager=screen._ui_manager, container=panel
        )
        btn._tf_index = ti

        dup_btn = UIButton(
            pygame.Rect(width - 78, y, 35, 26), "Dup",
            manager=screen._ui_manager, container=panel
        )
        dup_btn._dup_tf_index = ti

        del_btn = UIButton(
            pygame.Rect(width - 40, y, 30, 26), "X",
            manager=screen._ui_manager, container=panel
        )
        del_btn._del_tf_index = ti

        screen._tf_buttons.append(btn)
        screen._tf_dup_buttons.append((dup_btn, del_btn))
        y += 28

        # Show squadrons within TF
        for si, sq in enumerate(tf.squadrons):
            is_sq_selected = (
                screen.view_model.selected_tf_index == ti and screen.view_model.selected_sq_index == si
            )
            sq_marker = ">>" if is_sq_selected else "  "
            sq_label = f"{sq_marker} SQ: {sq.name} ({len(sq.all_ships)} ships)"
            sq_btn = UIButton(
                pygame.Rect(20, y, width - 110, 24), sq_label,
                manager=screen._ui_manager, container=panel
            )
            sq_btn._sq_tf_index = ti
            sq_btn._sq_index = si

            sq_dup = UIButton(
                pygame.Rect(width - 78, y, 35, 24), "Dup",
                manager=screen._ui_manager, container=panel
            )
            sq_dup._dup_sq_tf_index = ti
            sq_dup._dup_sq_index = si

            sq_del = UIButton(
                pygame.Rect(width - 40, y, 30, 24), "X",
                manager=screen._ui_manager, container=panel
            )
            sq_del._del_sq_tf_index = ti
            sq_del._del_sq_index = si

            y += 26

        # Show lone ships in TF
        for ship in tf.lone_ships:
            UILabel(pygame.Rect(30, y, width - 40, 20),
                    f"  {ship.name}",
                    manager=screen._ui_manager, container=panel)
            y += 22

    # Add task force button
    y += 5
    screen._add_tf_btn = UIButton(
        pygame.Rect(10, y, 130, 26), "Add Task Force",
        manager=screen._ui_manager, container=panel
    )
    screen._add_sq_btn = UIButton(
        pygame.Rect(150, y, 130, 26), "Add Squadron",
        manager=screen._ui_manager, container=panel
    )
    y += 32

    # === Selected item policy controls ===
    y = _build_policy_controls(screen, panel, y, width, fleet)

    # Unassigned ships (in fleet but not in any task force)
    unassigned = fleet.get_unassigned_ships()
    UILabel(pygame.Rect(10, y, width - 20, 22),
            f"Ships ({len(fleet.ships)} total, {len(unassigned)} unassigned):",
            manager=screen._ui_manager, container=panel)
    y += 25

    screen._ship_buttons = []
    for i, ship in enumerate(fleet.ships):
        hull = ship.design_data.get('ship_class', '?')
        is_selected = (screen.view_model.selected_ship_index == i)
        marker = "> " if is_selected else "  "
        btn = UIButton(
            pygame.Rect(10, y, width - 80, 26),
            f"{marker}{ship.name} ({hull})",
            manager=screen._ui_manager, container=panel
        )
        btn._ship_index = i

        remove_btn = UIButton(
            pygame.Rect(width - 65, y, 55, 26), "Remove",
            manager=screen._ui_manager, container=panel
        )
        remove_btn._remove_ship_index = i

        screen._ship_buttons.append((btn, remove_btn))
        y += 28

        # Show policy dropdowns for selected ship
        if is_selected:
            # Targeting policy for this ship
            UILabel(pygame.Rect(20, y, 60, 22), "Target:",
                    manager=screen._ui_manager, container=panel)
            tgt_names = ["(default)"] + [name for _, name in _TARGETING_OPTIONS]
            current_tgt = ship.design_data.get('_targeting_policy')
            current_tgt_display = "(default)"
            if current_tgt:
                current_tgt_display = next(
                    (n for tid, n in _TARGETING_OPTIONS if tid == current_tgt),
                    "(default)"
                )
            screen._ship_targeting_dropdown = UIDropDownMenu(
                tgt_names, current_tgt_display,
                pygame.Rect(80, y, width - 90, 24),
                manager=screen._ui_manager, container=panel
            )
            screen._ship_targeting_dropdown._targeting_ship_index = i
            y += 28

            # Movement policy for this ship
            UILabel(pygame.Rect(20, y, 60, 22), "Move:",
                    manager=screen._ui_manager, container=panel)
            mov_names = ["(default)"] + [name for _, name in _MOVEMENT_OPTIONS]
            current_mov = ship.design_data.get('_movement_policy')
            current_mov_display = "(default)"
            if current_mov:
                current_mov_display = next(
                    (n for mid, n in _MOVEMENT_OPTIONS if mid == current_mov),
                    "(default)"
                )
            screen._ship_movement_dropdown = UIDropDownMenu(
                mov_names, current_mov_display,
                pygame.Rect(80, y, width - 90, 24),
                manager=screen._ui_manager, container=panel
            )
            screen._ship_movement_dropdown._movement_ship_index = i
            y += 28


def _build_policy_controls(screen, panel, y: int, width: int, fleet) -> int:
    """Build policy dropdowns for the selected TF, SQ, or ship. Returns new y."""
    from game.ui.screens.battle_setup.constants import (
        _TARGETING_OPTIONS,
        _MOVEMENT_OPTIONS,
    )

    screen._targeting_dropdown = None
    screen._movement_dropdown = None
    screen._ship_targeting_dropdown = None
    screen._ship_movement_dropdown = None

    selected_node = None
    label = ""

    if screen.view_model.selected_tf_index is not None and screen.view_model.selected_tf_index < len(fleet.task_forces):
        tf = fleet.task_forces[screen.view_model.selected_tf_index]
        if screen.view_model.selected_sq_index is not None and screen.view_model.selected_sq_index < len(tf.squadrons):
            selected_node = tf.squadrons[screen.view_model.selected_sq_index]
            label = f"Squadron: {selected_node.name}"
        else:
            selected_node = tf
            label = f"Task Force: {tf.name}"

    if selected_node is not None:
        UILabel(pygame.Rect(10, y, width - 20, 22), f"Policies for {label}:",
                manager=screen._ui_manager, container=panel)
        y += 25

        # Targeting policy
        UILabel(pygame.Rect(10, y, 70, 22), "Target:",
                manager=screen._ui_manager, container=panel)
        tgt_names = ["(inherit)"] + [name for _, name in _TARGETING_OPTIONS]
        current_tgt = "(inherit)"
        if selected_node.policy.targeting:
            current_tgt = next(
                (n for tid, n in _TARGETING_OPTIONS if tid == selected_node.policy.targeting),
                "(inherit)"
            )
        screen._targeting_dropdown = UIDropDownMenu(
            tgt_names, current_tgt,
            pygame.Rect(80, y, width - 90, 24),
            manager=screen._ui_manager, container=panel
        )
        y += 28

        # Movement policy
        UILabel(pygame.Rect(10, y, 70, 22), "Move:",
                manager=screen._ui_manager, container=panel)
        mov_names = ["(inherit)"] + [name for _, name in _MOVEMENT_OPTIONS]
        current_mov = "(inherit)"
        if selected_node.policy.movement:
            current_mov = next(
                (n for mid, n in _MOVEMENT_OPTIONS if mid == selected_node.policy.movement),
                "(inherit)"
            )
        screen._movement_dropdown = UIDropDownMenu(
            mov_names, current_mov,
            pygame.Rect(80, y, width - 90, 24),
            manager=screen._ui_manager, container=panel
        )
        y += 28

    # Per-ship AI strategy for selected ship
    # (shown for unassigned ships when clicked in the ship list)

    y += 5
    return y
