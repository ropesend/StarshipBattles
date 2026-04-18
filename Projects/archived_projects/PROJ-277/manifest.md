# PROJ-277 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| `combat_lab/services/ab_battle_runner.py` | Production | NEW — ABBattleRunner service |
| `combat_lab/scenarios/ab_outcome.py` | Production | NEW — ABBattleOutcome DTO |
| `combat_lab/scenarios/templates.py` | Production | Refactor ComparisonScenario: delete `_run_baseline_battle` (L827), `_run_validation` override (L1120); add `build_baseline_spec` / `build_variant_spec` hooks; change `validate` signature |
| `combat_lab/services/scenario_run_helper.py` | Production | Dispatch ComparisonScenario to ABBattleRunner; non-ComparisonScenario unchanged |
| `combat_lab/scenarios/*_scenarios.py` | Production | Enumerate ComparisonScenario subclasses in Phase 5; migrate each `validate()` signature |
| `tests/unit/combat_lab/services/test_ab_battle_runner.py` | Test | NEW — unit tests for ABBattleRunner |
| `tests/unit/combat_lab/scenarios/test_comparison_scenario.py` | Test | Update/rewrite existing comparison scenario tests |
| `docs/guides/simulation_testing.md` | Doc | Add "Writing A/B Scenarios" section |
