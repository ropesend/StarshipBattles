# PROJ-76: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Empire-Wide Build Queue Window |
| 2026-02-07 | Add new button instead of replacing existing "Build Queues" | Keep existing button for backward compatibility; users may prefer per-hex access |
| 2026-02-07 | Use modular file structure | Follow PlanetListWindow pattern for maintainability; can extract modules later |
| 2026-02-07 | Row click opens hex build screen | Reuse existing BuildQueueScreen rather than inline editing; keeps complexity manageable |
| 2026-02-07 | Ctrl+click for multi-select | Consistent with BuildQueueScreen pattern; familiar Windows/Linux convention |
| 2026-02-07 | Start without virtual scrolling | Can add later if performance issues arise; most empires won't have 100+ queues |
| 2026-02-07 | Column visibility only (no reordering) | Simpler v1; reordering adds complexity without much benefit |
| 2026-02-07 | No preset save/load initially | Can add later following PlanetListWindow pattern if users request it |

## Open Questions

None currently.

## Implementation Notes

(Add notes here during implementation)
