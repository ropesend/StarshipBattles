# PROJ-92: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Project initialized | Starting point for Clean Up Residual Circular Dependency Artifacts |
| 2026-02-10 | Move entire hex_math.py to game/core/ (not just HexCoord class) | Module is self-contained (only depends on stdlib `math`). All functions (`hex_distance`, `hex_to_pixel`, `pixel_to_hex`, `hex_ring`, `hex_lerp`, `hex_linedraw`, `hex_to_dict`, `hex_from_dict`) are pure utilities with no strategy dependencies. Moving only HexCoord would split the module unnecessarily. |
| 2026-02-10 | Use temporary re-export shim at old location during migration | Ensures tests pass at every intermediate step. Pattern used successfully in PROJ-58. The shim at `game/strategy/data/hex_math.py` re-exports everything from `game/core/hex_math.py` so no callers break while imports are being updated. |
| 2026-02-10 | Delete the shim after all imports are updated — no permanent backward compat | Per CLAUDE.md "System Migration Policy": "When a new system replaces an old one, ERADICATE the old system completely." No permanent re-export layers. |
| 2026-02-10 | Skip Phase B deep dive swarm (6-8 agents) | The prior code review already thoroughly analyzed the architecture, all TYPE_CHECKING blocks, all late imports, and all cross-layer dependencies. No additional exploration needed for this mechanical refactor. |
| 2026-02-10 | User chose "Move HexCoord to core" over "Leave as-is" or "Use generic type" | Moving to core permanently fixes the core→strategy layer violation. The alternative (leaving it or using a generic type) would preserve the architectural inconsistency. |
