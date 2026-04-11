"""Fleet-based battle setup screen.

Replaces the old simple BattleSetupScreen with full fleet organization:
- Multiple fleets per side, each with TaskForce/Squadron hierarchy
- System-scope and sector-scope complex effects
- Design library browser for adding ships
- Save/load setup and individual fleets
- Task force/squadron management with duplication
- Multi-fleet deployment zones

IScene protocol: handle_event(), update(dt), draw(screen), handle_resize(w, h)
"""

import logging
import os

import pygame
import pygame_gui
from pygame_gui.elements import UIPanel, UIButton, UILabel, UIDropDownMenu

from game.core.paths import Paths
from game.core.json_utils import load_json, save_json
from game.ui.screens.battle_setup_state import BattleSetupState
from game.strategy.data.fleet_hierarchy import CombatPolicy, BattleRole
from game.strategy.data.task_force import TaskForce
from game.strategy.data.squadron import Squadron

logger = logging.getLogger(__name__)

# Complex design IDs that affect combat (system-scope)
_SYSTEM_SCOPE_COMPLEXES = [
    ("qs_system_shield_booster_complex", "System Shield Booster"),
    ("qs_system_shield_suppressor_complex", "System Shield Suppressor"),
    ("qs_system_shield_projector_complex", "System Shield Projector"),
    ("qs_system_damage_booster_complex", "System Damage Booster"),
    ("qs_system_damage_suppressor_complex", "System Damage Suppressor"),
]

_SECTOR_SCOPE_COMPLEXES = [
    ("qs_sector_shield_booster_complex", "Sector Shield Booster"),
    ("qs_sector_shield_suppressor_complex", "Sector Shield Suppressor"),
    ("qs_sector_shield_projector_complex", "Sector Shield Projector"),
    ("qs_sector_damage_booster_complex", "Sector Damage Booster"),
    ("qs_sector_damage_suppressor_complex", "Sector Damage Suppressor"),
]

# Targeting policy options for dropdowns
_TARGETING_OPTIONS = [
    ("focus_strongest", "Focus Strongest"),
    ("focus_nearest", "Focus Nearest"),
    ("focus_weakest", "Focus Weakest"),
    ("distributed", "Distributed"),
    ("anti_fighter", "Anti-Fighter"),
    ("anti_capital", "Anti-Capital"),
]

_MOVEMENT_OPTIONS = [
    ("advance", "Advance"),
    ("hold_range", "Hold Range"),
    ("hold_position", "Hold Position"),
    ("pursue", "Pursue"),
    ("hit_and_run", "Hit & Run"),
]

_BATTLE_ROLE_OPTIONS = [
    (BattleRole.MAIN_BODY, "Main Body"),
    (BattleRole.VANGUARD, "Vanguard"),
    (BattleRole.SCREEN, "Screen"),
    (BattleRole.FLANKER_LEFT, "Flanker Left"),
    (BattleRole.FLANKER_RIGHT, "Flanker Right"),
    (BattleRole.RESERVE, "Reserve"),
]


def _get_registries():
    """Get game registries for ship creation."""
    try:
        from game.core.registry import get_default_registry_provider, GameRegistries
        provider = get_default_registry_provider()
        return GameRegistries(
            components=provider.get_components(),
            modifiers=provider.get_modifiers(),
            vehicle_classes=provider.get_vehicle_classes(),
            resources=provider.get_resources(),
            resource_catalog=provider.get_resource_catalog(),
        )
    except Exception:
        return None


class FleetBattleSetupScreen:
    """Fleet-based battle setup screen with full hierarchy support."""

    def __init__(self, width: int, height: int, scene_callback=None):
        self.screen_width = width
        self.screen_height = height
        self.scene_callback = scene_callback

        self.state = BattleSetupState()
        self.active_side = 0
        self.active_fleet_index = 0
        self.available_designs = []

        self._ui_manager = None
        self._panels_built = False
        # Track complex toggle state per side: {(side, scope, design_id): bool}
        self._complex_toggles = {}

    # === IScene Protocol ===

    def handle_event(self, event):
        if self._ui_manager:
            self._ui_manager.process_events(event)
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            self._handle_button(event)
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            self._handle_dropdown(event)

    def update(self, dt: float):
        if self._ui_manager:
            self._ui_manager.update(dt)

    def draw(self, screen):
        screen.fill((20, 25, 35))
        if self._ui_manager:
            self._ui_manager.draw_ui(screen)

    def handle_resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        if self._ui_manager:
            self._ui_manager.set_window_resolution((width, height))
        self._rebuild_ui()

    # === Lifecycle ===

    def start(self, preserve_teams=False):
        if not preserve_teams:
            self.state.clear()
            self.state.side_0.create_fleet("Fleet Alpha")
            self.state.side_1.create_fleet("Fleet Beta")
            self.active_side = 0
            self.active_fleet_index = 0
            self._complex_toggles = {}

        self._scan_designs()
        self._rebuild_ui()

    def _scan_designs(self):
        self.available_designs = []
        designs_dir = Paths.STARTER_DESIGNS_DIR
        if not os.path.exists(designs_dir):
            return
        for filename in sorted(os.listdir(designs_dir)):
            if not filename.endswith('.json'):
                continue
            filepath = os.path.join(designs_dir, filename)
            try:
                data = load_json(filepath, default=None)
                if data and data.get('vehicle_type') == 'Ship':
                    data['_filepath'] = filepath
                    data['_design_id'] = filename.replace('.json', '')
                    self.available_designs.append(data)
            except Exception as e:
                logger.warning(f"Failed to load design {filename}: {e}")

    # === UI Construction ===

    def _rebuild_ui(self):
        if self._ui_manager:
            self._ui_manager.clear_and_reset()

        self._ui_manager = pygame_gui.UIManager(
            (self.screen_width, self.screen_height)
        )

        w = self.screen_width
        h = self.screen_height
        left_w = 250
        right_w = 280
        center_w = w - left_w - right_w
        bottom_h = 60

        self._build_left_panel(left_w, h - bottom_h)
        self._build_center_panel(left_w, center_w, h - bottom_h)
        self._build_right_panel(left_w + center_w, right_w, h - bottom_h)
        self._build_bottom_bar(w, h, bottom_h)
        self._panels_built = True

    def _build_left_panel(self, width, height):
        panel = UIPanel(
            relative_rect=pygame.Rect(0, 0, width, height),
            manager=self._ui_manager, object_id='#left_panel'
        )
        y = 10

        UILabel(pygame.Rect(10, y, width - 20, 30), "Battle Setup",
                manager=self._ui_manager, container=panel)
        y += 35

        # Side selector
        UILabel(pygame.Rect(10, y, 50, 25), "Side:",
                manager=self._ui_manager, container=panel)
        self._side_dropdown = UIDropDownMenu(
            ["Side 0 (Left)", "Side 1 (Right)"],
            f"Side {self.active_side} ({'Left' if self.active_side == 0 else 'Right'})",
            pygame.Rect(60, y, width - 70, 28),
            manager=self._ui_manager, container=panel
        )
        y += 35

        # Fleet list
        UILabel(pygame.Rect(10, y, width - 20, 22), "Fleets:",
                manager=self._ui_manager, container=panel)
        y += 25

        side = self.state.get_side(self.active_side)
        self._fleet_buttons = []
        for i, fleet in enumerate(side.fleets):
            name = getattr(fleet, '_battle_setup_name', f"Fleet {fleet.id}")
            ship_count = len(fleet.ships)
            btn = UIButton(
                pygame.Rect(10, y, width - 20, 28),
                f"{'> ' if i == self.active_fleet_index else '  '}{name} ({ship_count} ships)",
                manager=self._ui_manager, container=panel
            )
            btn._fleet_index = i
            self._fleet_buttons.append(btn)
            y += 30

        # Fleet management buttons
        y += 5
        half_w = (width - 30) // 2
        self._add_fleet_btn = UIButton(
            pygame.Rect(10, y, half_w, 28), "Add Fleet",
            manager=self._ui_manager, container=panel
        )
        self._remove_fleet_btn = UIButton(
            pygame.Rect(20 + half_w, y, half_w, 28), "Remove Fleet",
            manager=self._ui_manager, container=panel
        )
        y += 35

        # System complexes section
        UILabel(pygame.Rect(10, y, width - 20, 22), "System Complexes:",
                manager=self._ui_manager, container=panel)
        y += 25

        self._system_complex_btns = []
        for design_id, display_name in _SYSTEM_SCOPE_COMPLEXES:
            key = (self.active_side, "system", design_id)
            is_on = self._complex_toggles.get(key, False)
            icon = "[X]" if is_on else "[  ]"
            btn = UIButton(
                pygame.Rect(10, y, width - 20, 24),
                f"{icon} {display_name}",
                manager=self._ui_manager, container=panel
            )
            btn._complex_key = key
            btn._complex_design_id = design_id
            self._system_complex_btns.append(btn)
            y += 26

        y += 5
        # Sector complexes section
        UILabel(pygame.Rect(10, y, width - 20, 22), "Sector Complexes:",
                manager=self._ui_manager, container=panel)
        y += 25

        self._sector_complex_btns = []
        for design_id, display_name in _SECTOR_SCOPE_COMPLEXES:
            key = (self.active_side, "sector", design_id)
            is_on = self._complex_toggles.get(key, False)
            icon = "[X]" if is_on else "[  ]"
            btn = UIButton(
                pygame.Rect(10, y, width - 20, 24),
                f"{icon} {display_name}",
                manager=self._ui_manager, container=panel
            )
            btn._complex_key = key
            btn._complex_design_id = design_id
            self._sector_complex_btns.append(btn)
            y += 26

    def _build_center_panel(self, x, width, height):
        panel = UIPanel(
            relative_rect=pygame.Rect(x, 0, width, height),
            manager=self._ui_manager, object_id='#center_panel'
        )
        y = 10

        side = self.state.get_side(self.active_side)
        fleet = side.fleets[self.active_fleet_index] if self.active_fleet_index < len(side.fleets) else None

        fleet_name = getattr(fleet, '_battle_setup_name', "No Fleet") if fleet else "No Fleet"
        UILabel(pygame.Rect(10, y, width - 20, 28), f"Fleet: {fleet_name}",
                manager=self._ui_manager, container=panel)
        y += 32

        if not fleet:
            return

        # Fleet battle role
        UILabel(pygame.Rect(10, y, 80, 22), "Deploy:",
                manager=self._ui_manager, container=panel)
        role_names = [name for _, name in _BATTLE_ROLE_OPTIONS]
        current_role = fleet.task_forces[0].battle_role if fleet.task_forces else None
        if current_role is None:
            current_role_name = "Main Body"
        else:
            current_role_name = next((n for r, n in _BATTLE_ROLE_OPTIONS if r == current_role), "Main Body")
        self._fleet_role_dropdown = UIDropDownMenu(
            role_names, current_role_name,
            pygame.Rect(90, y, 160, 26),
            manager=self._ui_manager, container=panel
        )
        y += 32

        # Task forces section
        UILabel(pygame.Rect(10, y, width - 20, 22), "Task Forces:",
                manager=self._ui_manager, container=panel)
        y += 25

        self._tf_buttons = []
        self._tf_dup_buttons = []
        for ti, tf in enumerate(fleet.task_forces):
            # Task force header
            tf_label = f"TF: {tf.name} ({len(tf.all_ships)} ships)"
            btn = UIButton(
                pygame.Rect(10, y, width - 90, 26), tf_label,
                manager=self._ui_manager, container=panel
            )
            btn._tf_index = ti

            dup_btn = UIButton(
                pygame.Rect(width - 78, y, 35, 26), "Dup",
                manager=self._ui_manager, container=panel
            )
            dup_btn._dup_tf_index = ti

            del_btn = UIButton(
                pygame.Rect(width - 40, y, 30, 26), "X",
                manager=self._ui_manager, container=panel
            )
            del_btn._del_tf_index = ti

            self._tf_buttons.append(btn)
            self._tf_dup_buttons.append((dup_btn, del_btn))
            y += 28

            # Show squadrons within TF
            for si, sq in enumerate(tf.squadrons):
                sq_label = f"  SQ: {sq.name} ({len(sq.all_ships)} ships)"
                sq_btn = UIButton(
                    pygame.Rect(20, y, width - 110, 24), sq_label,
                    manager=self._ui_manager, container=panel
                )
                sq_btn._sq_tf_index = ti
                sq_btn._sq_index = si

                sq_dup = UIButton(
                    pygame.Rect(width - 78, y, 35, 24), "Dup",
                    manager=self._ui_manager, container=panel
                )
                sq_dup._dup_sq_tf_index = ti
                sq_dup._dup_sq_index = si

                sq_del = UIButton(
                    pygame.Rect(width - 40, y, 30, 24), "X",
                    manager=self._ui_manager, container=panel
                )
                sq_del._del_sq_tf_index = ti
                sq_del._del_sq_index = si

                y += 26

            # Show lone ships in TF
            for ship in tf.lone_ships:
                UILabel(pygame.Rect(30, y, width - 40, 20),
                        f"  {ship.name}",
                        manager=self._ui_manager, container=panel)
                y += 22

        # Add task force button
        y += 5
        self._add_tf_btn = UIButton(
            pygame.Rect(10, y, 130, 26), "Add Task Force",
            manager=self._ui_manager, container=panel
        )
        self._add_sq_btn = UIButton(
            pygame.Rect(150, y, 130, 26), "Add Squadron",
            manager=self._ui_manager, container=panel
        )
        y += 32

        # Unassigned ships (in fleet but not in any task force)
        unassigned = fleet.get_unassigned_ships()
        UILabel(pygame.Rect(10, y, width - 20, 22),
                f"Ships ({len(fleet.ships)} total, {len(unassigned)} unassigned):",
                manager=self._ui_manager, container=panel)
        y += 25

        self._ship_buttons = []
        for i, ship in enumerate(fleet.ships):
            hull = ship.design_data.get('ship_class', '?')
            btn = UIButton(
                pygame.Rect(10, y, width - 80, 26),
                f"{ship.name} ({hull})",
                manager=self._ui_manager, container=panel
            )
            btn._ship_index = i

            remove_btn = UIButton(
                pygame.Rect(width - 65, y, 55, 26), "Remove",
                manager=self._ui_manager, container=panel
            )
            remove_btn._remove_ship_index = i

            self._ship_buttons.append((btn, remove_btn))
            y += 28

    def _build_right_panel(self, x, width, height):
        panel = UIPanel(
            relative_rect=pygame.Rect(x, 0, width, height),
            manager=self._ui_manager, object_id='#right_panel'
        )
        y = 10

        UILabel(pygame.Rect(10, y, width - 20, 28), "Available Designs",
                manager=self._ui_manager, container=panel)
        y += 35

        self._design_buttons = []
        for i, design in enumerate(self.available_designs):
            name = design.get('name', '?')
            ship_class = design.get('ship_class', '')
            btn = UIButton(
                pygame.Rect(10, y, width - 20, 28),
                f"{name} ({ship_class})",
                manager=self._ui_manager, container=panel
            )
            btn._design_index = i
            self._design_buttons.append(btn)
            y += 30

    def _build_bottom_bar(self, width, height, bar_height):
        panel = UIPanel(
            relative_rect=pygame.Rect(0, height - bar_height, width, bar_height),
            manager=self._ui_manager, object_id='#bottom_bar'
        )

        btn_w = 140
        spacing = 15
        buttons = [
            ("Start Battle", "_start_btn"),
            ("Start Headless", "_headless_btn"),
            ("Save Setup", "_save_btn"),
            ("Load Setup", "_load_btn"),
            ("Return", "_return_btn"),
        ]
        total = len(buttons) * btn_w + (len(buttons) - 1) * spacing
        x = (width - total) // 2

        for text, attr in buttons:
            btn = UIButton(
                pygame.Rect(x, 10, btn_w, 40), text,
                manager=self._ui_manager, container=panel
            )
            setattr(self, attr, btn)
            x += btn_w + spacing

    # === Event Handlers ===

    def _handle_button(self, event):
        element = event.ui_element

        # Fleet selection
        if hasattr(element, '_fleet_index'):
            self.active_fleet_index = element._fleet_index
            self._rebuild_ui()
            return

        # Design buttons — add ship
        if hasattr(element, '_design_index'):
            self._add_ship_from_design(element._design_index)
            return

        # Remove ship
        if hasattr(element, '_remove_ship_index'):
            self._remove_ship(element._remove_ship_index)
            return

        # Complex toggles
        if hasattr(element, '_complex_key'):
            key = element._complex_key
            self._complex_toggles[key] = not self._complex_toggles.get(key, False)
            self._rebuild_ui()
            return

        # Task force duplication
        if hasattr(element, '_dup_tf_index'):
            self._duplicate_task_force(element._dup_tf_index)
            return

        # Task force deletion
        if hasattr(element, '_del_tf_index'):
            self._delete_task_force(element._del_tf_index)
            return

        # Squadron duplication
        if hasattr(element, '_dup_sq_tf_index'):
            self._duplicate_squadron(element._dup_sq_tf_index, element._dup_sq_index)
            return

        # Squadron deletion
        if hasattr(element, '_del_sq_tf_index'):
            self._delete_squadron(element._del_sq_tf_index, element._del_sq_index)
            return

        # Action buttons
        if element == self._start_btn:
            self._start_battle(headless=False)
        elif element == self._headless_btn:
            self._start_battle(headless=True)
        elif element == self._save_btn:
            self._save_setup()
        elif element == self._load_btn:
            self._load_setup()
        elif element == self._return_btn:
            if self.scene_callback:
                self.scene_callback("return_to_menu")
        elif element == self._add_fleet_btn:
            side = self.state.get_side(self.active_side)
            side.create_fleet(f"Fleet {len(side.fleets) + 1}")
            self._rebuild_ui()
        elif element == self._remove_fleet_btn:
            side = self.state.get_side(self.active_side)
            if len(side.fleets) > 1 and self.active_fleet_index < len(side.fleets):
                side.fleets.pop(self.active_fleet_index)
                self.active_fleet_index = min(self.active_fleet_index, len(side.fleets) - 1)
                self._rebuild_ui()
        elif hasattr(self, '_add_tf_btn') and element == self._add_tf_btn:
            self._add_task_force()
        elif hasattr(self, '_add_sq_btn') and element == self._add_sq_btn:
            self._add_squadron()

    def _handle_dropdown(self, event):
        if event.ui_element == self._side_dropdown:
            self.active_side = 1 if "1" in event.text else 0
            self.active_fleet_index = 0
            self._rebuild_ui()
        elif hasattr(self, '_fleet_role_dropdown') and event.ui_element == self._fleet_role_dropdown:
            self._set_fleet_battle_role(event.text)

    # === Task Force / Squadron Management ===

    def _get_active_fleet(self):
        side = self.state.get_side(self.active_side)
        if self.active_fleet_index < len(side.fleets):
            return side.fleets[self.active_fleet_index]
        return None

    def _add_task_force(self):
        fleet = self._get_active_fleet()
        if not fleet:
            return
        tf_num = len(fleet.task_forces) + 1
        tf = TaskForce(name=f"Task Force {tf_num}")
        fleet.add_task_force(tf)
        self._rebuild_ui()

    def _add_squadron(self):
        fleet = self._get_active_fleet()
        if not fleet:
            return
        # Add to first task force, or create one
        if not fleet.task_forces:
            tf = TaskForce(name="Task Force 1")
            fleet.add_task_force(tf)
        tf = fleet.task_forces[0]
        sq_num = len(tf.squadrons) + 1
        sq = Squadron(name=f"Squadron {sq_num}")
        tf.add_squadron(sq)
        self._rebuild_ui()

    def _duplicate_task_force(self, tf_index: int):
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return

        original = fleet.task_forces[tf_index]
        registries = _get_registries()

        # Deep copy: create new TF with same structure
        new_tf = TaskForce(
            name=f"{original.name} (Copy)",
            policy=CombatPolicy(
                targeting=original.policy.targeting,
                movement=original.policy.movement,
                retreat=original.policy.retreat,
            ),
            battle_role=original.battle_role,
        )

        # Duplicate squadrons with ships
        for sq in original.squadrons:
            new_sq = Squadron(
                name=sq.name,
                policy=CombatPolicy(
                    targeting=sq.policy.targeting,
                    movement=sq.policy.movement,
                    retreat=sq.policy.retreat,
                ),
                battle_role=sq.battle_role,
                spatial_behavior=sq.spatial_behavior,
                spatial_behavior_params=dict(sq.spatial_behavior_params) if sq.spatial_behavior_params else None,
            )
            # Clone ships
            for ship in sq.ships:
                from game.strategy.data.ship_instance import ShipInstance
                cloned = ShipInstance.create(
                    design_data=ship.design_data,
                    owner_id=ship.owner_id,
                    name=ship.name,
                    registries=registries,
                )
                new_sq.add_ship(cloned)
                fleet.add_ship(cloned)  # Also add to fleet master list
            new_tf.add_squadron(new_sq)

        # Duplicate lone ships
        for ship in original.lone_ships:
            from game.strategy.data.ship_instance import ShipInstance
            cloned = ShipInstance.create(
                design_data=ship.design_data,
                owner_id=ship.owner_id,
                name=ship.name,
                registries=registries,
            )
            new_tf.add_lone_ship(cloned)
            fleet.add_ship(cloned)

        fleet.add_task_force(new_tf)
        self._rebuild_ui()

    def _delete_task_force(self, tf_index: int):
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        tf = fleet.task_forces[tf_index]
        # Remove ships from fleet master list
        for ship in tf.all_ships:
            fleet.remove_ship(ship)
        fleet.remove_task_force(tf)
        self._rebuild_ui()

    def _duplicate_squadron(self, tf_index: int, sq_index: int):
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        tf = fleet.task_forces[tf_index]
        if sq_index >= len(tf.squadrons):
            return

        original = tf.squadrons[sq_index]
        registries = _get_registries()

        new_sq = Squadron(
            name=f"{original.name} (Copy)",
            policy=CombatPolicy(
                targeting=original.policy.targeting,
                movement=original.policy.movement,
                retreat=original.policy.retreat,
            ),
            battle_role=original.battle_role,
            spatial_behavior=original.spatial_behavior,
        )
        for ship in original.ships:
            from game.strategy.data.ship_instance import ShipInstance
            cloned = ShipInstance.create(
                design_data=ship.design_data,
                owner_id=ship.owner_id,
                name=ship.name,
                registries=registries,
            )
            new_sq.add_ship(cloned)
            fleet.add_ship(cloned)

        tf.add_squadron(new_sq)
        self._rebuild_ui()

    def _delete_squadron(self, tf_index: int, sq_index: int):
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        tf = fleet.task_forces[tf_index]
        if sq_index >= len(tf.squadrons):
            return
        sq = tf.squadrons[sq_index]
        for ship in sq.all_ships:
            fleet.remove_ship(ship)
        tf.remove_squadron(sq)
        self._rebuild_ui()

    def _set_fleet_battle_role(self, role_name: str):
        fleet = self._get_active_fleet()
        if not fleet:
            return
        role = next((r for r, n in _BATTLE_ROLE_OPTIONS if n == role_name), BattleRole.MAIN_BODY)
        # Set on all task forces in this fleet
        for tf in fleet.task_forces:
            tf.battle_role = role

    # === Ship Management ===

    def _add_ship_from_design(self, design_index: int):
        if design_index >= len(self.available_designs):
            return
        side = self.state.get_side(self.active_side)
        if self.active_fleet_index >= len(side.fleets):
            return

        fleet = side.fleets[self.active_fleet_index]
        design_data = self.available_designs[design_index]
        registries = _get_registries()

        self.state.add_ship_from_design(fleet, design_data, registries=registries)
        self._rebuild_ui()

    def _remove_ship(self, ship_index: int):
        side = self.state.get_side(self.active_side)
        if self.active_fleet_index >= len(side.fleets):
            return
        fleet = side.fleets[self.active_fleet_index]
        if ship_index < len(fleet.ships):
            ship = fleet.ships[ship_index]
            fleet.remove_ship(ship)
            self._rebuild_ui()

    # === Battle Start ===

    def _start_battle(self, headless: bool = False):
        registries = _get_registries()

        team0_ships = []
        team1_ships = []

        # Convert each fleet — use deployment zones for multi-fleet
        from game.strategy.services.deployment_zone_calculator import DeploymentZoneCalculator

        for fi, fleet in enumerate(self.state.side_0.fleets):
            # Determine battle role for this fleet
            role = BattleRole.MAIN_BODY
            if fleet.task_forces:
                role = fleet.task_forces[0].battle_role or BattleRole.MAIN_BODY
            elif fi == 1:
                role = BattleRole.FLANKER_RIGHT
            elif fi == 2:
                role = BattleRole.FLANKER_LEFT

            positions = DeploymentZoneCalculator.compute_positions(
                ship_count=len(fleet.get_combat_capable_ships()),
                battle_role=role,
                team_id=0,
            )
            ships = fleet.battle.to_battle_ships(
                team_id=0, formation_positions=positions, registries=registries
            )
            # Apply complex modifiers to these ships
            self._apply_complex_modifiers(ships, side_id=0)
            team0_ships.extend(ships)

        for fi, fleet in enumerate(self.state.side_1.fleets):
            role = BattleRole.MAIN_BODY
            if fleet.task_forces:
                role = fleet.task_forces[0].battle_role or BattleRole.MAIN_BODY
            elif fi == 1:
                role = BattleRole.FLANKER_RIGHT
            elif fi == 2:
                role = BattleRole.FLANKER_LEFT

            positions = DeploymentZoneCalculator.compute_positions(
                ship_count=len(fleet.get_combat_capable_ships()),
                battle_role=role,
                team_id=1,
            )
            ships = fleet.battle.to_battle_ships(
                team_id=1, formation_positions=positions, registries=registries
            )
            self._apply_complex_modifiers(ships, side_id=1)
            team1_ships.extend(ships)

        if not team0_ships or not team1_ships:
            logger.warning("Cannot start battle: both sides need ships")
            return

        if self.scene_callback:
            action = "start_headless" if headless else "start_battle"
            self.scene_callback(action, team0=team0_ships, team1=team1_ships)

    def _apply_complex_modifiers(self, ships, side_id: int):
        """Apply toggled complex effects to ships."""
        # Collect active modifiers for this side
        shield_mult = 1.0
        damage_mult = 1.0
        shield_add = 0.0

        for scope in ("system", "sector"):
            complexes = _SYSTEM_SCOPE_COMPLEXES if scope == "system" else _SECTOR_SCOPE_COMPLEXES
            for design_id, display_name in complexes:
                key = (side_id, scope, design_id)
                if not self._complex_toggles.get(key, False):
                    continue

                # Apply based on design type
                if "shield_booster" in design_id:
                    shield_mult *= 1.25 if "system" in design_id else 1.50
                elif "shield_suppressor" in design_id:
                    shield_mult *= 0.75 if "system" in design_id else 0.50
                elif "shield_projector" in design_id:
                    shield_add += 50 if "system" in design_id else 100
                elif "damage_booster" in design_id:
                    damage_mult *= 1.25 if "system" in design_id else 1.50
                elif "damage_suppressor" in design_id:
                    damage_mult *= 0.75 if "system" in design_id else 0.50

        # Apply to ships
        for ship in ships:
            if shield_mult != 1.0:
                ship.max_shields = int(ship.max_shields * shield_mult)
                ship.current_shields = min(ship.current_shields, ship.max_shields)
            if shield_add > 0:
                ship.max_shields += int(shield_add)
                ship.current_shields += int(shield_add)
            if damage_mult != 1.0:
                ship.damage_output_mult = damage_mult

    # === Save/Load ===

    def _save_setup(self):
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.asksaveasfilename(
            initialdir=Paths.OUTPUT_DIR,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Battle Setup"
        )
        root.destroy()

        if filepath:
            data = self.state.to_dict()
            data['_complex_toggles'] = {
                f"{k[0]}_{k[1]}_{k[2]}": v
                for k, v in self._complex_toggles.items()
            }
            save_json(filepath, data)
            logger.info(f"Saved battle setup to {filepath}")

    def _load_setup(self):
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            initialdir=Paths.OUTPUT_DIR,
            filetypes=[("JSON files", "*.json")],
            title="Load Battle Setup"
        )
        root.destroy()

        if filepath:
            data = load_json(filepath, default=None)
            if data:
                registries = _get_registries()
                self.state = BattleSetupState.from_dict(data, registries=registries)
                # Restore complex toggles
                self._complex_toggles = {}
                for key_str, val in data.get('_complex_toggles', {}).items():
                    parts = key_str.split('_', 2)
                    if len(parts) == 3:
                        try:
                            self._complex_toggles[(int(parts[0]), parts[1], parts[2])] = val
                        except (ValueError, IndexError):
                            pass
                self.active_side = 0
                self.active_fleet_index = 0
                self._rebuild_ui()
                logger.info(f"Loaded battle setup from {filepath}")
