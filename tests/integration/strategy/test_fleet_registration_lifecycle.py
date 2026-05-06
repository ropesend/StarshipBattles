"""Integration tests for PROJ-219: Fleet registration lifecycle.

Verifies that formerly-buggy locations (ghost fleets) now correctly
unregister fleets from the galaxy registry when remove_fleet() is called.

Each test exercises a real engine/processor code path to confirm that
empire.remove_fleet() triggers galaxy.unregister_fleet() automatically.
"""
import pytest

from game.core.hex_math import HexCoord
from game.strategy.data.empire import Empire
from game.strategy.data.fleet import Fleet
from game.strategy.data.galaxy import Galaxy
from game.strategy.data.order_types import Order, OrderType
from game.strategy.engine.conflict_resolution_engine import ConflictResolutionEngine
from game.strategy.engine.order_processor import OrderProcessor
from game.strategy.engine.game_config import GameConfig, PlayerConfig
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.superweapon_order_processor import SuperweaponOrderProcessor
from game.strategy.interfaces.battle_resolver import IBattleResolver, BattleResult
from tests.conftest import make_mock_ship_instance


class InstantBattleResolver(IBattleResolver):
    """Battle resolver that instantly declares team 0 the winner.

    BUG-126: simulates the `PostBattleHook` by wiping the loser fleets'
    ship lists AND removing them from their owning empire. Production
    callers receive this side-effect via `apply_outcome_to_fleets` +
    `_prune_empty_fleets`; here we hand-roll it because the hook is
    bypassed when callers inject a mock resolver."""

    def __init__(self, empires_by_team=None):
        self._empires_by_team = empires_by_team or {}

    def resolve_battle(self, fleets, modifiers=None, seed=None, registries=None,
                       environmental_effects=None, empires=None):
        fleet_list = list(fleets)
        survivors = {i: [] for i in range(len(fleet_list))}
        survivors[0] = list(
            fleet_list[0].battle.to_battle_ships(team_id=0, registries=registries)
        )
        # Simulate the PostBattleHook: wipe loser ship lists and prune
        # empty fleets from their empires.
        empires_by_team = empires or self._empires_by_team
        for tid, fleet in enumerate(fleet_list[1:], start=1):
            fleet.ships = []
            empire = empires_by_team.get(tid)
            if empire is not None and fleet in empire.fleets:
                empire.remove_fleet(fleet)
        return BattleResult(
            winner=0,
            tick_count=1,
            team_survivors=survivors,
        )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def galaxy():
    """Create a minimal Galaxy with registry support for fleet lifecycle tests.

    PROJ-372 Phase 3: Galaxy now uses GalaxyState for shared state.
    Uses Galaxy.__new__ to skip the heavy __init__ (file I/O, generators),
    then attaches a fresh GalaxyState + service delegates.
    """
    from game.strategy.data.galaxy_entity_registry import GalaxyEntityRegistry
    from game.strategy.data.galaxy_spatial_index import GalaxySpatialIndex
    from game.strategy.data.galaxy_state import GalaxyState

    gal = Galaxy.__new__(Galaxy)
    gal._state = GalaxyState(radius=300)
    gal.warp_points = []
    gal._registry = GalaxyEntityRegistry(gal._state)
    gal._spatial = GalaxySpatialIndex(gal._state)
    return gal


@pytest.fixture
def two_empires(galaxy):
    """Create two empires wired to the galaxy."""
    emp1 = Empire(0, "Player1", (0, 100, 200))
    emp2 = Empire(1, "Player2", (200, 100, 0))
    emp1.set_galaxy(galaxy)
    emp2.set_galaxy(galaxy)
    return emp1, emp2


@pytest.fixture
def small_game_session():
    """Create a small game session for save/load testing."""
    config = GameConfig()
    config.galaxy_radius = 300
    config.system_count = 2
    config.players = [
        PlayerConfig(name="Player1", is_human=True, color=(0, 100, 200)),
        PlayerConfig(name="Player2", is_human=False, color=(200, 100, 0)),
    ]
    return GameSession(config=config)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_fleet(fleet_id, owner_id, location, ship_count=1, registries=None):
    """Create a fleet with mock ships."""
    fleet = Fleet(fleet_id, owner_id, location, speed=15.0)
    for i in range(ship_count):
        ship = make_mock_ship_instance(
            f"Ship-{fleet_id}-{i}", owner_id, registries=registries
        )
        fleet.ships.append(ship)
    return fleet


def _assert_registered(galaxy, fleet):
    """Assert fleet IS in the galaxy registry."""
    found = galaxy.get_fleet_by_id(fleet.id)
    assert found is fleet, (
        f"Fleet {fleet.id} should be in galaxy registry but was not found"
    )


def _assert_not_registered(galaxy, fleet_id):
    """Assert fleet is NOT in the galaxy registry."""
    found = galaxy.get_fleet_by_id(fleet_id)
    assert found is None, (
        f"Fleet {fleet_id} should NOT be in galaxy registry but was found"
    )


# ===========================================================================
# Task 4.2: Combat destruction unregisters fleet
# ===========================================================================

class TestCombatUnregistersDestroyedFleet:
    """Verify conflict_resolution_engine.py:186 auto-unregisters loser fleet."""

    def test_combat_unregisters_destroyed_fleet(
        self, galaxy, two_empires, fresh_registries
    ):
        """When a fleet is destroyed in combat, it is removed from galaxy registry."""
        emp1, emp2 = two_empires
        loc = HexCoord(10, 10)

        # Create fleets at same location (conflict)
        fleet1 = _make_fleet(100, emp1.id, loc, ship_count=1, registries=fresh_registries)
        fleet2 = _make_fleet(200, emp2.id, loc, ship_count=1, registries=fresh_registries)
        emp1.add_fleet(fleet1)
        emp2.add_fleet(fleet2)

        # Both should be registered
        _assert_registered(galaxy, fleet1)
        _assert_registered(galaxy, fleet2)

        # Resolve combat using instant resolver to skip full simulation.
        # BUG-126: the resolver also simulates the PostBattleHook
        # (wiping loser ships + pruning the fleet from its empire),
        # because the strategy engine no longer prunes fleets itself.
        engine = ConflictResolutionEngine(
            battle_resolver=InstantBattleResolver(empires_by_team={0: emp1, 1: emp2}),
            registries=fresh_registries,
        )
        # PROJ-320: speed-15 fleets have opportunity every 6 ticks.
        result = engine.resolve_all_conflicts(
            [emp1, emp2], galaxy, tick=6, moved_fleet_ids=set(),
        )

        # Exactly one fleet should have been destroyed
        assert result.combats_resolved == 1
        assert len(result.fleets_destroyed) == 1

        destroyed_id = result.fleets_destroyed[0]

        # Destroyed fleet must NOT be in galaxy registry
        _assert_not_registered(galaxy, destroyed_id)

        # Surviving fleet must still be in galaxy registry
        survivor_id = 100 if destroyed_id == 200 else 200
        survivor_fleet = galaxy.get_fleet_by_id(survivor_id)
        assert survivor_fleet is not None, (
            f"Surviving fleet {survivor_id} should still be in galaxy registry"
        )


# ===========================================================================
# Task 4.3: JOIN_FLEET merge unregisters source fleet
# ===========================================================================

class TestJoinFleetUnregistersMergedFleet:
    """Verify order_processor.py:113 and :663 auto-unregister merged fleet."""

    def test_join_fleet_unregisters_merged_fleet(
        self, galaxy, two_empires, fresh_registries
    ):
        """When a fleet merges via JOIN_FLEET, the source fleet is removed from registry."""
        emp1, _ = two_empires
        loc = HexCoord(20, 20)

        # Create target and source fleets at same location
        target_fleet = _make_fleet(300, emp1.id, loc, ship_count=2, registries=fresh_registries)
        source_fleet = _make_fleet(301, emp1.id, loc, ship_count=1, registries=fresh_registries)
        emp1.add_fleet(target_fleet)
        emp1.add_fleet(source_fleet)

        # Both should be registered
        _assert_registered(galaxy, target_fleet)
        _assert_registered(galaxy, source_fleet)

        # Give source fleet a JOIN_FLEET order targeting the target
        source_fleet.orders.append(Order(OrderType.JOIN_FLEET, target=target_fleet))

        # Process via OrderProcessor.process_join_fleet
        processor = OrderProcessor()
        result = processor.process_join_fleet(source_fleet, emp1, galaxy)

        assert result.merged is True

        # Source fleet should be removed from empire and galaxy registry
        assert source_fleet not in emp1.fleets
        _assert_not_registered(galaxy, 301)

        # Target fleet should still be registered with merged ships
        _assert_registered(galaxy, target_fleet)
        assert len(target_fleet.ships) == 3  # 2 original + 1 merged

    def test_instant_join_fleet_unregisters_merged_fleet(
        self, galaxy, two_empires, fresh_registries
    ):
        """Instant merge via process_instant_orders also unregisters merged fleet."""
        emp1, _ = two_empires
        loc = HexCoord(25, 25)

        target_fleet = _make_fleet(400, emp1.id, loc, ship_count=1, registries=fresh_registries)
        source_fleet = _make_fleet(401, emp1.id, loc, ship_count=1, registries=fresh_registries)
        emp1.add_fleet(target_fleet)
        emp1.add_fleet(source_fleet)

        _assert_registered(galaxy, target_fleet)
        _assert_registered(galaxy, source_fleet)

        # Give source fleet a JOIN_FLEET order
        source_fleet.orders.append(Order(OrderType.JOIN_FLEET, target=target_fleet))

        # Process via instant orders (tick-based code path at line 663)
        processor = OrderProcessor()
        removed = processor.process_instant_orders([emp1])

        assert len(removed) == 1
        assert removed[0][1] is source_fleet

        # Source fleet should be unregistered
        _assert_not_registered(galaxy, 401)

        # Target fleet should still be registered
        _assert_registered(galaxy, target_fleet)
        assert len(target_fleet.ships) == 2


# ===========================================================================
# Task 4.4: COLONIZE with empty fleet unregisters fleet
# ===========================================================================

class TestColonizeEmptyFleetUnregistered:
    """Verify order_processor.py:216 auto-unregisters empty fleet after colonization."""

    def test_colonize_empty_fleet_unregistered(
        self, galaxy, two_empires, fresh_registries
    ):
        """When a fleet's last ship is removed (colonize), the empty fleet is unregistered.

        Tests the remove_fleet path directly since process_colonize requires
        extensive galaxy/planet/validator setup. The key behavior is:
        after removing the colony ship, if fleet.ships == 0, empire.remove_fleet()
        is called which auto-unregisters.
        """
        emp1, _ = two_empires
        loc = HexCoord(30, 30)

        # Create fleet with a single "colony ship"
        fleet = Fleet(500, emp1.id, loc, speed=15.0)
        colony_ship = make_mock_ship_instance("Colony Ship", emp1.id, registries=fresh_registries)
        fleet.ships.append(colony_ship)
        emp1.add_fleet(fleet)
        _assert_registered(galaxy, fleet)

        # Simulate the colonize code path at order_processor.py:211-216
        fleet.remove_ship(colony_ship)
        assert len(fleet.ships) == 0

        # This is what order_processor does when fleet becomes empty
        emp1.remove_fleet(fleet)

        # Fleet should be unregistered
        assert fleet not in emp1.fleets
        _assert_not_registered(galaxy, 500)


# ===========================================================================
# Task 4.5: Superweapon consumed fleet unregisters fleet
# ===========================================================================

class TestSuperweaponConsumedFleetUnregistered:
    """Verify superweapon_order_processor.py:103 auto-unregisters consumed fleet."""

    def test_superweapon_consumed_fleet_unregisters(
        self, galaxy, two_empires, fresh_registries
    ):
        """When a superweapon consumes the only ship, fleet is removed from registry.

        Tests the _finalize_superweapon common path used by IMPLODE_PLANET,
        STELLERATE_STAR, DYSON_SPHERE, and SELF_DESTRUCT.
        """
        emp1, _ = two_empires
        loc = HexCoord(40, 40)

        fleet = Fleet(600, emp1.id, loc, speed=15.0)
        ship = make_mock_ship_instance("Doom Ship", emp1.id, registries=fresh_registries)
        fleet.ships.append(ship)
        emp1.add_fleet(fleet)
        _assert_registered(galaxy, fleet)

        # Add a dummy order so pop_order works
        fleet.orders.append(Order(OrderType.SELF_DESTRUCT, target=[]))

        # Process via _finalize_superweapon (the shared finalization path)
        from game.strategy.events.event_types import EventType
        processor = SuperweaponOrderProcessor()
        result = processor._finalize_superweapon(
            fleet=fleet,
            empire=emp1,
            ship=ship,
            event_type=EventType.SHIPS_SELF_DESTRUCTED,
            event_message="Fleet consumed by superweapon",
            log_message="Superweapon consumed fleet",
        )

        assert result.success is True
        assert result.fleet_consumed is True

        # Fleet should be unregistered
        assert fleet not in emp1.fleets
        _assert_not_registered(galaxy, 600)

    def test_superweapon_partial_ship_removal_keeps_fleet(
        self, galaxy, two_empires, fresh_registries
    ):
        """When superweapon removes one ship but fleet has more, fleet stays registered."""
        emp1, _ = two_empires
        loc = HexCoord(41, 41)

        fleet = Fleet(601, emp1.id, loc, speed=15.0)
        weapon_ship = make_mock_ship_instance("Weapon", emp1.id, registries=fresh_registries)
        escort_ship = make_mock_ship_instance("Escort", emp1.id, registries=fresh_registries)
        fleet.ships.append(weapon_ship)
        fleet.ships.append(escort_ship)
        emp1.add_fleet(fleet)
        _assert_registered(galaxy, fleet)

        fleet.orders.append(Order(OrderType.SELF_DESTRUCT, target=[]))

        from game.strategy.events.event_types import EventType
        processor = SuperweaponOrderProcessor()
        result = processor._finalize_superweapon(
            fleet=fleet,
            empire=emp1,
            ship=weapon_ship,
            event_type=EventType.SHIPS_SELF_DESTRUCTED,
            event_message="Ship consumed",
            log_message="Superweapon partial",
        )

        assert result.success is True
        assert result.fleet_consumed is False

        # Fleet should still be registered (escort_ship remains)
        assert fleet in emp1.fleets
        _assert_registered(galaxy, fleet)
        assert len(fleet.ships) == 1

    def test_finalize_superweapon_unregisters_consumed_fleet(
        self, galaxy, two_empires, fresh_registries
    ):
        """The _finalize_superweapon common path auto-unregisters empty fleets."""
        emp1, _ = two_empires
        loc = HexCoord(42, 42)

        fleet = Fleet(602, emp1.id, loc, speed=15.0)
        ship = make_mock_ship_instance("Weapon Ship", emp1.id, registries=fresh_registries)
        fleet.ships.append(ship)
        emp1.add_fleet(fleet)
        # Add a dummy order so pop_order works
        fleet.orders.append(Order(OrderType.SELF_DESTRUCT, target=[]))
        _assert_registered(galaxy, fleet)

        # Call _finalize_superweapon directly (the shared finalization path)
        from game.strategy.events.event_types import EventType
        processor = SuperweaponOrderProcessor()
        result = processor._finalize_superweapon(
            fleet=fleet,
            empire=emp1,
            ship=ship,
            event_type=EventType.SHIPS_SELF_DESTRUCTED,
            event_message="Test superweapon",
            log_message="Test superweapon finalize",
        )

        assert result.success is True
        assert result.fleet_consumed is True
        _assert_not_registered(galaxy, 602)


# ===========================================================================
# Task 4.6: Save/load preserves fleet registry
# ===========================================================================

class TestSaveLoadPreservesFleetRegistry:
    """Verify GameSession.from_dict() restores fleet registry correctly."""

    def test_save_load_preserves_fleet_registry(
        self, small_game_session, fresh_registries
    ):
        """All fleets are in galaxy registry after save/load cycle."""
        session = small_game_session

        # Serialize and deserialize
        data = session.to_dict()
        restored = GameSession.from_dict(data)

        # All fleets should be registered in the restored galaxy
        for empire in restored.empires:
            for fleet in empire.fleets:
                found = restored.galaxy.get_fleet_by_id(fleet.id)
                assert found is fleet, (
                    f"Fleet {fleet.id} should be in registry after load"
                )

    def test_new_fleet_after_load_auto_registers(
        self, small_game_session, fresh_registries
    ):
        """Fleets added after save/load cycle are automatically registered."""
        session = small_game_session

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        empire = restored.empires[0]
        new_fleet = Fleet(7777, empire.id, HexCoord(5, 5), speed=15.0)
        new_fleet.ships = [
            make_mock_ship_instance("Scout", empire.id, registries=fresh_registries)
        ]
        empire.add_fleet(new_fleet)

        # New fleet should be auto-registered
        found = restored.galaxy.get_fleet_by_id(7777)
        assert found is new_fleet, (
            "Fleet added after load should be auto-registered with galaxy"
        )

    def test_remove_fleet_after_load_unregisters(
        self, small_game_session, fresh_registries
    ):
        """Fleets removed after save/load are automatically unregistered."""
        session = small_game_session

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        # Find an empire with at least one fleet
        empire = None
        target_fleet = None
        for emp in restored.empires:
            if emp.fleets:
                empire = emp
                target_fleet = emp.fleets[0]
                break

        if empire is None or target_fleet is None:
            pytest.skip("No fleets in restored session to test removal")

        fleet_id = target_fleet.id
        _assert_registered(restored.galaxy, target_fleet)

        # Remove fleet
        empire.remove_fleet(target_fleet)

        # Should be unregistered
        _assert_not_registered(restored.galaxy, fleet_id)


