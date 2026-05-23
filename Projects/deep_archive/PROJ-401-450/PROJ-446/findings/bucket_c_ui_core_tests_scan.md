# Bucket C — UI + Core + Tests Residue Scan (2026-05-18)

## Summary
- Total findings: 30
- By severity: high 0, medium 12, low 18
- By category: obsolete-code 14, test-inconsistency 8, missing-functionality 3, polish 5
- Files reviewed: ~70 (full reads) plus broad grep over all of `game/ui/`, `game/core/`, `tests/`
- Archived/active project decisions.md / findings_ledger.md scanned: PROJ-329A, PROJ-351A, PROJ-353A, PROJ-354A/B, PROJ-416..435 (subset), PROJ-FMS-A/B/C/D, PROJ-FMS-shared (skim), active PROJ-436/437/438/443

Deduplicated against the 9 entries in `AgentCoordination/discovered_issues/log.jsonl` (the two log entries naming `game/ui/screens/transfer_dialog.py` 523-LOC overflow and `game/ui/screens/builder/stat_rows_dynamic.py` LABEL_ABBREV are skipped here).

## Findings

### F-C-001 — Battle-setup `side_0` / `side_1` back-compat shim cluster still load-bearing
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/battle_setup_state.py:172` (property block 178-192)
- **Symbol**: `BattleSetupState.side_0` / `BattleSetupState.side_1`
- **Source refactor**: PROJ-275 Phase 4+5 (N-team migration)
- **What survived**: `side_0` / `side_1` read/write property pair atop `self.sides[0]` / `self.sides[1]`. The class docstring explicitly says callers "will be migrated incrementally."
- **Why it's a problem**: 2 production files (`battle_setup_state.py`, `battle_setup/controller.py`) and 5 tests still reach through `.side_0` / `.side_1` instead of `state.sides[i]` / `state.get_side(team_id=...)`. The migration was started in 2026-05-04 and never completed; new N-team code keeps having to coexist with hardcoded 2-team naming.
- **Suggested action**: Sweep the 2 production files + 5 tests to `state.sides[0]` / `state.sides[1]` (or the existing `state.get_side(team_id)` accessor), then delete the property pair.
- **Effort**: tiny (~30 mechanical edits)

### F-C-002 — `transfer_dialog._on_confirm` bare `except Exception` without intentional-reason comment
- **Severity**: low
- **Category**: polish
- **File**: `game/ui/screens/transfer_dialog.py:412`
- **Symbol**: `TransferDialog._on_confirm`
- **Source refactor**: PROJ-321..328 audit S1.2 / PROJ-343 T1.4
- **What survived**: `except Exception:` at line 412 has only a body-comment ("Catastrophic dispatch failure — close the modal..."), not the convention-required same-line or immediately-above `# Intentional broad catch: <reason>` marker. Every other `except Exception` in `game/ui/` carries the marker; this is the lone offender.
- **Why it's a problem**: Violates the broad-catch convention in `docs/03_CONVENTIONS.md` (Error Handling). The marker is the lint signal that the broad catch is intentional; without it future grep audits flag it as drift.
- **Suggested action**: Add `# Intentional broad catch: <reason>` on line 412 (or immediately above) describing the catastrophic-dispatch rationale already in the body comment.
- **Effort**: tiny (1 line)

### F-C-003 — `transfer_dialog.py` legacy public-method shims `_extract_dropdown_value`, `_format_pending`, `_discover_pod_designs`
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/transfer_dialog.py:279-286`
- **Symbol**: `TransferDialog._extract_dropdown_value` / `_format_pending` / `_discover_pod_designs`
- **Source refactor**: PROJ-328 Phase C / PROJ-437
- **What survived**: Three public-method shims that just delegate to `TransferGridRenderer.extract_dropdown_value`, `view_model.format_pending`, and `_controller.discover_pod_designs`. Comment at line 275 acknowledges "kept as public method shims for back-compat with tests that exercise them directly."
- **Why it's a problem**: Sibling cluster of the dialog-level `_get_amounts` / `_add_pod_rows` / `_all_pod_names` shims that PROJ-437 Phase 4 deleted. These three escaped that pass for the same reason (test reachability). With them retired, `transfer_dialog.py` drops further toward the 500-LOC ceiling without changing observable UX.
- **Suggested action**: Migrate the 2-3 characterization-test sites in `tests/unit/ui/screens/test_transfer_dialog_characterization.py` to call the underlying VM/controller/renderer surfaces directly, then delete the three method shims.
- **Effort**: tiny

### F-C-004 — `strategy_renderer.py` back-compat shims for `_bg_image` / `_bg_scaled` / `_hex_outline_cache` family
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/strategy_renderer.py:107-130`
- **Symbol**: `StrategyRenderer._bg_image` / `_bg_scaled` / `_bg_scaled_size` / `_bg_brightness` / `_hex_outline_cache` / `_hex_outline_cache_turn`
- **Source refactor**: PROJ-309 sub-phase 3.2 (renderer decomposition)
- **What survived**: Six read-only `@property` shims that just return the underlying field on `self._background` / `self._hex_outlines`. Class comment explicitly says: "Back-compat shims for tests that read these as instance attributes."
- **Why it's a problem**: Pre-PROJ-309 the renderer held these caches itself; after extraction tests still read through the old attribute names. Tests should reach the layer modules directly (`renderer._background._bg_image`) or, better, never poke private cache state at all.
- **Suggested action**: Find test sites still reading the six shimmed names and re-point them at the layer objects; delete the property block.
- **Effort**: tiny

### F-C-005 — Module-level `draw_grid(r, screen)` free function preserved for tests only
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/strategy_render/grid.py:104`
- **Symbol**: `game.ui.screens.strategy_render.grid.draw_grid`
- **Source refactor**: PROJ-374 (GridLayer surface cache)
- **What survived**: Free function `draw_grid` whose docstring says "Uncached fast path retained for back-compat with existing direct callers (e.g. tests). Production rendering goes through `GridLayer.draw`." Production callers all use `_draw_grid` method on the renderer; only the two test files at `tests/unit/ui/screens/test_strategy_renderer.py` and `tests/unit/ui/screens/strategy_render/test_grid_and_storms.py` reach the module-level function.
- **Why it's a problem**: A back-compat shim kept alive solely by tests is a maintenance liability — every refactor of `GridLayer` has to remember to preserve the fast-path semantics.
- **Suggested action**: Update the two test files to instantiate `GridLayer` and call `.draw`, then delete `draw_grid`.
- **Effort**: tiny

### F-C-006 — `BuildQueueScreen.build_context` positional kwarg preserved for back-compat
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/build_queue_screen.py:84-90`
- **Symbol**: `BuildQueueScreen.__init__(... build_context=None ...)`
- **Source refactor**: PROJ-376 Phase 1
- **What survived**: Constructor accepts both `initial_yard` (new keyword-only kwarg) and `build_context` (legacy positional/keyword arg). Body picks one with `effective_initial_yard = initial_yard if initial_yard is not None else build_context`. Docstring: "The legacy `build_context` positional/keyword arg is preserved for back-compat."
- **Why it's a problem**: Dual-name kwargs are confusing — call sites can pass both and the second is silently discarded. Renaming should have included a sweep of callers.
- **Suggested action**: `git grep -n "build_context=" game tests | grep -v build_queue_screen` to find remaining callers, migrate them to `initial_yard=`, drop the legacy parameter.
- **Effort**: tiny-to-small

### F-C-007 — `RaceSetupScreen._description_controller` shim
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/race_setup/screen.py:277-285`
- **Symbol**: `RaceSetupScreen._description_controller` (property + setter)
- **Source refactor**: race_setup MVVM split (PROJ-329A-era)
- **What survived**: Property reading `self._controller.description_controller` and setter that delegates to `self._controller.attach_description_controller(value)`. Comment: "Tests + legacy code read `screen._description_controller`."
- **Why it's a problem**: Same pattern as F-C-004 — a private attribute survived only because tests/legacy callers read the pre-refactor location. Bypass-init helpers also wire through it.
- **Suggested action**: Migrate callers to `screen._controller.description_controller` / `.attach_description_controller(...)`, delete the property/setter pair.
- **Effort**: tiny

### F-C-008 — `NewGameSetupScreen` view-model property shim cluster (6 properties)
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/new_game_setup_screen.py:272-321`
- **Symbol**: `NewGameSetupScreen.player_count` / `.galaxy_type` / `.system_count` / `.player_races` / `.active_race_modal` / `.race_modal_player_index` (all property + setter)
- **Source refactor**: PROJ-392 (controller / VM split)
- **What survived**: Six read/write property shims routing to `self._view_model.*`. Comment block at 272: "Backwards-compat property shims — view-model state." This is the same pattern as `battle_setup/screen.py` and `transfer_dialog.py` shims that have been at least partially retired.
- **Why it's a problem**: The screen is 734 LOC (over the 500-LOC ceiling). Retiring this cluster shrinks the file and removes a foot-gun where `screen.player_count = 4` and `view_model.player_count = 4` are two paths to the same state.
- **Suggested action**: Find callers (mostly tests) of the six names, point them at `screen._view_model.<name>`, delete the property block. Same recipe as PROJ-437 Phase 4 transfer-dialog shim retirement.
- **Effort**: small

### F-C-009 — `battle_setup/screen.py` view-model / controller shim cluster
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/battle_setup/screen.py:93-205`
- **Symbol**: `BattleSetupScreen.active_side` / `.active_fleet_index` / `.selected_tf_index` / `.selected_sq_index` / `.selected_ship_index` / `.available_designs` (VM shims, 93-143) plus `.tick_limit` / `.end_all_destroyed` / `.end_all_derelict` / `.end_mass_ratio` / `.mass_ratio_threshold` (controller shims, 145-205)
- **Source refactor**: battle_setup MVVM split
- **What survived**: ~11 read/write property shims between screen and either view-model or controller. Section comments self-identify as shims ("View-model property shims", "Controller property shims").
- **Why it's a problem**: Same retire-shims-via-test-migration pattern as F-C-008. Plus this file (559 LOC) is currently over the 500-LOC ceiling and these shims are most of the overflow.
- **Suggested action**: Same recipe — migrate test/renderer/panel sites to read `screen.view_model.<name>` / `screen.controller.<name>`, delete the property block. Likely drops the file under the LOC ceiling.
- **Effort**: small

### F-C-010 — `OrdersWindow._get_order_description` back-compat shim
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/orders_window.py:464-475`
- **Symbol**: `OrdersWindow._get_order_description`
- **Source refactor**: PROJ-328
- **What survived**: A method whose docstring says: "PROJ-328: Pre-refactor public-ish API. Tests / callers that used to call `screen._get_order_description(order)` get the same answer; the implementation now lives on `OrderDescriber`."
- **Why it's a problem**: Standard test-only shim — production calls `OrderDescriber` directly.
- **Suggested action**: Migrate test sites to instantiate `OrderDescriber` and call it directly, delete the shim method.
- **Effort**: tiny

### F-C-011 — `transfer_dialog.py` sentinel + layout-constant class re-exports kept for back-compat
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/transfer_dialog.py:58-66`
- **Symbol**: `TransferDialog._MAX_SENTINEL` etc., plus class-level layout constants
- **Source refactor**: PROJ-328 / PROJ-437
- **What survived**: Inline comments at lines 58 and 64 declare these are "re-exported on the class for back-compat with..." (legacy importers) and "Layout constants kept on the class for back-compat with any..."
- **Why it's a problem**: After PROJ-437 retired most of the transfer-dialog back-compat surface, the remaining `transfer_dialog.py` shim residue is mostly these two pockets. The constants belong on `TransferGridRenderer` or `TransferViewModel`; pulling them out of the dialog class would let the LOC drop further.
- **Suggested action**: Move sentinels / layout constants to their owning module, update the 1-2 importers, delete the class-level re-exports.
- **Effort**: tiny

### F-C-012 — `EventLogWindow.empire_name=None` back-compat default fallback
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/ui/screens/event_log_window.py:113-116`
- **Symbol**: `EventLogWindow.__init__(... empire_name=None ...)` (title rendering)
- **Source refactor**: BUG-123 fix
- **What survived**: When `empire_name` is None the window title falls back to the plain "Event Log" string. Docstring: "back-compat for callers that don't supply it, including tests."
- **Why it's a problem**: Production paths always have an empire name (the active empire); the None branch exists only because some tests construct the window without one. A minor cleanup, easy to miss in a future refactor.
- **Suggested action**: Audit `event_log_window` constructors in tests, supply an explicit empire_name, change the parameter to required (or default to a real value).
- **Effort**: tiny

### F-C-013 — `IFacility.consumable_levels` protocol method docstring describes facility-internal contract (kept by Phase-0 D1)
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/core/protocols/strategy_domain.py:144`
- **Symbol**: `IFacility.consumable_levels`
- **Source refactor**: PROJ-436 Phase 0 D1 default
- **What survived**: Protocol still declares `consumable_levels` as a `Dict[str, float]`. The Phase-6 audit chose "leave as-is" but PROJ-436 retired the equivalent `Planet.stockpile` and renamed `ShipInstance.consumable_levels` to a property over a private field. The protocol contract is inconsistent: stockpile/cargo on ships and planets routes through `IPlanetMutator` / manager APIs; facility consumables remain a directly-exposed mutable dict.
- **Why it's a problem**: New strategy code that touches facility consumables can directly mutate the returned dict, bypassing whatever future write-service might want to track changes. The protocol-surface ratchet at `tests/static_guards/test_no_legacy_protocol_names.py` explicitly pins this as a deliberate "stay-as-is" decision, which surfaces the inconsistency as audit-acknowledged tech debt rather than a hidden seam, but the inconsistency itself is still residue.
- **Suggested action**: Either declare `IFacility` immutable (`Mapping[str, float]`) and route writes through a new mutator, or leave-and-document. The static-guard `test_ifacility_still_declares_consumable_levels` already pins it; a docstring update on the protocol member declaring the intentional inconsistency would close the loop.
- **Effort**: tiny (doc) or medium (mutator extraction)

### F-C-014 — `IShipInstance.cargo_contents` protocol surface kept as a writable dict view
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `game/core/protocols/strategy_domain.py:188`
- **Symbol**: `IShipInstance.cargo_contents`
- **Source refactor**: PROJ-436 Phase 3f / Phase 6 audit
- **What survived**: Protocol member docstring explicitly states the property is "**not** read-only in absolute terms" because a concrete-class setter still exists for the legacy-kwarg constructor wrapper. Production code is told to "**prefer** the cargo manager API for writes."
- **Why it's a problem**: A protocol that says "this property exists, but please don't mutate it via the protocol" is a contract crack. Callers that narrow to `IShipInstance` get a read surface that quietly accepts writes. PROJ-443 Phase 5b explicitly retained the wrapper that's the reason for this; the protocol-side residue is the visible echo.
- **Suggested action**: Narrow the protocol to a read-only `Mapping[str, int]` view; if PROJ-443's deferred wrapper is removed, the concrete-class setter goes too. Until then, annotate the property with `Mapping[str, int]` instead of `Dict[str, int]` to at least communicate the intent in the type signature.
- **Effort**: tiny (type-annotation) or small (full migration)

### F-C-015 — `stat_rows_dynamic.py` hardcoded `PLANET_RESOURCE_NAMES` plus `LABEL_ABBREV` reach into resource catalog twice
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `game/ui/screens/builder/stat_rows_dynamic.py:177-181` (Construction section), :251-254 (Strategic section)
- **Symbol**: `get_construction_rows` / `get_strategic_rows` (LABEL_ABBREV constants are loop-local)
- **Source refactor**: PROJ-435 / PROJ-436 Phase 7
- **What survived**: Two separate `LABEL_ABBREV` dicts hardcoding 5 resource-id → display-name pairs. `PLANET_RESOURCE_NAMES` correctly iterates `ResourceCatalog.from_json().by_display_group("planetary")` (post-PROJ-436), but the display labels still come from a hardcoded dict instead of `ResourceDefinition.name`.
- **Why it's a problem**: Adding a 6th planetary resource produces a row whose getter works but whose label silently falls back to the raw resource_id. Same anti-pattern as the already-logged log.jsonl entry DI-2026-05-18-004 (which names this exact file but only flags the IDs side). This finding is the **label-side** companion — the IDs are now driven by the catalog, but display labels still aren't.
- **Suggested action**: Drop the two `LABEL_ABBREV` dicts; use `ResourceCatalog.from_json().get(res).name` (or a single helper `_label_for(resource_id)` that wraps the catalog lookup once per render).
- **Effort**: tiny

### F-C-016 — `tests/fixtures/README.md` describes `ui_widget_factory.py` with the retired "blocker" framing
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/fixtures/README.md:22` and `:310-333`
- **Symbol**: README documentation (`ui_widget_factory.py    # Non-UIWindow widget factory`, "Limitation — UIWindow super-init chain", link to `docs/known-issues.md#uiwindow-super-init-chain-blocker`)
- **Source refactor**: PROJ-329A retrofits + Compositional Construction (PROJ-322 onward)
- **What survived**: README still describes the factory as "Non-UIWindow only" and points at the old blocker. `docs/known-issues.md:34-36` explicitly flags this as a "Stale-doc warning: `tests/fixtures/README.md` still describes `ui_widget_factory.py` as 'non-UIWindow only' and points at the old blocker. The current authoritative guidance is the factory docstring plus `docs/02_PATTERNS.md` section 33."
- **Why it's a problem**: New contributors reading the README first will mis-route their UIWindow test setup. The fix is text-only and docs/known-issues.md already names it.
- **Suggested action**: Rewrite the `ui_widget_factory.py` section to point at the two-stage Pattern #33 plus the factory docstring; drop the "blocker" framing and stale anchor link.
- **Effort**: tiny

### F-C-017 — Deferred UIWindow retrofit: `SettingsWindow` + 4 `PlanetTargetEditor` subclasses lack DEDICATED behavior-locking retrofit tests
- **Severity**: low
- **Category**: missing-functionality (no DEDICATED retrofit/behavior-locking tests; some incidental coverage exists)
- **File**: `game/ui/screens/settings_window.py` (109 LOC), `game/ui/screens/atmosphere_target_editor.py` (273), `game/ui/screens/gravity_target_editor.py` (220), `game/ui/screens/water_target_editor.py` (227), `game/ui/screens/radiation_shield_editor.py` (231)
- **Symbol**: `SettingsWindow`, `AtmosphereTargetEditor`, `GravityTargetEditor`, `WaterTargetEditor`, `RadiationShieldEditor`
- **Source refactor**: PROJ-329A decisions D-003 / D-009
- **What survived**: PROJ-329A deferred the **dedicated retrofit + characterization test pass** for these 5 UIWindow subclasses until they gained coverage. Codex verification 2026-05-18 found incidental coverage exists: the 4 PlanetTargetEditor subclasses are exercised through the explicit-window-manager contract suite at `tests/unit/ui/screens/test_strategy_modal_window.py:367-398`, and `SettingsWindow` creation/slot handling is exercised via `SettingsRegistrar` in `tests/unit/ui/screens/strategy_windows/test_empire_panel_ctrl.py:100-127`. No DEDICATED test file exists for any of the 5 windows; no behavior-locking characterization pass has been run; the bypass-init shell retrofit recipe (Pattern #33) was never applied.
- **Why it's a problem**: The 5 windows are exercised structurally (do they instantiate? do their slots wire?) but not behaviorally (do their state transitions, validation rules, and ok/cancel paths preserve invariants?). Refactoring them without a characterization pass first means any future migration breaks invisibly until a user reports it. PROJ-329A's "refactoring untested code adds risk without locking behavior" framing still applies — just less acutely than the original "zero coverage" framing suggested.
- **Suggested action**: Pick the smallest one (`SettingsWindow`, 109 LOC) and write a characterization-test pass through the bypass-init shell, then apply the standard two-stage retrofit recipe. Use the existing 6 retrofitted windows (`RaceSetupScreen`, `NewGameSetupScreen`, etc.) as templates.
- **Effort**: medium (per window) — ~1 small project per window
- **Codex verification (2026-05-18)**: Original framing said "zero test coverage" — literally false; incidental modal-window and registrar coverage exists. Severity downgraded medium → low; category clarified to "no DEDICATED behavior-locking retrofit tests" rather than "untested."

### F-C-018 — No static guard against `DesignLibrary` class re-emergence
- **Severity**: low
- **Category**: missing-functionality
- **File**: `tests/static_guards/` (would-be guard does not exist)
- **Symbol**: missing `test_no_design_library_class.py`
- **Source refactor**: PROJ-427 / PROJ-434 (DesignLibrary → DesignCatalog + DesignRepository)
- **What survived**: 10 production files in `game/` still reference `DesignLibrary` in comments (workshop_ship_io.py, strategy_build_queue_manager.py, transfer_controller.py, build_queue_controller.py, etc.) describing what the new class replaced. The class itself is gone, but no static guard pins its absence — the established pattern for similar retirements (`test_no_resource_types_constant.py`, `test_no_legacy_storage_fields.py`, `test_no_carried_items_proxy.py`, `test_no_legacy_protocol_names.py`).
- **Why it's a problem**: A future "I'll just re-create DesignLibrary as a thin shim..." regression has no automated catcher. Every other major retirement in PROJ-436/437 got a guard; this one didn't.
- **Suggested action**: Add `tests/static_guards/test_no_design_library_class.py` that asserts `not hasattr(game.strategy.systems.design_catalog, "DesignLibrary")` and AST-scans the strategy/systems package for a `class DesignLibrary` definition. Sibling pattern to PROJ-436 Phase-9 carried_items proxy guard.
- **Effort**: tiny (~30 LOC test file)

### F-C-019 — No static guard against `_ACTIVATABLE_ABILITIES` UI re-emergence
- **Severity**: low
- **Category**: missing-functionality
- **File**: `tests/static_guards/` (would-be guard does not exist)
- **Symbol**: missing `test_no_activatable_abilities_constant.py`
- **Source refactor**: PROJ-435
- **What survived**: PROJ-435 retired the hardcoded `_ACTIVATABLE_ABILITIES` literal in `stat_rows_dynamic.py` in favor of `abilities_with_kind_tag(StrategicKind.ENERGY_DRAINING)`. The retirement is mentioned in `planet_energy_engine.py:92` and `ability_metadata.py:132`. No static guard pins the absence — same gap as F-C-018.
- **Why it's a problem**: PROJ-435 was an entire spin-off project to retire one hardcoded set. A future "just add it back, it's easier" regression would slip in silently.
- **Suggested action**: Add `tests/static_guards/test_no_activatable_abilities_constant.py` that AST-scans `game/ui/screens/builder/stat_rows_dynamic.py` for any `_ACTIVATABLE_ABILITIES =` assignment.
- **Effort**: tiny

### F-C-020 — `tests/fixtures/strategy_entities.py` still passes legacy `consumable_levels=` / `cargo_contents=` kwargs [JOINT-PHASE with PROJ-444]
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/fixtures/strategy_entities.py:140`, `:318`, `:320`
- **Symbol**: `create_test_planetary_facility`, `create_test_ship_instance`
- **Source refactor**: PROJ-436 Phase 3f / PROJ-443 Phase 5b
- **What survived**: The shared fixture module passes `consumable_levels={...}` and `cargo_contents={...}` to `PlanetaryFacility(...)` and `ShipInstance(...)`. Works only because the `_ship_instance_init_with_legacy_kwargs` wrapper translates them; the wrapper was kept by PROJ-443 Phase 5b ("retain the wrapper... revisit only if introspection-based tooling starts depending on the field shape").
- **Why it's a problem**: The fixture module is the single largest shared site of the legacy-kwarg surface. Migrating it would unblock most of the PROJ-444 F-A-003 / F-A-005 wrapper retirement. The PROJ-443 decision log specifically calls this out as a deferred follow-up.
- **Suggested action**: Migrate the 3 fixture sites to the post-PROJ-436 private kwargs (`_cargo_contents=...` / `_consumable_levels=...`) or use the cargo/resource managers. Then run the sharded suite to see how many direct callers still need migration; that number lets us decide whether the wrapper retirement is now in scope.
- **Effort**: tiny (fixture file) + small (downstream sweep)
- **CROSS-BUCKET CLASSIFICATION**: STRUCTURAL JOINT-PHASE, not mere coordination. The wrapper retirement (PROJ-444 F-A-003 / F-A-005) cannot land cleanly without first editing this fixture file, which PROJ-446 owns. **Either rebucket this finding into PROJ-444's wrapper-retirement phase, or commit to a stacked PR / joint phase across PROJ-444 + PROJ-446.** Codex consult 2026-05-18 flagged the original "coordination point" framing as understating the seam. Codex's `rg` audit also indicates the legacy-kwarg test footprint is materially larger than PROJ-443's earlier 18-file estimate; size the effort with a fresh count before committing.

### F-C-021 — Stale skip in `tests/integration/research_workflow/test_workflow.py` references unconditional "tech tree JSON not found"
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/integration/research_workflow/test_workflow.py:192`
- **Symbol**: `pytest.skip("Tech tree JSON not found")`
- **Source refactor**: pre-PROJ-416
- **What survived**: Skip path triggers when `tech_tree.json` isn't found in the repo. The file exists at `data/tech_tree.json` (verified earlier in PROJ-419 work). If the skip ever fires today it's a test-discovery bug, not a missing-file condition.
- **Why it's a problem**: A skip that never fires is dead code; one that fires for the wrong reason hides regressions.
- **Suggested action**: Either remove the skip (assert the file exists) or replace with an explicit fail when missing.
- **Effort**: tiny

### F-C-022 — `tests/unit/builder/test_builder_ui_sync.py:163` skip-on-empty-registry pattern is a wallpapered failure
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/unit/builder/test_builder_ui_sync.py:163`
- **Symbol**: `pytest.skip("No vehicle classes found to test type filtering.")`
- **Source refactor**: pre-PROJ-416
- **What survived**: Skip when `vehicle_classes` registry is empty. Production registries always have entries; an empty registry is a test-fixture bug, not a test skip case.
- **Why it's a problem**: If the registry hydration broke, this test would silently skip instead of failing.
- **Suggested action**: Replace the skip with an explicit assertion that `vehicle_classes` is non-empty; if fixtures don't provide them, fix the fixture.
- **Effort**: tiny

### F-C-023 — `tests/unit/quickstart/test_quickstart_designs.py:133` skip-when-`expected_stats`-missing wallpapers a contract gap
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/unit/quickstart/test_quickstart_designs.py:133`
- **Symbol**: `pytest.skip(f"{design_name} has no expected_stats")`
- **Source refactor**: pre-quickstart contract tightening
- **What survived**: Skip when an iterated quickstart design lacks `expected_stats`. Per `docs/03_CONVENTIONS.md` "Required starter design fields include `name`, `ship_class`, `vehicle_type`, `design_role`, `layers`, `expected_stats`, and `_metadata`" — `expected_stats` is required, so the skip would mask a real conformance failure.
- **Why it's a problem**: Convention says required; test says "skip when missing." Convention should win.
- **Suggested action**: Replace skip with assertion failure; designs lacking `expected_stats` are non-conformant per the documented convention.
- **Effort**: tiny

### F-C-024 — Five `pytest.skip(...)` paths in `tests/unit/modifiers/test_pipeline_unification.py` for "<component> doesn't have <ability>"
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/unit/modifiers/test_pipeline_unification.py:33,50,57,78,131,137`
- **Symbol**: Multiple `pytest.skip("railgun doesn't have ResourceConsumption")` etc.
- **Source refactor**: predates current ability-bindings contract
- **What survived**: Tests skip when a hardcoded component lacks a specific ability. If `data/components.json` changes shape (PROJ-428 worked on this surface), these tests silently skip rather than re-pointing at the right component.
- **Why it's a problem**: 6 skips in one file is a smell. Either fixturize the component selection (look up a component that actually has `ResourceConsumption`) or drop the test outright.
- **Suggested action**: Re-tool tests to discover a representative component dynamically (`first component with ability X from session registry`), so they exercise the unified pipeline instead of bailing.
- **Effort**: small

### F-C-025 — `tests/regression/modifier_ability_snapshots/test_*.py` has 16+ `pytest.skip("Baseline snapshot ... created - re-run test")` paths
- **Severity**: medium
- **Category**: test-inconsistency
- **File**: `tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py` (15+ sites) and `test_utility_modifiers.py` (8+ sites)
- **Symbol**: Various `pytest.skip(...)`
- **Source refactor**: pre-PROJ-416 regression-snapshot infrastructure
- **What survived**: A "first run creates the snapshot, skips, then second run actually compares" workflow that produces a skip every single CI run unless the baseline already exists. In CI this means the regression test never *fails* on a real regression in a fresh checkout — it just skips.
- **Why it's a problem**: 16 skips in two files. If a snapshot file is missing on a clean checkout/CI runner, the test silently skips instead of failing on a "baseline-missing" condition. That defeats the purpose of a regression test.
- **Suggested action**: Two options: (a) commit the baseline snapshot fixtures so the skip path never fires (the test asserts on every run), or (b) replace the "skip on missing" with `pytest.fail("Baseline missing — regenerate via X")`. Option (b) matches the intent better.
- **Effort**: small

### F-C-026 — `tests/unit/data/test_data_validation.py:36,67` skip "data/formations/ removed by PROJ-40 cleanup; vacuously passes"
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/unit/data/test_data_validation.py:36`, `:67`
- **Symbol**: `pytest.skip("data/formations/ removed by PROJ-40 cleanup; vacuously passes")`
- **Source refactor**: PROJ-40 (very old)
- **What survived**: Two skips that explicitly say "vacuously passes" because the data dir they tested is gone.
- **Why it's a problem**: A test that vacuously passes is dead code — it asserts nothing, just consumes a test slot. PROJ-40 was many years (in repo-time) ago.
- **Suggested action**: Delete both test functions outright. The convention doesn't include "vacuously passing" as a valid state.
- **Effort**: tiny

### F-C-027 — Production file size overflow: 12 UI files over the 500-LOC ceiling
- **Severity**: medium
- **Category**: polish
- **File**: `game/ui/screens/build_queue_screen.py` (961), `planet_list_window.py` (862), `test_lab/screen.py` (744), `new_game_setup_screen.py` (734), `empire_build_queue_window.py` (734), `event_log_window.py` (732), `panels/race_summary_panel.py` (732), `empire_panel_window.py` (724), `panels/build_queue_controller.py` (723), `panels/system_tree_panel.py` (711), `design_selector_window.py` (708), `strategy_detail_fmt.py` (707)
- **Symbol**: file-level (the 500-LOC ceiling per `docs/03_CONVENTIONS.md`)
- **Source refactor**: cumulative
- **What survived**: 12 production UI files exceed the 500-LOC ceiling. `build_queue_screen.py` is at 961 (almost 2x), `planet_list_window.py` at 862. Multiple other files in the 500-700 range.
- **Why it's a problem**: Convention is "should stay below 500 LOC. ... If a production file approaches or exceeds 500 LOC, split by cohesive responsibility." Several of these files (`build_queue_screen.py`, `event_log_window.py`) were recently touched by major refactors that left them over the ceiling.
- **Suggested action**: Pick the worst offender (`build_queue_screen.py`) and extract a responsibility (yard population, queue selection, drag handling) into a sibling module. Same pattern as the existing `build_queue_*` family split.
- **Effort**: medium per file (project-shaped, not single-pass)

### F-C-028 — `game/core/exceptions.py` is 544 LOC, over the 500-LOC ceiling
- **Severity**: low
- **Category**: polish
- **File**: `game/core/exceptions.py:1` (file-level)
- **Symbol**: `game.core.exceptions` module
- **Source refactor**: PROJ-45 (Error Handling)
- **What survived**: The exception-hierarchy module is 544 LOC. The 500-LOC convention applies to all production files under `game/`, not just UI.
- **Why it's a problem**: Same ceiling rule as F-C-027.
- **Suggested action**: Split by domain — `exceptions_persistence.py`, `exceptions_validation.py`, etc. — with the top-level `exceptions.py` re-exporting for back-compat (a re-export shim is allowed per the convention "Preserve public API with a re-export shim only when many callers exist"). The exception classes have many callers, so the shim is justified.
- **Effort**: small

### F-C-029 — `transfer_dialog.py` characterization tests still reach through 6 retired-style property shims (sibling to log entry DI-2026-05-18-002)
- **Severity**: medium
- **Category**: test-inconsistency
- **File**: `tests/unit/ui/screens/test_transfer_dialog.py:74-75` (and `test_transfer_dialog_enhanced.py:49`, plus 70+ references in `test_transfer_dialog_characterization.py`)
- **Symbol**: `dialog._current_source = ...`, `dialog._current_target = ...`, `dialog._row_data`, `dialog._filter_empty`, etc.
- **Source refactor**: PROJ-437 Phase 4 (back-compat property shims acknowledged as deferred)
- **What survived**: Three test files still write through the dialog-level property shims rather than the canonical view-model state. The single discovered-issue log entry calls this out at a high level; this finding pins the **concrete test sites** that have to change to enable the shim deletion.
- **Why it's a problem**: PROJ-437 Phase 4 explicitly recorded this as a deferred follow-up; the discovered-issues log entry estimated "~10-15 mechanical edits." Verified count: ~6 production-side property shims × ~70 test references = on the lower end of that estimate.
- **Suggested action**: Mechanical sweep: `dialog._row_data` → `dialog.view_model.row_data`, `dialog._current_source` → `dialog.view_model.current_source`, etc. Same recipe in 3 test files.
- **Effort**: tiny-to-small

### F-C-030 — `IShipInstance` / `IFacility` / `IEmpire` protocols still use legacy `Dict[]` / `List[]` / `Optional[]` annotations
- **Severity**: low
- **Category**: polish
- **File**: `game/core/protocols/strategy_domain.py:8`, `strategy_entities.py:8`, `boundary.py:7`, `combat.py:3`, `persistence.py:3`, `common.py:14`, `registry.py:3`
- **Symbol**: protocol-module top-level `from typing import ... Dict, List, Optional, FrozenSet, Tuple`
- **Source refactor**: pre-PEP-604 codebase migration
- **What survived**: 7 of the 9 `game/core/protocols/*.py` modules still import `Dict`/`List`/`Optional` from `typing` and use them throughout. Convention says "Do not introduce legacy `Optional[int]`, `List[int]`, or `Dict[str, T]` in new code" — existing code is grandfathered, but every time these protocols are touched the new edits add to the inconsistent style.
- **Why it's a problem**: The protocol surface is the *most-imported* layer (every layer above core consumes it). Drift between protocol annotations and the rest of the codebase's modern syntax is a constant friction point in code review.
- **Suggested action**: Single-shot mechanical rewrite: `Dict[K,V]` → `dict[K,V]`, `List[X]` → `list[X]`, `Optional[X]` → `X | None`, etc. Add `from __future__ import annotations` where needed. ~7 files, mostly find-and-replace.
- **Effort**: small

---

Additional minor findings observed during the scan but not promoted to entries (kept under the cap of ~30):

- `game/ui/screens/strategy_renderer.py` re-exports `WARP_POINT_ROTATION_SPEED` "for back-compat with `test_strategy_renderer_animation.py`" (lines 17, 51) — sibling of F-C-005.
- `game/ui/screens/race_setup/__init__.py:21` and `screen.py:13` carry an explanatory comment about the deleted `race_setup_screen.py` re-export shim — purely documentary, no code residue.
- `game/ui/screens/new_game_setup_controller.py:159` and `:232` carry PROJ-392 "static shim removed" comments — purely documentary.
- Multiple files carry `tkinter_utils.py`-style `except Exception` blocks with extensive intentional-reason comments — all conform to convention; not residue.
- `tests/integration/data/test_intrinsic_registries_coverage.py:21,61` skip when JSON files are absent — same wallpaper-pattern as F-C-021/F-C-022 but at one site each.
