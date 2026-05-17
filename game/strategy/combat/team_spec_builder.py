"""PROJ-426 — `TeamSpecBuilder`.

Owns the team-construction concerns previously embedded in
`spec_compiler.py`:

- `split_mine_groups(...)`: partition incoming fleets into combat fleets
  vs. mine-group fleets. Promoted from the private
  `_split_mine_groups_from_fleets` helper so tests can target a public
  seam.
- `team_spec_for_fleet_group(...)`: build a `TeamSpec` from one owner's
  fleets (each fleet contributes one `TaskForce` so the post-battle hook
  can still dispatch outcomes back to the originating Fleet).
- `pick_formation_for_fleet(...)`: per-fleet formation selection (explicit
  TF formation wins; falls back to the default task-force resolver).
- `ship_spec_from_instance(...)`: ShipInstance -> ShipSpec translation
  (theme, components, pose, instance_ref).

The PROJ-431 deployable substrate redesign will collapse the
mine-vs-combat split here once mines/satellites/fighters live on a
unified substrate; that simplification is intentionally deferred. See
`StrategyBattleAssembler.mine_group_filter`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple

from game.core.math import Vector2
from game.simulation.battle_spec import (
    ComponentStateSpec,
    EntryVector,
    ShipSpec,
    SquadronSpec,
    TaskForceSpec,
    TeamSpec,
    CombatPolicies,
)
from game.simulation.combat.formation import (
    FormationResolver,
    FormationSpec,
    resolve_default_for_task_force,
)

if TYPE_CHECKING:
    from game.strategy.data.fleet import Fleet
    from game.strategy.data.ship_instance import ShipInstance


__all__ = ["TeamSpecBuilder"]


class TeamSpecBuilder:
    """Build per-team `TeamSpec` artifacts from strategy-layer fleets."""

    def split_mine_groups(
        self,
        fleets: Sequence["Fleet"],
    ) -> Tuple[List["Fleet"], List["Fleet"]]:
        """Partition ``fleets`` into ``(combat_fleets, mine_groups)``.

        Mine-group Fleets carry mines in a synthetic-carrier ShipInstance
        whose `layers` / `components` are empty. They participate in
        tactical combat exclusively via `TacticalMineResolver`, not as
        ShipSpecs on a team. Without this filter the compiler would turn
        the synthetic carrier into a degenerate zero-HP ship.

        Other "group_kind" markers (`fighter_group`, `satellite_group`)
        carry real ships and stay in the combat-fleets stream.
        """
        combat: List["Fleet"] = []
        mine_groups: List["Fleet"] = []
        for fleet in fleets:
            if getattr(fleet, "group_kind", "fleet") == "mine_group":
                mine_groups.append(fleet)
            else:
                combat.append(fleet)
        return combat, mine_groups

    def group_fleets_by_owner(
        self,
        combat_fleets: Sequence["Fleet"],
    ) -> Tuple[Dict[Any, List["Fleet"]], List[Any]]:
        """Group combat fleets by `owner_id` and return the insertion-ordered owner list.

        Single source of truth for owner-order discovery used downstream
        by both `compute_owner_to_team_id` (assembler-side) and the
        post-battle hook builder. Without this helper, both call sites
        re-derived the same iteration independently — a drift risk if
        either side's tiebreak/order rules diverged over time.
        """
        fleets_by_owner: Dict[Any, List["Fleet"]] = {}
        for fleet in combat_fleets:
            fleets_by_owner.setdefault(fleet.owner_id, []).append(fleet)
        owner_order: List[Any] = list(fleets_by_owner.keys())
        return fleets_by_owner, owner_order

    def compute_owner_to_team_id(
        self,
        combat_fleets: Sequence["Fleet"],
    ) -> Dict[Any, int]:
        """Compute the canonical `owner_id -> team_id` mapping.

        team_ids are assigned by insertion order of unique owners across
        `combat_fleets`. The returned dict is the single source of truth:
        both `BattleSpecExtensions.owner_to_team_id` and the post-battle
        hook's owner-keyed dispatch share this exact object.
        """
        _, owner_order = self.group_fleets_by_owner(combat_fleets)
        return {owner_id: team_id for team_id, owner_id in enumerate(owner_order)}

    def team_spec_for_fleet_group(
        self,
        owner_fleets: List["Fleet"],
        *,
        team_id: int,
        entry_vector: EntryVector,
    ) -> TeamSpec:
        """Build a `TeamSpec` for one or more allied fleets sharing an owner.

        Each fleet contributes its own TaskForce inside the team — preserves
        fleet identity for the post-battle hook (which dispatches outcomes
        back into the originating Fleet's ships list). Formation resolution
        is per-fleet; team-level placement comes from `entry_vector`.
        """
        if not owner_fleets:
            raise ValueError(
                "TeamSpecBuilder.team_spec_for_fleet_group: "
                "owner_fleets must be non-empty"
            )

        task_forces: List[TaskForceSpec] = []
        for fleet in owner_fleets:
            formation = self.pick_formation_for_fleet(fleet)
            poses = FormationResolver.resolve(
                formation=formation,
                entry_vector=entry_vector,
                boundary=None,
                ships=fleet.ships,
            )
            ships: Tuple[ShipSpec, ...] = tuple(
                self.ship_spec_from_instance(ship, poses.get(ship.instance_id))
                for ship in fleet.ships
            )
            task_forces.append(
                TaskForceSpec(
                    task_force_id=f"tf-fleet-{fleet.id}",
                    formation=formation,
                    policies=CombatPolicies(),
                    squadrons=(
                        SquadronSpec(
                            squadron_id=f"sq-fleet-{fleet.id}",
                            policies=CombatPolicies(),
                            ships=ships,
                        ),
                    ),
                )
            )
        name = (
            f"Fleet {owner_fleets[0].id}"
            if len(owner_fleets) == 1
            else f"Empire {owner_fleets[0].owner_id} "
                 f"({len(owner_fleets)} fleets)"
        )
        return TeamSpec(
            team_id=team_id,
            name=name,
            entry_vector=entry_vector,
            fleet_hierarchy=tuple(task_forces),
        )

    def pick_formation_for_fleet(self, fleet: "Fleet") -> FormationSpec:
        """Pick the formation for a Fleet.

        Priority:
          1. Explicit `TaskForce.formation` if any TF on the fleet has one
             set (first TF wins).
          2. `resolve_default_for_task_force(fleet.ships)` otherwise.
        """
        for tf in getattr(fleet, "task_forces", []) or []:
            if getattr(tf, "formation", None) is not None:
                return tf.formation
        return resolve_default_for_task_force(fleet.ships)

    def ship_spec_from_instance(
        self,
        ship: "ShipInstance",
        pose: Optional[Tuple[Vector2, float]] = None,
    ) -> ShipSpec:
        """ShipInstance -> ShipSpec (theme, components, pose, instance_ref)."""
        theme_id = "Federation"
        if hasattr(ship, "design_data") and isinstance(ship.design_data, dict):
            theme_id = ship.design_data.get("theme_id", theme_id)

        component_specs: Tuple[ComponentStateSpec, ...] = ()
        instance_components = getattr(ship, "components", None) or {}
        if instance_components:
            sorted_states = sorted(
                instance_components.values(),
                key=lambda cs: (cs.component_id, cs.instance_index),
            )
            component_specs = tuple(
                ComponentStateSpec(
                    component_id=cs.component_id,
                    instance_index=cs.instance_index,
                    current_hp=float(cs.current_hp),
                    max_hp=float(cs.max_hp),
                    status="ACTIVE",
                    is_active=bool(cs.is_active),
                )
                for cs in sorted_states
            )

        if pose is not None:
            position, angle = pose
        else:
            position, angle = Vector2(0.0, 0.0), 0.0

        return ShipSpec(
            instance_id=ship.instance_id,
            design_id=ship.design_id,
            theme_id=theme_id,
            name=ship.name,
            position=position,
            angle=float(angle),
            velocity=Vector2(0.0, 0.0),
            components=component_specs,
            instance_ref=ship,
        )
