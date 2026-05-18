# Phase 3: Triage remaining `tests/unit/strategy/data/` failures

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** `tests/unit/strategy/data/*` (post-Phase-1/2 residual failures)

**Objective:** Resolve the long-tail failures in `tests/unit/strategy/data/` (~26 expected per PROJ-436 Phase 2 baseline, count to be refreshed from Phase 0 ledger). One-by-one or per-cluster classification + fix.

---

## Tasks (authored at phase start)

Cluster the remaining failures by file, then commit per cluster. Expected files likely involved (per PROJ-436 Phase 2 audit):
- `test_fleet_consumable_aggregator.py` — `TypeError: '<=' not supported between instances of 'MagicMock' and 'int'` — likely a mock-shape issue.
- `test_planet_classification_logic.py` — `TestClassificationConfigLoader::test_all_planet_types_have_rules`.
- `test_storm.py` — `TestStarSystemStormIntegration::test_star_system_from_dict_skips_invalid_storm_gracefully`.
- Other files surfaced by Phase 0 ledger.

For each: classify as (a) now passing, (b) fix test, (c) fix production, (d) delete. Commit per cluster.

---

## Phase Completion Checklist
- [ ] `pytest tests/unit/strategy/data/ -q -n 4` returns zero failures
- [ ] Sharded suite still green (visible-tests baseline preserved)
- [ ] Hidden directory now green by direct invocation — ready for Phase 4 config flip
- [ ] `plan.md` + `phase_state.json` updated
