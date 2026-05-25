# PROJ-499 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `tests/regression/modifier_ability_snapshots/conftest.py` | Test infrastructure | Modify `compare_snapshots()` (lines 139-173) to walk union of key sets; symmetric extra-key reporting |
| `tests/regression/modifier_ability_snapshots/test_compare_snapshots_strictness.py` | Test (NEW) | Phase 1 TDD test + Phase 4 negative guard |
| `tests/regression/snapshots/capital_missile_*.json` | Baseline data (18 files) | Re-shoot — bounded additive-key diff expected |
| `tests/regression/snapshots/crew_quarters_automation_*.json` | Baseline data (5 files) | Re-shoot — 4 PROJ-489 reshots already correct, the 0.00 baseline is stale |
| `tests/regression/snapshots/generator_efficiency_*.json` | Baseline data (4 files) | Re-shoot — 3 PROJ-489 reshots already correct, the 1.00 baseline is stale |
| `tests/regression/snapshots/laser_cannon_*.json` | Baseline data (7 files) | Re-shoot |
| `tests/regression/snapshots/railgun_*.json` | Baseline data (24 files) | Re-shoot |
| `tests/regression/snapshots/standard_engine_*.json` | Baseline data (6 files) | Re-shoot |
| `tests/regression/snapshots/thruster_*.json` | Baseline data (1 file) | Re-shoot |
| `Projects/active_projects/PROJ-499/findings/source_review.md` | Doc (NEW) | Phase 0 baseline-drift census |
| `Projects/active_projects/PROJ-499/findings/harness_survey.md` | Doc (NEW) | Phase 5 survey of other harnesses (already strict) |
| `tests/README.md` | Doc (modified) | Phase 5 — corrected stale "skip on first run" claim at lines 552-555; added PROJ-499 symmetric-comparator note |
| `Projects/projects_index.md` | Index | Updated PROJ-499 row status from `Planning` to `Awaiting Verification` |

## Files explicitly NOT touched

- `tests/infrastructure/deep_compare.py` — already symmetric
- `tests/infrastructure/state_snapshot.py` — delegates to deep_compare
- Any save/load roundtrip or golden-fixture harness — already strict (see design.md table)
- `tests/regression/modifier_ability_snapshots/conftest.py` `snapshot_full_component()` and the other writer-side helpers — compare-only hardening is sufficient
- `game/simulation/components/abilities/stat_keys.py` — production data; not modified
- `tests/regression/modifier_ability_snapshots/test_utility_modifiers.py` / `test_weapon_modifiers.py` — consumer tests; no changes needed once baselines are refreshed

## Conflict notes

- This project touches `tests/regression/snapshots/*.json` in bulk. Other projects that re-shoot baselines or change `snapshot_full_component()` will conflict — coordinate.
- The comparator edit at `conftest.py:139-173` is a contained 1-function change.
