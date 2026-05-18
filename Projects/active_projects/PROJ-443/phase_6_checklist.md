# Phase 6: Codex consult + verified-finding remediation

**Status:** Complete (2026-05-18, HEAD pending commit)
**Depends on:** phase_5
**Review Mode:** standard
**Files:**
- `game/strategy/engine/movement_phase_collaborator.py` (1 file changed; trigger_speed_recalculation added to `_prune_destroyed_fleet_contents`)
- `tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py` (RED test added pinning the invariant)
- `Projects/active_projects/PROJ-443/decisions.md` (consult findings + remediation ledger)

**Consult artifact:** `AgentCoordination/Scratchpad/Consult/20260518T053255Z_proj443-final/response.md`

---

## Tasks

### Task 6.1: Run Codex consult [Complete]

- [x] Invoked `claude-consult --with codex --mode pre-final-check --allow-tests` with a corrected framing (charter framing referenced `--ignore=./data` which we didn't add, and the regression-guard filename is `test_no_hidden_test_files.py`). 7 primary questions covering: norecursedirs audit, regression-guard AST filter soundness, Fleet Protocol-compliance forwarding, PROJ-370 boundary allowlist additions, planet.py LOC drift, addopts `--ignore=combat_lab` cwd-relativity, Phase 5b wrapper retention.
- [x] Response read in full. 11 findings: 1 MUST-FIX-NOW, 6 SHOULD-FIX-FOLLOWUP, 4 ACCEPT-AS-IS.

### Task 6.2: Verify findings against code [Complete]

- [x] **MUST-FIX-NOW finding (d.1)** verified: `movement_phase_collaborator.py:165-176` does mutate `fleet.ships` in place without calling `trigger_speed_recalculation()` or going through `Fleet.remove_ship()`. The fleet-speed invariant at `test_fleet_speed_invariants.py:3-7,21-22` is documented and `Fleet.remove_ship` at `fleet.py:202-208` shows the canonical recalc-paired pattern. Codex's claim holds.
- [x] **SHOULD-FIX-FOLLOWUP findings (d.2-d.4, e, f, g)** verified for accuracy; logged in `decisions.md` with rationale for deferring.
- [x] **ACCEPT-AS-IS findings (a, b, c, e galaxy_protocols)** confirmed; no action.

### Task 6.3: Author remediation sub-phases [Complete]

- [x] **6a — Fix `_prune_destroyed_fleet_contents` to honor the fleet-speed invariant.** Only sub-phase needed; the other consult findings deferred to follow-up per the project's bounded-scope preference (and documented in `decisions.md` for Phase 6 reviewer / next project).

### Task 6.4: Execute remediation — 6a [Complete]

- [x] **RED**: Added `test_resolve_after_prune_path_triggers_speed_recalculation` (`tests/unit/strategy/turn_engine/test_movement_phase_collaborator.py`). The `_SpyFleet` class records `trigger_speed_recalculation` calls; the test sets up a fleet with `[ship_kept, ship_lost]`, configures the resolver to destroy only `ship_lost`, and asserts both that `ship_kept` remains AND that `trigger_speed_recalculation` was called exactly once. Pre-fix run: FAILED with `trigger_calls == 0`.
- [x] **GREEN**: Updated `_prune_destroyed_fleet_contents` in `movement_phase_collaborator.py`: compute `survivors` from the filter, branch on `len(survivors) != len(fleet.ships)`, and call `fleet.trigger_speed_recalculation()` via `getattr(fleet, "trigger_speed_recalculation", None)` so existing `SimpleNamespace` fleet doubles in sibling tests continue to pass. Post-fix run: 7/7 green in the collaborator file.
- [x] Sharded suite re-verified at 23186 / 23184 passed / 0 failed / 0 errors / 2 skipped. No regression.

### Task 6.5: Document deferred findings [Complete]

- [x] `decisions.md` 2026-05-18 row "Phase 6 Codex consult findings + remediation" records all 11 findings with classification and per-finding rationale.

---

## Phase Completion Checklist
- [x] Codex consult run; response read; verdicts logged
- [x] MUST-FIX-NOW finding remediated (1 production touch in `movement_phase_collaborator.py` + 1 new pinning test)
- [x] SHOULD-FIX-FOLLOWUP findings logged in `decisions.md` for next project / phase 6 reviewer
- [x] Sharded suite green (23186/23184)
- [x] Project ready for final audit + user verification
- [x] `plan.md` updated
- [ ] **Final user action required**: apply the `verified` label and close the project per the project's authority constraint ("agents may set status:awaiting-confirmation, but only the user applies the verified label and closes the issue" — `CLAUDE.md`).
