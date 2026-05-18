# PROJ-FMS-B Phase 4: Sensitivity UI + selective self-destruct + ramming

> See [`../PROJ-FMS-shared/design.md`](../PROJ-FMS-shared/design.md) for full design context.

**Goal:** Surface owner-side controls for minefield behavior and add ramming for fighters/ships carrying warheads.

## Tasks

### Sensitivity + threshold UI
- [ ] In the sector / minefield management UI (locate in [`game/ui/screens/`](../../../game/ui/screens/) — closest analogue is fleet management), add controls for each owned `mine_group` in a hex:
  - LOW / MED / HIGH sensitivity radio (warhead trigger multiplier).
  - Continuous slider 0.0 → 1.0 for `expected_hit_chance_threshold` (laserhead gate). Default = 0.30 from balance file.
  - (Service layer `MineGroupService.set_sensitivity` / `set_threshold` is implemented and tested; the pygame UI binding is the remaining work and is deferred to a UI-binding pass.)
- [x] Both settings persist on the `mine_group` Fleet and serialize through save/load.
- [x] Changes apply immediately at the next minefield resolution; no in-flight effect on currently-resolving entries.

### Selective self-destruct
- [ ] UI affordance on each owned `mine_group`: list the mines by design (group-by-design with counts), allow the player to select N mines of a given design and self-destruct them.
  - (Service-layer `MineGroupService.self_destruct` is implemented and tested; pygame UI binding is the deferred remainder.)
- [x] Selected mines are removed from the group without triggering damage. If all mines removed → group destroyed.
- [ ] Confirm action (modal) before executing — destroying a player's own military assets shouldn't be a one-click slip. (UI binding deferred.)
- [x] Self-destruct works at both strategic layer (between turns) and tactical layer (during battle). Tactical self-destruct removes the mine from the tactical map immediately.

### Ramming (`RamTargetAbility`)

`RamTargetAbility` is a data-bearing tactical ability — its execution lives in the battle-engine / movement-AI path, not on the ability class. The ability instance holds the runtime ram target id.

- [x] Implement the in-combat hookup:
  - Action: `set_ram_target(rammer, target_ship)` — sets `rammer.ram_target_id = target.id`. (PROJ-FMS-B audit Fix 3 — 2026-05-16: `BattleEngine.set_ram_target` is the canonical action surface; routes through the auto-instantiated `BattleEngine.ram_resolver`.)
  - Movement AI ([`game/ai/controller.py`](../../../game/ai/controller.py) or the ship-movement layer): if `ram_target_id` is set, override normal pathing with intercept-and-collide pursuit toward the target ship. Disable conventional weapon fire (kamikaze commitment). (Pursuit-AI integration is still deferred — current behavior relies on the player/AI moving the rammer into collision range and the resolver detecting hull-radius intersection; the explicit pathing override lands with a follow-up AI pass.)
  - Collision: when the rammer's hull intersects the target's hull, every `Warhead` component on the rammer detonates against the target via the damage pipeline (each warhead's `damage` applied as a separate hit). The rammer is destroyed regardless of damage outcome. (Wired and tested end-to-end via `BattleEngine._run_ramming_tick` — PROJ-FMS-B audit Fix 3.)
  - If the target dies / leaves the battle before collision, the rammer's `ram_target_id` clears and it reverts to default AI (unless re-targeted).
- [ ] UI: add "Set ram target" context action on fighters / ships with `RamTargetAbility`, target picker for any enemy in tactical view. (Engine-side action surface ready — `BattleEngine.set_ram_target` — pygame binding is the remaining work.)
- [x] Designs without `RamTargetAbility` cannot ram — warheads on them are inert payload (still cargo).

### Tests
- [x] Sensitivity LOW → trigger rate drops to ~0.5× baseline; HIGH → ~1.5×. Statistical over many trials.
- [x] Threshold slider at 0.0 → all laserheads fire; at 1.0 → none fire (in practice).
- [x] Self-destruct 3 of 10 mines → group has 7; per-pass `P_trigger` and laserhead count adjust accordingly.
- [x] Self-destruct all → group destroyed.
- [x] Fighter with 1× `Warhead` + `RamTargetAbility`, set ram target on an enemy frigate → fighter flies into frigate, warhead detonates, fighter destroyed, frigate takes warhead damage.
- [x] Fighter with 3× `Warhead` rammed → 3 separate damage applications.
- [x] Fighter with `Warhead` but no `RamTargetAbility` → warhead never detonates from collision (warhead is inert payload).
- [x] Target dies before collision → rammer reverts to standard AI.

## Verification
- `python Tools/test_sharded/test_sharded.py`
- `pytest tests/unit/simulation/components/abilities/test_ram_target.py`
- Manual: battle scenario with kamikaze fighter wing vs enemy frigate; verify ramming feels right.

## Exit criteria
- Minefield owners have full sensitivity + threshold control.
- Selective self-destruct works at strategic and tactical layers.
- Ramming feels deliberate (explicit-action only) and applies expected damage on collision.
