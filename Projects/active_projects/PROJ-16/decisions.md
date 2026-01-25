# PROJ-16: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-25 | Project initialized | Starting point for Legacy Cleanup Phase 3 - Consolidate Re-exports |
| 2026-01-25 | Use package-level __init__.py facades instead of just removing re-exports | Maintains import convenience, establishes proper Python package structure, follows existing pattern in services/__init__.py |
| 2026-01-25 | Move calculate_snap_value() to ModifierControlRow instead of creating new utility file | Only 2 call sites in modifier_row.py - natural home for UI-specific snap logic, eliminates entire wrapper file |
| 2026-01-25 | Simplify ProfilerProxy to direct assignment `PROFILER = Profiler.instance()` | instance() is already thread-safe with double-checked locking; simplifies code while maintaining backward compat |
| 2026-01-25 | KEEP ShipControllableAdapter - not a Phase 3 candidate | Essential adapter pattern for AI system; backward compat features are actively tested; would require Ship to implement IControllable directly (separate project) |
| 2026-01-25 | Update order: Package facades -> Test infrastructure -> Production code -> Remove old re-exports | Root conftest.py affects ALL tests; must update dependencies before dependents to avoid cascading failures |
| 2026-01-25 | Remove dead TargetEvaluator re-export immediately | 0 imports found - pure dead code that can be safely removed |
