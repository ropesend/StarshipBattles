# Audit Closeout Review: PROJ-321..328 Sessions 1-4

**Date:** 2026-05-04
**Reviewer:** OpenCode (deepseek-v4-pro)
**Scope:** Commits d7cd97dc1 (S1.1), 47ed28aea (S1.2), 8b41f1420 (S1.3), 85d6723b7 (S1.4-S1.7), 7f94a0c94 (S2.8-S2.10), 71d727421 (S3), da02bee86 (S4)

---

## Question 5: S1.1 LLMUnexpectedError

### [MAJOR] FND-001: docs/05_ERROR_HANDLING.md Last-verified timestamp stale after S1.1
**File:** `docs/05_ERROR_HANDLING.md:3`
**Description:** The "Last verified" line reads `2026-04-28` and the comment describes only PROJ-308 archive link corrections. However, commit `d7cd97dc1` (S1.1, 2026-05-04) added `LLMUnexpectedError` to the exception hierarchy diagram (line 56-58), the "When to Use" table (line 83), and the L-codes section (line 161). The equivalent doc `docs/04_SERVICES.md` correctly updated its timestamp.
**Recommendation:** Bump "Last verified" to `2026-05-04` and add "`LLMUnexpectedError` (S1.1)" to the annotation.

### No findings: catch ordering, wait() contract, exception hierarchy
The `_run()` catch ordering (`LLMCancelled` → `LLMException` → bare `Exception`) at `game/services/llm/background.py:242-257` is correct — most specific subclass first. The bare `Exception` branch at line 257 wraps into `LLMUnexpectedError`, sets `status=ERROR`, and the inner `finally` at line 289 sets `_done_event` so `wait()` returns `True` for the terminal state. `LLMUnexpectedError` inherits `LLMException → GameException` with `code=None` (intentional). No defects.

---

## Question 6: S1.2 TransferDialog try/finally

### No findings
The `_on_confirm()` method at `game/ui/screens/transfer_dialog.py:372-378` guarantees `kill()` in a `finally` block. If `_controller.confirm_pending()` raises, `kill()` runs and the original exception propagates. No swallowing, no defect.

---

## Question 7: S2.x Doc Corrections

### [MAJOR] FND-001 (same as above)
Already captured — stale timestamp.

### No findings: all corrections verified coherent

| Check | Status | Evidence |
|-------|--------|----------|
| Pattern count 33 in docs/README.md + docs/02_PATTERNS.md | OK | 85d6723b7 fixed 3 locations; TOC lists 33 entries |
| §32/§33 "MUST" → "SHOULD" reword (S1.5) | OK | Lines 1771, 1776-1777, 1816, 1833 all consistent |
| §32 caveat "StrategyScreen only full adopter" (S1.6) | OK | Line 1726 matches Codex's wording |
| PROJ-327 -3.9s claim retracted (S2.8) | OK | `phase_3_checklist.md:26` and `phase_3_runtime_delta.md:21` correctly note 3.6s is sum-of-individual-measurements, 1.73s is real wall-clock |
| PROJ-328 TransferDialog LOC 380→471 (S2.10) | OK | `plan.md:23` reads "790 → 471 LOC (-40%) ... now 475 LOC after audit S1.2"; file is 475 lines |
| PROJ-327 decisions.md scorecard (S2.9) | OK | "Code-quality impact" column added; prefatory note at line 27 |
| docs/03_CONVENTIONS.md §1.6 (S3) | OK | Controller/renderer/ui_builder rows present (lines 90-92); cross-ref paragraph (line 97) uses correct relative links |
| docs/04_SERVICES.md CallStatus row (S3) | OK | Line 95 includes `LLMUnexpectedError` note |
| PROJ-324..328 status bump (S3) | OK | All show "Awaiting Verification", Last-Updated 2026-05-04 |
| Allowlist rationale comments (S3) | OK | Lines 68-76 have conftest rationale; entries 78-89 annotated |

---

## Question 8: S4.x Test Infra Hardening

### No CRITICAL/MAJOR findings

All 7 items evaluated:

| Item | File | Verdict |
|------|------|---------|
| S4.1: `_build_default_kwargs` logging | `tests/fixtures/ui_widget_factory.py:143-156` | **Genuine.** Previously returned `{}` silently on uninspectable `__init__`; now warns. Catches an actual failure mode for test authors. |
| S4.2: Defensive hasattr in MockRaceSetupUiBuilder | `tests/fixtures/race_setup_ui_builders.py:94-100` | **Genuine.** Missing `_renderer`/`_row_collector`/`empire` would AttributeError deep in production code with no signal the test wiring was wrong. Clear AssertionError message. |
| S4.3: Mutation guard in test_ship_io.py | `tests/unit/ui/services/test_ship_io.py:74-106` | **Genuine.** Module-scope fixtures that mutate silently corrupt later tests. The `to_dict()` snapshot guard catches this immediately. 54 tests still pass. |
| S4.4: Populate() idempotency across compositions | `tests/fixtures/strategy_screen_composition.py:122-135` | **Genuine.** Reusing one composition for two screens leaks mock identity — a test asserting on comp1's mock when screen holds comp2's mock is a real cross-test contamination path. |
| S4.5: UiBuilder Protocol | `tests/fixtures/ui_builder_protocol.py` | **Low-impact but proportional.** Adds static-analysis safety net for future per-screen builders. Runtime value is limited unless tests call `isinstance(builder, UiBuilder)`. |
| S4.6: `_build_default_kwargs` unit tests | `tests/fixtures/test_ui_widget_factory.py` | **Genuine.** 6 tests covering well-known names, mixed kwargs, keyword-only, positional-only, variadic, and `object.__init__`. Pins factory introspection independently of pygame_gui class shapes. |
| S4.7: Delegate factory parity tests | `tests/unit/ui/screens/test_race_setup_delegate_factory.py` | **Genuine.** 5 tests pinning wiring previously only exercised indirectly via full screen tests. Catches drift in the delegate bundle composition. |

**No items are over-engineered.** Each addresses a real failure mode or provides test-coverage for an untested contract. The guards are proportional — they add a clear failure signal where the previous behavior was silent corruption or confusing AttributeError deep in production code.

---

## Overall Verdict

The four audit sessions (S1-S4) are **clean**. All production fixes (S1.1 LLMUnexpectedError, S1.2 TransferDialog kill guarantee, S1.3 SystemTreePanel coverage) are correctly implemented. All doc corrections (S1.4-S1.7, S2.8-S2.10, S3) landed coherently with no remaining contradictions across plan.md / decisions.md / phase checklists. All test-infra hardening items (S4.1-S4.7) address real failure modes.

**One issue found:** `docs/05_ERROR_HANDLING.md` has a stale "Last verified" timestamp (2026-04-28) despite content changes on 2026-05-04 (S1.1). Minor bookkeeping fix — the doc content itself is accurate.

**Recommended action:** Merge all audit session commits as-is, with a follow-on commit to correct the `05_ERROR_HANDLING.md` timestamp.
