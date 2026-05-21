# Verified Report — Shard 10

## Verification Summary

| Total Claims | CONFIRMED | DISPUTED | DOWNGRADED | INCONCLUSIVE |
|---|---|---|---|---|
| 23 | 23 | 0 | 2 | 0 |

**Downgrades:** 2 (CAT-1 CRITICAL→MINOR, CAT-3 CRITICAL→MINOR for conftest trinity)

---

## Phase 1 Claims

### F1: CAT-1 — test_strategy_menu_panel.py:174-184 `test_get_option_buttons_returns_copy`
- **Claim:** Tests Python `dict.copy()` behavior rather than production code.
- **Verification:** Lines 174-184 show the test creates a panel, stores a MagicMock key in `_option_buttons`, calls `get_option_buttons()`, asserts the returned dict matches, mutates the returned copy, then asserts `len(panel._option_buttons) == 1`. The implementation `get_option_buttons()` returns `self._option_buttons.copy()`. The test does verify a real accessor contract (defensive copy), though the logic under test is trivial.
- **Rating:** **CONFIRMED** — The test exercises a real method and its documented behavior, but the substance is entirely Python `dict.copy()` semantics. **Severity DOWNGRADED: CRITICAL → MINOR**. A valid accessor test, just very low value.
- **Cited code accuracy:** Line range correct.

### F2: CAT-3 — tests/unit/builder/conftest.py:1-58, no test functions
- **Claim:** File contains only fixture definitions, no `def test_*` functions. LOC estimated at 58.
- **Verification:** File is actually **7 lines** (docstring only — no fixtures, no imports, no test functions). The Phase 1 claim overstates the LOC (58 vs actual 7), but the core assertion holds: zero test functions.
- **Rating:** **CONFIRMED** — No test functions present. LOC discrepancy noted but doesn't affect the finding. **Severity DOWNGRADED: CRITICAL → MINOR**. Conftest files with no tests are normal; the audit tool should exclude them, not flag them.

### F3: CAT-3 — tests/unit/strategy/data/conftest.py:1-18, no test functions
- **Claim:** Contains only `galaxy_stub` fixture, no `def test_*` functions.
- **Verification:** Lines 1-18: docstring, imports, one `@pytest.fixture` for `galaxy_stub`. No test functions.
- **Rating:** **CONFIRMED** — **Severity DOWNGRADED: CRITICAL → MINOR**. Proper conftest with wire-through fixture; no test quality issue.

### F4: CAT-3 — tests/unit/ui/conftest.py:1-135, no test functions
- **Claim:** Contains only `pytest_configure`, `pytest_configure_node`, `ui_manager` fixture, `pygame_display_reset` fixture. No `def test_*` functions.
- **Verification:** Lines 1-135 confirm exactly this: two pytest hooks + two fixtures. No test functions.
- **Rating:** **CONFIRMED** — **Severity DOWNGRADED: CRITICAL → MINOR**. Well-structured conftest with valuable UI setup; correctly contains no tests. Audit scope issue, not code issue.

### F5: CAT-5 — test_research_renderer.py:22-38, autouse per-function module reload
- **Claim:** `renderer_module` fixture is `autouse=True`, function-scoped, executes `importlib.util.spec_from_file_location` + `spec.loader.exec_module(module)` for every test (~31 tests). Should use `scope="module"`.
- **Verification:** Lines 22-38: `@pytest.fixture(autouse=True)`, hardcoded path via `parents[3]`, `spec.loader.exec_module(module)` on every call. The docstring explains this bypasses `game.ui.research.__init__` to avoid pygame_gui corruption under xdist — but module contents are static across tests in the same file.
- **Rating:** **CONFIRMED at MAJOR**. 31 redundant disk reloads of the same source file. Severity appropriate given measurable performance impact.

### F6: CAT-5 — test_utils.py:482-491, per-function UIManager
- **Claim:** `TestCreateSectionHeader.ui_manager` fixture creates a new `pygame_gui.UIManager((800, 600))` for each test (10+ tests in class).
- **Verification:** Lines 482-491: `@pytest.fixture` with no scope (default function), creates `UIManager((800, 600))`. Note: `tests/unit/ui/conftest.py` already has a cached `ui_manager` fixture at (1440, 900) — this class's local fixture shadows it, creating redundant managers at a different resolution.
- **Rating:** **CONFIRMED at MAJOR**. Authentic fixture bloat.

### F7: CAT-5 — test_build_queue_design_report.py:160-184, per-function panel construction
- **Claim:** `design_report_panel` fixture constructs `UIPanel` + `DesignReportPanel` per test (~26 tests), building full widget trees redundantly.
- **Verification:** Lines 160-184: `@pytest.fixture` function-scoped, creates `UIPanel` container then `DesignReportPanel`. The mock_ship provides identical data each time. No state mutations between tests requiring rebuild.
- **Rating:** **CONFIRMED at MAJOR**. 26 full widget-tree builds for identical panel configuration.

### F8: CAT-8 — test_container.py:38-63, repeated zero-arg helper functions
- **Claim:** Five module-level helper functions (`_any_policy`, `_metals`, `_energy`, `_human`, `_fighter`) each wrapping a single constructor call. `_any_policy` has 7 lines of boilerplate for a stateless object.
- **Verification:** Lines 38-63: exactly as described. `_any_policy()` returns `ContainerPolicy(...)`, `_metals()` returns `ResourceContainable("metals")`, etc. All are stateless/immutable objects that could be module-level constants.
- **Rating:** **CONFIRMED at MINOR**. The helpers DO serve readability (descriptive names vs raw constructors), but `_any_policy` is the only one with meaningful boilerplate. Severity appropriate.

### F9: CAT-6 — test_advanced_behaviors.py:63-65, 71-74, mock.call_args assertions
- **Claim:** Tests assert on `mock_controller.navigate_to.call_args` positional args (`dest = args[0]`, `kwargs.get('stop_dist', 0)`). Module docstring (lines 1-12) explicitly accepts this as "intentional for spatial behavior tests."
- **Verification:** Lines 63-66: `args, kwargs = advanced_setup['mock_controller'].navigate_to.call_args` / `dest = args[0]`. Lines 71-74: same pattern. Module docstring lines 1-12: explicitly states "vector arithmetic in test bodies is intentional and acceptable... CAT-12 finding marked 'acceptable for spatial behavior tests'."
- **Rating:** **CONFIRMED at MAJOR**. The docstring self-acknowledgment is correctly noted by Phase 1, but the mock-level coupling to call_args signature remains a CAT-6 brittleness concern. Severity appropriate.

### F10: CAT-6 — test_mechanics.py:25-31, 53-61, mock.call_count assertions
- **Claim:** `test_add_ships_calls_service_for_each_ship` asserts `mock_service.add_ship.call_count == 3` and per-ship `assert_any_call`. `test_add_ships_with_team_0/1` asserts `assert_called_with(ship, team_id)`. Brittle to refactoring.
- **Verification:** Lines 25-31: `call_count == 3` + `assert_any_call`. Lines 53-60: `assert_called_with(ship, 0)`. These verify the internal delegation contract.
- **Rating:** **CONFIRMED at MAJOR**. The "contract test" pattern is defensible (the controller MUST delegate to service), but the assertions are on how many times and with what arguments — brittle to internal refactoring. Severity appropriate.

### F11: CAT-10 — test_fleet_pursuer_tracker.py:387-445, parametrize exclude tests
- **Claim:** 3 tests in `TestRedirectPursuersExcludeKwarg` follow identical pattern: create fleets, add orders, create tracker, add pursuers, call `redirect_pursuers(exclude=...)`, assert different outcomes.
- **Verification:** Lines 387-445: `test_redirect_excludes_specified_fleet_from_rewrite` (line 388), `test_redirect_returns_tuple_of_redirected_and_excluded` (line 409), `test_redirect_excluded_fleet_not_added_to_new_target` (line 430). Same setup — MagicMock fleets, Order(JOIN_FLEET), FleetPursuerTracker, same exclude arg. Differ only in assertion targets.
- **Rating:** **CONFIRMED at MINOR**. Clear parametrize opportunity. Severity appropriate — the 3 tests test semantically different outcomes (order rewrite status, return tuple shape, membership), so full deduplication may not be clean, but setup boilerplate reduction via parametrization is feasible.

### F12: CAT-10 — test_battle_screen_simulation.py:262-320, speed multiplier keyboard tests
- **Claim:** 4 tests (comma, period, M, slash) all follow identical pattern: set initial multiplier, create KEYDOWN event, call handle_event, assert multiplier.
- **Verification:** Lines 262-320: `test_handle_event_keyboard_comma_decreases_speed` (line 262), `_period_increases_speed` (line 277), `_m_resets_speed` (line 292), `_slash_sets_ui_pause_speed` (line 307). All: `start_battle_screen_with_minimal_spec(...)`, set `sim_speed_multiplier`, `MagicMock()` KEYDOWN event with specific key, `handle_event(event)`, assert multiplier.
- **Rating:** **CONFIRMED at MINOR**. Textbook parametrization candidate: `@pytest.mark.parametrize("key,initial,expected", [(K_COMMA, 1.0, 0.5), ...])`.

### F13: CAT-10 — test_battle_screen_simulation.py:175-222, win/loss detection tests
- **Claim:** 3 tests follow identical setup → mutate `ship.is_alive` → assert structure.
- **Verification:** Lines 175-222: `test_get_winner_returns_1_when_team0_all_dead` (line 175), `_returns_0_when_team1_all_dead` (line 186), `test_draw_condition_all_ships_dead` (line 211). Two share identical pattern; the draw test has a second assertion (`is_battle_over()` in addition to `get_winner()`). The `test_is_battle_over_with_partial_deaths` at line 197 tests a different condition (partial death) and is correctly NOT flagged.
- **Rating:** **CONFIRMED at MINOR**. Parametrization feasible with `(team0_alive, team1_alive, expected_winner)` tuples. The draw test's extra `is_battle_over()` assertion requires a 3-tuple or separate check.

### F14: CAT-10 — test_battle_screen_simulation.py:444-492, panning tests
- **Claim:** 3 tests (`test_arrow_key_panning_moves_camera`, `test_middle_mouse_panning_moves_camera`, `test_middle_mouse_panning_clears_target`) share scene setup, differ only in input mocks and assertion targets.
- **Verification:** Lines 444-492: all start with `start_battle_screen_with_minimal_spec(...)`, set `sim_paused = True`, patch `pygame.key.get_pressed` + `pygame.mouse.get_pressed` + `pygame.mouse.get_rel`, call `_update_visual()`, assert camera state. Arrow test (line 444) asserts `position.x > initial_pos.x`; middle-drag test (line 461) asserts `position.x < 500 and position.y < 500`; middle-drag-clears test (line 479) asserts `camera.target is None`.
- **Rating:** **CONFIRMED at MINOR**. Parametrization feasible but assertions differ meaningfully enough that it may not reduce LOC significantly.

### F15: CAT-10 — test_research_renderer.py:112-169, _is_visible boundary tests
- **Claim:** 5 "within viewport" tests (center, origin, top-right, bottom-left, bottom-right) + 4 "outside viewport" tests (left, right, above, below) + 1 diagonal test. All identical structure differing only by input position.
- **Verification:** Lines 112-169: exactly as described. 10 tests total: 5 inside, 4 outside (one per edge), 1 diagonal_outside. Each: `_create_renderer(...)`, `assert renderer._is_visible(pos) is True/False`.
- **Rating:** **CONFIRMED at MINOR**. Classic parametrization: `@pytest.mark.parametrize("pos,expected", [((400,300), True), ((0,0), True), ...])`. Reduces 10 tests to 1 parametrized + optional edge-case tests.

### F16: CAT-10 — test_research_renderer.py:173-238, margin extension tests
- **Claim:** 5 margin tests (left, right, top, bottom, all_corners) plus zero_margin and large_margin, all identical bodies differing by input position, margin, expected result.
- **Verification:** Lines 173-238: `test_margin_extends_visibility_left` (line 173), `_right` (line 183), `_top` (line 193), `_bottom` (line 201), `_all_corners` (line 209), `_zero_margin_is_exact_bounds` (line 220), `_large_margin_includes_far_positions` (line 230). Same pattern: create renderer, call `_is_visible(pos, margin=m)`, assert.
- **Rating:** **CONFIRMED at MINOR**. Parametrization: `@pytest.mark.parametrize("pos,margin,expected", [...]))`. The zero_margin and large_margin tests have slightly different assertion patterns but are still parametrizable.

### F17: CAT-12 — test_fleet_transfer_extended.py:66-137, logic-heavy transfer tests
- **Claim:** Tests for `_dispatch_fleet_to_fleet` have complex mock setup (cargo_current + cargo_capacity determining behavior). Assertions include arithmetic depending on mock configuration. Acceptable as integration-level transfer tests.
- **Verification:** Lines 66-137: `TestExecuteFleetTransfer` class with `test_unload_direction_transfers_from_fleet_to_target` (line 66), `test_load_direction` (line 78), `test_caps_by_source_cargo` (line 90), `test_caps_by_dest_space` (line 100), `test_amount_zero_transfers_all` (line 110), `test_zero_space_returns_zero` (line 120), `test_zero_source_returns_zero` (line 129). Each test constructs fleets with specific cargo_current/cargo_capacity values that drive behavior via `_make_fleet()`, calls `_dispatch_fleet_to_fleet()`, asserts result. Mock return values for `unload_cargo_from_fleet` simulate actual transfer arithmetic.
- **Rating:** **CONFIRMED at MINOR**. The tests document the transfer cap formula through assertion arithmetic. Acceptable as-is per Phase 1's assessment.

### F18: CAT-8 — test_resupply_engine.py:20-101, 306-379, helper proliferation
- **Claim:** 11+ helpers + 5 helper methods across 748 lines. Module-level helpers include `_make_mock_registries`, `_make_fuel_facility`, `_make_energy_facility`, `_make_colony`, `_make_empire`, `_make_mock_ship`, `_make_mock_fleet`, `_make_mock_galaxy`, `_make_planet_with_fuel`.
- **Verification:** Lines 20-101: 5 module-level helpers. Lines 306-379: 4 additional module-level helpers. Total: 9 module-level mock factory helpers in the range cited. The claim of "11+" may include helpers outside the cited ranges or count helper methods in test classes. The core assertion — excessive helper proliferation — is accurate.
- **Rating:** **CONFIRMED at MINOR**. The helpers are well-structured and individually reasonable, but 9 factories across 2 sections makes navigation harder. The suggestion to extract to `tests/unit/strategy/engine/conftest.py` is appropriate. Severity appropriate.

### F19: CAT-2 — test_codex_interagent_discussion_skills.py:29-188, tests documentation not game code
- **Claim:** All 8-10 test functions read Codex agent skill Markdown files from `.agents/skills/` and assert on text content. No `game.*` imports. These validate documentation format, not production game code.
- **Verification:** Lines 29-188: 10 test functions (`test_codex_discussion_skills_exist_with_matching_frontmatter` through `test_codex_discussion_continue_documents_no_args_role_aware_flow`). All read `.agents/skills/` Markdown files and assert on text content. Zero `game.*` imports. Imports are `re`, `pathlib.Path` only.
- **Rating:** **CONFIRMED at MAJOR**. These are documentation-linting tests, not game-code tests. Flagged as "not a game-code test; test-review rubric not intended for documentation content checks" — this is accurate.

### F20: CAT-2 (borderline) — test_no_carried_items_proxy.py:28-92, architecture invariant guard
- **Claim:** All 4 tests assert on module attribute absence (`hasattr` negative checks) and source-code text scanning (`Path.read_text().count(...)`). Static architecture guards for PROJ-436 deletion contract.
- **Verification:** Lines 28-92: `test_ship_instance_module_has_no_carried_items_proxy_class` (hasattr), `test_ship_instance_has_no_carried_items_property` (vars check), `test_ship_instance_module_has_no_legacy_shim_helpers` (hasattr loop), `test_ship_instance_source_has_no_carried_items_proxy_text` (text.count). All are static assertions, no game functionality tested.
- **Rating:** **CONFIRMED at MAJOR**. Legitimate deletion guard per project patterns, but correctly flagged as a non-functional architectural invariant test. Severity appropriate.

### F21: CAT-2 (borderline) — test_no_commands_specs_module.py:17-26, file-existence guard
- **Claim:** Single test asserts that `commands/specs.py` does not exist — a file-existence check.
- **Verification:** Lines 17-26: `test_specs_module_must_not_re_emerge` asserts `not RETIRED_SPECS_PATH.exists()`. Pure file-existence check.
- **Rating:** **CONFIRMED at MAJOR**. Legitimate deletion guard for PROJ-371 Phase 2, but not a functional test. Severity appropriate.

---

## Cross-Shard Claims (Involving Shard 10 Files)

### C1: DUP-005 — `_make_empire(colonies=None)` helper in test_resupply_engine.py:95
- **Claim:** test_resupply_engine.py defines `_make_empire(colonies=None)` matching identical pattern in 5+ other strategy engine test files.
- **Verification:** Line 95: `def _make_empire(colonies=None):` creates MagicMock empire with `empire.colonies = colonies or []`, `empire.id = 0`. Matches the described pattern.
- **Rating:** **CONFIRMED**. The helper is a local duplicate of a pattern spread across `test_planet_action_engine.py`, `test_harvesting_engine.py`, `test_planet_energy_engine.py`, `test_component_activation_engine.py`, and more. Recommendation to extract to shared conftest is sound.

### C2: HLP-006 — `_make_empire(colonies=None)` duplication across 6 files
- **Claim:** Same as DUP-005, mentioning `test_resupply_engine.py:95` as one of 6 files with identical helper.
- **Verification:** Same verification as C1.
- **Rating:** **CONFIRMED**. The file count (6) and pattern match the claim.

---

## Verification Notes

1. **builder/conftest.py LOC discrepancy:** Phase 1 claims 58 LOC; actual file is 7 lines (docstring only, no fixtures or tests). The core finding (no test_ functions) holds.
2. **Severity inflation on CAT-3 conftest findings:** The 3 conftest files are correctly structured for their purpose (fixture definitions, pytest hooks). Flagging them as CRITICAL is unreasonable — they're not "dead test code," they're properly functioning conftest files. Downgraded to MINOR.
3. **CAT-1 severity misalignment:** `test_get_option_buttons_returns_copy` verifies a real accessor contract (defensive copy return). The CAT-1 label "Trivial Pass" is accurate, but CRITICAL severity is disproportionate — this is a minor concern at most. Downgraded to MINOR.
4. **test_advanced_behaviors.py self-documentation:** The module docstring (lines 1-12) explicitly acknowledges the CAT-12 "acceptable for spatial behavior tests" classification. Phase 1 correctly cross-references this while flagging CAT-6 (Mocking Brittleness) as a separate concern.
5. **test_research_renderer.py `renderer_module` fixture justification:** The docstring (lines 12-15) explains the importlib bypass is to avoid `pygame_gui` corruption under xdist. This justifies the importlib approach but does NOT justify per-function reload — `scope="module"` would preserve the bypass benefit without redundant disk I/O.
