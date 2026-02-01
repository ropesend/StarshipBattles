# PROJ-41: Decisions Log

## Decision 1: Phase Structure
**Date:** 2026-01-27
**Decision:** Organize work into 3 phases by priority (Critical → High → Archive)
**Rationale:** Critical issues (Phase 1) cause broken code and must be fixed first. High priority issues (Phase 2) cause confusion but not failures. Archival (Phase 3) is organizational cleanup that can wait.
**Alternatives Considered:**
- Single phase (rejected - too large, no prioritization)
- By document type (rejected - doesn't reflect urgency)

## Decision 2: Archive vs Delete
**Date:** 2026-01-27
**Decision:** Archive obsolete documents rather than delete them
**Rationale:** Preserves historical context and git history. Documents may have value as reference even if outdated. Easy to restore if needed.
**Alternatives Considered:**
- Delete (rejected - loses history)
- Leave in place with OBSOLETE marker (rejected - clutters docs folder)

## Decision 3: Source of Truth
**Date:** 2026-01-27
**Decision:** Use actual codebase as source of truth for documentation corrections
**Rationale:** The audit compared docs to code and found code to be correct. Documentation should reflect implementation, not vice versa.
**Alternatives Considered:** None - this is standard practice.
