"""
Battle Results Data Extraction

Pure data extraction from a `BattleOutcome` DTO into frozen dataclasses
for the results screen. No pygame dependency — fully testable.

PROJ-270 Phase 4.5: rewritten to consume `BattleOutcome` (post-PROJ-269
unified entry) instead of reading from a live `BattleEngine`. This
closes the visual-mode half of the "every battle produces a
BattleOutcome that the UI consumes" acceptance criterion.
"""
from dataclasses import dataclass
from typing import Any, List

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
    return_destination: str = "battle_setup"


def extract_battle_results(
    outcome: Any,
    return_destination: str = "battle_setup",
) -> BattleResults:
    """Extract battle results from a `BattleOutcome`.

    PROJ-270 Phase 4.5: function signature changed from
    `(engine, return_destination)` → `(outcome, return_destination)`.
    The outcome is the simulation-layer DTO produced by
    `run_battle(spec)` / `BattleController.get_outcome()`.

    Args:
        outcome: `BattleOutcome` instance with completed battle data.
        return_destination: Where to navigate after results screen.

    Returns:
        BattleResults with all ship and team statistics.
    """
    from game.simulation.battle_outcome import ShipStatus

    ship_results: List[ShipResult] = []
    team_summaries: List[TeamSummary] = []

    for team in outcome.teams:
        team_ship_results: List[ShipResult] = []
        for ship_outcome in team.ships:
            weapons = [
                WeaponStats(
                    name=w.component_name,
                    shots_fired=w.shots_fired,
                    shots_hit=w.shots_hit,
                    accuracy=(w.shots_hit / w.shots_fired) if w.shots_fired > 0 else 0.0,
                )
                for w in ship_outcome.weapons
            ]
            total_fired = sum(w.shots_fired for w in weapons)
            total_hit = sum(w.shots_hit for w in weapons)

            is_alive = ship_outcome.status in (
                ShipStatus.SURVIVED,
                ShipStatus.DERELICT,
            )
            is_derelict = ship_outcome.status == ShipStatus.DERELICT

            result = ShipResult(
                name=ship_outcome.name or ship_outcome.instance_id,
                team_id=team.team_id,
                is_alive=is_alive,
                is_derelict=is_derelict,
                hp=ship_outcome.hp,
                max_hp=ship_outcome.max_hp,
                hp_percent=(
                    ship_outcome.hp / ship_outcome.max_hp * 100
                    if ship_outcome.max_hp > 0 else 0.0
                ),
                current_shields=ship_outcome.current_shields,
                max_shields=ship_outcome.max_shields,
                weapons=weapons,
                total_shots_fired=total_fired,
                total_shots_hit=total_hit,
                overall_accuracy=(total_hit / total_fired) if total_fired > 0 else 0.0,
            )
            ship_results.append(result)
            team_ship_results.append(result)

        team_summaries.append(_build_team_summary(team.team_id, team_ship_results))

    winner = _derive_winner(team_summaries)

    return BattleResults(
        winner=winner,
        tick_count=outcome.duration_ticks,
        duration_seconds=outcome.duration_ticks * PhysicsConfig.TICK_RATE,
        teams=team_summaries,
        ships=ship_results,
        return_destination=return_destination,
    )


def _build_team_summary(team_id: int, ship_results: List[ShipResult]) -> TeamSummary:
    """Build aggregate team statistics."""
    alive = sum(1 for s in ship_results if s.is_alive and not s.is_derelict)
    derelict = sum(1 for s in ship_results if s.is_alive and s.is_derelict)
    destroyed = sum(1 for s in ship_results if not s.is_alive)
    total_fired = sum(s.total_shots_fired for s in ship_results)
    total_hit = sum(s.total_shots_hit for s in ship_results)

    return TeamSummary(
        team_id=team_id,
        total_ships=len(ship_results),
        ships_alive=alive,
        ships_derelict=derelict,
        ships_destroyed=destroyed,
        total_shots_fired=total_fired,
        total_shots_hit=total_hit,
        overall_accuracy=(total_hit / total_fired) if total_fired > 0 else 0.0,
    )


def _derive_winner(team_summaries: List[TeamSummary]) -> int:
    """Derive winner from team summaries.

    A team 'wins' if it has survivors AND all other teams are wiped.
    Returns -1 for a draw (no survivors anywhere, or multiple teams
    with survivors — which shouldn't happen in a concluded battle).
    """
    teams_with_survivors = [
        t for t in team_summaries
        if t.ships_alive > 0 or t.ships_derelict > 0
    ]
    if len(teams_with_survivors) == 1:
        return teams_with_survivors[0].team_id
    return -1
