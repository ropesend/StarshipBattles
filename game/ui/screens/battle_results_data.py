"""
Battle Results Data Extraction

Pure data extraction from BattleEngine state into frozen dataclasses
for the results screen. No pygame dependency — fully testable.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from game.core.config import PhysicsConfig


@dataclass(frozen=True)
class WeaponStats:
    """Per-weapon accuracy statistics."""
    name: str
    shots_fired: int
    shots_hit: int
    accuracy: float  # 0.0 to 1.0


@dataclass(frozen=True)
class ShipResult:
    """Post-battle statistics for a single ship."""
    name: str
    team_id: int
    is_alive: bool
    is_derelict: bool
    hp: float
    max_hp: float
    hp_percent: float
    current_shields: float
    max_shields: float
    weapons: List[WeaponStats]
    total_shots_fired: int
    total_shots_hit: int
    overall_accuracy: float


@dataclass(frozen=True)
class TeamSummary:
    """Aggregate statistics for a team."""
    team_id: int
    total_ships: int
    ships_alive: int  # alive and not derelict
    ships_derelict: int
    ships_destroyed: int
    total_shots_fired: int
    total_shots_hit: int
    overall_accuracy: float


@dataclass(frozen=True)
class BattleResults:
    """Complete post-battle results."""
    winner: int  # 0, 1, or -1 for draw
    tick_count: int
    duration_seconds: float
    teams: List[TeamSummary]
    ships: List[ShipResult]
    is_test_mode: bool


def extract_battle_results(engine: Any, is_test_mode: bool) -> BattleResults:
    """Extract battle results from engine state.

    Args:
        engine: BattleEngine instance with completed battle
        is_test_mode: Whether this was a Combat Lab test

    Returns:
        BattleResults with all ship and team statistics
    """
    ship_results = []
    for ship in engine.ships:
        weapons = _extract_weapons(ship)
        total_fired = sum(w.shots_fired for w in weapons)
        total_hit = sum(w.shots_hit for w in weapons)

        ship_results.append(ShipResult(
            name=ship.name,
            team_id=ship.team_id,
            is_alive=ship.is_alive,
            is_derelict=ship.is_derelict,
            hp=ship.hp,
            max_hp=ship.max_hp,
            hp_percent=(ship.hp / ship.max_hp * 100) if ship.max_hp > 0 else 0.0,
            current_shields=ship.current_shields,
            max_shields=ship.max_shields,
            weapons=weapons,
            total_shots_fired=total_fired,
            total_shots_hit=total_hit,
            overall_accuracy=(total_hit / total_fired) if total_fired > 0 else 0.0,
        ))

    # Build team summaries
    team_ids = sorted({s.team_id for s in ship_results})
    teams = [_build_team_summary(tid, ship_results) for tid in team_ids]

    return BattleResults(
        winner=engine.get_winner(),
        tick_count=engine.tick_counter,
        duration_seconds=engine.tick_counter * PhysicsConfig.TICK_RATE,
        teams=teams,
        ships=ship_results,
        is_test_mode=is_test_mode,
    )


def _extract_weapons(ship: Any) -> List[WeaponStats]:
    """Extract weapon statistics from a ship's components."""
    weapons = []
    for comp in ship.get_all_components():
        if getattr(comp, 'type', None) == "Weapon":
            fired = getattr(comp, 'shots_fired', 0)
            hit = getattr(comp, 'shots_hit', 0)
            weapons.append(WeaponStats(
                name=comp.name,
                shots_fired=fired,
                shots_hit=hit,
                accuracy=(hit / fired) if fired > 0 else 0.0,
            ))
    return weapons


def _build_team_summary(team_id: int, ship_results: List[ShipResult]) -> TeamSummary:
    """Build aggregate team statistics."""
    team_ships = [s for s in ship_results if s.team_id == team_id]
    alive = sum(1 for s in team_ships if s.is_alive and not s.is_derelict)
    derelict = sum(1 for s in team_ships if s.is_alive and s.is_derelict)
    destroyed = sum(1 for s in team_ships if not s.is_alive)
    total_fired = sum(s.total_shots_fired for s in team_ships)
    total_hit = sum(s.total_shots_hit for s in team_ships)

    return TeamSummary(
        team_id=team_id,
        total_ships=len(team_ships),
        ships_alive=alive,
        ships_derelict=derelict,
        ships_destroyed=destroyed,
        total_shots_fired=total_fired,
        total_shots_hit=total_hit,
        overall_accuracy=(total_hit / total_fired) if total_fired > 0 else 0.0,
    )
