# Phase 4: Closeout + cross-links + review cycle

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-379 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):**
- `Projects/active_projects/PROJ-377/decisions.md` (modify — append "MIN-002 resolved by PROJ-379" cross-link row)
- `Projects/active_projects/PROJ-379/decisions.md` (modify — final closeout row capturing review outcome)

**Objective:** Cross-link PROJ-377 → PROJ-379 so the audit trail closes; submit the OpenCode review; dispatch the verifier subagent; apply remediations.

---

## Tasks

### Task 4.1: Append PROJ-377 cross-link row [Simple]
**File:** `Projects/active_projects/PROJ-377/decisions.md`
**Tests:** N/A

- [ ] Append a row dated 2026-05-XX (closeout date) to `Projects/active_projects/PROJ-377/decisions.md`:
  > **PROJ-379 closeout: MIN-002 (capture-script double-seed fragility) RESOLVED.** PROJ-379 replaced `tests/fixtures/saves/_capture_baseline.py` with a hand-built fixture builder (`tests/fixtures/saves/_build_galaxy_fixture.py`) that constructs `Galaxy` / `StarSystem` / `Planet` / `WarpPoint` directly via `__init__` and routes through `Galaxy._registry.add_system()` / `register_planet()`. Re-runs are byte-identical across processes (Phase 2 enforces via subprocess + `PYTHONHASHSEED` tests). A new field-coverage guard at `tests/integration/strategy/test_golden_fixture_field_coverage.py` calls `planet_to_dict(_minimal_planet())` for the per-key serialized-default baseline, then asserts every emitted key (modulo `image_id`/`image_rotation` skiplist) has a non-default value somewhere in the populated fixture. Old capture script deleted. | The MIN-002 deferral in the 2026-05-07 row above is now cleared; the docstring caveat in `_capture_baseline.py` is gone with the file. PROJ-379 plan / decisions / manifest at `Projects/active_projects/PROJ-379/`. |
- [ ] **Verify:** PROJ-377 plan.md and decisions.md remain mutually consistent — no stale "MIN-002 deferred" claims.

**Notes:**

### Task 4.2: Submit OpenCode review request [Medium]
**File:** N/A — review dispatch
**Tests:** N/A

- [ ] Run pre-flight: confirm review daemon is running per `.claude/skills/claude-delegate-review/SKILL.md` (check PID file at `AgentCoordination/opencodereview/local/review_daemon.pid`).
- [ ] Compose review request payload listing in-scope commits (Phase 1, 2, 3 SHAs), in-scope files (`_build_galaxy_fixture.py`, regenerated JSONs, `test_save_round_trip.py` modifications, `test_golden_fixture_field_coverage.py`, deleted `_capture_baseline.py`, PROJ-377 cross-link), and 6-8 specific focus areas:
  1. Byte-determinism of `_build_galaxy_fixture.py` across two consecutive invocations and across processes (with `PYTHONHASHSEED=random`).
  2. Round-trip identity preservation for both regenerated fixtures.
  3. Field-coverage guard correctness — does `planet_to_dict(_minimal_planet())` produce the expected emitted-keys set? Does the per-key default comparison handle `default_factory` (mutable empties) and enum-name serialization (e.g., `PlanetType.BARREN` → `"BARREN"`) correctly?
  4. Skiplist scope (`image_id`, `image_rotation`) — is it justified and documented?
  5. Production registration paths preserved — fixtures route through `_registry.add_system()` / `register_planet()`, and `system.planets.append(planet)` is called for each planet (not just `register_planet`)?
  6. PROJ-377 cross-link consistency — is MIN-002 truly resolved, or does any docstring / decisions row still imply best-effort?
  7. No `set` iteration in fixture builder — confirm via inspection that builder uses lists/tuples for ordered fields. Phase 2 subprocess tests must demonstrate byte-equality across multiple `PYTHONHASHSEED` values.
  8. Test growth — sharded delta should be exactly +7 (Phase 1: 4 in `test_save_round_trip.py` + 1 in `test_golden_fixture_field_coverage.py`; Phase 2: 2 in `test_save_round_trip.py`).
- [ ] Submit via `python Tools/agent_coordination/create_review_request.py --payload-file <path>`. Capture request id.
- [ ] Update PROJ-379 `decisions.md` with the review request id.

**Notes:**

### Task 4.3: Dispatch verifier subagent [Medium]
**File:** N/A — verifier dispatch
**Tests:** N/A

- [ ] Wait for OpenCode review to complete (poll `AgentCoordination/opencodereview/completed_review_requests/req_<id>.md`).
- [ ] Read the report; spawn a verifier subagent (`general-purpose`) with the standard verifier prompt template (see `Projects/protocols/03c_phase_aware_execution.md` or prior project closeouts for the canonical shape):
  - Verify each MAJ / MIN finding independently with CONFIRM / REJECT / UNCERTAIN.
  - Spot-check the most load-bearing INFO findings.
  - Independent sweep: re-grep for `_capture_baseline` (should be zero in production paths); re-run the field-coverage guard on the populated fixture.
  - Write `verifier_report.md` next to the OpenCode `report.md`.
- [ ] Read the verifier's summary; apply confirmed "fix now" remediations; defer "fix later" items.

**Notes:**

### Task 4.4: Apply remediations + final closeout commit [Simple — usually]
**File:** depends on remediations
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Apply each verifier-confirmed "fix now" recommendation. Run focused tests after each.
- [ ] Update `Projects/active_projects/PROJ-379/decisions.md` with a final closeout row capturing: review request id, finding counts (CRIT/MAJ/MIN/INFO), remediations applied vs. deferred, links to `report.md` and `verifier_report.md`.
- [ ] Sharded suite green at HEAD.
- [ ] Commit: `PROJ-379 review remediation: <summary>` (only if remediations applied) OR `PROJ-379 closeout: log OpenCode review + verifier outcome` (if no remediations needed).

**Notes:**

### Task 4.5: Update plan.md Quick Status to Complete [Simple]
**File:** `Projects/active_projects/PROJ-379/plan.md`

- [ ] Update Quick Status row 4 (Phase 4) to `Complete`.
- [ ] Update Current State to "All phases complete; ready for user verification" or similar.
- [ ] Update Audit Log with cycle 1 (date, OpenCode finding count, resolution summary).
- [ ] Update Completion Checklist boxes that are now achievable.

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] PROJ-377 `decisions.md` has the cross-link row pointing at PROJ-379.
- [ ] OpenCode review dispatched, completed, verified.
- [ ] Remediations applied (if any) or deferred with rationale.
- [ ] Sharded suite green at HEAD; pass count = pre-PROJ-379 baseline + 7.
- [ ] PROJ-379 `decisions.md` final closeout row appended.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to "All phases complete; ready for user verification".
