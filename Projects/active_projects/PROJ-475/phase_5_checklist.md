# Phase 5: End-of-project Codex-audit remediation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-475 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address the VERIFIED findings from the end-of-project Codex audit
(`AgentCoordination/Scratchpad/Consult/proj475_exec_audit/audit.md`). Each finding
was re-verified against live code and classified VERIFIED / REJECTED below.

## Audit findings — verification + disposition

- **Finding 1 (Medium) — VERIFIED.** The plan's deferred-reader table
  (`plan.md:140`) assigns the build-queue `compute_planet_production(...)` tail to
  PROJ-475 ("Migrate onto a facade production-projection query OR allowlist-with-reason
  if no clean query exists"), but no phase covered it; the two import-allowlist entries
  (`test_facade_read_path_imports_guard.py:172-173`) are still present, so "all phases
  complete" overstated the import-guard shrink. Disposition: the two call sites
  (`build_queue_panel_factory.py:247-249`, `build_queue_screen.py:321-323`) render LIVE
  `Planet`/`yard` domain objects the build-queue screen already holds and call a pure
  read-only calculator with `facade.session_meta.registries()` — there is no `.session`
  leak. A clean facade `production_rates` projection requires the live-`Planet`→DTO
  bridge that is PROJ-477's render/read-model boundary work (PROJ-477 plan already scopes
  `build_queue_screen`/`build_queue_controller` + `strategy_build_queue_manager`). Per
  the plan.md:140 fallback, KEEP these two imports **allowlisted-with-reason** and pin
  the intentional deferral; defer the clean migration to PROJ-477.

- **Finding 2 (Low) — VERIFIED.** The import-guard comment for the StrategyScreen
  `GameSession` import (`test_facade_read_path_imports_guard.py:235-237`) said
  "deprecation is PROJ-475", but the `session` getter (and its `GameSession` import in
  the test-swap setter) is deferred to PROJ-477. Documentation drift. Disposition: retag
  the comment to PROJ-477.

- **Finding 3 (Missing/weak tests) — VERIFIED (partial).** (a) the build-queue tail has
  no deferral pin (covered by Task 5.1). (b) defensive fallback branches are
  normal-path-only: `planet_slice._resolve_has_planetary_yard` `(AttributeError, TypeError)`,
  `ShipInfo.has_spaceyard` `(ValidationException, AttributeError)`,
  `fleet_report_window._build_spaceyard_lookup` degrade-to-`{}` — add coverage (Task 5.2).
  (c) `system_tree_panel.py:418-425` string-getattr `session` is **REJECTED for PROJ-475**:
  it is the explicitly PROJ-477-deferred getter consumer; pinning/closing it is PROJ-477
  Phase 1 (dynamic-getattr guard hardening). Not in 475 scope.

---

## Tasks

### Task 5.1: Pin the build-queue `compute_planet_production` deferral [Simple]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** the guard's own suite

- [x] Add an explanatory comment above the two `compute_planet_production` build-queue
      allowlist entries documenting the conscious PROJ-475 deferral-to-PROJ-477 (live
      `Planet` render object + pure calculator; no `.session` leak; clean migration needs
      PROJ-477's render/read-model bridge).
- [x] Add a regression test asserting both entries are present + intentional (so a
      future agent doesn't silently drop or re-scope them without updating the rationale).
- [x] Verify: import guard green.

**Notes:** Added `test_build_queue_compute_planet_production_deferral_is_intentional`
pinning both `(build_queue_panel_factory.py / build_queue_screen.py,
planet_economy_projector, compute_planet_production)` entries with the deferral rationale.

---

### Task 5.2: Cover the new defensive fallback branches [Simple]
**Files:** `tests/unit/strategy/facade/test_planet_has_build_yard.py`,
`tests/unit/strategy/facade/test_ship_has_spaceyard.py`,
`tests/unit/ui/screens/test_fleet_report_spaceyard_bridge.py`
**Tests:** those modules

- [x] FAILING-FIRST then GREEN: `_resolve_has_planetary_yard` returns `False` (not raise)
      when `colony_has_planetary_yard` raises `TypeError`/`AttributeError`.
- [x] `ShipInfo.has_spaceyard` degrades to `False` when the calc raises
      `ValidationException`/`AttributeError`.
- [x] `_build_spaceyard_lookup` degrades to `{}` when `facade.fleets.get` raises.
- [x] Verify: all three modules green.

**Notes:** Added one degrade-path test per surface.

---

### Task 5.3: Fix the stale import-guard comment (Finding 2) [Simple]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py:235-237`

- [x] Retag the StrategyScreen `GameSession` import comment from "deprecation is
      PROJ-475" to "session getter + this import deferred to PROJ-477".
- [x] Verify: import guard green.

**Notes:** Comment retagged.

---

## Phase Completion Checklist
- [x] All VERIFIED findings addressed; REJECTED ones recorded with rationale
- [x] Both read-path guards green; sharded suite green
- [x] Update status to `Complete`; update plan.md phase table + Current State
