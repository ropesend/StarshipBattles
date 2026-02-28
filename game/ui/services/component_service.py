"""
Component Service for UI layer.

PROJ-43: This service provides a facade for component and modifier access,
allowing UI code to work with components without directly importing from
game.simulation.components.component.

PROJ-211: Strict DI - registry_provider is now required (no fallback).

The service encapsulates:
- Component registry access
- Modifier registry access
- Modifier restriction validation
"""
from typing import Any, Dict, List, Optional

from game.core.protocols import IRegistryProvider
from game.core.exceptions import ValidationException
from game.core.error_codes import ErrorCode


class ComponentService:
    """Service for accessing components and modifiers.

    This class provides a clean interface for UI code to access component
    and modifier data without directly importing from the simulation layer.

    Usage:
        # PROJ-211: Strict DI - registry_provider is required
        provider = get_default_registry_provider()  # Or inject from caller
        service = ComponentService(provider)
        components = service.get_all_components()
        modifiers = service.get_modifier_registry()
    """

    def __init__(self, registry_provider: IRegistryProvider):
        """Initialize the ComponentService.

        Args:
            registry_provider: Registry provider for dependency injection.
                PROJ-211: This parameter is now required (strict DI).

        Raises:
            ValidationException: If registry_provider is None.
        """
        if registry_provider is None:
            raise ValidationException(
                "registry_provider is required",
                code=ErrorCode.MISSING_DEPENDENCY.value,
                context={"service": "ComponentService", "parameter": "registry_provider"}
            )
        self._provider = registry_provider

    def _get_provider(self) -> IRegistryProvider:
        """Get the registry provider."""
        return self._provider

    def get_all_components(self) -> List[Any]:
        """Get a list of all components from the registry.

        Returns:
            List of Component instances from the component registry.
        """
        provider = self._get_provider()
        return list(provider.get_components().values())

    def get_modifier_registry(self) -> Dict[str, Any]:
        """Get the modifier registry dictionary.

        Returns:
            Dictionary mapping modifier IDs to modifier definitions.
        """
        provider = self._get_provider()
        return provider.get_modifiers()

    def get_modifier_definition(self, mod_id: str) -> Optional[Any]:
        """Get a specific modifier definition by ID.

        Args:
            mod_id: The modifier identifier.

        Returns:
            The modifier definition, or None if not found.
        """
        modifiers = self.get_modifier_registry()
        return modifiers.get(mod_id)

    def is_modifier_allowed(self, mod_id: str, component: Any) -> bool:
        """Check if a modifier is allowed for the given component.

        This checks the modifier's restrictions against the component's
        type and abilities.

        Args:
            mod_id: The modifier identifier.
            component: The component to check restrictions against.

        Returns:
            True if the modifier can be applied to the component, False otherwise.
        """
        mod_def = self.get_modifier_definition(mod_id)
        if mod_def is None:
            return False

        # No restrictions means always allowed
        if not mod_def.restrictions:
            return True

        restrictions = mod_def.restrictions

        # Check allow_types restriction
        if 'allow_types' in restrictions:
            if component.type_str not in restrictions['allow_types']:
                return False

        # Check deny_types restriction
        if 'deny_types' in restrictions:
            if component.type_str in restrictions['deny_types']:
                return False

        # Check allow_abilities restriction
        if 'allow_abilities' in restrictions:
            required = restrictions['allow_abilities']
            has_ability = False
            for abil in required:
                if abil in component.abilities or abil in component.data.get('abilities', {}):
                    has_ability = True
                    break
            if not has_ability:
                return False

        return True
