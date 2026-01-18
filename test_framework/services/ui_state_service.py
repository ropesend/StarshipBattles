"""
UI State Service

Manages the UI state for Combat Lab, including selected category, test,
hover states, and notifications to observers when state changes.
"""

from typing import Optional, Callable, List
from simulation_tests.logging_config import get_logger

logger = get_logger(__name__)


class UIStateService:
    """Service for managing UI state and notifying observers of changes."""

    def __init__(self):
        """Initialize UI state service."""
        # Selection state
        self._selected_category: Optional[str] = None
        self._selected_test_id: Optional[str] = None

        # Tag filter state
        self._active_tag_filters: List[str] = []  # Tags to filter by (AND logic)
        self._excluded_tags: List[str] = []  # Tags to exclude

        # Seed control state
        self._seed_mode: str = "random"  # "random", "metadata", "custom"
        self._custom_seed: Optional[int] = None

        # Hover state
        self._category_hover: Optional[str] = None
        self._test_hover: Optional[str] = None

        # Modal visibility
        self._json_popup_visible: bool = False
        self._confirmation_dialog_visible: bool = False

        # Test execution state
        self._headless_running: bool = False

        # Observers for state changes
        self._observers: List[Callable] = []

    def select_category(self, category: Optional[str]):
        """
        Select a category.

        Args:
            category: Category name or None to deselect
        """
        if self._selected_category != category:
            self._selected_category = category
            self._selected_test_id = None  # Clear test selection when category changes
            self._notify_observers()

    def select_test(self, test_id: Optional[str]):
        """
        Select a test.

        Args:
            test_id: Test ID or None to deselect
        """
        if self._selected_test_id != test_id:
            self._selected_test_id = test_id
            self._notify_observers()

    def set_category_hover(self, category: Optional[str]):
        """
        Set hover state for category.

        Args:
            category: Category name or None
        """
        if self._category_hover != category:
            self._category_hover = category

    def set_test_hover(self, test_id: Optional[str]):
        """
        Set hover state for test.

        Args:
            test_id: Test ID or None
        """
        if self._test_hover != test_id:
            self._test_hover = test_id

    def set_json_popup_visible(self, visible: bool):
        """Set JSON popup visibility."""
        self._json_popup_visible = visible

    def set_confirmation_dialog_visible(self, visible: bool):
        """Set confirmation dialog visibility."""
        self._confirmation_dialog_visible = visible

    def set_headless_running(self, running: bool):
        """Set headless test running state."""
        if self._headless_running != running:
            self._headless_running = running
            self._notify_observers()

    def reset_selection(self):
        """Reset all selection state."""
        self._selected_category = None
        self._selected_test_id = None
        self._notify_observers()

    def get_selected_category(self) -> Optional[str]:
        """Get currently selected category."""
        return self._selected_category

    def get_selected_test_id(self) -> Optional[str]:
        """Get currently selected test ID."""
        return self._selected_test_id

    def get_category_hover(self) -> Optional[str]:
        """Get currently hovered category."""
        return self._category_hover

    def get_test_hover(self) -> Optional[str]:
        """Get currently hovered test."""
        return self._test_hover

    def is_json_popup_visible(self) -> bool:
        """Check if JSON popup is visible."""
        return self._json_popup_visible

    def is_confirmation_dialog_visible(self) -> bool:
        """Check if confirmation dialog is visible."""
        return self._confirmation_dialog_visible

    def is_headless_running(self) -> bool:
        """Check if headless test is running."""
        return self._headless_running

    def add_observer(self, callback: Callable):
        """
        Add an observer to be notified of state changes.

        Args:
            callback: Function to call when state changes
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: Callable):
        """
        Remove an observer.

        Args:
            callback: Function to remove
        """
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Notify all observers of state change."""
        for callback in self._observers:
            try:
                callback()
            except Exception as e:
                logger.error(f"Error notifying observer: {e}")

    # === Tag Filter Methods ===

    def cycle_tag_state(self, tag: str):
        """
        Cycle a tag through three states: neutral -> include -> exclude -> neutral.

        Args:
            tag: Tag to cycle
        """
        if tag in self._active_tag_filters:
            # Currently included -> move to excluded
            self._active_tag_filters.remove(tag)
            self._excluded_tags.append(tag)
        elif tag in self._excluded_tags:
            # Currently excluded -> move to neutral
            self._excluded_tags.remove(tag)
        else:
            # Currently neutral -> move to included
            self._active_tag_filters.append(tag)
        self._notify_observers()

    def get_tag_state(self, tag: str) -> str:
        """
        Get the current state of a tag filter.

        Args:
            tag: Tag to check

        Returns:
            "include", "exclude", or "neutral"
        """
        if tag in self._active_tag_filters:
            return "include"
        elif tag in self._excluded_tags:
            return "exclude"
        else:
            return "neutral"

    def clear_tag_filters(self):
        """Clear all tag filters."""
        self._active_tag_filters = []
        self._excluded_tags = []
        self._notify_observers()

    def get_active_tag_filters(self) -> List[str]:
        """Get list of active tag filters (included tags)."""
        return self._active_tag_filters.copy()

    def get_excluded_tags(self) -> List[str]:
        """Get list of excluded tags."""
        return self._excluded_tags.copy()

    def is_tag_active(self, tag: str) -> bool:
        """Check if a tag is in the active filter list (included)."""
        return tag in self._active_tag_filters

    def is_tag_excluded(self, tag: str) -> bool:
        """Check if a tag is excluded."""
        return tag in self._excluded_tags

    # === Seed Control Methods ===

    def set_seed_mode(self, mode: str):
        """
        Set the seed mode.

        Args:
            mode: "random", "metadata", or "custom"
        """
        if mode not in ("random", "metadata", "custom"):
            raise ValueError(f"Invalid seed mode: {mode}")
        if self._seed_mode != mode:
            self._seed_mode = mode
            self._notify_observers()

    def set_custom_seed(self, seed: Optional[int]):
        """
        Set a custom seed value.

        Args:
            seed: Integer seed value or None
        """
        self._custom_seed = seed
        if seed is not None:
            self._seed_mode = "custom"
        self._notify_observers()

    def get_seed_mode(self) -> str:
        """Get current seed mode."""
        return self._seed_mode

    def get_custom_seed(self) -> Optional[int]:
        """Get custom seed value."""
        return self._custom_seed

    def get_effective_seed(self, metadata_seed: int) -> int:
        """
        Get the effective seed to use for a test run.

        Args:
            metadata_seed: The seed from test metadata

        Returns:
            Seed to use based on current mode
        """
        import random
        if self._seed_mode == "metadata":
            return metadata_seed
        elif self._seed_mode == "custom" and self._custom_seed is not None:
            return self._custom_seed
        else:  # random
            return random.randint(0, 2**31 - 1)
