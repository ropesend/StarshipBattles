# Review Report: PROJ-378 Galaxy Cleanup Test Pattern Update

**Request ID:** req_20260507_042609_bb3683
**Review Type:** code
**Review Mode:** Standard (inline analysis)
**Completed:** 2026-05-07T04:50:00Z
**Findings:** 0 CRIT, 0 MAJ, 2 MIN, 3 INFO

---

## 1. Fixture Correctness

`make_galaxy_stub()` in `tests/fixtures/galaxy_fixtures.py:42-48` correctly constructs a post-PROJ-372 `Galaxy` facade:

```python
galaxy = Galaxy.__new__(Galaxy)
galaxy._state = GalaxyState(radius=radius)
galaxy._registry = GalaxyEntityRegistry(galaxy._state)
galaxy._spatial = GalaxySpatialIndex(galaxy._state)
```

Verification:
- `GalaxyState(radius=radius)` — matches constructor signature `GalaxyState(radius: int)` (`galaxy_state.py:42`). All 11 dict fields and 2 ID counters default to empty dicts / `1` via `field(default_factory=...)`.
- `GalaxyEntityRegistry(galaxy._state)` — matches constructor signature `GalaxyEntityRegistry.__init__(self, state: GalaxyState)`.
- `GalaxySpatialIndex(galaxy._state)` — matches constructor signature `GalaxySpatialIndex.__init__(self, state: GalaxyState)` (`galaxy_spatial_index.py:26`).

The stub intentionally does NOT wire generators (`_warp_gen`, `_sys_gen`, `naming`, `star_generator`, `planet_generator`, `storm_generator`, `_pathfinder`) — matching design R4. The docstring (`galaxy_fixtures.py:16-33`) clearly enumerates safe and unsafe methods. **Correct.**

---

## 2. Migration Correctness

### 2.1 `test_galaxy_cleanup.py` — 3 fixtures

| Fixture (old → new) | Verification |
|---|---|
| `galaxy_with_planet` (`:60-93`) | Was: `Galaxy.__new__` + 10 dict assignments. Now: `make_galaxy_stub()` + 6 state-mutating lines. Sets the same 6 state fields (`next_planet_id`, `planets_by_id`, `_planet_to_system`, `_global_hex_planets`, `systems`, `name_map`). All 5 dependent tests still exercise `unregister_planet` which delegates to `_registry`. **Correct.** |
| `galaxy_with_warp_link` (`:153-170`) | Was: `Galaxy.__new__` + 5 dict assignments. Now: `make_galaxy_stub()` + 4 state-mutating lines. Sets `systems` and `name_map` (the two fields `remove_warp_link` reads at `galaxy.py:211-212`). All 4 dependent tests pass through `galaxy.remove_warp_link()` which reads `_state.name_map` directly. **Correct.** |
| `galaxy_with_fleets` (`:226-266`) | Was: `Galaxy.__new__` + 6 dict assignments. Now: `make_galaxy_stub()` + 2 state-mutating lines. Separated mock empire/fleet construction from galaxy state. `get_all_fleets_in_system` delegates to `_spatial` which reads `_state` indexes. The `planet.radius_hexes = 0` fix (line 236) is addressed in Finding #3 below. **Correct.** |

### 2.2 `test_empire.py` — 5 call sites

| Site | Verification |
|---|---|
| Lines 11, 18, 24, 42 | Was: `Galaxy.__new__(Galaxy)` + `galaxy._next_fleet_id = 1`. Now: `make_galaxy_stub()`. The stub initializes `_state.next_fleet_id = 1` (default), so `get_next_fleet_id()` returns 1. **Correct.** |
| Line 34 | `test_fleet_id_persists_across_save`: reads `galaxy._next_fleet_id` (property → `_ensure_state().next_fleet_id`→ `_state.next_fleet_id`) and writes `galaxy2._state.next_fleet_id = saved_counter` (direct state access → same underlying field). Semantically equivalent to the old `galaxy2._next_fleet_id = saved_counter` route through `_ensure_state()`. **Correct.** |

### 2.3 `test_fleet_registration_lifecycle.py` — 1 inline factory

Line 70: Was a 6-line inline block (`gal = Galaxy.__new__(Galaxy); gal._state = GalaxyState(radius=300); gal._registry = GalaxyEntityRegistry(gal._state); gal._spatial = GalaxySpatialIndex(gal._state); gal.warp_points = []`). Now: `gal = make_galaxy_stub(radius=300); gal.warp_points = []`. The `warp_points = []` line is preserved because it was a test-specific override. **Correct.** All 11 dependent tests in the file exercise fleet lifecycle operations through `galaxy.get_fleet_by_id()` which delegates to `_registry`. **Correct.**

---

## 3. Hidden Coupling (MagicMock Planet)

The `MagicMock` planet in `TestGalaxyGetAllFleetsInSystem` (`test_galaxy_cleanup.py:234-236`) correctly sets `planet.radius_hexes = 0`. Without this, `MagicMock().radius_hexes` returns a `MagicMock` object, and `MagicMock() > 0` evaluates to `True` (truthy `__gt__` return), causing `get_all_fleets_in_system` (`galaxy_spatial_index.py:107-110`) to attempt `for local_hex in planet.occupied_hexes:` which would silently iterate an empty or non-deterministic MagicMock iterator.

**Analysis of other latent fields in the code path:**

| Attribute accessed on planet | Source | Risk |
|---|---|---|
| `planet.location` | Explicitly set on mock (line 235) | None |
| `planet.radius_hexes` | Explicitly set to 0 (line 236) | None |
| `planet.occupied_hexes` | Only accessed if `radius_hexes > 0` (line 108) | None — branch not taken |
| `planet.armor`, `planet.hp`, etc. | Not accessed by `get_all_fleets_in_system` | None |

**Conclusion:** No other latent MagicMock attributes can silently pass numeric comparisons in the current code path. The `radius_hexes = 0` fix is sufficient and complete for this test.

**Observation:** If `get_all_fleets_in_system` later adds checks on additional planet attributes, a MagicMock planet could silently produce correct-looking results. Consider migrating to `make_mock_planet` from `tests/fixtures/mock_planet.py` for better maintainability (MIN-002).

---

## 4. Layering / Convention Adherence

**Canonical fixture location:** `tests/fixtures/galaxy_fixtures.py` follows the established `tests.fixtures.*` convention documented in `tests/fixtures/README.md`. The convention states: "Put shared fixtures in `tests/fixtures/` organized by domain." Precedent exists with `tests/fixtures/ai.py`, `tests/fixtures/battle.py`, `tests/fixtures/common.py`, etc. **Correct.**

**Cross-tree importability:** `from tests.fixtures.galaxy_fixtures import make_galaxy_stub` is importable from any test directory because `tests/fixtures/` is a package with `__init__.py`. This is the same import path used by `tests/integration/strategy/test_empire.py:5` and `tests/integration/strategy/test_fleet_registration_lifecycle.py:22`. **Correct.**

**Conftest bridge:** `tests/unit/strategy/data/conftest.py` exposes a `galaxy_stub` `@pytest.fixture` that delegates to `make_galaxy_stub()`. However, no test in `tests/unit/strategy/data/` currently uses this fixture — all three test classes import `make_galaxy_stub` directly. The conftest was intentionally created as an optional bridge (design Q1) but is currently unused infrastructure. See MIN-001.

**No unintended cross-tree import issues:** The conftest imports `from tests.fixtures.galaxy_fixtures`, which is the canonical location. Integration tests import directly from `tests.fixtures.galaxy_fixtures`. No circular or fragile import paths. **Correct.**

---

## 5. Completeness Sweep

**`Galaxy.__new__(Galaxy)` in `tests/`:** Exactly 1 match — the canonical implementation in `tests/fixtures/galaxy_fixtures.py:44`. **Zero** call sites remain in `test_galaxy_cleanup.py`, `test_empire.py`, or `test_fleet_registration_lifecycle.py`.

**`patch.object(Galaxy, '__init__')` in `tests/`:** Zero matches for the `Galaxy` class. Two matches found for `GalaxyTestScreen` class in `tests/unit/ui/screens/test_galaxy_test_screen.py:55,71` — these patch a completely different class (`GalaxyTestScreen`, a UI screen) and are unrelated.

**Sweep verified against plan checklist:**
- [x] Zero `Galaxy.__new__(Galaxy)` outside canonical
- [x] Zero `patch.object(Galaxy, '__init__')` 
- [x] `make_galaxy_stub()` is the only shared stub helper

---

## 6. Plan vs. Implementation Drift

**No deviations found.** All plan items are addressed:

| Plan item | Status |
|---|---|
| Phase 1: Shared `make_galaxy_stub()` + migrate `test_galaxy_cleanup.py` | Complete |
| Phase 2: Sweep `test_empire.py` + `test_fleet_registration_lifecycle.py` | Complete |
| Optional: `docs/02_PATTERNS.md` note | Intentionally skipped per design Q4 (logged in decisions.md 2026-05-07) |
| Optional: AST-guard test | Intentionally skipped per design Q4 (logged in decisions.md 2026-05-06) |
| Production code changes | None (as specified in scope) |
| `_ensure_state()` deletion | Deferred (logged in decisions.md as future opportunity) |

All 5 deliberate scope decisions (fix option B, fixture location, wiring scope, sweep scope, no production changes) are consistent between plan, design, decisions, and implementation.

---

## 7. Pre-Existing Failure: `test_pathfinder_attached_after_init`

The test `test_pathfinder_attached_after_init` lives at `tests/integration/strategy/test_save_round_trip_phase4.py:31`. It references `galaxy._intercept`, which was deleted from `Galaxy.__init__` as PROJ-372 review remediation MIN-001 (decisions row 2026-05-07). The deletion landed in a PROJ-372 changeset — before PROJ-378 existed.

**Confirmed unrelated to PROJ-378:**
- PROJ-378 touches only 5 test files (`galaxy_fixtures.py`, `conftest.py`, `test_galaxy_cleanup.py`, `test_empire.py`, `test_fleet_registration_lifecycle.py`).
- `test_save_round_trip_phase4.py` is not in PROJ-378's scope.
- The root cause (`galaxy._intercept` deleted from `Galaxy.__init__`) is a PROJ-372 production-side change.
- PROJ-378 makes zero production-code changes.

---

## Findings

### CRITICAL (0)

None.

### MAJOR (0)

None.

### MINOR (2)

**MIN-001 — Unused conftest bridge fixture**

`tests/unit/strategy/data/conftest.py:16` exports a `galaxy_stub` `@pytest.fixture` that no test in `tests/unit/strategy/data/` consumes. All three test classes directly import `make_galaxy_stub` from `tests.fixtures.galaxy_fixtures`. The conftest was intentionally created as an optional bridge per design Q1, but unused infrastructure adds a maintenance surface with no consumer.

**Recommendation:** Either remove the conftest until a test needs fixture-injection, or add a one-line note to its docstring clarifying "this fixture is available for tests that prefer pytest injection over direct `make_galaxy_stub()` imports."

**Severity:** MIN — no functional impact, intentionally optional.

**File:** `tests/unit/strategy/data/conftest.py:16`

---

**MIN-002 — MagicMock planet pattern is fragile**

`TestGalaxyGetAllFleetsInSystem` (`test_galaxy_cleanup.py:234-236`) uses a raw `MagicMock()` for planet, requiring `planet.radius_hexes = 0` to prevent `get_all_fleets_in_system` from silently entering the `occupied_hexes` iteration branch. While correctly handled for the current code path, this pattern is fragile: if `get_all_fleets_in_system` later accesses any un-set planet attribute, the MagicMock will return a truthy MagicMock that could silently pass comparisons.

**Recommendation:** In a follow-up, migrate to `make_mock_planet` from `tests/fixtures/mock_planet.py` (PROJ-322). The factory provides controlled defaults for all `Planet` attributes.

**Severity:** MIN — current code path is safe; risk is forward-looking only.

**File:** `tests/unit/strategy/data/test_galaxy_cleanup.py:234-236`

---

### INFO (3)

**INFO-001 — Mixed property/direct-state access in `test_fleet_id_persists_across_save`**

`test_empire.py:29-38` reads `galaxy._next_fleet_id` through the property (which routes through `_ensure_state()`) but writes `galaxy2._state.next_fleet_id` directly. Both paths reach the same underlying `GalaxyState.next_fleet_id` field. The direct write mirrors how `Galaxy.from_dict` (`galaxy.py:313`) restores state. Functionally correct — no bug.

**File:** `tests/integration/strategy/test_empire.py:34-35`

---

**INFO-002 — `GalaxyTestScreen` patch confirms sweep boundary**

The two `patch.object(GalaxyTestScreen, '__init__')` sites at `tests/unit/ui/screens/test_galaxy_test_screen.py:55,71` patch `GalaxyTestScreen` (a UI screen class), not `Galaxy`. They are correctly excluded from PROJ-378's completeness sweep. The grep boundary is clean.

---

**INFO-003 — Pre-existing `test_pathfinder_attached_after_init` failure**

The failure is in `tests/integration/strategy/test_save_round_trip_phase4.py:31` (not in PROJ-378's scope). Root cause: `galaxy._intercept` was deleted from `Galaxy.__init__` as PROJ-372 review remediation MIN-001. PROJ-378 touches zero production files and cannot be the cause. Remediation should be tracked under a separate project (PROJ-372 or a follow-up).

**File:** `tests/integration/strategy/test_save_round_trip_phase4.py:31`

---

## Summary

The PROJ-378 implementation correctly:
1. Provides a canonical `make_galaxy_stub()` factory that constructs a minimal post-PROJ-372 Galaxy with correctly wired `_state`, `_registry`, and `_spatial`.
2. Migrates all 3 legacy-pattern test fixtures in `test_galaxy_cleanup.py`, 5 call sites in `test_empire.py`, and 1 inline factory in `test_fleet_registration_lifecycle.py` — preserving original test semantics.
3. Achieves zero `Galaxy.__new__(Galaxy)` and zero `patch.object(Galaxy, '__init__')` outside the canonical implementation.
4. Follows the `tests.fixtures.*` convention for cross-tree importability.
5. Has no plan-vs-implementation drift.

Two minor findings (unused conftest bridge, MagicMock fragility) and three informational observations. No critical or major issues.
