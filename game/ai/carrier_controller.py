"""CarrierAIController — PROJ-FMS-C audit Fix 1 + QA-C mass-budget launch.

Production caller for :meth:`BattleEngine.launch_fighters_in_battle` and
:meth:`BattleEngine.launch_satellites_in_battle`.

Replaces the legacy ``VehicleLaunchAbility`` auto-launch path that lived
in :class:`WeaponFiringSystem` ``_process_hangar_launch`` (removed in
the PROJ-FMS-C audit-fix pass). The decision in
``Projects/active_projects/PROJ-FMS-C/decisions.md`` was "explicit
player / AI action surface" rather than weapon-system auto-launch;
this controller is that AI action surface.

QA-C: the per-tick launch decision uses a mass-tons/sec budget rather
than the older count-per-cycle + cooldown model. ``launch_rate_tons_per_sec``
is the authoritative tactical-throughput dial on each tactical-launch
ability. Per tick the controller increments a per-vehicle-type budget
by ``launch_rate_tons_per_sec * TICK_RATE``; carried vehicles whose
mass fits the budget are popped and dispatched, the budget is decremented,
and the residual carries to the next tick. This lets variable-mass
fighter fleets launch at variable rates from the same bay (a 50t
interceptor launches twice as often as a 100t bomber from a 100 t/s
bay) without any per-design tuning.

Behaviour per tick:
  1. Run the base :class:`AIController` ``update()`` — the carrier still
     moves and fires its standard weapons.
  2. For each launch ability the carrier has, accumulate the mass-tons
     budget. If any enemy is inside the launch radius, pop carried
     vehicles whose mass fits the residual budget and request the
     launch through the BattleEngine method named on the ability.
"""
from __future__ import annotations

import logging
import random
from typing import Any, List, Optional, TYPE_CHECKING

from game.ai.controller import AIController
from game.core.config import BattleTuning, PhysicsConfig
from game.strategy.data.carried_vehicle import CarriedVehicle

if TYPE_CHECKING:
    from game.ai.interfaces.controllable import ShipControllableAdapter
    from game.engine.spatial import SpatialGrid
    from game.simulation.systems.battle_engine import BattleEngine


logger = logging.getLogger(__name__)


class CarrierAIController(AIController):
    """AI controller for carrier-class ships.

    Subclasses :class:`AIController` so the carrier keeps full ship-AI
    behavior (movement policy, weapon firing, target acquisition). Adds
    a per-tick mass-budget auto-launch hook.

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
        # Per-vehicle-type mass-tons budget accumulator. Keys are the
        # ability_name string ("TacticalFighterLaunch" / "TacticalSatelliteLaunch").
        # Each tick the budget grows by ``launch_rate_tons_per_sec * TICK_RATE``
        # summed across active launch components of that type.
        self._mass_budget_by_ability: dict[str, float] = {}

    def update(self) -> None:
        """Run one tick of carrier AI.

        Order: base AI (movement / targeting / weapon-firing trigger), then
        the per-tick mass-budget launch checks. Base-AI failures are
        logged and swallowed so a bad sub-system can't break the launch
        path or the battle loop.
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
        if self._engine is None:
            return
        self._maybe_launch_fighter_wave()
        self._maybe_launch_satellite_wave()

    # ------------------------------------------------------------------
    # Auto-launch — fighters
    # ------------------------------------------------------------------

    def _maybe_launch_fighter_wave(self) -> None:
        """Accumulate mass budget and dispatch carried fighters."""
        self._maybe_launch_wave(
            ability_name="TacticalFighterLaunch",
            vehicle_type="fighter",
            launch_method_name="launch_fighters_in_battle",
        )

    # ------------------------------------------------------------------
    # Auto-launch — satellites
    # ------------------------------------------------------------------

    def _maybe_launch_satellite_wave(self) -> None:
        """Accumulate mass budget and dispatch carried satellites."""
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
        """Mass-tons-per-second tactical launch.

        Per tick:
          1. Sum ``launch_rate_tons_per_sec`` across active launch
             abilities of this vehicle type and add
             ``rate * TICK_RATE`` to the per-type budget.
          2. If no enemy is in range, skip the dispatch step — but
             still let the budget accumulate so the bay is "warmed
             up" when an enemy enters range.
          3. Pop carried vehicles whose mass fits the residual budget,
             deduct each launch's mass, and hand the list to the
             engine's launch method.
        """
        total_rate = self._sum_launch_rate(ability_name)
        if total_rate <= 0:
            return

        # Step 1: accumulate.
        prev = self._mass_budget_by_ability.get(ability_name, 0.0)
        budget = prev + (total_rate * PhysicsConfig.TICK_RATE)
        self._mass_budget_by_ability[ability_name] = budget

        carrier = self._unwrap_ship()
        if carrier is None:
            return
        if not self._enemy_in_launch_radius(carrier):
            return

        # Step 3: pop carried vehicles that fit the budget.
        popped, new_budget = self._pop_cvs_within_budget(
            carrier, vehicle_type, budget,
        )
        self._mass_budget_by_ability[ability_name] = new_budget
        if not popped:
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
            launch_method(carrier, popped)
        except Exception:  # Intentional broad catch: AI auto-launch must not break the battle loop on a bad design payload.
            logger.exception(
                "CarrierAIController: %s raised for carrier=%s; "
                "%d CVs were popped but not spawned.",
                launch_method_name,
                getattr(carrier, "name", "?"),
                len(popped),
            )
            return

    def _sum_launch_rate(self, ability_name: str) -> float:
        """Sum ``launch_rate_tons_per_sec`` across active launch abilities."""
        carrier = self._unwrap_ship()
        if carrier is None:
            return 0.0
        iter_components = getattr(carrier, "iter_components", None)
        if iter_components is None:
            return 0.0
        total = 0.0
        try:
            for _layer, comp in iter_components():
                if not getattr(comp, "is_active", True):
                    continue
                if not getattr(comp, "is_operational", True):
                    continue
                if not comp.has_ability(ability_name):
                    continue
                for ab in comp.get_abilities(ability_name):
                    rate = float(getattr(ab, "launch_rate_tons_per_sec", 0.0) or 0.0)
                    if rate > 0:
                        total += rate
        except Exception:  # Intentional broad catch: component-iter on minimal stubs raises across many shapes; treat as "no launch ability".
            return 0.0
        return total

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

        Legacy fighter-only count-based helper, retained for the
        pre-QA-C integration tests. New code should use
        :meth:`_pop_cvs_within_budget`.
        """
        return CarrierAIController._pop_cvs(carrier, "fighter", max_count)

    @staticmethod
    def _pop_cvs(
        carrier: Any, vehicle_type: str, max_count: int,
    ) -> List[CarriedVehicle]:
        """Pop up to ``max_count`` ``CarriedVehicle``s of ``vehicle_type``.

        Legacy count-based pop, retained for the pre-QA-C tests and the
        fighter-recovery-test setup paths. New tactical launches go
        through :meth:`_pop_cvs_within_budget`.
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

    @staticmethod
    def _pop_cvs_within_budget(
        carrier: Any, vehicle_type: str, budget: float,
    ) -> tuple[List[CarriedVehicle], float]:
        """Pop carried vehicles of ``vehicle_type`` whose mass fits ``budget``.

        Mass-tons/sec launch semantics. Walks ``carrier.carried_items``
        in order; for each matching CarriedVehicle whose ``mass`` fits
        the residual budget, the vehicle is popped and its mass deducted.
        Stops at the first matching vehicle that exceeds the budget so
        the budget carries cleanly to the next tick (no skip-ahead to a
        smaller vehicle further back in the bay).

        Returns ``(popped, remaining_budget)``.
        """
        carried = getattr(carrier, "carried_items", None)
        if not carried:
            return [], budget
        popped: List[CarriedVehicle] = []
        remaining_items: List[Any] = []
        vt = vehicle_type.lower()
        residual = budget
        launched_any = False
        for item in carried:
            cv = CarriedVehicle.from_any(item)
            if cv is None or cv.vehicle_type != vt:
                remaining_items.append(item)
                continue
            # Treat zero / negative mass as 1.0 to avoid divide-by-zero
            # bug-bait where a malformed design slips through.
            mass = float(cv.mass) if cv.mass and cv.mass > 0 else 1.0
            if mass > residual:
                # First matching vehicle that doesn't fit — preserve
                # FIFO bay ordering by keeping the rest behind it too.
                remaining_items.append(item)
                # Append the remaining list as-is and stop processing.
                idx = carried.index(item)
                remaining_items.extend(carried[idx + 1:])
                break
            popped.append(cv)
            residual -= mass
            launched_any = True
        if launched_any:
            try:
                carrier.carried_items = remaining_items
            except Exception:  # Intentional broad catch: stubs may set carried_items as a property; ignore and let the next tick retry.
                pass
        return popped, residual

    # ------------------------------------------------------------------
    # Legacy ability-lookup helper (kept for test fixtures)
    # ------------------------------------------------------------------

    def _find_tactical_launch_ability(
        self, ability_name: str = "TacticalFighterLaunch",
    ) -> Optional[Any]:
        """Return the first active tactical-launch ability, or None.

        Retained for tests that introspect the controller's ability
        lookup path. Production launch decisions now use
        :meth:`_sum_launch_rate` to aggregate across all active launch
        components of the same kind.
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
