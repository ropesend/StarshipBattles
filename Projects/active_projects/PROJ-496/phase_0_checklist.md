# Phase 0: Retarget / prune

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-496 0`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Re-grep every PROJ-480-inherited task's described pattern in the live tree before any TDD. Update phase 1-2 checklists in-place with corrected line numbers, drop NULL tasks, expand under-counted occurrences. No production-code or test edits in this phase — analysis only.

---

## Tasks

### Task 0.1: Re-grep every risky/integration pending task target

- [x] For each task in `phase_1_checklist.md` and `phase_2_checklist.md`, re-grep the described pattern in the target file.
- [x] Edit the task in-place if the count or line range differs from the PROJ-480 plan.
- [x] Strike-through (don't delete) any task whose target pattern no longer exists.

**Retarget summary (2026-05-23):**
- T1.1 (T3.29): 17 isinstance tests in `TestEagerDefaultEngines` (lines 34-177), not 18. Plus 2 isinstance/identity tests in `TestConflictEngineBattleResolverBranches` (lines 196-217). The PROJ-480 "18 isinstance" count was an approximation. The parametrize target is the 17-test cluster in TestEagerDefaultEngines (truly identical pattern).
- T1.2 (T5.14): `inspect.getsource` guard at lines 219-251 (test_conflict_engine_resolver_guard_present_at_dispatch_site). AST guard at lines 262-288 (test_registry_module_does_not_import_planet_modifier_effect_engine). Both confirmed present. ✅
- T1.3 (T4.1): literal dict at lines 113-147 (35 lines, not 50 — actual is smaller). assertion at line 150. Pattern matches PROJ-480 description. ✅
- T1.4 (T4.11): `assert ab.amount == 25` at line 60 (block 23-60). The current code already has formula comment at line 47-52, 59. Need to extract to intermediate `expected` variable. ✅
- T1.5 (T5.4): two loop tests at 610-617 (`test_multiple_ticks_increment_counter`) and 740-748 (`test_rapid_succession_ticks`). DROPPED — see Task 0.1 dropped list below.
- T1.6 (T5.5): `max(ai_indices) < min(ship_indices)` at line 388. NOTE: the existing assertion is already mathematically equivalent to `all(i < j for i in ai_indices for j in ship_indices)` (since min/max define those bounds). The PROJ-480 task wanted to strengthen from a weaker review suggestion to this form; the current form is already strong. DROPPED — see dropped list.
- T1.7 (T5.9): stochastic CO2 branching at lines 147-167. `generate_atmosphere` already accepts `rng: random.Random`. ✅
- T1.8 (T5.17): `rel=1e-9` happiness comparison at lines 436-451. DROPPED — see dropped list.
- T1.9 (T5.8): `if layer_key is None` at lines 45, 80; debug print at line 47. Confirmed. ✅
- T2.1 (T2.2): 73-line monolithic test at lines 22-95 (`test_custom_resource_type_full_pipeline`). Intermediate assertions at lines 48, 80-81. ✅
- T2.2 (T3.31): 4 deterministic tests at lines 18-127. ✅
- T2.3 (T5.11): RNG-driven conditional at lines 46-50 and 125-129. ✅
- T2.4 (T5.12): retry loop at lines 140-146 (`test_order_cleared_on_completion`, not 127-147 as cited — cited range includes preceding test). ✅
- T2.5 (T5.13): 2+ retry guards at lines 354-357 (`test_multiple_complexes_on_planet`). ✅

**Dropped tasks:**
- **T1.5 (T5.4) — DROPPED.** The two loop tests live in different classes with different intents: `test_multiple_ticks_increment_counter` (TestMultipleTicks class, exercises basic counter), `test_rapid_succession_ticks` (TestEdgeCases class, exercises rapid-succession with explicit TickLimitCondition(max_ticks=1000)). Per PROJ-496 risky-file judgment rule ("different setup/assertions = stay distinct"), parametrizing across class boundaries would hurt readability and lose the edge-case framing. PROJ-480's "+0.5 modest" delta does not justify the loss of intent clarity.
- **T1.6 (T5.5) — DROPPED.** The existing `max(ai_indices) < min(ship_indices)` assertion is logically identical to the proposed `all(i < j for i in ai_indices for j in ship_indices)` (since min/max of a set define both forms). The PROJ-480 task description was meant to UPGRADE FROM a weaker form proposed in a Codex review; the current form on disk already satisfies that strengthening. There is nothing to change. Re-grep evidence: line 388 already has the strong form.
- **T1.8 (T5.17) — DROPPED.** The test compares `rate_giddy == rate_normal * 2.0` — that IS an external relationship assertion (linear scaling of rate w.r.t. happiness), not a re-derivation. Replacing it with a hardcoded literal would risk encoding a stale formula constant; the relational form correctly couples to the formula without re-deriving it in test code. Per the guard-test sensitivity rule, leave alone.

### Task 0.2: Confirm T5.14 re-pending evidence is still valid

- [x] Re-read `tests/unit/strategy/turn_engine/test_turn_engine_lazy_properties.py:219-288` and confirm both `inspect.getsource(...)` guard and AST-parsing guard are still present (PROJ-480 audit_verification.md F1 evidence as of 2026-05-23). ✅ both still present.
- [x] If PROJ-479's Task 3.21 (NEEDS_REWORK) has since landed, mark T5.14 in Phase 1 as resolved and update the task notes accordingly. PROJ-479 T3.21 has been re-routed to PROJ-491 Task 1.5 (per its phase_1_checklist.md). PROJ-491 status is "Not Started" — Batch 4 has not landed. Proceed with T5.14.

### Task 0.3: Confirm same-file collision plan for turn_engine_lazy_properties

- [x] Phase 1 owns BOTH PROJ-480 T3.29 (parametrize 18 isinstance) and T5.14 (guard split) for `test_turn_engine_lazy_properties.py`. Confirm Phase 1 sequencing: T3.29 → T5.14.

### Task 0.4: Confirm risky-file boundary with PROJ-494/PROJ-495

- [x] Verify none of PROJ-496's files (per `manifest.md`) appear in PROJ-494/495 manifests. (Inspection of PROJ-491 surfaced T1.5 overlap, handled in T0.2.)

### Task 0.5: Validate Phase 0 closure

- [x] Phase 0 closure documented in this checklist.
- [x] Update plan.md Current State.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 1
