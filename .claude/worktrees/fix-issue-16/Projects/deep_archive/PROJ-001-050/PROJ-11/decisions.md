# PROJ-11: Decisions Log

## Decision 001: Project Created from Review Findings
**Date:** 2026-01-24
**Status:** Approved
**Context:** Code review identified critical layered architecture violations that prevent headless execution and testing.
**Decision:** Create dedicated project to establish clean layer boundaries.
**Rationale:**
- Enables headless testing and server deployment
- Reduces coupling for easier maintenance
- Prerequisite for clean god class decomposition (PROJ-12)

## Decision 002: Custom Vector2 vs External Library
**Date:** 2026-01-24
**Status:** Approved
**Context:** Need to replace pygame.math.Vector2 with something that doesn't require pygame.
**Options:**
1. Custom Vector2 class in game/core/math.py
2. Use numpy arrays
3. Use external library (e.g., euclid, pyrr)
**Decision:** Custom Vector2 class
**Rationale:**
- No new dependencies
- API compatibility with existing code (drop-in replacement)
- Full control over behavior
- Simple implementation for 2D vectors

## Decision 003: Phase Ordering
**Date:** 2026-01-24
**Status:** Approved
**Context:** Which layer separation to tackle first?
**Decision:** Phase order: Core Math → Simulation → Strategy-UI → Interfaces
**Rationale:**
- Core math is a prerequisite for simulation cleanup
- Simulation cleanup is larger effort, do it second
- Strategy-UI is smaller, do after simulation
- Interfaces are optional polish, do last

## Decision 004: Save File Compatibility
**Date:** 2026-01-24
**Status:** Pending
**Context:** Removing pygame Vector2 from persistence may affect save file format.
**Options:**
1. Store positions as (x, y) tuples (breaking change)
2. Store positions as dict {"x": ..., "y": ...} (readable)
3. Keep compatible format with migration
**Decision:** TBD - Need to analyze current save format first
**Rationale:** Will update when examining persistence.py in detail
