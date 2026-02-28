"""Registry for tracking pygame_gui UI elements for bulk cleanup.

PROJ-204 Phase 5: Centralized element cleanup pattern.
"""


class UIElementRegistry:
    """Registry for tracking UI elements that need cleanup.

    Provides a consistent pattern for registering UI elements and
    destroying them all at once, avoiding the repeated pattern of
    iterating over lists and calling kill() on each element.

    Example usage:
        self.elements = UIElementRegistry()
        self.button = self.elements.register(UIButton(...))
        self.label = self.elements.register(UILabel(...))

        # Later, when cleaning up:
        self.elements.kill_all()
    """

    def __init__(self):
        """Initialize empty element registry."""
        self._elements = []

    def register(self, element):
        """Register a UI element for tracking.

        Args:
            element: A pygame_gui UI element with a kill() method.

        Returns:
            The element, allowing chained assignment.
        """
        self._elements.append(element)
        return element

    def kill_all(self):
        """Destroy all registered elements and clear the registry."""
        for el in self._elements:
            el.kill()
        self._elements = []

    def clear(self):
        """Clear the registry without destroying elements.

        Use this when elements are destroyed by other means
        (e.g., parent container cleanup) and you just need
        to reset the registry.
        """
        self._elements = []

    def __len__(self):
        """Return the number of registered elements."""
        return len(self._elements)

    def __iter__(self):
        """Iterate over registered elements."""
        return iter(self._elements)
