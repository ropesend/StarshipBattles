# PROJ-FMS-C Design — Fighters slice

This project's slice of the shared design. **See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for the canonical, end-to-end design.** Only PROJ-FMS-C-specific notes go here.

## In scope
- `StrategicFighterLaunchAbility` and `TacticalFighterLaunchAbility` behavior.
- Replacement of the existing class-string launch path with design-instance deploy.
- `RecoverFightersAbility` strategic action.
- End-of-battle auto-reboard for fighters launched during the battle (with overflow → sector group).
- Minimal "target nearest enemy" fighter AI.
- Combat-join wiring for `fighter_group` Fleets.

## Out of scope
- Wingmate / formation AI — explicitly a follow-up.
- Mines / ramming (PROJ-FMS-B; ramming for fighters carrying warheads works at PROJ-FMS-C launch time but the ability behavior is owned by B).
- Satellites (PROJ-FMS-D).

## Key risks
- **Tagging `launched_in_battle_id`**: end-of-battle reboard policy depends on this tag. If the tag leaks between battles (carrier moves to a new sector mid-tag), behavior breaks. Reset / clear the tag on `fighter_group` formation and on battle end.
- **Carrier-destroyed-mid-battle**: fighters launched from a destroyed carrier need a clear policy for overflow. Document in `decisions.md`.
- **Stat contributor update**: changing the shape of launch abilities ripples through [`launch.py:29-61`](../../../game/simulation/entities/stat_contributors/launch.py#L29). Verify no regressions on the existing fighter capacity calc.
- **Old `VehicleLaunchAbility` cleanup**: removing it fully in Phase 1 vs warning-only is a backwards-compatibility judgment. Lean: keep with deprecation warning, plan removal in a follow-up housekeeping project once no shipped designs reference it.
- **Auto-join on contested hexes**: combat manifest construction must be aware of `group_kind` to avoid double-counting fighters that arrived via a normal Fleet that also carries fighters in bays (which would then ALSO launch tactically during the battle).

## Decisions deferred to implementation (PROJ-FMS-C)
- Spawn cluster pattern for combat-joining `fighter_group`s (random in owner-side spawn zone? Around the launching ship?).
- Overflow merge behavior when a pre-existing `fighter_group` is already in the hex at battle end (merge or new group?).
- Whether to fully remove `VehicleLaunchAbility` in Phase 1 or warn-only.
- Whether kamikaze-fighter handling needs special-casing in the launch path beyond PROJ-FMS-B's ramming work.
