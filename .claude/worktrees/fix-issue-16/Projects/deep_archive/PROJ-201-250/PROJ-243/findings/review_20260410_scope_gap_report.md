# PROJ-243 Scope Gap Analysis Report

**Date:** 2026-04-10
**Reviewer:** Scope Gap Analyst
**Project:** PROJ-243 (Mid-Battle Ship Addition Fix)
**Status:** All 4 phases complete

---

## Summary

PROJ-243 successfully addressed its core goals: `add_ship_mid_battle()` now runs the same initialization as `start()`, fleet bonus attributes are declared in `Ship.__init__`, `FleetAuraManager.register_ship()` exists for mid-battle aura registration, and fighter launch delegates to `add_ship_mid_battle()`. The test coverage is solid for the happy path.

However, the review identified **6 scope gaps** -- areas adjacent to the fix that were either explicitly deferred as out-of-scope or not considered, but that now represent inconsistencies or latent risks in the codebase.

---

## Findings

### GAP-01: collision.py getattr Fallback Is Now Dead Code

**Location:** `game/engine/collision.py:115-122`
**Related Goal:** Declared attributes (fleet_attack_bonus / fleet_defense_bonus in Ship.__init__)
**Gap Description:** The plan explicitly listed `collision.py getattr fallback cleanup` as out-of-scope, noting it was "defensive code, still valid." However, now that `fleet_attack_bonus` and `fleet_defense_bonus` are declared in `Ship.__init__` with default `0.0`, the `getattr(..., None)` + `isinstance(..., (int, float))` guard pattern on lines 115-122 is dead defensive code. Every Ship instance will always have these attributes as floats. The `getattr` with `None` default, followed by the `isinstance` type check, can never take the fallback branch for Ship targets.

**Current code:**
```python
fleet_atk = getattr(source_ship, 'fleet_attack_bonus', None)
if isinstance(fleet_atk, (int, float)):
    attack_score += fleet_atk

fleet_def = getattr(target, 'fleet_defense_bonus', None)
if isinstance(fleet_def, (int, float)):
    defense_score += fleet_def
```

**Impact:** Low severity. The code works correctly, but it masks the contract. Readers see `getattr` + `isinstance` and assume the attribute might not exist, which was the old reality but is no longer true. This also violates the project's Clean-Sheet Design rule (Rule 3) -- the defensive pattern was a workaround for undeclared attributes, and now that the root cause is fixed, the workaround should be removed.

**Note:** The `target` could be a `Projectile` (PDC shooting at missiles), which does NOT have `fleet_defense_bonus`. So the `getattr` on `target` at line 120 is still needed for Projectile targets. However, `source_ship` is always a Ship (line 111-113 checks `hasattr(source_ship, 'get_total_sensor_score')`), so the getattr on line 115 is genuinely dead.

**Proposed Resolution:** Simplify line 115-117 to `attack_score += source_ship.fleet_attack_bonus`. Leave line 120-122 as-is (target can be Projectile). Alternatively, add `fleet_defense_bonus = 0.0` to Projectile and simplify both.

**Effort:** Simple

---

### GAP-02: remove_ship() Does Not Unregister From FleetAuraManager

**Location:** `game/simulation/systems/battle_engine.py:383-409`
**Related Goal:** Aura re-scan (FleetAuraManager picks up new ship's fleet-scope abilities)
**Gap Description:** PROJ-243 added `register_ship()` to FleetAuraManager for the add path, but the plan noted `remove_ship()` as out-of-scope ("already works"). However, `remove_ship()` does NOT call any aura manager method. When a ship providing fleet-scope abilities is removed (retreat/escape), its `AuraProvider` entries remain in `self._providers`. The ship is no longer in `self.ships`, so:

1. The `_recalculate()` method checks `ship.is_alive` on the provider (line 188), which filters it out if the ship was killed. But if the ship retreated (removed but alive), the provider entry references a live ship that is no longer in the battle.
2. The `_get_provider_fingerprint()` method (line 155-169) iterates `self._providers` and accesses `provider.ship.is_alive` and `provider.ship.get_all_components()` -- this still works on the removed ship object, but produces stale data.
3. The `update()` method at line 141-142 only processes ships passed to it, and `_apply_bonuses()` at line 237-246 iterates the ships list. Since the removed ship is no longer in `engine.ships`, it won't receive bonuses, which is correct. But the provider entry creates unnecessary iteration overhead and could lead to stale bonus calculations if the removed ship's `is_alive` status doesn't change.

**Impact:** Medium. In the current codebase, ships are typically removed on retreat (still alive), meaning their AuraProvider entries will continue to contribute bonuses to teammates even though the ship has left the battle. This is a logic bug: a retreated ship should not provide fleet bonuses to the remaining fleet.

**Proposed Resolution:** Add `unregister_ship(ship)` to FleetAuraManager that removes matching AuraProvider entries and triggers `_recalculate()`. Call it from `BattleEngine.remove_ship()`. This is the symmetric counterpart to `register_ship()`.

**Effort:** Simple

---

### GAP-03: No Test for add_ship_mid_battle() Before start()

**Location:** `game/simulation/systems/battle_engine.py:342-381`
**Related Goal:** Parity with start()
**Gap Description:** The test suite does not cover what happens if `add_ship_mid_battle()` is called before `start()`. In this case:
- `self.aura_manager` is not initialized (`_initialized = False`)
- `self.combat_events` is a CombatEventBus (initialized in `__init__`)
- `self.rng` is unseeded default
- `register_ship()` calls `_recalculate()` which will run even though `initialize()` was never called

The `FleetAuraManager.update()` method has a guard (`if not self._initialized: return`), but `register_ship()` does NOT check `_initialized`. This means `register_ship()` called before `initialize()` will populate `_providers` and call `_recalculate()` on an un-initialized manager. This is unlikely in production (BattleController always calls start() first), but is a defensive gap.

**Impact:** Low. This is a defensive edge case that is unlikely in practice but represents an implicit contract violation. If any code path ever calls `add_ship_mid_battle()` before `start()`, the aura state would be inconsistent.

**Proposed Resolution:** Either add a guard in `add_ship_mid_battle()` that raises if battle hasn't started, or add a guard in `register_ship()` that checks `_initialized`. Add a unit test documenting the expected behavior.

**Effort:** Simple

---

### GAP-04: Stale _alive_ships_cache When Fighter Launched Mid-Tick

**Location:** `game/simulation/systems/tick_phase.py:86-98` and `game/simulation/systems/battle_engine.py:505-534`
**Related Goal:** Fighter launch fix (uses add_ship_mid_battle())
**Gap Description:** The tick phase sequence is:
1. `RebuildGridPhase` (priority 100): Builds `_alive_ships_cache`
2. `AIAndShipUpdatePhase` (priority 200): Updates AI and ships
3. `AttackProcessingPhase` (priority 300): Collects attacks from `_alive_ships_cache`, processes them
4. `RammingPhase` (priority 400): Processes ramming on `engine.ships`
5. `ProjectileUpdatePhase` (priority 500): Updates projectiles

When a LAUNCH attack is processed in step 3, `_process_launch_attack()` calls `add_ship_mid_battle()`, which appends the new fighter to `engine.ships`. However:
- The fighter is NOT in `_alive_ships_cache` (built in step 1)
- The fighter is NOT in the spatial grid (built in step 1)
- The fighter WILL appear in `engine.ships` for the RammingPhase (step 4), meaning it could be rammed on the same tick it spawns
- The fighter's weapons cannot fire until next tick (collected from `_alive_ships_cache` in step 3)

This is not a bug introduced by PROJ-243 -- the old code had the same timing. But the refactoring to use `add_ship_mid_battle()` makes this more visible. The fighter is partially initialized mid-tick: it has stats and event bus, but it's not in the grid and can't fire.

**Impact:** Low. The one-tick delay before a launched fighter can fire is acceptable behavior and was pre-existing. The ramming exposure is a minor edge case (fighters are small and unlikely to overlap a kamikaze ship on spawn). No tests verify or document this timing behavior.

**Proposed Resolution:** Document the mid-tick addition timing in the code comments or battle engine lifecycle docs. Optionally, add the launched fighter to the grid immediately in `add_ship_mid_battle()` (but this may have side effects). A test asserting the expected one-tick delay would prevent regressions if someone tries to "fix" it.

**Effort:** Simple (documentation) / Medium (if adding to grid)

---

### GAP-05: combat_lab getattr Fallbacks in tohit_attack_fleet_scenarios.py

**Location:** `combat_lab/scenarios/tohit_attack_fleet_scenarios.py:53, 140, 201, 248`
**Related Goal:** Declared attributes (fleet_attack_bonus / fleet_defense_bonus in Ship.__init__)
**Gap Description:** The Combat Lab fleet aura test scenarios use `getattr(self.attacker, 'fleet_attack_bonus', None)` or `getattr(self.attacker, 'fleet_attack_bonus', 0.0)` with defensive fallbacks. Like GAP-01, these are now unnecessary since the attribute is always declared on Ship. The tests should use direct attribute access to validate the contract.

**Impact:** Very low. Tests still work correctly. But they test the wrong thing: they test that the attribute exists OR that the fallback works, when the contract now says the attribute ALWAYS exists.

**Proposed Resolution:** Replace `getattr(ship, 'fleet_attack_bonus', ...)` with `ship.fleet_attack_bonus` in the scenario validation methods. This makes the tests stricter and consistent with the Ship contract.

**Effort:** Simple

---

### GAP-06: Projectile Hit Resolution Does Not Use Fleet Bonuses

**Location:** `game/simulation/projectile_manager.py:78-126`
**Related Goal:** Adjacent to fleet bonus propagation
**Gap Description:** This is not a gap in PROJ-243's scope, but is an adjacent asymmetry worth noting. Beam weapons (in `collision.py:110-122`) incorporate fleet attack and defense bonuses into hit chance calculation. However, projectile weapons (in `projectile_manager.py:78-126`) use purely geometric collision detection with no hit chance -- they either collide or they don't. This means fleet aura attack/defense bonuses only affect beam weapons, not projectiles.

This may be intentional design (projectiles are ballistic, beams are aimed), but it is not documented anywhere. PROJ-243's changes to fleet bonus propagation only matter for beam combat.

**Impact:** Informational only. If this asymmetry is intentional, it should be documented. If not, it's a separate design issue unrelated to PROJ-243.

**Proposed Resolution:** Document the asymmetry (fleet bonuses only affect beam hit chance, not projectile collision). If projectile accuracy should also be affected, that would be a separate ticket.

**Effort:** Simple (documentation) / Complex (if implementing projectile accuracy)

---

## Risk Assessment

| Finding | Severity | Correctness Bug? | Action Recommended |
|---------|----------|-------------------|--------------------|
| GAP-01 | Low | No (dead code) | Clean up in next pass |
| GAP-02 | Medium | Yes (stale aura on retreat) | New ticket |
| GAP-03 | Low | No (edge case) | Add guard + test |
| GAP-04 | Low | No (pre-existing timing) | Document |
| GAP-05 | Very Low | No (test strictness) | Clean up in next pass |
| GAP-06 | Informational | No (design question) | Document |

## Recommendations

1. **GAP-02 is the only finding that represents a real logic bug** -- retreated ships continue to provide fleet aura bonuses. This should be filed as a new ticket.

2. **GAP-01 and GAP-05** are cleanup items that can be batched together (remove defensive getattr patterns now that attributes are declared).

3. **GAP-03** is a low-risk defensive improvement that could be added to any battle engine hardening pass.

4. **GAP-04 and GAP-06** are documentation items that help future developers understand the battle engine's behavior.
