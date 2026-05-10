# Verifier Report: PROJ-378 Galaxy Cleanup Test Pattern Update

**Verifier:** Claude (independent) for OpenCode review
**Source report:** `report.md` (same directory)
**Commits in scope:** `9667eaa5a`, `2611ce6e1` on `feat/03c-phase-aware-execution`
**Verification date:** 2026-05-06

---

## Verdicts Table

| Finding | Severity | Verdict | Notes |
|---|---|---|---|
| MIN-001 — Unused conftest bridge | MIN | **CONFIRM** | Only the conftest defines `galaxy_stub`; no test parameter consumes it. |
| MIN-002 — MagicMock planet fragility | MIN | **CONFIRM** | Current code path only reads `planet.location` and `planet.radius_hexes`; risk is forward-looking only. |
| INFO-001 — Mixed property/direct-state read+write | INFO | **CONFIRM** | Both paths reach `_state.next_fleet_id`; semantically identical. |
| INFO-002 — `GalaxyTestScreen` patch boundary | INFO | **CONFIRM** | Lines 55, 71 patch `GalaxyTestScreen`, not `Galaxy`. Out of scope. |
| INFO-003 — Pre-existing `_intercept` failure | INFO | **CONFIRM** | Test file untouched by PROJ-378; failure is PROJ-372-side. |

---

## Per-Finding Details (MINs)

### MIN-001 — CONFIRM

**Claim:** `tests/unit/strategy/data/conftest.py:16` exports a `galaxy_stub` fixture nobody consumes.

**Evidence checked:** `Grep "galaxy_stub" tests/unit/strategy/data/` returns matches only inside `conftest.py` (definition) and three direct calls to `make_galaxy_stub()` in `test_galaxy_cleanup.py`. No test function declares `galaxy_stub` as a parameter. The conftest is an unused bridge.

**Verdict:** CONFIRM (legitimately unused). The recommendation (delete or document as an opt-in alternative) is reasonable; severity MIN is appropriate.

---

### MIN-002 — CONFIRM

**Claim:** The MagicMock planet at `test_galaxy_cleanup.py:234-236` is fragile because it relies on the current `get_all_fleets_in_system` reading only two attributes.

**Evidence checked:** `game/strategy/data/galaxy_spatial_index.py:90-121` (the body of `get_all_fleets_in_system`). The only planet attribute reads are:
- `planet.location` (line 99) — explicitly mocked.
- `planet.radius_hexes` (line 108) — explicitly mocked to `0`, gating the `occupied_hexes` branch.
- `planet.occupied_hexes` (line 109) — only reachable if `radius_hexes > 0`; the `= 0` mock skips it.

No other planet attribute is touched in the method or in the helper `is_zone_occupant` (called only on `star`, not `planet`). Confirmed no other `planet.*` access on this code path.

**Forward-looking risk acknowledged:** if a future change adds e.g. `planet.is_destroyed`, a raw MagicMock would silently return a truthy MagicMock and skew results. Migrating to `make_mock_planet` is a defensible follow-up, not a current-correctness fix.

**Verdict:** CONFIRM. Severity MIN is appropriate (no current-path bug; suggested as defer-to-follow-up).

---

## INFO sanity checks (one-liner each)

- **INFO-001 — CONFIRM:** `galaxy.py:135-141` defines `_next_fleet_id` as a property routed through `_ensure_state().next_fleet_id`; reading at `test_empire.py:29,32` and writing `galaxy2._state.next_fleet_id = saved_counter` at `test_empire.py:35` both target the same `GalaxyState.next_fleet_id` field. Mirror of `Galaxy.from_dict` restore path. No semantic change.
- **INFO-002 — CONFIRM:** `tests/unit/ui/screens/test_galaxy_test_screen.py:55,71` literally read `patch.object(GalaxyTestScreen, '__init__', ...)`. UI screen class, not the strategy `Galaxy` class. Sweep boundary is clean.
- **INFO-003 — CONFIRM:** `tests/integration/strategy/test_save_round_trip_phase4.py:31-34` references `galaxy._intercept`. PROJ-378 commits touch only the 5 enumerated test files (no production code, no `test_save_round_trip_phase4.py`). Failure originates from PROJ-372-side deletion of `_intercept` from `Galaxy.__init__`.

---

## Independent Sweep

- **`Galaxy.__new__(Galaxy)` outside `tests/fixtures/galaxy_fixtures.py`:** `Grep` returns exactly one match — `tests/fixtures/galaxy_fixtures.py:44` (the canonical helper). Zero stragglers in PROJ-378 scope. **CLEAN.**
- **`patch.object(Galaxy,` (no underscore prefix) in `tests/`:** `Grep` returns zero matches. **CLEAN.**
- **`_next_fleet_id` writes converted to `_state.next_fleet_id` writes:** the only such conversion is `test_empire.py:35`. The setter and direct-write paths are equivalent because `_state` is non-None on a stubbed galaxy (`make_galaxy_stub` assigns `_state` immediately), so `_ensure_state()` returns the existing state. No subtle behavior change.
- **Lingering `galaxy._next_fleet_id = N` writes:** `test_save_round_trip_phase3.py:38` still uses `galaxy._next_fleet_id = 33` — this routes through the property setter and remains correct (test is out of PROJ-378's migration scope and uses a real `Galaxy(radius=...)` instance, not a stub). No issue.
- **OpenCode oversight check:** None of significance. The migration is mechanical and tight; no behavior-changing edits hidden in the test changes.

---

## Recommended Actions for Claude

1. **MIN-001 (defer or trivially fix):** the conftest bridge is harmless but unused. Lowest-friction option is to add a single docstring sentence ("this fixture is the pytest-injection alternative; tests may also import `make_galaxy_stub` directly") and leave the file. Deleting is also defensible. Either way, do *not* spend significant effort here.
2. **MIN-002 (defer):** log a follow-up note in PROJ-378 decisions or the PROJ-322 mock-planet ticket suggesting `TestGalaxyGetAllFleetsInSystem` migrate to `make_mock_planet` next time the test is touched. No fix-now action needed.
3. **INFO-001/002/003:** no action required. INFO-003 should be tracked under the PROJ-372 follow-up where `_intercept` was removed; not PROJ-378's responsibility.
4. **No production code action.** PROJ-378 scope is correctly test-only. Sweep is clean. Migration semantics preserved.

The OpenCode review is well-supported. PROJ-378 can be closed (subject to MIN-001 disposition decision) without further code changes.
