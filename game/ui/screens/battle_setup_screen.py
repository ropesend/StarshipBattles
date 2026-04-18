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

from game.core.paths import Paths
from game.core.json_utils import load_json, save_json
from game.ui.screens.battle_setup_state import BattleSetupState
from game.ui.screens.battle_setup.view_model import BattleSetupViewModel
from game.ui.screens.battle_setup.renderer import BattleSetupRenderer
from game.ui.screens.battle_setup.input_handler import BattleSetupInputHandler
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
        # PROJ-282 Phase 3: view state (selection indices, scanned designs)
        # lives on `BattleSetupViewModel`. Screen exposes property shims
        # so the existing ~60 `self.active_side` / `self.selected_tf_index`
        # reads/writes continue to work during the transition. Phase 8
        # drops the shims when the screen is rewritten as a thin shell.
        self.view_model = BattleSetupViewModel()

        # PROJ-282 Phase 4: panel construction moved to
        # `game.ui.screens.battle_setup.renderer.BattleSetupRenderer` +
        # `panels/{left,center,right}_panel.py`. `_rebuild_ui` delegates
        # to `self.renderer.rebuild(self)`.
        self.renderer = BattleSetupRenderer()

        # PROJ-282 Phase 5: pygame_gui event dispatch moved to
        # `BattleSetupInputHandler`. `handle_event` routes to it.
        self.input_handler = BattleSetupInputHandler(self)

        self._ui_manager = None
        self._panels_built = False

    # === View-model property shims (PROJ-282 Phase 3) ===

    @property
    def active_side(self) -> int:
        return self.view_model.active_side

    @active_side.setter
    def active_side(self, value: int) -> None:
        self.view_model.active_side = value

    @property
    def active_fleet_index(self) -> int:
        return self.view_model.active_fleet_index

    @active_fleet_index.setter
    def active_fleet_index(self, value: int) -> None:
        self.view_model.active_fleet_index = value

    @property
    def selected_tf_index(self):
        return self.view_model.selected_tf_index

    @selected_tf_index.setter
    def selected_tf_index(self, value) -> None:
        self.view_model.selected_tf_index = value

    @property
    def selected_sq_index(self):
        return self.view_model.selected_sq_index

    @selected_sq_index.setter
    def selected_sq_index(self, value) -> None:
        self.view_model.selected_sq_index = value

    @property
    def selected_ship_index(self):
        return self.view_model.selected_ship_index

    @selected_ship_index.setter
    def selected_ship_index(self, value) -> None:
        self.view_model.selected_ship_index = value

    @property
    def available_designs(self) -> list:
        return self.view_model.available_designs

    @available_designs.setter
    def available_designs(self, value: list) -> None:
        self.view_model.available_designs = value

        # End condition settings
        self.tick_limit = 100000
        self.end_all_destroyed = True
        self.end_all_derelict = False
        self.end_mass_ratio = False
        self.mass_ratio_threshold = 0.10

        # PROJ-282 Phase 2: complex toggle state lives on `BattleSetupSide`
        # (system_complex_toggles / sector_complex_toggles dicts). No
        # screen-level dict. Toggle reads go through `_get_toggle(...)`;
        # writes through `_set_toggle(...)`.

    # === IScene Protocol ===

    def handle_event(self, event):
        if self._ui_manager:
            self._ui_manager.process_events(event)
        # PROJ-282 Phase 5: dispatch delegated to BattleSetupInputHandler.
        self.input_handler.handle_event(event)

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
            # PROJ-282 Phase 2: toggles live on state; `clear()` resets them.

        self._scan_designs()
        self._rebuild_ui()

    # === Complex toggle accessors (PROJ-282 Phase 2) ===

    def _toggle_dict_for(self, side_id: int, scope: str) -> dict:
        """Return the per-side, per-scope toggle dict on state."""
        side = self.state.sides[side_id]
        if scope == "system":
            return side.system_complex_toggles
        if scope == "sector":
            return side.sector_complex_toggles
        raise ValueError(f"unknown complex scope: {scope!r}")

    def _get_toggle(self, side_id: int, scope: str, design_id: str) -> bool:
        return self._toggle_dict_for(side_id, scope).get(design_id, False)

    def _set_toggle(self, side_id: int, scope: str, design_id: str, enabled: bool) -> None:
        self._toggle_dict_for(side_id, scope)[design_id] = enabled

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
        """Delegate panel construction to `BattleSetupRenderer` (PROJ-282 Phase 4)."""
        self.renderer.rebuild(self)

    # _build_left_panel moved to game/ui/screens/battle_setup/panels/left_panel.py (PROJ-282 Phase 4)

    # _build_center_panel + _build_policy_controls + _build_right_panel + _build_bottom_bar
    # all moved to game/ui/screens/battle_setup/{renderer.py,panels/*_panel.py} (PROJ-282 Phase 4)

    # === Event Handlers ===

    # _handle_button + _handle_dropdown moved to
    # game/ui/screens/battle_setup/input_handler.py (PROJ-282 Phase 5)

    def _set_ship_policy(self, key: str, display_name: str, options_list):
        """Set a targeting or movement policy on the selected ship's design_data."""
        fleet = self._get_active_fleet()
        if not fleet or self.selected_ship_index is None:
            return
        if self.selected_ship_index >= len(fleet.ships):
            return

        ship = fleet.ships[self.selected_ship_index]

        # Map display name to policy ID; "(default)" clears the override
        value = None
        for pid, pname in options_list:
            if pname == display_name:
                value = pid
                break

        if value is not None:
            ship.design_data[key] = value
        elif key in ship.design_data:
            del ship.design_data[key]

    def _set_selected_policy(self, axis: str, display_name: str):
        """Set a policy axis on the selected TF or SQ."""
        fleet = self._get_active_fleet()
        if not fleet:
            return

        selected_node = None
        if self.selected_tf_index is not None and self.selected_tf_index < len(fleet.task_forces):
            tf = fleet.task_forces[self.selected_tf_index]
            if self.selected_sq_index is not None and self.selected_sq_index < len(tf.squadrons):
                selected_node = tf.squadrons[self.selected_sq_index]
            else:
                selected_node = tf

        if not selected_node:
            return

        # Map display name to policy ID
        value = None  # "(inherit)" maps to None
        if axis == "targeting":
            value = next((tid for tid, n in _TARGETING_OPTIONS if n == display_name), None)
        elif axis == "movement":
            value = next((mid for mid, n in _MOVEMENT_OPTIONS if n == display_name), None)

        setattr(selected_node.policy, axis, value)

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

        # Create the ship instance and add to fleet master list
        ship = self.state.add_ship_from_design(fleet, design_data, registries=registries)

        # Also assign to the selected task force/squadron
        if self.selected_tf_index is not None and self.selected_tf_index < len(fleet.task_forces):
            tf = fleet.task_forces[self.selected_tf_index]
            if self.selected_sq_index is not None and self.selected_sq_index < len(tf.squadrons):
                # Add to selected squadron
                tf.squadrons[self.selected_sq_index].add_ship(ship)
            else:
                # Add as lone ship in the task force
                tf.add_lone_ship(ship)

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
        """Compile a BattleSpec from the current UI state and hand it to the app.

        PROJ-270 Phase 3: the inline `fleet.battle.to_battle_ships(...)` +
        `DeploymentZoneCalculator` materialization is replaced by the
        spec compiler `build_manual_battle_spec` (which uses
        `FormationResolver` for positioning). Complex toggles flow into
        `spec.modifier_stack` via `_sync_complex_toggles_to_state`.
        """
        from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec

        registries = _get_registries()

        # Sync `_complex_toggles` dict onto `BattleSetupSide.system_complexes` /
        # `sector_complexes` so the compiler can translate toggled complexes
        # into `ModifierStack` entries.
        self._sync_complex_toggles_to_state()

        # Guard: both sides must have at least one ship.
        def _total_ships(side) -> int:
            return sum(len(fleet.ships) for fleet in side.fleets)

        if _total_ships(self.state.side_0) == 0 or _total_ships(self.state.side_1) == 0:
            logger.warning("Cannot start battle: both sides need ships")
            return

        end_condition = self._build_end_condition()
        spec = build_manual_battle_spec(
            self.state,
            registries,
            end_condition=end_condition,
        )

        if self.scene_callback:
            action = "start_headless" if headless else "start_battle"
            self.scene_callback(action, spec=spec)

    def _build_end_condition(self):
        """Build composite end condition from UI settings."""
        from game.simulation.systems.battle_end_conditions import (
            TickLimitCondition, TeamEliminatedCondition,
            MassRatioCondition, AnyCondition,
        )

        # Read tick limit from text entry
        try:
            tick_text = self._tick_limit_entry.get_text() if hasattr(self, '_tick_limit_entry') else str(self.tick_limit)
            self.tick_limit = max(100, int(tick_text))
        except (ValueError, AttributeError):
            pass  # Keep current value

        conditions = [TickLimitCondition(self.tick_limit)]

        if self.end_all_destroyed:
            conditions.append(TeamEliminatedCondition(check_derelict=False))

        if self.end_all_derelict:
            conditions.append(TeamEliminatedCondition(check_derelict=True))

        if self.end_mass_ratio:
            conditions.append(MassRatioCondition(threshold=self.mass_ratio_threshold))

        return AnyCondition(conditions)

    def _sync_complex_toggles_to_state(self) -> None:
        """Project each side's `*_complex_toggles` dict onto `*_complexes` list.

        PROJ-282 Phase 2: source of truth is now `BattleSetupSide.system_complex_toggles`
        / `sector_complex_toggles` (per-side dicts, not a screen-level dict).
        The spec compiler still reads `side.system_complexes: List[Dict]`, so
        we rebuild those materialized lists from the toggle dicts at launch
        time. Iterates ALL sides (PROJ-275 N-team) — the old hardcoded
        `side_0` / `side_1` projection silently dropped toggles for sides 2-7.
        """
        display_name_by_design_id: dict = {
            "system": {d: n for d, n in _SYSTEM_SCOPE_COMPLEXES},
            "sector": {d: n for d, n in _SECTOR_SCOPE_COMPLEXES},
        }

        def _materialize(toggles: dict, scope: str) -> list:
            lookup = display_name_by_design_id[scope]
            return [
                {
                    "design_id": design_id,
                    "display_name": lookup.get(design_id, design_id),
                }
                for design_id, enabled in toggles.items()
                if enabled
            ]

        for side in self.state.sides:
            side.system_complexes = _materialize(side.system_complex_toggles, "system")
            side.sector_complexes = _materialize(side.sector_complex_toggles, "sector")

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
            # PROJ-282 Phase 2: state.to_dict() now carries the per-side
            # `system_complex_toggles` / `sector_complex_toggles`; no need
            # for a top-level `_complex_toggles` mirror.
            data = self.state.to_dict()
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
                # PROJ-282 Phase 2: legacy-save migration — if an old save
                # carries a top-level `_complex_toggles` dict with flat
                # string keys `f"{side_id}_{scope}_{design_id}"`, project
                # onto the per-side toggle dicts so users don't lose state
                # across the upgrade. New saves don't emit this key.
                legacy = data.get('_complex_toggles', {})
                for key_str, val in legacy.items():
                    parts = key_str.split('_', 2)
                    if len(parts) != 3:
                        continue
                    try:
                        side_id = int(parts[0])
                        scope = parts[1]
                        design_id = parts[2]
                    except ValueError:
                        continue
                    if side_id < 0 or side_id >= len(self.state.sides):
                        continue
                    if scope == "system":
                        self.state.sides[side_id].system_complex_toggles[design_id] = bool(val)
                    elif scope == "sector":
                        self.state.sides[side_id].sector_complex_toggles[design_id] = bool(val)
                self.active_side = 0
                self.active_fleet_index = 0
                self._rebuild_ui()
                logger.info(f"Loaded battle setup from {filepath}")
