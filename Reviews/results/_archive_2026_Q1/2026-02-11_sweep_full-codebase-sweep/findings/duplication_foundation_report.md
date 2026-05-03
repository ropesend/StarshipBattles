# Duplication & Fragmentation Sweep: Foundation

## Summary
- **Shard:** Foundation
- **Directories:** `game/core/`, `game/ai/`, `game/research/`, `game/engine/`
- **Files Scanned:** 43
- **Total Issues Found:** 10
- **Critical:** 1 | **Major:** 4 | **Minor:** 4 | **Info:** 1

## Findings

#### CRITICAL: Duplicated Resource Loading Logic (`load_resources` vs `load_resources_data`)
**ID:** DUP-FND-001
**Location:** `game/core/resources.py:55-98` AND `game/core/resources.py:101-143`
**Issue:** Two near-identical functions `load_resources_data()` and `load_resources()` implement the same resource-loading logic with the same error handling pattern. Both call `_resolve_resource_path()`, both call `load_json_required()`, both iterate over `data.get('resources', [])`, and both have identical 4-branch exception handling (FileNotFoundError, JSONDecodeError, PermissionError/OSError, TypeError/AttributeError) with the same fallback to `_get_default_resources()`. The only difference is that `load_resources_data()` returns a dict (pure function) while `load_resources()` writes to the RegistryManager singleton. This is 88 lines of near-duplicate code with active divergence risk -- the pure function does `copy.deepcopy(res_def)` while the singleton version does not, meaning one path gets defensive copies and the other does not.
**Impact:** If a bug fix is applied to one function's error handling, the other is very likely to be missed. The `deepcopy` inconsistency could lead to shared mutable state bugs. The docstring on `load_resources()` even acknowledges it as a "thin wrapper" but it is a full reimplementation, not a wrapper.
**Recommendation:** Make `load_resources()` a true thin wrapper that delegates to `load_resources_data()`, e.g.: `resources.update(load_resources_data(file_path))`. Delete the 40+ lines of duplicated logic inside `load_resources()`.
**Effort:** Simple

#### MAJOR: StrategyMetadataService Uses Hand-Rolled Singleton Instead of SingletonMeta
**ID:** DUP-FND-002
**Location:** `game/core/strategy_metadata.py:50-94` AND `game/core/singleton.py:27-98`
**Issue:** `StrategyMetadataService` implements its own singleton pattern with `_instance`, `_lock`, double-checked locking in `instance()`, and `reset()` -- exactly the same pattern that `SingletonMeta` was created to eliminate. The module docstring for `singleton.py` states it "Eliminates duplicate singleton boilerplate in ~7 classes." Every other singleton in `game/core/` (Logger, Profiler, ScreenshotManager, RegistryManager) uses `SingletonMeta`, but `StrategyMetadataService` has 25+ lines of hand-rolled singleton boilerplate that duplicates the metaclass functionality. Additionally, StrategyMetadataService's `__init__` raises `StateException` to prevent direct construction, which is unnecessary with `SingletonMeta` (which naturally makes `MyClass()` return the singleton).
**Impact:** Maintenance overhead of two singleton implementations. If the singleton pattern needs to change (e.g., for async support), this class will be missed. The hand-rolled version also has a subtle difference: `__init__` raises if `_instance is not None`, but this check happens after `_instance` is already set by the `instance()` method, creating a race window that `SingletonMeta` handles correctly.
**Recommendation:** Migrate `StrategyMetadataService` to `metaclass=SingletonMeta`. Remove the `_instance`, `_lock`, `instance()`, and `reset()` boilerplate. Replace `StateException` guard in `__init__` with natural SingletonMeta behavior.
**Effort:** Simple

#### MAJOR: Repeated "Flee Away" Vector Pattern Across AI Behaviors
**ID:** DUP-FND-003
**Location:** `game/ai/behaviors.py:95-101` (FleeBehavior) AND `game/ai/behaviors.py:213-218` (AttackRunBehavior retreat) AND `game/ai/controller.py:447-451` (check_avoidance)
**Issue:** Three locations implement the identical "calculate flee direction" pattern:
1. Get vector from target to ship: `vec = ship_pos - target.position`
2. Guard zero-length: `if vec.length() == 0: vec = Vector2(1, 0)`
3. Calculate flee position: `flee_pos = ship_pos + vec.normalize() * DISTANCE`
4. Navigate to flee position: `self.controller.navigate_to(flee_pos, ...)`

The code is structurally identical across all three sites with only the distance constant and stop_dist varying. Additionally, `KiteBehavior.update()` at line 147-152 uses the same pattern for kiting (move away to maintain distance).
**Impact:** If the flee logic needs updating (e.g., adding obstacle avoidance or noise), all 3-4 locations must be updated in sync. Copy-paste drift is already visible: `FleeBehavior` and `AttackRunBehavior` use `self.FLEE_DISTANCE` while `check_avoidance` uses `BattleConfig.AVOIDANCE_TARGET_DISTANCE`.
**Recommendation:** Extract a shared `calculate_flee_position(from_pos, away_from_pos, distance)` utility method on `AIController` or as a standalone function in `combat_utils.py`.
**Effort:** Simple

#### MAJOR: Repeated Entity ID Fallback Pattern in AI Layer
**ID:** DUP-FND-004
**Location:** `game/ai/combat_utils.py:65` AND `game/ai/combat_utils.py:97` AND `game/ai/controller.py:193` AND `game/ai/controller.py:221` AND `game/ai/controller.py:413`
**Issue:** The expression `getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))` is repeated verbatim 5 times across 2 files. This is a defensive entity identification pattern used for logging context. Each instance duplicates the same 3-level fallback logic: try `.id`, then `.name`, then `id(obj)`.
**Impact:** If the fallback logic changes (e.g., adding `.label` as an option, or changing the format), 5 locations must be updated. Minor bug risk but high cognitive overhead when reading the code.
**Recommendation:** Extract to a shared `get_entity_id(entity)` function in `combat_utils.py` (which already exists as a utility module). Use it from all 5 call sites.
**Effort:** Simple

#### MAJOR: Inline Angle Difference Calculation Instead of Using `game.core.math.angle_diff`
**ID:** DUP-FND-005
**Location:** `game/ai/controller.py:462` AND `game/ai/behaviors.py:290` AND `game/ai/combat_utils.py:223`
**Issue:** Three locations compute angle difference with the inline formula `(angle_a - angle_b + 180) % 360 - 180`, despite `game.core.math` providing a canonical `angle_diff(from_angle, to_angle)` function that does the exact same calculation: `diff = (to_angle - from_angle) % 360; if diff > 180: diff -= 360`. These are mathematically equivalent. The AI layer does not import or use the core `angle_diff` function anywhere. Additionally, the `navigate_to` method in controller.py manually computes `math.degrees(math.atan2(dy, dx)) % 360` for the target angle, while `Vector2.angle_to()` in `game.core.math` provides this exact computation.
**Impact:** Inconsistency between layers. If the angle_diff formula needs to be fixed for edge cases (e.g., at exactly 180 degrees), the core function would be updated but the AI inline implementations would be missed.
**Recommendation:** Replace inline angle difference calculations with `from game.core.math import angle_diff` calls. Replace `math.degrees(math.atan2(dy, dx))` patterns with `Vector2.angle_to()` where applicable.
**Effort:** Simple

#### MINOR: `_resolve_resource_path` Reimplements Project Root Discovery
**ID:** DUP-FND-006
**Location:** `game/core/resources.py:31-52` AND `game/core/paths.py:21-43`
**Issue:** `_resolve_resource_path()` manually computes the project root via `os.path.dirname(os.path.abspath(__file__))` walking up directory levels, while `game/core/paths.py` already has `_find_project_root()` and the `Paths` class with `ROOT_DIR`, `DATA_DIR`, and `RESOURCES_FILE` constants. The resources module could simply use `Paths.RESOURCES_FILE` for the default path instead of maintaining its own root-finding logic with `os.path.join(project_root, file_path)`.
**Impact:** Low risk since both approaches reach the same directory, but it is conceptual duplication. If the project structure changes, `_resolve_resource_path` might break independently of `Paths`.
**Recommendation:** Replace `_resolve_resource_path()` with `Paths.RESOURCES_FILE` for the default path, and use `Paths.get_root() / file_path` for custom paths.
**Effort:** Simple

#### MINOR: Repeated Zero-Vector Guard Pattern in AI Behaviors
**ID:** DUP-FND-007
**Location:** `game/ai/behaviors.py:97-98` AND `game/ai/behaviors.py:148-149` AND `game/ai/behaviors.py:215-216` AND `game/ai/controller.py:449-450`
**Issue:** Four locations repeat the exact same guard: `if vec.length() == 0: vec = Vector2(1, 0)`. This is a safety check to prevent normalizing a zero-length vector. While each instance is only 2 lines, the pattern is identical and spread across behaviors and controller.
**Impact:** Low maintenance risk since the pattern is simple, but it adds noise. If the default direction ever needed to change (e.g., randomized to prevent deterministic stacking), all 4 sites would need updating.
**Recommendation:** Could be absorbed into the proposed `calculate_flee_position` utility (DUP-FND-003) or a `safe_normalize(vec, default=Vector2(1,0))` helper. Low priority.
**Effort:** Simple

#### MINOR: AIController._get_hp_percent and _is_in_pdc_arc Are Trivial Pass-Through Wrappers
**ID:** DUP-FND-008
**Location:** `game/ai/controller.py:269-273`
**Issue:** `AIController._get_hp_percent(self, ship)` simply returns `get_hp_percent(ship)` and `_is_in_pdc_arc(self, target)` simply returns `is_in_pdc_arc(self.ship, target)`. These are 1-line methods that add no logic, just delegate to `combat_utils`. They were likely created during PROJ-108 refactoring as intermediate steps. The `_get_hp_percent` wrapper is called from one location (line 332) and `_is_in_pdc_arc` is never called at all (dead code).
**Impact:** Minor code bloat. `_is_in_pdc_arc` is dead code that should be removed. `_get_hp_percent` could be inlined.
**Recommendation:** Delete `_is_in_pdc_arc` (dead code). Inline `_get_hp_percent` by replacing `self._get_hp_percent(self.ship)` with `get_hp_percent(self.ship)` at the single call site.
**Effort:** Simple

#### MINOR: `load_data` Duplication Between StrategyManager and StrategyMetadataService
**ID:** DUP-FND-009
**Location:** `game/ai/strategy_manager.py:83-99` AND `game/core/strategy_metadata.py:166-188`
**Issue:** Both `StrategyManager.load_data()` and `StrategyMetadataService.load_data()` load strategy data from the same JSON file (`combat_strategies.json`). `StrategyManager.load_data()` loads the file and then calls `StrategyMetadataService.instance().set_strategies(self.strategies)` to populate the metadata service. However, `StrategyMetadataService.load_data()` also independently loads the same file for cases where StrategyManager is not involved (e.g., WorkshopDataLoader). This creates two code paths that read the same JSON file for the same purpose.
**Impact:** If the JSON structure changes, both load paths must be updated. The docstring on `StrategyMetadataService.load_data()` notes it is "Used by WorkshopDataLoader" as an alternative to going through StrategyManager.
**Recommendation:** Consider making StrategyManager the single authority for loading strategy data, with StrategyMetadataService only receiving data via `set_strategies()`. Alternatively, have `StrategyMetadataService.load_data()` delegate to a shared parsing function.
**Effort:** Medium

#### INFO: Paths Class Maintains Both String and Path Properties
**ID:** DUP-FND-010
**Location:** `game/core/paths.py:46-134`
**Issue:** The `Paths` class defines every path twice: once as an `os.path.join` string (class attribute) and once as a `pathlib.Path` (classmethod). For example, `DATA_DIR = os.path.join(ROOT_DIR, "data")` and `get_data_dir()` returns `_PROJECT_ROOT / "data"`. Similarly, `SAVES_DIR = os.path.join(OUTPUT_DIR, "saves")` and `get_saves_dir()` returns `_PROJECT_ROOT / "output" / "saves"`. Only a subset of directories have Path versions (root, data, assets, output, saves, logs, planets_v3), creating an inconsistent dual API.
**Impact:** Not a significant maintenance risk since both approaches point to the same paths, but it is conceptual duplication. New code might use either form inconsistently. The string paths reconstruct intermediate segments (e.g., `PLANETS_V3_DIR` is a chain from `ASSET_DIR`), while the Path versions independently reconstruct from `_PROJECT_ROOT`.
**Recommendation:** This is a legacy pattern. If the codebase standardizes on `pathlib.Path`, the string properties could be deprecated. Low priority -- this is an observation, not a recommendation for immediate action.
**Effort:** Medium (requires updating all callers if standardizing)

## Top 5 Priority Issues

1. **DUP-FND-001 (CRITICAL):** `load_resources_data()` and `load_resources()` are near-identical with 88 lines of duplicated error handling and a `deepcopy` inconsistency that could cause shared mutable state bugs. Fix is trivial: make `load_resources()` delegate to `load_resources_data()`.

2. **DUP-FND-005 (MAJOR):** Three inline angle-difference calculations in the AI layer ignore the canonical `game.core.math.angle_diff()` function, creating cross-layer inconsistency and edge-case divergence risk. Simple import-and-replace fix.

3. **DUP-FND-003 (MAJOR):** The "flee away from position" vector calculation pattern is copy-pasted 3-4 times across AI behaviors and controller. Extract to a shared utility function.

4. **DUP-FND-002 (MAJOR):** `StrategyMetadataService` has 25+ lines of hand-rolled singleton boilerplate that duplicates the `SingletonMeta` metaclass used by every other singleton in `game/core/`. Migration is straightforward.

5. **DUP-FND-004 (MAJOR):** The `getattr(entity, 'id', getattr(entity, 'name', str(id(entity))))` entity ID fallback is repeated 5 times. Extract to `get_entity_id()` in `combat_utils.py`.
