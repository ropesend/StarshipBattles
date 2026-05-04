# PROJ-326: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source

- OpenCode 321-review: `Reviews/results/2026-05-04_015902_consistency_proj-321-p0-dead-trivial-test-cleanup-completion-c_req-req_20260504_015901_0ba42a/report.md` (recommendation #1, MAJ-001, MIN-002)
- PROJ-321 design.md "Opportunities Discovered" — linter to prevent zero-game-import test files
- Existing tests/unit/data/test_test_infrastructure.py (8 skipped TODOs that the linter will absorb)
- Continuation plan: [`AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`](../../../AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md)

## Phase 1 — Linter Design

### What it catches

A test file with **zero** `from game.*`, `import game.*`, or `from game import …` import statements has a high probability of either:
1. Reimplementing production logic locally (the `tests/unit/test_modifier_logic.py` pattern PROJ-321 deleted), OR
2. Testing only stdlib / third-party / test infrastructure — legitimate but should be allowlisted to make intent explicit.

### Algorithm

```
for each *.py file under tests/ (recursive):
  if file matches an allowlist pattern: skip
  parse imports via AST (ast.parse / ast.walk for ast.Import + ast.ImportFrom)
  if no import has module starting with "game" or "game.":
    flag the file
```

AST-based parsing (NOT regex) is critical — string-matching for "import game" produces false positives on docstrings and comments.

### Allowlist strategy

A standalone `Tools/lint_test_files_allowlist.txt` file (one path per line, blank lines + `#`-comments allowed) holds:
- `tests/unit/tools/**/*.py` (tools tests don't import game)
- `tests/unit/combat_lab/**/*.py` (combat lab service tests)
- `tests/data/**/*.py` (data fixtures)
- `tests/unit/data/test_test_infrastructure.py` (after Phase 1 Task 1.4 migration; or removed entirely)
- Plus any individual files added by the Phase 3 audit

Allowlist entries support glob patterns. Non-allowlisted, non-game-importing files cause exit-1 with the file list.

### Pre-commit vs CI integration

**Recommendation: both.** Pre-commit hook stops mistakes before commit; CI catches anything that bypasses the pre-commit. The Phase 1 implementation creates the linter as a standalone script and documents both integration points; the user picks which to wire up.

Pre-commit hook script:
```bash
#!/bin/sh
# .git/hooks/pre-commit (or invoked via existing hook framework)
python Tools/lint_test_files.py
exit $?
```

CI integration: add `python Tools/lint_test_files.py` as a step in the existing CI workflow.

### Migrating `tests/unit/data/test_test_infrastructure.py`

The 8 skipped tests (`test_no_duplicate_*`) implement scan logic that is duplicated by what the linter will do. After Phase 1 Task 1.1 lands the linter:
- Delete the 8 skipped tests, OR
- Convert them to fast assertions that call into the linter and check its output (Phase 1 Task 1.4 picks one).

The TODO debt in those tests has been documented since the file's creation; this project closes that debt.

## Phase 2 — SystemTreePanel + Facade Contract

### SystemTreePanel coverage check (PROJ-321 review MAJ-001)

PROJ-321 deleted `tests/unit/ui/panels/test_system_tree_panel.py` (664 LOC). The deletion is defensible — the file was full of `__new__` bypass-init tests that exercised no real production behavior. But the deletion also removed the only systematic check that SystemTreePanel still works.

**Audit step (Phase 2 Task 2.1):** Search `tests/integration/` for SystemTreePanel exercise. If found and adequate, this task closes. If missing, add a minimal smoke test:

```python
# tests/integration/ui/test_system_tree_panel_smoke.py (NEW)
def test_system_tree_panel_constructs_and_displays(headless_pygame_session):
    """Smoke: SystemTreePanel constructs against a real strategy session and renders without error."""
    session = make_test_strategy_session()  # use existing test factory
    panel = SystemTreePanel(...)
    panel.refresh()
    assert panel.tree_root is not None
    # Optionally: simulate a click event to confirm interaction works
```

The exact shape depends on what's testable. Goal: ensure regression that breaks panel construction surfaces in CI, even without unit-level coverage.

### StrategySessionFacade contract guard (PROJ-321 review MIN-002)

PROJ-321 whole-file deleted `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` (112 LOC) per the P0 directive on trivial-pass tests. The original source review suggested keeping the file as a "contract guard." The OpenCode review recommended restoring focused public-API tests.

**Implementation:**
```python
# tests/unit/strategy/facade/test_strategy_session_facade_contract.py (NEW)
"""
Public-API contract guard for StrategySessionFacade.

Originally part of test_strategy_session_facade_public_api.py (deleted by PROJ-321).
Restored per OpenCode review MIN-002 + PROJ-321 design.md note.

Each test exercises a public method and asserts on observable behavior — NOT
trivially-pass calls. If a public method's signature or contract changes,
these tests fail and the change is caught at code-review time.
"""

class TestStrategySessionFacadeContract:
    def test_get_active_empire_returns_empire(self, facade):
        empire = facade.get_active_empire()
        assert empire.id is not None
        assert empire.name

    def test_get_galaxy_state_includes_systems(self, facade):
        state = facade.get_galaxy_state()
        assert len(state.systems) > 0

    def test_apply_command_dispatches(self, facade, mock_command):
        result = facade.apply_command(mock_command)
        assert result.status in ('accepted', 'rejected')

    # 1-2 more methods that exercise the canonical public surface
```

~30 LOC total; behavioral, not trivial.

## Phase 3 — Audit

### Process

1. Run `python Tools/lint_test_files.py` against the tree with no allowlist. Capture the full file list.
2. For each file:
   - Read its top-level docstring + first 50 lines
   - Categorize: tools-test (allowlist), test-infra (allowlist), data-fixture (allowlist), CANDIDATE FOR DELETION (zero game imports, reimplements production), SUSPECT (review needed).
3. Build the initial allowlist from the (a) + (b) + (c) categories.
4. Document SUSPECT files in this phase's Notes for user review. Do NOT delete unilaterally — surface to user.

### `tests/unit/tools/test_validate_agent_surfaces.py` (1102 LOC)

Specifically called out by the OpenCode 321-review as worth a closer look. Likely a legitimate tooling test (it validates agent-surface tooling), but the size warrants a manual audit for any CAT-1/2/3 patterns missed by PROJ-321's review.

## Architecture

This project introduces NO new architectural patterns. The linter is standalone tooling. The contract test is a simple unit test. The integration smoke test (if added) follows existing `tests/integration/` patterns.

## Risks

1. **False positives at first run.** Without an allowlist, the linter will flag dozens of legitimate tools / infrastructure tests. Phase 3 builds the allowlist before the linter is wired into CI / pre-commit. **Do NOT install the hook before Phase 3 completes** — flagging legitimate files breaks developer flow.

2. **Glob pattern in allowlist file format.** Use a minimal glob library (e.g., `pathlib.Path.match` or `fnmatch`) — avoid full shell globbing that could surprise users. Document the supported pattern syntax in the allowlist file's header comments.

3. **AST parse failures.** Malformed Python in a test file should be a hard failure (exit 1), not a silent allow. Better to break the linter than miss a real test bug.

4. **Test_test_infrastructure migration.** The 8 skipped tests document patterns to detect (duplicate test names, etc.). Verify the linter (or a separate fast assertion) covers each pattern before deleting the tests. Don't drop coverage in the migration.

5. **SystemTreePanel "no integration coverage exists" outcome.** If Phase 2 Task 2.1 finds no coverage, the smoke test must be added carefully — `SystemTreePanel` likely has heavy pygame_gui dependencies. Use the headless integration pattern from `tests/integration/ui/build_queue_screen/`.

## Patterns Reused

- **Linter pattern**: any of the existing tools under `Tools/` for style reference (e.g., `Tools/test_sharded/test_sharded.py` for argparse layout).
- **Headless integration tests**: `tests/integration/ui/build_queue_screen/` for SystemTreePanel smoke (if added).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
