"""MockBattleUIService - Test double for BattleUIService.

PROJ-43 Phase 12: Provides a configurable mock implementation of IBattleUI
for testing UI components in isolation without requiring a real battle engine.

Usage:
    from tests.unit.ui.mocks import MockBattleUIService
    from game.ui.interfaces.battle_ui import ShipDTO
    from game.core.math import Vector2

    # Create mock with default empty state
    mock = MockBattleUIService()

    # Or create with pre-configured ships
    ship = ShipDTO(
        id="ship_1", name="Test Ship", team_id=0,
        position=Vector2(0, 0), velocity=Vector2(0, 0),
        heading=0.0, is_alive=True, is_derelict=False,
        hp=100.0, max_hp=100.0, current_shields=0.0,
        max_shields=0.0, current_speed=0.0, max_speed=100.0,
        mass=1000.0, total_thrust=500.0, turn_speed=0.1,
        total_shots_fired=0, crew_onboard=10, crew_required=10,
        current_target_name=None, secondary_target_names=[],
        max_targets=1, ai_strategy="default", source_file=None,
        resources=[], components=[]
    )
    mock = MockBattleUIService(ships=[ship])

    # Use in tests
    assert len(mock.get_ships()) == 1
    mock.set_battle_over(True, winner=0)
    assert mock.is_battle_over()
"""
from typing import List, Optional

from game.ui.interfaces.battle_ui import (
    IBattleUI,
    ShipDTO,
    ProjectileDTO,
    BeamDTO,
)


class MockBattleUIService:
    """Mock implementation of IBattleUI for testing.

    Provides configurable battle state for testing UI components
    without requiring a real battle engine.

    Attributes:
        ships: List of ShipDTO to return from get_ships()
        projectiles: List of ProjectileDTO to return from get_projectiles()
        beams: List of BeamDTO to return from get_recent_beams()
        battle_over: Whether battle is over
        winner: Winning team ID (0, 1, -1 for draw, None if ongoing)
        tick_count: Current tick count

        call_counts: Dict tracking method call counts for assertions
    """

    def __init__(
        self,
        ships: Optional[List[ShipDTO]] = None,
        projectiles: Optional[List[ProjectileDTO]] = None,
        beams: Optional[List[BeamDTO]] = None,
        battle_over: bool = False,
        winner: Optional[int] = None,
        tick_count: int = 0
    ):
        """Initialize the mock with configurable state.

        Args:
            ships: Initial list of ships (default: empty)
            projectiles: Initial list of projectiles (default: empty)
            beams: Initial list of beams (default: empty)
            battle_over: Initial battle_over state (default: False)
            winner: Initial winner (default: None)
            tick_count: Initial tick count (default: 0)
        """
        self.ships = ships or []
        self.projectiles = projectiles or []
        self.beams = beams or []
        self._battle_over = battle_over
        self._winner = winner
        self._tick_count = tick_count

        # Track method calls for assertions
        self.call_counts = {
            'get_ships': 0,
            'get_projectiles': 0,
            'get_recent_beams': 0,
            'is_battle_over': 0,
            'get_winner': 0,
            'get_tick_count': 0,
        }

    def get_ships(self) -> List[ShipDTO]:
        """Return configured ships list.

        Returns:
            List of ShipDTO objects
        """
        self.call_counts['get_ships'] += 1
        return self.ships

    def get_projectiles(self) -> List[ProjectileDTO]:
        """Return configured projectiles list.

        Returns:
            List of ProjectileDTO objects
        """
        self.call_counts['get_projectiles'] += 1
        return self.projectiles

    def get_recent_beams(self) -> List[BeamDTO]:
        """Return configured beams list and clear it.

        Mimics real behavior where beams are cleared after retrieval.

        Returns:
            List of BeamDTO objects
        """
        self.call_counts['get_recent_beams'] += 1
        beams = self.beams
        self.beams = []  # Clear after retrieval like real service
        return beams

    def is_battle_over(self) -> bool:
        """Return configured battle_over state.

        Returns:
            True if battle is over, False otherwise
        """
        self.call_counts['is_battle_over'] += 1
        return self._battle_over

    def get_winner(self) -> Optional[int]:
        """Return configured winner.

        Returns:
            Winning team ID or None
        """
        self.call_counts['get_winner'] += 1
        return self._winner

    def get_tick_count(self) -> int:
        """Return configured tick count.

        Returns:
            Current tick count
        """
        self.call_counts['get_tick_count'] += 1
        return self._tick_count

    # === Configuration Methods ===

    def set_ships(self, ships: List[ShipDTO]) -> None:
        """Set the ships list.

        Args:
            ships: New list of ships
        """
        self.ships = ships

    def add_ship(self, ship: ShipDTO) -> None:
        """Add a ship to the list.

        Args:
            ship: Ship to add
        """
        self.ships.append(ship)

    def set_projectiles(self, projectiles: List[ProjectileDTO]) -> None:
        """Set the projectiles list.

        Args:
            projectiles: New list of projectiles
        """
        self.projectiles = projectiles

    def add_projectile(self, projectile: ProjectileDTO) -> None:
        """Add a projectile to the list.

        Args:
            projectile: Projectile to add
        """
        self.projectiles.append(projectile)

    def add_beam(self, beam: BeamDTO) -> None:
        """Add a beam to the list.

        Args:
            beam: Beam to add
        """
        self.beams.append(beam)

    def set_battle_over(self, is_over: bool, winner: Optional[int] = None) -> None:
        """Set the battle over state.

        Args:
            is_over: Whether battle is over
            winner: Winning team ID (0, 1, -1 for draw, None if ongoing)
        """
        self._battle_over = is_over
        self._winner = winner

    def set_tick_count(self, count: int) -> None:
        """Set the tick count.

        Args:
            count: New tick count
        """
        self._tick_count = count

    def advance_tick(self, count: int = 1) -> None:
        """Advance the tick count.

        Args:
            count: Number of ticks to advance (default: 1)
        """
        self._tick_count += count

    def reset_call_counts(self) -> None:
        """Reset all call counts to zero."""
        for key in self.call_counts:
            self.call_counts[key] = 0

    # === Verification Methods ===

    def assert_get_ships_called(self, times: Optional[int] = None) -> None:
        """Assert get_ships was called.

        Args:
            times: Exact number of times expected (None = at least once)
        """
        if times is not None:
            assert self.call_counts['get_ships'] == times, \
                f"get_ships called {self.call_counts['get_ships']} times, expected {times}"
        else:
            assert self.call_counts['get_ships'] > 0, "get_ships was never called"

    def assert_get_projectiles_called(self, times: Optional[int] = None) -> None:
        """Assert get_projectiles was called.

        Args:
            times: Exact number of times expected (None = at least once)
        """
        if times is not None:
            assert self.call_counts['get_projectiles'] == times, \
                f"get_projectiles called {self.call_counts['get_projectiles']} times, expected {times}"
        else:
            assert self.call_counts['get_projectiles'] > 0, "get_projectiles was never called"


# Verify MockBattleUIService satisfies IBattleUI protocol
assert isinstance(MockBattleUIService(), IBattleUI), "MockBattleUIService must satisfy IBattleUI"
