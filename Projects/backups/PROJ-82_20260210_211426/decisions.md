# PROJ-82: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Project initialized | Starting point for Planet Resources Panel Redesign |
| 2026-02-08 | Production rates passed as optional parameter | Cleanest separation of UI from harvesting logic. Panel doesn't need to know about HarvestingEngine internals. Caller computes and passes `Dict[str, float]`. |
| 2026-02-08 | Compact value format (250k, Q:85) | Space-efficient for narrow columns. Consistent with existing format used in format_planet_info(). |
| 2026-02-08 | Resource panel always shown | Appears in all contexts (both show_complexes=True and False). Resources are fundamental planet info. |
| 2026-02-08 | Reuse RESOURCE_PORTRAIT_FILES mapping, not BuildQueuePortraitLoader class | Panel loads icons directly via pygame.image.load using the existing filename mapping. Avoids dependency on DesignLibrary and Session objects that BuildQueuePortraitLoader requires. |
| 2026-02-08 | Fixed 100px height for resource panel | Enough for icon row (30px) + 3 data rows (20px each) + padding. Simple fixed layout. |
