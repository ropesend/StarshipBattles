# PROJ-377: Design — PROJ-372 Phase 5 Leftovers

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

PROJ-372 review report (`Reviews/results/2026-05-07_020327_code_proj-372-galaxy-planet-star-god-class-decompositio_req-req_20260507_020326_6c1cc3/report.md`):
- **MAJ-001:** save round-trip is synthetic-only — no checked-in pre-decomposition fixture.
- **MIN-002:** pathfinding shim sweep promised at PROJ-372 Phase 5 Tasks 5.1-5.2 was not done; 14 production sites still import the shim.

PROJ-372 verifier (`verifier_report.md`):
- MAJ-001 confirmed; "golden-file remediation is appropriate".
- MIN-002 confirmed; remediation revised to "either complete the migration or file a follow-up project; file PROJ-376 if you'd rather not interleave".
- Verifier's design constraint on the shim: "_intercept_for(galaxy) … always wraps `_pathfinder_for(galaxy)` in a fresh InterceptCalculator — by design, per its own docstring … even if `galaxy._intercept` were used, test-patch transparency would break."

---

## Initial Analysis: per-site migration matrix

The 14 cited shim importers split across three classes of caller. The classification turns on **whether `unittest.mock.patch('game.strategy.data.pathfinding.X')` is used in the test suite to mock the function's behavior at this caller site**:

### Class A — Migrate (no test patches reach this site through the shim)

| # | Site | Function used | Migration target |
|---|------|---------------|------------------|
| 3 | `game/strategy/engine/superweapon_order_processor.py:31` (uses `get_system_at_hex` ~10x in file) | `get_system_at_hex` | `galaxy._pathfinder.get_system_at_hex(hex_c, radius=50)` |
| 10 | `game/ui/screens/strategy_screen.py:436` (`calculate_hybrid_path` method) | `find_hybrid_path` | `self.galaxy._pathfinder.find_hybrid_path(start, end)` |
| 11 | `game/ui/screens/strategy_screen.py:441` (`_get_system_at_hex` method) | `get_system_at_hex` | `self.galaxy._pathfinder.get_system_at_hex(hex)` |
| 12 | `game/ui/screens/strategy_screen.py:446` (`_find_nearest_system` method) | `find_nearest_system` | `self.galaxy._pathfinder.find_nearest_system(hex)` |
| 14 | `game/ui/screens/strategy_colonization.py:258` (`_get_system_at_hex` method) | `get_system_at_hex` | `self.scene.galaxy._pathfinder.get_system_at_hex(hex)` |

**Migration cost:** trivial. Each is a 2-line edit (drop `from … import …`; replace the call). Sharded suite + targeted UI tests confirm.

### Class B — Defer (test patches the shim at this caller's reach)

| # | Site | Function used | Test patches it |
|---|------|---------------|-----------------|
| 1 | `game/strategy/engine/game_session.py:321` | `find_hybrid_path`, `strip_start_hex` | `tests/integration/strategy/test_command_handlers.py:84,310`, `tests/integration/strategy/turn_engine/test_basics.py:14,51` |
| 2 | `game/strategy/engine/game_session.py:340` | `project_fleet_path` | `tests/unit/strategy/test_advanced_fleet_orders.py:98,99,190,191,305,306` |
| 4 | `game/strategy/engine/handlers/base.py:20` (`add_move_order_if_needed`) | `find_hybrid_path`, `strip_start_hex` | reached from `test_command_handlers.py` paths that patch `find_hybrid_path` |
| 5 | `game/strategy/services/fleet_navigation_service.py:36` (`compute_path` calls `find_hybrid_path`, `strip_start_hex`) | `find_hybrid_path`, `strip_start_hex` | `tests/unit/strategy/pathfinding/test_edge_cases.py:208,256,297`, `test_hybrid_and_intercept.py` extensively |
| 6 | `game/strategy/services/fleet_navigation_service.py:206` (lazy import of `calculate_intercept_point`) | `calculate_intercept_point` | `test_advanced_fleet_orders.py:156`, `tests/unit/strategy/fleet_movement_engine/test_warp.py:36`, `tests/unit/strategy/turn_engine/test_tick_mechanics.py:80` |
| 13 | `game/ui/screens/strategy_superweapons.py:350` | `get_system_at_hex` | `tests/unit/ui/screens/test_strategy_superweapons.py:425` patches `pathfinding.get_system_at_hex` while exercising this UI |

**Migration cost (if we did it):** medium. The production-side change is 2 lines per site, but each defer-site has 1-N tests that depend on the shim level. To migrate without breaking tests we must rewrite the patches: `patch('game.strategy.data.pathfinding.find_hybrid_path')` → `patch.object(galaxy._pathfinder, 'find_hybrid_path', …)` or `patch('game.strategy.services.galaxy_pathfinding_service.GalaxyPathfindingService.find_hybrid_path', …)`. The latter is brittle (instance vs class patch); the former requires the test to have a `galaxy` reference at patch time, which most don't (they patch globally before constructing the SUT).

**PROJ-377 decision:** defer all 6 sites. Closing them costs a separate ticket that explicitly co-migrates production+test pairs.

### Class C — Stays (intentional shim-infrastructure routing)

| # | Site | Function used | Why it stays |
|---|------|---------------|--------------|
| 7 | `game/strategy/services/intercept_calculator.py:121` (`_pf_shim.project_fleet_path`) | `project_fleet_path` | The intercept calculator deliberately routes back through the shim so test patches of the shim's `project_fleet_path` flow through. Documented at the call site. |
| 8 | `game/strategy/services/intercept_calculator.py:169` (`_pf_shim.find_hybrid_path`) | `find_hybrid_path` | Same — preserves test-patch transparency. |

**Migration cost:** would require redesigning intercept's test surface. Out of PROJ-377 scope.

### Class D — Verify-then-decide

| # | Site | Function used | Verification |
|---|------|---------------|--------------|
| 9 | `game/strategy/facade/slices/planet_slice.py:66` (radius-fallback in `get_planets_at_hex`) | `get_system_at_hex` | `tests/unit/strategy/facade/test_facade_robust_resolution.py:73,87` patches `pathfinding.get_system_at_hex`. **Phase 2 Task 2.1 reads those tests** and decides: if the patches exercise this slice (likely yes, given file name match), defer to Class B; otherwise migrate. |

---

## Today's vs. target shim shape

**Today** (`pathfinding.py` 104 LOC):
```
strip_start_hex          → forwards to GalaxyPathfindingService.strip_start_hex (staticmethod)
find_path_deep_space     → forwards to GalaxyPathfindingService.find_path_deep_space (staticmethod)
find_path_interstellar   → forwards via _pathfinder_for(galaxy)
get_system_at_hex        → forwards via _pathfinder_for(galaxy)
find_nearest_system      → forwards via _pathfinder_for(galaxy)
find_hybrid_path         → forwards via _pathfinder_for(galaxy)
project_fleet_path       → forwards to InterceptCalculator-module-level helper (which delegates to FleetNavigationService)
calculate_intercept_point→ forwards via _intercept_for(galaxy)
+ helpers _pathfinder_for, _intercept_for
```

**Target after PROJ-377 Phase 3** (assuming 6 of 14 migrate; intercept stays shim-routed):
```
# Shim file kept as the test-patch transparency surface.
# Free functions actively mock-patched in the test suite:
strip_start_hex       (used by Class B sites only via fleet_navigation_service / game_session)
find_hybrid_path      (Class B sites: game_session, handlers/base, fleet_navigation_service, intercept_calculator infra)
project_fleet_path    (Class B sites: game_session, intercept_calculator infra)
calculate_intercept_point (Class B sites: fleet_navigation_service infra)
get_system_at_hex     (Class B sites: superweapons screen — but if UI patch is reachable; otherwise dropped)
+ helpers _pathfinder_for, _intercept_for

# Free functions Phase 3 is allowed to drop (no Class B caller, no test patch):
find_path_deep_space  → NO callers among the 14; tests import it directly via shim. Verify in Phase 3.
find_path_interstellar → 1 production caller (engine? UI?) — verify in Phase 3 by re-grep.
find_nearest_system   → 1 caller (Class A site #12). After migration: zero. Drop.
```

Phase 3's AST guard pins the surviving set explicitly, so future refactors can't silently regrow the shim.

---

## Golden-fixture format

### Decision: JSON, NOT pickle

- **JSON** (decision): the in-tree `Galaxy.to_dict()` produces a `dict` of plain types. JSON is human-diffable, version-control-friendly, language-agnostic, and immune to Python-version unpickling drift (relevant given PROJ-295 just bumped to 3.13). The fixture is a snapshot of `Galaxy.to_dict()` output written via `json.dump(..., indent=2, sort_keys=True)`.
- **Pickle** (rejected): brittle across Python upgrades, opaque, and a security footgun if the fixture is ever loaded from a non-trusted source.

### Decision: deterministic capture script

`tests/fixtures/saves/_capture_baseline.py`:
- Imported, NOT pytest-discovered (leading underscore).
- Runs `random.seed(K)` for fixed K; constructs the same shape as the synthetic test (`generate_systems(...)`); strips storms (PROJ-372 known drift); calls `galaxy.to_dict()`; writes via `json.dump(..., indent=2, sort_keys=True)`.
- Idempotent: re-running produces byte-identical output.
- Run by humans: `python tests/fixtures/saves/_capture_baseline.py`. CI never runs it; CI only loads-and-asserts.

### Decision: two fixtures, not five

PROJ-372 Phase 5 plan said "5 fixture saves". The synthetic test already covers 5 shapes. PROJ-377 ships TWO fixtures:
1. **baseline** — 5-system synthetic + warp lanes (no planets), seed=2 (matches existing synthetic `test_round_trip_5_system_synthetic_with_warp`).
2. **populated** — 10-system + planets (best-effort) + warp lanes + manually-added owned planet with non-default fields (atmosphere, deposits, stockpile, owned_id, populations) so the `Planet.to_dict` path with all 47 fields lit up is exercised — caught by the round-trip identity even when generation happens to leave most fields default.

Two is enough to catch field-drift regressions without inflating CI cost or fixture maintenance burden. Add a third only if a real regression-class shows up.

### Decision: storm fields stripped before capture

Per `tests/integration/strategy/test_save_round_trip.py:34-38`, `Storm.to_dict()/from_dict()` has pre-existing drift that PROJ-372 explicitly scoped out. The capture script clears `system.storms = []` before calling `galaxy.to_dict()`. Document in the capture-script docstring + `decisions.md`.

### Decision: round-trip identity assertion

```python
fixture = json.load(open(fixture_path))
galaxy = Galaxy.from_dict(fixture)
roundtripped = galaxy.to_dict()
assert roundtripped == fixture
```

This catches:
- A field added to `to_dict` but not read by `from_dict` (round-trip diverges).
- A field renamed (load fails or round-trip diverges).
- A type narrowed (e.g., `dict` → `OrderedDict`; serializer output diverges).
- A new index built lazily that isn't restored on load (the second `to_dict` shape diverges).

It does NOT catch:
- A field added to both `to_dict` and `from_dict` consistently but with the wrong meaning.
- A semantic change to a field's content (e.g., happiness ratio rescaled). PROJ-377 doesn't aim to catch semantic drift; only structural drift.

This is the same trade-off the synthetic test already accepts.

---

## Alternatives considered

### A. Full sweep — migrate all 14 + rewrite all ~30 test patches in one ticket
- **Pro:** clean — `pathfinding.py` deletes; AST guard = "module gone".
- **Con:** ~30 test-patch rewrites across ~10 files. Each requires reasoning about whether the test's intent is "patch the algorithm globally" (`patch('module.func')`) or "patch this fleet's pathfinding" (`patch.object(galaxy._pathfinder, …)`). The two patterns aren't behaviorally equivalent — if production has multiple callers of the same function, the global patch covers all; the object patch covers only the one. Test authors picked the global form on purpose. Rewriting them collapses that intent and risks subtle test-meaning drift.
- **Estimated work:** 1-2 hours of test-rewriting + 30-60 min of careful review to verify patch-scope semantics preserved.
- **Rejected** as scope-creep for PROJ-377; appropriate as a successor ticket once the test-patch convention is agreed.

### B. Partial sweep — Phase 2 of this plan (5-6 of 14 migrated, deferred sites pinned)
- **Pro:** safe, mechanical, no test rewrites. Closes the half of MIN-002 that has no test-patch coupling. Leaves the other half explicitly logged.
- **Con:** doesn't fully close MIN-002. The shim file lives on as a permanent dependency. PROJ-372's plan said "delete shims at Phase 5 close"; this plan formalizes that the deletion is conditional on test-patch unification, which is a separate concern.
- **Accepted.** This is the body of PROJ-377.

### C. Golden-file only (skip shim sweep)
- **Pro:** smallest possible scope; closes MAJ-001 alone.
- **Con:** doesn't close MIN-002 at all. PROJ-372's plan committed both; deferring MIN-002 indefinitely accumulates plan-vs-reality drift.
- **Rejected** — the partial sweep is cheap and real progress.

### D. Leave both as-is
- **Pro:** zero churn.
- **Con:** PROJ-372 review explicitly flagged both as missed deliverables. Leaving them undone is exactly the failure mode "Phase 5 closed without the work".
- **Rejected.**

### E. Migrate `_pathfinder_for(galaxy)` callers to `galaxy._pathfinder` directly (skip `isinstance` guard)
- **Pro:** removes the `getattr(galaxy, "_pathfinder", None)` + `isinstance` dance.
- **Con:** `_pathfinder_for` is the "stub-galaxy escape hatch" — tests sometimes pass a `MagicMock()` galaxy without `_pathfinder`; the helper synthesizes a fresh `GalaxyPathfindingService(stub)` on the fly. Migrating callers to `galaxy._pathfinder` directly breaks those tests.
- **Rejected** — keep the helper semantics inside the shim; production callers (Class A) reach `galaxy._pathfinder` directly because production galaxies always have it.

### F. Use a binary save fixture (load via `save_load.py`) instead of a JSON fixture
- **Pro:** matches the user's actual save artifact — catches save-format drift one layer deeper than `Galaxy.to_dict()`.
- **Con:** depends on the entire save_load pipeline (Empire / GameSession / etc.), not just `Galaxy.to_dict`. PROJ-372's review concern was specifically about Galaxy/Planet/Star serialization. A `Galaxy.to_dict() / from_dict()` golden fixture is the smallest test that catches the cited drift. A wider save-load fixture is a separate concern (and would belong to a different project).
- **Rejected for PROJ-377;** appropriate as a successor.

### G. Move pathfinding shim file under `tests/` (since its only remaining purpose is test-patch transparency)
- **Pro:** signals intent — "this exists for tests".
- **Con:** the deferred Class B production sites still import it. Production code can't import from `tests/`. Would require either making the shim importable from both (file duplication) or migrating those sites first (alternative A).
- **Rejected.**

---

## Risks

- **R1: Test-patch transparency loss.** The biggest risk. If a Phase 2 migration accidentally moves a Class B caller off the shim, tests that patch `pathfinding.X` silently no longer reach the new code — production runs unmocked, tests pass against unmocked algorithm output, results may look fine until a real regression. Mitigation: Phase 2 Task 2.1 re-runs `Grep` for every patch site BEFORE any migration; defer-list is data, not opinion. Phase 2 Task 2.6 runs the full sharded suite and asserts test count is preserved (no silent skips).
- **R2: Golden-fixture maintenance cost.** The fixture must be re-captured every time `to_dict` adds a field. `Storm.to_dict` drift will be a recurring annoyance — Phase 1 strips storms. Mitigation: capture script is committed; re-running it produces a deterministic update; CI failure mode is "fixture diff in PR", which is human-reviewable.
- **R3: Capture script non-determinism.** `random.seed(K)` covers the explicit RNG, but Python `dict` ordering, `set` iteration, or third-party library behavior (e.g., naming registry order) could still drift. Mitigation: `json.dump(..., sort_keys=True)` normalizes key order; the synthetic test already passes round-trip equality with the same seed, proving determinism for this test shape.
- **R4: AST shim-scope guard over-fits.** If Phase 3 pins an exact function-name list, future legitimate work (e.g., adding a new pathfinding helper that genuinely belongs in services but tests want to patch globally) tripped the guard. Mitigation: the guard test pins **only** the absence of currently-deletable functions, not the presence of currently-required ones — and the test docstring directs future authors to update the list deliberately.
- **R5: PROJ-372 plan deviation accumulation.** PROJ-372 had two plan deviations beyond Phase 5: `remove_warp_link` not extracted (decisions.md row 2026-05-07) and the Phase 5 leftovers (this project). Each is documented; PROJ-377 closes the second. Mitigation: PROJ-377's cross-link in PROJ-372 decisions.md spells out which deliverables landed and which were re-scoped, so future agents reading PROJ-372's plan don't repeat the gap.
- **R6: Round-trip equality via `==` on `dict[HexCoord, …]`.** `Galaxy.to_dict()` returns plain JSON-shaped dicts; `HexCoord` keys are converted to `{"q": …, "r": …}` per `hex_to_dict` (verified in `galaxy.py:289-292`). After `json.load`, all keys are strings/lists; equality holds. Mitigation: capture script uses `json.dump`; test loads with `json.load`; both go through plain JSON, so type-stability is guaranteed.
- **R7: Hidden test count regression.** Migrating a caller while preserving behavior could still affect a test that depended on the import path itself (e.g., `from game.strategy.data.pathfinding import strip_start_hex` then mocking `module.strip_start_hex`). Mitigation: Phase 2 runs `pytest --collect-only` before and after; counts must match.
- **R8: PROJ-377 surfaces a NEW concern.** If Phase 1 finds the synthetic round-trip already fails (pre-existing real bug), this project widens. Mitigation: synthetic test passes today (PROJ-372 closure confirmed `12/12 audit-gate tests pass on focused run`); a regression here is news.

---

## Dependencies

- **PROJ-372** — predecessor; PROJ-377 closes its two outstanding Phase 5 deliverables.
- **No upstream dependency on PROJ-370 / PROJ-376 / PROJ-378.** PROJ-377 touches different files.
- **Sequencing freedom:** the Phase 2 partial-sweep migrates production-only sites; tests are untouched. The deferred sites are pinned so that a future test-patch unification project (alternative A) can proceed without re-discovering this analysis.

---

## Open questions

- **OQ-1.** Should the golden fixture be JSON or pickle? **Architect recommendation: JSON** (rejected pickle — see Alternatives). User confirms.
- **OQ-2.** Should we ship 1, 2, or 5 golden fixtures? **Architect recommendation: 2** (baseline + populated). Rationale in Decisions.
- **OQ-3.** Should PROJ-377 also rewrite the ~30 test patches to migrate the deferred Class B sites (full alternative A)? **Architect recommendation: NO** — defer to a successor ticket where the test-patch convention is settled. PROJ-377 closes the half that doesn't require test rewrites and pins the rest.
- **OQ-4.** Should the surviving shim live in `game/strategy/data/pathfinding.py` or be relocated to (e.g.) `game/strategy/services/pathfinding_test_surface.py` with a clearer name? **Architect recommendation: keep it in place** — the path is in 6+ test files and 6+ production files; renaming requires every patch string to update; the docstring change is a 5-line edit that achieves the same intent at zero churn.
- **OQ-5.** What seed values should the two fixtures use? **Architect recommendation: baseline=seed 2 (matches existing synthetic test for parity), populated=seed 100 (fresh).** User confirms.
- **OQ-6.** Should we delete the per-phase `test_save_round_trip_phase{1,2,3,4}.py` tests now that the consolidated test exists? **Architect recommendation: NO** — PROJ-372 marked them "kept for now as boundary checks". Deleting them is a separate concern; PROJ-377 is additive only.
