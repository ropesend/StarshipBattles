"""PROJ-282 Phase 6: `BattleSetupController`.

Owns every mutation on `BattleSetupState`. Lifts:
  - Fleet/Ship/TaskForce/Squadron CRUD
  - Complex toggles (system/sector)
  - End-condition settings (tick_limit, destroyed/derelict/mass-ratio toggles)
  - Save/load (tkinter file dialog)
  - Battle launch (spec compile + scene_callback fire)

out of `FleetBattleSetupScreen`. The controller is pygame-free — save/load
uses tkinter (fine, it's stdlib) and battle launch imports the spec
compiler (core layer, not UI).

Pattern: the input handler calls controller methods on button/dropdown
events. After each mutation the controller fires `on_change()` — the
screen passes `self._rebuild_ui` there, so the pygame_gui tree rebuilds
without the controller itself knowing about pygame.

Phase 7 will extract the duplicated TF/SQ ship-cloning loops into a
`FleetHierarchyEditor`; for this phase, the duplication sits inline on
the controller and matches the pre-extraction screen behavior exactly.
"""
from __future__ import annotations

import logging
import os
from typing import Any, Callable, Optional

from game.core.json_utils import load_json, save_json
from game.core.paths import Paths
from game.strategy.data.fleet_hierarchy import BattleRole
from game.ui.screens.battle_setup.fleet_hierarchy_editor import FleetHierarchyEditor
from game.ui.screens.battle_setup_state import BattleSetupState
from game.ui.screens.battle_setup.view_model import BattleSetupViewModel

logger = logging.getLogger(__name__)


def _get_registries():
    """Pull GameRegistries from the default provider.

    Duplicated verbatim from `battle_setup_screen.py` — both callsites
    converge here after Phase 8 deletes the screen-side copy. Returns
    None if the provider isn't initialized (tests that don't load data).
    """
    try:
        from game.core.registry import GameRegistries, get_default_registry_provider
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


class BattleSetupController:
    """Mutator for `BattleSetupState` + orchestrator for battle launch.

    Does NOT own pygame_gui or the `UIManager`. Mutations are pushed
    through this class; when something changes, `self._on_change()` is
    invoked so the screen (or whichever owner) can rebuild its UI.
    """

    def __init__(
        self,
        state: BattleSetupState,
        view_model: BattleSetupViewModel,
        *,
        scene_callback: Optional[Callable[..., Any]] = None,
        on_change: Optional[Callable[[], None]] = None,
    ) -> None:
        self._state = state
        self._view_model = view_model
        self._scene_callback = scene_callback
        self._on_change = on_change or (lambda: None)

        # End-condition settings (moved off screen — they were being reset
        # by a Phase 3 dead-code regression every time `available_designs`
        # was assigned). These are part of the battle setup's configuration
        # surface, sized intentionally to match the previous screen defaults.
        self.tick_limit: int = 100000
        self.end_all_destroyed: bool = True
        self.end_all_derelict: bool = False
        self.end_mass_ratio: bool = False
        self.mass_ratio_threshold: float = 0.10

    # === Lifecycle ===

    def start(self, preserve_teams: bool = False) -> None:
        """Reset state (or not) and prepare for UI display.

        Mirrors the pre-Phase-6 `FleetBattleSetupScreen.start` behavior.
        """
        if not preserve_teams:
            self._state.clear()
            self._state.side_0.create_fleet("Fleet Alpha")
            self._state.side_1.create_fleet("Fleet Beta")
            self._view_model.active_side = 0
            self._view_model.active_fleet_index = 0

        self.scan_designs()
        self._on_change()

    def scan_designs(self) -> None:
        """Populate `view_model.available_designs` from the starter-designs dir."""
        designs = []
        designs_dir = Paths.STARTER_DESIGNS_DIR
        if os.path.exists(designs_dir):
            for filename in sorted(os.listdir(designs_dir)):
                if not filename.endswith('.json'):
                    continue
                filepath = os.path.join(designs_dir, filename)
                try:
                    data = load_json(filepath, default=None)
                    if data and data.get('vehicle_type') == 'Ship':
                        data['_filepath'] = filepath
                        data['_design_id'] = filename.replace('.json', '')
                        designs.append(data)
                except Exception as e:
                    logger.warning(f"Failed to load design {filename}: {e}")
        self._view_model.available_designs = designs

    # === Side / Fleet ===

    def set_active_side(self, side_id: int) -> None:
        self._view_model.active_side = side_id
        self._view_model.active_fleet_index = 0
        self._on_change()

    def add_side(self) -> None:
        """Append a new empty side and switch to it.

        PROJ-282 Phase 11: surfaces `BattleSetupState.add_side()` through
        the controller. No-op (with a warning) at `MAX_SIDES` so the UI
        button's bounds handling is safe even if the disabled state
        misfires.
        """
        try:
            self._state.add_side()
        except ValueError:
            logger.warning(
                "Cannot add side: already at maximum (%d).", len(self._state.sides),
            )
            return
        self._view_model.active_side = len(self._state.sides) - 1
        self._view_model.active_fleet_index = 0
        self._view_model.clear_selection()
        self._on_change()

    def remove_side(self, index: int) -> None:
        """Remove the side at `index`. No-op at `MIN_SIDES` or out-of-range.

        PROJ-282 Phase 11: surfaces `BattleSetupState.remove_side(index)`.
        Reconciles `view_model.active_side` when the removal shifts the
        active side's index or removes the active side outright.
        """
        if index < 0 or index >= len(self._state.sides):
            return
        try:
            self._state.remove_side(index)
        except ValueError:
            # At MIN_SIDES — no-op.
            return

        # Reconcile active_side.
        current_active = self._view_model.active_side
        if current_active == index:
            # Removed the active side: clamp to a valid neighbor.
            self._view_model.active_side = min(
                current_active, len(self._state.sides) - 1
            )
        elif current_active > index:
            # Removed a side before the active one: active's index shifts
            # down by 1 to track the same side.
            self._view_model.active_side = current_active - 1

        self._view_model.active_fleet_index = 0
        self._view_model.clear_selection()
        self._on_change()

    def add_fleet(self) -> None:
        side = self._state.get_side(self._view_model.active_side)
        side.create_fleet(f"Fleet {len(side.fleets) + 1}")
        self._on_change()

    def remove_fleet(self) -> None:
        """Remove the active fleet. Preserves the one-fleet minimum."""
        side = self._state.get_side(self._view_model.active_side)
        if len(side.fleets) > 1 and self._view_model.active_fleet_index < len(side.fleets):
            side.fleets.pop(self._view_model.active_fleet_index)
            self._view_model.active_fleet_index = min(
                self._view_model.active_fleet_index, len(side.fleets) - 1
            )
            self._on_change()

    def _get_active_fleet(self):
        """Return the currently-active fleet, or None."""
        side = self._state.get_side(self._view_model.active_side)
        if self._view_model.active_fleet_index < len(side.fleets):
            return side.fleets[self._view_model.active_fleet_index]
        return None

    # === Ship CRUD ===

    def add_ship_from_design(self, design_index: int) -> None:
        if design_index >= len(self._view_model.available_designs):
            return
        side = self._state.get_side(self._view_model.active_side)
        if self._view_model.active_fleet_index >= len(side.fleets):
            return

        fleet = side.fleets[self._view_model.active_fleet_index]
        design_data = self._view_model.available_designs[design_index]
        registries = _get_registries()

        ship = self._state.add_ship_from_design(fleet, design_data, registries=registries)

        # Also assign to the currently-selected TF or SQ, if any.
        tf_i = self._view_model.selected_tf_index
        sq_i = self._view_model.selected_sq_index
        if tf_i is not None and tf_i < len(fleet.task_forces):
            tf = fleet.task_forces[tf_i]
            if sq_i is not None and sq_i < len(tf.squadrons):
                tf.squadrons[sq_i].add_ship(ship)
            else:
                tf.add_lone_ship(ship)

        self._on_change()

    def remove_ship(self, ship_index: int) -> None:
        side = self._state.get_side(self._view_model.active_side)
        if self._view_model.active_fleet_index >= len(side.fleets):
            return
        fleet = side.fleets[self._view_model.active_fleet_index]
        if ship_index < len(fleet.ships):
            fleet.remove_ship(fleet.ships[ship_index])
            self._on_change()

    # === TaskForce / Squadron CRUD ===
    # All delegate to `FleetHierarchyEditor` (PROJ-282 Phase 7) — the editor
    # owns the ship-cloning logic that was duplicated between
    # `duplicate_task_force` and `duplicate_squadron`.

    def add_task_force(self) -> None:
        fleet = self._get_active_fleet()
        if not fleet:
            return
        FleetHierarchyEditor.create_task_force(fleet)
        self._on_change()

    def add_squadron(self) -> None:
        fleet = self._get_active_fleet()
        if not fleet:
            return
        if not fleet.task_forces:
            FleetHierarchyEditor.create_task_force(fleet, "Task Force 1")
        FleetHierarchyEditor.create_squadron(fleet.task_forces[0])
        self._on_change()

    def duplicate_task_force(self, tf_index: int) -> None:
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        FleetHierarchyEditor.duplicate_task_force(fleet, fleet.task_forces[tf_index])
        self._on_change()

    def delete_task_force(self, tf_index: int) -> None:
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        FleetHierarchyEditor.delete_task_force(fleet, fleet.task_forces[tf_index])
        self._on_change()

    def duplicate_squadron(self, tf_index: int, sq_index: int) -> None:
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        tf = fleet.task_forces[tf_index]
        if sq_index >= len(tf.squadrons):
            return
        FleetHierarchyEditor.duplicate_squadron(fleet, tf, tf.squadrons[sq_index])
        self._on_change()

    def delete_squadron(self, tf_index: int, sq_index: int) -> None:
        fleet = self._get_active_fleet()
        if not fleet or tf_index >= len(fleet.task_forces):
            return
        tf = fleet.task_forces[tf_index]
        if sq_index >= len(tf.squadrons):
            return
        FleetHierarchyEditor.delete_squadron(fleet, tf, tf.squadrons[sq_index])
        self._on_change()

    # === Policies ===

    def set_fleet_battle_role(self, role_name: str) -> None:
        from game.ui.screens.battle_setup.constants import _BATTLE_ROLE_OPTIONS
        fleet = self._get_active_fleet()
        if not fleet:
            return
        role = next(
            (r for r, n in _BATTLE_ROLE_OPTIONS if n == role_name),
            BattleRole.MAIN_BODY,
        )
        for tf in fleet.task_forces:
            tf.battle_role = role

    def set_ship_policy(self, key: str, display_name: str, options_list) -> None:
        """Set targeting/movement policy on the currently-selected ship."""
        fleet = self._get_active_fleet()
        if not fleet or self._view_model.selected_ship_index is None:
            return
        if self._view_model.selected_ship_index >= len(fleet.ships):
            return

        ship = fleet.ships[self._view_model.selected_ship_index]

        value = None
        for pid, pname in options_list:
            if pname == display_name:
                value = pid
                break

        if value is not None:
            ship.design_data[key] = value
        elif key in ship.design_data:
            del ship.design_data[key]

    def set_selected_policy(self, axis: str, display_name: str) -> None:
        """Set a policy axis on the currently-selected TF or SQ."""
        from game.ui.screens.battle_setup.constants import (
            _MOVEMENT_OPTIONS,
            _TARGETING_OPTIONS,
        )
        fleet = self._get_active_fleet()
        if not fleet:
            return

        selected_node = None
        tf_i = self._view_model.selected_tf_index
        sq_i = self._view_model.selected_sq_index
        if tf_i is not None and tf_i < len(fleet.task_forces):
            tf = fleet.task_forces[tf_i]
            if sq_i is not None and sq_i < len(tf.squadrons):
                selected_node = tf.squadrons[sq_i]
            else:
                selected_node = tf

        if not selected_node:
            return

        value = None
        if axis == "targeting":
            value = next((tid for tid, n in _TARGETING_OPTIONS if n == display_name), None)
        elif axis == "movement":
            value = next((mid for mid, n in _MOVEMENT_OPTIONS if n == display_name), None)

        setattr(selected_node.policy, axis, value)

    # === Complex toggles ===

    def _toggle_dict_for(self, side_id: int, scope: str) -> dict:
        side = self._state.sides[side_id]
        if scope == "system":
            return side.system_complex_toggles
        if scope == "sector":
            return side.sector_complex_toggles
        raise ValueError(f"unknown complex scope: {scope!r}")

    def get_complex_toggle(self, side_id: int, scope: str, design_id: str) -> bool:
        return self._toggle_dict_for(side_id, scope).get(design_id, False)

    def toggle_complex(self, side_id: int, scope: str, design_id: str) -> None:
        current = self.get_complex_toggle(side_id, scope, design_id)
        self._toggle_dict_for(side_id, scope)[design_id] = not current
        self._on_change()

    # === End-condition toggles ===

    def toggle_end_destroyed(self) -> None:
        self.end_all_destroyed = not self.end_all_destroyed
        self._on_change()

    def toggle_end_derelict(self) -> None:
        self.end_all_derelict = not self.end_all_derelict
        self._on_change()

    def toggle_end_mass_ratio(self) -> None:
        self.end_mass_ratio = not self.end_mass_ratio
        self._on_change()

    def set_tick_limit_from_text(self, text: str) -> None:
        """Parse a tick-limit string from the left panel's text entry.

        Clamps to a 100 minimum; ignores non-integers (keeps current value).
        """
        try:
            self.tick_limit = max(100, int(text))
        except (ValueError, TypeError):
            pass

    def _build_end_condition(self):
        """Compose an `IEndCondition` from the current toggle settings."""
        from game.simulation.systems.battle_end_conditions import (
            AnyCondition,
            MassRatioCondition,
            TeamEliminatedCondition,
            TickLimitCondition,
        )
        conditions = [TickLimitCondition(self.tick_limit)]
        if self.end_all_destroyed:
            conditions.append(TeamEliminatedCondition(check_derelict=False))
        if self.end_all_derelict:
            conditions.append(TeamEliminatedCondition(check_derelict=True))
        if self.end_mass_ratio:
            conditions.append(MassRatioCondition(threshold=self.mass_ratio_threshold))
        return AnyCondition(conditions)

    # === Sync + battle launch ===

    def _sync_complex_toggles_to_state(self) -> None:
        """Project per-side toggle dicts onto the materialized `*_complexes` lists.

        Spec compiler reads `side.system_complexes: List[Dict]`; toggle dicts
        are the source of truth. Iterates all sides (PROJ-275 N-team) — the
        pre-Phase-2 hardcoded sides-0/1 projection silently dropped toggles
        for sides 2-7.
        """
        from game.ui.screens.battle_setup.constants import (
            _SECTOR_SCOPE_COMPLEXES,
            _SYSTEM_SCOPE_COMPLEXES,
        )
        display_name_by_design_id = {
            "system": {d: n for d, n in _SYSTEM_SCOPE_COMPLEXES},
            "sector": {d: n for d, n in _SECTOR_SCOPE_COMPLEXES},
        }

        def _materialize(toggles: dict, scope: str) -> list:
            lookup = display_name_by_design_id[scope]
            return [
                {"design_id": design_id, "display_name": lookup.get(design_id, design_id)}
                for design_id, enabled in toggles.items()
                if enabled
            ]

        for side in self._state.sides:
            side.system_complexes = _materialize(side.system_complex_toggles, "system")
            side.sector_complexes = _materialize(side.sector_complex_toggles, "sector")

    def start_battle(self, headless: bool = False) -> None:
        """Compile a `BattleSpec` from state and fire the scene callback.

        Guard: both sides must have ≥1 ship. (Screen's original guard
        hardcoded side_0/side_1 here — preserved as-is because this is the
        Battle Setup flow which requires a 2-team adversarial default. The
        N-team extension is Phase 4+ UI work.)
        """
        from game.ui.screens.battle_setup.spec_compiler import build_manual_battle_spec

        self._sync_complex_toggles_to_state()

        def _total_ships(side) -> int:
            return sum(len(fleet.ships) for fleet in side.fleets)

        if _total_ships(self._state.side_0) == 0 or _total_ships(self._state.side_1) == 0:
            logger.warning("Cannot start battle: both sides need ships")
            return

        registries = _get_registries()
        end_condition = self._build_end_condition()
        spec = build_manual_battle_spec(
            self._state,
            registries,
            end_condition=end_condition,
        )

        if self._scene_callback:
            action = "start_headless" if headless else "start_battle"
            self._scene_callback(action, spec=spec)

    def return_to_menu(self) -> None:
        if self._scene_callback:
            self._scene_callback("return_to_menu")

    # === Save / load ===

    def save_setup(self) -> None:
        """Prompt for a filepath and save the current setup to JSON."""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.asksaveasfilename(
            initialdir=Paths.OUTPUT_DIR,
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Save Battle Setup",
        )
        root.destroy()

        if filepath:
            self._save_to_path(filepath)

    def _save_to_path(self, filepath: str) -> None:
        """Write current state to a specific path (test-friendly hook)."""
        save_json(filepath, self._state.to_dict())
        logger.info(f"Saved battle setup to {filepath}")

    def load_setup(self) -> None:
        """Prompt for a filepath and load a setup from JSON."""
        import tkinter as tk
        from tkinter import filedialog

        root = tk.Tk()
        root.withdraw()
        filepath = filedialog.askopenfilename(
            initialdir=Paths.OUTPUT_DIR,
            filetypes=[("JSON files", "*.json")],
            title="Load Battle Setup",
        )
        root.destroy()

        if filepath:
            self._load_from_path(filepath)

    def _load_from_path(self, filepath: str) -> None:
        """Load state from a specific path (test-friendly hook).

        Replaces `self._state` entirely — subsequent mutations land on the
        freshly-loaded instance. Legacy `_complex_toggles` top-level keys
        (pre-Phase-2) are migrated onto per-side toggle dicts.
        """
        data = load_json(filepath, default=None)
        if not data:
            return

        registries = _get_registries()
        self._state = BattleSetupState.from_dict(data, registries=registries)

        # Legacy toggle migration.
        legacy = data.get('_complex_toggles', {}) or {}
        for key_str, val in legacy.items():
            parts = key_str.split('_', 2)
            if len(parts) != 3:
                continue
            try:
                side_id = int(parts[0])
            except ValueError:
                continue
            scope = parts[1]
            design_id = parts[2]
            if side_id < 0 or side_id >= len(self._state.sides):
                continue
            if scope == "system":
                self._state.sides[side_id].system_complex_toggles[design_id] = bool(val)
            elif scope == "sector":
                self._state.sides[side_id].sector_complex_toggles[design_id] = bool(val)

        self._view_model.active_side = 0
        self._view_model.active_fleet_index = 0
        self._on_change()
        logger.info(f"Loaded battle setup from {filepath}")

    # === State access ===

    @property
    def state(self) -> BattleSetupState:
        """Read-only access to the current state (may have been replaced by load_setup)."""
        return self._state
