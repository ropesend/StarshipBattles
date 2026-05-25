# PROJ-499: Harness Survey

**Date:** 2026-05-23
**Reviewer:** Claude orchestrator + Codex planning consult + Codex mid-project audit
**Sources:**
- Codex planning consult at `AgentCoordination/Scratchpad/Consult/20260523T125809Z_plan-snapshot-harness-fix/response.md` findings 1-2 (response.md:13-15)
- Codex mid-project audit at `AgentCoordination/Scratchpad/Consult/20260523T131241Z_audit-PROJ-499/response.md` (perf bench additions + galaxy_repro_baseline addition)
- Re-verified by Claude (Phase 0 + Phase 5) via `Grep compare_snapshots|deep_compare|json.load|baseline\.json` over `tests/`.

## Goal

Confirm that the asymmetric "iterate expected-only" comparator gap exists ONLY in `tests/regression/modifier_ability_snapshots/conftest.py:147-173` and not in other snapshot, save/load, or golden-fixture harnesses across the repo.

## Survey results

| Harness | Symmetric / strict? | Evidence (`file:line`) | Notes |
|---------|--------------------|----------------------|-------|
| `tests/regression/modifier_ability_snapshots/conftest.py` `compare_snapshots()` | **NO — this is the gap** | `conftest.py:147-156` | Iterates `for key in expected_val` only. PROJ-499 fixes this. |
| `tests/infrastructure/deep_compare.py` `deep_compare()` | YES (unions key sets, emits extra-key diffs) | `deep_compare.py:77-106` | Used by all save/load and QA harnesses. |
| `tests/infrastructure/state_snapshot.py` `compare_game_states()` | YES (delegates to `deep_compare`) | `state_snapshot.py:38-66` | QA save/load round-trip verifier. |
| `tests/integration/save_load/conftest.py` + `test_full_roundtrip.py` | YES (deep_compare) | `conftest.py:68-108`, `test_full_roundtrip.py:81-100` | Full save/load roundtrip. |
| `tests/integration/strategy/test_save_round_trip.py` | YES (strict dict equality) | `test_save_round_trip.py:222-231` | Strategy-layer save roundtrip. |
| `tests/integration/strategy/test_galaxy_reproducibility.py` | YES (strict equality) | `test_galaxy_reproducibility.py:40-45` | Deterministic galaxy gen. |
| `tests/unit/simulation/entities/test_ship_stats_golden.py` | YES (explicit key-set equality) | `test_ship_stats_golden.py:261-275`, `test_ship_stats_golden.py:315-325` | Golden ship-stats test. |
| `tests/integration/strategy/test_golden_fixture_field_coverage.py` | YES (explicit emitted-keys equality) | `test_golden_fixture_field_coverage.py:65-86` | Field-coverage guard. |
| `tests/performance/bench_turn_processing.py` | N/A — numeric thresholds, not dict walks | `bench_turn_processing.py:206-272` | Captures min-of-N timing baseline; compares total + per-phase numeric ratios against a 5x blow-up ceiling. No structural dict comparison. Unaffected by PROJ-499. |
| `tests/performance/bench_galaxy_planet_star.py` | N/A — numeric thresholds, not dict walks | `bench_galaxy_planet_star.py:143-206` | Same model — per-bench ratio against tolerance; no dict-key comparison. Unaffected. |
| `tests/fixtures/strategy/galaxy_repro_baseline.py` | N/A — golden fixture writer/loader, comparison is in test_galaxy_reproducibility / test_golden_fixture_field_coverage above | `galaxy_repro_baseline.py:247-249` | Just `json.load`; comparator logic lives in the tests above (already strict). |
| `tests/regression/modifier_ability_snapshots/test_allowance_matrix.py` (PROJ-498) | N/A — boolean intersection-rule pair check, not a snapshot comparator | `test_allowance_matrix.py:109-128` | Parametrized over `(modifier, component)` pairs; asserts `service.is_modifier_allowed(...) is expected_bool`. Loads raw `data/modifiers.json` and `data/components.json` (not baseline JSON). Unaffected by PROJ-499. |

## Conclusion

Only the modifier-ability snapshot harness `compare_snapshots()` has the asymmetric gap. **No propagation of PROJ-499's fix to other harnesses is required.** Phase 5 documents this; no code changes elsewhere.

PROJ-499 only modifies `tests/regression/modifier_ability_snapshots/conftest.py`. No other harness needs the same treatment.

If future work introduces a NEW JSON-baseline harness, the maintainer must explicitly choose strict (union-of-keys) comparison — and ideally reuse `deep_compare()` rather than rolling another asymmetric walker.

## Independent verification commands

For future agents wanting to re-verify the survey:

```
Grep -r "compare_snapshots" tests/
Grep -r "deep_compare" tests/
Grep -r "json.load" tests/regression/
```

(Phase 0 Task 0.2 re-runs these and updates this file with any new harnesses found.)
