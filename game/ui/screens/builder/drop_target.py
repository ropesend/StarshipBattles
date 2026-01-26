from typing import Protocol, runtime_checkable

@runtime_checkable
class DropTarget(Protocol):
    def can_accept_drop(self, pos) -> bool:
        """Check if this target can accept a drop at the given position."""
        ...

    def accept_drop(self, pos, component, count=1) -> bool:
        """Handle the drop of a component. Returns True if successful."""
        ...
