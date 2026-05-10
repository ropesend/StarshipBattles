# PROJ-12: Decisions Log

## Decision 001: Project Created from Review Findings
**Date:** 2026-01-24
**Status:** Approved
**Context:** Code review identified three major god classes that impede maintainability.
**Decision:** Create dedicated project for decomposition with phased approach.
**Rationale:**
- Concentrated effort on highest-impact refactoring
- Phased approach reduces risk
- Clear dependencies between phases

## Decision 002: Facade Pattern During Transition
**Date:** 2026-01-24
**Status:** Approved
**Context:** Ship class is used throughout the codebase. Changing its interface would require updating hundreds of call sites.
**Decision:** Keep Ship as a thin facade that delegates to extracted classes.
**Rationale:**
- Backward compatibility maintained
- Callers don't need immediate updates
- Gradual migration path
- Can deprecate facade methods over time

## Decision 003: Phase Order
**Date:** 2026-01-24
**Status:** Approved
**Context:** Which god class to tackle first?
**Decision:** Ship → TurnEngine → RaceSetupScreen
**Rationale:**
- Ship is most critical and has clearest extraction points
- TurnEngine depends on Ship structure
- RaceSetupScreen is UI-only, lower risk
- Allows lessons learned to apply to later phases

## Decision 004: Component Manager vs Stats Aggregator
**Date:** 2026-01-24
**Status:** Approved
**Context:** Should stat calculation be in ComponentManager or separate class?
**Decision:** Separate ShipStatsAggregator class (already exists as ShipStatsCalculator)
**Rationale:**
- Single responsibility: components manage membership, aggregator calculates stats
- Existing ShipStatsCalculator can be evolved
- Cleaner testing boundaries

## Decision 005: TurnEngine Decomposition Granularity
**Date:** 2026-01-24
**Status:** Pending
**Context:** How fine-grained should TurnEngine decomposition be?
**Options:**
1. Three classes: Movement, Combat, Production
2. Four classes: Add separate OrderProcessor
3. Five+ classes: Further split movement/combat
**Decision:** TBD - will evaluate after Phase 2
**Rationale:** Need to see Ship decomposition results first
