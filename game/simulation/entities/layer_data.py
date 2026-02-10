"""
LayerData - Typed structure for ship layer data.

PROJ-84: Ship Layer Data Typed Structures
Replaces raw Dict[str, Any] layer dictionaries with a typed dataclass
for IDE autocomplete, type safety, and protection against typos.
"""
from dataclasses import dataclass, field
from typing import List, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from game.simulation.components.component import Component


@dataclass
class LayerData:
    """
    Typed structure for ship layer data.

    Replaces the raw dictionary:
        {
            'components': [],
            'radius_pct': 0.5,
            'restrictions': [],
            'max_mass_pct': 1.0,
            'mass': 0.0,
            'hp_pool': 0,
            'max_hp_pool': 0
        }

    Attributes:
        components: List of Component instances in this layer.
        radius_pct: Layer radius as percentage (0.0-1.0).
        restrictions: List of restriction strings (e.g., 'HullOnly', 'ArmorOnly').
        max_mass_pct: Maximum mass capacity as percentage.
        mass: Current total mass of components in this layer.
        hp_pool: Current HP of this layer.
        max_hp_pool: Maximum HP capacity of this layer.
    """
    components: List[Any] = field(default_factory=list)  # List['Component']
    radius_pct: float = 0.5
    restrictions: List[str] = field(default_factory=list)
    max_mass_pct: float = 1.0
    mass: float = 0.0
    hp_pool: int = 0
    max_hp_pool: int = 0

    @classmethod
    def create_hull(cls) -> 'LayerData':
        """
        Create a LayerData configured for HULL layer.

        Returns:
            LayerData with:
                - radius_pct=0.0 (structural, no visual radius)
                - restrictions=['HullOnly']
                - max_mass_pct=100.0
        """
        return cls(
            components=[],
            radius_pct=0.0,
            restrictions=['HullOnly'],
            max_mass_pct=100.0,
            mass=0.0,
            hp_pool=0,
            max_hp_pool=0
        )

    @classmethod
    def from_definition(cls, l_def: Dict[str, Any]) -> 'LayerData':
        """
        Create LayerData from a vehicle class layer definition dictionary.

        Args:
            l_def: Dictionary with optional keys:
                - 'radius_pct': float (default 0.5)
                - 'restrictions': List[str] (default [])
                - 'max_mass_pct': float (default 1.0)

        Returns:
            LayerData initialized from the definition with defaults
            for missing keys.
        """
        return cls(
            components=[],
            radius_pct=l_def.get('radius_pct', 0.5),
            restrictions=l_def.get('restrictions', []),
            max_mass_pct=l_def.get('max_mass_pct', 1.0),
            mass=0.0,
            hp_pool=0,
            max_hp_pool=0
        )

    def clear(self) -> None:
        """
        Reset mutable runtime state while preserving layer configuration.

        Clears:
            - components (to empty list)
            - mass (to 0.0)
            - hp_pool (to 0)
            - max_hp_pool (to 0)

        Preserves:
            - radius_pct
            - restrictions
            - max_mass_pct
        """
        self.components.clear()
        self.mass = 0.0
        self.hp_pool = 0
        self.max_hp_pool = 0
