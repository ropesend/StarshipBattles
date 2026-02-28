# PROJ-64: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-06 | Project initialized | Starting point for Narrow Exception Handling |
| 2026-02-06 | Scope: All ~72 narrowable sites (not just worst offenders) | Complete cleanup eliminates issue entirely across 47 files |
| 2026-02-06 | Add `# Intentional broad catch: <reason>` comments to ~18 Tier 1 sites | Future reviewers understand why broad catch is kept; prevents re-filing the same issue |
| 2026-02-06 | Include Tier 4 structural validation (5 sites) | Input validation before try blocks is more robust than just narrowing catches |
| 2026-02-06 | Organize phases bottom-up by layer (core → sim → strategy → ui) | Dependencies flow upward; fixing lower layers first ensures stability |
| 2026-02-06 | Keep existing fallback behavior unchanged | Only narrow exception types, don't change recovery logic (return values, logging patterns) |
| 2026-02-06 | Clipboard and Tkinter catches stay broad | Platform-dependent code with unpredictable failure modes; broad catch is correct |
| 2026-02-06 | Event bus/handler isolation stays broad | Handler isolation is a deliberate pattern — handlers must never crash callers |
| 2026-02-06 | Formula eval() catch-and-convert stays broad | eval() can throw any exception; wrapping in FormulaException is the correct pattern |
| 2026-02-06 | Safety-net-with-re-raise stays broad | Logging before re-raise is diagnostic; broad catch is needed to log all errors |
| 2026-02-06 | Replace `print()` with logger in 3 builder files + test_lab.py | Console prints are not captured in log files; proper logging aids debugging |
| 2026-02-06 | No new exception classes needed | Existing hierarchy (PROJ-45) covers all semantic categories already |
| 2026-02-06 | No new error handling tests needed | Existing coverage (15 tests for save_game_service, 7 for race_asset_loader, etc.) is adequate |
| 2026-02-06 | pygame.error must be explicit in image catches | pygame.error is NOT a subclass of OSError; must include separately |
