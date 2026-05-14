"""Storm generator for environmental hazards (PROJ-189; PROJ-300 schema v2.0).

Generates storm entities during galaxy system generation. Reads the v2.0
storms.json schema (abilities-dict shape per PROJ-300) and emits Storm
instances with `abilities` populated. The legacy v1.0 schema (with `effects`
block) is no longer accepted — Phase 7 of PROJ-300 deletes the StormEffect
class.
"""
import copy
import random
from typing import Any, Dict, List, Optional, Set

from game.core.hex_math import HexCoord, hex_random_cluster
from game.core.string_utils import display_name
from game.strategy.data.storm import Storm

# Greek letters for storm naming
GREEK_LETTERS = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta",
    "Eta", "Theta", "Iota", "Kappa", "Lambda", "Mu",
    "Nu", "Xi", "Omicron", "Pi", "Rho", "Sigma",
    "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"
]


class StormGenerator:
    """Generates storms for star systems based on blueprint configuration.

    Storms are multi-hex environmental hazards with effects that
    apply to ships within their occupied hexes.
    """

    def __init__(self, storm_defs: Dict[str, Any]) -> None:
        """Initialize the storm generator.

        Args:
            storm_defs: Parsed storms.json data containing storm type definitions.
        """
        self._storm_types: Dict[str, Dict[str, Any]] = storm_defs.get("storm_types", {})

    def generate_storms(
        self,
        system: 'StarSystem',
        blueprint_config: Dict[str, Any],
        rng: random.Random
    ) -> List[Storm]:
        """Generate storms for a star system.

        Args:
            system: StarSystem to generate storms for.
            blueprint_config: Blueprint configuration with storms section.
            rng: Random number generator for deterministic results.

        Returns:
            List of Storm objects.
        """
        storms_config = blueprint_config.get("storms", {})
        if not storms_config:
            return []

        count_config = storms_config.get("count", {"min": 0, "max": 0})
        min_count = count_config.get("min", 0)
        max_count = count_config.get("max", 0)

        if max_count <= 0:
            return []

        # Roll storm count
        storm_count = rng.randint(min_count, max_count)
        if storm_count <= 0:
            return []

        # Get allowed types or use all
        allowed_types = storms_config.get("allowed_types", list(self._storm_types.keys()))

        # Collect occupied hexes to avoid
        occupied = self._collect_occupied_hexes(system, [])

        # Generate storms
        storms: List[Storm] = []
        greek_index = 0

        for _ in range(storm_count):
            # Select random type
            storm_type_id = rng.choice(allowed_types)
            storm_type_def = self._storm_types.get(storm_type_id)
            if not storm_type_def:
                continue

            # Find valid center location
            center = self._find_valid_center(system, occupied, rng)
            if center is None:
                continue  # Can't place more storms

            # Determine cluster size
            size_config = storm_type_def.get("size", {"min": 2, "max": 5})
            target_size = rng.randint(size_config["min"], size_config["max"])

            # Generate cluster shape
            hex_offsets = hex_random_cluster(center, target_size, rng, frozenset(occupied))

            # PROJ-300 v2.0 schema: copy abilities from the type template.
            # No min/max rolls on storms today — PROJ-301..304 use the shared
            # roll_intrinsic_abilities helper for those.
            abilities_template = storm_type_def.get("abilities", {})
            storm_abilities: Dict[str, Any] = copy.deepcopy(abilities_template)
            storm_description = storm_type_def.get("description", "")

            # Select image variant
            image_variants = storm_type_def.get("image_variants", [1])
            image_variant = rng.choice(image_variants)

            # Roll intensity
            intensity = rng.uniform(0.3, 1.0)

            # Generate name
            type_name = storm_type_def.get("name", display_name(storm_type_id))
            greek_letter = GREEK_LETTERS[greek_index % len(GREEK_LETTERS)]
            name = f"{type_name} {greek_letter}"
            greek_index += 1

            # Create storm (PROJ-300 v2.0 — abilities + description, no effects).
            storm = Storm(
                name=name,
                storm_type=storm_type_id,
                description=storm_description,
                location=center,
                hex_offsets=hex_offsets,
                abilities=storm_abilities,
                image_variant=image_variant,
                intensity=intensity,
            )
            storms.append(storm)

            # Update occupied hexes
            occupied.update(storm.occupied_hexes)

        return storms

    def _collect_occupied_hexes(
        self,
        system: 'StarSystem',
        existing_storms: List[Storm]
    ) -> Set[HexCoord]:
        """Collect all hexes that storms cannot occupy.

        Args:
            system: StarSystem containing stars and planets.
            existing_storms: Previously generated storms in this system.

        Returns:
            Set of occupied HexCoords.
        """
        occupied: Set[HexCoord] = set()

        # Collect star occupied hexes
        for star in system.stars:
            occupied.update(star.occupied_hexes)

        # Collect planet locations
        for planet in system.planets:
            occupied.add(planet.location)

        # Collect existing storm hexes
        for storm in existing_storms:
            occupied.update(storm.occupied_hexes)

        return occupied

    def _find_valid_center(
        self,
        system: 'StarSystem',
        occupied: Set[HexCoord],
        rng: random.Random,
        max_attempts: int = 50
    ) -> Optional[HexCoord]:
        """Find a valid center hex for a new storm.

        Args:
            system: StarSystem for context on valid range.
            occupied: Set of hexes that cannot be used.
            rng: Random number generator.
            max_attempts: Maximum placement attempts before giving up.

        Returns:
            Valid HexCoord for storm center, or None if no valid location found.
        """
        # Determine search radius based on star system extent
        # Use largest star orbital radius plus margin
        max_radius = 15  # Default search radius

        if system.stars:
            # Find max extent from stars
            for star in system.stars:
                star_extent = len(star.occupied_hexes) + 5
                if star_extent > max_radius:
                    max_radius = star_extent

        # Also check planet distances
        for planet in system.planets:
            dist = max(abs(planet.location.q), abs(planet.location.r))
            if dist + 5 > max_radius:
                max_radius = dist + 5

        # Clamp to reasonable bounds
        max_radius = min(max_radius, 30)

        for _ in range(max_attempts):
            # Generate random hex within radius
            q = rng.randint(-max_radius, max_radius)
            r = rng.randint(-max_radius, max_radius)
            candidate = HexCoord(q, r)

            if candidate not in occupied:
                return candidate

        return None


# Type hint forward reference
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from game.strategy.data.star_system import StarSystem