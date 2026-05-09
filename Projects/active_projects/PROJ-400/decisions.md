# PROJ-400: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 1 B-01: NewGameSetupScreen deleted-wrapper call |
| 2026-05-09 | Call shape: `NewGameSetupController.generate_default_save_name()` (class-static, no args) | The controller method is `@staticmethod` taking no args (controller.py:268-271). Mirrors the existing `NewGameSetupController.validate_save_name(...)` call already in the same file at line 162 — same import already at module top, no instance plumbing needed. PROJ-392 migrated all other callers to this exact shape. |
