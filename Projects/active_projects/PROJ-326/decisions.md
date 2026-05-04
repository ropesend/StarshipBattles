# PROJ-326: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Continuation of PROJ-321 follow-ups: linter to prevent zero-game-import test files (PROJ-321 design.md opportunity + OpenCode review recommendation #1), SystemTreePanel coverage check (review MAJ-001), StrategySessionFacade contract guard restoration (review MIN-002). |
| 2026-05-04 | **D-001:** AST-based parsing for the linter, not regex | Regex string-matching produces false positives on docstrings and comments. AST parsing is the only reliable approach. |
| 2026-05-04 | **D-002:** Standalone allowlist file (`Tools/lint_test_files_allowlist.txt`) with glob support | Keeps the rule visible in code review. A YAML config or in-file `# noqa: lint-test-files` markers were considered — rejected because they're either heavyweight (YAML) or scatter intent across the codebase (in-file markers). |
| 2026-05-04 | **D-003:** Build the allowlist BEFORE wiring the linter into pre-commit / CI | Without an allowlist, the first run flags dozens of legitimate tools / infra tests. Phase 3 must complete the audit before the hook is installed. Flagging legitimate files breaks developer flow. |
| 2026-05-04 | **D-004:** Migrate `tests/unit/data/test_test_infrastructure.py` 8 skipped TODOs into the linter | The TODO debt has existed since the file was created. The new linter is the right home for the same scan logic. Closes both the prevention gap and documented test debt in one move. |
| 2026-05-04 | **D-005:** Document both pre-commit AND CI integration; user picks which to wire up | Pre-commit hooks are user-local (each developer installs them independently). CI is centralized. Both are valid; user preference. |
| 2026-05-04 | **D-006:** SystemTreePanel coverage check is conditional — only add a smoke test if existing integration coverage is inadequate | Don't add coverage just because PROJ-321 deleted a unit test. The Phase 2 Task 2.1 audit determines whether coverage actually exists. |
| 2026-05-04 | **D-007:** StrategySessionFacade contract guard is BEHAVIORAL, not trivial | The original deleted file was full of trivial-pass tests. The restored guard exercises 3-5 public methods with assertions on observable behavior. ~30 LOC. |
| 2026-05-04 | **D-008:** Do NOT delete any zero-game-import survivors unilaterally in Phase 3 | Surface SUSPECT files to the user. The previous PROJ-321 worked from a heavily-vetted source review; this audit doesn't have that vetting layer. |
| 2026-05-04 | **D-009:** Out-of-scope items NOT silently dropped | All PROJ-322 deferrals not closed by PROJ-324 are queued in PROJ-327. PROJ-326 explicitly does not own them. |
| 2026-05-04 | **D-010:** Branch strategy: same as PROJ-324 (`feat/03c-phase-aware-execution` unless user directs otherwise) | Awaiting user confirmation. |
