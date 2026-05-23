# Phase 4: Codex exec-audit remediation (VERIFIED findings)

> Added post-audit. Implements the two VERIFIED Codex exec-audit findings via TDD.

**Status:** Complete
**Objective:** Close the two VERIFIED findings from the Codex exec-audit
(`AgentCoordination/Scratchpad/Consult/proj476_exec_audit/audit.md`):
(F1) the `DesignCatalog` runtime import in `design_selector_window.py` is
annotation/docstring-only under PEP 563 — root-cause fix is to move it under
`TYPE_CHECKING` and drop its tooling-exemption triple, not normalize a
removable import into policy; (F2) there is no AST-backed liveness test that
every `_TOOLING_EXEMPTIONS` triple still exists in source — so a stale entry
(exactly F1's `DesignCatalog`) can sit undetected.

---

## Tasks

### Task 4.1: Failing AST-liveness test for `_TOOLING_EXEMPTIONS` [Medium]
**File:** `tests/static_guards/test_facade_read_path_imports_guard.py`
**Symbol:** new `test_tooling_exemptions_are_live_runtime_imports`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py -k tooling_exemptions_are_live`

- [x] Write the test FIRST: for every `_TOOLING_EXEMPTIONS` triple, AST-parse
      the file and assert the `(module, member)` appears as a RUNTIME (non-
      `TYPE_CHECKING`) import — i.e. the exemption is actually load-bearing.
- [x] Run it — confirm it FAILS on the stale `DesignCatalog` triple (still a
      runtime import at this point, so it would PASS; the real RED comes after
      4.2 moves the import — so verify the test by temporarily asserting the
      detection logic against a synthetic stale triple too). Recorded: the test
      is non-vacuous (synthetic stale triple is detected).

### Task 4.2: Root-cause fix — move `DesignCatalog` under TYPE_CHECKING [Medium]
**File:** `game/ui/screens/design_selector_window.py`,
`tests/static_guards/test_facade_read_path_imports_guard.py`
**Tests:** `pytest tests/static_guards/test_facade_read_path_imports_guard.py`

- [x] Move `from game.strategy.systems.design_catalog import DesignCatalog`
      under the existing `if TYPE_CHECKING:` block (annotation-only under PEP 563
      `from __future__ import annotations`; no runtime use — verified by grep:
      only `:21` import + `:59` param annotation + docstrings).
- [x] Drop the now-dead `("...design_selector_window.py", "...design_catalog",
      "DesignCatalog", "design-editor", ...)` triple from `_TOOLING_EXEMPTIONS`.
- [x] Run the guard module — confirm GREEN (TC import ignored; liveness test
      passes; no-misfile + tag-parity intact).
- [x] Verify: `design_selector_window.py` still imports/uses its real runtime
      `get_default_design_role_registry` exemption unchanged.

**Notes (execution 2026-05-22):** F1 + F2 both VERIFIED against live code.
F1: `DesignCatalog` at `design_selector_window.py:21` had zero runtime use under
PEP 563 (only param annotation `:59` + docstrings `:9`/`:71`) — moved under
`TYPE_CHECKING`, triple dropped. The other design-editor triple
(`get_default_design_role_registry`, runtime-local at `:348`/`:390`) is genuinely
runtime and stays. F2: added `test_tooling_exemptions_are_live_runtime_imports`
(AST-parses each exemption file, asserts the member is a runtime import; plus a
synthetic non-vacuity assertion). This test catches future stale entries and
would have flagged the `DesignCatalog` triple after the move. `_TOOLING_EXEMPTIONS`
is now 29 triples (was 30). Guard module GREEN after fix.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `pytest tests/static_guards/test_facade_read_path_imports_guard.py` GREEN
- [x] Full static-guard suite + sharded suite GREEN
- [x] Update status to `Complete`; update plan.md
