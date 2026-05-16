# PROJ-FMS-C Phase 2: Deployed wing combat join + fighter AI

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** `fighter_group` Fleets that exist in a hex automatically join any tactical combat that occurs there on their owner's side. Launched fighters have a minimal "target nearest enemy" AI.

## Tasks

### Combat join
- [x] Audit [`game/strategy/engine/conflict_resolution_engine.py:312-321,357-376`](../../../game/strategy/engine/conflict_resolution_engine.py#L312). If it iterates `empire.fleets` to build combat manifests, `fighter_group` Fleets are picked up for free thanks to PROJ-FMS-A's `group_kind`. Verify with a targeted test.
- [x] If the engine has any path that filters by "fleet with movement" or "fleet with crew," extend it to include non-fleet kinds. Add a guard against assuming a group has a flagship / can carry orders / has resources.
- [x] When a `fighter_group` participates in combat, each fighter in the group becomes a tactical entity placed on the owner's side at battle start. (Position: cluster near the owner-side spawn zone? Random within a small radius? Document the choice in [`decisions.md`](decisions.md).)

### Minimal fighter AI
- [x] Add a `FighterAIController` (or extend [`game/ai/controller.py`](../../../game/ai/controller.py)).
- [x] Each tick: pick the nearest enemy ship; turn toward it; thrust forward; if a weapon is in range and `cooldown` allows, fire.
- [x] No formation logic, no wingman behavior, no retreat — that's a follow-up.
- [x] When the target dies, re-target on next tick.
- [x] When all enemies are dead / fighter is alone, idle / hold position.
- [x] Confirm fighters with `RamTargetAbility` set (PROJ-FMS-B Phase 4) follow ram intercept rather than the default AI when their target is set.

### Fighter combat behavior
- [x] Fighters fire any weapons they have per their design; damage flows through standard pipeline.
- [x] Fighters take damage; HP tracked per-fighter (each is its own combat entity).
- [x] Destroyed fighters are removed from the tactical map AND the parent `fighter_group` Fleet's ship list (for end-of-battle reckoning).

### Tests
- [x] `fighter_group` of 3 in a hex; trigger combat with an enemy fleet there → all 3 fighters appear on the owner's side.
- [x] Minimal AI: fighter with weapons targets nearest enemy and fires when in range; verify behavior over a few ticks of a contrived scenario.
- [x] Fighter destroyed mid-battle → removed from `fighter_group`.
- [x] Kamikaze fighter (Warhead + RamTarget) launched and target set → fighter intercepts and detonates (verifies the RamTarget path from PROJ-FMS-B doesn't break for launched fighters).
- [x] Tactical launch (Phase 1) + auto-join (this phase) interact correctly: a fighter launched from a carrier mid-battle is a peer of fighters from a pre-existing `fighter_group` in the same hex.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `python -m combat_lab.run_tests` — combat behavior smoke.
- Manual: pre-deployed `fighter_group` + enemy fleet enters → battle → fighters fight.

## Exit criteria
- Deployed `fighter_group`s automatically participate in their hex's tactical battles.
- Minimal fighter AI targets and fires on nearest enemy.
- Per-fighter HP and destruction tracked correctly.
