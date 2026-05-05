# PROJ-326 File Manifest

> Generated during planning. Used by `/proj-parallel` for conflict detection.
> Updated if implementation discovers additional files.

## Phase 1 (linter)

| File | Type | Change |
|------|------|--------|
| `Tools/lint_test_files.py` (NEW) | Production (tooling) | AST-based linter. Argparse for `--allowlist`, `--strict`, etc. Returns exit 1 with file list when violations found. |
| `Tools/lint_test_files_allowlist.txt` (NEW) | Config | Initial seed entries for `tests/unit/tools/`, `tests/unit/combat_lab/`, `tests/data/`. Phase 3 extends this from audit. |
| `tests/unit/tools/test_lint_test_files.py` (NEW) | Test | Smoke tests for the linter: detects zero-game-import file, honors allowlist, AST parse failure handling, glob pattern correctness. |
| `tests/unit/data/test_test_infrastructure.py` | Test (modified) | Remove the 8 skipped TODO `test_no_duplicate_*` tests (logic absorbed by the linter). Add a comment pointing at `Tools/lint_test_files.py`. |
| `docs/guides/pre_commit_hooks.md` (potentially NEW) | Doc | Document how to install / opt-in to the linter as a pre-commit hook. If a similar guide already exists, append to it instead. |

## Phase 2 (SystemTreePanel + Facade contract)

| File | Type | Change |
|------|------|--------|
| `tests/integration/ui/test_system_tree_panel_smoke.py` (POTENTIALLY NEW) | Test | Only added if Phase 2 Task 2.1 audit finds existing integration coverage inadequate. |
| `tests/unit/strategy/facade/test_strategy_session_facade_contract.py` (NEW) | Test | Restore public-API contract guard. ~30 LOC. Behavioral, not trivial-pass. |

## Phase 3 (audit)

| File | Type | Change |
|------|------|--------|
| `Tools/lint_test_files_allowlist.txt` | Config (modified) | Add allowlist entries for legitimately-zero-game-import files identified by the audit. |
| `Projects/active_projects/PROJ-326/findings/zero_import_audit.md` (NEW) | Report | Per-file categorization for the ~41 flagged files. |

## Files explicitly NOT touched

These are owned by sibling continuation projects:

| File | Owner | Why excluded |
|------|-------|--------------|
| `game/ui/screens/strategy_modal_window.py`, `game/ui/screens/race_setup/screen.py`, `game/ui/screens/new_game_setup_screen.py`, `game/services/llm/background.py`, `tests/fixtures/ui_widget_factory.py`, `tests/unit/ui/screens/test_*` (the 13 deferred-migration files) | PROJ-324 | UIWindow + LLM blocker work + 13 deferred-migration files |
| `Projects/active_projects/PROJ-323/*` | PROJ-325 | PROJ-323 documentation corrections |
| `tests/unit/strategy/engine/test_command_handlers.py` | PROJ-325 | PROJ-323 Task 3.34 parametrize |
| `tests/unit/ui/screens/test_race_setup_screen.py`, `game/ui/screens/race_setup/screen.py` | PROJ-325 (Phase 3) | RaceSetupScreen testable construction |
| `tests/unit/ui/components/test_virtual_table.py` | PROJ-327 | 700-LOC `@patch` decorator sweep (PROJ-322 Task 3.14) |
| Mutable-mock fixture rescope candidates (PROJ-322 Tasks 2.6 / 2.11 / 2.15 / 2.19 / 3.15) | PROJ-327 | Phase 2 of PROJ-327 |
| `tests/unit/ui/screens/test_strategy_screen.py` (or wherever 50-test cluster lives) | PROJ-327 | PROJ-322 Task 3.25 strategy-screen refactor |
