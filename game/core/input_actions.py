"""
Input action definitions and key binding data model for the hotkey system.

This module defines all bindable actions in the game and the data structures
for representing key bindings. It is pure data with no pygame dependency.

Usage:
    from game.core.input_actions import InputAction, KeyBinding, ACTION_DISPLAY_NAMES

    action = InputAction.FLEET_MOVE
    binding = KeyBinding(key="K_m", modifiers=frozenset())
    print(binding.display_text())  # "M"
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, FrozenSet, List, Optional


class InputAction(str, Enum):
    """All bindable input actions, organized by context.

    Values use dot-notation: "context.action_name".
    The context prefix is used for filtering which actions are active
    in a given screen/mode.
    """

    # --- Global (always active) ---
    GLOBAL_EXIT = "global.exit"
    GLOBAL_TOGGLE_PROFILER = "global.toggle_profiler"

    # --- Strategy screen ---
    STRATEGY_NEXT_TURN = "strategy.next_turn"
    STRATEGY_PREV_COLONY = "strategy.prev_colony"
    STRATEGY_NEXT_COLONY = "strategy.next_colony"
    STRATEGY_PREV_FLEET = "strategy.prev_fleet"
    STRATEGY_NEXT_FLEET = "strategy.next_fleet"
    STRATEGY_OPEN_PLANETS = "strategy.open_planets"
    STRATEGY_OPEN_EMPIRE = "strategy.open_empire"
    STRATEGY_OPEN_RESEARCH = "strategy.open_research"
    STRATEGY_OPEN_DESIGN = "strategy.open_design"
    STRATEGY_OPEN_BUILD_QUEUES = "strategy.open_build_queues"
    STRATEGY_SAVE_GAME = "strategy.save_game"
    STRATEGY_ZOOM_GALAXY = "strategy.zoom_galaxy"
    STRATEGY_ZOOM_SYSTEM = "strategy.zoom_system"
    STRATEGY_ZOOM_IN = "strategy.zoom_in"
    STRATEGY_ZOOM_OUT = "strategy.zoom_out"

    # --- Fleet commands ---
    FLEET_MOVE = "fleet.move"
    FLEET_JOIN = "fleet.join"
    FLEET_COLONIZE = "fleet.colonize"
    FLEET_TRANSFER = "fleet.transfer"
    FLEET_DROP_CARGO = "fleet.drop_cargo"
    FLEET_LOAD_CARGO = "fleet.load_cargo"
    FLEET_WARP = "fleet.warp"
    FLEET_CANCEL_MODE = "fleet.cancel_mode"

    # Superweapon commands
    FLEET_IMPLODE_PLANET = "fleet.implode_planet"
    FLEET_STELLERATE_STAR = "fleet.stellerate_star"
    FLEET_OPEN_WARP_POINT = "fleet.open_warp_point"
    FLEET_CLOSE_WARP_POINT = "fleet.close_warp_point"
    FLEET_CREATE_DYSON_SPHERE = "fleet.create_dyson_sphere"
    FLEET_SELF_DESTRUCT = "fleet.self_destruct"

    # --- Detail panel buttons ---
    DETAIL_PANEL_ORDERS = "detail_panel.orders"
    DETAIL_PANEL_FLEET_REPORT = "detail_panel.fleet_report"
    DETAIL_PANEL_BUILD = "detail_panel.build"
    DETAIL_PANEL_COLONIZE = "detail_panel.colonize"
    DETAIL_PANEL_BUILD_YARD = "detail_panel.build_yard"
    DETAIL_PANEL_PLANET_ORDERS = "detail_panel.planet_orders"  # PROJ-238

    # --- Planet commands ---
    PLANET_SHIELD_TOGGLE = "planet.shield_toggle"  # PROJ-238
    PLANET_GEOLOGIC_TOGGLE = "planet.geologic_toggle"
    PLANET_STELLAR_TOGGLE = "planet.stellar_toggle"
    PLANET_WARP_TOGGLE = "planet.warp_toggle"
    PLANET_ABILITIES_WINDOW = "planet.abilities_window"

    # --- Build queue screen ---
    BUILD_QUEUE_CLOSE = "build_queue.close"
    BUILD_QUEUE_ADD = "build_queue.add"
    BUILD_QUEUE_REMOVE = "build_queue.remove"
    BUILD_QUEUE_CAT_COMPLEXES = "build_queue.cat_complexes"
    BUILD_QUEUE_CAT_SHIPS = "build_queue.cat_ships"
    BUILD_QUEUE_CAT_SATELLITES = "build_queue.cat_satellites"
    BUILD_QUEUE_CAT_FIGHTERS = "build_queue.cat_fighters"

    # --- Fleet orders window ---
    FLEET_ORDERS_UNDO = "fleet_orders.undo"
    FLEET_ORDERS_CLEAR = "fleet_orders.clear"

    # --- Transfer dialog ---
    TRANSFER_CONFIRM = "transfer.confirm"
    TRANSFER_CANCEL = "transfer.cancel"


# Human-readable display names for the settings screen
ACTION_DISPLAY_NAMES: Dict[InputAction, str] = {
    # Global
    InputAction.GLOBAL_EXIT: "Exit Game",
    InputAction.GLOBAL_TOGGLE_PROFILER: "Toggle Profiler",
    # Strategy
    InputAction.STRATEGY_NEXT_TURN: "End Turn",
    InputAction.STRATEGY_PREV_COLONY: "Previous Colony",
    InputAction.STRATEGY_NEXT_COLONY: "Next Colony",
    InputAction.STRATEGY_PREV_FLEET: "Previous Fleet",
    InputAction.STRATEGY_NEXT_FLEET: "Next Fleet",
    InputAction.STRATEGY_OPEN_PLANETS: "Open Planets",
    InputAction.STRATEGY_OPEN_EMPIRE: "Open Empire",
    InputAction.STRATEGY_OPEN_RESEARCH: "Open Research",
    InputAction.STRATEGY_OPEN_DESIGN: "Open Design",
    InputAction.STRATEGY_OPEN_BUILD_QUEUES: "Open Build Yards",
    InputAction.STRATEGY_SAVE_GAME: "Save Game",
    InputAction.STRATEGY_ZOOM_GALAXY: "Zoom to Galaxy",
    InputAction.STRATEGY_ZOOM_SYSTEM: "Zoom to System",
    InputAction.STRATEGY_ZOOM_IN: "Zoom In",
    InputAction.STRATEGY_ZOOM_OUT: "Zoom Out",
    # Fleet
    InputAction.FLEET_MOVE: "Move Fleet",
    InputAction.FLEET_JOIN: "Join Fleet",
    InputAction.FLEET_COLONIZE: "Colonize",
    InputAction.FLEET_TRANSFER: "Transfer Cargo",
    InputAction.FLEET_DROP_CARGO: "Drop Cargo",
    InputAction.FLEET_LOAD_CARGO: "Load Cargo",
    InputAction.FLEET_WARP: "Warp Fleet",
    InputAction.FLEET_CANCEL_MODE: "Cancel Mode",
    InputAction.FLEET_IMPLODE_PLANET: "Destroy Planet",
    InputAction.FLEET_STELLERATE_STAR: "Destroy Star",
    InputAction.FLEET_OPEN_WARP_POINT: "Open Warp Point",
    InputAction.FLEET_CLOSE_WARP_POINT: "Close Warp Point",
    InputAction.FLEET_CREATE_DYSON_SPHERE: "Create Dyson Sphere",
    InputAction.FLEET_SELF_DESTRUCT: "Self-Destruct",
    # Detail panel
    InputAction.DETAIL_PANEL_ORDERS: "Fleet Orders",
    InputAction.DETAIL_PANEL_FLEET_REPORT: "Fleet Report",
    InputAction.DETAIL_PANEL_BUILD: "Build Fleet",
    InputAction.DETAIL_PANEL_COLONIZE: "Colonize Planet",
    InputAction.DETAIL_PANEL_BUILD_YARD: "Build Space Yard",
    InputAction.DETAIL_PANEL_PLANET_ORDERS: "Planet Orders",
    InputAction.PLANET_SHIELD_TOGGLE: "Toggle Shield",
    InputAction.PLANET_GEOLOGIC_TOGGLE: "Toggle Geologic Stabilizer",
    InputAction.PLANET_STELLAR_TOGGLE: "Toggle Stellar Stabilizer",
    InputAction.PLANET_WARP_TOGGLE: "Toggle Warp Stabilizer",
    InputAction.PLANET_ABILITIES_WINDOW: "Planet Abilities",
    # Build queue
    InputAction.BUILD_QUEUE_CLOSE: "Close Build Yard",
    InputAction.BUILD_QUEUE_ADD: "Add to Queue",
    InputAction.BUILD_QUEUE_REMOVE: "Remove from Queue",
    InputAction.BUILD_QUEUE_CAT_COMPLEXES: "Category: Complexes",
    InputAction.BUILD_QUEUE_CAT_SHIPS: "Category: Ships",
    InputAction.BUILD_QUEUE_CAT_SATELLITES: "Category: Satellites",
    InputAction.BUILD_QUEUE_CAT_FIGHTERS: "Category: Fighters",
    # Fleet orders
    InputAction.FLEET_ORDERS_UNDO: "Undo Order",
    InputAction.FLEET_ORDERS_CLEAR: "Clear Orders",
    # Transfer
    InputAction.TRANSFER_CONFIRM: "Confirm Transfer",
    InputAction.TRANSFER_CANCEL: "Cancel Transfer",
}

# Grouped actions for organized settings display
ACTION_GROUPS: Dict[str, List[InputAction]] = {
    "Global": [
        InputAction.GLOBAL_EXIT,
        InputAction.GLOBAL_TOGGLE_PROFILER,
    ],
    "Strategy": [
        InputAction.STRATEGY_NEXT_TURN,
        InputAction.STRATEGY_PREV_COLONY,
        InputAction.STRATEGY_NEXT_COLONY,
        InputAction.STRATEGY_PREV_FLEET,
        InputAction.STRATEGY_NEXT_FLEET,
        InputAction.STRATEGY_OPEN_PLANETS,
        InputAction.STRATEGY_OPEN_EMPIRE,
        InputAction.STRATEGY_OPEN_RESEARCH,
        InputAction.STRATEGY_OPEN_DESIGN,
        InputAction.STRATEGY_OPEN_BUILD_QUEUES,
        InputAction.STRATEGY_SAVE_GAME,
        InputAction.STRATEGY_ZOOM_GALAXY,
        InputAction.STRATEGY_ZOOM_SYSTEM,
        InputAction.STRATEGY_ZOOM_IN,
        InputAction.STRATEGY_ZOOM_OUT,
    ],
    "Fleet Commands": [
        InputAction.FLEET_MOVE,
        InputAction.FLEET_JOIN,
        InputAction.FLEET_COLONIZE,
        InputAction.FLEET_TRANSFER,
        InputAction.FLEET_DROP_CARGO,
        InputAction.FLEET_LOAD_CARGO,
        InputAction.FLEET_WARP,
        InputAction.FLEET_CANCEL_MODE,
        InputAction.FLEET_IMPLODE_PLANET,
        InputAction.FLEET_STELLERATE_STAR,
        InputAction.FLEET_OPEN_WARP_POINT,
        InputAction.FLEET_CLOSE_WARP_POINT,
        InputAction.FLEET_CREATE_DYSON_SPHERE,
        InputAction.FLEET_SELF_DESTRUCT,
    ],
    "Detail Panel": [
        InputAction.DETAIL_PANEL_ORDERS,
        InputAction.DETAIL_PANEL_FLEET_REPORT,
        InputAction.DETAIL_PANEL_BUILD,
        InputAction.DETAIL_PANEL_COLONIZE,
        InputAction.DETAIL_PANEL_BUILD_YARD,
        InputAction.DETAIL_PANEL_PLANET_ORDERS,
    ],
    "Planet": [
        InputAction.PLANET_SHIELD_TOGGLE,
        InputAction.PLANET_GEOLOGIC_TOGGLE,
        InputAction.PLANET_STELLAR_TOGGLE,
        InputAction.PLANET_WARP_TOGGLE,
        InputAction.PLANET_ABILITIES_WINDOW,
    ],
    "Build Yard": [
        InputAction.BUILD_QUEUE_CLOSE,
        InputAction.BUILD_QUEUE_ADD,
        InputAction.BUILD_QUEUE_REMOVE,
        InputAction.BUILD_QUEUE_CAT_COMPLEXES,
        InputAction.BUILD_QUEUE_CAT_SHIPS,
        InputAction.BUILD_QUEUE_CAT_SATELLITES,
        InputAction.BUILD_QUEUE_CAT_FIGHTERS,
    ],
    "Fleet Orders": [
        InputAction.FLEET_ORDERS_UNDO,
        InputAction.FLEET_ORDERS_CLEAR,
    ],
    "Transfer": [
        InputAction.TRANSFER_CONFIRM,
        InputAction.TRANSFER_CANCEL,
    ],
}


# Display names for special pygame key names
_SPECIAL_KEY_DISPLAY: Dict[str, str] = {
    "K_ESCAPE": "Esc",
    "K_SPACE": "Space",
    "K_RETURN": "Enter",
    "K_TAB": "Tab",
    "K_DELETE": "Del",
    "K_BACKSPACE": "Backspace",
    "K_INSERT": "Ins",
    "K_HOME": "Home",
    "K_END": "End",
    "K_PAGEUP": "PgUp",
    "K_PAGEDOWN": "PgDn",
    "K_UP": "Up",
    "K_DOWN": "Down",
    "K_LEFT": "Left",
    "K_RIGHT": "Right",
    "K_COMMA": ",",
    "K_PERIOD": ".",
    "K_LEFTBRACKET": "[",
    "K_RIGHTBRACKET": "]",
    "K_SEMICOLON": ";",
    "K_QUOTE": "'",
    "K_SLASH": "/",
    "K_BACKSLASH": "\\",
    "K_MINUS": "-",
    "K_EQUALS": "=",
    "K_KP_PLUS": "Numpad +",
    "K_KP_MINUS": "Numpad -",
    "K_KP_EQUALS": "Numpad =",
}

# Canonical modifier display order
_MODIFIER_ORDER = ("ctrl", "shift", "alt")


@dataclass(frozen=True)
class KeyBinding:
    """An immutable key binding: a key name plus optional modifier keys.

    Attributes:
        key: Pygame key constant name (e.g., "K_m", "K_F12").
        modifiers: Frozen set of modifier names ("shift", "ctrl", "alt").
    """

    key: str
    modifiers: FrozenSet[str]

    def display_text(self) -> str:
        """Return a human-readable string like 'Ctrl+Shift+M' or 'F12'."""
        parts: list[str] = []

        # Add modifiers in canonical order
        for mod in _MODIFIER_ORDER:
            if mod in self.modifiers:
                parts.append(mod.capitalize())

        # Add key display name
        parts.append(self._key_display_name())

        return "+".join(parts)

    def _key_display_name(self) -> str:
        """Convert a pygame key name to a readable display string."""
        if self.key in _SPECIAL_KEY_DISPLAY:
            return _SPECIAL_KEY_DISPLAY[self.key]

        # Function keys: K_F1 -> F1
        if self.key.startswith("K_F") and self.key[3:].isdigit():
            return self.key[2:]  # "F12"

        # Letter keys: K_m -> M, K_a -> A
        if self.key.startswith("K_") and len(self.key) == 3:
            return self.key[2:].upper()

        # Fallback: strip K_ prefix
        return self.key.replace("K_", "")

    @classmethod
    def from_dict(cls, data: dict) -> Optional["KeyBinding"]:
        """Create a KeyBinding from a JSON-style dict.

        Args:
            data: Dict with "key" and optional "modifiers" fields.
                  Empty dict or missing "key" returns None (unbound action).

        Returns:
            KeyBinding instance, or None if the action is unbound.
        """
        if not data or "key" not in data:
            return None
        return cls(
            key=data["key"],
            modifiers=frozenset(data.get("modifiers", [])),
        )

    def to_dict(self) -> dict:
        """Serialize to a JSON-compatible dict.

        Returns:
            Dict with "key" and "modifiers" fields.
        """
        return {
            "key": self.key,
            "modifiers": sorted(self.modifiers),
        }
