"""
Tests for GameSession with multi-empire support
"""
from game.strategy.engine.game_session import GameSession
from game.strategy.engine.game_config import GameConfig, PlayerConfig, THEME_DEFAULTS


class TestGameSessionMultiEmpire:
    """Tests for GameSession multi-empire support"""

    def test_game_session_creates_n_empires(self):
        """GameSession creates empire for each PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert len(session.empires) == 3
        assert session.empires[0].name == "Empire A"
        assert session.empires[1].name == "Empire B"
        assert session.empires[2].name == "Empire C"

    def test_game_session_assigns_empire_ids_sequentially(self):
        """Empire IDs are 0, 1, 2, 3 based on player order"""
        config = GameConfig(
            players=[
                PlayerConfig(name=f"Empire {i}", theme=THEME_DEFAULTS[i][0], color=THEME_DEFAULTS[i][1])
                for i in range(4)
            ],
            system_count=10
        )

        session = GameSession(config=config)

        for i, empire in enumerate(session.empires):
            assert empire.id == i

    def test_game_session_sets_human_player_ids(self):
        """human_player_ids reflects is_human flag from PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Human 1", theme="Federation", color=(255, 0, 0), is_human=True),
                PlayerConfig(name="AI 1", theme="Atlantians", color=(0, 255, 0), is_human=False),
                PlayerConfig(name="Human 2", theme="Romulans", color=(0, 0, 255), is_human=True),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert len(session.human_player_ids) == 2
        assert 0 in session.human_player_ids  # Human 1
        assert 1 not in session.human_player_ids  # AI 1
        assert 2 in session.human_player_ids  # Human 2

    def test_game_session_initial_scenario_distributes_colonies(self):
        """Each empire gets a starting colony in different system"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        # Each empire should have at least one colony
        for empire in session.empires:
            assert len(empire.colonies) > 0, f"Empire {empire.name} has no colonies"

        # Colonies should be in different systems
        colony_systems = set()
        for empire in session.empires:
            for colony in empire.colonies:
                # Find which system this colony is in
                for system in session.systems:
                    if colony in system.planets:
                        colony_systems.add(system)
                        break

        assert len(colony_systems) == 2, "Empires should start in different systems"

    def test_game_session_3_player_setup(self):
        """3-player game creates exactly 3 empires with colonies"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert len(session.empires) == 3

        # All should have colonies
        for empire in session.empires:
            assert len(empire.colonies) > 0

    def test_game_session_4_player_setup(self):
        """4-player game creates exactly 4 empires with colonies"""
        config = GameConfig(
            players=[
                PlayerConfig(name=f"Empire {i}", theme=THEME_DEFAULTS[i][0], color=THEME_DEFAULTS[i][1])
                for i in range(4)
            ],
            system_count=15  # Need enough systems for 4 players
        )

        session = GameSession(config=config)

        assert len(session.empires) == 4

        # All should have colonies
        for empire in session.empires:
            assert len(empire.colonies) > 0

    def test_game_session_empire_themes_match_config(self):
        """Empire themes are set from PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Fed", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Atl", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert session.empires[0].empire_theme_id == "Federation"
        assert session.empires[1].empire_theme_id == "Atlantians"

    def test_game_session_empire_colors_match_config(self):
        """Empire colors are set from PlayerConfig"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Red", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Green", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert session.empires[0].color == (255, 0, 0)
        assert session.empires[1].color == (0, 255, 0)

    def test_game_session_serialization_preserves_empires(self):
        """GameSession serialization preserves all empire data"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Empire A", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Empire B", theme="Atlantians", color=(0, 255, 0)),
                PlayerConfig(name="Empire C", theme="Romulans", color=(0, 0, 255)),
            ],
            system_count=10
        )

        original = GameSession(config=config)
        original.turn_number = 5

        data = original.to_dict()
        restored = GameSession.from_dict(data)

        assert len(restored.empires) == 3
        assert restored.turn_number == 5
        assert restored.empires[0].name == "Empire A"
        assert restored.empires[1].name == "Empire B"
        assert restored.empires[2].name == "Empire C"

    def test_game_session_1_player_setup(self):
        """1-player game creates single empire"""
        config = GameConfig(
            players=[
                PlayerConfig(name="Solo Empire", theme="Federation", color=(255, 0, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert len(session.empires) == 1
        assert len(session.empires[0].colonies) > 0


class TestGameSessionActiveEmpire:
    """`session.active_empire` is the active turn-taker (BUG-125).

    Renamed from `player_empire`, which never rotated and silently broke
    every authorization gate that read it in hot-seat. The rename to
    `active_empire` makes the rotation contract explicit, and
    `StrategyGameStateManager.advance_turn` pushes the rotation into the
    session each turn change."""

    def test_active_empire_defaults_to_first_empire(self):
        """At session creation, active_empire is empires[0] (the first
        player's turn comes first)."""
        config = GameConfig(
            players=[
                PlayerConfig(name="First", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Second", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert session.active_empire is session.empires[0]

    def test_active_empire_rotates_on_assignment(self):
        """`session.active_empire = next_empire` rotates the active empire."""
        config = GameConfig(
            players=[
                PlayerConfig(name="First", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Second", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)
        session.active_empire = session.empires[1]

        assert session.active_empire is session.empires[1]

    def test_enemy_empire_reference(self):
        """enemy_empire convenience reference points to second empire."""
        config = GameConfig(
            players=[
                PlayerConfig(name="First", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Second", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )

        session = GameSession(config=config)

        assert session.enemy_empire is session.empires[1]

    def test_active_empire_round_trips_through_save_load(self):
        """`active_empire` defaults to empires[0] after `from_dict` —
        rotation is the UI's concern (rotation index lives in
        StrategyScreen.current_player_index, which is also the source
        that pushes into session.active_empire on advance_turn).
        Save/load explicitly reset to empires[0] so loading a save
        always lands on player 1's turn."""
        config = GameConfig(
            players=[
                PlayerConfig(name="First", theme="Federation", color=(255, 0, 0)),
                PlayerConfig(name="Second", theme="Atlantians", color=(0, 255, 0)),
            ],
            system_count=10
        )
        session = GameSession(config=config)
        session.active_empire = session.empires[1]

        data = session.to_dict()
        restored = GameSession.from_dict(data)

        assert restored.active_empire is restored.empires[0]


class TestGameSessionInitializationErrorBoundary:
    """PROJ-381 Phase 2 (B-11): GameSession.__init__ must wrap
    GameInitializer.initialize failures so the session lands in a
    deterministic null-object state rather than partially constructed.
    """

    def test_initializer_failure_leaves_session_null_object(self, monkeypatch):
        """When GameInitializer.initialize raises, the session must:

        - Re-raise as SessionInitializationError preserving __cause__.
        - Land in a deterministic state: galaxy=None, empires=[],
          systems=[], human_player_ids=[], active_empire=None — never
          have these attributes "missing" / undefined.
        """
        import pytest
        from game.core.exceptions import (
            SessionInitializationError,
            ValidationException,
        )
        from game.strategy.engine import game_initializer as gi_module

        def _boom_initialize(*_args, **_kwargs):
            raise ValidationException("simulated initializer crash")

        monkeypatch.setattr(
            gi_module.GameInitializer, "initialize", staticmethod(_boom_initialize)
        )

        config = GameConfig(
            players=[
                PlayerConfig(name="A", theme="Federation", color=(255, 0, 0)),
            ],
            system_count=4,
        )

        session = GameSession.__new__(GameSession)
        with pytest.raises(SessionInitializationError) as exc_info:
            GameSession.__init__(session, config=config)

        # __cause__ chained.
        assert isinstance(exc_info.value.__cause__, ValidationException)
        # Null-object state — every attribute set to a deterministic value.
        assert session.galaxy is None
        assert session.empires == []
        assert session.systems == []
        assert session.human_player_ids == []
        assert session.active_empire is None
