# PROJ-370 Data Layer Boundary Protocols — Code Review

**Review mode:** normal (full code review)
**Scope:** 6 commits on `feat/03c-phase-aware-execution` — 4 mutator protocols, 4 write services, 26 write sites, ~10 production files
**Request ID:** req_20260506_090314_5da777

---

## Findings Summary

| Severity | Count |
|----------|-------|
| CRIT | 0 |
| MAJ | 2 |
| MIN | 5 |
| INFO | 8 |

---

## CRITICAL — None

No critical findings. Core architecture is sound: mutators constructed exactly once, all busy write sites routed, AST guards live and passing, no `_facade_state` references, no layering violations.

---

## MAJOR

### MAJ-001: Dead function `_prune_empty_fleets` in post_battle_hook.py
**File:** `game/strategy/combat/post_battle_hook.py:251-269`
**Severity:** MAJ

The legacy `_prune_empty_fleets()` function is defined but never called. The call site at `apply_outcome_to_fleets:116` now routes through `empire_mutator.prune_empty_fleets(...)`. The old function is dead code and should be removed.

The conflict resolution engine (`conflict_resolution_engine.py:15`) references `PostBattleHook._prune_empty_fleets` in a docstring comment — that reference is now stale.

**Remediation:** Delete `_prune_empty_fleets()` from `post_battle_hook.py:251-269` and update the stale comment in `conflict_resolution_engine.py:15`.

---

### MAJ-002: Planet boundary not enforced at write site `game_initializer.py:344`
**File:** `game/strategy/engine/game_initializer.py:344`
**Severity:** MAJ

`home_planet.populations.append(initial_pop)` writes directly through the Planet attribute surface without routing through `IPlanetMutator.add_species_population()`. The manifest (`manifest.md` Phase 3 row) listed this as "Routed" but the implementation chose to allowlist `game_initializer.py` instead.

Similarly, `game_initializer.py:86` does `empire.colonies.clear()` directly — also allowlisted rather than routed through `IEmpireMutator.clear_colonies()`.

These are initialization-time writes (not engine-tick), so the architectural risk is low. However, the allowlist approach creates a gap: if a future developer adds a tick-phase Planet/Empire write to `game_initializer.py`, the AST guard won't catch it because the entire file is allowlisted.

**Remediation:** Either: (a) accept `planet_mutator`/`empire_mutator` kwargs in `GameInitializer` and route these writes through them (preferred, per manifest), or (b) tighten the allowlist to per-attribute rather than per-file so later additions to this file are caught.

---

## MINOR

### MIN-001: ShipInstance guard allows 19 paths — largest bloat risk
**File:** `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py:171-202`
**Severity:** MIN

The ShipInstance AST guard has 19 allowlisted paths — the largest of the four guards. Most (13 paths) are simulation-side `Ship`, `Component`, and battle-state files that share attribute names but operate on different classes. This is intentional per the design ("simulation-layer writes are out of scope"), but the broad allowlist means that a future engine-side `ShipInstance.cargo_contents[...] = X` write inside any of those 19 files would pass the guard unnoticed.

The risk is contained because the files are all in `game/simulation/` (which shouldn't normally hold strategy ShipInstance), but the workshop UI path (`game/ui/screens/builder/layer_panel.py`) and `post_battle_hook.py` are also allowlisted — both are places where strategy ShipInstance references could plausibly appear.

**Remediation:** Document why `post_battle_hook.py` and `builder/layer_panel.py` are in the ShipInstance allowlist (post_battle_hook now routes through the mutator but the file is allowlisted, so a future direct write bypassing the mutator would be missed). Consider removing `post_battle_hook.py` from the ShipInstance allowlist now that all writes within it route through the mutator.

---

### MIN-002: `TurnEngineConfig` docstring states "18 engine dependencies" — actually 22
**File:** `game/strategy/engine/turn_engine_config.py:3`
**Severity:** MIN

The module docstring says "Bundles the 18 engine dependencies" but the dataclass now has 22 fields (18 engines + 4 mutators added by PROJ-370). This is stale documentation.

**Remediation:** Update the docstring to say "22 fields (18 engines + 4 mutator protocols)".

---

### MIN-003: `design_validator.py` broad `except Exception` without Intentional comment
**File:** `game/strategy/services/design_validator.py:76,92`
**Severity:** MIN

Two broad `except Exception` blocks lack the required `# Intentional broad catch:` comment per `docs/03_CONVENTIONS.md` §6.3 ("Specific exceptions > Broad except catches"). These are in `game/strategy/services/` — the same package as the new write services — though not introduced by PROJ-370.

**Remediation:** Add `# Intentional broad catch: Ship.from_dict can raise multiple exception types from formula evaluation` to line 76 and `# Intentional broad catch: simulation validator delegates multiple sub-validators` to line 92.

---

### MIN-004: `EmpireWriteService.remove_colony` bypasses `Empire.remove_colony`
**File:** `game/strategy/services/empire_write_service.py:37-44`
**Severity:** MIN

The `remove_colony` method in `EmpireWriteService` does a direct `empire.colonies.remove(planet)` instead of delegating to the new `Empire.remove_colony` data-class method (added by PROJ-370 at `empire.py:61-73`). The comment says this is intentional for test mocks, but the `add_colony` method (line 32-35) delegates to `empire.add_colony(planet)` — creating asymmetry in how the two methods handle the data class.

The `add_colony` delegation preserves `planet.owner_id = empire.id` semantics intact. The `remove_colony` direct-list approach still works correctly (returns True/False, removes from list), but it misses any future side effects that might be added to `Empire.remove_colony`.

**Remediation:** For consistency with `add_colony`, route through `empire.remove_colony(planet)` when the method exists (the same `hasattr` pattern used in `prune_empty_fleets`).

---

### MIN-005: `planet.pop_order` for non-zero index directly accesses `planet.orders`
**File:** `game/strategy/services/planet_write_service.py:107-108`
**Severity:** MIN

For `pop_order` with a non-zero index, the implementation does `planet.orders.pop(index)` directly — bypassing `Planet.pop_order()` (which only supports index 0). The comment says this "emulates the data-class API by direct list pop for non-zero indices." This is correct behavior but means that a direct write to `planet.orders` exists in the mutator service itself for this one edge case. Since `planet_write_service.py` is allowlisted, the AST guard doesn't complain.

**Remediation:** Consider adding a `pop_order_at(index)` method to `Planet` or extending `Planet.pop_order(index=-1)` to handle arbitrary indices. Low priority.

---

## INFO — Verified Clean

### INFO-001: AST guard correct — self/cls exclusion works
**Verified.** The walker (`_mutator_ast_walker.py:48-53`) defines `_INTERNAL_OWNERS = {"self", "cls"}` and skips any `Store`/`AugStore`/subscript-assign/method-call where the target value is a `Name` resolving to `self` or `cls`. The self-test (`test_mutator_boundary_ast_guard_self_test.py:152-193`) confirms both `self.attr = X` and `self.orders.append(x)` are correctly excluded. The walker catches `obj.attr = X` where `obj` is a parameter or local variable (any `Name` not in `_INTERNAL_OWNERS`).

### INFO-002: All 4 AST guards have non-empty attribute sets
**Verified.** Fleet (9 attrs), Planet (15 attrs), Empire (4 attrs), ShipInstance (12 attrs) — all `target_attributes` are populated. The `test_phase_status_summary` correctly asserts Fleet is live.

### INFO-003: Write-site routing verified — all 26 sites routed
**Verified via grep:**
- `fleet.location = ...` — only appears in `fleet_navigation_service.py:769` (mutator implementation). All other matches are reads (`fleet.location ==`). 8 external write sites → 0 remaining.
- `fleet.path = ...` — only in `fleet_navigation_service.py:755,773`. The `add_move_order_if_needed` change at `handlers/base.py:78-82` routes through `session.fleet_mutator.set_path(...)` — semantically identical to the prior direct assignment.
- `planet.stockpile[...]` — only in `planet_write_service.py:71` (mutator).
- `instance.is_alive = ...` — only in `ship_instance_write_service.py:32` (mutator).
- `planet.populations.append/remove` — only in `planet_write_service.py:39,45` (mutator) + `game_initializer.py:344` (allowlisted, see MAJ-002).

### INFO-004: GameSession wiring correct — all 4 mutators constructed exactly once
**Verified.** `game_session.py:100-123` constructs `FleetNavigationService`, `FleetWriteService` (with nav), `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService` — all four stored as instance attributes. Threaded through `TurnEngineConfig.create_default()` at line 130.

### INFO-005: No `_facade_state` references in write services
**Verified.** `grep _facade_state game/strategy/services/` returned zero hits. Per joint Codex+Claude review r004, the wiring site is `GameSession.__init__` + `TurnEngineConfig.create_default()`, not the facade.

### INFO-006: `TurnEngineConfig.create_default()` mutator defaults are safe
**Verified.** Lines 188-202 create lazy-default `PlanetWriteService`, `EmpireWriteService`, `ShipInstanceWriteService` instances when `None` is passed. Tests using `dataclasses.replace(cfg, ...)` will see `fleet_mutator=None, planet_mutator=None, empire_mutator=None, ship_mutator=None` unless they explicitly override them. Engines that need mutators pull from the config — those engines in `create_default()` are always constructed with non-None mutator kwargs (because `create_default` populates them first). Tests that don't exercise mutator-using engines are safe with `None`.

### INFO-007: All lazy-defaults construct equivalently
**Verified.** The lazy-default paths in `superweapon_order_processor.py:70-76`, `transfer_branches.py:104-120`, `environmental_hazard_engine.py:65-71`, and `post_battle_hook.py:72-89` all construct identically to the `GameSession` path: `EmpireWriteService()`, `ShipInstanceWriteService()`, `PlanetWriteService()` with no extra dependencies. The `FleetWriteService` in post_battle_hook includes a `FleetNavigationService()` for navigation slice delegation — same two-service composition as GameSession.

### INFO-008: LOC compliance — all new files under 500 line ceiling
**Verified.** FleetWriteService 136 LOC, PlanetWriteService 147 LOC, EmpireWriteService 136 LOC, ShipInstanceWriteService 118 LOC, strategy_mutators.py 211 LOC, TurnEngineConfig 254 LOC. All well under ceiling.

---

## Verification Matrix

| Finding | Status | Notes |
|---------|--------|-------|
| MAJ-001 (dead _prune_empty_fleets) | unresolved | Old function remains in post_battle_hook.py; should be deleted |
| MAJ-002 (game_initializer direct writes) | unresolved | Manifest planned routing; implementation allowlisted instead |
| MIN-001 (ShipInstance guard width) | info | Intentional per design; post_battle_hook allowlisting redundant post-routing |
| MIN-002 (config docstring stale) | unresolved | 18 → 22 field count needs doc update |
| MIN-003 (design_validator exceptions) | unresolved | Not PROJ-370 scope but same package; convention gap |
| MIN-004 (remove_colony bypass) | unresolved | Asymmetric with add_colony delegation |
| MIN-005 (planet.pop_order edge case) | info | Works correctly; low-priority cleanup candidate |
