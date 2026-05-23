# PROJ-417: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-13 | Project initialized | Starting point for Legacy removal — test_run_details.py shim (2026-05-13) |
| 2026-05-13 | Bundled findings from `2026-05-13_194106_legacy-audit` by removal cluster `test_run_details_shim` per user direction | Bundling driven by removal cluster (one project per system being eradicated) rather than severity to maximize deletion-PR coherence; full bundling discussion in findings/bundling_decisions.md |
| 2026-05-14 | results_panel.py is N/A — no import from shim | Codex consult confirmed: results_panel.py only stores an injected reference (comment at line 37); it never imports from the shim. Original plan overcounted callers at 2; real production import count is 1 (panel_manager.py only). |
| 2026-05-14 | Test file migrated, not deleted | `tests/unit/test_lab/test_test_run_details_public_api.py` explicitly imports the shim path 4 times as a contract test. Deleting it without update would leave red tests. Decision: migrate imports to `game.ui.screens.test_lab.details`, delete only the `test_legacy_and_new_paths_resolve_to_same_class` test (which tests the shim contract itself). Remaining tests retain value as public-API contracts for `details/panel.py`. |
| 2026-05-14 | Import target is package-level `details`, not `details.panel` | `details/__init__.py` explicitly presents `from game.ui.screens.test_lab.details import TestRunDetailsPanel` as the canonical caller surface. Use relative style `from .details import TestRunDetailsPanel` in panel_manager.py to match existing relative imports there. |
| 2026-05-14 | Stale doc cleanup in same PR | `game/ui/screens/test_lab/__init__.py`, `README.md`, `details/__init__.py`, and `docs/02_PATTERNS.md` Pattern #36 entry all reference the shim. Per codex consult and project conventions, doc updates travel with the same PR as code changes. Historical origin notes in `details/*.py` docstrings (references to `test_run_details.py` as extraction source) do not preserve a live import surface and may be left as-is. |
| 2026-05-14 | Verification grep narrowed to import-path search | Broad `grep -rn 'test_run_details' .` hits historical origin docstrings and README table entries that are acceptable to leave. Narrowed to: exact import-path strings (`from .test_run_details import`, `game.ui.screens.test_lab.test_run_details`) and shim-targeted `mock.patch` strings, excluding `__pycache__`. |
