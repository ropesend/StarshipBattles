# Test Suite Audit — Summary (Verified)

## Run Info
- Date: 2026-05-20 21:05:50
- Seed: 2026-05-20
- Shards: 16
- Total test files reviewed: 1,476
- Total LOC reviewed (est): 391,324
- Phase 1 claims: 305 → **Verified: 322** | Disputed: 22 | Inconclusive: 5

> Note: Verified count (322) exceeds Phase 1 claims (305) because cross-shard claims (DUP-*, HLP-*) were independently verified and counted in their respective shard reports.

## Verified Findings by Category

| Category | CRITICAL | MAJOR | MINOR | Total |
|----------|----------|-------|-------|-------|
| CAT-1 Trivial Pass | 34 | 2 | 0 | **36** |
| CAT-2 Tests Nothing Real | 15 | 3 | 0 | **18** |
| CAT-3 Dead Test Code | 1 | 1 | 2 | **4** |
| CAT-4 Duplicate Testing | 0 | 16 | 2 | **18** |
| CAT-5 Fixture Bloat | 0 | 15 | 4 | **19** |
| CAT-6 Mocking Brittleness | 0 | 25 | 3 | **28** |
| CAT-7 Sleep/Latency | 0 | 4 | 0 | **4** |
| CAT-8 Needless Complexity | 0 | 6 | 32 | **38** |
| CAT-9 Simplification | 0 | 1 | 21 | **22** |
| CAT-10 Parameterize | 0 | 0 | 88 | **88** |
| CAT-11 Fragile Assertion | 0 | 6 | 7 | **13** |
| CAT-12 Logic-Heavy | 0 | 0 | 24 | **24** |
| CAT-13 Tests Targeting Deleted Code | 10 | 0 | 0 | **10** |
| **Totals** | **60** | **79** | **183** | **322** |

## Top 20 Highest-Impact Verified Findings
Ordered by estimated LOC affected × severity weight (CRITICAL=10, MAJOR=5, MINOR=1).

| # | ID | Category | Severity | File | LOC | Score | Title |
|---|-----|----------|----------|------|-----|-------|-------|
| 1 | S07-F012 | CAT-9 | MINOR | test_engine_validation.py | 280 | 280 | 12 near-identical engine validation test classes |
| 2 | S06-F005 | CAT-10 | MINOR | test_superweapon_order_pop_matrix.py | 260 | 260 | 10 superweapon tests identically parametrized over 6 abilities |
| 3 | S07-F011 | CAT-9 | MINOR | test_strategy_input_handler_transfer.py | 230 | 230 | 3 identical mode-test classes |
| 4 | S08-F004 | CAT-5 | MAJOR | test_battle_state_serialization.py | 200 | 1000 | 9 function-scoped heavy fixtures |
| 5 | S08-F006 | CAT-6 | MAJOR | test_ship_detail_panel.py | 200 | 1000 | 23 tests bypass __init__ |
| 6 | S07-F005 | CAT-6 | MAJOR | test_superweapon_order_processor.py | 200 | 1000 | Deep patching of internal validator method |
| 7 | S03-F012 | CAT-10 | MINOR | test_fleet_menu_items.py | 200 | 200 | 10+ near-identical FMS row tests |
| 8 | S03-F011 | CAT-8 | MINOR | test_ai_controller_unit.py | 187 | 187 | TestNavigateTo 12 repeated setup patterns |
| 9 | S01-F004 | CAT-2 | CRITICAL | test_workshop_screen.py | ~150 | 1500 | 13 phantom-method / bypass-init tests |
| 10 | S02-F008 | CAT-10 | MINOR | test_engine_event_emission.py | 150 | 150 | 9 event assertion tests with identical pattern |
| 11 | S08-F002 | CAT-10 | MINOR | test_ship_io.py | 150 | 150 | 7 near-identical round-trip tests |
| 12 | S02-F007 | CAT-4 | MAJOR | test_propulsion_ability_bindings.py | 100 | 500 | Duplicate patterns across 3 propulsion ability classes |
| 13 | S04-F008 | CAT-6 | MAJOR | test_empire_build_queue_window.py | 100 | 500 | _make_window patches __init__ with no-op |
| 14 | S02-F005 | CAT-5 | MAJOR | test_ai.py | 130 | 650 | Function-scoped fixture rebuilds full Ship objects |
| 15 | S01-F002 | CAT-10 | MINOR | test_build_queue_helpers.py | 125 | 125 | 2 clusters of same-pattern tests (6+7 tests) |
| 16 | S03-F010 | CAT-9 | MINOR | test_system_selection_window.py | 120 | 120 | 6 repeated window constructions |
| 17 | S03-F013 | CAT-9 | MINOR | test_fleet_menu_items.py | 100 | 100 | Repeated fleet/mapper/galaxy construction |
| 18 | S04-F010 | CAT-8 | MAJOR | test_camera.py | 80 | 400 | 13 tests with triple-nested with patch blocks |
| 19 | S02-F006 | CAT-5 | MAJOR | test_theme_discovery.py | 80 | 400 | 9 autouse fixture classes re-init pygame display |
| 20 | S01-F006 | CAT-9 | MINOR | test_workshop_screen.py | 80 | 80 | Repeated mock/lambda definitions across test classes |

## Shard Verification Summary

| Shard | Phase 1 Claims | Verified | Disputed | Inconclusive |
|-------|---------------|----------|----------|--------------|
| 01 | 23 | 22 | 2 | 2 |
| 02 | 24 | 27 | 0 | 1 |
| 03 | 22 | 29 | 0 | 0 |
| 04 | 16 | 18 | 3 | 0 |
| 05 | 11 | 12 | 0 | 0 |
| 06 | 19 | 19 | 4 | 0 |
| 07 | 30 | 29 | 5 | 0 |
| 08 | 9 | 10 | 1 | 0 |
| 09 | 9 | 10 | 0 | 1 |
| 10 | 21 | 23 | 0 | 0 |
| 11 | 19 | 21 | 0 | 0 |
| 12 | 25 | 24 | 1 | 0 |
| 13 | 26 | 22 | 2 | 1 |
| 14 | 27 | 24 | 3 | 0 |
| 15 | 6 | 9 | 1 | 0 |
| 16 | 18 | 23 | 0 | 0 |
| **Totals** | **305** | **322** | **22** | **5** |

> Verified counts may exceed Phase 1 claims because cross-shard findings (DUP-\*, HLP-\*) verified in each shard's scope are included in the verified total.

## Cross-Shard Duplicates

### Duplicate Test Patterns (DUP-001 through DUP-006)

| ID | Description | Shards | Est. LOC Savings |
|----|-------------|--------|------------------|
| DUP-001 | `_make_fleet` + `_make_empire` near-identical across combat round budget tests | 01, 11, 16 | ~60 |
| DUP-002 | `_draw_setup` + `_stub_fonts` battle panel helpers | 02, 14 | ~70 |
| DUP-003 | Ship serialization roundtrip pattern (to_dict/from_dict/assert property) | 08, 11 | ~80 |
| DUP-004 | ShipInstance serialization roundtrip — DISPUTED in S01, CONFIRMED in S16 | 01, 16 | ~40 |
| DUP-005 | `_make_colony` / `_make_planet` / `_make_empire` proliferation across strategy engine tests | 03, 05, 06, 09, 10, 16 | ~180 |
| DUP-006 | Stub Modifier classes — DISPUTED in S07, INCONCLUSIVE in S02 | 02, 07 | ~40 |

### Helper Duplications (HLP-001 through HLP-006)

| ID | Description | Copies | Shards | Est. LOC Savings |
|----|-------------|--------|--------|------------------|
| HLP-001 | `MockGameSession` class — 5 identical copies | 5 | 03, 07, 15, 16 | ~110 |
| HLP-002 | `MockPlanetType(Enum)` — 10+ copies, same pattern | 10+ | 02, 03, 04, 06, 09, 12, 15 | ~80 |
| HLP-003 | `make_mock_ship_instance` — canonical exists in root conftest, 4 local copies | 4 | 03, 08, 15, 16 | ~60 |
| HLP-004 | `_make_fleet` — 43+ definitions across codebase | 43+ | 01, 02, 04, 06, 07, 11, 16, others | ~200 |
| HLP-005 | `setup_tmpdir` fixture pattern — 4 copies | 4 | 03, 07, 15, 16 | ~30 |
| HLP-006 | `_make_empire(colonies=None)` — 6 identical copies | 6 | 03, 05, 07, 09, 10, 16 | ~50 |
| **Total** | | | | **~740** |

## Priority Action Plan

### P0 — Immediate Attention (52 findings)
- **CAT-1 Trivial Pass** (34 CRITICAL): Tests that can never fail — `assert True`, `assert not hasattr`, import-then-assert-not-None, tautological assertions. Zero regression value. Delete or rewrite.
- **CAT-2 Tests Nothing Real** (15 CRITICAL): Tests that mock the SUT's own methods with local lambdas, bypass `__init__`, test phantom methods that don't exist in production. Most severe case: `test_workshop_screen.py` where ~13 tests replace production methods with inline lambdas.
- **CAT-13 Tests Targeting Deleted Code** (10 CRITICAL): Tests verifying code absence that act as deletion guards — valid but misclassified. Re-tag as CAT-3 regression guards.

### P1 — Address Before Next Major Feature (69 findings)
- **CAT-4 Duplicate Testing** (16 MAJOR): Identical or near-identical tests differing only in input values. Merge or parametrize.
- **CAT-5 Fixture Bloat** (15 MAJOR): Function-scoped fixtures that rebuild expensive state (pygame displays, full Ship objects, registry hydration) per test. Rescope to module/class.
- **CAT-6 Mocking Brittleness** (25 MAJOR): Tests coupling to private methods, `__init__` bypass patterns, internal call_args, or module-internal imports. Replace with behavioral assertions.
- **CAT-7 Sleep/Latency** (4 MAJOR): `time.sleep()` calls in test bodies (~0.02-0.1s each, cumulative in CI). Replace with threading.Event synchronization.

### P2 — Improve Opportunistically (201 findings)
- **CAT-8 Needless Complexity** (6 MAJOR, 32 MINOR): Deeply nested `with patch()` blocks, long helper functions, excessive mock wiring. Extract helpers and shared fixtures.
- **CAT-9 Simplification** (1 MAJOR, 21 MINOR): Repeated imports in test methods, redundant inline definitions, verifiable simplification opportunities.
- **CAT-10 Parameterize** (88 MINOR): Clusters of structurally identical tests differing only in input/output pairs. Textbook `@pytest.mark.parametrize` candidates.
- **CAT-11 Fragile Assertion** (6 MAJOR, 7 MINOR): Exact list/dict/pixel-coordinate assertions brittle to formatting changes. Use relaxed matching or property-based assertions.
- **CAT-12 Logic-Heavy** (24 MINOR): Tests with for-loops, conditional branches, and derived assertions inside test bodies. Extract to helpers, pre-compute expected values.

## Estimated Impact (Verified Only)

| Metric | Count |
|--------|-------|
| Tests removable with zero coverage loss (CAT-1, CAT-2) | ~52 |
| Tests mergeable via parametrize (CAT-10) | ~180 tests → ~88 parametrized |
| Duplicate tests removable (CAT-4) | ~18 pairs |
| Fixture rescoping candidates (CAT-5) | ~19 |
| Cross-shard helper deduplication (HLP-*) | ~6 helper classes, ~43+ factories |
| Cross-shard test deduplication (DUP-*) | ~30 tests across 6 patterns |
| **Estimated total LOC reduction** | **~4,800** (shard findings) + **~740** (cross-shard) = **~5,540** |

## Layer-Weighted Priority

Layer weights (from `Tools/_audit_common/layer_weight.py`) multiply with severity for priority ordering. The top layers (game/core, game/services, game/engine) carry higher weight than leaf layers (game/ui). All findings are repo-wide test code, so layer weighting applies uniformly. See `Tools/_audit_common/layer_weight.py` for the full weighting schema.

## Trend Comparison

run_tracker.py exists at `Tools/_audit_common/run_tracker.py`. No prior test-review audit records were found for trend comparison. This is the first recorded test-review run with this audit infrastructure.

## Known Disputes and Caveats

1. **MagicMock session-scoping**: S06 Claims 11-12 (CAT-5 MAJOR) proposed session-scoping MagicMock fixtures. DISPUTED — MagicMock accumulates call state; function scope is correct.
2. **Superweapon parametrization**: S06 Claim 5 (CAT-10) proposed parametrizing 15 superweapon tests. DISPUTED — per-weapon setup differs too significantly.
3. **DUP-006 stub classes**: S07 disputed the cross-shard claim that `_Modifier` stubs are identical across files — they serve different domains with different attribute structures.
4. **Test ordering dependency**: S14 Finding 11 (CAT-5) claimed tests require sequential execution. DISPUTED — `reset_game_state` autouse fixture ensures clean state; tests pass in any order.
5. **Conftest files as CAT-3**: S10 (3 files), S16 (3 files) flagged conftest files with no test functions. Downgraded to ADVISORY — conftest files are expected to have only fixtures.
6. **CAT-1 vs CAT-3 regression guards**: S12 Finding 2 was CAT-1 flagged but should be CAT-3 — `assert not hasattr(m, "X")` CAN fail if deleted code is re-added. Reclassified.

## Full Report Paths
- Phase 1 shard reports: `Reviews/results/2026-05-20_210550_test-review/SHARD_01.md` through `SHARD_16.md`
- Phase 2 cross-shard: `Reviews/results/2026-05-20_210550_test-review/CROSS_SHARD.md`
- Phase 3 verified reports: `Reviews/results/2026-05-20_210550_test-review/VERIFIED_SHARD_01.md` through `VERIFIED_SHARD_16.md`
- SHARD_CONFIG.json: `Reviews/results/2026-05-20_210550_test-review/SHARD_CONFIG.json`
- Summary JSON: `Reviews/results/2026-05-20_210550_test-review/SUMMARY.json`
- Final summary: `Reviews/results/2026-05-20_210550_test-review/SUMMARY.md`
