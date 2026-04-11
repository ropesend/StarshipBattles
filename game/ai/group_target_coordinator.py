"""
Group target coordinator — group-level combat coordination.

Handles focus fire (selecting one target for the group), reserve
commitment (deciding when reserves should engage), and flagship
succession (finding the next flagship when the current one is destroyed).

These are stateless utility functions used by the battle setup and
AI systems to coordinate group behavior.
"""

from typing import Any, Callable, List, Optional

from game.core.math import Vector2


class GroupTargetCoordinator:
    """Coordinates group-level combat decisions.

    All methods are stateless — they take inputs and return results
    without maintaining any internal state between calls.
    """

    def select_focus_target(
        self,
        enemies: List[Any],
        priority: str,
        reference_position: Optional[Vector2] = None,
    ) -> Optional[Any]:
        """Select a single focus-fire target for the group.

        Args:
            enemies: List of enemy ships to consider.
            priority: Selection priority — 'strongest', 'nearest',
                      'most_damaged', 'largest'.
            reference_position: Group centroid for distance calculations.

        Returns:
            The selected target, or None if no valid enemies.
        """
        alive_enemies = [e for e in enemies if e.is_alive]
        if not alive_enemies:
            return None

        if priority == "strongest":
            return max(alive_enemies, key=lambda e: e.mass)

        elif priority == "most_damaged":
            return min(alive_enemies, key=lambda e: e.hp / max(e.max_hp, 1))

        elif priority == "nearest":
            if reference_position is None:
                reference_position = Vector2(0, 0)
            return min(
                alive_enemies,
                key=lambda e: (e.position - reference_position).length(),
            )

        elif priority == "largest":
            return max(alive_enemies, key=lambda e: e.mass)

        # Default: pick first alive
        return alive_enemies[0]

    @staticmethod
    def compute_group_hp_ratio(ships: List[Any]) -> float:
        """Compute aggregate HP ratio for a group of ships.

        Args:
            ships: Ships in the group.

        Returns:
            Total current HP / total max HP, or 0.0 if empty.
        """
        total_hp = sum(s.hp for s in ships)
        total_max = sum(s.max_hp for s in ships)

        if total_max <= 0:
            return 0.0

        return total_hp / total_max

    @staticmethod
    def should_commit_reserve(
        main_body_ships: List[Any],
        threshold: float = 0.50,
    ) -> bool:
        """Determine if reserves should be committed.

        Args:
            main_body_ships: Ships in the main body groups.
            threshold: HP ratio at or below which reserves commit.

        Returns:
            True if reserves should engage.
        """
        ratio = GroupTargetCoordinator.compute_group_hp_ratio(main_body_ships)
        return ratio <= threshold

    @staticmethod
    def find_flagship_successor(
        ships: List[Any],
        has_cnc_check: Callable[[Any], bool],
    ) -> Optional[Any]:
        """Find the next flagship from remaining ships.

        Selects the heaviest alive ship that has CommandAndControl.

        Args:
            ships: Candidate ships for succession.
            has_cnc_check: Callable that returns True if a ship has C&C.

        Returns:
            The successor ship, or None if no eligible ship found.
        """
        candidates = [
            s for s in ships
            if s.is_alive and has_cnc_check(s)
        ]

        if not candidates:
            return None

        return max(candidates, key=lambda s: s.mass)
