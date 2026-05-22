import logging
import os
import yaml
import random
from typing import List, Optional, Set

logger = logging.getLogger(__name__)


class NameRegistry:
    """Registry for unique system names loaded from YAML files."""

    def __init__(
        self,
        data_file_path: Optional[str] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        """Initialize the name registry.

        Args:
            data_file_path: Optional path to YAML file containing names.
            rng: Optional seeded RNG for the load-time name shuffle (PROJ-473
                S8). The shuffle happens at construction (load time), not at
                ``get_system_name()`` time, so the rng must be supplied here.
                When ``None`` an unseeded ``random.Random()`` is used so the
                shuffle never touches global module state — names are simply
                non-reproducible in that case (the production path injects a
                seeded rng from the composition root). Hazard H1: this fixes
                the previous bare ``random.shuffle`` that drew from the
                unseeded global stream.
        """
        self.available_names: List[str] = []
        self.used_names: Set[str] = set()
        self._rng: random.Random = rng if rng is not None else random.Random()

        if data_file_path:
            self.load_data(data_file_path)

    def load_data(self, file_path: str) -> None:
        """Load names from YAML file.

        Args:
            file_path: Path to YAML file containing a 'names' list.
        """
        if not os.path.exists(file_path):
            logger.error(f"Name data file not found: {file_path}")
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if "names" in data and isinstance(data["names"], list):
                self.available_names = data["names"]
                # Default behavior: shuffle for random selection. Uses the
                # injected seeded rng (PROJ-473 S8) so name order is
                # reproducible for a fixed galaxy_seed.
                self._rng.shuffle(self.available_names)
            else:
                logger.warning(f"Invalid format in {file_path}: 'names' list missing.")

        except (FileNotFoundError, OSError, yaml.YAMLError, KeyError, TypeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to load name data: {e}")

    def get_system_name(self) -> str:
        """Get a unique system name.

        Returns:
            A unique name, or a fallback "Unknown-N" if names are exhausted.
        """
        if not self.available_names:
            return f"Unknown-{len(self.used_names) + 1}"

        name = self.available_names.pop()
        while name in self.used_names:
            if not self.available_names:
                return f"Unknown-{len(self.used_names) + 1}"
            name = self.available_names.pop()

        self.used_names.add(name)
        return name

    @staticmethod
    def to_roman(n: int) -> str:
        """Convert integer to Roman numeral (1-3999)."""
        if not (0 < n < 4000):
            return str(n)
            
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        syb = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = ''
        i = 0
        while  n > 0:
            for _ in range(n // val[i]):
                roman_num += syb[i]
                n -= val[i]
            i += 1
        return roman_num

