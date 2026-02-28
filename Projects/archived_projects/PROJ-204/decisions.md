# PROJ-204: Decision Log

## DEC-001: Phase Organization by Theme, Not Severity
**Date:** 2026-02-27
**Decision:** Organize phases thematically (foundation, quick wins, commands, strategy, UI) rather than by finding severity.
**Rationale:** Thematic phases allow each phase to be self-contained and reduce cross-phase dependencies. Foundation utilities in Phase 1 unblock later phases.

## DEC-002: Defer Large Architectural Findings
**Date:** 2026-02-27
**Decision:** Defer AR-01 (Parallel Delegate Hierarchies), AR-03 (DTO consolidation), AR-04 (Validation framework), AR-05 (Service framework), AR-06 (Calculator framework) to future projects.
**Rationale:** These are complex cross-cutting concerns that would expand scope significantly. Focus on concrete, bounded duplication elimination first.

## DEC-003: Scope Limited to Actionable Consolidations
**Date:** 2026-02-27
**Decision:** Include only findings where the consolidation is bounded and testable. Exclude findings marked as "no action needed" (CQ-51, CQ-86, CQ-87) and deferred items (CQ-83 blocked by PROJ-193).
**Rationale:** Keep project focused and completable. Each phase should be achievable in a single work session.

## DEC-004: LayerIterator in game/core/
**Date:** 2026-02-27
**Decision:** Place LayerIterator in `game/core/patterns/` rather than `game/strategy/services/`.
**Rationale:** Layer iteration is used across strategy, simulation, and UI layers. Placing in core avoids layer violations.

## DEC-005: DesignCostCalculator in game/strategy/services/
**Date:** 2026-02-27
**Decision:** Place DesignCostCalculator in strategy services, not core.
**Rationale:** Cost calculation is a strategy-layer concern. All current callers are in the strategy layer.
