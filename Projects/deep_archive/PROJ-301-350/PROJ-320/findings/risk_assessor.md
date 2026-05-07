# PROJ-320 — Risk Assessor Findings

## Top 3 Critical Risks

### 1. Atomic Fleet Pruning (HIGH)
- **Location:** `conflict_resolution_engine.py:247-268` + `post_battle_hook.py:180-199`
- **Issue:** `resolve_all_conflicts` snapshots the hex_map once per tick. If Fleet A is destroyed mid-tick via `apply_outcome_to_fleets`, the fleet is removed from `Empire.fleets`. But if a second combat round fires for the same hex, the static hex_map still references the destroyed Fleet A, causing undefined behavior.
- **Mitigation:** Rebuild hex_map after each combat, or validate fleet liveness (confirm each fleet still exists in its empire's roster) before invoking `_resolve_combat_at_hex`.

### 2. Mid-encounter Fleet Destruction (HIGH)
- **Location:** `conflict_resolution_engine.py:247-268` (_resolve_conflicts)
- **Issue:** When multiple combats occur at the same hex in one tick, the first combat's pruning invalidates the static roster. The second combat uses stale fleet references.
- **Mitigation:** Implement dynamic hex_map updates or per-battle roster refresh. Re-derive occupants from `empire.fleets` after each `apply_outcome_to_fleets` call.

### 3. Mid-encounter Fleet Merge (HIGH)
- **Location:** `order_processor.py:86-98` (_execute_fleet_merge)
- **Issue:** Phase 1 (JOIN_FLEET) fires before Phase 4 (combat). When Fleet A merges into Fleet B, the combined fleet's speed is not recalculated via `FleetSpeedCalculator.update_fleet_speed()`. The merged fleet retains the target fleet's old speed, causing the new tick interval to be wrong. This breaks the per-fleet movement-opportunity trigger rule.
- **Mitigation:** Call `FleetSpeedCalculator.update_fleet_speed(target_fleet)` in `_execute_fleet_merge` after merge. Ensures merged fleet's speed reflects the slowest ship in the combined composition.

## Medium-Severity Risks

### 4. Mid-encounter Fleet Creation (MEDIUM)
Fleet spawned in Phase 0e at a contested hex may trigger combat on its spawning tick if tick alignment matches. Mitigate by tagging spawned fleets and skipping them in Phase 4 until next tick.

### 5. Speed Change Mid-Turn (MEDIUM)
Combat damage changes fleet speed, but interval is reactive (recomputed next tick). One tick of de-sync is acceptable but should be documented.

### 6. Entry Combat Semantics (MEDIUM)
Confirm whether "entry" (fleet moved to enemy hex) and "staying" (fleet at contested hex, hit tick) combats are the same rule. Current code treats all co-locations identically.

### 7. Multiple Fleets Per Empire (MEDIUM, BLOCKING)
Current `_resolve_combat_at_hex` takes only one fleet per empire (line 295-300). PROJ-320 spec requires all empire fleets to contribute. Change `fleets_by_empire` from `Dict[int, Fleet]` to `Dict[int, List[Fleet]]`.

## Low-Severity Risks (Already Handled)
- **Storm interaction:** Already correct; effective_speed recomputed per tick.
- **Order popping:** Already correct; Phase 3 applies movement before Phase 4 combat.
- **Replay determinism:** No risk; fewer combats → fewer replays.
- **Save/load:** No new persistent fields identified.

## File Locations

- `game/strategy/engine/conflict_resolution_engine.py` — `_resolve_conflicts` (line 247), `_resolve_combat_at_hex` (line 269)
- `game/strategy/combat/post_battle_hook.py` — `apply_outcome_to_fleets` (line 40), `_prune_empty_fleets` (line 180)
- `game/strategy/engine/order_processor.py` — `_execute_fleet_merge` (line 86), `process_instant_orders` (line 745)
- `game/strategy/services/fleet_speed_calculator.py` — `update_fleet_speed` (line 149)
- `game/strategy/engine/fleet_movement_engine.py` — `collect_movements` (line 209)

## Recommendation Summary

1. **Refactor `resolve_all_conflicts`** to dynamically rebuild the hex_map after each battle OR validate fleet liveness before each combat round.
2. **Update `_execute_fleet_merge`** to call `FleetSpeedCalculator.update_fleet_speed(target_fleet)` immediately post-merge.
3. **Change `_resolve_combat_at_hex`** to support `fleets_by_empire: Dict[int, List[Fleet]]` for multi-fleet-per-empire battles (PROJ-320 feature requirement).
4. **Add comments** in conflict_resolution_engine.py explaining that tick-interval triggers are determined at Phase 2 (before Phase 4 combat modifies speed).
5. **Test scenario:** 5 fleets at contested hex with mixed speeds; verify combat cadence matches expected intervals across merges, destruction, and damage.
