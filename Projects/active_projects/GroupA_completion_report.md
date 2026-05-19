# Group A Completion Report

> Branch: `group-a` (merged into `main` for the final time at SHA `9ef0e1878`)
> Date completed: 2026-05-19
> Executing agent: Claude (Opus 4.7) running on this machine
> Cross-group state observed at last fetch: Group B has merged PROJ-453/454/456 to `main`; PROJ-457 still in planning. Group C state on `origin/main` not directly inspected.

---

## 1. Projects landed (merge SHAs)

| Project | Title | Phases | End-of-project merge SHA |
|---------|-------|--------|---------------------------|
| **PROJ-449** | Strategy entity wrapper retirement (Planet + ShipInstance kwarg/property cluster) | 7 (Phase 0 + Phases 1-6) | `ebb5c0e7f` |
| **PROJ-451** | Production resource-consumption semantics (DI-006 + DI-007 engine half) | 4 (Phases 1-4) | `893482c04` |
| **PROJ-459** | Strategy data LOC extractions (fleet_serde + planet_gen split + ship_instance LOC decision) | 4 (Phase 0 + Phases 1-3) | `2574d5000` |
| **PROJ-450** | Typed staging-yard substrate completion | 6 (Phase 0 + Phases 1-5) | `9ef0e1878` |

### PROJ-449 — Wrapper retirement (closed `ebb5c0e7f`)

- Phases 0-6 all Complete in Quick Status table.
- F-A-002 (Planet wrapper), F-A-003 (ShipInstance wrapper), F-A-004 (Planet setter cluster), F-A-005 (ShipInstance setter cluster), F-C-014 (IShipInstance.cargo_contents docstring), F-A-011 (Empire.resource_pool profile) all closed.
- F-A-012 deferred (PlanetaryFacility public field — future project).
- F-A-007 deferred (ship_instance.py at 783 LOC after this project — decision passed to PROJ-459 Phase 3).
- **Phase 3 scope adjustment**: kept read-only @property getters (audit had under-counted ~16 production + ~50 test read sites). Deleted only setters + wrapper. Documented in decisions.md.
- Sharded landing baseline: 23375/23375 green.

### PROJ-451 — Production resource-consumption (closed `893482c04`)

- Phases 1-4 all Complete.
- DI-2026-05-18-006 (data half + engine UX gap), DI-2026-05-18-007 (engine bool-return), F-B-019 (Protocol contract) all closed.
- Phase 3 decision: **option B (strict assertion)** chosen per Codex r4 + CLAUDE.md "Capability validation is hard, not soft."
- Sharded landing baseline: 23395/23395 green (post-audit-fix bumped to 23394 after rebase).

### PROJ-459 — LOC extractions (closed `2574d5000`)

- Phases 0-3 all Complete.
- F-A-008 (fleet_serde extraction) closed via Phase 1 — `fleet.py` 693→632 LOC; `fleet_serde.py` 168 LOC; new characterization test.
- F-A-009 (planet_gen split) closed via Phase 2 — `planet_gen.py` 610→427 LOC (under 500 ceiling); new `planet_gen_surface.py` 236 LOC.
- F-A-007 (ship_instance LOC) **SPUN OUT as PROJ-461** — 789 LOC > 500. Verdict-only here.
- Doc-consolidation staged at `_doc_consolidation/PROJ-459_pending.md`. Not the last finisher; PROJ-457/460 will consolidate.

### PROJ-450 — Typed staging-yard substrate (closed `9ef0e1878`)

- Phases 0-5 all Complete.
- F-B-013 (staging-yard substrate widening) FULLY CLOSED. DI-2026-05-18-001 substrate half FULLY CLOSED.
- Phase 1: Path A engine API cleanup (typed accept + typed pop, 3 helpers moved into Planet).
- Phase 2: substrate widened `_staging_yard: List[CarriedVehicle | DropPod]`; serde normalize/emit.
- Phase 3: bridge replaced with permanent typed read-only `Planet.staging_yard -> tuple[CarriedVehicle | DropPod, ...]`. UI/DTO/validator/write-service tightened.
- Phase 4: 6 integration-test mutation sites migrated to typed.
- Phase 5: static guard added.
- Sharded landing baseline: 23413/23413 green (post audit fix).
- All 3 Stage 3 preflight blockers closed.

---

## 2. Per-project codex audit outcomes

| Project | Audit verdict | Verified issues | Extra phases spawned | Disputes filed |
|---------|---------------|-----------------|----------------------|----------------|
| PROJ-449 | `needs-fixes` | 2 (lying docstrings in `ship_instance.py:106-125` + `:241-244`) | 0 — handled as docstring fixes in the same merge | None |
| PROJ-451 | `ok` | 1 latent (paused-queue fleet fixture returns None) | 0 — proactive fix in same merge | None |
| PROJ-459 | `needs-fixes` | 2 (PROJ-459 findings.md "1-line facade" claim; PROJ-461 plan.md template-y) | 0 — handled as doc fixes in same merge | Disputed codex's LOC measurement of 655 for `ship_instance.py` (my `wc -l` and Python `sum(1 for _ in open(...))` both give 789; codex's tool strips blanks/comments). Recorded in decisions.md. |
| PROJ-450 | `needs-fixes` | 1 verified blocker (`TransferValidator._validate_load` rejected tuple from real `Planet.staging_yard`); 8 non-blocker observations (stale comments, ceiling headroom). | 0 — blocker fixed in same merge + new regression test added (`TestDropPodTransferAgainstRealPlanet`); ceiling reset 525→520; non-blockers deferred. | None |

Consult-leaf paths (all under `Projects/active_projects/PROJ-<N>/consults/<UTC-ts>_end-of-project-audit/`):

- `PROJ-449/consults/20260519T061346Z_end-of-project-audit/`
- `PROJ-451/consults/20260519T072144Z_end-of-project-audit/`
- `PROJ-459/consults/20260519T080236Z_end-of-project-audit/`
- `PROJ-450/consults/20260519T092428Z_end-of-project-audit/`

All four codex responses came back as `needs-fixes` or `ok`; the validator (which only accepts the literal string `"ok"` as exit_status) rejected the three `needs-fixes` responses to `.invalid-output-*.txt` files. Per protocol §10 the workflow handled this by copying the invalid response to `response.md` after manual verification — all four audit response.md files are now in their leaf directories and committed.

---

## 3. `ship_instance.py` LOC trail for the F-A-007 decision (PROJ-459 Phase 3)

| Stage | LOC | Notes |
|-------|-----|-------|
| Pre-Group-A (2026-05-18 baseline) | 839 | Per PROJ-459 plan.md historical baseline. |
| Post-PROJ-449 Phase 4 | 783 | After wrapper + 2 setters deleted; read-only getters retained. Recorded in PROJ-449 decisions.md. |
| Post-PROJ-449 Phase 5 + final audit fixes | 789 | Docstring restoration; static guards added. PROJ-459 Phase 0 measurement. |
| Post-Group-B PROJ-454 (component_inspector retirement, function-local imports removed) | 789 | No measurable delta from PROJ-454 in my local checkout (Codex r5 anticipated ~3-5 LOC). |
| **Phase 3 verdict** | **789 (+289 over 500 ceiling)** | **SPINOUT to PROJ-461** per Codex r4 directive. |

PROJ-461 created at `Projects/active_projects/PROJ-461/` with populated plan.md (scope-audit Phase 1 spec'd) and findings carrying F-A-007 verbatim.

---

## 4. discovered_issues/log.jsonl entries appended during execution

None. Group A did not surface any out-of-scope residue worth logging. All issues encountered during execution were either in-scope for the current phase, deferred per documented decision rows, or routed through codex audit findings.

---

## 5. Doc-consolidation outcome

- Group A's pending doc edits are staged at `Projects/active_projects/_doc_consolidation/PROJ-459_pending.md` per protocol §9.
- At end-of-Group-A (PROJ-450 close), `git ls-tree origin/main _doc_consolidation/` showed only `PROJ-459_pending.md` and the `README.md`. PROJ-457 (Group B) and PROJ-460 (Group C) had NOT yet staged their pending files.
- **Group A is NOT the last finisher.** Per protocol §9.2, I left `PROJ-459_pending.md` in place and closed PROJ-459 without applying any consolidated doc edit.
- The last of PROJ-457/PROJ-460 (whichever finishes last and sees all three pending files on `origin/main`) applies the consolidated edit to `docs/01_ARCHITECTURE.md` + `docs/02_PATTERNS.md`.

---

## 6. Unresolved sync-gate timeouts

None. PROJ-450's Phase 0 cross-group sync gate (PROJ-454 + PROJ-456) cleared on first check — both Group B projects were already Complete on `origin/main` by the time Group A reached PROJ-450 (last in serial order).

---

## 7. Cross-group communication notes

### For Group B (PROJ-457)

- PROJ-457 staged doc edits should be added to `Projects/active_projects/_doc_consolidation/PROJ-457_pending.md`.
- When PROJ-457 closes, check the `_doc_consolidation/` directory state: if both PROJ-459 (already there) and PROJ-460 are present, PROJ-457 is the last finisher and consolidates per protocol §9.2.

### For Group C (PROJ-460)

- Same instructions: stage doc edits to `_doc_consolidation/PROJ-460_pending.md`.
- Last finisher of PROJ-457/PROJ-460 owns the consolidated doc edit.

### General observations

- The cross-group sync gate model (PROJ-450 last; verify Group B Complete on `origin/main` before Phase 1) worked cleanly — no manual coordination needed.
- The `response.md.invalid-output-*.txt` pattern from codex consults: the validator rejects `exit_status: needs-fixes` even though `needs-fixes` is the documented schema value. Workflow: the response content is correct; just `cp` the file to `response.md` and proceed. This may be worth a follow-up fix to the validator if other groups hit it.
- The codex tool reports lower LOC counts than `wc -l` (strips blanks/comments?). PROJ-459 audit cited 655 LOC for `ship_instance.py` vs my `wc -l` count of 789. Trust `wc -l` / Python `sum(1 for _ in open(...))` for the authoritative count.

---

## 8. Group A sharded test count progression

| Milestone | Sharded count |
|-----------|---------------|
| Group A start (baseline) | 23368 / 23368 |
| PROJ-449 close | 23375 / 23375 |
| Post Group B PROJ-454 merge (rebased) | 23370 / 23370 (PROJ-454 deletions/renames netted -5) |
| PROJ-451 close | 23395 / 23395 |
| Post-rebase / pre-PROJ-459 | 23394 / 23394 |
| PROJ-459 close | 23397 / 23397 |
| PROJ-450 Phase 1 | 23406 / 23406 |
| PROJ-450 Phase 2 | 23409 / 23409 |
| PROJ-450 Phase 3 | 23411 / 23411 |
| PROJ-450 Phase 4 | 23411 / 23411 (test migrations; no test count delta) |
| PROJ-450 Phase 5 + audit fix | 23413 / 23413 |

Net: Group A added **+45 tests** to the sharded suite while shipping **4 production-side projects** across the strategy data / engine / facade / UI layers.

---

## 9. New projects scaffolded during execution

| ID | Title | Created by | State at close |
|----|-------|------------|-----------------|
| PROJ-461 | ShipInstance LOC reduction (F-A-007 spinout from PROJ-459) | PROJ-459 Phase 3 verdict | Scaffolded; phase_1_checklist scoped to a caller-audit Phase 1; plan.md populated; findings carry F-A-007 verbatim. Awaiting independent execution. |

---

## 10. Files / project locations

All Group A artifacts merged into `main` at SHA `9ef0e1878`. See:

- `Projects/active_projects/PROJ-449/` (full project + consults)
- `Projects/active_projects/PROJ-451/` (full project + consults)
- `Projects/active_projects/PROJ-459/` (full project + consults)
- `Projects/active_projects/PROJ-450/` (full project + consults)
- `Projects/active_projects/PROJ-461/` (new spinout project, scaffold only)
- `Projects/active_projects/_doc_consolidation/PROJ-459_pending.md` (staged; awaits last-finisher consolidation)

---

**Group A serial execution complete.**
