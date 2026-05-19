# PROJ-449 Consolidated Findings

> Findings closed (or partially closed) by this project. Each entry copied from the archived bucket reports + a current-state verification line dated **2026-05-19**.
>
> Sources:
> - `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md`
> - `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md`

---

## F-A-002 — `Planet` class has a wrapped `__init__` legacy-kwargs shim
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `game/strategy/data/planet.py:398-420` (wrapper definition + assignment); `game/strategy/data/planet_serde.py:160-162` (non-test dependent)
- **Symbol**: `_planet_init_with_legacy_kwargs` (module-level wrapper assigned to `Planet.__init__`)
- **Source refactor**: PROJ-436 Phase 4f
- **What survived**: A module-level wrapper that translates `stockpile=...`, `max_stockpile=...`, `staging_yard=...` kwargs to their private-field spellings, so test fixtures don't have to migrate. Mirrors PROJ-443 Phase 5b retention rationale for `_ship_instance_init_with_legacy_kwargs`.
- **Why it's a problem**: Two coupled deletion shims (this + `_ship_instance_init_with_legacy_kwargs` at `ship_instance.py:809`) survive because the test sweep was scoped out. Per CLAUDE.md "saves are disposable" + "no compatibility shims" — and `planet_serde.planet_to_dict` ALSO uses the public name `"stockpile"` for the save key (line 53), plus `planet_from_dict_kwargs` reconstructs through the wrapper at planet_serde.py:160-162. So the wrapper isn't just protecting test files; it's load-bearing for serialization too.
- **Suggested action**: Audit-then-decide (Phase 0). Migrate to post-PROJ-436 private kwargs (`_stockpile=`, `_max_stockpile=`, `_staging_yard=`) or factory helpers, plus a rewrite of `planet_from_dict_kwargs`; then delete the wrapper.
- **Effort**: small (audit) → medium (sweep) — sizing depends on the audit count.
- **Codex verification (2026-05-18)**: Wrapper confirmed at planet.py:398-420 (start line was 398, not 382 — corrected). `planet_serde.py:160-162` confirmed as non-test dependent. Effort estimate revised; sweep footprint is materially larger than the original Phase-4f comment suggests.
- **Status as of 2026-05-19**: open. Wrapper is still at `planet.py:398-420`; `planet_serde.py:130-162` still reconstructs through it. Closed by **PROJ-449 Phase 3**.

---

## F-A-003 — `_ship_instance_init_with_legacy_kwargs` constructor wrapper (kept-with-rationale per PROJ-443 5b)
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/ship_instance.py:787-833`
- **Symbol**: `_ship_instance_init_with_legacy_kwargs`
- **Source refactor**: PROJ-436 Phase 3f, retained per PROJ-443 Phase 5b
- **What survived**: Same shape as F-A-002 — translates `consumable_levels=` / `cargo_contents=` kwargs to private-field spellings. Comment block at lines 797-804 documents the explicit retention rationale (18 test files would have to change).
- **Why it's a problem**: Compat shim that ought eventually to be retired in the same pass as F-A-002. Survives intentionally; no current bug; tracking visibility only.
- **Suggested action**: Reassess when F-A-002 ships — if the planet-side wrapper deletion sweep is small, this one is similar in shape and could be deleted in the same pass.
- **Effort**: medium (18-file test sweep) if eventually retired
- **Status as of 2026-05-19**: open. Wrapper still at `ship_instance.py:786-833`. Closed by **PROJ-449 Phase 4**. PROJ-443's 18-file audit-of-record is the input to Phase 0's verification rerun.

---

## F-A-004 — `Planet.stockpile` / `max_stockpile` / `staging_yard` Phase-4f deletion-shim @property cluster
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/planet.py:224-262`
- **Symbol**: `Planet.stockpile`, `Planet.max_stockpile`, `Planet.staging_yard` (+ their setters)
- **Source refactor**: PROJ-436 Phase 4f
- **What survived**: Three @property/@setter pairs that expose private `_stockpile`/`_max_stockpile`/`_staging_yard` under the public legacy names. The docstrings state these are "Phase 4f deletion shim" entries kept so test infrastructure that does `planet.stockpile[k] = v` keeps working. `planet_serde.py:53-55` also reads through these properties, so they are NOT purely a test surface.
- **Why it's a problem**: Three thin property pairs (~30 LOC) survive on Planet because deletion would force the test sweep in F-A-002. Production writers route through `IPlanetMutator` and the helper methods (`add_to_stockpile`, etc.) so the @property accessors are mostly read-paths plus test pokes.
- **Suggested action**: Bundle with F-A-002. Once the kwarg wrapper deletion sweep lands, also retire these three @property pairs and let `planet_serde` read directly from `_stockpile` / `_max_stockpile` / `_staging_yard`.
- **Effort**: small (mechanical, must land with F-A-002)
- **Status as of 2026-05-19**: open. Property cluster still at `planet.py:224-262`. Closed by **PROJ-449 Phase 3** alongside F-A-002.

---

## F-A-005 — `ShipInstance.consumable_levels` / `cargo_contents` Phase-3f deletion-shim @property cluster
- **Severity**: low
- **Category**: obsolete-code
- **File**: `game/strategy/data/ship_instance.py:237-262`
- **Symbol**: `ShipInstance.consumable_levels`, `ShipInstance.cargo_contents`
- **Source refactor**: PROJ-436 Phase 3f
- **What survived**: Same shape as F-A-004 on the ship side — @property/@setter pairs over `_consumable_levels` / `_cargo_contents`.
- **Why it's a problem**: Same as F-A-004.
- **Suggested action**: Bundle with F-A-003. The two ship-side shim clusters (kwarg wrapper + @property) retire together.
- **Effort**: small
- **Status as of 2026-05-19**: open. Property cluster still at `ship_instance.py:237-262`. Closed by **PROJ-449 Phase 4** alongside F-A-003.

---

## F-A-011 — `Empire.resource_pool` is a pure aggregation walked every read; Phase-0 D2 deferred caching
- **Severity**: low
- **Category**: missing-functionality
- **File**: `game/strategy/data/empire.py:228-249`
- **Symbol**: `Empire.resource_pool`
- **Source refactor**: PROJ-436 Phase 5 (deleted `_fleet_resource_pool`)
- **What survived**: Phase 5's commit comment explicitly says "Per Phase 0 D2 default this stays an uncached pure query; if post-Phase-5 profiling shows the aggregation is hot at large-empire scale, caching with explicit invalidation (PROJ-293 pattern) can land as a sibling sub-phase." No profiling has happened. Used by UI affordability checks (`Empire.has_resources`, `Empire.get_resource`).
- **Why it's a problem**: Documented missing-functionality / deferred decision. At large-empire scale (200+ colonies, several reads per UI frame), this walks every colony stockpile every call. Cheap until it's not.
- **Suggested action**: Profile under late-game save. If hot, add cache with explicit invalidation hooks on `Planet.add_to_stockpile` / `consume_from_stockpile` / `IPlanetMutator.set_stockpile_amount` and on `Empire.add_colony` / `remove_colony`.
- **Effort**: small (profile is the gate)
- **Status as of 2026-05-19**: open. Aggregation still walked uncached at `empire.py:228-249`. Closed by **PROJ-449 Phase 6** either way (code OR documented-defer-indefinitely).

---

## F-C-014 — `IShipInstance.cargo_contents` protocol surface kept as a writable dict view
- **Severity**: medium
- **Category**: obsolete-code
- **File**: `game/core/protocols/strategy_domain.py:208-233`
- **Symbol**: `IShipInstance.cargo_contents`
- **Source refactor**: PROJ-436 Phase 3f / Phase 6 audit
- **What survived**: Protocol member docstring explicitly states the property is "**not** read-only in absolute terms" because a concrete-class setter still exists for the legacy-kwarg constructor wrapper. Production code is told to "**prefer** the cargo manager API for writes."
- **Why it's a problem**: A protocol that says "this property exists, but please don't mutate it via the protocol" is a contract crack. Callers that narrow to `IShipInstance` get a read surface that quietly accepts writes. PROJ-443 Phase 5b explicitly retained the wrapper that's the reason for this; the protocol-side residue is the visible echo.
- **Suggested action**: Narrow the protocol to a read-only `Mapping[str, int]` view; if PROJ-443's deferred wrapper is removed, the concrete-class setter goes too. Until then, annotate the property with `Mapping[str, int]` instead of `Dict[str, int]` to at least communicate the intent in the type signature.
- **Effort**: tiny (type-annotation) or small (full migration)
- **Status as of 2026-05-19**: **partially-resolved**. PROJ-446 Phase 2 narrowed the annotation from `Dict[str, int]` to `Mapping[str, int]` (verified at `strategy_domain.py:208`). The "not read-only in absolute terms" caveat in the docstring (lines 219-224) is still present and explicitly says it will be dropped when "PROJ-444 wrapper retirement lands" — i.e. this project's Phase 4. **Completed by PROJ-449 Phase 5.**

---

## F-C-020 — `tests/fixtures/strategy_entities.py` still passes legacy `consumable_levels=` / `cargo_contents=` kwargs
- **Severity**: low
- **Category**: test-inconsistency
- **File**: `tests/fixtures/strategy_entities.py:140`, `:318`, `:320` (+ a 4th site at `:425` flagged by Codex r3)
- **Symbol**: `create_test_planetary_facility`, `create_test_ship_instance`, `create_test_empire` (the planet seed-reserve)
- **Source refactor**: PROJ-436 Phase 3f / PROJ-443 Phase 5b
- **What survived**: The shared fixture module passes `consumable_levels={...}` and `cargo_contents={...}` to `PlanetaryFacility(...)` and `ShipInstance(...)`. Works only because the `_ship_instance_init_with_legacy_kwargs` wrapper translates them; the wrapper was kept by PROJ-443 Phase 5b ("retain the wrapper... revisit only if introspection-based tooling starts depending on the field shape"). The 4th site at line 425 (`create_test_empire`'s seed-reserve helper) was flagged by Codex r3 — it constructs a hidden `_starting_reserve` colony with `stockpile=dict(seed_pool)`, hitting the Planet wrapper.
- **Why it's a problem**: The fixture module is the single largest shared site of the legacy-kwarg surface. Migrating it would unblock most of the PROJ-444 F-A-003 / F-A-005 wrapper retirement.
- **Suggested action**: Migrate the 4 fixture sites to the post-PROJ-436 private kwargs (`_cargo_contents=...` / `_consumable_levels=...` / `_stockpile=...`) or use the manager APIs. Then run the sharded suite to see how many direct callers still need migration; that number lets us decide whether the wrapper retirement is now in scope.
- **Effort**: tiny (fixture file) + small (downstream sweep)
- **CROSS-BUCKET CLASSIFICATION** (historical): STRUCTURAL JOINT-PHASE, not mere coordination. PROJ-444 + PROJ-446 owners deadlocked on this in the old layer-bucket partition. **Codex r4 redesign job 1 absorbs the seam** — PROJ-449 owns both the fixture migration and the wrapper deletion.
- **Status as of 2026-05-19**: open. Fixture file still hits the wrapper. Closed by **PROJ-449 Phase 1**.

---

## PROJ-443 Phase 5b carry-over

PROJ-443 Phase 5b (2026-05-17) attempted to delete `_ship_instance_init_with_legacy_kwargs`, hit a sharded-suite regression of "19 failures + 16 errors across 18 test files," and reverted both the wrapper deletion and the factory translation block. The decision-of-record:

> ~25 LOC wrapper carry-cost < 50+ site sweep cost. Cleanup deferred indefinitely; the wrapper has no production-runtime impact.

PROJ-449 reopens this with the post-PROJ-444..447 understanding that the audit-then-decide gate should run first (Phase 0). If the sweep size has not changed materially since 2026-05-17 (still ~18 files for the ShipInstance side), the project still proceeds — the new sequencing-by-job means that the planet-side and ship-side sweeps can happen together and the cost is amortized across both shim clusters, not just one.

Codex r4 rationale (job 1):
> Retire the `Planet`/`ShipInstance` legacy kwarg translators and property shims, migrate `tests/fixtures/strategy_entities.py` and `planet_serde`, then drop the `IShipInstance.cargo_contents` caveat. Closes `F-A-002/003/004/005`, `F-C-020`, completes `F-C-014`. Sequential. Depends on: none. Size: large.
