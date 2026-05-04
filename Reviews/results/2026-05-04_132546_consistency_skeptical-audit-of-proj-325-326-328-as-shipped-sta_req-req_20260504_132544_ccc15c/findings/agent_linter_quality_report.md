# Linter Quality Report — PROJ-326 (Focus Areas 4 & 8 subset)

**Auditor:** OpenCode (skeptical review)  
**Date:** 2026-05-04  
**Scope:** Focus Area 4 (PROJ-326 linter quality) + Focus Area 8 subset (plan coherence, docs)

---

## 1. Linter Correctness Test

### Synthetic File Results

Five synthetic test files were created in a temp directory and run through the linter
with an empty allowlist:

| File | Import | Expected | Actual |
|------|--------|----------|--------|
| `test_should_flag.py` | `from somethinglikegame import X` | FLAGGED | FLAGGED |
| `test_should_not_flag.py` | `from game.foo import Bar` | NOT flagged | NOT flagged |
| `test_import_game_dot.py` | `import game.foo.bar` | NOT flagged | NOT flagged |
| `test_from_game.py` | `from game import foo` | NOT flagged | NOT flagged |
| `test_import_something_game.py` | `import something_game` | FLAGGED | FLAGGED |

**Result:** 5/5 correct. Exit code was 1 (2 violations: the two expected files).

### Edge Cases Verified

- **Lookalike module name** (`somethinglikegame`): Correctly flagged — the AST-based check extracts the root
  of the dotted import path (`somethinglikegame` != `game`).
- **Dotted import** (`import game.foo.bar`): Correctly NOT flagged — root is `game`.
- **Bare from-import** (`from game import foo`): Correctly NOT flagged — root is `game`.
- **Non-game top-level** (`import something_game`): Correctly flagged — root is `something_game`.
- **Docstring mentions** are not false positives (AST-based, not regex).

### Conclusion: PASS

---

## 2. Linter Tool Code Review (`Tools/lint_test_files.py`)

### AST Parsing (line 192)
```python
tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
```
Uses `ast.parse` → `ast.walk`, NOT regex. The `imports_game()` function (line 132-149) walks the AST
looking for `ast.Import` and `ast.ImportFrom` nodes, extracts the root of each import, and compares
against `"game"`. This is the correct approach.

### AST Parse Failure Handling (line 194-199)
AST parse failures (SyntaxError, OSError) are collected in `parse_errors` and the file is skipped
for that scan. The `main()` function treats parse_errors as failures (line 260):
```python
if violations or parse_errors:
    return 1
```
This is **correct behavior** — a file that can't be parsed is treated as a hard failure,
not silently skipped. Confirmed by test `test_ast_parse_failure_is_a_hard_error`.

### Allowlist Glob Matching (line 117-129)
The script uses a **custom glob-to-regex translator** (`_glob_to_regex`, lines 81-114), NOT
`pathlib.Path.match`. The comment at line 121-123 explains why:
> `pathlib.Path.match` does NOT recurse on `**` until Python 3.13's `full_match`,
> and we need 3.11 compatibility.

The custom translator correctly handles `*`, `**`, `?`, and literal path segments.
Test `test_allowlist_glob_pattern_works` confirms this.

### Scan-Root Outside PROJECT_ROOT (line 186-189)
When the scan root is outside PROJECT_ROOT (e.g., temp tree used in tests), the script
falls back to computing `rel` relative to the scan root. This allows the synthetic test
scenario to work correctly.

### Conclusion: PASS. Well-engineered, no shortcuts.

---

## 3. Allowlist Audit (`Tools/lint_test_files_allowlist.txt`)

### 3.1 Real-Tree Linter Run
```
$ python Tools/lint_test_files.py
lint_test_files: OK (0 violations).
```
Exit code: 0. The allowlist matches the current tree exactly.

### 3.2 Glob Pattern Coverage

| Glob | Files Covered | Legitimacy |
|------|--------------|------------|
| `tests/unit/tools/**/*.py` | 16 files | Valid: tools tests test repo tooling. **Note:** 2 files in this directory (`test_regenerate_ship_portraits.py`, `test_codex_ship_theme_creator_skill.py`) DO import `from game.core.ship_classes import ...`. They would pass the linter without the allowlist. The blanket glob means the linter would NOT catch a game-logic-reimplementing test placed in this directory — but tooling tests belong here. |
| `tests/unit/combat_lab/**/*.py` | 28 files | Valid: combat lab service tests. |
| `tests/data/**/*.py` | Test data fixtures | Valid. |
| `tests/projects/**/*.py` | Project tooling | Valid. |
| `tests/unit/agent_coordination/**/*.py` | Agent coordination | Valid. |
| `tests/fixtures/**/*.py` + `tests/unit/fixtures/**/*.py` | Shared fixtures | Valid. |
| `tests/infrastructure/**/*.py` + `tests/unit/infrastructure/**/*.py` | Test infrastructure | Valid. |
| `tests/unit/simulation/mocks/**/*.py` | Test doubles | Valid. |

### 3.3 Individual File Entries — Consolidation Analysis

**Guard tests (lines 53-59) — 7 individual files:**
- `tests/regression/test_services_layer_rule.py` — AST scanner, no game imports. Confirmed.
- `tests/unit/quality/test_no_unseeded_random.py` — AST scanner, no game imports. Confirmed.
- `tests/unit/simulation/entities/test_ship_component_manager_di.py` — DI test. Confirmed in a directory where all other files import game.*.
- `tests/unit/strategy/adapters/test_no_ai_import.py` — The ONLY file in its directory that doesn't import game.*. Confirmed.
- `tests/unit/strategy/data/test_data_layer_boundaries.py` — AST scanner. Confirmed.
- `tests/unit/strategy/interfaces/test_engine_inheritance.py` — import-based guard, no game imports. Confirmed.
- `tests/unit/strategy/services/test_ability_sources_no_global_registry_access.py` — AST scanner. Confirmed.

**Verdict:** Each is a true singleton in a directory full of game-importing files. No reasonable glob
would capture them without also catching legitimate tests. Individual listing is correct.

**JSON/validation (lines 62-63) — 2 files:**
- `tests/regression/test_caption_schemas_validate.py` — JSON schema validation. No game imports. Confirmed.
- `tests/unit/data/test_data_validation.py` — Filesystem data validation. No game imports. Confirmed.

**Repro (line 66):**
- `tests/repro_issues/test_bug_11_dialog_size.py` — The ONLY file in `tests/repro_issues/` that doesn't import game.* (all 7 other files import game.* heavily). Individual listing is correct.

**Conftest-dependent (lines 70-77) — 8 individual files:**
Each was individually inspected. None imports `game.*` directly — they depend on game.* through
sibling conftest fixtures or importlib.util:
- `tests/integration/save_load/test_live_verification.py` — Imports from `tests.infrastructure`, uses conftest fixtures. Confirmed.
- `tests/unit/core/profiling/test_recording.py` — Uses conftest fixture `profiler`. Confirmed no game imports.
- `tests/unit/engine/collision_edge_cases/test_ccd.py` — Uses conftest fixtures. Confirmed no game imports.
- `tests/unit/engine/collision_edge_cases/test_damage_tracking.py` — Uses conftest fixtures. Confirmed no game imports.
- `tests/unit/research/research_controls/test_reset_state.py` — Pure mock-based. Confirmed no game imports.
- `tests/unit/research/test_research_renderer.py` — Loads module via importlib.util. Confirmed no direct game imports.
- `tests/unit/services/llm/test_http_block.py` — Tests conftest HTTP blocker. Confirmed no game imports.
- `tests/unit/simulation/battle_controller/test_utilities.py` — Uses conftest fixtures. Confirmed no game imports.

**Consolidation opportunity:** `tests/unit/engine/collision_edge_cases/test_ccd.py` and
`test_damage_tracking.py` could be globbed as `tests/unit/engine/collision_edge_cases/test_*.py`
(since conftest.py is excluded from scanning). Only 2 files — not pressing.

### 3.4 `test_test_infrastructure.py` — TODO Removal Verification
The plan claims 8 skipped TODO tests were removed from this file. Verified:
- No `@pytest.mark.skip` decorators found (only a comment referencing the history).
- File is 129 lines (consistent with the TODO tests being removed).

### 3.5 Allowlist Comments
All entries have descriptive comments explaining WHY they're allowed. The file header
documents the format, purpose, and rule of thumb. Good maintainability.

### Conclusion: PASS. No incorrectly allowlisted files found. Minor note: the
`tests/unit/tools/**/*.py` glob is broader than strictly necessary (2 files in it
import game.* and would pass without the allowlist), but this is acceptable since
the directory's purpose IS tooling infrastructure.

---

## 4. Pre-Commit Hook Verification

### Existence
```
$ ls -la .git/hooks/pre-commit
-rwxr-xr-x 1 rossr 197609 268 May  3 20:26 .git/hooks/pre-commit
```
File exists, is executable, 268 bytes, dated 2026-05-03.

### Content
```sh
#!/bin/sh
# PROJ-326 zero-game-import test-file linter.
# Skip on merge / rebase / cherry-pick states where partial trees are normal.
if [ -f .git/MERGE_HEAD ] || [ -d .git/rebase-merge ] || [ -d .git/rebase-apply ]; then
    exit 0
fi
python Tools/lint_test_files.py
```

### Verification
- **Matches documented hook:** Yes — content is identical to the script in `docs/guides/pre_commit_hooks.md`.
- **Merge/rebase skip:** Correctly skips on MERGE_HEAD, rebase-merge, rebase-apply states.
- **Not git-tracked:** Confirmed — `.git/hooks/` is not tracked, as expected.
- **Minor concern:** Uses bare `python` command. On systems where `python` does not exist
  (Python 3-only installs where the binary is `python3`), the hook would fail. The docs
  note says "Python alone is sufficient" but doesn't address this edge case. Mitigated by
  the fact that `python` works on the current Windows setup and most modern Python installs.

### Conclusion: PASS (minor: hardcoded `python` instead of `python3` or `sys.executable`)

---

## 5. SystemTreePanel Smoke Test (`test_system_tree_panel_smoke.py`)

### Test Run
```
tests/integration/ui/test_system_tree_panel_smoke.py::test_system_tree_panel_constructs PASSED
tests/integration/ui/test_system_tree_panel_smoke.py::test_set_items_empty_is_a_noop PASSED
tests/integration/ui/test_system_tree_panel_smoke.py::test_set_items_with_content_populates_tree PASSED
tests/integration/ui/test_system_tree_panel_smoke.py::test_set_items_twice_clears_previous_items PASSED
4 passed in 1.58s
```

### Skeptical Assessment

| Test | Assertions | Meaningful? |
|------|-----------|-------------|
| `test_system_tree_panel_constructs` | `panel.scrolling_container is not None`, `panel.items == []`, `panel.root_items == []` | **Yes.** Constructs panel with real `pygame_gui.UIManager` (no `__new__` bypass). A broken constructor (signature change, missing attribute) fails here. |
| `test_set_items_empty_is_a_noop` | `panel.items == []`, `panel.root_items == []` | **Yes.** Exercises the early-return path for empty content. Catches infinite loops or type errors on empty input. |
| `test_set_items_with_content_populates_tree` | `len(panel.items) >= 2`, `len(panel.root_items) >= 2` | **Yes.** Creates real opaque objects, passes through `set_items`, verifies tree population. Catches if the "others" bucket routing changes. |
| `test_set_items_twice_clears_previous_items` | `len(panel.items) >= 2`, `"First" not in labels` | **Yes.** This is the BUG-26 guard: verifies that calling `set_items` a second time correctly clears the previous items without crashing (mutation-during-iteration bug). |

### Design Judgment
The deleted 664-LOC test used `__new__` bypass to skip initialization entirely — these tests
are categorically different. They construct a real `SystemTreePanel` with a real `UIManager`
and exercise observable behavior. The assertions check specific observable state, not
internal implementation.

**Conclusion: PASS.** Not smoke-test-in-name-only. Four meaningful tests that would catch
real breakage.

---

## 6. StrategySessionFacade Contract Guard (`test_strategy_session_facade_contract.py`)

### Test Run
```
9 passed in 1.65s
```

### Assertion Categorization

| Test | Assertions | Category |
|------|-----------|----------|
| `test_get_all_empires_returns_one_dto_per_empire` | `len(empires) == 2`, `{e.empire_id for e in empires} == {1, 2}` | **Behavioral:** Verifies DTO count and ID correctness. 2 assertions. |
| `test_get_empire_by_id_resolves` | `empire is not None`, `empire.empire_id == 1`, `empire.name == "Alpha"` | **Behavioral:** Verifies DTO content, not just presence. 3 assertions. |
| `test_get_empire_unknown_id_returns_none` | `assert facade.get_empire(999) is None` | **Contract:** "Unknown → None, not raise." The `is None` tests a behavioral contract, not trivial presence. |
| `test_get_all_systems_returns_empty_list_for_empty_galaxy` | `assert systems == []` | **Contract:** "Empty galaxy → empty list (not None)." Behavioral — if someone changes return type to None, this fails. |
| `test_get_system_at_unknown_hex_returns_none` | `assert facade.get_system_at_hex(HexCoord(99, 99)) is None` | **Contract:** "Unknown coordinates → None." Prevents a try/except being needed at call sites. |
| `test_get_fleet_unknown_id_returns_none` | `assert facade.get_fleet(404) is None` | **Contract:** "Unknown fleet → None." |
| `test_get_fleets_at_empty_hex_returns_empty_list` | `assert facade.get_fleets_at_hex(HexCoord(0, 0)) == []` | **Contract:** "Empty hex → empty list." |
| `test_get_turn_number_forwards_session_value` | `assert facade.get_turn_number() == 7` | **Meaningful:** Verifies the facade correctly forwards session state. |
| `test_handle_command_returns_validation_result` | `isinstance(result, ValidationResult)`, `assert_called_once_with(cmd)` | **Behavioral:** Verifies dispatch contract — facade always returns ValidationResult, delegates to session. 2 assertions. |

### Tally
- **Total assertions:** ~14 (counting compound assertions)
- **Trivial-pass style** (`assert x is not None` without context): **0**
- **Contract-style** (behavioral guarantees): **9**
- **Content-verifying** (checks specific values): **5**

### Design Judgment
The docstring correctly claims "Each test here exercises a public method and asserts on
**observable behavior** — never `assert facade.method() is not None`." This is true.
The `is None` assertions are paired with the behavioral comment that the return type is
None (not a raise), making them contract guards, not trivial presence checks.

**Conclusion: PASS.** All 9 tests make meaningful behavioral assertions. No trivial-pass tests.

---

## 7. PROJ-326 plan.md Reference Verification

### Internal References (within PROJ-326 directory)
All resolve correctly (relative to `Projects/active_projects/PROJ-326/`):
- `phase_1_checklist.md` ✓
- `phase_2_checklist.md` ✓
- `phase_3_checklist.md` ✓
- `design.md` ✓
- `decisions.md` ✓
- `manifest.md` ✓
- `findings/zero_import_audit.md` ✓

### External References (relative to repo root)
Paths as rendered in Markdown are relative to the plan.md location. Verified each resolves:

| Reference in plan.md | Resolves from repo root? | Notes |
|----------------------|--------------------------|-------|
| `AgentCoordination/Scratchpad/plans/proj_324_325_326_327_parallelism_map.md` | ✓ | Exists |
| `Reviews/results/2026-05-04_015902_.../report.md` | ✓ | Exists |
| `AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md` | ✓ | Exists |
| `tests/unit/data/test_test_infrastructure.py` | ✓ | Exists (line 33 link is technically relative to plan.md dir — broken in Markdown renderer — but human-readable) |
| `Projects/scripts/current_task.py` | ✓ | Exists |
| `Projects/scripts/validate_phase.py` | ✓ | Exists |

**Minor issue:** The Markdown link `[tests/unit/data/test_test_infrastructure.py](tests/unit/data/test_test_infrastructure.py)` on line 33 would 404 on GitHub (it resolves relative to the plan.md directory, not the repo root). This is cosmetic — the path is clearly a repo-root-relative path in context.

### Checklist References
Checked the phase checklists reference real files in their task blocks. Spot-checked 5 entries across
phases 1-3 — all reference both the expected file and the expected action.

### Conclusion: PASS. All meaningful references resolve. One cosmetic markdown link issue (non-blocking).

---

## 8. `docs/guides/pre_commit_hooks.md` Review

### Content Assessment
74 lines, well-structured:
- L1-3: Header + explanation that hooks are raw scripts (not `pre-commit` framework). Accurate.
- L9-19: `lint_test_files` section. Describes purpose, references real files. Accurate.
- L21-48: Installation instructions for Bash and PowerShell. The PowerShell snippet is
  incomplete — it's missing the `chmod` equivalent that Bash has, and the EOF heredoc
  terminates differently. **Minor**: PowerShell snippet doesn't show setting executable bit
  (less relevant on Windows but the hook won't run in Git Bash without it).
- L50-51: Bypass instruction. Correct (`git commit --no-verify`).
- L53-59: CI integration. References `.github/workflows/agent_coordination.yml`. Correct.
- L61-63: Notes. States the linter has no third-party deps. Correct (stdlib-only AST + argparse).
- L66-73: Maintenance notes. Correct guidance on what to do when the hook fails.

### Coherence
Reads as a single coherent document. No internal contradictions. References match reality.

### Conclusion: PASS. Coherent and accurate. PowerShell snippet has a minor completeness issue.

---

## Overall Summary

| Focus Area | Verdict | Issues Found |
|------------|---------|--------------|
| 1. Linter correctness (synthetic files) | **PASS** | None |
| 2. Linter tool code quality | **PASS** | None |
| 3a. Allowlist audit — coverage | **PASS** | None |
| 3b. Allowlist — consolidation opportunities | **PASS** | Minor: 2 files in `tests/unit/tools/` could be individually listed instead of blanket glob |
| 4. Pre-commit hook | **PASS** | Minor: hardcoded `python` command |
| 5. SystemTreePanel smoke test | **PASS** | None |
| 6. Facade contract guard | **PASS** | None |
| 7. PROJ-326 plan references | **PASS** | Cosmetic: one relative markdown link |
| 8. pre_commit_hooks.md | **PASS** | Minor: PowerShell snippet missing chmod |

**Bottom line:** PROJ-326's linter infrastructure is solid. The linter uses proper AST parsing
(not regex), handles edge cases correctly (lookalike module names, docstring mentions, parse failures),
and exits 0 against the current tree. The allowlist is comprehensive with no incorrectly-admitted
files. The SystemTreePanel smoke test provides genuine behavioral coverage (not bypass-init trivia).
The facade contract guard makes meaningful behavioral assertions (not trivial is-not-None checks).
All plan references resolve. No blocking issues found.

### Non-blocking Recommendations

1. The `tests/unit/tools/**/*.py` blanket glob could mask a future bad file added to that
   directory. Consider narrowing or adding a comment flagging the risk.
2. The pre-commit hook's bare `python` command should be documented as requiring `python`
   (not `python3`) in the PATH, or changed to `python3` with fallback.
3. The PowerShell snippet in `docs/guides/pre_commit_hooks.md` is incomplete (missing
   executable bit setting for Git Bash compatibility).
