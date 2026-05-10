# Agent 2 Report: CAT-12 Reference-Value Pattern & CAT-11 Fragile Assertions

## 1. CAT-12 Reference-Value Pattern Audit

### Task 5.18: test_resupply_engine.py — Hardcoded reference values 200.0/40.0
- **Docstring quality:** PRESENT+INFORMATIVE
- **Derivation traceability:** Can re-derive from production. Simple arithmetic: 240 fuel / (10 + 2) cost/hex = 20 hex range; Ship A = 10 * 20 = 200.0; Ship B = 2 * 20 = 40.0. Cites validation date (2026-05-03) and production component (ResupplyEngine). Docstring explicitly warns: "Updating these values without re-validating production is a regression signal."
- **Brittleness assessment:** LOW. The equalization rule is structurally simple (divide available fuel by combined consumption rate). If the engine's allocation algorithm changes (e.g., priority-based instead of equal-range), the derivation becomes invalid and the test fails — which is exactly the desired regression signal.
- **Snippet:** `tests/unit/strategy/engine/test_resupply_engine.py:486-532`
```python
def test_fuel_distributed_to_equalize_range(self):
    """... Derivation (validated against ResupplyEngine 2026-05-03):
      - 240 fuel available; combined cost 10+2=12/hex -> max equalized
        range = 240/12 = 20 hexes.
      - Ship A allocation = cost(10) * range(20) = 200.0
      - Ship B allocation = cost(2)  * range(20) =  40.0
    Total: 240.0. Updating these values without re-validating production
    is a regression signal — the engine has changed the equalization rule.
    """
    ...
    assert a_call_args[0][1] == pytest.approx(200.0)
    assert b_call_args[0][1] == pytest.approx(40.0)
```

---

### Task 5.19: test_colony_output.py — Hardcoded reference value -0.005596103475344202
- **Docstring quality:** PRESENT+INFORMATIVE
- **Derivation traceability:** Partially re-derivable. The docstring walks through the formula step-by-step (effective_r, K_eff, logistic_factor, logistic_term, decline_term, net), but uses ~ approximations (~0.94 habitability, ~9_400 K_eff, ~0.9787 logistic_factor, ~0.004404 logistic_term) that do not decompose cleanly to the precise final value checked via `pytest.approx(rel=1e-9)`. The intermediate habitability score depends on `calculate_habitability()` (`game/strategy/formulas/habitability.py:99`), which weighs multiple planet attributes against race preferences — the ~0.94 figure is not derived inline. A maintainer facing a test failure from a production change to `score_planet_for_race`, `DECLINE_RATE`, or the logistic formula itself will struggle to recompute the exact expected value from the docstring approximations alone.
- **Brittleness assessment:** MEDIUM-HIGH. The test depends on 4 sub-formulas (habitability scoring, K_eff capping, logistic factor, decline rate). The docstring's derivation precision (3-4 significant digits) is lower than the assertion precision (1e-9 relative tolerance). If any sub-formula changes, the test fails — which is correct — but the maintainer cannot re-derive the precise new value without re-running the computation manually or temporarily reverting to the old code. The docstring should include the key intermediate values at assertion-precision, or the assertion tolerance should match the docstring's precision.
- **Snippet:** `tests/unit/strategy/formulas/test_colony_output.py:385-409`
```python
def test_partial_food_and_low_happiness_matches_hand_computation(self):
    """...Derivation (do not recompute in test body):
      - habitability ~ 0.94 for default-prefs human on Earth-like
      - K_eff ≈ 9_400. logistic_factor = 1 - 200/9_400 ≈ 0.9787.
      - effective_r = 0.03 * 0.5 = 0.015.
      - logistic = 0.015 * 0.9787 * 0.3 ≈ 0.004404.
      - decline  = -0.02 * (1-0.5) = -0.01.
      - net      ≈ -0.005596.
    """
    ...
    assert rate == pytest.approx(-0.005596103475344202, rel=1e-9)
```

---

### Task 5.23: test_fleet_report_filters.py — Hardcoded reference 0.7667
- **Docstring quality:** PRESENT+INFORMATIVE
- **Derivation traceability:** Can re-derive from production. Simple arithmetic: `(1.0 + 0.5 + 0.8) / 3 ≈ 0.7666666...` Cites validation date (2026-05-03) and production function (`calculate_fleet_stats`).
- **Brittleness assessment:** LOW. Average HP percent is a straightforward arithmetic mean. The tolerance (`abs(... - 0.7667) < 0.01`) is appropriately loose for floating-point comparison. Minor concern: the tolerance is looser than strictly necessary for this calculation (0.01 vs the actual rounding delta of ~0.000033), which could mask a production rounding change that introduces sub-1% drift. However, for a UI stat display, this margin is negligible and intentional.
- **Snippet:** `tests/unit/ui/screens/test_fleet_report_filters.py:117-134`
```python
def test_average_hp_calculation(self):
    """... PROJ-323 Task 5.23: hardcoded reference 0.7667 (validated against
    calculate_fleet_stats 2026-05-03). For inputs (1.0, 0.5, 0.8) the
    production avg is (1.0 + 0.5 + 0.8) / 3 ≈ 0.7666666...
    """
    ...
    assert abs(stats['avg_hp_percent'] - 0.7667) < 0.01
```

---

### Task 5.1: test_strategy_game_state_manager.py — Counter pattern (itertools.count)
- **Docstring quality:** PRESENT+INFORMATIVE
- **Derivation traceability:** N/A (not a reference-value pattern; this is an internal-call-count → outcome assertion refactor).
- **Brittleness assessment:** LOW. The pattern change is sound: replaces `mock_pft.call_count == 2` (asserting an internal mock detail) with `completed == 2` (asserting the observable outcome). The `itertools.count` side_effect trips the cancel flag after the 2nd `process_full_turn` call, so the loop completes 2 iterations before checking the flag — this is correct. Risk: the flag check ordering depends on the loop structure in `run_n_turns`. If that structure changes (e.g., flag checked before process_full_turn), only 1 iteration would complete. This is test-design intent, not a flaw — it IS asserting on the production loop behavior.
- **Snippet:** `tests/unit/ui/screens/test_strategy_game_state_manager.py:278-304`
```python
def test_stops_on_cancel_after_current_turn(self):
    """... PROJ-323 Task 5.1: use itertools.count Counter for tick-tracking
    side_effect, assert on outcome (completed) rather than internal
    mock call counts.
    """
    from itertools import count
    ...
    counter = count(1)
    def trip_cancel_after_two(*args, **kwargs):
        if next(counter) == 2:
            screen.dev_run_cancel_requested = True
    ...
    completed = manager.run_n_turns(10)
    assert completed == 2  # Outcome assertion
```

---

### Task 5.12: test_builder_validation.py — Set comprehension issubset
- **Docstring quality:** PRESENT-WEAK (single-line comment: `# PROJ-323 Task 5.12: pre-compute id-set once instead of two any(...) scans.`)
- **Derivation traceability:** N/A (not a reference-value pattern; structural assertion improvement).
- **Brittleness assessment:** LOW. This IS an improvement over the original pattern. Before: two separate `any(c.id == ...)` scans could fail to detect one-component-in-group scenarios (if only one of the two exclusive components was present, both `any()` calls would return False, passing the test). After: `{"group_a_1", "group_a_2"}.issubset(...)` correctly asserts that BOTH exclusive components cannot be present simultaneously — a stricter, more correct invariant. The regression signal is strengthened, not weakened.
- **Snippet:** `tests/unit/builder/test_builder_validation.py:128-132`
```python
inner_component_ids = {c.id for c in self.ship.layers[LayerType.INNER].components}
assert not {"group_a_1", "group_a_2"}.issubset(inner_component_ids), (
    "Should not allow multiple components from same exclusive group"
)
```

---

## 2. CAT-11 Fragile-Assertion Replacement Audit

### Task 4.2: test_deprecated_code_removed.py
- **Original assertion pattern:** Already `assert total <= EXPECTED_X_COUNT` — a soft upper-bound assertion. The task description (S02-CAT11-001) proposed converting to "advisory soft assertions (e.g., pytest.skip, pytest.warns)", but the implementer correctly identified this as a no-op. The existing test IS already soft in the sense of using an adjustable threshold (`<=`), but it IS hard in the sense of using `assert` (not `warn` or `skip`). The test will fail the build if `RegistryManager.instance()` usage increases.
- **Current assertion pattern:** Same `assert total <= self.EXPECTED_GAME_COUNT` with a descriptive failure message that tells the developer to verify necessity before bumping the constant. Two settings: `EXPECTED_GAME_COUNT = 0` (production code should have zero `.instance()` calls) and `EXPECTED_TESTS_COUNT = 13` (known string occurrences in test commentary).
- **Regression signal preserved?** YES. The test catches increases. The assertion fires and fails the build. The developer must deliberately update the constant to make the build pass, which forces at least a cursory review of the new occurrence.
- **Risk of silent erosion:** LOW. The erosion vector is a developer bumping `EXPECTED_GAME_COUNT` without adding a shim guard to block the `.instance()` pattern in production code — but this is no different from any configurable threshold. The error message guides them: "If this is truly necessary, update EXPECTED_GAME_COUNT in this test." The alternative proposed in the task (converting to `pytest.skip`) would have been *worse* — it would never fail the build and would silently accept regression.
- **Analysis:** Task 4.2 was correctly handled as a no-op. The `assert total <= EXPECTED_X_COUNT` pattern with a descriptive failure message is the right balance: it catches regressions while providing clear guidance for legitimate increases. Converting to `pytest.skip` or `pytest.warns` would have destroyed the regression-detection signal entirely, since the test file's primary value is as a CI gate against reintroducing the deprecated `.instance()` singleton pattern. The design.md's description of "advisory soft assertions" (line 42) mischaracterizes this — the assertions are hard with soft thresholds, not soft assertions — but the implementation result is correct.

---

### Task 4.9: test_colonize_mission_handler.py — Duplicate key removal
- **Original assertion pattern:** A duplicate `'colony_pod'` key in `make_component_registry()` caused the second dictionary entry to silently overwrite the first. The first entry defined `'ColonizePlanet': True`; the second is unknown (was deleted). Tests that consumed this registry may have been operating on silently-overwritten data.
- **Current assertion pattern:** The duplicate key has been removed. The single `'colony_pod'` entry now has an unambiguous definition: `'abilities': {'ColonizePlanet': True}`. The `'gas_giant_colony_pod'` entry remains as a separate, distinct key.
- **Regression signal preserved?** PARTIAL-IMPROVED. This was test-data cleanup, not assertion cleanup. The regression signal was ambiguous before (which definition did the test intend to use?); it is now unambiguous. However, the change is purely in test-data setup, not in what is asserted. The actual assertions remain unchanged.
- **Risk of silent erosion:** LOW. No framework-level effect. This was a straightforward data-integrity fix.
- **Analysis:** This task should be classified as CAT-7 (test-data cleanup) rather than CAT-11 (fragile assertion replacement). It was bundled into Phase 4 opportunistically but has no bearing on assertion fragility. The removal is correct and the test continues to pass.

---

### Task 5.8: test_planet_physics.py — Split conditional assertions (Cross-category note)
- **Cross-reference:** Although categorized as CAT-12 (Phase 5), this task is structurally a CAT-11 concern — it replaced a single test with conditional `if` branches into two named tests with explicit assertions.
- **Original:** `test_atmosphere_retention` had conditional assertions (`if comp.get('H2', 0) < 1.0: ...`).
- **Current:** Split into `test_earthlike_planet_does_not_retain_h2` and `test_jupiterlike_planet_retains_h2`. The greenhouse effect conditional in `test_greenhouse_effect` was correctly kept (`if press > 10000: assert temp_atm > 300`) because it's opportunistic — the planet may legitimately not retain atmosphere under the given parameters.
- **Regression signal preserved?** YES. Each split test now fails independently with a named test title, making failure diagnosis immediate. The kept conditional is justified: it avoids false negatives when the test inputs happen to produce no atmosphere.
- **Snippet:** `tests/integration/strategy/test_planet_physics.py:31-54`

---

### Task 5.10: test_bug_13_weapons_report.py — Split assertions (Cross-category note)
- **Cross-reference:** Also CAT-12 but structurally similar to CAT-11 assertion splitting. Replaced `test_prioritization_logic` (conditional asserts on priority classes) with 3 tests: endpoints (priority 0), intermediate range (priority 2), accuracy threshold (priority 1).
- **Key design decision (Task 5.10, test_prioritization_accuracy_threshold_points_are_priority_one):** The accuracy-point test uses a defensive `all(...)` pattern over potentially empty lists — it does NOT assert that accuracy points exist. The docstring explains: "The shallow-falloff setup used here (accuracy_falloff=0.001, range=100) may not yield any accuracy threshold points; this test only asserts the priority invariant when they exist." This is a well-justified guard against false negatives from production changes to point-of-interest generation.
- **Regression signal preserved?** YES — strengthened. The old single test conflated 3 priority classes; failures were harder to triage. The new split tests surface the failing priority class immediately.

---

## 3. Findings Summary

| ID | Severity | Description |
|----|----------|-------------|
| FND-P2-001 | MEDIUM | **Task 5.19 precision mismatch**: Docstring derivation uses ~ approximations (~0.94, ~0.9787) but assertion uses `rel=1e-9` tolerance (-0.005596103475344202). A maintainer facing a formula-change failure cannot re-derive the precise expected value from the docstring alone. Recommend either adding intermediate values at assertion-precision to the docstring, or relaxing the assertion tolerance to match docstring precision (e.g., `rel=1e-5`). |
| FND-P2-002 | LOW | **Task 5.23 tolerance is over-generous**: `abs(... - 0.7667) < 0.01` for a value that should be ~0.7666667. The tolerance of 0.01 masks up to 1.3% drift in a pure arithmetic mean. Not a bug, but a maintainer should be aware this is looser than necessary. |
| FND-P2-003 | LOW | **Design.md stale reference**: `design.md:41` cites `test_projectile_manager.py` as the canonical CAT-12 reference-value example, but this file was deleted by PROJ-321 (confirmed: `deed107b8`). The design doc should reference an extant file (e.g., `test_resupply_engine.py` or `test_colony_output.py`). |
| FND-P2-004 | LOW | **Task 4.9 mis-categorized**: Duplicate key removal in `make_component_registry()` is test-data cleanup (CAT-7 territory), not a fragile-assertion replacement (CAT-11). No functional impact, but the categorization is misleading. |
| FND-P2-005 | LOW | **Task 4.2 design.md description mismatch**: `design.md:42` describes "converting hard count-based assertions to advisory soft assertions" as the pattern, but the actual implementation left hard `assert total <= EXPECTED_X_COUNT` in place. The implemented pattern is correct (hard assertion with adjustable threshold); the design doc description should be updated to avoid confusion. |
| FND-P2-006 | LOW | **Task 5.12 regression signal strengthened**: The `issubset` check is stricter than the original two `any()` scans — it correctly asserts mutual exclusion of both components. This is a net improvement beyond what the CAT-12 scope specified. |
| FND-P2-007 | INFO | **Reference-value pattern is fundamentally sound**: All three reference-value tasks (5.18, 5.19, 5.23) follow the correct pattern: (1) call production, (2) compare result to hardcoded reference, (3) provide derivation docstring. Production formula changes cause test failure — the desired regression signal. The brittleness risk is well-managed by the derivation docstrings, except for FND-P2-001. |
