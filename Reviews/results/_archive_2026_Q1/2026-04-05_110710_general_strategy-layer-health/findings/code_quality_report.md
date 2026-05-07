# Code Quality Report: Strategy Layer

**Scope:** `game/strategy/` -- 131 Python files, ~30,600 lines
**Date:** 2026-04-05
**Analyst:** Code Quality Agent

---

### Summary
- Total issues found: 18
- Critical: 1, Major: 7, Minor: 7, Info: 3

---

### Findings

#### CRITICAL: Oversized File - command_handlers.py (1062 lines)
**ID:** CQ-001
**Location:** `game/strategy/engine/command_handlers.py:1-1062`
**Issue:** At 1062 lines this file is more than double the 500-line target. It contains the BaseCommandHandler base class, CommandHandlerRegistry, 14 concrete command handler classes, the `add_move_order_if_needed` utility function, and the `create_default_registry` factory. This is a god-module that aggregates too many responsibilities in one file.
**Impact:** Hard to navigate, increased merge conflicts, and makes code ownership unclear. Each handler has different concerns (fleet orders, construction queues, fleet management) that should map to separate files.
**Recommendation:** Split into separate files by domain, mirroring the structure already used for `superweapon_command_handlers.py` and `planet_command_handlers.py`:
- `command_handlers/base.py` -- BaseCommandHandler, ICommandHandler, CommandHandlerRegistry
- `command_handlers/fleet_order_handlers.py` -- Move, Colonize, Intercept, Join, ClearOrders, Warp, Transfer, ColonizeMission
- `command_handlers/fleet_management_handlers.py` -- Split, DeleteOrder, ReorderOrder
- `command_handlers/construction_queue_handlers.py` -- Add/Remove/Reorder construction queue
- `command_handlers/registry.py` -- create_default_registry()
**Effort:** Medium

---

#### MAJOR: Dead Code / Stale Comments in pathfinding.py
**ID:** CQ-002
**Location:** `game/strategy/data/pathfinding.py:80-140`
**Issue:** The `find_path_interstellar` function contains extensive "thinking aloud" comments left from initial development: "Wait, galaxy.systems is keyed by location", "Optimization: Build name_to_system cache or linear search?", "Cost is distance? Or just +1 hop?", etc. There is also a dead assignment at line 89 (`current_sys = galaxy.systems[...]`) that is immediately overwritten at line 104.
**Impact:** Misleading for maintainers; the comments suggest uncertainty about the design, and the dead code wastes reader attention. Violates the clean-sheet design rule.
**Recommendation:** Remove all "thinking aloud" comments and the dead assignment. Replace with concise doc explaining the actual A* implementation decisions.
**Effort:** Simple

---

#### MAJOR: Duplicate Stabilizer Check Pattern in SuperweaponOrderProcessor
**ID:** CQ-003
**Location:** `game/strategy/engine/superweapon_order_processor.py:707-815`
**Issue:** Three nearly identical private methods `_is_planet_stabilized`, `_is_system_stellar_stabilized`, and `_is_system_warp_stabilized` each iterate empires and scopes calling `find_abilities_in_scope` with the same pattern. They differ only in the ability name string and the scopes checked. This is a DRY violation.
**Impact:** If the stabilizer-checking logic ever changes (e.g., new scope added), it must be updated in three places. Bug risk from drift between the methods.
**Recommendation:** Extract a single parameterized method:
```python
def _is_stabilized(self, ability_name: str, target_or_location, galaxy, empires, scopes: list) -> bool:
    ref = self._get_reference(target_or_location, galaxy, empires)
    if ref is None: return False
    for empire in empires:
        for scope in scopes:
            if find_abilities_in_scope(ability_name, ref, galaxy, empire, scope):
                return True
    return False
```
**Effort:** Simple

---

#### MAJOR: Mock Object Hack in FleetNavigationService.compute_path
**ID:** CQ-004
**Location:** `game/strategy/services/fleet_navigation_service.py:185-200`
**Issue:** `compute_path()` creates a `MockCapabilities` inner class and a dynamic `fleet_like` object using `type()` just to satisfy the `find_hybrid_path` function's `fleet` parameter. This is a workaround rather than fixing the interface. The function needs only a `can_warp` boolean but the API demands a full fleet-like object.
**Impact:** Fragile -- any change to what `find_hybrid_path` reads from the fleet object will silently break this mock. Violates Rule 3 (clean-sheet design: "DO NOT monkey-patch objects to change behavior -- redesign the interface").
**Recommendation:** Refactor `find_hybrid_path` to accept an explicit `can_warp: bool` parameter (or accept `NavigationState` directly), eliminating the need for mock objects.
**Effort:** Medium

---

#### MAJOR: Duplicated Ownership Check Pattern in planet_command_handlers.py
**ID:** CQ-005
**Location:** `game/strategy/engine/planet_command_handlers.py:47,106,124,145`
**Issue:** The pattern `planet.owner_id != session.player_empire.id` with `return ValidationResult.error("Planet does not belong to this empire.")` is repeated verbatim in 4 out of 4 handler methods. This is copy-paste code that should be in a base class or shared method.
**Impact:** If the ownership error message or logic changes, four places must be updated. The planet command handlers also do not extend `BaseCommandHandler`, inconsistent with every other handler family.
**Recommendation:** Have the planet command handlers extend `BaseCommandHandler` and add a `_validate_planet_ownership(session, planet)` helper to the base. Alternatively, add planet resolution + ownership check as a single helper.
**Effort:** Simple

---

#### MAJOR: Planet Lookup O(N*M) in Facade._get_planet_by_id
**ID:** CQ-006
**Location:** `game/strategy/facade/strategy_session_facade.py:279-292`
**Issue:** `_get_planet_by_id` iterates all systems then all planets in each system for an O(systems * planets) lookup. Meanwhile, `Galaxy` already has `planets_by_id` dict for O(1) lookups, and `GameSession._get_planet_by_id` likely uses it. The facade creates its own slower version instead of delegating.
**Impact:** Performance degradation for frequent planet lookups from the UI layer, especially in large galaxies. Inconsistency between facade and session planet resolution.
**Recommendation:** Delegate to `self._session._get_planet_by_id(planet_id)` or `self._session.galaxy.get_planet_by_id(planet_id)`, matching the pattern used for fleet lookups.
**Effort:** Simple

---

#### MAJOR: Oversized Files Exceeding 500-Line Target
**ID:** CQ-007
**Location:** Multiple files
**Issue:** Nine files exceed the 500-line convention target:
- `engine/command_handlers.py` -- 1062 lines (2.1x)
- `engine/superweapon_order_processor.py` -- 815 lines (1.6x)
- `engine/order_processor.py` -- 762 lines (1.5x)
- `data/stars.py` -- 759 lines (1.5x)
- `services/ship_stats_calculator.py` -- 750 lines (1.5x)
- `services/fleet_navigation_service.py` -- 697 lines (1.4x)
- `data/galaxy.py` -- 653 lines (1.3x)
- `engine/production_engine.py` -- 620 lines (1.2x)
- `data/ship_instance.py` -- 606 lines (1.2x)
**Impact:** Harder to navigate and maintain. Some of these (galaxy.py, ship_instance.py) have already been partially decomposed via delegates, but remain over budget.
**Recommendation:** Prioritize splitting the top 3 (command_handlers.py, superweapon_order_processor.py, order_processor.py). The data files (stars.py, galaxy.py) are more naturally cohesive and lower priority.
**Effort:** Medium

---

#### MAJOR: Broad Exception Catches
**ID:** CQ-008
**Location:** `game/strategy/data/empire.py:329`, `game/strategy/data/fleet.py:394`, `game/strategy/data/order_serializer.py:57`
**Issue:** Three deserialization locations use bare `except Exception as e` to catch all errors during entity reconstruction. While the intent (skip corrupt entries) is reasonable, catching `Exception` is too broad and can mask programming errors (AttributeError, TypeError from code bugs vs. data corruption).
**Impact:** Bugs in deserialization code are silently swallowed and logged as "corrupt data," making debugging difficult.
**Recommendation:** Narrow catches to `(KeyError, ValueError, TypeError, PersistenceException)` or whatever the known data corruption exceptions are. This matches the pattern used in `galaxy.py:637` which already uses specific exception types.
**Effort:** Simple

---

#### MINOR: Duplicate TYPE_CHECKING Import Block
**ID:** CQ-009
**Location:** `game/strategy/engine/superweapon_command_handlers.py:21-33`
**Issue:** Two separate `if TYPE_CHECKING:` blocks import from the same location. The second block (line 32-33) re-imports `GameSession` which is already imported in the first block (line 21).
**Impact:** Minor clutter and confusion. No runtime effect since both are TYPE_CHECKING guarded.
**Recommendation:** Merge into a single `if TYPE_CHECKING:` block.
**Effort:** Simple

---

#### MINOR: Inconsistent Handler Base Class Usage
**ID:** CQ-010
**Location:** `game/strategy/engine/planet_command_handlers.py:26-153`
**Issue:** The planet command handler classes (`IssuePlanetOrderCommandHandler`, `ClearPlanetOrdersCommandHandler`, etc.) do not extend `BaseCommandHandler`. Instead, they import and call `BaseCommandHandler._resolve_planet` as a static method from within each `execute()` method. Every other command handler family (fleet, superweapon, construction) inherits from `BaseCommandHandler`.
**Impact:** Inconsistent pattern makes the codebase harder to reason about. Planet handlers miss inherited helpers and future base class improvements.
**Recommendation:** Have planet handlers extend `BaseCommandHandler` and call `self._resolve_planet()` instead of `BaseCommandHandler._resolve_planet()`.
**Effort:** Simple

---

#### MINOR: Superweapon Mission Handlers Are Repetitive
**ID:** CQ-011
**Location:** `game/strategy/engine/superweapon_command_handlers.py:201-372`
**Issue:** The five mission command handlers (ImplodePlanetMission, StellerateStar Mission, OpenWarpPoint Mission, CloseWarpPoint Mission, CreateDysonSphere Mission) all follow an identical 5-step pattern: resolve fleet, validate, add_move_order_if_needed, queue action order, return success. They differ only in the validator called and the order type/target created.
**Impact:** 170 lines of near-identical code. Adding a new superweapon mission requires copying one and changing 3 values.
**Recommendation:** Create a generic `MissionCommandHandler` that accepts validator function, order type, and target builder as parameters. Each mission becomes a one-line registration.
**Effort:** Medium

---

#### MINOR: Superweapon Processor Methods Are Repetitive
**ID:** CQ-012
**Location:** `game/strategy/engine/superweapon_order_processor.py:127-628`
**Issue:** The five main processor methods (process_implode_planet, process_stellerate_star, process_open_warp_point, process_close_warp_point, process_create_dyson_sphere) all follow the same 5-step pattern: check order type, find system, check stabilizer, find ship with ability, execute effect, finalize. The `_finalize_superweapon` helper already consolidates the tail, but the head (order check, system resolution, stabilizer check, ability check) is repeated.
**Impact:** 500 lines of structurally similar code. New superweapons require copying 80+ lines of boilerplate.
**Recommendation:** Extract the common prologue into a template method pattern or a `_prepare_superweapon()` helper that returns (fleet, system, ship, order) or an error result.
**Effort:** Medium

---

#### MINOR: DesignLibrary Instantiated Repeatedly Per Command
**ID:** CQ-013
**Location:** `game/strategy/engine/command_handlers.py:869,904`
**Issue:** `AddToConstructionQueueCommandHandler._check_design_valid()` and `_load_design_cost()` each create a new `DesignLibrary(session.save_path, empire_id)` instance. If both are called for the same command (which they always are), two instances are created for the same empire in the same execution.
**Impact:** Minor performance cost (DesignLibrary creates directories in __init__). More importantly, it indicates a missing service-layer caching pattern.
**Recommendation:** Create the DesignLibrary once in `execute()` and pass it to both helpers, or cache it on the session.
**Effort:** Simple

---

#### MINOR: `process_self_destruct` Duplicates `_finalize_superweapon` Logic
**ID:** CQ-014
**Location:** `game/strategy/engine/superweapon_order_processor.py:630-705`
**Issue:** `process_self_destruct` manually implements the fleet cleanup and event logging that `_finalize_superweapon` already handles (pop order, check empty fleet, remove fleet, log event). It does not call `_finalize_superweapon` even though the finalization pattern is identical.
**Impact:** If finalization logic changes (e.g., new cleanup step), self_destruct will drift.
**Recommendation:** Refactor to use `_finalize_superweapon` with `consume_ship=False` after the multi-ship removal loop, or extend the helper to support batch ship removal.
**Effort:** Simple

---

#### MINOR: Stale Duplicate Step Numbering
**ID:** CQ-015
**Location:** `game/strategy/engine/command_handlers.py:821-825`
**Issue:** In `AddToConstructionQueueCommandHandler.execute()`, step comments jump from "4." to "5." (cost calculation), then another "5." (turns estimate). The second step 5 should be step 6, and step 6 below should be 7.
**Impact:** Cosmetic, but misleading when trying to follow the execution flow from comments.
**Recommendation:** Renumber the steps sequentially.
**Effort:** Simple

---

#### INFO: `_get_reference_planet` Returns First Planet Via For Loop
**ID:** CQ-016
**Location:** `game/strategy/engine/superweapon_order_processor.py:798-815`
**Issue:** `_get_reference_planet` uses a for loop that immediately returns the first planet: `for planet in planets: return planet`. This is a roundabout way to write `return planets[0] if planets else None`.
**Impact:** No functional issue, but obscures intent.
**Recommendation:** Replace with `return planets[0] if planets else None`.
**Effort:** Simple

---

#### INFO: Galaxy.__init__ Does File I/O (CWD-Dependent Paths)
**ID:** CQ-017
**Location:** `game/strategy/data/galaxy.py:179-189`
**Issue:** Galaxy's constructor loads YAML and JSON files using `os.path.join(os.getcwd(), ...)` for star system names and storm definitions. This couples the Galaxy class to the current working directory and makes it harder to test.
**Impact:** Tests must be run from the project root or set up CWD correctly. Makes Galaxy harder to use in isolation.
**Recommendation:** Accept file paths as constructor parameters with defaults resolved via a centralized `Paths` utility (which already exists in `game.core.paths`), consistent with how `SaveGameService` resolves paths.
**Effort:** Medium

---

#### INFO: Facade Exposes Private Session Methods
**ID:** CQ-018
**Location:** `game/strategy/facade/strategy_session_facade.py:83-94`
**Issue:** The facade's `_get_fleet_by_id` and `_get_empire_by_id` methods are marked private (single underscore) but access `self._session._get_fleet_by_id()` -- a private method on GameSession. The facade exists to prevent UI from accessing session internals, but its own implementation reaches into private methods.
**Impact:** If GameSession's internal API changes, the facade breaks. The abstraction boundary is somewhat porous.
**Recommendation:** Add public query methods to GameSession (e.g., `get_fleet_by_id`) that the facade delegates to, keeping the private underscored versions truly internal. Low urgency since both layers are in the strategy package.
**Effort:** Simple

---

### Top 5 Priority Issues

1. **CQ-001 (CRITICAL)** -- command_handlers.py at 1062 lines is a god-module. Split by domain (fleet orders, construction, fleet management) to match existing patterns for superweapon and planet handlers.

2. **CQ-004 (MAJOR)** -- MockCapabilities/fleet_like hack in FleetNavigationService violates clean-sheet design. Refactor `find_hybrid_path` to accept `can_warp: bool` directly.

3. **CQ-003 (MAJOR)** -- Three near-identical stabilizer check methods in SuperweaponOrderProcessor. Extract a single parameterized method to eliminate the DRY violation.

4. **CQ-006 (MAJOR)** -- O(N*M) planet lookup in facade when O(1) is available. Simple delegation fix with immediate performance improvement.

5. **CQ-011 + CQ-012 (MINOR)** -- Repetitive superweapon handlers (both command and processor). A template method or parameterized handler would eliminate ~300 lines of near-duplicate code.
