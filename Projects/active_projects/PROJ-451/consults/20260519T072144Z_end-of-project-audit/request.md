---
protocol: consult/v1
from: claude
to: codex
mode: planning
allow_tests: false
created_at_utc: 2026-05-19T07:21:44Z
repo_root: <runtime-discovered>
consult_leaf: <runtime-discovered>
complete: true
---

# PROJ-451 — End-of-Project Audit Consult

## Context

PROJ-451 ("Production resource-consumption semantics — DI-006 + DI-007 engine half") closed all 4 phases on the `group-a` branch. The project closed the engine-side residue of the affordability/consumption symmetry contract that PROJ-436 Phase 12 tightened and that PROJ-444 Phase 2 had only partially closed on the data side.

What this project did:

- **Phase 1 (RED reproduction)**: added 3 xfail-strict tests reproducing (a) the engine-call-level rounded-to-zero stall and (b) the queue-tick-loop stall — none of them emitted `RESOURCE_SHORTAGE` pre-fix. Plus a unit test reproducing the zero-consume / no-diff path inside `_apply_resource_consumption`.

- **Phase 2 (GREEN)**:
  - Task 2.0 closed the DI-006 data-half asymmetry. `Fleet.consume_cargo_resource` at `game/strategy/data/fleet.py:285` now does `int(round(amount))` symmetric to `has_cargo_resources` at `:267`. New symmetry ratchet at `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py`.
  - Task 2.1 added `_log_zero_consume_shortage` (sibling to `_log_resource_shortage`) in `production_engine.py`. `_apply_resource_consumption` now collects resources where `actually_consumed == 0` despite `amount > 0` and emits `RESOURCE_SHORTAGE` with `cause="rounded_to_zero"`. Respects `item['_shortage_logged']` to avoid duplicate emits.
  - Task 2.2 removed xfail markers from the 3 Phase 1 RED tests.
  - Task 2.5 updated `production_engine.py` module docstring to drop the pre-PROJ-436 "empire pool" framing.
  - Side fix: the `colony` fixture in `tests/unit/strategy/engine/test_production_refactor.py` now mutates the stockpile dict in `production_consume_resource` (previously a MagicMock no-op caused the new zero-consume detection to fire spuriously in `test_no_shortage_event_when_affordable`).

- **Phase 3 (DI-007 closure, option B)**: per Codex r4 and CLAUDE.md "Capability validation is hard, not soft", added `assert consume_succeeded, "Contract breach: ..."` in `_apply_resource_consumption` right after the `production_consume_resource` call. The Protocol contract docstring at `production_engine.py:65-99` already carries MUST-language with DI-006/007 references. New test `test_apply_resource_consumption_raises_on_contract_breach`. Side fix: the `_make_colony` helper in `tests/unit/strategy/production_engine/test_paused_queue.py` now returns bool from `consume_from_stockpile` to mirror real `Planet`.

- **Phase 4 (ratchet)**: new file `tests/unit/strategy/data/test_production_resource_source_ratchet.py` with 17 parametrized + class-grouped cases that pin `has_resources(costs)==True → consume(resource, amount)==True` for Planet (float stockpile) and Fleet (integer cargo with `int(round(...))` rounding). Defense-in-depth alongside Phase 3's engine assertion.

What this project did NOT do (deliberately):

- It did NOT widen the cargo store typing to floats (that was Option A from PROJ-444; Option B was chosen).
- It did NOT touch `Planet.has_stockpile` or `Planet.consume_from_stockpile` (already symmetric).
- It did NOT affect wrapper retirement (PROJ-449) or staging-yard substrate (PROJ-450).

Final sharded baseline: **23395 tests / 23395 passed / 0 failed / 0 errors**.

## Files modified across the 4 phases

- `game/strategy/data/fleet.py` — `consume_cargo_resource` gate rounded (Phase 2 Task 2.0)
- `game/strategy/engine/production_engine.py` — module docstring, `_apply_resource_consumption` (zero-consume detection + strict assertion), new `_log_zero_consume_shortage` (Phase 2 Task 2.1 + Phase 3)
- `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py` (new) — Phase 2 Task 2.0 ratchet
- `tests/unit/strategy/data/test_production_resource_source_ratchet.py` (new) — Phase 4 implementer ratchet
- `tests/integration/test_production_engine_fractional_fleet_cost.py` — Phase 1 RED → Phase 2 GREEN
- `tests/unit/strategy/engine/test_production_engine_consumption.py` — Phase 1 RED zero-consume + Phase 3 contract-breach
- `tests/unit/strategy/engine/test_production_refactor.py` — colony fixture realism fix (consume mutates dict)
- `tests/unit/strategy/production_engine/test_paused_queue.py` — `_make_colony` helper bool return

## Commit range on `origin/group-a`

```
abb2676f3 PROJ-451 Phase 1 RED: reproduction tests for DI-006 engine UX gap + zero-consume detection
453fd6d68 PROJ-451 Phase 2 GREEN: close DI-006 data + engine halves
5d4628e10 PROJ-451 Phase 3 (option B): close DI-2026-05-18-007 with strict assertion
8b099ba60 PROJ-451 Phase 4: implementer ratchet for IProductionResourceSource (closes F-B-019)
```

## What I want you to do

Audit the closed project end-to-end. Four things I most want a second opinion on:

### 1. Verify each finding's closure status against current HEAD

- **DI-2026-05-18-006 data half**: confirm `fleet.py:285` now does `int(round(amount))` and matches `:267`. Confirm the symmetry ratchet at `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py` covers the key cases.
- **DI-2026-05-18-006 engine UX gap**: confirm `_apply_resource_consumption` in `production_engine.py` collects zero-consume resources and emits `RESOURCE_SHORTAGE` with `cause="rounded_to_zero"`. Confirm the new `_log_zero_consume_shortage` method.
- **DI-2026-05-18-007**: confirm the assertion `assert consume_succeeded, "Contract breach: ..."` is in place right after the `production_consume_resource` call.
- **F-B-019**: confirm the Protocol contract docstring at `production_engine.py:65-99` carries MUST-language and that the engine enforces it.

### 2. Spot-check the test changes for over-mocking

Two fixture updates (`test_production_refactor.py::colony` and `test_paused_queue.py::_make_colony`) were forced by the new contract enforcement. Are they realistic mirrors of real-Planet behavior, or did they accidentally hide a real bug? Specifically: do they correctly compose with the engine's truth-up diff math (Phase 12)?

### 3. Look for residue / missed sites

- Are there other `IProductionResourceSource` implementers besides Planet and Fleet that should also satisfy the ratchet?
- Is there any test that mocks `production_consume_resource` returning None / no-op MagicMock that the new assertion would catch as a contract breach? (Beyond the 2 fixture sites I already migrated.)
- The Phase 2 zero-consume detection compares with `actually_consumed == 0` (exact float). Could float precision cause false positives where the actual consume produced a tiny non-zero diff that rounds to 0? If so, suggest the right tolerance.

### 4. Identify nearby residue

Look at `game/strategy/engine/production_engine.py` for other comments, docstrings, or branches that are pre-PROJ-436 and now stale. The Phase 2 Task 2.5 polish covered the module docstring; are there other locations (method docstrings, comment headers, etc.) that still carry the old "empire pool" / `context_type` framing?

## Output schema

Standard consult/v1 response.md per the harmonized schema:

- `## Findings` — per concern. Each must cite `file:line` evidence. Label unverified claims `[unverified]`.
- `## Risks` — anything that might break later.
- `## Open questions` — anything you couldn't answer from read-only inspection. Don't speculate.
- Set `exit_status: ok` if no blockers; `exit_status: needs-fixes` if the audit found a verified issue that requires code change before the project closes.

## Constraints

(Inline-include the canonical Constraints block from `AgentCoordination/protocols/consult_prompt_block.md`.)

- Strict TDD: identify failing tests first; don't propose code that bypasses this.
- Documentation first: reference `docs/` as source of truth; never read or cite `docs/_ignore/`.
- No backward-compat shims, monkey patches, fallback systems, or save-file migrations.
- Respect layer boundaries (per `docs/01_ARCHITECTURE.md`, `docs/02_PATTERNS.md`).
- Do NOT revert unrelated user changes; work around existing dirty state.
- Evidence standard: cite `file:line`, command output, or transcript. Label unverified claims `[unverified]`.
- Final ownership: the initiator owns synthesis. You advise; you do NOT implement.
- Follow-up rule: the initiator may ask follow-ups. You stop when advice converges or repeats.
- Permission contract: read repo, run tests only when `allow_tests: true` AND the mode is `pre-final-check` or `deep-dive`, write only inside the directory named by `consult_leaf` in the request frontmatter. Do NOT edit production code, docs, tickets, projects, configs, commits, branches, or PRs.

This consult has `allow_tests: false` and `mode: planning` — read-only inspection only.
