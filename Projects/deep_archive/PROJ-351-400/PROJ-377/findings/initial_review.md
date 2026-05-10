# PROJ-377: Initial Review

> Site-by-site cost matrix for the pathfinding shim sweep + golden-fixture decision tree.
> Authored 2026-05-06 during PROJ-377 plan authoring; pinned for downstream phases.

---

## Site-by-site migration cost matrix

The 14 production sites that import from `game.strategy.data.pathfinding` split into four classes by **whether `unittest.mock.patch('game.strategy.data.pathfinding.X')` is used in the test suite to mock the function's behavior at this caller site**:

### Class A — Migrate (no test patches reach the shim at this caller's reach)

5 sites, ~2-line edits each, total ~10-line diff:

| # | File:line | Function | Edit |
|---|-----------|----------|------|
| 3 | `game/strategy/engine/superweapon_order_processor.py:31` (~10 in-file call sites) | `get_system_at_hex` | drop import; rewrite ~10 calls to `galaxy._pathfinder.get_system_at_hex(…)` |
| 10 | `game/ui/screens/strategy_screen.py:436` (`calculate_hybrid_path` method) | `find_hybrid_path` | drop import; `self.galaxy._pathfinder.find_hybrid_path(start, end)` |
| 11 | `game/ui/screens/strategy_screen.py:441` (`_get_system_at_hex`) | `get_system_at_hex` | drop import; `self.galaxy._pathfinder.get_system_at_hex(hex)` |
| 12 | `game/ui/screens/strategy_screen.py:446` (`_find_nearest_system`) | `find_nearest_system` | drop import; `self.galaxy._pathfinder.find_nearest_system(hex)` |
| 14 | `game/ui/screens/strategy_colonization.py:258` (`_get_system_at_hex`) | `get_system_at_hex` | drop import; `self.scene.galaxy._pathfinder.get_system_at_hex(hex)` |

### Class B — Defer (test patches the shim at this caller's reach)

6 sites, deferred. Each is paired with at least one test that patches the shim:

| # | File:line | Test that pins it |
|---|-----------|-------------------|
| 1 | `game/strategy/engine/game_session.py:321` (`find_hybrid_path`, `strip_start_hex`) | `tests/integration/strategy/test_command_handlers.py:84,310` (`patch('game.strategy.data.pathfinding.find_hybrid_path')`) + `tests/integration/strategy/turn_engine/test_basics.py:14,51` |
| 2 | `game/strategy/engine/game_session.py:340` (`project_fleet_path`) | `tests/unit/strategy/test_advanced_fleet_orders.py:98,99,190,191,305,306` |
| 4 | `game/strategy/engine/handlers/base.py:20` (`add_move_order_if_needed` calls `find_hybrid_path`, `strip_start_hex`) | `tests/integration/strategy/test_command_handlers.py:84,310` reaches via command handler dispatch |
| 5 | `game/strategy/services/fleet_navigation_service.py:36` (`compute_path` calls `find_hybrid_path`, `strip_start_hex`) | `tests/unit/strategy/pathfinding/test_edge_cases.py:208,256,297`, `test_hybrid_and_intercept.py` (extensive) |
| 6 | `game/strategy/services/fleet_navigation_service.py:206` (`get_destination` lazy-imports `calculate_intercept_point`) | `tests/unit/strategy/test_advanced_fleet_orders.py:156`, `tests/unit/strategy/fleet_movement_engine/test_warp.py:36`, `tests/unit/strategy/turn_engine/test_tick_mechanics.py:80` |
| 13 | `game/ui/screens/strategy_superweapons.py:350` (`get_system_at_hex`) | `tests/unit/ui/screens/test_strategy_superweapons.py:425` (`patch('game.strategy.data.pathfinding.get_system_at_hex')`) |

**Why these are deferred:** the production-side change is mechanically trivial (2 lines per site), but each defer-site has 1+ tests that patch `pathfinding.X` globally to mock that algorithm. Migrating production to `galaxy._pathfinder.X(...)` makes those test patches no longer reach the new code path — production runs the unmocked algorithm in the test, the test passes against unmocked output, and a real algorithmic regression in pathfinding becomes invisible to the test.

The full fix requires co-migrating tests: rewrite each `patch('game.strategy.data.pathfinding.X')` to `patch.object(galaxy._pathfinder, 'X', ...)` (instance-level) or `patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.X', ...)` (class-level). Each rewrite has subtle scope semantics — the global patch covers all callers; the object/class patch covers one. ~30 patch sites across ~10 test files; a focused successor ticket is the right home.

### Class C — Stays (intentional shim-infrastructure routing)

2 sites, intentional shim routing:

| # | File:line | Why it stays |
|---|-----------|--------------|
| 7 | `game/strategy/services/intercept_calculator.py:121` (`from game.strategy.data import pathfinding as _pf_shim; _pf_shim.project_fleet_path(...)`) | Intentional routing through the shim so test patches of `pathfinding.project_fleet_path` reach the calculator's call. Documented in code comments + intercept_calculator.py docstring. |
| 8 | `game/strategy/services/intercept_calculator.py:169` (`_pf_shim.find_hybrid_path(...)`) | Same — preserves test-patch transparency. PROJ-372 verifier_report.md MIN-001 confirmed: routing through `galaxy._intercept` would defeat the transparency. |

### Class D — Verify-then-decide (1 site)

| # | File:line | Pending verification |
|---|-----------|---------------------|
| 9 | `game/strategy/facade/slices/planet_slice.py:66` (`get_system_at_hex` radius-fallback) | `tests/unit/strategy/facade/test_facade_robust_resolution.py:73,87` patch `pathfinding.get_system_at_hex`. The test file's name ("robust resolution") strongly suggests it exercises this slice via the patches; Phase 2 Task 2.1 reads the tests and confirms migrate-or-defer. **Architect prediction:** defer. |

---

## Migration headcount by class

| Class | Count | Disposition |
|-------|------:|-------------|
| A — migrate now | 5 | Phase 2 Tasks 2.2-2.4 |
| B — defer (test-patched) | 6 | Phase 2 Task 2.6 (pin with rationale rows) |
| C — stays (shim infra) | 2 | No action; preserved by design |
| D — verify-then-decide | 1 | Phase 2 Task 2.1 → likely defer |
| **Total** | **14** | |

**Plausible Phase 2 outcome:** 5 of 14 migrated (Class A only); 6 deferred (Class B); 2 stay shim infrastructure (Class C); 1 deferred (Class D after verification). 7 net continued shim importers + 2 shim-infra = 9 sites continue to use `pathfinding.py`.

If Class D site #9 turns out to be migratable (the patch doesn't reach it), 6 of 14 migrated.

---

## Golden-fixture decision tree

```
Q1: pickle or JSON?
├── pickle:    rejected — Python-version drift risk just removed by PROJ-295
└── JSON:      ACCEPTED — `Galaxy.to_dict()` already produces JSON-shaped dicts;
                     human-diffable; sort_keys + indent normalize for VCS

Q2: how many fixtures?
├── 1:         insufficient — generation paths often default-fill,
                     missing field-drift in owned-planet fields
├── 2:         ACCEPTED — baseline (5-system warp lanes) + populated
                     (10-system planets + manually populated owned planet)
├── 3-5:       rejected — diminishing returns; CI cost + maintenance cost rises

Q3: where do fixtures live?
├── tests/system/:                       no such directory
├── tests/integration/save_load/:        too area-specific (PROJ-377 is galaxy
                                              serialization, not save_load)
├── tests/fixtures/saves/:               ACCEPTED — mirrors existing
                                              tests/fixtures/{captions/,
                                              test_components.json}

Q4: capture-script convention?
├── pytest test (test_capture.py):       rejected — would over-write the
                                              fixture every run
├── manual script:                       ACCEPTED — leading underscore
                                              `_capture_baseline.py` excludes
                                              from pytest discovery

Q5: storm-serde drift?
├── ignore (let the fixture include
       storms; if from_dict drifts,
       round-trip fails):                rejected — known pre-existing drift
                                              that PROJ-372 explicitly scoped
                                              out (synthetic test does the same)
└── strip storms before capture:         ACCEPTED — capture script clears
                                              `system.storms = []` before
                                              `to_dict()`

Q6: assertion shape?
└── `Galaxy.from_dict(fixture).to_dict() == fixture`:  ACCEPTED — same shape
                                                         as synthetic test;
                                                         catches structural
                                                         drift, not semantic
```

---

## Top 5 surprises

### 1. The shim is doing more work than the review report suggests

The 14 cited importers are the production sites — but `tests/` adds another ~30 import + patch sites that depend on the shim's free-function form. The shim isn't just "deprecated forwarders"; it's the **actively-used test-patch transparency surface** for ~10 test files. A naive "delete the shim" sweep breaks ~30 tests, not 14.

### 2. PROJ-372 review MIN-001 was already remediated, but the remediation depended on the shim

PROJ-372 decisions.md row 2026-05-07 deleted `Galaxy._intercept` as dead code, with the rationale "routing through galaxy._intercept would defeat the transparency the shim provides". This means the shim's role is **load-bearing**, not deprecated. PROJ-377's framing is corrected accordingly: the shim isn't being removed, it's being formalized.

### 3. `superweapon_order_processor.py` is the single biggest migration win

Site #3 has ~10 in-file call sites for `get_system_at_hex` (lines 345, 408, 413, 453, 470, 540, 546, 597, 605, 715). Migrating site #3 in Phase 2 Task 2.2 closes ~10 of the visible "shim usage" hits in a single file edit. The other 4 Class A sites are 1 hit each.

### 4. The `_intercept_for(galaxy)` helper is structurally important

It always constructs a fresh `InterceptCalculator(GalaxyPathfindingService(galaxy))` rather than reusing `galaxy._intercept` (deleted) or `galaxy._pathfinder`-derived. This is by design (per PROJ-372 verifier_report.md): tests patching `pathfinding.find_hybrid_path` get a fresh `_pathfinder_for(galaxy)` that reads the patched module-level function. Migrating away from `_intercept_for` would defeat ~10 test patches in `tests/unit/strategy/pathfinding/test_hybrid_and_intercept.py` alone. **`_intercept_for` and `_pathfinder_for` are the heart of the shim's value-add and must be preserved.**

### 5. The synthetic round-trip test is genuinely strong; the gap is the lack of a checked-in artifact

`test_save_round_trip.py`'s 5 functions cover empty / 1-system / 5-system + warp / 10-system + planets / 20-system + planets + warp. Each runs `to_dict → from_dict → to_dict` and asserts identity. **It catches in-flight drift well** — what it can't catch is "a save written from PROJ-369 commit X loads correctly post-PROJ-372". That's a different kind of regression: cumulative-format drift across long-lived saves. The golden-fixture artifact pins the format AT a known commit, so the next refactor that touches `to_dict` / `from_dict` has a checked-in baseline to round-trip against.
