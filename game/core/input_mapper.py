"""
Centralized input mapping service for the keybinding system.

Resolves pygame KEYDOWN events to InputAction values using a data-driven
binding table loaded from JSON. Supports user overrides, conflict detection,
and save/reset operations.

Usage:
    from game.core.input_mapper import InputMapper
    from game.core.input_actions import InputAction
    from game.core.paths import Paths

    mapper = InputMapper()
    mapper.load(Paths.DEFAULT_KEYBINDINGS_FILE, Paths.USER_KEYBINDINGS_FILE)

    action = mapper.resolve(event, contexts=["strategy", "fleet"])
    if action == InputAction.FLEET_MOVE:
        start_move_mode()

    hint = mapper.get_display_text(InputAction.FLEET_MOVE)  # "M"
"""
from __future__ import annotations

from typing import Dict, FrozenSet, List, Optional, Tuple

import pygame

from game.core.input_actions import InputAction, KeyBinding
from game.core.json_utils import load_json, save_json
from game.core.logger import log_debug, log_error


# Mapping of pygame modifier bitmask flags to canonical modifier names.
_MOD_MAP: List[Tuple[int, str]] = [
    (pygame.KMOD_CTRL, "ctrl"),
    (pygame.KMOD_SHIFT, "shift"),
    (pygame.KMOD_ALT, "alt"),
]

# Context overlap rules: contexts that should be considered overlapping
# when checking for conflicts. Key = context, Value = set of contexts
# that overlap with it. "global" overlaps with everything (handled separately).
_CONTEXT_OVERLAP: Dict[str, set] = {
    "fleet": {"strategy", "fleet", "detail_panel"},
    "strategy": {"strategy", "fleet", "detail_panel"},
    "detail_panel": {"strategy", "fleet", "detail_panel"},
    "build_queue": {"build_queue"},
    "fleet_orders": {"fleet_orders"},
    "transfer": {"transfer"},
    "global": set(),  # global overlaps with everything (special case)
}


class InputMapper:
    """Maps pygame KEYDOWN events to InputAction values.

    The mapper maintains two binding tables:
    - _defaults: bindings loaded from the defaults JSON file
    - _bindings: current active bindings (defaults + user overrides)

    A pre-built lookup dict provides O(1) event resolution.
    """

    def __init__(self) -> None:
        """Initialize with empty binding tables."""
        self._defaults: Dict[InputAction, Optional[KeyBinding]] = {}
        self._bindings: Dict[InputAction, Optional[KeyBinding]] = {}
        self._lookup: Dict[Tuple[int, FrozenSet[str]], List[InputAction]] = {}
        self._defaults_path: Optional[str] = None

    def load(
        self,
        defaults_path: Optional[str] = None,
        overrides_path: Optional[str] = None,
    ) -> None:
        """Load bindings from defaults JSON and optional user overrides.

        Args:
            defaults_path: Path to the defaults JSON file.
            overrides_path: Path to the user overrides JSON file (may not exist).
        """
        self._defaults_path = defaults_path
        self._defaults.clear()
        self._bindings.clear()

        # Initialize all actions as unbound
        for action in InputAction:
            self._defaults[action] = None
            self._bindings[action] = None

        # Load defaults
        if defaults_path:
            self._load_bindings_from_file(defaults_path, self._defaults)
            # Copy defaults to current bindings
            self._bindings.update(self._defaults)

        # Overlay user overrides
        if overrides_path:
            self._load_bindings_from_file(overrides_path, self._bindings)

        self._build_lookup()

    def _load_bindings_from_file(
        self,
        path: str,
        target: Dict[InputAction, Optional[KeyBinding]],
    ) -> None:
        """Load bindings from a JSON file into target dict.

        Args:
            path: Path to the JSON file.
            target: Dict to populate with loaded bindings.
        """
        data = load_json(path, default=None)
        if data is None:
            return

        bindings_data = data.get("bindings", {})
        for action_value, binding_data in bindings_data.items():
            try:
                action = InputAction(action_value)
            except ValueError:
                log_debug(f"Unknown action in keybindings file: {action_value}")
                continue
            target[action] = KeyBinding.from_dict(binding_data)

    def _build_lookup(self) -> None:
        """Build the (key_int, modifiers) -> [InputAction] lookup dict.

        Multiple actions can share the same key+modifiers if they belong
        to non-overlapping contexts (e.g., ESC for fleet.cancel_mode,
        build_queue.close, and transfer.cancel).
        """
        self._lookup.clear()
        for action, binding in self._bindings.items():
            if binding is None:
                continue
            key_int = self._resolve_pygame_key(binding.key)
            if key_int is None:
                continue
            lookup_key = (key_int, binding.modifiers)
            if lookup_key not in self._lookup:
                self._lookup[lookup_key] = []
            self._lookup[lookup_key].append(action)

    @staticmethod
    def _resolve_pygame_key(key_name: str) -> Optional[int]:
        """Convert a pygame key name string to its integer constant.

        Args:
            key_name: Pygame key constant name (e.g., "K_m", "K_F12").

        Returns:
            The integer key constant, or None if the name is invalid.
        """
        value = getattr(pygame, key_name, None)
        if isinstance(value, int):
            return value
        log_error(f"Unknown pygame key name: {key_name}")
        return None

    @staticmethod
    def _extract_modifiers(event_mod: int) -> FrozenSet[str]:
        """Convert a pygame modifier bitmask to a frozenset of modifier names.

        Normalizes left/right variants (LSHIFT/RSHIFT -> "shift").

        Args:
            event_mod: The event.mod bitmask from a pygame KEYDOWN event.

        Returns:
            Frozenset of active modifier names ("ctrl", "shift", "alt").
        """
        mods = set()
        for mask, name in _MOD_MAP:
            if event_mod & mask:
                mods.add(name)
        return frozenset(mods)

    def resolve(
        self,
        event: object,
        contexts: Optional[List[str]] = None,
    ) -> Optional[InputAction]:
        """Resolve a pygame event to an InputAction.

        Performs O(1) lookup using the pre-built dict. Only KEYDOWN events
        are processed. Context filtering ensures actions only match when
        their context prefix is in the provided context list.

        When multiple actions share the same key+modifiers (e.g., ESC in
        different contexts), returns the first one whose context matches.

        Args:
            event: A pygame event (only KEYDOWN events are resolved).
            contexts: List of active context prefixes (e.g., ["strategy", "fleet"]).
                     Global actions always match regardless of this filter.

        Returns:
            The matching InputAction, or None if no match found.
        """
        if getattr(event, "type", None) != pygame.KEYDOWN:
            return None

        key_int = event.key
        mods = self._extract_modifiers(event.mod)
        lookup_key = (key_int, mods)

        actions = self._lookup.get(lookup_key)
        if not actions:
            return None

        # No context filter: return first action
        if contexts is None:
            return actions[0]

        # Context filtering: return first matching action
        for action in actions:
            action_context = action.value.split(".")[0]
            if action_context == "global" or action_context in contexts:
                return action

        return None

    def get_binding(self, action: InputAction) -> Optional[KeyBinding]:
        """Get the current key binding for an action.

        Args:
            action: The InputAction to look up.

        Returns:
            The current KeyBinding, or None if the action is unbound.
        """
        return self._bindings.get(action)

    def get_default_binding(self, action: InputAction) -> Optional[KeyBinding]:
        """Get the default key binding for an action.

        Returns the binding from the defaults file, ignoring any user overrides.
        Useful for the keybindings editor to show "Reset to Default" values.

        Args:
            action: The InputAction to look up.

        Returns:
            The default KeyBinding, or None if the action has no default binding.
        """
        return self._defaults.get(action)

    def get_display_text(self, action: InputAction) -> str:
        """Get human-readable display text for an action's current binding.

        Args:
            action: The InputAction to look up.

        Returns:
            Display text like "M" or "Shift+G", or empty string if unbound.
        """
        binding = self.get_binding(action)
        if binding is None:
            return ""
        return binding.display_text()

    def set_binding(
        self,
        action: InputAction,
        binding: Optional[KeyBinding],
    ) -> None:
        """Set or clear the binding for an action.

        Updates the active bindings and rebuilds the lookup dict.

        Args:
            action: The InputAction to rebind.
            binding: The new KeyBinding, or None to unbind.
        """
        self._bindings[action] = binding
        self._build_lookup()

    def get_conflicts(
        self,
        binding: KeyBinding,
        context: Optional[str] = None,
    ) -> List[InputAction]:
        """Find actions that conflict with a proposed binding.

        Two bindings conflict if they have the same key+modifiers and
        their contexts overlap (i.e., both could be active simultaneously).

        Args:
            binding: The proposed KeyBinding to check.
            context: The context of the action being rebound (e.g., "fleet").

        Returns:
            List of conflicting InputAction values.
        """
        key_int = self._resolve_pygame_key(binding.key)
        if key_int is None:
            return []

        conflicts: List[InputAction] = []
        for action, current_binding in self._bindings.items():
            if current_binding is None:
                continue
            # Check if same key + modifiers
            other_key = self._resolve_pygame_key(current_binding.key)
            if other_key != key_int or current_binding.modifiers != binding.modifiers:
                continue
            # Check context overlap
            if self._contexts_overlap(context, action.value.split(".")[0]):
                conflicts.append(action)

        return conflicts

    @staticmethod
    def _contexts_overlap(context_a: Optional[str], context_b: str) -> bool:
        """Check if two contexts can be active simultaneously.

        Global context overlaps with everything.

        Args:
            context_a: First context (the one being rebound).
            context_b: Second context (the existing binding's context).

        Returns:
            True if the contexts overlap.
        """
        # Global overlaps with everything
        if context_a == "global" or context_b == "global":
            return True

        if context_a is None:
            return True

        # Check overlap table
        overlapping = _CONTEXT_OVERLAP.get(context_a, {context_a})
        return context_b in overlapping

    def save_user_overrides(self, path: Optional[str] = None) -> bool:
        """Save only the bindings that differ from defaults.

        Args:
            path: File path to save to. Uses Paths.USER_KEYBINDINGS_FILE if None.

        Returns:
            True if save succeeded, False otherwise.
        """
        if path is None:
            from game.core.paths import Paths
            path = Paths.USER_KEYBINDINGS_FILE

        diffs: Dict[str, dict] = {}
        for action in InputAction:
            current = self._bindings.get(action)
            default = self._defaults.get(action)
            if current != default:
                diffs[action.value] = current.to_dict() if current else {}

        if not diffs:
            log_debug("No keybinding overrides to save")
            return True

        data = {"bindings": diffs}
        return save_json(path, data)

    def reset_to_defaults(self) -> None:
        """Discard all user overrides and reload from defaults only."""
        self._bindings.clear()
        self._bindings.update(self._defaults)
        self._build_lookup()

    def get_all_bindings(self) -> Dict[InputAction, Optional[KeyBinding]]:
        """Get all current bindings for the settings screen.

        Returns:
            Dict mapping every InputAction to its current KeyBinding (or None).
        """
        return dict(self._bindings)
