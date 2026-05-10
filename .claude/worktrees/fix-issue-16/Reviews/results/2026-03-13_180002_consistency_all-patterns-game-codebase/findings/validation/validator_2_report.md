# Validation Report: Validator 2

## Summary
- **Findings Reviewed:** 7
- **Confirmed:** 3
- **Downgraded:** 2
- **Rejected:** 2
- **Rejection Rate:** 29%

## Verdicts

#### Finding: AR-008
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** The method is `_apply_shield_interference` (not `_apply_shield_fatigue` as claimed), and it does directly set `ship.max_shields` and `ship.current_shields` at lines 198-201. However, these are plain instance attributes (not computed via the ability system), and this is an intentional pre-battle environmental modifier (storm shield interference per PROJ-189), not a general-purpose stat mutation. The direct manipulation is appropriate for a temporary battle-scoped effect. The method name and context in the finding are inaccurate.

#### Finding: AR-009
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** There are 92 `hasattr()` occurrences across 49 files, not 41 as claimed. However, examining the distribution shows most are in UI code doing defensive checks on heterogeneous objects (panels, windows, widgets) where protocol enforcement would be impractical. The simulation/core layers use protocols correctly. This is a minor code smell in the UI layer, not a major architectural violation.

#### Finding: AR-010
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Only 1 file outside the aggregator module itself imports from `ability_aggregator` (`ship_stats.py`), while 4 other files import specific functions (`calculate_ability_totals`, `get_ability_total`, `get_ability_instances_by_class`). Meanwhile, 13 files directly iterate `.ability_instances` with 29 occurrences. The pattern exists but is underutilized relative to direct iteration, as described.

#### Finding: AR-011
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Three distinct event/callback systems verified: (1) `core/event_logging.py` with global handler pattern, (2) `EventBus` in builder UI across 14 files, (3) `EventLog` in strategy layer across 7 files. The callback count (460 occurrences across 59 files) exceeds the claimed 67 files. These systems are independent and serve different domains, which is a real architectural concern for consistency.

#### Finding: AR-012
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** `StrategyMetadataService` in `core/` is an intentional decoupling layer. Its docstring explicitly states it exists to decouple UI from the AI layer's `StrategyManager`. Placing it in `core/` is correct because core is the shared dependency layer that both AI (writer) and UI (reader) can access. Moving it to `strategy/` or `ai/` would create the very cross-layer dependency it was designed to prevent. The "Strategy" in its name refers to combat strategies (game domain concept), not the `strategy/` code layer.

#### Finding: AR-013
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified that `game/research/` has zero imports from outside `game/ui/research/`. Grep for `from game.research` excluding the research directory itself returned no results. The research layer is consumed only by UI research screens, making it effectively a UI subsystem that happens to live at the top level.

#### Finding: AR-014
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is a positive observation ("architecture is clean here"), not an actionable finding. Info-level positive findings do not constitute issues to validate. The observation about GameSession as composition root appears accurate from the docstring, but there is nothing to confirm or deny as a problem.
