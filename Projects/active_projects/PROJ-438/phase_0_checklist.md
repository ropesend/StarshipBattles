# Phase 0: Post-436/437 audit freeze + verification gate decision

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** PROJ-436 Phases 0–9 + PROJ-437 Phase 0 on `main` (verified `eb8da3d85`)
**Objective:** Freeze the exact residual scope after PROJ-436/437, fix the verification blind spot around `tests/unit/strategy/data/` by default, and capture the contact surface in the findings directory before any implementation changes.

---

## Tasks

### Task 0.1: Re-read predecessor project artifacts [Simple]
**Files:** `Projects/active_projects/PROJ-423/plan.md`, `Projects/active_projects/PROJ-424/plan.md`, `Projects/active_projects/PROJ-425/plan.md`, `Projects/active_projects/PROJ-429/plan.md`, `Projects/active_projects/PROJ-436/plan.md`, `Projects/active_projects/PROJ-437/plan.md`
**Tests:** None (planning only)

- [x] Confirm which `#1` and `#3` surfaces were already absorbed by 423/424/425/429 and by the assumed 436/437 outcomes. *(Captured in findings post-Phase-0 re-verification table. Notably: PROJ-436 plan.md / phase_state.json on this checkout are stale — Phase 9 code is on main per `git log` but the artifact still shows "Not Started." Other-machine ownership.)*
- [x] Record any predecessor overlap risks in `findings/post_436_437_contact_audit.md`. *(Hard-block gates re-checked; only Phase 8 awaits PROJ-436 Phase 10.)*
- [x] Verify this project still excludes #2 (temporal scheduler), storage/container work, and transfer UI. *(decisions.md unchanged on scope; findings exclusions section reaffirmed.)*

### Task 0.2: Capture residual `#1` contact surface [Medium]
**Files:** `game/strategy/engine/session/persistence_adapter.py`, `game/strategy/engine/turn_state_snapshot.py`, `game/strategy/engine/game_session.py`, `game/strategy/facade/strategy_session_facade.py`, `game/strategy/facade/slices/_facade_state.py`, `game/strategy/data/planet.py`, `game/strategy/data/fleet.py`, `game/strategy/data/empire.py`, `game/strategy/data/ship_instance.py`
**Tests:** None (planning only)

- [x] Map the remaining duplicated graph-restoration steps with file:line evidence. *(`persistence_adapter.py:172–197` ↔ `turn_state_snapshot.py:112–136`; asymmetric `DesignCatalog` repop at `persistence_adapter.py:199–228`.)*
- [x] Map remaining broad entity/root surfaces on `Planet`, `Fleet`, `Empire`, and `ShipInstance`. *(`ship_instance.py` reset to 768 LOC by Phase 9; Phase 3 must re-audit at phase start, not from pre-Phase-9 line numbers.)*
- [x] Identify any session/facade/cache seams that still compensate for the live graph. *(Façade cache is intentional performance boundary per prompt — preserved.)*
- [x] Write the findings to `findings/post_436_437_contact_audit.md`. *(Phase 0 re-verification section appended.)*

### Task 0.3: Capture residual `#3` contact surface [Medium]
**Files:** `game/strategy/engine/commands/__init__.py`, `game/strategy/engine/planet_command_handlers.py`, `game/strategy/engine/planet_action_engine.py`, `game/strategy/engine/component_activation_engine.py`, `game/strategy/engine/action_execution_engine.py`, `game/strategy/engine/order_processor.py`, `game/strategy/engine/order_handlers/base.py`, `game/strategy/data/order_types.py`, `game/strategy/data/order_serializer.py`, `game/strategy/engine/commands/registry.py`, `game/strategy/engine/commands/order_metadata_view.py`
**Tests:** None (planning only)

- [x] Map the current planet strategic-intent lifecycle from command DTO to timer execution. *(`IssuePlanetOrderCommand` at `commands/__init__.py:557–574` → string→enum mapping at `planet_command_handlers.py:62–90` → instant pop in `PlanetActionEngine` → timer in `ComponentActivationEngine`.)*
- [x] Identify the private `_handler_registry` reach-in / `TypeError` fallback seam and all its callers. *(`action_execution_engine.py:299–337`. Only external `_handler_registry` consumer in repo. Fallback exists because recovery vs. launch handlers have different kwarg signatures.)*
- [x] Identify how much order persistence still sits outside executable metadata. *(`CommandSpec.serializer_codec`, `Order.to_dict()` target-shape branching, `OrderSerializer` marker-dict deserialization + rebinding/dead-ref removal — all intact for Phase 7.)*
- [x] Record which special cases are likely in-scope versus likely acceptable residual behavior. *(D3 default LOCKED: `JOIN_FLEET`/mission decomposition/`IMPLICIT_ACTION_ORDER_TYPES` are acceptable specialized behavior unless implementation audit proves blocking leakage.)*

### Task 0.4: Fix or explicitly replace the verification blind spot [Simple]
**Files:** `pytest.ini`, `tests/unit/strategy/data/`, `tests/unit/strategy/engine/`, `tests/unit/strategy/ship_instance/`
**Tests:** `python Tools/test_sharded/test_sharded.py` plus direct-run candidates if needed

- [x] Verify whether `tests/unit/strategy/data/` is included in the canonical suite after predecessor changes. *(Pytest.ini line 6: `norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes` — `data` not listed. Sharded suite collected 23,211 tests, confirming visibility.)*
- [x] Resolve D1 in `decisions.md`: default is to fix collection now; only keep a supplemental direct-run matrix if the collection fix proves materially riskier than expected. *(Settled in option (a). PROJ-443 Phase 4 (`e12603992`) flipped it ahead of PROJ-438 start with +1953 newly-visible tests. No PROJ-438 code change needed.)*
- [x] If fixing collection: record the exact `pytest.ini` change and the first sharded/direct validation proving those tests are now visible. *(Recorded in decisions.md. Validation: this Phase 0 sharded run.)*
- [x] If not fixing collection: add the required supplemental direct-run commands to the findings doc and later project phases, and record why the collection fix was rejected. *(N/A — collection settled.)*

### Task 0.5: Pre-create follow-on checklist skeletons [Simple]
**Files:** `phase_1_checklist.md` through `phase_8_checklist.md`
**Tests:** None

- [x] Ensure each phase checklist exists with an objective that matches the charter. *(All 8 follow-on checklists present.)*
- [x] Keep detailed task lists only for the current phase; leave later phases as objective stubs per local charter convention. *(Per kickoff prompt override, Phase 1, 2, 3 have detailed TDD-shaped subtask lists; Phase 4–8 remain objective stubs.)*

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
