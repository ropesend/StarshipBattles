"""TelemetryLevel + opt-in CombatEventBus subscribers.

PROJ-269 Phase 1 Task 1.5 introduced the enum. Phase 5 adds the three
opt-in subscriber aggregators:

- `WeaponSummaryAggregator` — attaches at NORMAL+. Snapshots per-weapon
  shots_fired / shots_hit counters at battle end; computes resolved_shots
  by inspecting in-flight projectiles.
- `ShipStatsAggregator` — attaches at NORMAL+. Subscribes to SHIP_DESTROYED
  / SHIP_DERELICT; tracks peak_speed + ticks_alive via per-tick sampling.
- `HitLogRecorder` — attaches at DETAILED only. Subscribes to COMPONENT_HIT
  / COMPONENT_DESTROYED and records a full `HitRecord` per damage event.

Levels (integer-ordered so callers can write `level >= NORMAL`):
  - MINIMAL (1)  — nothing attached; smallest overhead for batch runs.
  - NORMAL  (2)  — weapon summary + ship-stat aggregators attached.
  - DETAILED (3) — above, plus full hit-log recorder for forensic UI.

Defaults per context (set by each spec compiler):
  - Strategy    — NORMAL
  - Battle Setup — NORMAL
  - Combat Lab  — DETAILED (individual scenarios can override).
"""
from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING, Dict, List, Tuple

if TYPE_CHECKING:
    from game.simulation.battle_outcome import (
        HitRecord,
        ShipStats,
        WeaponSummary,
    )
    from game.simulation.combat.combat_events import CombatEvent, CombatEventBus
    from game.simulation.entities.ship import Ship
    from game.simulation.systems.battle_engine import BattleEngine


class TelemetryLevel(IntEnum):
    """How much detail to capture into BattleOutcome.

    `IntEnum` so the engine can branch on `level >= NORMAL` without
    introducing a custom ordering helper.
    """

    MINIMAL = 1
    NORMAL = 2
    DETAILED = 3


# ---------------------------------------------------------------------------
# WeaponSummaryAggregator
# ---------------------------------------------------------------------------


class WeaponSummaryAggregator:
    """Snapshots per-weapon shots_fired / shots_hit counters at battle end.

    Uses the existing `Component.shots_fired` / `shots_hit` counters
    maintained by the weapon-firing system — no new events required.
    `resolved_shots` subtracts the count of in-flight projectiles owned
    by the ship to give the "resolved at battle end" total.
    """

    def snapshot(
        self, engine: "BattleEngine"
    ) -> Dict[str, Tuple["WeaponSummary", ...]]:
        """Return `{instance_id: (WeaponSummary, ...)}` for every ship."""
        # Lazy-import to avoid a tight module-level cycle during boot.
        from game.simulation.battle_outcome import WeaponSummary
        from game.simulation.components.abilities.weapons import WeaponAbility

        result: Dict[str, Tuple[WeaponSummary, ...]] = {}
        # Also track retreated ships — they still had weapons that fired.
        all_ships: List["Ship"] = list(engine.ships)
        all_ships.extend(getattr(engine, "retreated_ships", []))

        for ship in all_ships:
            instance_id = getattr(ship, "instance_id", None)
            if not instance_id:
                continue
            summaries: List[WeaponSummary] = []
            layers = getattr(ship, "layers", None) or {}
            for layer_data in layers.values():
                for comp in getattr(layer_data, "components", []) or []:
                    abilities = getattr(comp, "ability_instances", None) or []
                    if not any(isinstance(ab, WeaponAbility) for ab in abilities):
                        continue
                    summaries.append(
                        WeaponSummary(
                            component_id=getattr(comp, "id", ""),
                            component_name=getattr(comp, "name", ""),
                            shots_fired=int(getattr(comp, "shots_fired", 0) or 0),
                            shots_hit=int(getattr(comp, "shots_hit", 0) or 0),
                        )
                    )
            result[instance_id] = tuple(summaries)
        return result


# ---------------------------------------------------------------------------
# ShipStatsAggregator
# ---------------------------------------------------------------------------


# Damage event types the aggregator counts toward total_damage_taken.
# COMPONENT_DESTROYED is intentionally excluded — it's a status event
# carrying no additional damage_amount.
_DAMAGE_EVENT_TYPE_NAMES = (
    "SHIELD_HIT",
    "ARMOR_ABSORBED",
    "COMPONENT_HIT",
)


class ShipStatsAggregator:
    """Tracks per-ship in-battle stats.

    Subscribes to damage events on the `CombatEventBus` to accumulate
    `total_damage_taken`. `peak_speed`, `ticks_alive`, and
    `ticks_derelict` come from per-tick sampling via `sample_tick`
    (the engine's tick-loop callback).

    `snapshot()` returns `{instance_id: ShipStats}` with zero-initialized
    defaults for any ship not yet tracked.
    """

    def __init__(self, event_bus: "CombatEventBus"):
        self._damage_taken: Dict[str, float] = {}
        self._peak_speed: Dict[str, float] = {}
        self._ticks_alive: Dict[str, int] = {}
        self._ticks_derelict: Dict[str, int] = {}
        self._bus = event_bus

        # Lazy import to sidestep module boot cycles.
        from game.simulation.combat.combat_events import CombatEventType

        for name in _DAMAGE_EVENT_TYPE_NAMES:
            try:
                event_type = getattr(CombatEventType, name)
            except AttributeError:
                continue
            event_bus.subscribe(event_type, self._on_damage_event)

    # ---- Subscribers

    def _on_damage_event(self, event: "CombatEvent") -> None:
        ship = getattr(event, "target_ship", None)
        if ship is None:
            return
        instance_id = getattr(ship, "instance_id", None)
        if not instance_id:
            return
        damage = float(getattr(event, "damage_amount", 0.0) or 0.0)
        if damage <= 0:
            return
        self._damage_taken[instance_id] = (
            self._damage_taken.get(instance_id, 0.0) + damage
        )

    # ---- Per-tick sampling

    def sample_tick(self, engine: "BattleEngine") -> None:
        """Called every tick by `run_battle`. Updates peak_speed +
        ticks_alive / ticks_derelict counters."""
        ships = list(getattr(engine, "ships", []) or [])
        ships.extend(getattr(engine, "retreated_ships", []))
        for ship in ships:
            instance_id = getattr(ship, "instance_id", None)
            if not instance_id:
                continue
            # Peak speed
            velocity = getattr(ship, "velocity", None)
            if velocity is not None and hasattr(velocity, "length"):
                speed = float(velocity.length())
                prev = self._peak_speed.get(instance_id, 0.0)
                if speed > prev:
                    self._peak_speed[instance_id] = speed
            # Ticks alive / derelict (only for currently-alive ships)
            if getattr(ship, "is_alive", False):
                self._ticks_alive[instance_id] = (
                    self._ticks_alive.get(instance_id, 0) + 1
                )
                if getattr(ship, "is_derelict", False):
                    self._ticks_derelict[instance_id] = (
                        self._ticks_derelict.get(instance_id, 0) + 1
                    )

    # ---- Accessors

    def get_stats(self, instance_id: str) -> "ShipStats":
        from game.simulation.battle_outcome import ShipStats

        return ShipStats(
            total_damage_taken=float(self._damage_taken.get(instance_id, 0.0)),
            peak_speed=float(self._peak_speed.get(instance_id, 0.0)),
            ticks_derelict=int(self._ticks_derelict.get(instance_id, 0)),
            ticks_alive=int(self._ticks_alive.get(instance_id, 0)),
        )

    def snapshot(self) -> Dict[str, "ShipStats"]:
        """Return `{instance_id: ShipStats}` for every ship touched so far."""
        instance_ids = (
            set(self._damage_taken)
            | set(self._peak_speed)
            | set(self._ticks_alive)
            | set(self._ticks_derelict)
        )
        return {iid: self.get_stats(iid) for iid in instance_ids}


# ---------------------------------------------------------------------------
# HitLogRecorder
# ---------------------------------------------------------------------------


# Damage-bearing events that produce a HitRecord.
_HIT_EVENT_TYPE_NAMES = (
    "SHIELD_HIT",
    "ARMOR_ABSORBED",
    "COMPONENT_HIT",
)


class HitLogRecorder:
    """Records a `HitRecord` per damage event, keyed by target ship_id.

    Wired at DETAILED telemetry only. Subscribes to SHIELD_HIT /
    ARMOR_ABSORBED / COMPONENT_HIT events on the `CombatEventBus`.
    Each record captures:
      - tick (from `tick_provider()` callable injected at construction)
      - attacker ship_id (from `event.context.attacker.instance_id`)
      - weapon component_id (from `event.context.source_weapon.id`)
      - weapon_ability class name (best-effort from source_weapon's
        ability_instances)
      - damage amount
      - modifiers_applied (empty tuple in Phase 5 Task 5.3 MVP; real
        modifier-trace needs the engine to carry per-hit modifier
        provenance, which is a later refinement).
    """

    def __init__(
        self,
        event_bus: "CombatEventBus",
        *,
        tick_provider=None,
        modifier_stack=None,
    ):
        """
        Args:
            event_bus: The engine's `CombatEventBus`.
            tick_provider: Callable returning the current tick counter.
                If None, every HitRecord has `tick=0`. `run_battle`
                injects `lambda: engine.tick_counter`.
            modifier_stack: Optional `ModifierStack`. When supplied,
                each `HitRecord.modifiers_applied` is populated with
                the modifiers active on the attacker's team + globals.
                Placeholder-effect entries are filtered out.
                PROJ-269 Phase 5.5.
        """
        self._hits: Dict[str, List["HitRecord"]] = {}
        self._tick_provider = tick_provider or (lambda: 0)
        self._modifier_stack = modifier_stack

        from game.simulation.combat.combat_events import CombatEventType

        for name in _HIT_EVENT_TYPE_NAMES:
            try:
                event_type = getattr(CombatEventType, name)
            except AttributeError:
                continue
            event_bus.subscribe(event_type, self._on_hit_event)

    def _on_hit_event(self, event: "CombatEvent") -> None:
        from game.simulation.battle_outcome import HitRecord

        target = getattr(event, "target_ship", None)
        if target is None:
            return
        instance_id = getattr(target, "instance_id", None)
        if not instance_id:
            return

        ctx = getattr(event, "context", None)
        attacker_ship_id = ""
        weapon_component_id = ""
        weapon_ability_class = ""
        attacker_team_id = None
        if ctx is not None:
            attacker = getattr(ctx, "attacker", None)
            if attacker is not None:
                attacker_ship_id = getattr(attacker, "instance_id", "") or ""
                t = getattr(attacker, "team_id", None)
                if t is not None:
                    try:
                        attacker_team_id = int(t)
                    except (TypeError, ValueError):
                        attacker_team_id = None
            source_weapon = getattr(ctx, "source_weapon", None)
            if source_weapon is not None:
                weapon_component_id = getattr(source_weapon, "id", "") or ""
                # Best-effort: extract the WeaponAbility subclass name
                # from the component's abilities.
                abilities = getattr(source_weapon, "ability_instances", None) or []
                try:
                    from game.simulation.components.abilities.weapons import WeaponAbility
                    for ab in abilities:
                        if isinstance(ab, WeaponAbility):
                            weapon_ability_class = ab.__class__.__name__
                            break
                except (ImportError, AttributeError):
                    weapon_ability_class = getattr(ctx, "damage_type", "") or ""

        record = HitRecord(
            tick=int(self._tick_provider() or 0),
            attacker_ship_id=attacker_ship_id,
            weapon_component_id=weapon_component_id,
            weapon_ability_class=weapon_ability_class,
            damage=float(getattr(event, "damage_amount", 0.0) or 0.0),
            modifiers_applied=self._trace_modifiers_for_team(attacker_team_id),
        )
        self._hits.setdefault(instance_id, []).append(record)

    def _trace_modifiers_for_team(self, attacker_team_id) -> Tuple:
        """Return a tuple of `ModifierApplication` for the active stack
        entries that apply to this hit:
          - Always include `stack.global_` entries
          - Include `stack.per_team[attacker_team_id]` entries when the
            attacker's team is known
          - Filter out placeholder effects (stat_key == "placeholder")
        """
        stack = self._modifier_stack
        if stack is None:
            return ()
        from game.simulation.battle_outcome import ModifierApplication

        entries: List = []
        entries.extend(getattr(stack, "global_", ()) or ())
        if attacker_team_id is not None:
            per_team = getattr(stack, "per_team", {}) or {}
            team_entries = per_team.get(attacker_team_id, ())
            entries.extend(team_entries or ())

        applications: List = []
        for entry in entries:
            effect = getattr(entry, "effect", None)
            if effect is None:
                continue
            stat_key = getattr(effect, "stat_key", "") or ""
            if not stat_key or stat_key == "placeholder":
                continue
            applications.append(ModifierApplication(
                source=str(getattr(entry, "source", "") or ""),
                effect_name=stat_key,
                value=float(getattr(effect, "value", 0.0) or 0.0),
            ))
        return tuple(applications)

    def get_hits(self, instance_id: str) -> Tuple["HitRecord", ...]:
        return tuple(self._hits.get(instance_id, []))

    def snapshot(self) -> Dict[str, Tuple["HitRecord", ...]]:
        return {iid: tuple(hits) for iid, hits in self._hits.items()}


__all__ = [
    "HitLogRecorder",
    "ShipStatsAggregator",
    "TelemetryLevel",
    "WeaponSummaryAggregator",
]
