# Verified Findings — Shard 15

## Verification Summary
- **Total claims verified**: 10 (6 Phase 1 + 4 cross-shard)
- **CONFIRMED**: 9 | **DISPUTED**: 1 | **INCONCLUSIVE**: 0
- **Severity changes**: 1 (HLP-005 downgraded claim accuracy)

---

## Phase 1 Claims

### F-1: CAT-1 test_resource_grid_items_list_exists — **CONFIRMED** (CRITICAL)

- **File**: `tests/unit/ui/panels/test_planet_report_panel.py:88-97`
- **Claim**: Test assigns `panel._resource_grid_items = []` then asserts `isinstance(panel._resource_grid_items, list)` — self-fulfilling assertion.
- **Evidence**: Lines 93-97:
  ```python
  panel = PlanetReportPanel.__new__(PlanetReportPanel)
  panel._resource_grid_items = []
  assert isinstance(panel._resource_grid_items, list)
  ```
  The assertion is a direct consequence of the preceding assignment. It cannot fail unless the Python runtime is fundamentally broken (e.g. `isinstance` monkey-patched).
- **Severity**: CRITICAL — UPHOLD. This is a textbook trivial-pass test. Provides zero behavioral coverage.
- **Recommendation**: Verified. Either remove the test or rewrite to verify `_build_resource_grid` populates the list from real input.

---

### F-2: CAT-1 test_update_does_not_raise — **CONFIRMED** (CRITICAL)

- **File**: `tests/unit/ui/screens/test_keybindings_scene.py:272-275`
- **Claim**: No assertions beyond "does not raise".
- **Evidence**: Lines 272-275:
  ```python
  def test_update_does_not_raise(self, scene):
      """update() should not raise."""
      scene.update(0.016)
  ```
  Zero assertions. The `scene` fixture (line 44-47) creates a real `KeybindingsScene` which wraps `pygame_gui.UIManager` — `update()` could theoretically fail but the test provides no behavioral verification. A true "no-op validator" test.
- **Severity**: CRITICAL — UPHOLD.
- **Recommendation**: Verified. Add at minimum an assertion on `scene._elapsed_time` or `scene._ui_manager.get_time_since_last_update()`, or remove.

---

### F-3: CAT-1 test_draw_does_not_raise — **CONFIRMED** (CRITICAL)

- **File**: `tests/unit/ui/screens/test_keybindings_scene.py:276-279`
- **Claim**: No assertions beyond "does not raise".
- **Evidence**: Lines 276-279:
  ```python
  def test_draw_does_not_raise(self, scene):
      """draw() should not raise on a valid surface."""
      surface = pygame.Surface((1280, 800))
      scene.draw(surface)
  ```
  Zero assertions. Same pattern as F-2.
- **Severity**: CRITICAL — UPHOLD.
- **Recommendation**: Verified. Add assertion on surface contents (e.g. pixel inspection) or remove.

---

### F-4: CAT-10 TestGetShipClassColor — 4 parametrize-able tests — **CONFIRMED** (MINOR)

- **File**: `tests/unit/ui/utils/test_portraits.py:18-28`
- **Claim**: 4 test methods with identical body, different data.
- **Evidence**:
  - L18-19: `test_known_class_fighter` → `assert get_ship_class_color("Fighter") == SHIP_CLASS_FIGHTER`
  - L21-22: `test_known_class_cruiser` → `assert get_ship_class_color("Cruiser") == SHIP_CLASS_CRUISER`
  - L24-25: `test_unknown_class_returns_default` → `assert get_ship_class_color("Dreadnought") == SHIP_CLASS_DEFAULT`
  - L27-28: `test_none_returns_default` → `assert get_ship_class_color(None) == SHIP_CLASS_DEFAULT`
  All are single-line asserts with `call(x)` → `== y`. Identical logic, differing only in inputs/outputs.
- **Severity**: MINOR — UPHOLD.
- **Recommendation**: Verified. Merge into `@pytest.mark.parametrize`.

---

### F-5: CAT-10 TestHpColor — 6 parametrize-able tests — **CONFIRMED** (MINOR)

- **File**: `tests/unit/ui/screens/test_battle_results_screen.py:21-43`
- **Claim**: 6 test methods with identical body, different HP input and expected color output.
- **Evidence**:
  - L21-23: `test_zero_hp_returns_destroyed` → `_hp_color(0) == HP_DESTROYED`
  - L25-27: `test_negative_hp_returns_destroyed` → `_hp_color(-5) == HP_DESTROYED`
  - L29-31: `test_low_hp_returns_critical` → `_hp_color(10) == HP_CRITICAL`
  - L33-35: `test_medium_hp_returns_damaged` → `_hp_color(30) == HP_DAMAGED`
  - L37-39: `test_high_hp_returns_healthy` → `_hp_color(80) == HP_HEALTHY`
  - L41-43: `test_full_hp_returns_healthy` → `_hp_color(100) == HP_HEALTHY`
  All are single-assert calls. Identical shape.
- **Severity**: MINOR — UPHOLD.
- **Recommendation**: Verified. Merge into `@pytest.mark.parametrize`.

---

### F-6: CAT-10 TestCategoryIcons — 4 parametrize-able tests — **CONFIRMED** (MINOR)

- **File**: `tests/unit/ui/screens/test_event_log_data_source.py:100-118`
- **Claim**: 4 test methods with identical body for different categories.
- **Evidence**:
  - L100-103: `test_combat_icon` → `assert "combat" in CATEGORY_ICONS` + `assert "[Combat]" in CATEGORY_ICONS["combat"]`
  - L105-108: `test_production_icon` → `assert "production" in CATEGORY_ICONS` + `assert "[Prod]" in CATEGORY_ICONS["production"]`
  - L110-113: `test_colonies_icon` → `assert "colonies" in CATEGORY_ICONS` + `assert "[Colony]" in CATEGORY_ICONS["colonies"]`
  - L115-118: `test_fleet_operations_icon` → `assert "fleet_operations" in CATEGORY_ICONS` + `assert "[FleetOps]" in CATEGORY_ICONS["fleet_operations"]`
  All are 2-assert blocks with identical structure.
- **Severity**: MINOR — UPHOLD.
- **Recommendation**: Verified. Merge into `@pytest.mark.parametrize`.

---

## Cross-Shard Claims

### C-1: HLP-001 MockGameSession in test_auto_save.py — **CONFIRMED**

- **File**: `tests/unit/strategy/test_auto_save.py:14-41`
- **Claim**: Identical `MockGameSession` to 4 other locations, including the canonical at `tests/unit/strategy/save_game_service/conftest.py:12-39`.
- **Evidence**: 
  - **test_auto_save.py:14-41**: `MockGameSession.__init__(self, turn_number=1, save_path=None, num_empires=2)`. Always creates `GameConfig()`. `to_dict()` returns turn_number, save_path, config, galaxy, empires, human_player_ids.
  - **Canonical conftest.py:12-39**: `MockGameSession.__init__(self, config=None, turn_number=1, num_empires=2)`. Accepts config param (defaults to `GameConfig()`). `save_path = None` always. `to_dict()` identical structure.
  - Minor signature differences (test_auto_save has `save_path` param, canonical has `config` param) but the class serves the same purpose with the same `to_dict()` contract. The canonical is slightly more flexible.
- **Recommendation**: Confirmed. Delete from test_auto_save.py, import from save_game_service/conftest.py. If `save_path` init is needed, pass it post-construction or extend the canonical.

---

### C-2: HLP-002 MockPlanetType in test_fleet_order_processor.py — **CONFIRMED**

- **File**: `tests/unit/strategy/test_fleet_order_processor.py` at lines 157, 282, 484
- **Claim**: `MockPlanetType(Enum)` duplicated inline 3 times in 3 classes within the same file.
- **Evidence**:
  - L157-159 — `TestColonizeProcessing.mock_planet_continental`: `MockPlanetType.CONTINENTAL = "CONTINENTAL"`
  - L282-283 — `TestEndTurnOrderProcessing.test_execute_action_order_colonize`: `MockPlanetType.CONTINENTAL = "CONTINENTAL"` (inline in test method, not even a fixture)
  - L484-485 — `TestExecuteActionOrderColonize.mock_planet_ice_dwarf`: `MockPlanetType.ICE_DWARF = "ICE_DWARF"`
  3 separate local Enum definitions with overlapping values. Two define CONTINENTAL, one defines ICE_DWARF.
- **Recommendation**: Confirmed. Define a single `MockPlanetType` at module level (or in a shared fixture) with both CONTINENTAL and ICE_DWARF values. Reuse across all 3 classes.

---

### C-3: HLP-003 make_mock_ship_instance duplicates — **CONFIRMED**

- **Files**: 
  - `tests/integration/ui/test_fleet_build_button.py:12-40`
  - `tests/repro_issues/test_bug_27_ordertype.py:12-30`
- **Claim**: Both define `make_mock_ship_instance` locally despite canonical at `tests/conftest.py:350`.
- **Evidence**:
  - **Canonical** (conftest.py:350-384): `make_mock_ship_instance(name="Test Ship", owner_id=0, registries=None)`. Creates ShipInstance with `instance_id = f"test-{name.lower().replace(' ', '-')}-{id(name)}"`. Sets `ship._registries = registries`.
  - **test_fleet_build_button.py:12-40**: Adds `has_yard=False` parameter and uses `ship.set_registries(registries)` (public API) instead of direct `_registries` assignment. Extends canonical but duplicates core logic.
  - **test_bug_27_ordertype.py:12-30**: Nearly byte-for-byte identical to canonical. Same signature `name, owner_id, registries`. Only difference: `instance_id = f"test-{name.lower().replace(' ', '-')}"` (no `-{id(name)}` suffix). Uses `ship._registries = registries` (same as canonical).
- **Recommendation**: Confirmed. Remove local copies; import from root conftest. For test_fleet_build_button's `has_yard` extension, extend the canonical helper with a `**kwargs` or optional parameter, or handle the `has_yard` setup post-factory. test_bug_27_ordertype.py can use canonical directly.

---

### C-4: HLP-005 setup_tmpdir in test_auto_save.py — **DISPUTED** (claim accuracy)

- **File**: `tests/unit/strategy/test_auto_save.py:47-55`
- **Claim**: "Identical 10-line pattern" of `tempfile.mkdtemp()`, patch `Paths.SAVES_DIR`, yield, `shutil.rmtree()` matching 3 other files.
- **Evidence**:
  - **test_auto_save.py:47-55**:
    ```python
    @pytest.fixture(autouse=True)
    def setup_tmpdir(self):
        tmpdir = tempfile.mkdtemp()
        original_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(original_cwd)
        shutil.rmtree(tmpdir)
    ```
  - **Canonical** save_game_service/conftest.py:42-50:
    ```python
    @pytest.fixture
    def setup_tmpdir():
        tmpdir = tempfile.mkdtemp()
        saves_dir = os.path.join(tmpdir, "saves")
        os.makedirs(saves_dir, exist_ok=True)
        with patch.object(paths_module.Paths, 'SAVES_DIR', saves_dir):
            yield tmpdir
        shutil.rmtree(tmpdir)
    ```
  - **Key difference**: test_auto_save uses `os.chdir()` to redirect the working directory. It does NOT patch `Paths.SAVES_DIR`. The canonical patches `Paths.SAVES_DIR` and creates a `saves/` subdirectory. These are different mechanisms for achieving similar goals (redirecting save paths).
  - **Structural similarity**: Both share the core lifecycle — `mkdtemp()` → setup → yield → `rmtree()`. The claim's description of "patch Paths.SAVES_DIR" is inaccurate for test_auto_save.py specifically.
- **Severity adjustment**: Claim of "identical" is overstated. The pattern is structurally similar but implements different redirection strategies. The consolidation recommendation remains valid (these could share a common tempdir fixture), but the implementation details differ enough that direct consolidation would require choosing one strategy.
- **Recommendation**: Disputed on accuracy grounds. Consolidation is still reasonable but would require reconciling `os.chdir()` vs `patch(Paths.SAVES_DIR)` approaches. A unified fixture supporting both patterns via an optional parameter is feasible.

---

## Verification Methodology

For each claim:
1. Read cited source lines + 10 lines above/below for context
2. Cross-referenced canonical sources where applicable (conftest.py, save_game_service/conftest.py)
3. Validated severity against CAT definitions (CAT-1 = trivial/non-failing test; CAT-10 = parametrize candidate)
4. For cross-shard claims: compared byte-level implementation against the claimed "identical" / "near-identical" characterization

No claims required downgrade from CRITICAL to lower severity — all three CAT-1 claims are textbook trivial-pass tests. No claims were found to be INCONCLUSIVE due to insufficient evidence.
