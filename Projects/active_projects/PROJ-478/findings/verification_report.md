# PROJ-478 — Verification Report (P0 tier)

**Source review:** `Reviews/results/2026-05-20_210550_test-review/`
**Run date:** 2026-05-20
**Priority tier:** P0 (CAT-1 Trivial Pass, CAT-2 Tests Nothing Real, CAT-3 Dead Test Code)
**Batch summary:** 44 verified / 9 needs-rework / 0 rejected / 5 out-of-scope out of 58 OpenCode CONFIRMED candidates for this tier.

The per-shard re-verification reports under `.agent_reports/2026-05-20_210550_test-review/` (15 files: `verification_w1_s01.md` through `verification_w6_cross_shard.md`) capture all CAT-1 / CAT-2 / CAT-3 verdicts; the tables below extract the subset that affects this project.

## Verified

| id | category | severity | file | test_name | suggestion |
|----|----------|----------|------|-----------|------------|
| S01-F001 | CAT-2 | CRITICAL | tests/unit/ui/screens/test_workshop_screen.py | event_router lambda | Delete |
| S01-F005..F013 | CAT-2 | CRITICAL | tests/unit/ui/screens/test_workshop_screen.py | 9 bypass-init / lambda-replacement tests | Delete |
| S02-F001 | CAT-1 | CRITICAL | tests/unit/builder/test_ship_loading.py | test_all_ships_match_expected_stats | Add `assert len(ship_files) >= 1` |
| S02-F003 | CAT-1 | CRITICAL | tests/unit/builder/test_bulk_add.py | test_bulk_add_success | Add component-identity assert |
| S02-F009 | CAT-1 | MAJOR | tests/unit/strategy/consumable_management_engine/conftest.py | dead-fixture conftest | Delete or have sibling consume |
| S02-F021 | CAT-2 | MAJOR | tests/unit/ui/screens/test_strategy_ui_tooltips.py | exact keybinding strings | Use injected bindings |
| S02-F023 | CAT-1 | CRITICAL | tests/integration/strategy/test_fleet_navigation_consistency.py | test_already_at_destination_consistency | Assert location, not order-queue internals |
| S03-F018 / F019 / F020 | CAT-1 | CRITICAL | tests/unit/ui/screens/test_strategy_widgets.py | 3 import-smoke tests | Delete |
| S04-F001 | CAT-1 | CRITICAL | tests/unit/strategy/engine/test_superweapon_event_payloads.py | empty-body test | Delete |
| S04-F002 | CAT-1 | CRITICAL | tests/unit/strategy/test_galaxy_state_encapsulation.py | empty-frozenset loop | Delete |
| S04-F003 | CAT-2 | CRITICAL | tests/regression/test_panel_full_open_benchmark.py | 2 zero-assert benchmarks | Move to profiling/ |
| S07-F009 | CAT-1 | CRITICAL | tests/unit/simulation/combat/test_fleet_aura_cache.py | _providers_dirty hasattr | Delete |
| S09-F005 | CAT-3 | MAJOR | tests/unit/ui/screens/test_build_queue_screen_lifecycle.py | 4 issue17 tests w/ _spy_invalidate | `@pytest.mark.skip` |
| S10-F019 | CAT-2 | MAJOR | tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py | 10 doc-linting tests | Move to tests/static_guards/ |
| S11-F001 | CAT-1 | CRITICAL | tests/unit/workshop/test_workshop_viewmodel_public_api.py | 9 isinstance(property) tests | Delete |
| S11-F002 | CAT-1 | CRITICAL | tests/unit/workshop/test_workshop_viewmodel_public_api.py | callable(method) tautology | Delete |
| S11-F003 | CAT-1 | CRITICAL | tests/unit/ui/screens/test_strategy_renderer_public_api.py | 7 structural tests | Delete |
| S11-F004 | CAT-1 | CRITICAL | tests/unit/core/test_role.py | 4 dataclass equality tests | Delete |
| S11-F005 | CAT-1 | CRITICAL | tests/unit/strategy/data/test_colony_yard_registries.py | hasattr fixture test | Delete |
| S12-F001 | CAT-1 | CRITICAL | tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py | assert True | Delete |
| S13-F004 | CAT-3 | MINOR | tests/unit/ui/test_race_summary_panel.py | empty TestCallbackIntegration class | Delete class |
| S13-F020 | CAT-1 | CRITICAL | tests/unit/strategy/combat/test_post_battle_hook_builder.py | test_build_hook_threads_mine_groups_and_engine_ref | Add behavior assertions |
| S13-F021 | CAT-1 | CRITICAL | tests/unit/tools/test_codex_project_config.py | validates external .codex/config.toml | Move to tests/tooling/ |
| S14-F001 | CAT-1 | CRITICAL | tests/unit/ui/screens/test_event_log_sidebar.py | test_event_log_sidebar_class_exists | Delete |
| S14-F003 | CAT-1 | MINOR | tests/unit/ui/screens/test_galaxy_test_screen.py | constants validation isinstance | Evaluate (keep or delete) |
| S15-F001 | CAT-1 | CRITICAL | tests/unit/ui/panels/test_planet_report_panel.py | _resource_grid_items self-fulfilling | Delete |
| S15-F002 | CAT-1 | CRITICAL | tests/unit/ui/screens/test_keybindings_scene.py | update no-assertion | Delete |
| S15-F003 | CAT-1 | CRITICAL | tests/unit/ui/screens/test_keybindings_scene.py | draw no-assertion | Delete |

## Needs Rework

| id | original suggestion | Claude's adjusted suggestion | rationale |
|----|---------------------|------------------------------|-----------|
| S01-F002 | Delete test (CAT-2) | Rewrite to call real `save_ship()` or delete | Test patches phantom method `_save_ship`; the underscore-prefixed name does not exist in production but `save_ship` (no underscore) does. Deleting drops coverage of a real flow. |
| S01-F003 | Delete test (CAT-2) | Rewrite to call real `load_ship()` or delete | Same pattern: phantom `_load_ship` vs real `load_ship`. |
| S01-F004 | Delete test (CAT-2) | Rewrite to call real `on_select_target_pressed()` or delete | Same pattern: phantom `_on_select_target_pressed` vs real `on_select_target_pressed`. |
| S02-F022 | Delete test (CAT-2) | Move to `tests/static_guards/` or `tests/projects/` | Tests serve a valid purpose (agent skill metadata validation) but are mis-located in `tests/unit/`. |
| S07-F003 | Delete test (CAT-1) | Replace with extract_outcome integration test that propagates `replay_id` through BattleResult → COMBAT_RESOLVED | Original is hasattr + None-default, but the underlying invariant (`replay_id` propagation) is real and worth keeping. |
| S08-F007 | Delete test (CAT-2) | Construct real `ResearchTreeScene` and assert `detect_cycles` is called as `__init__` side effect | The test's intent is valid; only the tautological implementation (mock calls itself then asserts) is broken. |
| S09-F005 | Add `@pytest.mark.skip` (Phase 1 original) | `@pytest.mark.skip(reason="PROJ-410 Phase 2 pending")` on 4 affected tests (3 helper + 1 direct call line 1534) | Verification confirmed 4 tests are affected, not the 3 the original suggestion mentioned. |
| S12-F002 | Delete test (CAT-1) | Reclassify as CAT-3 regression guard; keep test, drop CAT-1 flag | `assert not hasattr(module, "create_default_turn_engine")` CAN fail if the symbol is re-added — valid deletion guard, not trivial pass. |
| S13-F021 | Delete (or relocate) | Move to `tests/tooling/`, do not delete | Validates external `.codex/config.toml`; loss of this test reduces ability to detect config drift. |

## Rejected

(No P0-tier items were rejected.)

## Out of Scope

| id | claim | reason for not acting |
|----|-------|------------------------|
| S03-F003 | test_ship_component_manager_di.py:13-17 — `assert not hasattr` test for deleted symbol | `ast_guard_intentional` (PROJ-252 Phase-3 deletion guard) |
| S10-F002 / F003 / F004 | conftest files flagged CAT-3 with no test fns | `conftest_advisory` per SUMMARY caveat #5 (conftest files are expected to have only fixtures) |
| S10-F020 / F021 | test_no_carried_items_proxy.py / test_no_commands_specs_module.py — CAT-2 file-existence guards | `ast_guard_intentional` (PROJ-436 Phase 9, PROJ-371 Phase 2) |
| S12-F009 | test_colors.py constants validation | `conftest_advisory` (already correctly excluded by rubric) |
| S12-F016 | test_fleet_group_kind.py CAT-3 adj | `ast_guard_intentional` (already correctly excluded by rubric) |
