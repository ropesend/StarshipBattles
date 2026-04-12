"""
UI State Service

Holds the Combat Lab UI selection/filter/seed state used by the screen,
input handler, renderer, and executor.
"""

from typing import Optional, List


class UIStateService:
    """Service for managing UI state."""

    def __init__(self):
        """Initialize UI state service."""
        # Selection state
        self._selected_category: Optional[str] = None
        self._selected_test_id: Optional[str] = None

        # Tag filter state
        self._active_tag_filters: List[str] = []  # Tags to include (AND logic)
        self._excluded_tags: List[str] = []       # Tags to exclude

        # Seed control state
        self._seed_mode: str = "random"  # "random", "metadata", "custom"
        self._custom_seed: Optional[int] = None

        # Group tree state (collapsible sidebar)
        self._expanded_groups: set = set()
        self._selected_group: Optional[str] = None

        # Hover state
        self._category_hover: Optional[str] = None
        self._test_hover: Optional[str] = None

        # Test execution state
        self._headless_running: bool = False

    # === Selection ===

    def select_category(self, category: Optional[str]):
        """Select a category (clears group and test selection)."""
        if self._selected_category != category:
            self._selected_category = category
            self._selected_group = None
            self._selected_test_id = None
            # Auto-expand the group containing this category
            if category:
                from combat_lab.registry import get_group_for_category
                group = get_group_for_category(category)
                self._expanded_groups.add(group)

    def select_group(self, group: Optional[str]):
        """Select a group for filtering (shows all tests in group)."""
        if self._selected_group != group:
            self._selected_group = group
            self._selected_category = None
            self._selected_test_id = None

    def get_selected_group(self) -> Optional[str]:
        """Get currently selected group."""
        return self._selected_group

    def select_test(self, test_id: Optional[str]):
        """Select a test."""
        if self._selected_test_id != test_id:
            self._selected_test_id = test_id

    def get_selected_category(self) -> Optional[str]:
        """Get currently selected category."""
        return self._selected_category

    def get_selected_test_id(self) -> Optional[str]:
        """Get currently selected test ID."""
        return self._selected_test_id

    def reset_selection(self):
        """Reset all selection state."""
        self._selected_category = None
        self._selected_test_id = None
        self._selected_group = None

    # === Group expansion ===

    def toggle_group(self, group: str):
        """Toggle expand/collapse of a group in the sidebar."""
        if group in self._expanded_groups:
            self._expanded_groups.discard(group)
        else:
            self._expanded_groups.add(group)

    def is_group_expanded(self, group: str) -> bool:
        """Check if a group is expanded in the sidebar."""
        return group in self._expanded_groups

    # === Hover ===

    def set_category_hover(self, category: Optional[str]):
        """Set hover state for category."""
        self._category_hover = category

    def set_test_hover(self, test_id: Optional[str]):
        """Set hover state for test."""
        self._test_hover = test_id

    def get_category_hover(self) -> Optional[str]:
        """Get currently hovered category."""
        return self._category_hover

    def get_test_hover(self) -> Optional[str]:
        """Get currently hovered test."""
        return self._test_hover

    # === Execution state ===

    def set_headless_running(self, running: bool):
        """Set headless test running state."""
        self._headless_running = running

    def is_headless_running(self) -> bool:
        """Check if headless test is running."""
        return self._headless_running

    # === Tag filters ===

    def cycle_tag_state(self, tag: str):
        """Cycle a tag: neutral -> include -> exclude -> neutral."""
        if tag in self._active_tag_filters:
            self._active_tag_filters.remove(tag)
            self._excluded_tags.append(tag)
        elif tag in self._excluded_tags:
            self._excluded_tags.remove(tag)
        else:
            self._active_tag_filters.append(tag)

    def clear_tag_filters(self):
        """Clear all tag filters."""
        self._active_tag_filters = []
        self._excluded_tags = []

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

    # === Seed control ===

    def set_seed_mode(self, mode: str):
        """Set the seed mode. Valid: "random", "metadata", "custom"."""
        if mode not in ("random", "metadata", "custom"):
            raise ValueError(f"Invalid seed mode: {mode}")
        self._seed_mode = mode

    def set_custom_seed(self, seed: Optional[int]):
        """Set a custom seed value; flips seed mode to 'custom' if non-None."""
        self._custom_seed = seed
        if seed is not None:
            self._seed_mode = "custom"

    def get_seed_mode(self) -> str:
        """Get current seed mode."""
        return self._seed_mode

    def get_custom_seed(self) -> Optional[int]:
        """Get custom seed value."""
        return self._custom_seed

    def get_effective_seed(self, metadata_seed: int) -> int:
        """
        Get the effective seed to use for a test run based on current mode.
        """
        import random
        if self._seed_mode == "metadata":
            return metadata_seed
        elif self._seed_mode == "custom" and self._custom_seed is not None:
            return self._custom_seed
        return random.randint(0, 2**31 - 1)
