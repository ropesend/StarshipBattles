# PROJ-13: Decisions Log

## Decision 001: Project Created from Review Findings
**Date:** 2026-01-24
**Status:** Approved
**Context:** Code review identified various code quality, documentation, and dead code issues that don't fit other projects.
**Decision:** Create catch-all project for remaining improvements.
**Rationale:**
- Clean codebase improves maintainability
- Documentation is critical for future development
- Dead code removal reduces confusion

## Decision 002: Dead Code vs Deprecation
**Date:** 2026-01-24
**Status:** Approved
**Context:** Should deprecated code be removed immediately or given deprecation period?
**Decision:** Remove immediately for internal deprecated code. Add deprecation warnings for any external-facing APIs (none identified).
**Rationale:**
- Internal code has no external consumers
- Deprecation warnings are unnecessary overhead
- Git history preserves old code if needed

## Decision 003: Documentation Priority
**Date:** 2026-01-24
**Status:** Approved
**Context:** Which documentation should be prioritized?
**Decision:** Priority order: Architecture overview → Core systems → Public APIs
**Rationale:**
- Architecture understanding is prerequisite for other docs
- Core systems have highest impact on development
- Public APIs can be documented incrementally

## Decision 004: Constants Organization
**Date:** 2026-01-24
**Status:** Approved
**Context:** Should all constants go in one file or be distributed?
**Decision:** Domain-specific constant classes in relevant modules, with shared constants in core/constants.py
**Rationale:**
- Keeps related constants together
- Avoids huge constants file
- Clear ownership of constants
