# PROJ-228: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-26 | Project initialized | Starting point for Reduce complexity: filter_ships (CC 36) |
| 2026-02-26 | Use generic `_passes_binary_filter()` helper | Binary filter pattern repeats 4+ times with identical structure |
| 2026-02-26 | Extract `_get_ship_status()` helper | Status determination is reusable and testable; similar logic exists in `sort_ships` |
| 2026-02-26 | Keep status priority chain inline initially | Critical invariant - only extract after test coverage confirms correctness |
| 2026-02-26 | Move late import before ship loop | Currently imports inside loop (line 185); should import once before loop |
| 2026-02-26 | Replace `_skip` flag with helper function | `_passes_special_capability_filters()` can use early return instead of flag |
| 2026-02-26 | Add test fortification phase | Safety analysis found coverage gaps for edge cases |
| 2026-02-26 | Target CC < 20 | Per complexity_target.md; original CC is 36 (grade F) |
