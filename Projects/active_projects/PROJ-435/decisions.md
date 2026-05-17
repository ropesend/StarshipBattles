# PROJ-435: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-17 | Project initialized as a PROJ-429 Phase 8 spin-off | Codex consult finding 4 (PROJ-429 Phase 8) flagged `_ACTIVATABLE_ABILITIES` in `stat_rows_dynamic.py:381-463` as a hardcoded literal set, but the UI map has UI-specific structure (display labels + 2 abilities not in the registry) that prevents a mechanical inline migration. Spun off rather than forcing migration in PROJ-429. |
| 2026-05-17 | Phase 1 must decide registry-extension vs UI-side label map (Options A/B/C in design.md) | The two viable migrations make different layering trade-offs; the call is not pre-determined by existing patterns. |
