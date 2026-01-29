# PROJ-49: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-28 | Project initialized | Starting point for Performance & Dead Code Cleanup |
| 2026-01-28 | Skip DC-01, UI-002, UI-003 (broken imports) | Investigation by Explore agent confirmed imports work correctly via launcher.py adding project root to sys.path. Both `ui/` and `Tools/` directories have `__init__.py` and are importable. |
| 2026-01-28 | Skip SIM-021 (formula eval replacement) | Investigation confirmed the formula system is properly secured: uses AST validation, restricted builtins (`{"__builtins__": {}}`), whitelist-based approach with ALLOWED_MATH_FUNCTIONS. No security risk from internal game data. |
| 2026-01-28 | Dead code cleanup first, performance second | User preference. Quick wins from dead code removal clean up codebase and reduce confusion before tackling more complex performance optimizations. |
| 2026-01-28 | Archive dead code before deletion | User preference for safety. Dead code will be moved to `_marked_for_deletion_2026-01-28/` directory before final removal. Git history preserves code if rollback needed. |
| 2026-01-28 | Use property-based caching with dirty flags | Pattern already exists in ship.py (lines 98-102). Consistent with codebase patterns. Dirty flag invalidation prevents stale cache bugs. |
| 2026-01-28 | Build ability index at instantiation | MRO walking in get_abilities() is O(n) per lookup. Index lookup is O(1). Pattern matches existing caching approaches. |
| 2026-01-28 | Pre-calculate distances before targeting loop | Target evaluator recalculates same distance 2-3x per target. Pre-calculation with dict cache eliminates duplicates. |
| 2026-01-28 | In-place list modification for projectiles | Current list comprehension rebuilds entire list every tick. In-place mark-and-sweep with del slice is more efficient. |
| 2026-01-28 | Phase 5 (spatial grid) conditional on research | Incremental grid updates may be complex with uncertain benefit. Task 5.1 is research-only to evaluate cost/benefit before implementation. |

## Clarification Questions Asked

### Q1: Broken Imports Investigation
**Asked:** Should I skip the import issues or investigate further?
**Answer:** Investigate further
**Outcome:** Investigation confirmed imports work - excluded from scope

### Q2: Dead Code Handling
**Asked:** Delete directly or archive first?
**Answer:** Archive first
**Outcome:** Dead code will be moved to `_marked_for_deletion_2026-01-28/` before removal

### Q3: Formula eval() Security
**Asked:** Replace with custom parser or leave as-is?
**Answer:** Leave as-is (Recommended)
**Outcome:** Formula system confirmed secure - excluded from scope

### Q4: Priority Order
**Asked:** Performance first or dead code first?
**Answer:** Dead code first (Recommended)
**Outcome:** Phase 1 is dead code cleanup, Phases 2-6 are performance
