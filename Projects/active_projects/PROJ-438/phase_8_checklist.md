# Phase 8: DTO / protocol / doc sync + Codex consult remediation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 8`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Doc-sync complete; **Codex consult pending user authorization** (separate cost — see plan.md Current State).
**Depends on:** PROJ-436 Phase 10 (docs) merged on `main` (commit `622e63055`, merged via `5c97f0903`).
**Objective:** Sync public seams and docs to the landed post-PROJ-438 reality, then run the required Codex consult and absorb verified findings.

---

## Tasks

### Task 8.0: Pull main + verify PROJ-436 Phase 10 landed
**Files:** repo state

- [x] `git pull origin main` — auto-merged with PROJ-438 Phases 0–7 commit `820d6d4b8` as merge commit `5c97f0903`. No conflicts; Phase 5 inline doc edits preserved.
- [x] Verified `622e63055 PROJ-436 Phase 10: doc refresh against unified Container substrate` and `9f822a38a PROJ-436 Phase 11: end-of-project Codex consult + finding disposition` are on main.
- [x] Post-merge baseline sharded suite: **23,268 passed / 0 failed / 0 errors / 2 skipped**.

### Task 8.1: Audit docs/protocol surfaces touched by PROJ-438 phases 1–7
**Files:** all `docs/` + `game/core/protocols/strategy_domain.py` + `strategy_mutators.py`

- [x] Grep target docs for `IssuePlanetOrderCommand`, `_handler_registry`, `execute_for_issuer`, `serializer_codec`, `restore_graph_wiring`, persistence-adapter rehydrate references. Result: 4 doc files need surgical edits; protocol files need no Phase 8 changes (Phase 3 already pinned `IShipInstance` shape; Phase 6's `execute_for_issuer` lives in `order_handlers/base.py` not in `core/protocols/`).

### Task 8.2: Doc surface sync (surgical)
**Files:** `docs/systems/strategy_layer.md`, `docs/systems/orders_system.md`, `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`

- [x] `strategy_layer.md`: SessionPersistenceAdapter row updated to mention the `restore_graph_wiring` collaborator; added a dedicated `restore_graph_wiring` row; expanded the Rehydrate parity paragraph (now PROJ-432 + PROJ-438 Phase 1) to document the shared collaborator + the DesignCatalog asymmetry; added Issuer-aware execution contract paragraph (Phase 6) after the OrderProcessor section.
- [x] `orders_system.md`: added "Issuer-aware execution contract (PROJ-438 Phase 6)" section and "Metadata-driven serialization lookup (PROJ-438 Phase 7)" section after the Planet Ability Orders block. Phase 5 inline updates from the original commit preserved.
- [x] `01_ARCHITECTURE.md`: SessionPersistenceAdapter bullet updated to mention the `restore_graph_wiring` collaborator and the intentional DesignCatalog asymmetry.
- [x] `02_PATTERNS.md`: tightened the `execute_for_issuer` signature from the loose `(adapter, order, ...)` to the canonical 5-kwarg PROJ-438 Phase 6 form.
- [x] No protocol-file changes needed (see Task 8.1 audit conclusion).

### Task 8.3: Required Codex consult on landed PROJ-438 work
**Files:** consult artifact under `AgentCoordination/Scratchpad/...` or `Reviews/results/...`

- [ ] **Pending user authorization** — external cost (codex API tokens). Per CLAUDE.md feedback memory, end-of-project consult is required. Verified findings become added phases 9+, 10+; out-of-scope / unverified findings logged in `decisions.md`.

### Task 8.4: Sharded suite + validate_phase
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded suite green after merge (23,268 passed / 0 failed / 0 errors / 2 skipped).
- [ ] Final pass after Phase 8.3 consult remediation.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] Doc-sync subset of tasks complete
- [x] `python Tools/test_sharded/test_sharded.py` green
- [ ] Required Codex consult run + verified findings absorbed (pending user authorization)
- [x] Update status at top of this file to reflect partial completion
- [x] Update plan.md phase table row to reflect partial completion
- [x] Update plan.md Current State to call out Codex consult authorization
- [ ] `python Projects/scripts/validate_phase.py PROJ-438 8` passes
