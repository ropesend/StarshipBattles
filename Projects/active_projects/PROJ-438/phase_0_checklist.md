# Phase 0: Post-436/437 audit freeze + verification gate decision

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** PROJ-436 and PROJ-437 complete and merged
**Objective:** Freeze the exact residual scope after PROJ-436/437, fix the verification blind spot around `tests/unit/strategy/data/` by default, and capture the contact surface in the findings directory before any implementation changes.

---

## Tasks

### Task 0.1: Re-read predecessor project artifacts [Simple]
**Files:** `Projects/active_projects/PROJ-423/plan.md`, `Projects/active_projects/PROJ-424/plan.md`, `Projects/active_projects/PROJ-425/plan.md`, `Projects/active_projects/PROJ-429/plan.md`, `Projects/active_projects/PROJ-436/plan.md`, `Projects/active_projects/PROJ-437/plan.md`
**Tests:** None (planning only)

- [ ] Confirm which `#1` and `#3` surfaces were already absorbed by 423/424/425/429 and by the assumed 436/437 outcomes.
- [ ] Record any predecessor overlap risks in `findings/post_436_437_contact_audit.md`.
- [ ] Verify this project still excludes #2 (temporal scheduler), storage/container work, and transfer UI.

### Task 0.2: Capture residual `#1` contact surface [Medium]
**Files:** `game/strategy/engine/session/persistence_adapter.py`, `game/strategy/engine/turn_state_snapshot.py`, `game/strategy/engine/game_session.py`, `game/strategy/facade/strategy_session_facade.py`, `game/strategy/facade/slices/_facade_state.py`, `game/strategy/data/planet.py`, `game/strategy/data/fleet.py`, `game/strategy/data/empire.py`, `game/strategy/data/ship_instance.py`
**Tests:** None (planning only)

- [ ] Map the remaining duplicated graph-restoration steps with file:line evidence.
- [ ] Map remaining broad entity/root surfaces on `Planet`, `Fleet`, `Empire`, and `ShipInstance`.
- [ ] Identify any session/facade/cache seams that still compensate for the live graph.
- [ ] Write the findings to `findings/post_436_437_contact_audit.md`.

### Task 0.3: Capture residual `#3` contact surface [Medium]
**Files:** `game/strategy/engine/commands/__init__.py`, `game/strategy/engine/planet_command_handlers.py`, `game/strategy/engine/planet_action_engine.py`, `game/strategy/engine/component_activation_engine.py`, `game/strategy/engine/action_execution_engine.py`, `game/strategy/engine/order_processor.py`, `game/strategy/engine/order_handlers/base.py`, `game/strategy/data/order_types.py`, `game/strategy/data/order_serializer.py`, `game/strategy/engine/commands/registry.py`, `game/strategy/engine/commands/order_metadata_view.py`
**Tests:** None (planning only)

- [ ] Map the current planet strategic-intent lifecycle from command DTO to timer execution.
- [ ] Identify the private `_handler_registry` reach-in / `TypeError` fallback seam and all its callers.
- [ ] Identify how much order persistence still sits outside executable metadata.
- [ ] Record which special cases are likely in-scope versus likely acceptable residual behavior.

### Task 0.4: Fix or explicitly replace the verification blind spot [Simple]
**Files:** `pytest.ini`, `tests/unit/strategy/data/`, `tests/unit/strategy/engine/`, `tests/unit/strategy/ship_instance/`
**Tests:** `python Tools/test_sharded/test_sharded.py` plus direct-run candidates if needed

- [ ] Verify whether `tests/unit/strategy/data/` is included in the canonical suite after predecessor changes.
- [ ] Resolve D1 in `decisions.md`: default is to fix collection now; only keep a supplemental direct-run matrix if the collection fix proves materially riskier than expected.
- [ ] If fixing collection: record the exact `pytest.ini` change and the first sharded/direct validation proving those tests are now visible.
- [ ] If not fixing collection: add the required supplemental direct-run commands to the findings doc and later project phases, and record why the collection fix was rejected.

### Task 0.5: Pre-create follow-on checklist skeletons [Simple]
**Files:** `phase_1_checklist.md` through `phase_8_checklist.md`
**Tests:** None

- [ ] Ensure each phase checklist exists with an objective that matches the charter.
- [ ] Keep detailed task lists only for the current phase; leave later phases as objective stubs per local charter convention.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 1
