# Remediation Strategist Report

### Summary
- Total issues found: 14
- Critical: 2, Major: 5, Minor: 5, Info: 2

---

### Strategy Assessments

#### Strategy 1: Strict Layering & Facades
**Feasibility:** High
**Impact:** Medium
**Effort:** Simple
**Risk:** Low
**Current State:** A well-designed facade (`StrategySessionFacade`) already exists at `game/strategy/facade/strategy_session_facade.py`. It implements a CQRS-lite pattern with Command objects for writes and DTOs for reads. The `game/strategy/engine/commands.py` module defines pure data command classes with no business logic. The `CommandHandlerRegistry` in `game/strategy/engine/command_handlers.py` dispatches commands to dedicated handler classes.

**Assessment:**
The facade/command pattern is already substantially in place. The UI layer issues commands via `facade.handle_command(cmd)` and reads state via DTO-returning query methods. However, there are inconsistencies:

1. **Some UI files import commands at top level** (`strategy_colonization.py`, `strategy_superweapons.py`, `cargo_quick_dialog.py`, `transfer_dialog.py`) -- these are clean and acceptable because `commands.py` is a pure-data module with no circular risk.

2. **Some UI files defer command imports into methods** (`strategy_window_manager.py:282`, `strategy_fleet_ops.py:120/148/192`, `strategy_build_queue_manager.py:131`) -- these deferred imports are unnecessary since `commands.py` has only stdlib and `game.core.hex_math` dependencies. They could safely be moved to top level.

3. **The `strategy_build_queue_manager.py` reaches through `self._screen.session.handle_command(cmd)`** instead of going through the facade, which is a minor layering violation.

4. **The `strategy_window_manager.py:282`** creates a `ClearFleetOrdersCommand` inside a closure, deferring the import -- again unnecessary since commands.py is leaf-level.

The facade pattern is working well. The remaining deferred imports of command classes in the UI layer are **not caused by circular dependencies** -- they appear to be cargo-culted from earlier patterns or added out of caution. These can simply be promoted to top-level imports.

**Recommendation:** Do it (low-hanging fruit). Promote 5 deferred command imports to top-level in UI files. Fix the 1 facade bypass in `strategy_build_queue_manager.py`. No architecture changes needed -- the infrastructure already exists.

---

#### Strategy 2: Extract DTOs & Enums
**Feasibility:** High
**Impact:** High
**Effort:** Medium
**Risk:** Low
**Current State:** `OrderType` (an enum with 17 values), `FleetOrder` (a data class), and `MOVEMENT_ORDER_TYPES`/`ACTION_ORDER_TYPES` (frozensets) are all defined in `game/strategy/data/fleet.py` alongside the heavyweight `Fleet` class (553 lines). There is no existing `game/strategy/data/enums.py` or similar.

**Assessment:**
This is the single largest source of deferred imports in the codebase. The pattern is clear and pervasive:

- **15 deferred imports** of `OrderType`/`FleetOrder` from `fleet.py` across 4 files
- **11 of those** are in `command_handlers.py` alone, where every handler method does `from game.strategy.data.fleet import FleetOrder, OrderType`
- `fleet.py` imports `FleetResourceAggregator`, `FleetCapabilityCalculator`, `FleetBattleAdapter`, and `ShipInstance` at the top level, creating a heavy import tree
- Files like `action_time_resolver.py` wrap `OrderType` access in helper functions (`_get_order_to_ability_map()`, `_get_movement_order_types()`) purely to defer the import

The root cause is that `fleet.py` is a "monolithic model" -- it combines pure data types (OrderType, FleetOrder) with a heavyweight domain class (Fleet) that has many dependencies. Importing `OrderType` drags in the entire Fleet dependency graph.

**Extraction targets:**
1. `OrderType` enum --> `game/strategy/data/order_types.py`
2. `FleetOrder` class --> same file (it only depends on OrderType + HexCoord)
3. `MOVEMENT_ORDER_TYPES` and `ACTION_ORDER_TYPES` frozensets --> same file
4. `fleet.py` would then import from `order_types.py` and re-export for backward compat

**Impact analysis:**
- 27 files import `OrderType` (18 via grep for `OrderType` generally, 15 of which are deferred)
- After extraction, all 15 deferred imports could become top-level
- `command_handlers.py` alone would lose 11 deferred imports
- No circular dependency risk: `order_types.py` would depend only on `game.core.hex_math`

**Other candidates for similar extraction:**
- `EventType` and `EventCategory` enums are already properly in `game/strategy/events/event_types.py` -- good precedent
- `ResourceType` is in `game/core/constants.py` -- already extracted
- `PlanetType` is in `game/strategy/data/planet.py` but is not causing deferred import issues

**Recommendation:** Do it. This is the highest-impact single change. Extract `OrderType`, `FleetOrder`, and the order type sets to `game/strategy/data/order_types.py`. This eliminates roughly 15 deferred imports immediately and sets a precedent for clean data model organization.

---

#### Strategy 3: Dependency Injection
**Feasibility:** Medium
**Impact:** Medium
**Effort:** Medium
**Risk:** Medium
**Current State:** The codebase has a well-established DI infrastructure:

1. **`RegistryManager`** singleton (game/core/registry.py) -- stores component/modifier/vehicle class/resource registries
2. **`DefaultRegistryProvider`** -- production implementation wrapping the singleton
3. **`TestRegistryProvider`** -- isolated test implementation
4. **`get_default_registry_provider()`** -- factory function for DI
5. **`GameRegistries`** -- frozen dataclass bundling all registries

DI is already used in 24 files (those importing `get_default_registry_provider` or `GameRegistries`). However, many files still use inline access patterns:

- `fleet_capability_calculator.py` has a module-level `_get_default_component_registry()` helper that calls `get_default_registry_provider().get_components()` -- this is effectively service-locator rather than true DI
- `strategy_session_facade.py:493` does `from game.core.registry import get_default_registry_provider` inline in `get_fleet_remaining_pods()`
- `empire_economy_calculator.py:60` does the same inline

**Assessment:**
DI is appropriate for **service-level dependencies** (registries, validators, calculators) but is **not a good fit for the core deferred import problem**. The biggest cluster of deferred imports (OrderType/FleetOrder in command_handlers.py) is about **data type imports**, not service resolution. You cannot inject an enum via DI.

The "intentional late imports" documented in ARCHITECTURE.md fall into categories:
1. **Cross-layer boundary** (strategy -> simulation): `ShipSerializer`, `ShipStatsCalculator` -- DI could help here by injecting a stats calculator interface
2. **Circular within layer** (data <-> services): `FleetSpeedCalculator`, `ComponentInspector` -- DI could help by injecting these as service dependencies
3. **Pure data type circularity** (Fleet <-> Planet, OrderType imports) -- DI is not the right tool; extraction is

For the 15 "INTENTIONAL LATE IMPORT" sites, roughly 5-6 could potentially benefit from DI (the service-based ones), while the rest are better solved by extraction or interface separation.

**Recommendation:** Defer for now. The existing DI infrastructure is adequate. Apply DI selectively to the 5-6 service-level deferred imports after the higher-impact extraction work (Strategy 2) is complete. Do not over-engineer DI for data type imports.

---

#### Strategy 4: Linting Restrictions
**Feasibility:** Low (short-term), Medium (long-term)
**Impact:** Low (preventive only)
**Effort:** Medium
**Risk:** Low
**Current State:** The project has **zero linting configuration**. No `.flake8`, `pylintrc`, `setup.cfg`, `pyproject.toml`, `ruff.toml`, or `tox.ini` files exist anywhere in the repository. There is no CI pipeline configuration visible either.

**Assessment:**
A blanket ban on nested imports would flag approximately 591 deferred import sites across 211 files. This is impractical without first resolving the underlying architectural issues. Many of these deferred imports are:

1. **Intentional and documented** (15 sites with "INTENTIONAL LATE IMPORT" comments)
2. **In app.py** (14 sites for lazy screen loading -- legitimate performance optimization)
3. **In TYPE_CHECKING blocks** (these would need to be exempted)
4. **Working around real circular dependencies** that need structural fixes first

A useful exceptions policy would need to allow:
- `if TYPE_CHECKING:` blocks (standard Python pattern)
- `app.py` lazy screen imports (startup performance)
- Documented "INTENTIONAL LATE IMPORT" sites (documented architecture decisions)
- Test fixtures and conftest files

Even with exceptions, introducing linting tooling on a project with no existing linting culture would be a significant process change.

**Recommendation:** Skip for now. Introduce linting only after the structural fixes (Strategies 2 and 1) have reduced the deferred import count. At that point, a `ruff` configuration with `TID252` (banned-module-level-imports) or a custom import-graph checker would be more practical. The team should first establish a linting baseline (even just `ruff check --select=I` for import sorting) before adding architectural lint rules.

---

#### Strategy 5: General Deferred Import Elimination
**Feasibility:** Medium
**Impact:** High (cumulative)
**Effort:** Complex
**Risk:** Medium
**Current State:** 591 deferred/nested import sites across 211 files in the `game/` directory.

**Assessment:**
Not all deferred imports are problematic. They fall into distinct categories:

| Category | Count | Action |
|----------|-------|--------|
| `command_handlers.py` OrderType/FleetOrder | 11 | Fix via Strategy 2 (extraction) |
| Other OrderType deferred imports | 4 | Fix via Strategy 2 (extraction) |
| UI command imports (unnecessary deferral) | 5 | Fix via Strategy 1 (promote to top-level) |
| `app.py` screen lazy loading | 14 | Keep (legitimate performance optimization) |
| INTENTIONAL LATE IMPORT (documented) | 15 | Keep 10, fix 5 via DI (Strategy 3) |
| TYPE_CHECKING blocks | ~100+ | Keep (standard Python pattern, not actual deferred imports) |
| Other deferred imports (various) | ~40 | Evaluate case-by-case after above fixes |

After applying Strategies 1 and 2, approximately 20 deferred imports would be eliminated. The remaining ~40 non-documented, non-TYPE_CHECKING deferred imports would need individual analysis. Many may turn out to be safe to promote once the Fleet/OrderType extraction removes the main import cycle anchor.

**Recommendation:** Treat as ongoing cleanup. After Strategies 1 and 2, do a second pass to identify remaining deferred imports that can be safely promoted. Target: reduce the 591 count to under 550 in the first pass, then to under 530 in a second pass.

---

### Prioritized Implementation Order

| Priority | Strategy | Rationale |
|----------|----------|-----------|
| 1 | **Strategy 2: Extract DTOs & Enums** | Highest impact, eliminates 15+ deferred imports from the single most affected file. Low risk since extracted types are pure data with no side effects. Sets a clean precedent. |
| 2 | **Strategy 1: Promote Command Imports** | Quick wins -- 5 unnecessary deferred imports in UI files can be promoted to top-level today. Fix 1 facade bypass. Zero architectural risk. |
| 3 | **Strategy 3: Selective DI** | Apply DI to 5-6 cross-layer service imports after extraction work clears the landscape. Moderate effort, moderate impact. |
| 4 | **Strategy 5: General Cleanup** | Second-pass elimination of remaining deferred imports once the structural fixes are in place. |
| 5 | **Strategy 4: Linting** | Only after the codebase is in a cleaner state. Introduce `ruff` with import rules as a preventive measure, not a corrective one. |

---

### Findings

#### CRITICAL: OrderType/FleetOrder in monolithic fleet.py causes 15+ deferred imports
**ID:** RS-001
**Location:** `game/strategy/data/fleet.py:20-61` (definitions), `game/strategy/engine/command_handlers.py` (11 sites), 3 other files
**Issue:** The `OrderType` enum and `FleetOrder` class are defined in `fleet.py` alongside the heavyweight `Fleet` class. Importing `OrderType` transitively imports `Fleet`, which imports `FleetResourceAggregator`, `FleetCapabilityCalculator`, `FleetBattleAdapter`, `ShipInstance`, and their dependency trees. This forces 15 files to use deferred imports for what should be a lightweight enum.
**Impact:** The command_handlers module -- the central dispatch hub for all strategy commands -- cannot use top-level imports for its most basic data types. This makes the code harder to read, harder to static-analyze, and violates the principle that enums should be leaf-level imports.
**Recommendation:** Extract `OrderType`, `FleetOrder`, `MOVEMENT_ORDER_TYPES`, and `ACTION_ORDER_TYPES` to `game/strategy/data/order_types.py`. Update `fleet.py` to import from the new module. Keep re-exports in `fleet.py` and `strategy/__init__.py` for backward compatibility during migration.
**Effort:** Medium (create new file, update 27 import sites, verify all tests pass)

#### CRITICAL: command_handlers.py has 16 deferred imports within method bodies
**ID:** RS-002
**Location:** `game/strategy/engine/command_handlers.py` (lines 50, 93, 263, 307, 355, 380, 409, 500, 527, 578, 601, 620, 666)
**Issue:** Every command handler method in this 713-line file starts with `from game.strategy.data.fleet import FleetOrder, OrderType`. The `create_default_registry()` function also defers importing all superweapon handlers. The `add_move_order_if_needed()` and `create_auto_load_population_order()` helper functions do the same.
**Impact:** 16 deferred import statements make this critical file harder to maintain, review, and refactor. Static analysis tools cannot trace the dependency graph correctly.
**Recommendation:** After RS-001 extraction, promote all `OrderType`/`FleetOrder` imports to top-level. The superweapon handler import in `create_default_registry()` (line 666) is legitimate (avoids loading handlers at module level) but could be restructured to use a plugin registration pattern.
**Effort:** Simple (after RS-001 is done, this is a mechanical find-and-replace)

#### MAJOR: UI files unnecessarily defer command imports
**ID:** RS-003
**Location:** `game/ui/screens/strategy_fleet_ops.py:120,148,192`, `game/ui/screens/strategy_window_manager.py:282`, `game/ui/screens/strategy_build_queue_manager.py:131`
**Issue:** These UI files defer imports of command classes (`IssueMoveCommand`, `IssueInterceptCommand`, `IssueJoinFleetCommand`, `ClearFleetOrdersCommand`, `IssueBuildOrderCommand`) that have no circular dependency risk. The `commands.py` module only depends on `game.core.hex_math`.
**Impact:** Unnecessary code complexity. Other UI files in the same layer (`strategy_colonization.py`, `strategy_superweapons.py`) already import commands at top level with no issues, proving these deferrals are unnecessary.
**Recommendation:** Move all 5 deferred command imports to top-level. This is a safe, zero-risk change.
**Effort:** Simple (5 lines changed across 3 files)

#### MAJOR: strategy_build_queue_manager.py bypasses the facade
**ID:** RS-004
**Location:** `game/ui/screens/strategy_build_queue_manager.py:142`
**Issue:** `self._screen.session.handle_command(cmd)` reaches through the scene to access `session` directly, bypassing the `StrategySessionFacade`. This violates the CQRS-lite architecture where all UI-to-engine communication should go through the facade.
**Impact:** Makes the code harder to test and monitor. The facade provides a single choke point for all commands, which is valuable for logging, validation, and debugging.
**Recommendation:** Route through `self._screen.facade.handle_command(cmd)` or `self._screen._facade.handle_command(cmd)` instead. Verify the screen has a facade reference.
**Effort:** Simple (1-line change, but verify the screen exposes the facade)

#### MAJOR: action_time_resolver.py wraps OrderType access in functions to avoid circular import
**ID:** RS-005
**Location:** `game/strategy/services/action_time_resolver.py:30-48`
**Issue:** Creates wrapper functions `_get_order_to_ability_map()` and `_get_movement_order_types()` whose sole purpose is to defer the `from game.strategy.data.fleet import OrderType` import. These functions are called on every order time resolution.
**Impact:** Performance overhead from repeated import lookups. Obscures the simple mapping between order types and abilities. Makes the module harder to understand.
**Recommendation:** After RS-001 extraction, convert these to module-level constants using top-level imports from `order_types.py`.
**Effort:** Simple (after RS-001)

#### MAJOR: FleetOrder.to_dict() imports Planet at runtime
**ID:** RS-006
**Location:** `game/strategy/data/fleet.py:78`
**Issue:** `FleetOrder.to_dict()` does `from game.strategy.data.planet import Planet` to check `isinstance(self.target, Planet)` during serialization. This is a real circular dependency: `fleet.py` and `planet.py` reference each other.
**Impact:** Called on every save game operation. The isinstance check is used for serialization dispatch.
**Recommendation:** Use duck typing or a protocol check instead of isinstance. For example, check `hasattr(self.target, 'planet_type')` or use a `target_type` attribute on FleetOrder to avoid needing to import Planet.
**Effort:** Medium (requires careful refactoring of the serialization dispatch logic)

#### MAJOR: fleet_capability_calculator.py uses service-locator pattern for registry
**ID:** RS-007
**Location:** `game/strategy/data/fleet_capability_calculator.py:14-17` and lines 41, 67, 117, 137, 184
**Issue:** Uses a module-level `_get_default_component_registry()` helper function that calls `get_default_registry_provider().get_components()`. This is a service-locator anti-pattern -- the calculator should receive the registry via its constructor or method parameters.
**Impact:** Makes unit testing harder (requires global state setup). Tightly couples data-layer code to the DI singleton.
**Recommendation:** Pass the component registry as a parameter to `FleetCapabilityCalculator.__init__()` or to individual methods. The `Fleet` class (which creates the calculator) can pass it through.
**Effort:** Medium (update constructor, update Fleet class, update call sites)

#### MINOR: Inconsistent command import patterns across UI files
**ID:** RS-008
**Location:** Codebase-wide (UI layer)
**Issue:** Some UI files import commands at top-level (`strategy_colonization.py`, `strategy_superweapons.py`, `cargo_quick_dialog.py`, `transfer_dialog.py`), while others defer them (`strategy_fleet_ops.py`, `strategy_window_manager.py`, `strategy_build_queue_manager.py`). There is no documented policy.
**Impact:** Inconsistency creates confusion about whether deferred imports are required or optional. New developers may cargo-cult the deferred pattern.
**Recommendation:** Standardize on top-level imports for all command classes. Document the policy that `game.strategy.engine.commands` is a leaf-level module safe for top-level import from any layer.
**Effort:** Simple

#### MINOR: fleet.py's trigger_speed_recalculation() is a documented intentional late import
**ID:** RS-009
**Location:** `game/strategy/data/fleet.py:191`
**Issue:** `from game.strategy.services.fleet_speed_calculator import FleetSpeedCalculator` is deferred inside `trigger_speed_recalculation()`. Documented as intentional: "Edge operation (only on ship add/remove)."
**Impact:** Low -- called infrequently. But the comment references a circular dependency that may no longer exist after PROJ-87 delegate extractions.
**Recommendation:** Re-test whether `FleetSpeedCalculator` can now be imported at module level. If the delegate extraction broke the cycle, promote to top-level. If not, leave as-is with updated documentation.
**Effort:** Simple (test and either promote or document)

#### MINOR: ship_instance.py has 3 documented cross-layer late imports
**ID:** RS-010
**Location:** `game/strategy/data/ship_instance.py:194, 254, 531`
**Issue:** Cross-layer imports from strategy->simulation (ShipSerializer, ShipStatsCalculator) are deferred. These are documented intentional patterns for maintaining layer separation.
**Impact:** Low -- these are edge operations (ship creation, stats caching, battle conversion). The layer boundary justifies the deferral.
**Recommendation:** Keep these as-is. They are well-documented and serve a legitimate architectural purpose. If the team later introduces an interface layer for strategy-simulation communication, these could be refactored to use protocol-based DI.
**Effort:** N/A (keep as-is)

#### MINOR: fleet_report_filters.py has 4 intentional late imports
**ID:** RS-011
**Location:** `game/ui/screens/fleet_report_filters.py:150, 187, 299, 307`
**Issue:** Four late imports of strategy data/service modules, all documented as intentional to avoid circular imports with strategy data.
**Impact:** Low -- filter functions are called on UI interaction, not hot paths.
**Recommendation:** Investigate whether the circular dependency still exists. The fleet_report_filters module is UI-layer and should be able to import strategy data modules at top-level (UI -> Strategy is allowed). If the cycle is actually UI -> Strategy -> UI, that's a deeper architecture issue.
**Effort:** Simple (test whether top-level import works)

#### MINOR: fleet_data_source.py has 4 intentional late imports
**ID:** RS-012
**Location:** `game/ui/screens/fleet_data_source.py:227, 235, 242, 262`
**Issue:** Late imports of `FleetSpeedCalculator`, `ShipStatsCalculator`, and `FleetCapabilityCalculator` from strategy services/data. All documented as avoiding circular imports.
**Impact:** Low -- called per-cell in table rendering but not on hot paths.
**Recommendation:** Same as RS-011 -- verify the circular dependency still exists. These are UI -> Strategy imports which should be legal. If the issue is transitive (Strategy -> ... -> UI), the fix belongs in the strategy layer.
**Effort:** Simple (test whether top-level import works)

#### INFO: app.py has 14 deferred imports for lazy screen loading
**ID:** RS-013
**Location:** `game/app.py:123, 245, 246, 261, 295-297, 338, 360, 408, 438, 476, 635, 711`
**Issue:** Deferred imports of UI screens, services, and strategy modules in App class methods.
**Impact:** None -- this is a legitimate and common pattern for application entry points. Lazy loading screens improves startup time.
**Recommendation:** Keep as-is. This is standard Python application architecture.
**Effort:** N/A (keep as-is)

#### INFO: No linting infrastructure exists
**ID:** RS-014
**Location:** Codebase-wide
**Issue:** No `.flake8`, `pylintrc`, `setup.cfg`, `pyproject.toml`, `ruff.toml`, or `tox.ini` exists in the repository. No automated code quality enforcement.
**Impact:** No prevention of new deferred imports being introduced. No consistent code style enforcement.
**Recommendation:** Introduce a minimal `pyproject.toml` with `ruff` configuration as a first step toward automated quality checks. Start with import sorting (`I`) and gradually add rules.
**Effort:** Medium (tool setup, initial baseline suppression, team process change)

---

### Top 5 Priority Issues

1. **RS-001** (Critical) -- Extract OrderType/FleetOrder from fleet.py to eliminate the root cause of 15+ deferred imports. This is the single highest-leverage change.

2. **RS-002** (Critical) -- Clean up command_handlers.py's 16 deferred imports. Becomes a trivial mechanical fix once RS-001 is complete.

3. **RS-003** (Major) -- Promote 5 unnecessary deferred command imports in UI files to top-level. Zero risk, immediate clarity improvement.

4. **RS-005** (Major) -- Eliminate action_time_resolver.py's wrapper functions after RS-001. Simplifies code and removes per-call overhead.

5. **RS-006** (Major) -- Fix FleetOrder.to_dict() circular dependency with Planet using duck typing. Removes the only real data-layer circular dependency in fleet.py.
