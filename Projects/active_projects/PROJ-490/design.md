# PROJ-490: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit
- **Audit directory:** `Reviews/results/2026-05-20_210635_legacy-audit/`
- **Bundle counts:** Audit verified: 17 (across all sibling projects) | This bundle: 9 verified, 0 uncertain, 0 INFO, 0 deferred
- **Sibling projects:** PROJ-484, PROJ-485, PROJ-486, PROJ-487, PROJ-488, PROJ-489
- **Cluster identity:** stale_comments — orphan markers, archived-PROJ references, and contradictory doc comments
- **Severity breakdown:** 0 CRITICAL, 0 MAJOR, 9 MINOR

## Initial Analysis
The audit's verifier confirmed nine documentation-quality issues across seven files. None affect runtime behavior. The cluster's "system being eradicated" is the practice of leaving stale historical or contradictory comments in active production modules.

### Categories
- **Orphan references to deleted symbols** (LEG-01-002, LEG-01-003, A-05): comments in `ship_instance.py` claim a `carried_items` property exists, but it was deleted in PROJ-436 Phase 9.
- **Archived PROJ references** (LEG-02-009 PROJ-225, LEG-02-010 PROJ-67, LEG-02-011 PROJ-218): each project is in deep_archive and the work is long complete.
- **Misleading prose** (D-01 "legacy projection"): comment misrepresents current architecture by labeling canonical data flow as "legacy."
- **Fallback for legacy test stubs** (LEG-02-002 `mine_group_service.py:130`): the comment correctly notes legacy test usage; the fallback exists for compatibility but lacks a removal date or PROJ reference.

### Architecture
No architectural impact — pure documentation hygiene.

### Key Patterns to Reuse
- **Dated TODOs with PROJ references**: any comment marking transitional code should include a target removal date or PROJ ticket. The `mine_group_service.py` fallback is the canonical case where this pattern applies.

### Dependencies & Risks
1. **Comment-only changes** — no behavioral risk. Test suite should pass unchanged.
2. **`mine_group_service.py` Task 1.4 has a fork** — either add a dated TODO (minimal change) or migrate the test stubs and remove the fallback (cleaner). Either is fine; the project commit message should record which path was taken.

### Opportunities Discovered
- If Task 1.4 chooses the "migrate test stubs and remove fallback" path, the resulting `mine_group_service.py` becomes simpler — single attribute lookup instead of an iteration.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
