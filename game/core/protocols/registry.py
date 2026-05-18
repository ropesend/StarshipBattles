"""Data-registry DI protocol (PROJ-27/PROJ-50)."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class IRegistryProvider(Protocol):
    """
    Protocol for registry access abstraction.

    PROJ-27/PROJ-50: Enables dependency injection for registry access, allowing
    services to be tested in isolation without relying on the global singleton.

    Implementations:
        - DefaultRegistryProvider: Delegates to RegistryManager singleton (production)
        - TestRegistryProvider: Provides isolated registry data (testing)

    Usage (PROJ-50 strict DI - registry is required):
        def calculate_stats(design: dict, registry: IRegistryProvider):
            # PROJ-50: registry is now required, not optional
            components = registry.get_components()
            ...
    """
    def get_components(self) -> dict[str, Any]:
        """Get the component registry dictionary."""
        ...

    def get_modifiers(self) -> dict[str, Any]:
        """Get the modifier registry dictionary."""
        ...

    def get_vehicle_classes(self) -> dict[str, Any]:
        """Get the vehicle classes dictionary."""
        ...

    def get_resources(self) -> dict[str, Any]:
        """Get the resources registry dictionary."""
        ...
