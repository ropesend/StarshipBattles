"""
Species population dataclass.

Extracted from planet.py (PROJ-210) to reduce module size.
"""

from dataclasses import dataclass

from game.core.validation_helpers import require_keys


@dataclass
class SpeciesPopulation:
    """
    Represents a population of a single species on a planet.

    Population is tracked in units of 1,000 people for manageable numbers.
    Happiness affects growth rate and productivity.
    """
    race_id: str  # References RaceConfig.race_id
    count: int = 0  # Population units (1 unit = 1,000 people)
    happiness: float = 0.5  # 0.0 (miserable) to 1.0 (ecstatic)

    @classmethod
    def from_dict(cls, data: dict) -> 'SpeciesPopulation':
        """
        Deserialize population from dict.

        Args:
            data: Dict with population data

        Returns:
            Reconstructed SpeciesPopulation

        Raises:
            PersistenceException: If required keys missing
        """
        require_keys(data, ['race_id', 'count'], 'SpeciesPopulation')
        return cls(
            race_id=data['race_id'],
            count=data['count'],
            happiness=data.get('happiness', 0.5)
        )
