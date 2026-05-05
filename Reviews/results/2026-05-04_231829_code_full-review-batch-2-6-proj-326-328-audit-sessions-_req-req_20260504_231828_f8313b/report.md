# Review Report: Full Review Batch 2/6 — PROJ-326..328 + Audit Sessions 1-4

**Review Type:** code | **Request ID:** req_20260504_231828_f8313b | **Date:** 2026-05-04
**Review Mode:** fresh-eyes (no prior review reports consulted)
**Scope:** PROJ-326, PROJ-327, PROJ-328, plus audit closeout commits d7cd97dc1..da02bee86
**Limitations:** 4 parallel subagent review; each agent had full read access to source files; no coverage/profiling tools run.

---

## Summary

| Area | CRITICAL | MAJOR | Key Concern |
|------|----------|-------|-------------|
| PROJ-326 (test linter) | 0 | 6 | Documentation/cosmetic only — linter works correctly |
| PROJ-327 (runtime + composition) | 2 | 3 | Stale -3.9s claims in reference docs; mock docs misaligned |
| PROJ-328 (UIWindow MVVM) | 0 | 2 | TransferDialog behavioral regression; incomplete extraction |
| Audit Sessions S1-S4 | 0 | 1 | Stale doc timestamp |
| **Total** | **2** | **12** | |

---

## CRITICAL Findings

### [CRITICAL] FND-001: Scorecard still presents -3.9s as definitive wall-clock delta after retraction

**File:** `Projects/active_projects/PROJ-327/decisions.md:31`

The Per-technique scorecard's Wall-clock delta column for Phase 1 reads `**~3.9 s** suite-level (~30 ms file-level)` with no retraction qualifier. Audit commit `7f94a0c94` (S2.9) added a "Code-quality impact" column but did not correct or qualify the 3.9s figure. Meanwhile, `findings/runtime_delta.md:11` carries the explicit headline retraction: "PROJ-327 did not establish a causal suite-level runtime reduction … should not be cited as reclaimed time."

**Recommendation:** Append a `[†]` dagger with footnote explaining the retraction, or replace with `~0 s (retracted)` and note the file-level 30ms verifiable delta in the Verdict column.

---

### [CRITICAL] FND-002: `virtual_table_runtime.md` claims disproven amplification mechanism with no retraction

**File:** `Projects/active_projects/PROJ-327/findings/virtual_table_runtime.md:25-27`

Lines 25-27 present the 3.9s as a definitive delta with the explanatory mechanism: "The slowest-shard delta (3.9 s) is roughly the per-test reclaim … amplified by the fact that other tests in the same shard depend on this file's runtime budget." This is the precise mechanism audit S2.7 disproved: the sharded runner uses greedy bin-packing and one file completing 30ms faster saves 30ms from its shard — not 3.9s. The file was not updated by commit `7f94a0c94` and carries zero retraction mention.

**Recommendation:** Add a "RETRACTED 2026-05-04 (audit-remediation S2.7)" banner and cross-reference `runtime_delta.md` for the full analysis.

---

## MAJOR Findings

### PROJ-326 — Test Linter, Coverage, Facade Contract

### [MAJOR] FND-003: Allowlist header claims `pathlib.PurePosixPath.match` semantics but linter uses custom regex

**File:** `Tools/lint_test_files_allowlist.txt:5`

The header states patterns use `pathlib.PurePosixPath.match` semantics but the linter at `lint_test_files.py:81-114` uses a custom `_glob_to_regex()` translator (documented reason at line 121-123: `pathlib.match` doesn't recurse on `**`). The header is misleading to maintainers.

**Recommendation:** Correct header to note POSIX glob semantics with custom `**` support via regex translator.

---

### [MAJOR] FND-004: Dynamic imports (`importlib`, `__import__`) invisible to AST-based linter

**File:** `Tools/lint_test_files.py:132-149`

The `imports_game()` function only walks `ast.Import`/`ast.ImportFrom` nodes. Dynamic imports via `importlib.import_module("game.foo")` produce `ast.Call` nodes and are not detected. This causes false positives for files that legitimately load game-code modules at runtime. Currently only `test_engine_inheritance.py` is affected, but the limitation is undocumented.

**Recommendation:** Document the limitation in the linter's module docstring and on `imports_game()`.

---

### [MAJOR] FND-005: Linter comment cites Python 3.11 compatibility; codebase targets 3.14

**File:** `Tools/lint_test_files.py:121-123`

Comment reads "we need 3.11 compatibility — hence the custom translator." The codebase requires Python 3.14 per `AGENTS.md`. The custom code works correctly — only the stated rationale is wrong.

**Recommendation:** Update comment to note the custom translator exists for explicit `**` handling.

---

### [MAJOR] FND-006: Facade contract guard is test-only — no runtime enforcement on bypass

**File:** `game/strategy/facade/strategy_session_facade.py:79-95`

The facade's `self._session` is protected only by the Python `_` naming convention. The PROJ-326 contract guard test (`test_strategy_session_facade_contract.py`, 114 LOC) verifies method contracts but does not prevent or detect `facade._session` bypass. Per Pattern §5, facades are the single point of access; bypassable private attributes create a maintainability risk.

**Recommendation:** Document that convention-based protection is intentional, or add a lint rule forbidding `facade._session` outside the facade package.

---

### [MAJOR] FND-007: Plan estimated ~30 LOC for contract guard test; delivered 114 LOC

**File:** `Projects/active_projects/PROJ-326/plan.md:72` vs `tests/unit/strategy/facade/test_strategy_session_facade_contract.py:1-114`

The delivered test is thorough (9 tests, realistic mock fixture, all contracts verified) — quality validates the overshoot. Planning inaccuracy only.

---

### PROJ-327 — Runtime Retraction + Compositional Construction

### [MAJOR] FND-008: Mock's populate() idempotency check catches different scenario than documented

**File:** `tests/fixtures/strategy_screen_composition.py:115-134`

Docstring claims the check detects "same screen populated with a *different* composition." Code at line 125-126 actually detects "same composition reused across two *different* screens" (`self._populated_screen_id != screen_id`). Both scenarios are worth detecting, but the one documented is NOT the one caught. Additionally, neither path is tested — `test_strategy_screen_composition.py` has no test exercising `populate()` called twice.

**Recommendation:** Fix docstring to match actual behavior. Add two tests: repeated `populate(same_screen)` passes, and `populate(different_screen)` raises `AssertionError`.

---

### [MAJOR] FND-009: No structural conformance test between Protocol, Factory, and Mock

**File:** `tests/unit/ui/screens/test_strategy_screen_composition.py`

The smoke tests iterate over `MockStrategyScreenComposition._SLOTS` (line 54, separately maintainable tuple). If a developer adds a method to the Protocol and Factory but forgets the Mock, existing tests won't catch it because they don't verify the Mock structurally conforms to the Protocol. Protocol/Factory methods match (8/8 verified), but no test enforces this stays true.

**Recommendation:** Add a test iterating `typing.get_type_hints(StrategyScreenComposition)` and verifying every method has a matching entry in `_SLOTS`.

---

### [MAJOR] FND-010: Stale -3.9s claims in phase_5_checklist and phase_1_checklist

**File:** `Projects/active_projects/PROJ-327/phase_5_checklist.md:27,44,56,83` and `phase_1_checklist.md:92`

Five total sites across two checklist files carry uncaveated `-3.9 s` mentions. Audit commit `7f94a0c94` did not touch either checklist.

**Recommendation:** Append `(retracted per audit S2.7; see findings/runtime_delta.md)` to each mention.

---

### PROJ-328 — UIWindow MVVM Rollout

### [MAJOR] FND-011: TransferDialog `_on_confirm` always closes window — behavioral regression

**File:** `game/ui/screens/transfer_dialog.py:372-378`

Post-refactor `_on_confirm` wraps `controller.confirm_pending()` in `try/finally: self.kill()`. Pre-refactor (`909bfbecf^`) had two early-return paths that kept the dialog open: when no source/target is selected, and when both endpoints are non-fleet. The `finally` guarantee (audit S1.2) is correct for exception safety but also closes the dialog on benign early-exit paths, preventing user correction.

**Recommendation:** Add an early-return guard before the try/finally: `if view_model.current_source is None or view_model.current_target is None: return`.

---

### [MAJOR] FND-012: NewGameSetupScreen widget construction not extracted — thin builder seam

**File:** `game/ui/screens/new_game_setup_ui_builder.py:37-38`

The production builder's `build()` is a one-line pass-through to `screen._create_ui()`. All ~400 lines of widget construction remain on `NewGameSetupScreen` (733 total LOC). Pattern §33's intent is that the builder owns construction; this is a thin seam, not a real extraction. Contrast with `TransferDialog` where the renderer genuinely owns construction.

**Recommendation:** Move `_create_ui`, `_create_empire_inputs`, `_update_empire_visibility`, and `_update_race_display` into `NewGameSetupUiBuilder`.

---

### Audit Sessions S1-S4

### [MAJOR] FND-013: docs/05_ERROR_HANDLING.md "Last verified" timestamp stale

**File:** `docs/05_ERROR_HANDLING.md:3`

Timestamp reads `2026-04-28` with annotation about PROJ-308 archive links. Commit `d7cd97dc1` (S1.1, 2026-05-04) added `LLMUnexpectedError` to the exception hierarchy diagram, the "When to Use" table, and the L-codes section. Content is accurate, but the verification timestamp should reflect the 2026-05-04 edit.

**Recommendation:** Bump to `2026-05-04` with "`LLMUnexpectedError` (S1.1)" annotation.

---

## Verified Correct

The following items were reviewed and confirmed as correctly implemented:

- **LLMUnexpectedError catch ordering** (`background.py:242-257`): LLMCancelled → LLMException → bare Exception → LLMUnexpectedError. Correct ordering.
- **wait() contract**: `_done_event` set in `finally` after all terminal branches. Consumers see correct result/error semantics.
- **LLMUnexpectedError hierarchy**: inherits `LLMException → GameException` with `code=None`. Correct.
- **TransferDialog try/finally** (S1.2): `kill()` in `finally` block, original exception propagates. Exception safety is correct (though early-exit regression exists — see FND-011).
- **SystemTreePanel coverage** (S1.3): `is_planet`/`is_star`/`is_warp_point` classification logic genuinely exercised via `_has_attrs`-compatible stubs. Coverage is meaningful.
- **All S2.x doc corrections**: Pattern count (33), §32/§33 reword, PROJ-327 retraction in `runtime_delta.md`, PROJ-328 LOC correction, decisions.md scorecard column, conventions §1.6 cross-refs, allowlist rationale comments — all landed coherently.
- **All S4.x test infra hardening**: 7 items all address real failure modes. None over-engineered. The mutation guard (S4.3), idempotency check (S4.4), and defensive hasattr checks (S4.2) are the highest-value additions.
- **All allowlist entries** (spot-checked 5 diverse entries): legitimately justified. Zero suspect entries.
- **Protocol/Factory/Mock 8/8 method alignment**: `StrategyScreenComposition` Protocol, Factory, and Mock all match. All return-type annotated.
- **bypass_init guards**: All 6 PROJ-328 classes use correct `getattr(type(self), "bypass_init", False)` form. All subclasses consume correctly. All 5 non-base classes have corresponding `Null*UiBuilder`/`Mock*UiBuilder` fixtures.
- **TransferDialog Phase C MVVM split**: Primary code paths behaviorally equivalent. Controller/ViewModel/Renderer/UI builder decomposition clean.

---

## Overall Verdict

**PROJ-326 (test linter):** Solid. Ship as-is. All 6 findings are documentation/accuracy issues, not production behavior defects.

**PROJ-327 (runtime reduction + composition):** Two critical stale-claim documents must be fixed before the -3.9s claim can be considered fully retracted. The Compositional Construction pattern is well-designed; the mock fixture needs docstring + structural test fixes.

**PROJ-328 (UIWindow MVVM):** Passes core structural requirements. Two gaps remain: a behavioral regression in TransferDialog's `_on_confirm`, and incomplete widget extraction in NewGameSetupScreen.

**Audit sessions S1-S4:** Clean. One stale doc timestamp. All production fixes correct, all doc corrections coherent, all test infra hardening genuine.
