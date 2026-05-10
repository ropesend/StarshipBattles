# PROJ-326 Review Report

> Agent: OpenCode (deepseek-v4-pro) | Date: 2026-05-04 | Scope: Test linter, SystemTreePanel coverage, StrategySessionFacade contract guard

---

## Q1: Test Linter + Allowlist

### MAJOR FND-001: Allowlist header claims `pathlib.PurePosixPath.match` semantics but linter uses custom regex translator
**File:** `Tools/lint_test_files_allowlist.txt:5`
**Description:** The allowlist header states *"Glob patterns use `pathlib.PurePosixPath.match` semantics"* but the linter at `Tools/lint_test_files.py:81-114` uses a custom `_glob_to_regex()` translator. This is a deliberate choice (line 121-123 documents the reason: `pathlib.match` doesn't recurse on `**`), but the header comment is misleading. A maintainer reading the header and consulting `pathlib.PurePosixPath.match` docs would find behavior that differs from what the linter actually implements — particularly around `**` semantics, separator handling, and anchoring.
**Recommendation:** Correct the header to state that patterns use POSIX glob semantics equivalent to `pathlib.PurePosixPath.full_match` (Python ≥3.13), and that the implementation uses a custom regex translator for `**` support. This is a documentation fix, no code change needed.

### MAJOR FND-002: `importlib.import_module` / `__import__` dynamic imports are invisible to the AST check
**File:** `Tools/lint_test_files.py:132-149`
**Description:** The `imports_game()` function walks the AST looking for `ast.Import` and `ast.ImportFrom` nodes. Dynamic imports via `importlib.import_module("game.foo")` or `__import__("game.foo")` produce only `ast.Call` nodes and are not detected. This causes **false positives**: files that legitimately load game-code modules at runtime (e.g., `tests/unit/strategy/interfaces/test_engine_inheritance.py:51-52` uses `importlib.import_module(engine_module)`) are flagged as having zero game imports. These files must be individually allowlisted instead of the linter recognizing they do depend on `game.*`. The false-positive rate is low (the Phase 3 audit found `test_engine_inheritance.py` was the only affected file), but the limitation is undocumented in the linter's source.
**Recommendation:** Document this limitation in a comment on `imports_game()` and/or in the linter's module docstring. Optionally, extend the AST walk to check for calls to `importlib.import_module` with `game.*` string arguments — though this is a heuristic improvement, not required.

### MAJOR FND-003: `_glob_to_regex` rationale cites Python 3.11 but target is 3.14
**File:** `Tools/lint_test_files.py:121-123`
**Description:** The comment reads *"`pathlib.Path.match` does NOT recurse on `**` until Python 3.13's `full_match`, and we need 3.11 compatibility — hence the custom translator."* The codebase requires Python 3.14 per `AGENTS.md` (non-negotiable). On 3.13+, `pathlib.PurePosixPath.match()` supports `**` recursive patterns and `PurePosixPath.full_match()` (added in 3.13) handles full-path matching natively. The custom `_glob_to_regex` works correctly — there is no functional bug — but the stated compatibility rationale is incorrect for the target Python version. This is a dead-comment/comment-drift issue; it could mislead future maintainers into writing unnecessary compatibility workarounds.
**Recommendation:** Update the comment to note that the custom translator was written for clarity and explicit `**` handling rather than for Python version compatibility, or simplify the code to use `PurePosixPath.full_match()` since 3.13+ is available.

---

## Q1 (Continued): Allowlist Spot-Check

Five diverse allowlist entries were verified by reading the referenced test files. All are legitimately justified.

| Entry | File Verified | Verdict |
|---|---|---|
| `tests/unit/tools/**/*.py` | `test_lint_test_files.py` (imports linter via `importlib.util`, no `game.*`) | Justified |
| `tests/unit/combat_lab/**/*.py` | `test_spec_compiler.py` (imports `game.simulation.*` — **already passes the linter**; the `test_runner_cleanup.py` file likely does not) | Justified (covers files within dir that lack imports) |
| `tests/unit/data/test_test_infrastructure.py` | Entire file (129 LOC, checks repo file naming/tooling; uses `ast`, `pathlib` only) | Justified |
| `tests/regression/test_services_layer_rule.py` | Entire file (94 LOC, AST-scans `game/services/` via filesystem; stdlib only) | Justified |
| `tests/unit/simulation/mocks/**/*.py` | `mock_ai_controller.py` (78 LOC, plain test-double class; no `game.ai` imports) | Justified |

**Verdict on allowlist entries:** All ~55 entries (glob patterns + individual files) pass spot-check verification. The Phase 3 audit (`Projects/active_projects/PROJ-326/findings/zero_import_audit.md`) correctly categorized 32 surviving files into categories A-D (tools, infrastructure, fixtures, stdlib-only) with zero SUSPECT (E/F) files.

---

## Q1 (Continued): Allowlist Parser Correctness

The `_glob_to_regex()` function at `Tools/lint_test_files.py:81-114` handles all patterns in use:
- `*` → `[^/]*` (segment-only match)
- `**` → `.*` (cross-separator, with optional trailing `/` consumed)
- `?` → `[^/]`
- Anchored at both ends (`^...$`)

All allowlist glob patterns follow the `prefix/**/*.py` form. The `**` regex (`.*`) combined with `*` regex (`[^/]*`) correctly matches any `.py` file at any depth under the prefix directory. The test `test_allowlist_glob_pattern_works` in `tests/unit/tools/test_lint_test_files.py:143-152` validates this behavior directly.

---

## Q2: SystemTreePanel Coverage

### MAJOR FND-004: Classification stubs use `_has_attrs`-compatible attribute names — tests are meaningful
**File:** `tests/integration/ui/test_system_tree_panel_smoke.py:149-267`
**Description:** The classification-path tests (`test_set_items_classifies_planet_correctly`, `test_set_items_classifies_star_correctly`, `test_set_items_classifies_warp_point_correctly`) use plain `object`-based stubs with the exact attribute names checked by `is_planet` / `is_star` / `is_warp_point` in `game/core/protocols/strategy_entities.py:424-436`. The stub classes:

| Stub | Attributes | Matches Protocol |
|---|---|---|
| `_PlanetStub` | `planet_type` | `is_planet` → `_has_attrs(obj, 'planet_type')` |
| `_StarStub` | `star_type`, `color`, `mass` | `is_star` → `_has_attrs(obj, 'star_type', 'color', 'mass')` |
| `_WarpPointStub` | `destination_id` | `is_warp_point` → `_has_attrs(obj, 'destination_id')` |

These genuinely exercise the classification logic in `system_tree_panel.py:211-218`. The tests assert on observable panel state (root items, item count, label text, indent level, group header presence) — not on internal state. The smoker also exercises construction, empty-set no-op, and BUG-26 re-set guard. **The audit S1.3 claim of meaningful classification coverage is confirmed.**

**Coverage gaps (noted for completeness):** The multi-planet group path (planetary-system header at line 404 of `system_tree_panel.py`), multi-warp-point group path, and flat-view code paths are not exercised. These are minor gaps; the core classification contract is tested.

---

## Q3: StrategySessionFacade Contract Guard

### MAJOR FND-005: Contract guard exists only in tests — no runtime enforcement on facade bypass
**File:** `game/strategy/facade/strategy_session_facade.py:79-95`
**Description:** The facade's docstring (lines 63-64) states *"The UI layer should never access GameSession internals directly."* However, `self._session` (line 85) is only protected by the Python `_` naming convention — there is no `__init_subclass__`, `__post_init__`, `__setattr__` guard, or `MappingProxyType` wrapper preventing external callers from accessing `facade._session` and bypassing the facade entirely. Per Pattern §5 (Facade/Delegate), facades are the single point of access; the absence of runtime enforcement means a well-intentioned developer adding a new UI screen could accidentally call `facade._session.galaxy` instead of `facade.get_all_systems()` and no test or lint would catch it.

The PROJ-326 contract guard is implemented as a behavioral test at `tests/unit/strategy/facade/test_strategy_session_facade_contract.py` (114 LOC, 9 tests). These tests verify that public methods return correct DTOs when invoked through a Mock session — they guard against facade **method contract breakage**, not facade **bypass**. Both the original frozen-surface test (`test_strategy_session_facade_public_api.py`, 77 LOC) and the new behavioral contract test complement each other, but neither prevents direct `_session` access.
**Recommendation:** Unless the project considers `_`-prefix convention sufficient (as it does elsewhere), consider one of: (a) a lint rule that forbids `facade._session` outside `game/strategy/facade/`, (b) a `__getattr__` override that raises `AttributeError` for unexpected attribute access in production, or (c) documenting in the facade class docstring that the `_` convention is the sole enforcement mechanism and that this is intentional. At minimum, the test file docstring should note that bypass is not tested.

### MAJOR FND-006: Contract guard test is 114 LOC (vs. planned ~30 LOC) — test quality validates the overshoot
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_contract.py:1-114` and `Projects/active_projects/PROJ-326/plan.md:72`
**Description:** The plan estimated ~30 LOC for the restored contract guard test. The delivered file is 114 LOC including imports, docstring, fixture, and 9 test methods. This is a planning inaccuracy, not a quality issue — every test asserts on observable behavior (DTO identity, nullability contracts, empty-list-vs-None contracts) and none are trivial-pass. The fixture at line 41-59 constructs a realistic Mock GameSession with two empires, a turn number, and null-returning lookup helpers. The 9-test surface covers empire queries, system queries, fleet queries, game state, and command dispatch — exceeding the planned 3-5 method coverage. **No action required beyond updating plan.md if micro-accuracy is desired.**

---

## Overall Verdict

PROJ-326 is solid work across all three scoped areas. No CRITICAL findings. Six MAJOR findings, all in the documentation/limitation-documentation category rather than in production behavior:

| ID | Severity | Area | Summary |
|---|---|---|---|
| FND-001 | MAJOR | Allowlist | Header claims `pathlib.match` semantics; linter uses custom regex |
| FND-002 | MAJOR | Linter | Dynamic imports (`importlib`, `__import__`) invisible to AST check |
| FND-003 | MAJOR | Linter | Comment cites 3.11 compatibility; codebase targets 3.14 |
| FND-004 | MAJOR | Coverage | Coverage IS meaningful — confirms audit S1.3 claim (no fix needed) |
| FND-005 | MAJOR | Facade | Contract guard is test-only; no runtime bypass enforcement |
| FND-006 | MAJOR | Facade | Plan estimated ~30 LOC; delivered 114 LOC (quality validates overshoot) |

**Recommendation:** Ship as-is. All six findings are documentation/planning-accuracy issues. The linter catches the intended class of bug (zero-import re-implementations), the SystemTreePanel coverage is genuine behavioral testing of classification logic, and the facade contract guard test provides meaningful regression protection against method-contract breakage.
