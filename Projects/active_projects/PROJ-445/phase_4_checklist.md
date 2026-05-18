# PROJ-445 Phase 4: Service-layer shim retirement + PROJ-368 facade unwinding

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-445 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** Phases 1-3 complete
**Objective:** Retire the two deferred service-layer re-export shims (`effect_ability_metadata.py`, `component_inspector.py`) that PROJ-429 and PROJ-433 explicitly kept as caller-migration shims. Then unwind PROJ-368's half-finished facade migration (F-B-017 + F-B-018) — the concrete handler signatures already match the unified Protocol; the residue is the facade-side reshape of `OrderExecutionResult` back into pre-PROJ-368 typed result dataclasses.

**Cross-bucket file-ownership rule:** Only edit `game/strategy/engine/`, `game/strategy/services/`, and engine/services-subject tests. Migration of caller imports may reach into `game/ui/` callers via `git grep` — only update import statements, do NOT refactor UI behavior. If UI behavior changes are needed, coordinate with PROJ-446.

**Source-of-truth findings:** [`findings/bucket_b_engine_services_scan.md`](findings/bucket_b_engine_services_scan.md) — F-B-004, F-B-005, F-B-017 (revised per Codex 2026-05-18 — see finding for the corrected framing), F-B-018.

---

## Tasks

### Task 4.1: F-B-004 — Retire effect_ability_metadata.py shim [Medium]
**File:** `game/strategy/services/effect_ability_metadata.py:1-131` (delete entire module); migrate 2 callers
**Tests:** `pytest tests/unit/strategy/services/ tests/integration/ -v`

- [ ] Read the existing shim module — it's 131 LOC of pure delegation to `ability_metadata.py`. Header documents the deferral.
- [ ] **Audit callers**: `git grep -n "from game.strategy.services.effect_ability_metadata import"`. Expected: 2 callers per the finding text (`system_effects_collector.py:42-45`, `effect_ability_display.py` — transitive).
- [ ] **GREEN — caller migration**: For each call site, replace the import with the equivalent from `game/strategy/services/ability_metadata.py`. Names map directly: `find_metadata` / `is_known_effect_ability` / `all_owner_aware_scopes` all exist on the unified registry.
- [ ] Move the `_OWNER_AWARE_SCOPES` constant: either inline at its single use-site OR move to `ability_metadata.py`. Document the choice in decisions.md.
- [ ] **GREEN — delete the shim**: Remove `effect_ability_metadata.py` entirely.
- [ ] Run sharded suite to confirm zero remaining references.

### Task 4.2: F-B-005 — Retire component_inspector.py re-export shim [Medium]
**File:** `game/strategy/services/component_inspector.py:1-67` (delete entire module); migrate ~50 callers
**Tests:** `pytest tests/ -v`

- [ ] Read the shim — 67 LOC of re-exports from `component_abilities.py` + `component_layers.py`. Header explicitly states it's a caller-migration shim.
- [ ] **Audit callers**: `git grep -n "from game.strategy.services.component_inspector import"`. Expected ~50 sites across engines, UI, validators, and tests.
- [ ] For each call site, determine whether the imported name lives in `component_abilities.py` (Surface A) or `component_layers.py` (Surface B). Read the shim's re-export list to map names → modules.
- [ ] **GREEN — caller migration**: Replace each import with the direct module path. Use a script if patterns are uniform; do a few manually first to catch edge cases.
- [ ] **CAUTION — UI callers**: Some sites are in `game/ui/`. Only edit the import statement (mechanical change); do NOT refactor UI behavior. If a UI caller's import needs deeper restructuring, log it for PROJ-446 and leave that one site on the shim until PROJ-446 picks it up.
- [ ] **GREEN — delete the shim**: Once all callers migrated, remove `component_inspector.py`.
- [ ] Run sharded suite.

### Task 4.3: F-B-017 — Unwind facade-side OrderExecutionResult reshape [Medium]
**File:** `game/strategy/engine/order_processor.py:97-143`; eventual deletion of `JoinFleetResult`, `ColonizeResult`, `TransferResult` typed result dataclasses
**Tests:** `pytest tests/unit/strategy/engine/test_order_processor.py tests/integration/ -v`

- [ ] **READ THE REVISED FINDING FIRST**: F-B-017's original framing claimed handler signature mismatch; Codex 2026-05-18 refuted this. The handlers (`JoinFleetHandler`, `ColonizeHandler`, `TransferHandler`) already accept the 5-kwarg unified shape. The actual residue is the facade-side reshape.
- [ ] **Audit external callers**: `git grep -n "JoinFleetResult\|ColonizeResult\|TransferResult"` across `game/` and `tests/`. The legacy typed result dataclasses are what callers consume; identify each consumer.
- [ ] For each consumer: refactor it to read `OrderExecutionResult` directly. The `merged`, `cancelled`, `colonized`, `planet_name`, `amount_transferred` fields on `OrderExecutionResult` carry the same information.
- [ ] **GREEN — drop facade methods**: Once all callers migrated, delete `OrderProcessor.process_join_fleet`, `process_colonize`, `process_transfer` and have callers invoke the underlying `handler.execute_action_order(...)` directly through the unified path. Keep the `OrderProcessor` itself; it has other responsibilities.
- [ ] **GREEN — narrow the Protocol**: With facade methods gone, the `IOrderHandler` Protocol can drop the legacy-shape parameters from `execute_action_order` if any remain. Confirm the Protocol declaration is now clean.
- [ ] Coordinate with PROJ-333 characterization callers (see comment at `order_processor.py:14-19`).

### Task 4.4: F-B-018 — Delete OrderExecutionResult legacy fields [Simple — after Task 4.3]
**File:** `game/strategy/engine/order_handlers/base.py:36-56`
**Tests:** `pytest tests/unit/strategy/engine/order_handlers/ -v`

- [ ] Verify no remaining callers read `result.merged`, `result.cancelled`, `result.colonized`, `result.planet_name`, `result.amount_transferred`. Run `git grep -n` for each.
- [ ] **GREEN**: Delete the five "legacy field" attributes from `OrderExecutionResult`. Drop the inline comments at base.py:36-56.
- [ ] If a future handler needs to communicate side-channel results (e.g., a custom "ship was destroyed" flag), it should subclass `OrderExecutionResult` or return a typed payload — NOT add new "legacy fields."
- [ ] Run targeted tests.

---

## Phase Completion Checklist

- [ ] `effect_ability_metadata.py` deleted; no `from game.strategy.services.effect_ability_metadata import` remains in `git grep`
- [ ] `component_inspector.py` deleted; no `from game.strategy.services.component_inspector import` remains in `git grep`
- [ ] `OrderProcessor.process_*` facade methods deleted; consumers read `OrderExecutionResult` directly
- [ ] `JoinFleetResult` / `ColonizeResult` / `TransferResult` typed dataclasses deleted
- [ ] `OrderExecutionResult` legacy fields deleted
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-445 4` — PASSED
- [ ] Update status to `Complete`; plan.md all phases Complete; Current State → "Project complete — awaiting verification"
- [ ] decisions.md updated with choices made in Tasks 4.1, 4.3 (e.g., `_OWNER_AWARE_SCOPES` location decision)

## Risks / Notes

- Task 4.2 (component_inspector caller sweep) is the largest mechanical task in PROJ-445. Allocate time for ~50 import-statement edits + targeted re-runs.
- Task 4.3 unwinding is the riskiest behavioral change in PROJ-445 — callers that depend on the legacy typed results might be deeper than the audit reveals. Run the full sharded suite at multiple checkpoints, not just at the end.
- If F-B-017 unwinding reveals further coupling (e.g., a UI flow that depends on the legacy result type), surface it and coordinate with PROJ-446 rather than refactoring UI inline.
