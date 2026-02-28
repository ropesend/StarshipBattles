# PROJ-182: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized from PROJ-176 audit findings | Post-refactor cleanup of dead code and stale documentation |
| 2026-02-24 | Delete primitives.py (don't integrate into validators) | BaseCommandHandler `_resolve_*` methods already solve the same problem with a superior pattern (entity resolution in handlers, not validators). Integrating unused primitives would add coupling for zero benefit. |
| 2026-02-24 | Keep `with_errors` naming (don't rename to `errors`) | Only 4 call sites use it. The design doc said `errors()` but `with_errors()` avoids shadowing the `errors` field name on the dataclass. Renaming would be pointless churn. |
| 2026-02-24 | Keep CrewRequired `fallback_keys=('amount',)` | Works correctly, causes no harm, has test coverage. The `amount` key doesn't exist in current JSON but the defensive code is clean and harmless. |
| 2026-02-24 | Update PATTERNS.md ValidationResult entirely | The snippet is doubly stale: field name is wrong (`success` vs `is_valid`) AND all constructor examples use deprecated patterns. Both must be fixed together. |
| 2026-02-24 | Single-phase project | All 5 tasks are simple, independent edits with no dependencies between them. No need for phased execution. |
