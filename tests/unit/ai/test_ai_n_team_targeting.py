"""Tests for N-team AI targeting (PROJ-269 Phase 3 Task 3.4).

Confirms `AIController._find_enemies_in_radius` treats every non-self team
as equally hostile. No target preference between teams — each non-self
team is a valid enemy, and the closest is selected.
"""
from game.ai.ai_factory import AIControllerFactory
from game.simulation.systems.battle_engine import BattleEngine
from game.simulation.systems.battle_end_conditions import TickLimitCondition


def _ship(fresh_registries, name: str, team_id: int, x: float = 0, y: float = 0):
    from game.simulation.entities.ship import Ship

    return Ship(
        name=name,
        x=x,
        y=y,
        color=(200, 200, 200),
        team_id=team_id,
        ship_class="Escort",
        theme_id="Federation",
        registries=fresh_registries,
    )


def test_ai_finds_enemies_across_all_non_self_teams(fresh_registries):
    """In a 3-team setup, team 0's AI must see BOTH team 1 and team 2
    ships as valid enemies (no alliance / target preference)."""
    engine = BattleEngine(ai_factory=AIControllerFactory())

    me = _ship(fresh_registries, "Me", 0, 0, 0)
    team1_foe = _ship(fresh_registries, "Foe1", 1, 200, 0)
    team2_foe = _ship(fresh_registries, "Foe2", 2, -200, 0)

    engine.start_teams(
        {0: [me], 1: [team1_foe], 2: [team2_foe]},
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    engine.update()

    # Locate my AI controller and ask it for enemies.
    my_ai = next(
        ai for ai in engine.ai_controllers
        if getattr(ai, "ship", None) is not None
        and getattr(ai.ship, "ship", None) is me
    )
    enemies = my_ai._find_enemies_in_radius()
    enemy_names = {
        getattr(e, "name", None) for e in enemies
    }
    assert "Foe1" in enemy_names
    assert "Foe2" in enemy_names


def test_ai_does_not_target_own_team_members(fresh_registries):
    engine = BattleEngine(ai_factory=AIControllerFactory())

    me = _ship(fresh_registries, "Me", 0, 0, 0)
    friend = _ship(fresh_registries, "Friend", 0, 100, 0)
    foe = _ship(fresh_registries, "Foe", 1, -100, 0)

    engine.start_teams(
        {0: [me, friend], 1: [foe]},
        seed=0,
        end_condition=TickLimitCondition(max_ticks=1),
    )
    engine.update()

    my_ai = next(
        ai for ai in engine.ai_controllers
        if getattr(ai.ship, "ship", None) is me
    )
    enemies = my_ai._find_enemies_in_radius()
    names = {getattr(e, "name", None) for e in enemies}
    assert "Friend" not in names
    assert "Foe" in names
