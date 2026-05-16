"""CarrierAIController — PROJ-FMS-C audit Fix 1.

Production caller for :meth:`BattleEngine.launch_fighters_in_battle`.

Replaces the legacy ``VehicleLaunchAbility`` auto-launch path that lived in
:class:`WeaponFiringSystem` ``_process_hangar_launch`` (removed in the
same audit-fix pass). The decision in
``Projects/active_projects/PROJ-FMS-C/decisions.md`` was "explicit
player / AI action surface" rather than weapon-system auto-launch;
this controller is that AI action surface, mirroring the AI-driven
auto-launch behaviour the legacy path provided but going through the
new design-instance launch path so spawned fighters keep their full
components / weapons / HP.

Behavior per tick:
  1. Run the base :class:`AIController` ``update()`` — the carrier still
     moves and fires its standard weapons.
  2. If the carrier has any active ``TacticalFighterLaunchAbility``
     component, any ``fighter``-type ``CarriedVehicle`` in
     ``carried_items``, an enemy within launch range, and the per-controller
     cooldown has elapsed, pop up to ``capacity_per_action`` fighters and
     call ``engine.launch_fighters_in_battle(carrier, [CarriedVehicle, ...])``.

Cooldown is tick-based on ``cycle_time`` to mirror the legacy
:class:`VehicleLaunchAbility` semantics (cycle_time × ticks-per-second).
We approximate as ``cycle_time`` seconds at 60 Hz; the controller doesn't
have access to a per-battle tick-rate so this is a fixed approximation —
production carriers shipped today all use a 5–6 second cycle which is
well above the per-tick noise floor.
"""
from __future__ import annotations

import logging
import random
from typing import Any, List, Optional, TYPE_CHECKING

from game.ai.controller import AIController
from game.core.config import BattleTuning
from game.strategy.data.carried_vehicle import CarriedVehicle

if TYPE_CHECKING:
    from game.ai.interfaces.controllable import ShipControllableAdapter
    from game.engine.spatial import SpatialGrid
    from game.simulation.systems.battle_engine import BattleEngine


logger = logging.getLogger(__name__)


# Approximation: BattleEngine runs at PhysicsConfig.TICK_RATE (60 Hz). The
# tactical-launch cycle_time is specified in seconds; convert to ticks.
_TICKS_PER_SECOND_DEFAULT: float = 60.0


class CarrierAIController(AIController):
    """AI controller for carrier-class ships.

    Subclasses :class:`AIController` so the carrier keeps full ship-AI
    behavior (movement policy, weapon firing, target acquisition). Adds
    a per-tick auto-launch hook that calls
    :meth:`BattleEngine.launch_fighters_in_battle` when conditions are
    met.

    Args:
        ship: The :class:`ShipControllableAdapter` wrapping the carrier.
        grid: Spatial grid for enemy detection.
        enemy_team_id: Enemy team id (legacy single-team field; the
            base class also supports multi-team via ``team_id``).
        rng: Per-battle seeded RNG.
        engine: Owning :class:`BattleEngine`. Required for the
            auto-launch path; falsy ``engine`` disables auto-launch
            cleanly (the controller falls back to plain :class:`AIController`
            behavior).
        launch_radius: Optional override for the "enemy within range"
            check. Defaults to :attr:`BattleTuning.TARGET_QUERY_RADIUS`.
    """

    def __init__(
        self,
        ship: 'ShipControllableAdapter',
        grid: 'SpatialGrid',
        enemy_team_id: int,
        *,
        rng: Optional[random.Random] = None,
        engine: Optional['BattleEngine'] = None,
        launch_radius: Optional[float] = None,
    ) -> None:
        super().__init__(ship, grid, enemy_team_id, rng=rng)
        self._engine = engine
        self._launch_radius: float = (
            launch_radius if launch_radius is not None
            else float(BattleTuning.TARGET_QUERY_RADIUS)
        )
        # Tick-based cooldown counter. Decrements each ``update``; a launch
        # resets it to ``cycle_time * TICKS_PER_SECOND``.
        self._cooldown_ticks: int = 0

    def update(self) -> None:
        """Run one tick of carrier AI.

        Order: base AI (movement / targeting / weapon-firing trigger), then
        auto-launch check. Base-AI failures are logged and swallowed so a
        bad sub-system can't break the launch path or the battle loop.
        """
        try:
            super().update()
        except Exception:  # Intentional broad catch: base AI sub-systems (target eval, behavior trees) raise across many edge cases; the auto-launch hook must still run on subsequent ticks.
            logger.exception(
                "CarrierAIController: base AIController.update() raised; "
                "continuing to auto-launch check."
            )
        if not self._ship_is_alive():
            return
        if self._cooldown_ticks > 0:
            self._cooldown_ticks -= 1
            return
        if self._engine is None:
            return
        self._maybe_launch_fighter_wave()
        # PROJ-FMS-D Phase 1: same cooldown gate also throttles satellite
        # launches — a carrier that can launch both fighters and
        # satellites will alternate via the same per-tick cycle.
        if self._cooldown_ticks > 0:
            return
        self._maybe_launch_satellite_wave()

    # ------------------------------------------------------------------
    # Auto-launch — fighters
    # ------------------------------------------------------------------

    def _maybe_launch_fighter_wave(self) -> None:
        """Pop up to ``capacity_per_action`` fighters and request a launch."""
        self._maybe_launch_wave(
            ability_name="TacticalFighterLaunch",
            vehicle_type="fighter",
            launch_method_name="launch_fighters_in_battle",
        )

    # ------------------------------------------------------------------
    # Auto-launch — satellites (PROJ-FMS-D Phase 1)
    # ------------------------------------------------------------------

    def _maybe_launch_satellite_wave(self) -> None:
        """Pop up to ``capacity_per_action`` satellites and request a launch."""
        self._maybe_launch_wave(
            ability_name="TacticalSatelliteLaunch",
            vehicle_type="satellite",
            launch_method_name="launch_satellites_in_battle",
        )

    # ------------------------------------------------------------------
    # Shared launch helper
    # ------------------------------------------------------------------

    def _maybe_launch_wave(
        self,
        *,
        ability_name: str,
        vehicle_type: str,
        launch_method_name: str,
    ) -> None:
        """Generic per-vehicle-type tactical launch.

        PROJ-FMS-D Phase 1: extracted from the original fighter-only path
        so satellites and fighters share one implementation. Each call
        site declares the ability name, the CarriedVehicle's
        ``vehicle_type``, and the BattleEngine method that performs the
        spawn.
        """
        ability = self._find_tactical_launch_ability(ability_name)
        if ability is None:
            return

        capacity = int(getattr(ability, "capacity_per_action", 0) or 0)
        if capacity <= 0:
            return
        cycle_time = float(getattr(ability, "cycle_time", 0.0) or 0.0)
        if cycle_time <= 0:
            return

        carrier = self._unwrap_ship()
        if carrier is None:
            return

        if not self._enemy_in_launch_radius(carrier):
            return

        cvs = self._pop_cvs(carrier, vehicle_type, capacity)
        if not cvs:
            return

        launch_method = getattr(self._engine, launch_method_name, None)
        if launch_method is None:
            logger.warning(
                "CarrierAIController: engine missing %s; cannot launch "
                "%s wave from carrier=%s",
                launch_method_name,
                vehicle_type,
                getattr(carrier, "name", "?"),
            )
            return
        try:
            launch_method(carrier, cvs)
        except Exception:  # Intentional broad catch: AI auto-launch must not break the battle loop on a bad design payload.
            logger.exception(
                "CarrierAIController: %s raised for carrier=%s; "
                "%d CVs were popped but not spawned.",
                launch_method_name,
                getattr(carrier, "name", "?"),
                len(cvs),
            )
            return

        # Reset cooldown. Mirrors the legacy VehicleLaunchAbility cycle.
        self._cooldown_ticks = max(1, int(cycle_time * _TICKS_PER_SECOND_DEFAULT))

    def _find_tactical_launch_ability(
        self, ability_name: str = "TacticalFighterLaunch",
    ) -> Optional[Any]:
        """Return the first active tactical-launch ability, or None.

        Walks the carrier's components. Uses the ``has_ability`` /
        ``get_ability`` surface so the controller stays decoupled from
        the ability class — the ability name is passed by string so
        both ``TacticalFighterLaunch`` and ``TacticalSatelliteLaunch``
        share this path.
        """
        carrier = self._unwrap_ship()
        if carrier is None:
            return None
        iter_components = getattr(carrier, "iter_components", None)
        if iter_components is None:
            return None
        try:
            for _layer, comp in iter_components():
                if not getattr(comp, "is_active", True):
                    continue
                if not getattr(comp, "is_operational", True):
                    continue
                if not comp.has_ability(ability_name):
                    continue
                ab = comp.get_ability(ability_name)
                if ab is not None:
                    return ab
        except Exception:  # Intentional broad catch: component-iter on minimal stubs raises across many shapes; treat as "no launch ability".
            return None
        return None

    def _enemy_in_launch_radius(self, carrier: Any) -> bool:
        """Cheap spatial-grid check: any live enemy inside ``_launch_radius``."""
        my_pos = getattr(carrier, "position", None)
        if my_pos is None:
            return False
        try:
            candidates = self.grid.query_radius_exact(my_pos, self._launch_radius)
        except Exception:  # Intentional broad catch: grid lookups on stub fixtures may raise; treat as "no enemy".
            return False
        my_team = getattr(carrier, "team_id", None)
        for obj in candidates:
            if not getattr(obj, "is_alive", False):
                continue
            if getattr(obj, "is_derelict", False):
                continue
            obj_team = getattr(obj, "team_id", None)
            if obj_team is None or obj_team == my_team:
                continue
            return True
        return False

    @staticmethod
    def _pop_fighter_cvs(carrier: Any, max_count: int) -> List[CarriedVehicle]:
        """Pop up to ``max_count`` fighter ``CarriedVehicle``s from the carrier.

        Thin wrapper around :meth:`_pop_cvs` for the legacy fighter-only
        callers (used by the carrier-AI integration tests that pre-date
        PROJ-FMS-D's generalisation).
        """
        return CarrierAIController._pop_cvs(carrier, "fighter", max_count)

    @staticmethod
    def _pop_cvs(
        carrier: Any, vehicle_type: str, max_count: int,
    ) -> List[CarriedVehicle]:
        """Pop up to ``max_count`` ``CarriedVehicle``s of ``vehicle_type``.

        PROJ-FMS-D Phase 1: generalised pop so the fighter and satellite
        launch paths share one implementation. Mutates
        ``carrier.carried_items`` — popped entries are removed.
        """
        carried = getattr(carrier, "carried_items", None)
        if not carried:
            return []
        popped: List[CarriedVehicle] = []
        remaining: List[Any] = []
        vt = vehicle_type.lower()
        for item in carried:
            if len(popped) >= max_count:
                remaining.append(item)
                continue
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != vt:
                remaining.append(item)
                continue
            popped.append(cv)
        if popped:
            try:
                carrier.carried_items = remaining
            except Exception:  # Intentional broad catch: stubs may set carried_items as a property; ignore and let the next tick retry.
                pass
        return popped

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _unwrap_ship(self) -> Optional[Any]:
        """Reach through the controllable adapter to the wrapped Ship."""
        return getattr(self.ship, "_ship", None) or getattr(self.ship, "ship", None)

    def _ship_is_alive(self) -> bool:
        try:
            return bool(self.ship.is_alive())
        except Exception:  # Intentional broad catch: stub adapters may raise; treat as "dead".
            return False


__all__ = ["CarrierAIController"]
