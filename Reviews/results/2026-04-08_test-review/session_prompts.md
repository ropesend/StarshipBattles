# Test Review Session Prompts

Copy-paste each session prompt into a separate Claude Code conversation.
Sessions 1-4 can run in parallel. Session 5 runs after 1-4 complete.

---

## SESSION 1: Core + Simulation + AI

```
# Test Suite Review — Session 1: Core + Simulation + AI

You are conducting a comprehensive test suite review for the Starship Battles project. Your job is to produce REPORTS ONLY — no code changes. You will coordinate 4 subagents, each reviewing a portion of the tests assigned to this session.

## Project Context
- Python 3.x game project, ~14,689 pytest tests across 1,044 files
- Source: ~123,258 LOC across 495 files in game/
- Coverage data is available at `coverage.json` in the project root (line-level coverage for every source file)
- This is a clean-sheet review — ignore any prior review results

## Your Domain
**Source ownership:** game/core/ (25 files, 96.5% coverage), game/simulation/ (83 files, 93.6% coverage), game/ai/ (10 files, 92.8% coverage), game/engine/ (4 files, 96.1%)

**Test territory (~276 files):**
- tests/unit/core/ — 48 files
- tests/unit/simulation/ — 107 files
- tests/unit/ai/ — 19 files
- tests/unit/entities/ — 13 files (possibly old/superseded by simulation/entities/)
- tests/unit/combat/ — 2 files (possibly old/superseded)
- tests/unit/systems/ — 15 files
- tests/unit/modifiers/ — 23 files
- tests/unit/abilities/ — 4 files
- tests/unit/data/ — 2 files
- tests/unit/engine/ — 4 files
- tests/unit/combat_lab/ — 16 files
- tests/unit/test_lab/ — 6 files
- tests/unit/fixtures/ — 5 files
- tests/integration/fleet_combat/ — 4 files
- tests/integration/simulation/ — 1 file
- tests/integration/ai_strategy/ — 3 files
- tests/regression/ — snapshot tests

## Known Low-Coverage Source Files
- game/simulation/components/component_loader.py (151 stmts, 64%)
- game/simulation/services/design_loader.py (46 stmts, 70%)
- game/simulation/battle_state.py (277 stmts, 75%)
- game/simulation/components/modifier_manager.py (129 stmts, 77%)
- game/simulation/combat/fleet_aura_manager.py (150 stmts, 79%)
- game/core/patterns/layer_iterator.py (46 stmts, 80%)
- game/ai/interfaces/controllable.py (205 stmts, 81%)
- game/core/formula_evaluator.py (152 stmts, 86%)

## Goals
For every test file in your domain:
1. **Find unnecessary tests:** duplicates, trivial constant assertions, scaffold-only tests, over-mocked tests that exercise no real code, tests for deleted code
2. **Find happy-path-only tests:** tests that never exercise error handling, edge cases, or boundary conditions
3. **Find coverage gaps:** source code with no tests or inadequate tests

## Subagent Plan
Launch 4 subagents in parallel. Each writes its report to the specified path.

**Agent 1 — Core Domain** → `Reviews/results/2026-04-08_test-review/session_1_core_sim_ai/agent_1_core.md`
- Source: game/core/ (25 files) + game/engine/ (4 files)
- Tests: tests/unit/core/ + tests/unit/data/ + tests/unit/engine/ + tests/unit/fixtures/
- Read coverage.json for game/core/ and game/engine/ files
- Focus: trivial constant tests, formula evaluator coverage (86%), layer_iterator coverage (80%), registry edge cases, protocol coverage

**Agent 2 — Simulation Components & Entities** → `Reviews/results/2026-04-08_test-review/session_1_core_sim_ai/agent_2_sim_components.md`
- Source: game/simulation/components/ + game/simulation/entities/ + game/simulation/interfaces/ + game/simulation/validation/
- Tests: tests/unit/simulation/components/ + tests/unit/simulation/entities/ + tests/unit/entities/ (old?) + tests/unit/modifiers/ + tests/unit/abilities/
- Read coverage.json for these source files
- Focus: check if tests/unit/entities/ duplicates tests/unit/simulation/entities/, modifier_manager coverage (77%), component_loader coverage (64%), ability aggregator coverage, component lifecycle edge cases

**Agent 3 — Simulation Combat/Systems/Services** → `Reviews/results/2026-04-08_test-review/session_1_core_sim_ai/agent_3_sim_combat.md`
- Source: game/simulation/combat/ + game/simulation/systems/ + game/simulation/services/ + game/simulation/managers/ + game/simulation/battle_controller.py + game/simulation/battle_state.py + game/simulation/projectile_manager.py
- Tests: tests/unit/simulation/combat/ + tests/unit/simulation/systems/ + tests/unit/simulation/services/ + tests/unit/simulation/battle_controller/ + tests/unit/simulation/ship_combat_engine/ + tests/unit/combat/ (old?) + tests/unit/systems/ + tests/unit/combat_lab/ + tests/unit/test_lab/ + tests/integration/fleet_combat/ + tests/integration/simulation/ + tests/regression/
- Read coverage.json for these source files
- Focus: battle_state.py coverage (75%), fleet_aura_manager coverage (79%), weapon_firing_system edge cases, damage calculator boundary conditions, check if tests/unit/combat/ and tests/unit/systems/ are old duplicates

**Agent 4 — AI** → `Reviews/results/2026-04-08_test-review/session_1_core_sim_ai/agent_4_ai.md`
- Source: game/ai/ (10 files)
- Tests: tests/unit/ai/ + tests/integration/ai_strategy/
- Read coverage.json for game/ai/ files
- Focus: controllable.py coverage (81%), combat_utils coverage (85%), behavior tree edge cases, target evaluator boundary conditions, AI controller test file is 1,152 lines — check if proportionate or over-testing

## Report Format
Each subagent MUST use this exact format:

```markdown
# Test Review Report: [Agent Name]
## Scope
- Source files reviewed: [list with line counts]
- Test files reviewed: [list with line counts]
- Coverage data referenced: [yes/no, summary stats]

## Summary
- Test files reviewed: N
- Source files reviewed: N
- Tests flagged for removal: N (estimated LOC: N)
- Tests flagged as happy-path-only: N
- Source files with inadequate coverage: N

## A. Tests Recommended for Removal
For each:
- **File:** path
- **Test(s):** class/method names
- **Reason:** DUPLICATE_OF:<path> | TRIVIAL_CONSTANT | DEAD_CODE | OVER_MOCKED | SCAFFOLD_ONLY | TESTS_NOTHING_REAL
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:** 1-3 sentence proof (cite specific line numbers)
- **Estimated LOC saved:** N

## B. Tests That Are Happy-Path-Only
For each:
- **File:** path
- **Test(s):** class/method names
- **What's tested:** description
- **What's missing:** specific error paths, edge cases, boundary values
- **Source method(s) affected:** path:line
- **Priority:** HIGH | MEDIUM | LOW (based on source criticality)

## C. Source Code with Inadequate Coverage
For each:
- **Source file:** path (LOC)
- **Coverage:** percentage from coverage.json + qualitative assessment
- **Untested areas:** specific methods, branches, error paths
- **Risk:** what could break without tests
- **Priority:** HIGH | MEDIUM | LOW

## D. Cross-Domain Observations
Anything that affects other sessions' domains.
```

## Criteria

### Remove:
- Tests asserting static constants equal specific values
- Tests that only verify an import succeeds (scaffold tests)
- Tests where every dependency is mocked and no real game code executes
- Exact or near-exact duplicates (keep the more complete one)
- Tests for code that no longer exists
- Old directory trees superseded by reorganized directories

### Flag as Happy-Path-Only (improve, don't remove):
- Tests that only test the success path of functions that can fail
- Tests that only use valid inputs for functions with validation
- Tests that never trigger error handling code
- Tests where mocks always return success values

### Keep (even if they look trivial):
- Regression guards for specific bug fixes
- Tests validating invariants between related values
- Tests documenting API contracts
- Integration tests exercising cross-layer behavior

## Instructions
1. Read coverage.json to extract coverage data for your domain's source files
2. Launch all 4 subagents in parallel
3. Each subagent should READ the source files and test files thoroughly — not just filenames
4. After all subagents complete, read their reports and write a brief summary to the console
5. Every test file in the domain must be reviewed by exactly one subagent — no gaps, no overlaps
```

---

## SESSION 2: Strategy Layer

```
# Test Suite Review — Session 2: Strategy Layer

You are conducting a comprehensive test suite review for the Starship Battles project. Your job is to produce REPORTS ONLY — no code changes. You will coordinate 5 subagents, each reviewing a portion of the tests assigned to this session.

## Project Context
- Python 3.x game project, ~14,689 pytest tests across 1,044 files
- Source: ~123,258 LOC across 495 files in game/
- Coverage data is available at `coverage.json` in the project root (line-level coverage for every source file)
- This is a clean-sheet review — ignore any prior review results

## Your Domain
**Source ownership:** game/strategy/ (137 files, 87.9% coverage — lowest of the major packages)

**Test territory (~308 files, ~5,200 tests):**
- tests/unit/strategy/ — 228 files (largest single test directory)
- tests/integration/strategy/ — 40 files
- tests/integration/colonization/ — 5 files
- tests/integration/resource_system/ — 3 files
- tests/integration/gameplay_loop/ — 3 files
- tests/integration/save_load/ — 22 files
- tests/unit/quickstart/ — 3 files
- tests/repro_issues/ — relevant strategy repro scripts

## Known Low-Coverage Source Files
- game/strategy/validation/planet_order_validator.py (80 stmts, 15%)
- game/strategy/engine/planet_command_handlers.py (78 stmts, 18%)
- game/strategy/data/homeworld_presets.py (43 stmts, 53%)
- game/strategy/systems/race_library.py (132 stmts, 58%)
- game/strategy/data/orbital_generation_config.py (103 stmts, 60%)
- game/strategy/data/build_queue_source.py (167 stmts, 65%)
- game/strategy/data/classification_config.py (76 stmts, 66%)
- game/strategy/services/design_validator.py (119 stmts, 67%)

## Goals
For every test file in your domain:
1. **Find unnecessary tests:** duplicates, trivial constant assertions, scaffold-only tests, over-mocked tests that exercise no real code, tests for deleted code
2. **Find happy-path-only tests:** tests that never exercise error handling, edge cases, or boundary conditions
3. **Find coverage gaps:** source code with no tests or inadequate tests

## Subagent Plan
Launch 5 subagents in parallel. Each writes its report to the specified path.

**Agent 1 — Strategy Data** → `Reviews/results/2026-04-08_test-review/session_2_strategy/agent_1_data.md`
- Source: game/strategy/data/ (46 files)
- Tests: tests/unit/strategy/data/ + tests/unit/strategy/ship_instance/ + tests/unit/strategy/ship_stats/ + tests/unit/strategy/empire/ + tests/unit/strategy/stars/ + tests/unit/strategy/planet_atmosphere/ and any other tests/unit/strategy/ subdirs that test data/ source files
- Read coverage.json for game/strategy/data/ files
- Focus: homeworld_presets (53%), orbital_generation_config (60%), build_queue_source (65%), classification_config (66%), entity serialization coverage, happy-path-only data validation

**Agent 2 — Strategy Engine** → `Reviews/results/2026-04-08_test-review/session_2_strategy/agent_2_engine.md`
- Source: game/strategy/engine/ (30 files)
- Tests: tests/unit/strategy/engine/ + any turn_engine/production_engine/fleet_movement subdirectories
- Read coverage.json for game/strategy/engine/ files
- Focus: planet_command_handlers (18% coverage!), command handler completeness (1,062 LOC source file), turn engine edge cases, event emission tests, production engine coverage

**Agent 3 — Strategy Services/Validation/Fleet** → `Reviews/results/2026-04-08_test-review/session_2_strategy/agent_3_services.md`
- Source: game/strategy/services/ + game/strategy/validation/ + game/strategy/interfaces/ + game/strategy/adapters/ + game/strategy/formulas/ + game/strategy/systems/
- Tests: tests/unit/strategy/services/ + tests/unit/strategy/validation/ + tests/unit/strategy/fleet/ + tests/unit/strategy/pathfinding/ + tests/unit/strategy/interfaces/ + tests/unit/strategy/adapters/ + tests/unit/strategy/formulas/ + related fleet navigation tests
- Read coverage.json for these source files
- Focus: planet_order_validator (15% coverage!), race_library (58%), design_validator (67%), fleet_navigation_service coverage, pathfinding coverage, colonize_validator test file is 1,247 lines — check if proportionate

**Agent 4 — Strategy Facade/Generation/Save** → `Reviews/results/2026-04-08_test-review/session_2_strategy/agent_4_facade_gen.md`
- Source: game/strategy/facade/ + game/strategy/generation/ + game/strategy/events/ + save-related code
- Tests: tests/unit/strategy/facade/ + tests/unit/strategy/generation/ + tests/unit/strategy/save_game_service/ + tests/unit/strategy/design_library/ + tests/unit/quickstart/ + tests/integration/save_load/
- Read coverage.json for these source files
- Focus: facade integration overlap, save/load roundtrip quality, generation edge cases, quickstart adequacy

**Agent 5 — Strategy Integration** → `Reviews/results/2026-04-08_test-review/session_2_strategy/agent_5_integration.md`
- Tests: tests/integration/strategy/ + tests/integration/colonization/ + tests/integration/resource_system/ + tests/integration/gameplay_loop/ + tests/repro_issues/ (strategy-related ones)
- For each integration test, also read the unit tests that cover the same source code
- Focus: unit-vs-integration overlap (are integration tests retesting what unit tests already cover?), repro scripts that should be deleted or promoted to proper tests, gameplay loop coverage, colonization integration quality

## Report Format
Each subagent MUST use this exact format:

```markdown
# Test Review Report: [Agent Name]
## Scope
- Source files reviewed: [list with line counts]
- Test files reviewed: [list with line counts]
- Coverage data referenced: [yes/no, summary stats]

## Summary
- Test files reviewed: N
- Source files reviewed: N
- Tests flagged for removal: N (estimated LOC: N)
- Tests flagged as happy-path-only: N
- Source files with inadequate coverage: N

## A. Tests Recommended for Removal
For each:
- **File:** path
- **Test(s):** class/method names
- **Reason:** DUPLICATE_OF:<path> | TRIVIAL_CONSTANT | DEAD_CODE | OVER_MOCKED | SCAFFOLD_ONLY | TESTS_NOTHING_REAL
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:** 1-3 sentence proof (cite specific line numbers)
- **Estimated LOC saved:** N

## B. Tests That Are Happy-Path-Only
For each:
- **File:** path
- **Test(s):** class/method names
- **What's tested:** description
- **What's missing:** specific error paths, edge cases, boundary values
- **Source method(s) affected:** path:line
- **Priority:** HIGH | MEDIUM | LOW (based on source criticality)

## C. Source Code with Inadequate Coverage
For each:
- **Source file:** path (LOC)
- **Coverage:** percentage from coverage.json + qualitative assessment
- **Untested areas:** specific methods, branches, error paths
- **Risk:** what could break without tests
- **Priority:** HIGH | MEDIUM | LOW

## D. Cross-Domain Observations
Anything that affects other sessions' domains.
```

## Criteria

### Remove:
- Tests asserting static constants equal specific values
- Tests that only verify an import succeeds (scaffold tests)
- Tests where every dependency is mocked and no real game code executes
- Exact or near-exact duplicates (keep the more complete one)
- Tests for code that no longer exists
- Old directory trees superseded by reorganized directories

### Flag as Happy-Path-Only (improve, don't remove):
- Tests that only test the success path of functions that can fail
- Tests that only use valid inputs for functions with validation
- Tests that never trigger error handling code
- Tests where mocks always return success values

### Keep (even if they look trivial):
- Regression guards for specific bug fixes
- Tests validating invariants between related values
- Tests documenting API contracts
- Integration tests exercising cross-layer behavior

## Instructions
1. Read coverage.json to extract coverage data for your domain's source files
2. Launch all 5 subagents in parallel
3. Each subagent should READ the source files and test files thoroughly — not just filenames
4. After all subagents complete, read their reports and write a brief summary to the console
5. Every test file in the domain must be reviewed by exactly one subagent — no gaps, no overlaps
```

---

## SESSION 3: UI Layer

```
# Test Suite Review — Session 3: UI Layer

You are conducting a comprehensive test suite review for the Starship Battles project. Your job is to produce REPORTS ONLY — no code changes. You will coordinate 5 subagents, each reviewing a portion of the tests assigned to this session.

## Project Context
- Python 3.x game project, ~14,689 pytest tests across 1,044 files
- Source: ~123,258 LOC across 495 files in game/
- Coverage data is available at `coverage.json` in the project root (line-level coverage for every source file)
- This is a clean-sheet review — ignore any prior review results

## Your Domain
**Source ownership:** game/ui/ (224 files, 57.6% coverage — the LOWEST of all packages, major gap area)

**Test territory (~219 files, ~4,100 tests):**
- tests/unit/ui/ — 175 files
- tests/integration/ui/ — 17 files
- tests/unit/builder/ — 24 files
- tests/unit/workshop/ — 3 files

## Known Low-Coverage Source Files (0% coverage)
- game/ui/screens/atmosphere_target_editor.py (131 stmts, 0%)
- game/ui/screens/battle_results_screen.py (167 stmts, 0%)
- game/ui/screens/planet_abilities_window.py (119 stmts, 0%)
- game/ui/screens/settings_window.py (45 stmts, 0%)

## Known Low-Coverage Source Files (<10% coverage)
- game/ui/screens/planet_list_sidebar.py (90 stmts, 3%)
- game/ui/screens/star_list_sidebar.py (77 stmts, 5%)
- game/ui/screens/test_lab/test_run_details.py (610 stmts, 5%)
- game/ui/screens/test_lab/test_run_card.py (237 stmts, 6%)

## Goals
For every test file in your domain:
1. **Find unnecessary tests:** duplicates, trivial constant assertions, scaffold-only tests, over-mocked tests that exercise no real code, tests for deleted code
2. **Find happy-path-only tests:** tests that never exercise error handling, edge cases, or boundary conditions
3. **Find coverage gaps:** source code with no tests or inadequate tests (UI has the most gaps)

## Subagent Plan
Launch 5 subagents in parallel. Each writes its report to the specified path.

**Agent 1 — UI Strategy Screens** → `Reviews/results/2026-04-08_test-review/session_3_ui/agent_1_strategy_screens.md`
- Source: Strategy-related screens in game/ui/screens/ — strategy_renderer.py, strategy_screen.py, strategy_window_manager.py, strategy_click_dispatcher.py, strategy_panel_manager.py, fleet-related screens, planet-related screens, star-related screens, empire-related screens, event_log screens
- Tests: All test_strategy_*.py + test_fleet_*.py + test_planet_*.py + test_star_*.py + test_empire_*.py + test_event_log_*.py + test_sub_window_hotkeys.py + test_system_selection_window.py + test_warp_hotkey.py + test_superweapon_*.py (UI-side) in tests/unit/ui/screens/
- Read coverage.json for these source files
- Focus: overlap among 20+ strategy screen test files, strategy_click_dispatcher coverage gap, strategy_panel_manager coverage gap, planet_list_sidebar (3%), star_list_sidebar (5%)

**Agent 2 — UI Battle + Setup + Misc Screens** → `Reviews/results/2026-04-08_test-review/session_3_ui/agent_2_battle_setup.md`
- Source: Battle screens, setup screens, formation editor, menu, galaxy_test screens, misc screens in game/ui/screens/
- Tests: test_battle_*.py (there are 6 battle test files — likely overlap) + test_menu_*.py + test_setup_*.py + test_race_*.py + test_new_game_*.py + test_formation_*.py + test_design_*.py + test_click_gate_*.py + test_cargo_quick_*.py + test_save_selection.py + test_camera_navigator.py + test_galaxy_test_screen.py + test_keybindings_scene.py in tests/unit/ui/screens/
- Read coverage.json for these source files
- Focus: 6 battle screen test files with potential overlap, atmosphere_target_editor (0%), battle_results_screen (0%), planet_abilities_window (0%), settings_window (0%), new_game_setup coverage gap, formation editor coverage

**Agent 3 — UI Panels + Components + Services** → `Reviews/results/2026-04-08_test-review/session_3_ui/agent_3_panels_services.md`
- Source: game/ui/panels/ + game/ui/components/ + game/ui/widgets/ + game/ui/services/ + game/ui/filters/ + game/ui/renderer/ + game/ui/effects/ + game/ui/assets/ + game/ui/utils/ + game/ui/interfaces/ + game/ui/orchestration/ + root-level game/ui/ files
- Tests: tests/unit/ui/panels/ + tests/unit/ui/components/ + tests/unit/ui/widgets/ + tests/unit/ui/services/ + tests/unit/ui/filters/ + tests/unit/ui/renderer/ + misc root-level tests/unit/ui/ tests (test_colors.py, test_fonts.py, test_sprites.py, test_config.py, test_overlay.py, test_slider_snap_logic.py, test_ui_imports.py, etc.)
- Read coverage.json for these source files
- Focus: panel test quality, service mock quality, trivial color/font/config tests, renderer coverage, dead mock files

**Agent 4 — UI Builder + Workshop** → `Reviews/results/2026-04-08_test-review/session_3_ui/agent_4_builder.md`
- Source: game/ui/screens/builder/ (36 files) + workshop-related code in game/ui/screens/
- Tests: tests/unit/ui/screens/builder/ + tests/unit/builder/ + tests/unit/workshop/ + tests/unit/ui/screens/test_workshop_*.py
- Read coverage.json for these source files
- Focus: there appear to be TWO builder test directories (tests/unit/ui/screens/builder/ and tests/unit/builder/) — check for duplication, weapons_renderer coverage gap, layer_panel coverage gap, workshop coverage

**Agent 5 — UI Integration + Test Lab** → `Reviews/results/2026-04-08_test-review/session_3_ui/agent_5_integration.md`
- Source: game/ui/screens/test_lab/ (16 files)
- Tests: tests/integration/ui/ + tests/unit/ui/test_lab_scene/ + tests/unit/ui/interfaces/ + tests/unit/ui/mocks/ + tests/unit/ui/battle_state_viewer/ + tests/unit/ui/schematic_view/ + tests/unit/ui/left_panel/
- Read coverage.json for these source files
- Focus: test_run_details.py (610 stmts, 5% coverage!), test_run_card.py (237 stmts, 6%), integration overlap with unit tests, dead mock files (check if tests/unit/ui/mocks/ files are actually imported by any test), test_lab_scene quality, build_queue integration tests

## Report Format
Each subagent MUST use this exact format:

```markdown
# Test Review Report: [Agent Name]
## Scope
- Source files reviewed: [list with line counts]
- Test files reviewed: [list with line counts]
- Coverage data referenced: [yes/no, summary stats]

## Summary
- Test files reviewed: N
- Source files reviewed: N
- Tests flagged for removal: N (estimated LOC: N)
- Tests flagged as happy-path-only: N
- Source files with inadequate coverage: N

## A. Tests Recommended for Removal
For each:
- **File:** path
- **Test(s):** class/method names
- **Reason:** DUPLICATE_OF:<path> | TRIVIAL_CONSTANT | DEAD_CODE | OVER_MOCKED | SCAFFOLD_ONLY | TESTS_NOTHING_REAL
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:** 1-3 sentence proof (cite specific line numbers)
- **Estimated LOC saved:** N

## B. Tests That Are Happy-Path-Only
For each:
- **File:** path
- **Test(s):** class/method names
- **What's tested:** description
- **What's missing:** specific error paths, edge cases, boundary values
- **Source method(s) affected:** path:line
- **Priority:** HIGH | MEDIUM | LOW (based on source criticality)

## C. Source Code with Inadequate Coverage
For each:
- **Source file:** path (LOC)
- **Coverage:** percentage from coverage.json + qualitative assessment
- **Untested areas:** specific methods, branches, error paths
- **Risk:** what could break without tests
- **Priority:** HIGH | MEDIUM | LOW

## D. Cross-Domain Observations
Anything that affects other sessions' domains.
```

## Criteria

### Remove:
- Tests asserting static constants equal specific values
- Tests that only verify an import succeeds (scaffold tests)
- Tests where every dependency is mocked and no real game code executes
- Exact or near-exact duplicates (keep the more complete one)
- Tests for code that no longer exists
- Old directory trees superseded by reorganized directories

### Flag as Happy-Path-Only (improve, don't remove):
- Tests that only test the success path of functions that can fail
- Tests that only use valid inputs for functions with validation
- Tests that never trigger error handling code
- Tests where mocks always return success values

### Keep (even if they look trivial):
- Regression guards for specific bug fixes
- Tests validating invariants between related values
- Tests documenting API contracts
- Integration tests exercising cross-layer behavior

## Instructions
1. Read coverage.json to extract coverage data for your domain's source files
2. Launch all 5 subagents in parallel
3. Each subagent should READ the source files and test files thoroughly — not just filenames
4. After all subagents complete, read their reports and write a brief summary to the console
5. Every test file in the domain must be reviewed by exactly one subagent — no gaps, no overlaps
```

---

## SESSION 4: Cross-Domain + Research + Misc

```
# Test Suite Review — Session 4: Cross-Domain + Research + Misc

You are conducting a comprehensive test suite review for the Starship Battles project. Your job is to produce REPORTS ONLY — no code changes. You will coordinate 4 subagents. This session has a dual role: review smaller domains AND perform cross-domain deduplication analysis.

## Project Context
- Python 3.x game project, ~14,689 pytest tests across 1,044 files
- Source: ~123,258 LOC across 495 files in game/
- Coverage data is available at `coverage.json` in the project root (line-level coverage for every source file)
- This is a clean-sheet review — ignore any prior review results
- Sessions 1-3 are reviewing Core+Sim+AI, Strategy, and UI respectively — this session handles everything else plus cross-domain dedup

## Your Domain
**Source ownership:** game/research/ (7 files, 100% coverage)
**Cross-domain analysis:** colonization, superweapons, fleet orders, production — features that span multiple source packages and have tests scattered across many directories

**Test territory:** ~80 files + cross-domain reads

## Goals
1. Review research and misc test quality
2. Identify cross-domain test duplication — tests in different directories that assert the same behaviors
3. Review infrastructure/repro/regression tests for staleness

## Subagent Plan
Launch 4 subagents in parallel. Each writes its report to the specified path.

**Agent 1 — Research** → `Reviews/results/2026-04-08_test-review/session_4_crossdomain/agent_1_research.md`
- Source: game/research/ (7 files — research_tracker.py, tech_node.py, tech_tree.py, research_service.py, etc.)
- Tests: tests/unit/research/ (16 files) + tests/integration/research_workflow/ (2 files)
- Read coverage.json for game/research/ files (100% line coverage — but does that mean QUALITY coverage?)
- Focus: 100% line coverage doesn't mean good tests — check if tests exercise edge cases, error paths, boundary conditions. Research went from 0% to 100% recently, so tests may be superficial. Check for: empty tech trees, circular dependencies, invalid node references, resource overflow, concurrent research conflicts

**Agent 2 — Cross-Domain Colonization + Superweapons Dedup** → `Reviews/results/2026-04-08_test-review/session_4_crossdomain/agent_2_colonization_dedup.md`
- No source ownership — this is a dedup-only analysis
- Search for ALL colonization-related test files across the entire tests/ directory (grep for "coloniz", "colony", "settle", "ColonizeAbility", "colonize_planet")
- Search for ALL superweapon-related test files (grep for "superweapon", "super_weapon", "SuperWeapon")
- For each cluster of related tests found:
  - Read the test assertions in each file
  - Determine: are these testing genuinely different layers/concerns, or duplicating the same assertions at different abstraction levels?
  - Produce a dedup map: "Test A in tests/unit/strategy/engine/ duplicates Test B in tests/integration/colonization/ because both assert [specific thing]"
- Does NOT re-review individual test quality (sessions 1-3 handle that)
- Focus purely on: which test files across sessions overlap in what they verify

**Agent 3 — Cross-Domain Fleet Orders + Production Dedup** → `Reviews/results/2026-04-08_test-review/session_4_crossdomain/agent_3_fleet_production_dedup.md`
- No source ownership — dedup-only analysis
- Search for ALL fleet order-related test files (grep for "fleet_order", "FleetOrder", "order_processor", "move_order", "patrol_order", "transfer_order")
- Search for ALL production-related test files (grep for "production", "build_queue", "ComputePlanetProduction", "production_rate", "production_engine")
- For each cluster, same approach as Agent 2: read assertions, determine genuine layer separation vs duplication
- Known issue: TestComputePlanetProduction exists in 4+ files — map exactly where and whether they're truly different
- Focus: fleet order tests spread across strategy/engine, strategy/data, strategy/fleet, integration/strategy, integration/gameplay_loop; production tests spread similarly

**Agent 4 — Misc Infrastructure** → `Reviews/results/2026-04-08_test-review/session_4_crossdomain/agent_4_misc.md`
- Tests: tests/unit/performance/ + tests/unit/infrastructure/ + tests/unit/regressions/ + tests/repro_issues/ + tests/projects/ + any orphaned test files not assigned to sessions 1-3
- Also check: tests/unit/services/ (may be empty or orphaned), any test files in the root of tests/unit/ that aren't in subdirectories
- For repro_issues/: read each file and determine if the bug it reproduces is now covered by proper tests elsewhere (making the repro script redundant)
- For regressions/: check if the regression snapshots are still valid and useful
- For performance/: check if performance tests are maintained and meaningful
- Focus: which of these are still needed, which are dead infrastructure, which should be deleted vs promoted

## Report Format
Each subagent MUST use this exact format:

```markdown
# Test Review Report: [Agent Name]
## Scope
- Source files reviewed: [list with line counts]
- Test files reviewed: [list with line counts]
- Coverage data referenced: [yes/no, summary stats]

## Summary
- Test files reviewed: N
- Source files reviewed: N
- Tests flagged for removal: N (estimated LOC: N)
- Tests flagged as happy-path-only: N
- Source files with inadequate coverage: N

## A. Tests Recommended for Removal
For each:
- **File:** path
- **Test(s):** class/method names
- **Reason:** DUPLICATE_OF:<path> | TRIVIAL_CONSTANT | DEAD_CODE | OVER_MOCKED | SCAFFOLD_ONLY | TESTS_NOTHING_REAL
- **Confidence:** HIGH | MEDIUM | LOW
- **Evidence:** 1-3 sentence proof (cite specific line numbers)
- **Estimated LOC saved:** N

## B. Tests That Are Happy-Path-Only
For each:
- **File:** path
- **Test(s):** class/method names
- **What's tested:** description
- **What's missing:** specific error paths, edge cases, boundary values
- **Source method(s) affected:** path:line
- **Priority:** HIGH | MEDIUM | LOW (based on source criticality)

## C. Source Code with Inadequate Coverage
For each:
- **Source file:** path (LOC)
- **Coverage:** percentage from coverage.json + qualitative assessment
- **Untested areas:** specific methods, branches, error paths
- **Risk:** what could break without tests
- **Priority:** HIGH | MEDIUM | LOW

## D. Cross-Domain Observations
Anything that affects other sessions' domains.

## E. Dedup Map (Agents 2 and 3 only)
For each duplicated behavior:
- **Behavior:** what is being tested
- **Test locations:** [file1:class:method, file2:class:method, ...]
- **Recommendation:** which to keep, which to remove, or "genuinely different concerns"
```

## Instructions
1. Read coverage.json for research domain files
2. Launch all 4 subagents in parallel
3. Subagents 2 and 3 should use Grep extensively to find all relevant test files before reading them
4. After all subagents complete, read their reports and write a brief summary to the console
```

---

## SESSION 5: Skeptical Validator + Synthesis

```
# Test Suite Review — Session 5: Skeptical Validator + Synthesis

You are the final session of a comprehensive test suite review. Sessions 1-4 have produced reports with claims about tests to remove, happy-path-only tests, and coverage gaps. YOUR JOB IS TO SKEPTICALLY VALIDATE EVERY REMOVAL CLAIM and then synthesize a final report.

## Project Context
- Python 3.x game project, ~14,689 pytest tests across 1,044 files
- Coverage data at `coverage.json` in the project root
- Sessions 1-4 reports are at `Reviews/results/2026-04-08_test-review/`

## Your Role
You are a SKEPTICAL VALIDATOR. Your default assumption is that every "remove this test" claim is WRONG until you independently verify it. You are looking for:
- Claims where the reviewer missed that a test covers a subtle edge case
- Claims where "duplicate" tests actually test different code paths
- Claims where "trivial" tests actually guard against regressions
- Claims where removing a test would leave a real coverage gap
- Overclaims — marking things HIGH confidence that should be MEDIUM or LOW

## Subagent Plan
First, read ALL reports from sessions 1-4 to understand the full scope of claims. Then launch 5 subagents.

**Read these report directories first:**
- Reviews/results/2026-04-08_test-review/session_1_core_sim_ai/ (4 reports)
- Reviews/results/2026-04-08_test-review/session_2_strategy/ (5 reports)
- Reviews/results/2026-04-08_test-review/session_3_ui/ (5 reports)
- Reviews/results/2026-04-08_test-review/session_4_crossdomain/ (4 reports)

Extract all HIGH and MEDIUM confidence removal claims from every report. Then launch validators.

**Validator 1 — Core + Sim + AI claims** → `Reviews/results/2026-04-08_test-review/session_5_validation/validator_1_core_sim.md`
- Take every HIGH and MEDIUM removal claim from session_1 reports
- For each claim: read the actual test file, read the source code it tests, independently assess
- Verdict for each: CONFIRMED (agree with removal), DOWNGRADED (lower confidence than claimed), or REJECTED (should keep)
- If REJECTED: explain what the reviewer missed

**Validator 2 — Strategy claims** → `Reviews/results/2026-04-08_test-review/session_5_validation/validator_2_strategy.md`
- Same process for session_2 reports

**Validator 3 — UI claims** → `Reviews/results/2026-04-08_test-review/session_5_validation/validator_3_ui.md`
- Same process for session_3 reports

**Validator 4 — Cross-domain claims** → `Reviews/results/2026-04-08_test-review/session_5_validation/validator_4_crossdomain.md`
- Same process for session_4 reports
- Pay special attention to dedup claims — "these two tests duplicate each other" requires reading BOTH tests carefully

**Synthesizer** → Runs AFTER validators 1-4 complete (do NOT launch in parallel with validators)
Writes: `Reviews/results/2026-04-08_test-review/session_5_validation/synthesis.md` AND `Reviews/results/2026-04-08_test-review/final_report.md`

The synthesizer reads all validator reports plus all session 1-4 reports and produces a final report with:

```markdown
# Test Suite Review — Final Report

## Executive Summary
- Total tests reviewed: N
- Tests recommended for removal (validated): N (LOC: N)
- Tests flagged as happy-path-only: N
- Source files with inadequate coverage: N
- Cross-domain duplicates found: N

## 1. Validated Removals (by priority)
### HIGH confidence (confirmed by validator)
[list each with file, reason, LOC]

### MEDIUM confidence (confirmed or not rejected)
[list each]

### Rejected claims (reviewer was wrong)
[list with explanation of why]

## 2. Happy-Path-Only Tests (by priority)
### HIGH priority (critical source code)
[list with what's missing]

### MEDIUM priority
[list]

### LOW priority
[list]

## 3. Coverage Gaps (by priority)
### Critical (0-30% coverage, important code)
[list with specific untested methods]

### Major (30-60% coverage)
[list]

### Minor (60-80% coverage)
[list]

## 4. Cross-Domain Dedup Recommendations
[validated dedup findings]

## 5. Recommended Action Order
1. [First thing to do — highest impact, lowest risk]
2. [Second]
3. ...

## 6. Statistics
- Estimated LOC reduction from removals: N
- Estimated new tests needed: N
- Current coverage: 71.9% → Projected after improvements: N%
```

## Validation Report Format
Each validator uses:

```markdown
# Validation Report: [Domain]

## Claims Reviewed: N
## Confirmed: N | Downgraded: N | Rejected: N

## Detailed Verdicts

### [Claim 1]
- **Original claim:** [file, reason, confidence]
- **Verdict:** CONFIRMED | DOWNGRADED | REJECTED
- **Evidence:** [what I found when I read the actual code]
- **Validated confidence:** HIGH | MEDIUM | LOW | KEEP

### [Claim 2]
...
```

## Skeptical Questions to Ask for Each Claim
- "Is this REALLY a duplicate, or does it test a subtly different code path?"
- "Is this REALLY testing nothing, or does it guard against a regression?"
- "Would removing this test leave a gap that no other test covers?"
- "Does git blame show this test was added to fix a specific bug?"
- "If I deleted this test and someone broke the code it covers, would any other test catch it?"

## Instructions
1. Read ALL session 1-4 reports first
2. Extract all HIGH and MEDIUM removal claims into a list
3. Launch validators 1-4 in parallel (one per session domain)
4. WAIT for all validators to complete
5. Then launch the synthesizer (NOT in parallel — it needs validator results)
6. Print the final summary to the console
```
