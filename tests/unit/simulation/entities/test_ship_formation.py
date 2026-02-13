"""
Unit tests for ShipFormation class.

Tests cover:
- Formation creation and initialization
- Adding/removing ships from formations
- Join/leave formation operations
- Formation positioning (offset management)
- Edge cases (empty formation, single ship, bidirectional relationships)
- Property behavior (is_master, is_member)

Uses mock ships to isolate ShipFormation behavior from Ship implementation details.
"""
import pytest
from unittest.mock import MagicMock, PropertyMock

from game.simulation.entities.ship_formation import ShipFormation
from game.core.math import Vector2


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_ship():
    """Create a mock ship for isolated unit testing."""
    ship = MagicMock()
    ship.name = "MockShip"
    # Add a real formation attribute that can be accessed
    ship.formation = None  # Will be set by tests as needed
    return ship


@pytest.fixture
def mock_ship_with_formation():
    """Create a mock ship that has a formation attribute pre-configured."""
    ship = MagicMock()
    ship.name = "MockShipWithFormation"
    ship.formation = MagicMock()
    ship.formation.members = []
    ship.formation.master = None
    ship.formation.offset = None
    ship.formation.active = True
    return ship


@pytest.fixture
def formation(mock_ship):
    """Create a ShipFormation with a mock ship owner."""
    return ShipFormation(mock_ship)


@pytest.fixture
def master_ship():
    """Create a mock master ship with formation support."""
    ship = MagicMock()
    ship.name = "MasterShip"
    ship.formation = MagicMock()
    ship.formation.members = []
    return ship


@pytest.fixture
def follower_ship():
    """Create a mock follower ship with formation support."""
    ship = MagicMock()
    ship.name = "FollowerShip"
    ship.formation = MagicMock()
    ship.formation.master = None
    ship.formation.offset = None
    ship.formation.active = True
    return ship


# =============================================================================
# Test: Formation Creation and Initialization
# =============================================================================

class TestShipFormationCreation:
    """Tests for ShipFormation instantiation and default state."""

    def test_creation_with_ship_reference(self, mock_ship):
        """ShipFormation stores reference to owning ship."""
        formation = ShipFormation(mock_ship)

        assert formation.ship is mock_ship

    def test_default_master_is_none(self, formation):
        """New formation has no master by default."""
        assert formation.master is None

    def test_default_offset_is_none(self, formation):
        """New formation has no offset by default."""
        assert formation.offset is None

    def test_default_rotation_mode_is_relative(self, formation):
        """Default rotation mode is 'relative'."""
        assert formation.rotation_mode == 'relative'

    def test_default_members_is_empty_list(self, formation):
        """New formation has empty members list."""
        assert formation.members == []
        assert isinstance(formation.members, list)

    def test_default_active_is_true(self, formation):
        """New formation is active by default."""
        assert formation.active is True


# =============================================================================
# Test: is_master Property
# =============================================================================

class TestIsMasterProperty:
    """Tests for the is_master computed property."""

    def test_is_master_false_with_no_members(self, formation):
        """is_master returns False when members list is empty."""
        assert formation.is_master is False

    def test_is_master_true_with_one_member(self, formation, follower_ship):
        """is_master returns True when one member exists."""
        formation.members.append(follower_ship)

        assert formation.is_master is True

    def test_is_master_true_with_multiple_members(self, formation, follower_ship):
        """is_master returns True with multiple members."""
        follower1 = MagicMock(name="Follower1")
        follower2 = MagicMock(name="Follower2")
        formation.members.extend([follower1, follower2])

        assert formation.is_master is True

    def test_is_master_becomes_false_after_all_members_removed(self, formation):
        """is_master returns False after all members are removed."""
        follower = MagicMock(name="Follower")
        formation.members.append(follower)
        assert formation.is_master is True

        formation.members.remove(follower)

        assert formation.is_master is False


# =============================================================================
# Test: is_member Property
# =============================================================================

class TestIsMemberProperty:
    """Tests for the is_member computed property."""

    def test_is_member_false_with_no_master(self, formation):
        """is_member returns False when master is None."""
        assert formation.is_member is False

    def test_is_member_true_with_master(self, formation, master_ship):
        """is_member returns True when master is set."""
        formation.master = master_ship

        assert formation.is_member is True

    def test_is_member_becomes_false_when_master_cleared(self, formation, master_ship):
        """is_member returns False after master is cleared."""
        formation.master = master_ship
        assert formation.is_member is True

        formation.master = None

        assert formation.is_member is False


# =============================================================================
# Test: join() Method
# =============================================================================

class TestJoinFormation:
    """Tests for the join() method."""

    def test_join_sets_master(self, formation, master_ship):
        """join() sets the master reference."""
        offset = Vector2(50, 30)

        formation.join(master_ship, offset)

        assert formation.master is master_ship

    def test_join_sets_offset(self, formation, master_ship):
        """join() sets the offset vector."""
        offset = Vector2(50, 30)

        formation.join(master_ship, offset)

        assert formation.offset == offset

    def test_join_sets_active_true(self, formation, master_ship):
        """join() sets active to True."""
        formation.active = False
        offset = Vector2(50, 30)

        formation.join(master_ship, offset)

        assert formation.active is True

    def test_join_registers_with_master_formation(self, mock_ship, master_ship):
        """join() adds this ship to master's formation.members."""
        formation = ShipFormation(mock_ship)
        offset = Vector2(50, 30)

        formation.join(master_ship, offset)

        assert mock_ship in master_ship.formation.members

    def test_join_does_not_duplicate_in_master_members(self, mock_ship, master_ship):
        """join() doesn't add duplicate entries to master's members."""
        formation = ShipFormation(mock_ship)
        master_ship.formation.members.append(mock_ship)  # Already in list
        offset = Vector2(50, 30)

        formation.join(master_ship, offset)

        assert master_ship.formation.members.count(mock_ship) == 1

    def test_join_with_zero_offset(self, formation, master_ship):
        """join() works with zero offset."""
        offset = Vector2(0, 0)

        formation.join(master_ship, offset)

        assert formation.offset == Vector2(0, 0)

    def test_join_with_negative_offset(self, formation, master_ship):
        """join() works with negative offset values."""
        offset = Vector2(-100, -50)

        formation.join(master_ship, offset)

        assert formation.offset == Vector2(-100, -50)


# =============================================================================
# Test: leave() Method
# =============================================================================

class TestLeaveFormation:
    """Tests for the leave() method."""

    def test_leave_clears_master(self, mock_ship, master_ship):
        """leave() clears the master reference."""
        formation = ShipFormation(mock_ship)
        formation.master = master_ship

        formation.leave()

        assert formation.master is None

    def test_leave_sets_active_false(self, mock_ship, master_ship):
        """leave() sets active to False."""
        formation = ShipFormation(mock_ship)
        formation.master = master_ship
        formation.active = True

        formation.leave()

        assert formation.active is False

    def test_leave_removes_from_master_members(self, mock_ship, master_ship):
        """leave() removes this ship from master's formation.members."""
        formation = ShipFormation(mock_ship)
        formation.master = master_ship
        master_ship.formation.members.append(mock_ship)

        formation.leave()

        assert mock_ship not in master_ship.formation.members

    def test_leave_without_master_does_not_raise(self, formation):
        """leave() handles case when already not in a formation."""
        formation.master = None

        # Should not raise
        formation.leave()

        assert formation.master is None
        assert formation.active is False

    def test_leave_when_not_in_master_members_handles_gracefully(self, mock_ship, master_ship):
        """leave() handles case when ship not in master's members list."""
        formation = ShipFormation(mock_ship)
        formation.master = master_ship
        # Note: mock_ship is NOT in master_ship.formation.members

        # Should not raise ValueError
        formation.leave()

        assert formation.master is None


# =============================================================================
# Test: add_member() Method
# =============================================================================

class TestAddMember:
    """Tests for the add_member() method."""

    def test_add_member_adds_to_members_list(self, formation, follower_ship):
        """add_member() adds ship to members list."""
        offset = Vector2(50, 30)

        formation.add_member(follower_ship, offset)

        assert follower_ship in formation.members

    def test_add_member_does_not_duplicate(self, formation, follower_ship):
        """add_member() doesn't add duplicate entries."""
        offset = Vector2(50, 30)
        formation.members.append(follower_ship)

        formation.add_member(follower_ship, offset)

        assert formation.members.count(follower_ship) == 1

    def test_add_member_sets_follower_master(self, mock_ship, follower_ship):
        """add_member() sets follower's formation.master to this ship."""
        formation = ShipFormation(mock_ship)
        offset = Vector2(50, 30)

        formation.add_member(follower_ship, offset)

        assert follower_ship.formation.master is mock_ship

    def test_add_member_sets_follower_offset(self, formation, follower_ship):
        """add_member() sets follower's formation.offset."""
        offset = Vector2(50, 30)

        formation.add_member(follower_ship, offset)

        assert follower_ship.formation.offset == offset

    def test_add_member_sets_follower_active(self, formation, follower_ship):
        """add_member() sets follower's formation.active to True."""
        follower_ship.formation.active = False
        offset = Vector2(50, 30)

        formation.add_member(follower_ship, offset)

        assert follower_ship.formation.active is True

    def test_add_multiple_members(self, formation):
        """add_member() supports adding multiple followers."""
        follower1 = MagicMock(name="Follower1")
        follower1.formation = MagicMock()
        follower2 = MagicMock(name="Follower2")
        follower2.formation = MagicMock()

        formation.add_member(follower1, Vector2(50, 0))
        formation.add_member(follower2, Vector2(-50, 0))

        assert len(formation.members) == 2
        assert follower1 in formation.members
        assert follower2 in formation.members


# =============================================================================
# Test: remove_member() Method
# =============================================================================

class TestRemoveMember:
    """Tests for the remove_member() method."""

    def test_remove_member_removes_from_list(self, formation, follower_ship):
        """remove_member() removes ship from members list."""
        formation.members.append(follower_ship)

        formation.remove_member(follower_ship)

        assert follower_ship not in formation.members

    def test_remove_member_clears_follower_master(self, formation, follower_ship):
        """remove_member() clears follower's formation.master."""
        formation.members.append(follower_ship)
        follower_ship.formation.master = formation.ship

        formation.remove_member(follower_ship)

        assert follower_ship.formation.master is None

    def test_remove_member_sets_follower_inactive(self, formation, follower_ship):
        """remove_member() sets follower's formation.active to False."""
        formation.members.append(follower_ship)
        follower_ship.formation.active = True

        formation.remove_member(follower_ship)

        assert follower_ship.formation.active is False

    def test_remove_nonexistent_member_handles_gracefully(self, formation, follower_ship):
        """remove_member() handles removing non-member without error."""
        # follower_ship is NOT in formation.members

        # Should not raise ValueError
        formation.remove_member(follower_ship)

    def test_remove_all_members_makes_not_master(self, formation):
        """Removing all members makes is_master return False."""
        follower1 = MagicMock(name="Follower1")
        follower1.formation = MagicMock()
        follower2 = MagicMock(name="Follower2")
        follower2.formation = MagicMock()

        formation.members.extend([follower1, follower2])
        assert formation.is_master is True

        formation.remove_member(follower1)
        formation.remove_member(follower2)

        assert formation.is_master is False


# =============================================================================
# Test: Edge Cases - Empty Formation
# =============================================================================

class TestEmptyFormationEdgeCases:
    """Tests for empty formation scenarios."""

    def test_empty_formation_is_not_master(self, formation):
        """Empty formation is not a master."""
        assert formation.is_master is False

    def test_empty_formation_has_no_members(self, formation):
        """Empty formation has zero members."""
        assert len(formation.members) == 0

    def test_can_iterate_empty_members(self, formation):
        """Can safely iterate over empty members list."""
        count = 0
        for _ in formation.members:
            count += 1

        assert count == 0


# =============================================================================
# Test: Edge Cases - Single Ship
# =============================================================================

class TestSingleShipEdgeCases:
    """Tests for single ship scenarios."""

    def test_solo_ship_is_not_master(self, formation):
        """Solo ship (no members) is not a master."""
        assert formation.is_master is False

    def test_solo_ship_is_not_member(self, formation):
        """Solo ship (no master) is not a member."""
        assert formation.is_member is False

    def test_solo_ship_can_become_master(self, formation, follower_ship):
        """Solo ship becomes master when member added."""
        assert formation.is_master is False

        formation.add_member(follower_ship, Vector2(50, 0))

        assert formation.is_master is True

    def test_solo_ship_can_become_member(self, formation, master_ship):
        """Solo ship becomes member when joining formation."""
        assert formation.is_member is False

        formation.join(master_ship, Vector2(50, 0))

        assert formation.is_member is True


# =============================================================================
# Test: Formation Positioning
# =============================================================================

class TestFormationPositioning:
    """Tests for formation offset and positioning."""

    def test_offset_preserves_vector_values(self, formation, master_ship):
        """Offset vector values are preserved correctly."""
        offset = Vector2(123.45, -67.89)

        formation.join(master_ship, offset)

        assert formation.offset.x == pytest.approx(123.45)
        assert formation.offset.y == pytest.approx(-67.89)

    def test_different_followers_can_have_different_offsets(self):
        """Multiple followers can have unique offsets."""
        master = MagicMock(name="Master")
        master.formation = MagicMock()
        master.formation.members = []

        follower1 = MagicMock(name="Follower1")
        follower1.formation = MagicMock()
        follower2 = MagicMock(name="Follower2")
        follower2.formation = MagicMock()

        master_formation = ShipFormation(master)

        master_formation.add_member(follower1, Vector2(50, 0))
        master_formation.add_member(follower2, Vector2(-50, 0))

        assert follower1.formation.offset == Vector2(50, 0)
        assert follower2.formation.offset == Vector2(-50, 0)


# =============================================================================
# Test: Rotation Mode
# =============================================================================

class TestRotationMode:
    """Tests for rotation mode settings."""

    def test_default_rotation_mode(self, formation):
        """Default rotation mode is 'relative'."""
        assert formation.rotation_mode == 'relative'

    def test_set_rotation_mode_fixed(self, formation):
        """Can set rotation mode to 'fixed'."""
        formation.rotation_mode = 'fixed'

        assert formation.rotation_mode == 'fixed'

    def test_rotation_mode_can_be_changed(self, formation):
        """Rotation mode can be changed after initialization."""
        assert formation.rotation_mode == 'relative'

        formation.rotation_mode = 'fixed'
        assert formation.rotation_mode == 'fixed'

        formation.rotation_mode = 'relative'
        assert formation.rotation_mode == 'relative'


# =============================================================================
# Test: Bidirectional Relationship Consistency
# =============================================================================

class TestBidirectionalRelationships:
    """Tests ensuring bidirectional relationships stay consistent."""

    def test_join_creates_bidirectional_relationship(self, mock_ship, master_ship):
        """join() creates relationship in both directions."""
        formation = ShipFormation(mock_ship)

        formation.join(master_ship, Vector2(50, 0))

        # Follower -> Master
        assert formation.master is master_ship
        # Master -> Follower
        assert mock_ship in master_ship.formation.members

    def test_add_member_creates_bidirectional_relationship(self, mock_ship, follower_ship):
        """add_member() creates relationship in both directions."""
        formation = ShipFormation(mock_ship)

        formation.add_member(follower_ship, Vector2(50, 0))

        # Master -> Follower
        assert follower_ship in formation.members
        # Follower -> Master
        assert follower_ship.formation.master is mock_ship

    def test_leave_clears_bidirectional_relationship(self, mock_ship, master_ship):
        """leave() clears relationship in both directions."""
        formation = ShipFormation(mock_ship)
        formation.join(master_ship, Vector2(50, 0))

        formation.leave()

        # Follower -> Master cleared
        assert formation.master is None
        # Master -> Follower cleared
        assert mock_ship not in master_ship.formation.members

    def test_remove_member_clears_bidirectional_relationship(self, mock_ship, follower_ship):
        """remove_member() clears relationship in both directions."""
        formation = ShipFormation(mock_ship)
        formation.add_member(follower_ship, Vector2(50, 0))

        formation.remove_member(follower_ship)

        # Master -> Follower cleared
        assert follower_ship not in formation.members
        # Follower -> Master cleared
        assert follower_ship.formation.master is None


# =============================================================================
# Test: Active State Management
# =============================================================================

class TestActiveStateManagement:
    """Tests for active state behavior."""

    def test_join_activates_formation(self, formation, master_ship):
        """join() sets active to True."""
        formation.active = False

        formation.join(master_ship, Vector2(50, 0))

        assert formation.active is True

    def test_leave_deactivates_formation(self, formation, master_ship):
        """leave() sets active to False."""
        formation.join(master_ship, Vector2(50, 0))
        assert formation.active is True

        formation.leave()

        assert formation.active is False

    def test_add_member_activates_follower(self, formation, follower_ship):
        """add_member() sets follower's active to True."""
        follower_ship.formation.active = False

        formation.add_member(follower_ship, Vector2(50, 0))

        assert follower_ship.formation.active is True

    def test_remove_member_deactivates_follower(self, formation, follower_ship):
        """remove_member() sets follower's active to False."""
        formation.add_member(follower_ship, Vector2(50, 0))
        assert follower_ship.formation.active is True

        formation.remove_member(follower_ship)

        assert follower_ship.formation.active is False


# =============================================================================
# Test: Ships Without Formation Attribute (hasattr checks)
# =============================================================================

class TestShipsWithoutFormationAttribute:
    """Tests for handling ships that may not have formation attribute."""

    def test_join_handles_master_without_formation_attr(self, formation):
        """join() handles master ship without formation attribute."""
        master_without_formation = MagicMock(spec=[])  # No 'formation' attribute

        # Should not raise AttributeError
        formation.join(master_without_formation, Vector2(50, 0))

        assert formation.master is master_without_formation

    def test_leave_handles_master_without_formation_attr(self, formation):
        """leave() handles master without formation attribute."""
        master_without_formation = MagicMock(spec=[])  # No 'formation' attribute
        formation.master = master_without_formation

        # Should not raise AttributeError
        formation.leave()

        assert formation.master is None

    def test_add_member_handles_ship_without_formation_attr(self, formation):
        """add_member() handles ship without formation attribute."""
        follower_without_formation = MagicMock(spec=[])  # No 'formation' attribute

        # Should not raise AttributeError
        formation.add_member(follower_without_formation, Vector2(50, 0))

        assert follower_without_formation in formation.members

    def test_remove_member_handles_ship_without_formation_attr(self, formation):
        """remove_member() handles ship without formation attribute."""
        follower_without_formation = MagicMock(spec=[])  # No 'formation' attribute
        formation.members.append(follower_without_formation)

        # Should not raise AttributeError
        formation.remove_member(follower_without_formation)

        assert follower_without_formation not in formation.members
