"""TacticalMineResolver — PROJ-FMS-B Phase 3.

Per-tick tactical-layer mine behaviour. Owns:

- Mine entities placed on the tactical map at scatter coordinates
  derived from the strategic-layer ``mine_group``.
- Per-tick warhead-proximity trigger rolls against enemy ships.
- Per-tick laserhead range-trigger rolls (with the same threshold gate
  used at the strategic layer).
- Mine HP (from ``Hull`` component) — mines destroyed by point-defense
  fire are removed without detonating.
- Per-tick chance scaling so that the same enemy passing through a
  mined area in tactical combat has roughly equivalent expected damage
  as in a strategic-pass entry. Scaling strategy:
  ``per_tick_chance = strategic_p_trigger / expected_ticks_in_proximity``
  with ``expected_ticks_in_proximity`` derived from ship speed and the
  warhead-proximity radius (see ``decisions.md``).

This module intentionally lives in :mod:`game.simulation.systems` so
the per-tick loop in :class:`BattleEngine` can hook it cleanly. The
strategic-layer mine_group is the source of truth for inventory and
scatter; this resolver mirrors the inventory to per-tick consumption
state and writes consumed-inventory deltas back to the mine_group at
the end of the battle.
"""
from __future__ import annotations

import logging
import math
import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Mine entity (tactical placement)
# ---------------------------------------------------------------------------


@dataclass
class TacticalMineEntity:
    """A single mine placed on the tactical map.

    Attributes:
        position: ``(x, y)`` tactical coords.
        owner_id: Empire id of the mine's owner.
        source_mine_group_id: Strategic-layer mine_group id (for cleanup).
        warhead_damage: Sum of all Warhead damages on the source design.
        laserhead_attrs: Laserhead ability dict (None if not a laserhead mine).
        hp: Current hull HP (from the Hull component).
        max_hp: Initial hull HP.
        consumed: True once the mine has detonated / been destroyed.
        sensitivity: 'LOW' / 'MED' / 'HIGH' from the mine_group.
        threshold: Laserhead expected-hit-chance threshold from the mine_group.
        mine_dict: The original CarriedVehicle-shaped dict (for cleanup
            writeback to the strategic mine_group).
    """

    position: Tuple[float, float]
    owner_id: int
    source_mine_group_id: Any
    warhead_damage: float
    laserhead_attrs: Optional[Dict[str, Any]]
    hp: float = 30.0
    max_hp: float = 30.0
    consumed: bool = False
    sensitivity: str = "MED"
    threshold: float = 0.30
    mine_dict: Optional[Dict[str, Any]] = None
    # Per-mine cooldown so a mine that fails a per-tick roll won't
    # spam its trigger every frame; gives ships a meaningful window
    # to move out of proximity.
    cooldown_until_tick: int = 0


@dataclass
class TacticalMineEvent:
    """Per-tick mine event reported by the resolver."""

    mine_entity: TacticalMineEntity
    target_ship: Any
    damage: float
    pass_kind: str  # "warhead" or "laserhead"
    hit: bool
    tick: int


# ---------------------------------------------------------------------------
# Resolver
# ---------------------------------------------------------------------------


class TacticalMineResolver:
    """Per-tick mine behaviour at the tactical layer.

    Usage::

        resolver = TacticalMineResolver(
            mine_entities=[...],     # built from mine_group state at battle start
            balance=load_minefield_balance(),
            rng=random.Random(seed),
        )
        # Once per tick:
        events = resolver.tick(tick=engine.tick_counter,
                                enemy_ships=enemy_team_ships,
                                damage_calculator=DamageCalculator(),
                                event_bus=engine.event_bus)
    """

    # PROJ-FMS-B Phase 3: per-tick scaling tuning. ``expected_ticks_in_proximity``
    # converts a strategic-pass chance into a per-tick chance such that
    # the ship spends approximately this many ticks inside the proximity
    # radius and the integrated expected damage matches the strategic pass.
    #
    # PROJ-FMS-B audit Fix 5: the runtime value now flows from
    # ``MinefieldBalance.tactical.expected_ticks_in_proximity`` (set via
    # ``data/balance/mines.json``). This class constant remains as the
    # documented default when no balance is supplied or the field is
    # missing from the balance file.
    DEFAULT_EXPECTED_TICKS_IN_PROXIMITY = 50

    def __init__(
        self,
        mine_entities: Optional[List[TacticalMineEntity]] = None,
        balance: Optional[Any] = None,
        rng: Optional[random.Random] = None,
    ) -> None:
        self.mines: List[TacticalMineEntity] = list(mine_entities or [])
        if balance is None:
            # Local import to avoid cross-layer issue at module load.
            from game.strategy.engine.minefield_balance import (
                load_minefield_balance,
            )
            balance = load_minefield_balance()
        self._balance = balance
        self._rng = rng if rng is not None else random.Random()

    # ------------------------------------------------------------------
    # Per-tick entry point
    # ------------------------------------------------------------------

    def tick(
        self,
        tick: int,
        enemy_ships: List[Any],
        damage_calculator: Optional[Any] = None,
        event_bus: Optional[Any] = None,
    ) -> List[TacticalMineEvent]:
        """Run one tick of mine resolution.

        Args:
            tick: Current battle tick.
            enemy_ships: Ships not owned by the same empire as the mines.
                The caller is responsible for filtering by team.
            damage_calculator: Optional :class:`DamageCalculator`. When
                provided, mine damage is routed through the full
                shield/armor/hull pipeline. When None, direct HP
                decrement is used (mirrors the strategic-layer
                fallback).
            event_bus: Optional event bus (currently unused; reserved
                for emitting CombatEvent rows).

        Returns:
            List of :class:`TacticalMineEvent` rows describing
            detonations and laserhead fires this tick.
        """
        events: List[TacticalMineEvent] = []
        alive_mines: List[TacticalMineEntity] = []

        # Per-tick chance is the same for both passes — derived from
        # strategic_p_trigger / DEFAULT_EXPECTED_TICKS_IN_PROXIMITY.
        for mine in self.mines:
            if mine.consumed or mine.hp <= 0:
                continue

            # If the mine just fired, sit on its cooldown.
            if tick < mine.cooldown_until_tick:
                alive_mines.append(mine)
                continue

            mine_consumed = self._evaluate_mine_against_ships(
                mine=mine,
                tick=tick,
                enemy_ships=enemy_ships,
                damage_calculator=damage_calculator,
                events=events,
            )
            if not mine_consumed:
                alive_mines.append(mine)

        self.mines = alive_mines
        return events

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _evaluate_mine_against_ships(
        self,
        mine: TacticalMineEntity,
        tick: int,
        enemy_ships: List[Any],
        damage_calculator: Optional[Any],
        events: List[TacticalMineEvent],
    ) -> bool:
        """Evaluate a single mine against the enemy-ship list.

        Returns True if the mine was consumed and should be dropped
        from the active list.
        """
        radius = float(self._balance.tactical.warhead_proximity_radius)

        # Find closest enemy ship within proximity / beam range.
        nearest_for_warhead = None
        nearest_d2_w = math.inf
        nearest_for_laser = None
        nearest_d2_l = math.inf

        laser_range = (
            float(mine.laserhead_attrs.get("range", 0.0))
            if mine.laserhead_attrs else 0.0
        )

        for ship in enemy_ships:
            if not getattr(ship, "is_alive", True):
                continue
            sx = float(getattr(ship, "x", 0.0))
            sy = float(getattr(ship, "y", 0.0))
            dx = sx - mine.position[0]
            dy = sy - mine.position[1]
            d2 = dx * dx + dy * dy
            if mine.warhead_damage > 0.0 and d2 <= radius * radius and d2 < nearest_d2_w:
                nearest_d2_w = d2
                nearest_for_warhead = ship
            if mine.laserhead_attrs is not None and laser_range > 0.0 \
                    and d2 <= laser_range * laser_range and d2 < nearest_d2_l:
                nearest_d2_l = d2
                nearest_for_laser = ship

        # Warhead pass first.
        if mine.warhead_damage > 0.0 and nearest_for_warhead is not None:
            triggered = self._warhead_per_tick_roll(mine, nearest_for_warhead)
            if triggered:
                applied = self._apply_damage(
                    nearest_for_warhead, mine.warhead_damage, damage_calculator,
                )
                events.append(TacticalMineEvent(
                    mine_entity=mine,
                    target_ship=nearest_for_warhead,
                    damage=applied,
                    pass_kind="warhead",
                    hit=True,
                    tick=tick,
                ))
                mine.consumed = True
                return True

        # Laserhead pass second.
        if mine.laserhead_attrs is not None and nearest_for_laser is not None:
            fired, hit, applied = self._laserhead_per_tick(
                mine, nearest_for_laser, damage_calculator,
            )
            if fired:
                events.append(TacticalMineEvent(
                    mine_entity=mine,
                    target_ship=nearest_for_laser,
                    damage=applied,
                    pass_kind="laserhead",
                    hit=hit,
                    tick=tick,
                ))
                mine.consumed = True  # consume_on_fire
                return True

        # No trigger — short cooldown so we don't spam rolls every tick
        # for stationary mines / slow-moving ships.
        mine.cooldown_until_tick = tick + 1
        return False

    def _warhead_per_tick_roll(
        self, mine: TacticalMineEntity, ship: Any,
    ) -> bool:
        """Per-tick warhead trigger roll vs ``ship``.

        Per-tick chance is the strategic p_trigger divided by the
        expected number of ticks the ship spends in proximity.
        """
        # Local import to avoid cycles at module load.
        from game.strategy.engine.minefield_resolver import (
            _get_ship_scores,
            _sigmoid,
        )

        size_score, maneuver_score = _get_ship_scores(ship)
        wh = self._balance.warhead_trigger
        bulk = -size_score
        x = (wh.k_size * bulk) - (wh.k_eva * maneuver_score) - wh.bias
        base = _sigmoid(x)
        sens = self._balance.sensitivity_factor(mine.sensitivity)
        strategic_p = max(0.0, min(0.9999, sens * base))

        # PROJ-FMS-B audit Fix 5: pull the divisor from the balance file
        # instead of the class constant. Falls back to the class constant
        # if the balance object is missing the field (defensive default).
        expected_ticks = int(
            getattr(
                self._balance.tactical,
                "expected_ticks_in_proximity",
                self.DEFAULT_EXPECTED_TICKS_IN_PROXIMITY,
            )
        )
        per_tick = strategic_p / max(1, expected_ticks)
        per_tick = max(self._balance.tactical.min_tick_chance, per_tick)
        return self._rng.random() < per_tick

    def _laserhead_per_tick(
        self,
        mine: TacticalMineEntity,
        ship: Any,
        damage_calculator: Optional[Any],
    ) -> Tuple[bool, bool, float]:
        """Per-tick laserhead trigger + standard hit roll.

        Returns ``(fired, hit, applied_damage)``.
        """
        from game.strategy.engine.minefield_resolver import _sigmoid

        attrs = mine.laserhead_attrs or {}
        base_accuracy = float(attrs.get("base_accuracy", 1.0))
        falloff = float(attrs.get("accuracy_falloff", 0.001))
        beam_range = float(attrs.get("range", 0.0))
        damage = float(attrs.get("damage", 0.0))

        # Distance to target.
        sx = float(getattr(ship, "x", 0.0))
        sy = float(getattr(ship, "y", 0.0))
        dx = sx - mine.position[0]
        dy = sy - mine.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > beam_range:
            return (False, False, 0.0)

        try:
            defense_score = float(getattr(ship, "total_defense_score", 0.0) or 0.0)
        except Exception:  # Intentional broad catch: stat lookup can vary across Ship implementations.
            defense_score = 0.0

        net_score = base_accuracy - (falloff * distance + defense_score)
        expected_hit_chance = _sigmoid(net_score)

        if expected_hit_chance < mine.threshold:
            return (False, False, 0.0)

        # Threshold passed — roll the standard beam hit.
        roll = self._rng.random()
        hit = roll < expected_hit_chance
        applied = 0.0
        if hit:
            applied = self._apply_damage(ship, damage, damage_calculator)
        return (True, hit, applied)

    def _apply_damage(
        self,
        ship: Any,
        damage: float,
        damage_calculator: Optional[Any],
    ) -> float:
        """Apply mine damage to a tactical-layer Ship.

        When ``damage_calculator`` is provided this routes through the
        full :class:`DamageCalculator.apply_damage` pipeline (shields,
        armor, hull layers). Otherwise falls back to a direct HP
        decrement so the resolver still works in test fixtures with
        lightweight ship stand-ins.
        """
        if damage_calculator is not None and hasattr(ship, "layers"):
            try:
                damage_calculator.apply_damage(ship, float(damage))
                return float(damage)
            except Exception as exc:  # Intentional broad catch: per-tick mine damage must never break the battle loop on a single misbehaving target.
                logger.warning(
                    "TacticalMineResolver: damage pipeline failed for ship "
                    "%s (%s); falling back to direct HP decrement",
                    getattr(ship, "name", "?"),
                    exc,
                )
        # Fallback path.
        current = float(getattr(ship, "hp", 0.0) or 0.0)
        new_hp = max(0.0, current - float(damage))
        applied = current - new_hp
        if hasattr(ship, "hp"):
            ship.hp = new_hp
        if new_hp <= 0.0 and hasattr(ship, "is_alive"):
            ship.is_alive = False
        return applied

    # ------------------------------------------------------------------
    # Sector-scatter construction
    # ------------------------------------------------------------------

    @classmethod
    def from_mine_group(
        cls,
        mine_group: Any,
        balance: Optional[Any] = None,
        battle_boundary: Optional[Tuple[float, float, float, float]] = None,
        rng: Optional[random.Random] = None,
    ) -> "TacticalMineResolver":
        """Construct a resolver from a strategic ``MineGroup``.

        Args:
            mine_group: The strategic-layer :class:`MineGroup` instance.
            balance: Optional :class:`MinefieldBalance`.
            battle_boundary: Optional ``(xmin, ymin, xmax, ymax)``
                bounding rect for the tactical map. When provided,
                mines are scattered uniformly inside the box using
                the mine_group's stored seed. When None, the stored
                ``mine_positions`` are used as-is (already produced at
                strategic-launch time using the fallback radius).
            rng: Optional :class:`random.Random` for the per-tick
                trigger rolls (independent of the scatter PRNG).
        """
        if balance is None:
            from game.strategy.engine.minefield_balance import (
                load_minefield_balance,
            )
            balance = load_minefield_balance()

        # PROJ-431 Phase 2: inventory comes directly off the typed
        # ``MineGroup.mines`` list — no synthetic carrier. Materialise
        # each entry as a dict so the existing per-mine extraction
        # helpers (``_sum_warhead_damage`` / ``_extract_laserhead`` /
        # ``_extract_hull_hp``) keep operating on the
        # ``CarriedVehicle.to_dict()`` shape.
        mines_data: List[Dict[str, Any]] = [
            cv.to_dict() for cv in getattr(mine_group, "mines", [])
        ]

        # Choose scatter coordinates.
        if battle_boundary is not None and mine_group.scatter_seed is not None:
            positions = _scatter_in_box(
                count=len(mines_data),
                seed=int(mine_group.scatter_seed),
                box=battle_boundary,
            )
        else:
            positions = list(getattr(mine_group, "mine_positions", []) or [])
            # Pad / trim to match inventory length.
            while len(positions) < len(mines_data):
                positions.append((0.0, 0.0))
            positions = positions[: len(mines_data)]

        sensitivity = str(getattr(mine_group, "sensitivity", "MED"))
        threshold = float(
            getattr(mine_group, "expected_hit_chance_threshold", 0.30)
        )

        entities: List[TacticalMineEntity] = []
        for mine_dict, pos in zip(mines_data, positions):
            wh_damage = _sum_warhead_damage(mine_dict)
            lh_attrs = _extract_laserhead(mine_dict)
            hp = _extract_hull_hp(mine_dict)
            entities.append(TacticalMineEntity(
                position=pos,
                owner_id=int(mine_group.owner_id),
                source_mine_group_id=mine_group.id,
                warhead_damage=wh_damage,
                laserhead_attrs=lh_attrs,
                hp=hp,
                max_hp=hp,
                sensitivity=sensitivity,
                threshold=threshold,
                mine_dict=mine_dict,
            ))
        return cls(mine_entities=entities, balance=balance, rng=rng)

    def writeback_to_mine_group(self, mine_group: Any) -> None:
        """Update the strategic ``MineGroup``'s inventory after the battle.

        Drops any mine entries marked ``consumed`` (or HP <= 0) from
        the group's typed ``mines`` list. Mirrors the strategic-layer
        consumption semantics so post-battle the strategic state
        matches what happened tactically.

        PROJ-FMS-B audit Fix 6: always replaces the inventory — even
        when the resulting list is empty. Pre-fix the function silently
        no-op'd when every mine was consumed, leaving a zombie
        inventory on the strategic mine_group.

        PROJ-431 Phase 2: writeback now operates directly on
        ``mine_group.mines``. Survivors are matched by positional index
        (mine entities and the strategic mines list were zipped 1:1 at
        :meth:`from_mine_group` construction time).
        """
        mines_attr = getattr(mine_group, "mines", None)
        if mines_attr is None:
            return
        current_mines = list(mines_attr)
        kept_indices = {
            i for i, m in enumerate(self.mines)
            if not m.consumed and m.hp > 0 and i < len(current_mines)
        }
        mine_group.mines = [
            cv for i, cv in enumerate(current_mines) if i in kept_indices
        ]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sum_warhead_damage(mine_dict: Dict[str, Any]) -> float:
    """Total Warhead damage on a mine design."""
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    total = 0.0
    for _name, layer in layers.items():
        for comp in (layer.get("components") if isinstance(layer, dict) else []) or []:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            wh = abilities.get("Warhead")
            if wh is None:
                continue
            if isinstance(wh, dict):
                total += float(wh.get("damage", 0.0))
            elif isinstance(wh, (int, float)):
                total += float(wh)
    return total


def _extract_laserhead(mine_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Return the first Laserhead ability dict on a mine, or None."""
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    for _name, layer in layers.items():
        for comp in (layer.get("components") if isinstance(layer, dict) else []) or []:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            lh = abilities.get("Laserhead")
            if lh is None:
                continue
            if isinstance(lh, dict):
                return dict(lh)
            elif isinstance(lh, (int, float)):
                return {"damage": float(lh)}
    return None


def _extract_hull_hp(mine_dict: Dict[str, Any]) -> float:
    """Sum of StructuralIntegrity hp values on the mine design."""
    design = mine_dict.get("design_data") or {}
    layers = design.get("layers") or {}
    total = 0.0
    for _name, layer in layers.items():
        for comp in (layer.get("components") if isinstance(layer, dict) else []) or []:
            if not isinstance(comp, dict):
                continue
            abilities = comp.get("abilities") or {}
            si = abilities.get("StructuralIntegrity")
            if si is None:
                continue
            if isinstance(si, dict):
                total += float(si.get("hp", 0.0))
            elif isinstance(si, (int, float)):
                total += float(si)
    if total == 0.0:
        total = 30.0  # Conservative default for mines without explicit hull.
    return total


def _scatter_in_box(
    count: int,
    seed: int,
    box: Tuple[float, float, float, float],
) -> List[Tuple[float, float]]:
    """Uniformly sample ``count`` positions inside ``box``."""
    rng = random.Random(seed)
    xmin, ymin, xmax, ymax = box
    positions: List[Tuple[float, float]] = []
    for _ in range(count):
        positions.append((
            rng.uniform(xmin, xmax),
            rng.uniform(ymin, ymax),
        ))
    return positions


__all__ = [
    "TacticalMineEntity",
    "TacticalMineEvent",
    "TacticalMineResolver",
]
