# Validation Synthesis

## Per-Validator Tallies

| Validator | Claims | Confirmed | Downgraded | Rejected |
|-----------|--------|-----------|------------|----------|
| 1 (Core+Sim+AI) | 25 | 16 | 7 | 2 |
| 2 (Strategy) | 29 | 15 | 9 | 5 |
| 3 (UI) | 40 | 30 | 8 | 2 |
| 4 (Cross-domain) | 40 | 24 | 10 | 6 |
| **Total** | **134** | **85 (63%)** | **34 (25%)** | **15 (11%)** |

## Overclaim Patterns

### Most Common Overclaim Type: "Full File is Duplicate" When Only Partial Overlap Exists
- Validator 1 rejected claim 14 (component_getters/operations) -- substantial unique coverage existed
- Validator 2 rejected claim 12 (colonize_validator) -- high test-to-source ratio from edge cases, not duplication
- Validator 2 rejected claim 13 (TestEventQueries) -- claimed duplicate target file did not exist
- Validator 4 rejected claim 20 (production_rates unit vs integration) -- different concerns entirely

### Second Pattern: "Scaffold" Tests That Actually Guard Architectural Constraints
- Validator 1 rejected claim 12 (DI source-reading tests) -- these are architecture guard tests
- Validator 1 rejected claim 25 (formation integrity adapter tests) -- tests a documented bug fix
- Validator 2 rejected claim 26 (empire fleet ID tests) -- includes real serialization integration test
- Validator 2 rejected claim 28 (roman numerals) -- only test of to_roman() in the codebase
- Validator 3 rejected claim 25 (font constants) -- guards against silent rendering breaks

### Third Pattern: Reviewers Claiming Blanket File Removal When Partial Removal Is Appropriate
- Validator 2 downgraded claims 18-20 (DTO files) -- frozen tests removable but factory tests should stay
- Validator 2 downgraded claim 10 (battle_resolver) -- ~8 scaffold tests removable, ~6 contract tests should stay
- Validator 1 downgraded claim 3 (test_config.py) -- 4 of 6 tests removable, 2 should stay
- Validator 1 downgraded claim 16 (test_combat_ops.py) -- integration tests should stay, facade unit tests removable
- Validator 4 downgraded claim 11 (superweapon_handler_validation) -- "passes component_registry" tests are unique

## Cross-Validator Contradictions

### Session 5 Agent 5 vs Validator 4 on Repro Issues
Session 5 (strategy integration) agent recommended keeping nearly all repro tests as regression guards. Validator 4 (cross-domain) confirmed many as duplicates of proper unit tests now. Resolution: the validator's finding is more reliable since it verified specific duplicate targets exist.

### Session 3 Agent 2 vs Agent 5 on Battle State Viewer Tests
Both Agent 2 and Agent 5 of Session 3 flagged the battle_state_viewer test files. These were counted once in the final report (not double-counted). The validators confirmed all three files (test_json_diff.py, test_ui_logic.py, test_viewer_ui.py) test reimplemented local logic, not production code.

### No True Contradictions Between Validators
The four validators were largely consistent. Where they overlapped (e.g., superweapon operations tests flagged by both validator 3 and validator 4), their verdicts agreed.

## Key Bugs Found During Validation

1. **Shadowed TestHullAutoEquip** (validator 1, claim 9) -- first class silently never runs
2. **Shadowed TestGameStateQueries** (validator 2, claim 14) -- first class silently never runs
3. **`assert X or True` no-op assertions** (validator 2, claims 16-17) -- tests that can never fail
4. **Potential `json.JSONDecodeError` NameError** (session 2, agent 4) -- `json` module not imported but `json.JSONDecodeError` referenced in except clause
5. **Budget reduction does not clamp allocations** (session 4, agent 1) -- potential research system bug
