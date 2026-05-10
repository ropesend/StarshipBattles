# Test Review Report: Core + Engine Domain

## Scope
- Source files reviewed: game/core/ (24 files, 1604 stmts), game/engine/ (4 files, 154 stmts)
- Test files reviewed: 59 test files across tests/unit/core/, tests/unit/data/, tests/unit/engine/, tests/unit/fixtures/
- Total test LOC: ~13,947 lines
- Coverage data referenced: yes

## Summary
- Test files reviewed: 59
- Source files reviewed: 28
- Tests flagged for removal: 12 (estimated LOC: 186)
- Tests flagged as happy-path-only: 5
- Source files with inadequate coverage: 3

## A. Tests Recommended for Removal

### A1.
- **File:** tests/unit/core/test_combat_types.py
- **Test(s):** `TestDamageContext.test_import_path` (lines 33-35)
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 34 imports DamageContext as DC and line 35 asserts `DC is DamageContext`. This only verifies the import works, which is already proven by the import at line 6. No game logic is exercised.
- **Estimated LOC saved:** 4

### A2.
- **File:** tests/unit/core/test_combat_types.py
- **Test(s):** `TestDamageContext.test_slots` (lines 29-31)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** MEDIUM
- **Evidence:** Line 31 asserts `hasattr(ctx, "__slots__")`. This checks an implementation detail of the dataclass (slots=True), not behavior. If slots were removed, the class would still function correctly. However, this could be considered an API contract if performance is critical.
- **Estimated LOC saved:** 4

### A3.
- **File:** tests/unit/core/test_config.py
- **Test(s):** `TestDisplayConfig.test_default_resolution_values`, `TestDisplayConfig.test_test_resolution_values`, `TestAIConfig.test_spacing_values`, `TestPhysicsConfig.test_tick_rate`, `TestBattleConfig.test_query_radius`, `TestBattleConfig.test_collision_values` (lines 13-80)
- **Reason:** TRIVIAL_CONSTANT
- **Confidence:** HIGH
- **Evidence:** Lines 15-16 assert `DisplayConfig.DEFAULT_WIDTH == 3840` and `DEFAULT_HEIGHT == 2160`. Lines 50-52 assert `AIConfig.MIN_SPACING == 150`, `DEFAULT_ORBIT_DISTANCE == 500`, `MAX_CORRECTION_FORCE == 500`. Line 61 asserts `PhysicsConfig.TICK_RATE == 0.01`. These tests verify static class attributes equal hardcoded literal values. If someone changes the constant, the test breaks for no reason other than the test needing a matching update. The companion file test_config_edge_cases.py already tests the *invariants* between these values (e.g., FLEE > ORBIT, throttle in 0..1).
- **Estimated LOC saved:** 68

### A4.
- **File:** tests/unit/core/test_constants.py
- **Test(s):** `TestPhysicsConstants.test_earth_mass_importable`, `TestPhysicsConstants.test_earth_mass_is_float` (lines 48-61)
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Line 51 asserts `EARTH_MASS is not None` and line 61 asserts `isinstance(EARTH_MASS, float)`. The companion test `test_earth_mass_value` (line 53-56) already verifies the value range, which subsumes both the not-None and is-float checks.
- **Estimated LOC saved:** 14

### A5.
- **File:** tests/unit/core/test_constants.py
- **Test(s):** `TestPlanetaryResources.test_planetary_resources_is_list`, `TestPlanetaryResources.test_planetary_resources_has_five_elements`, `TestPlanetaryResources.test_planetary_resources_elements_are_strings` (lines 17-42)
- **Reason:** DUPLICATE_OF:test_planetary_resources_has_expected_values
- **Confidence:** HIGH
- **Evidence:** `test_planetary_resources_has_expected_values` (line 23-29) asserts `ids == ["metals", "organics", "vapors", "radioactives", "exotics"]`. This exact-list comparison already proves the result is a list (line 28), has 5 elements, and all elements are strings. The three other tests add zero incremental coverage.
- **Estimated LOC saved:** 26

### A6.
- **File:** tests/unit/core/test_protocols.py
- **Test(s):** `TestProtocolExistence.test_import_all_protocols`, `TestProtocolExistence.test_import_all_typeguards` (lines 12-75)
- **Reason:** SCAFFOLD_ONLY
- **Confidence:** HIGH
- **Evidence:** Lines 16-46 import protocols and assert `is not None`. Lines 50-75 import TypeGuards and assert `callable()`. Every protocol and TypeGuard is already exercised with real game objects in the subsequent test classes (TestProtocolsWithRealClasses, TestTypeGuardFunctions, etc.), which necessarily prove the imports succeed.
- **Estimated LOC saved:** 30

### A7.
- **File:** tests/unit/core/test_protocols.py
- **Test(s):** `TestPROJ193ProtocolImports.test_import_new_protocols`, `TestPROJ193ProtocolImports.test_import_new_typeguards` (lines 493-520)
- **Reason:** SCAFFOLD_ONLY / DUPLICATE_OF:TestPROJ193ProtocolSatisfaction
- **Confidence:** HIGH
- **Evidence:** Lines 498-507 and 510-520 repeat the import-and-assert-not-None pattern. The `TestPROJ193ProtocolSatisfaction` class (lines 523-581) imports and uses all four protocols with real objects, which subsumes the import checks.
- **Estimated LOC saved:** 28

### A8.
- **File:** tests/unit/core/test_error_codes.py
- **Test(s):** `TestErrorCodeCategories` class (lines 84-120)
- **Reason:** DUPLICATE_OF:TestErrorCodeNamingConvention
- **Confidence:** MEDIUM
- **Evidence:** `TestErrorCodeCategories` checks that at least one code exists per category prefix (e.g., `len(v_codes) > 0`). But `TestErrorCodeNamingConvention` (lines 33-81) already iterates all codes and validates their prefix categorization. If any category were empty, the naming convention tests would also fail (no codes to iterate). The `TestErrorCodeMinimumSet` class (lines 148-178) provides more specific existence checks.
- **Estimated LOC saved:** 12

## B. Tests That Are Happy-Path-Only

### B1.
- **File:** tests/unit/core/test_formula_evaluator.py
- **Test(s):** `TestFormulaEvaluatorBasic`, `TestASTWalker`
- **What's tested:** Basic arithmetic, variable substitution, caret power, function calls, cache hits, security rejection
- **What's missing:** The 22 missing coverage lines include: non-numeric constant rejection (line 88), unsupported binary operator (line 110), unsupported unary operator (line 121), non-callable function name (line 146), comparison operators (lines 154-166), IfExp ternary expressions (lines 169-170), List/Tuple literal evaluation (lines 173-176), validate() with unknown function names, SyntaxError path from _parse_formula (line 295). The `safe_evaluate` only tests the fallback-to-default path, not the successful-evaluation path explicitly.
- **Source method(s) affected:** game/core/formula_evaluator.py:88-176, 295
- **Priority:** HIGH

### B2.
- **File:** tests/unit/core/patterns/test_layer_iterator.py
- **Test(s):** `TestIterComponents`, `TestIterLayersAndComponents`, `TestIterKeyedComponents`
- **What's tested:** List format, dict format with components key, string components, empty layers, missing layers key, mixed formats, invalid formats
- **What's missing:** Missing lines 89-93 and 154-157 in layer_iterator.py. Lines 89-93 appear to be an alternative code path in `iter_layers_and_components` for dict format with `components` not being a list (e.g., `components` key exists but value is a non-list type). Lines 154-157 appear to be the `iter_keyed_components` path for dict-format layers where `components` is not a list. No test provides `{"components": "not_a_list"}` dict-format layer data.
- **Source method(s) affected:** game/core/patterns/layer_iterator.py:89-93, 154-157
- **Priority:** MEDIUM

### B3.
- **File:** tests/unit/core/test_json_utils.py
- **Test(s):** `TestSaveJson`, `TestSaveJsonAtomicWrite`
- **What's tested:** Successful save, directory creation, overwrite, indent, Path objects, unicode, atomic write success, failure preservation
- **What's missing:** Missing lines 110-111 and 192-193 in json_utils.py. These likely correspond to the cleanup path when the temp file exists but rename fails (e.g., a partial write scenario on Windows where temp file cleanup is needed), and possibly the `else` branch of a conditional during atomic write. The tests mock IO errors but don't test the specific temp-file-cleanup-on-rename-failure path.
- **Source method(s) affected:** game/core/json_utils.py:110-111, 192-193
- **Priority:** LOW

### B4.
- **File:** tests/unit/core/math_utils/ (all files)
- **Test(s):** `TestVector2Creation`, `TestVector2Arithmetic`, `TestVector2Indexing`
- **What's tested:** Standard creation, arithmetic, indexing, normalization, rotation, angles, distances, clamp, lerp, angle_diff
- **What's missing:** Missing lines 38-40 in math.py correspond to the `Vector2.__init__` path where `y is None` and `x` is an iterable (tuple/list) -- tested indirectly via pygame interop but no explicit test for `Vector2((3, 4))` or `Vector2([3, 4])`. Line 55 is the `__radd__` path. Line 63 is the `__rsub__` path. Lines 245-248 are the `normalize_angle` function.
- **Source method(s) affected:** game/core/math.py:38-40, 55, 63, 245-248
- **Priority:** MEDIUM

### B5.
- **File:** tests/unit/engine/collision_edge_cases/test_beam_ramming.py
- **Test(s):** `TestBeamRaycastingEdgeCases`, `TestRammingEdgeCases`
- **What's tested:** Zero direction, target at origin, dead target, no target, zero hit chance, tangent hit, target behind origin, geometry, ramming edge cases
- **What's missing:** Missing lines 117, 139-140, 181-183 in collision.py. Line 117 is the `fleet_atk` bonus addition path (needs source_ship with `fleet_attack_bonus` attribute). Lines 139-140 are the PDC/Projectile target path (`elif hasattr(target, 'take_damage')`). Lines 181-183 are the ramming path where `hp_target < hp_rammer` (rammer has more HP than target).
- **Source method(s) affected:** game/engine/collision.py:117, 139-140, 181-183
- **Priority:** MEDIUM

## C. Source Code with Inadequate Coverage

### C1.
- **Source file:** game/core/formula_evaluator.py (152 stmts)
- **Coverage:** 85.5% -- 22 missing lines
- **Untested areas:**
  - Non-numeric constant rejection (line 88): `ast.Constant` with string/bool value
  - Unsupported binary operator (line 110): e.g., `@` matrix multiply operator
  - Unsupported unary operator (line 121): e.g., `~` bitwise not
  - Method call rejection (line 140): e.g., `obj.method()`
  - Dangerous function in Call node (lines 146): e.g., `exec(...)` when exec is in names
  - Non-callable name in Call context (lines 154-158): variable used as function
  - Comparison operators (lines 162-166): `<`, `>`, `==`, `!=` in formulas
  - IfExp ternary (lines 169-170): `x if condition else y`
  - List/Tuple literals (lines 173-176): `[1, 2, 3]` in formulas
  - SyntaxError wrapping (line 295): malformed formula that passes security but fails parsing
- **Risk:** Formula evaluator is a security-critical component (evaluates user-facing formulas from data files). Untested AST node types could be exploited or cause unexpected crashes. The comparison and ternary operators are likely used in production modifier formulas.
- **Priority:** HIGH

### C2.
- **Source file:** game/core/patterns/layer_iterator.py (46 stmts)
- **Coverage:** 80.4% -- 9 missing lines
- **Untested areas:**
  - `iter_layers_and_components` dict format with non-list components key (lines 89-93)
  - `iter_keyed_components` dict format with non-list components key (lines 154-157)
  - These are defensive code paths for malformed layer data where `components` key exists but is not a list
- **Risk:** Malformed ship design data from saves or mods could trigger these paths. Without tests, we don't know if they silently skip (correct) or raise (incorrect).
- **Priority:** MEDIUM

### C3.
- **Source file:** game/core/math.py (108 stmts)
- **Coverage:** 91.7% -- 9 missing lines
- **Untested areas:**
  - `Vector2.__init__` iterable path (lines 38-40): constructing from tuple/list `Vector2((1, 2))`
  - `__radd__` (line 55): `other_vec_type + Vector2(1, 2)` where other has x,y
  - `__rsub__` (line 63): `other_vec_type - Vector2(1, 2)` where other has x,y
  - `normalize_angle` (lines 245-248): wrapping angles to (-180, 180]
- **Risk:** The iterable constructor path is used for pygame Vector2 interop. If broken, ship positions from pygame could fail to convert. `normalize_angle` is used in rotation calculations; untested means angle wrapping bugs could go undetected.
- **Priority:** MEDIUM

## D. Cross-Domain Observations

1. **Duplicate ResourceCatalog test coverage:** The ResourceCatalog is tested in three separate locations: `test_resource_catalog.py`, `test_resources.py`, and `resources_registry/test_loading.py`. Many tests overlap significantly (e.g., "file not found returns empty", "duplicate IDs last wins", "resource without id skipped"). These three files total ~580 lines and could likely be consolidated into one file of ~350 lines without losing coverage. This crosses no domain boundary but is worth noting for maintainability.

2. **Profiling tests duplicated:** `test_profiling_edge_cases.py` and the `profiling/` subdirectory (test_decorators.py, test_persistence.py, test_recording.py, test_singleton_threading.py) have substantial overlap. The edge_cases file re-tests `profile_action` decorator behavior, `profile_block` context manager, save_history error paths, toggle/clear, and nested blocks -- all of which are also covered in the subdirectory files. Estimated ~100 lines of overlap.

3. **Simulation-layer tests in core directory:** `test_pure_loaders.py`, `test_registry_manager_reload.py`, and `test_service_injection.py` import and test simulation-layer code (`game.simulation.components.component`, `game.simulation.services.*`, `game.simulation.entities.ship_loader`). These are cross-layer integration tests masquerading as core unit tests. They should either be moved to `tests/unit/simulation/` or explicitly marked as integration tests.

4. **Formula evaluator security gap affects simulation domain:** The formula evaluator's untested comparison operators, ternary expressions, and list/tuple literals are likely used in production modifier formulas (referenced in CLAUDE.md memory: "1.0 + 0.514 * ln(1.0 + param / 30.0)"). If more complex formulas using conditionals are added to modifiers.json, they would exercise untested code paths.

5. **Collision system missing lines affect battle simulation fidelity:** The untested `fleet_attack_bonus` / `fleet_defense_bonus` paths in collision.py (lines 117, 121-122) and the PDC-targets-projectile path (lines 139-140) are used in fleet combat scenarios. The simulation domain's battle tests should verify these paths with real fleet aura bonuses applied.
