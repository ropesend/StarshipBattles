# PROJ-478 File Manifest

> Generated from `Reviews/results/2026-05-20_210550_test-review/` after independent verification.
> Every file appears in at least one `phase_N_checklist.md`; every checklist file appears here.

## Files

| File | Type | Notes |
|------|------|-------|
| tests/unit/ui/screens/test_workshop_screen.py | Test | Phase 2 — delete 10 bypass-init/lambda CAT-2 tests, rewrite 3 phantom-method tests |
| tests/unit/workshop/test_workshop_viewmodel_public_api.py | Test | Phase 1 — delete 10 CAT-1 tests (callable + 9 isinstance property) |
| tests/unit/ui/screens/test_strategy_renderer_public_api.py | Test | Phase 1 — delete 7 CAT-1 structural tests |
| tests/unit/core/test_role.py | Test | Phase 1 — delete 4 CAT-1 dataclass equality tests |
| tests/unit/strategy/data/test_colony_yard_registries.py | Test | Phase 1 — delete 1 CAT-1 hasattr test |
| tests/unit/ui/screens/test_strategy_widgets.py | Test | Phase 1 — delete 3 CAT-1 import-smoke tests |
| tests/unit/ui/screens/test_keybindings_scene.py | Test | Phase 1 — delete 2 CAT-1 no-assertion tests |
| tests/unit/ui/panels/test_planet_report_panel.py | Test | Phase 1 — delete 1 CAT-1 self-fulfilling test |
| tests/unit/simulation/combat/test_fleet_aura_cache.py | Test | Phase 1 — delete 1 CAT-1 hasattr test |
| tests/unit/simulation/test_battle_outcome_replay_id.py | Test | Phase 1 — rewrite CAT-1 as integration test (NEEDS_REWORK) |
| tests/unit/builder/test_ship_loading.py | Test | Phase 1 — add minimum-files guard to vacuous-pass test |
| tests/unit/builder/test_bulk_add.py | Test | Phase 1 — add component-identity assertion |
| tests/unit/strategy/consumable_management_engine/conftest.py | Test | Phase 1 — delete dead-fixtures conftest (52 LOC) |
| tests/integration/strategy/test_fleet_navigation_consistency.py | Test | Phase 1 — rewrite to assert location, not order-queue internals |
| tests/unit/strategy/engine/test_superweapon_event_payloads.py | Test | Phase 1 — delete empty-body CAT-1 test |
| tests/unit/strategy/test_galaxy_state_encapsulation.py | Test | Phase 1 — delete empty-frozenset CAT-1 test |
| tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py | Test | Phase 1 — delete `assert True` CAT-1 test |
| tests/unit/ui/screens/test_event_log_sidebar.py | Test | Phase 1 — delete import-then-assert CAT-1 test |
| tests/unit/ui/screens/test_galaxy_test_screen.py | Test | Phase 1 — evaluate constants-validation guard |
| tests/unit/strategy/combat/test_post_battle_hook_builder.py | Test | Phase 1 — rewrite CAT-1 hook callable assertion with real behavioral checks |
| tests/unit/tools/test_codex_project_config.py | Test | Phase 1 — relocate to tests/tooling/ (validates external `.codex/config.toml`) |
| tests/unit/ui/screens/test_strategy_ui_tooltips.py | Test | Phase 2 — replace exact-keybinding string asserts with injected bindings |
| tests/unit/agent_coordination/test_codex_consult_skills.py | Test | Phase 2 — relocate to tests/static_guards/ (CAT-2 NEEDS_REWORK) |
| tests/unit/agent_coordination/test_codex_interagent_discussion_skills.py | Test | Phase 2 — relocate to tests/static_guards/ (CAT-2 doc-linting) |
| tests/regression/test_panel_full_open_benchmark.py | Test | Phase 2 — relocate to profiling/, 2 CAT-2 benchmarks |
| tests/unit/research/research_scene/test_interaction.py | Test | Phase 2 — rewrite tautological detect_cycles test (CAT-2 NEEDS_REWORK) |
| tests/unit/ui/test_race_summary_panel.py | Test | Phase 3 — delete empty TestCallbackIntegration class |
| tests/unit/ui/screens/test_build_queue_screen_lifecycle.py | Test | Phase 3 — add @pytest.mark.skip to 4 issue17 tests pending PROJ-410 Phase 2 |
