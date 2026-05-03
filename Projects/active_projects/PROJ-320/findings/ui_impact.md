# PROJ-320 UI Impact Review: Combat Event Scheduling Shift

**Reviewer:** UI Impact Specialist  
**Date:** 2026-05-02  
**Project:** PROJ-320 — Shift strategy combat from per-tick to per-fleet-movement-opportunity  
**Scope:** All UI surfaces consuming COMBAT_RESOLVED events or rendering contested-hex feedback

---

## Executive Summary

PROJ-320 reduces event spam by shifting combat scheduling from per-tick (100 combats/turn max) to per-fleet-movement-opportunity (1-2 combats/turn typical). Impact:

- **Event Log:** Dramatically fewer combat rows → improved readability, but test assertions on event counts need updating
- **Filter columns:** No change to filtering logic; per-empire scoping is correct by design
- **Turn-end reporting:** No "N battles this turn" summary exists; no changes needed
- **Processing overlay:** UI remains blocked identically; fewer combat events don't affect blocking
- **Replay button:** Fewer disabled buttons (visual improvement); underlying issue #8 bug is independent
- **Battle results screen:** Auto-resolved combats never trigger results; no impact
- **Mini-map/hex visuals:** No combat indicators currently implemented; no impact
- **Audio cues:** No sound system found; no impact
- **Tooltips:** Hex info is occupancy-based, not history-based; no impact
- **Auto-pause:** No auto-pause logic found; no impact

**UI Breakage Risk: MEDIUM** (test assertions only; functional code is resilient)

---

## 1. Event Log Window & Data Source

**Files:** game/ui/screens/event_log_window.py, event_log_data_source.py, event_types.py

**Current Behavior:**
- EventLogWindow displays events newest-first (line 282)
- Combat events filtered by category == "combat" (line 213)
- Per-row Replay button on combats with replay_id (FEAT-26)

**Expected Changes:**
- Fewer combat rows per turn (1-2 vs. 100 typical)
- More diverse event types on first page
- More enabled Replay buttons (fewer disabled ghost combats)

**Breaking Points:**
- Tests asserting len(combat_events) > 5 per turn will fail
- Sample data should reflect realistic volumes (1-2 per turn)

**Assessment:** Functional code is resilient; only tests need updating.

---

## 2. Strategy Event Log Filter Columns (Per-Empire Scoping)

**Files:** event_log_data_source.py, strategy_session_facade.py, strategy_layer.md

**Current Behavior:**
- Category filtering is UI-level; empire filtering is facade-level (BUG-123 fix)
- EventLogWindow shows empire_name in title (line 102)
- One COMBAT_RESOLVED event appears in both empires' logs

**Expected Changes:** None — empire scoping is already per-facade-call

**Assessment:** No double-counting risk; per-empire visibility is correct by design.

---

## 3. Combat Result Aggregation (Turn-End Report)

**Files:** strategy_game_state_manager.py, strategy_screen.py

**Current Behavior:** No turn-end "combat summary" dialog exists; event log is the only summary

**Expected Changes:** None — event log presentation unchanged

**Assessment:** LOW RISK — the change actually improves readability.

---

## 4. Processing Turn Overlay & Per-Tick Feedback (Related to Issue #7)

**Files:** strategy_game_state_manager.py (line 96: turn_processing flag)

**Current Behavior:**
- UI is completely frozen for 100-tick loop
- No per-tick progress indicator currently exists
- Issue #7 will eventually add tick progress separately

**Expected Changes:** None — tick loop duration unchanged by PROJ-320

**Assessment:** ZERO IMPACT — issue #7 is independent and unaffected.

---

## 5. Replay Button (Issue #8 — Shortcut-Branch Bug)

**Files:** event_log_window.py (lines 379-388), event_log_data_source.py (lines 150-170)

**Current Behavior:** Per-row Replay button disabled when replay_id is None

**Expected Changes:**
- Fewer disabled buttons visible (cosmetic)
- Underlying shortcut-branch bug unchanged

**Assessment:** INDIRECT BENEFIT; issue #8 remains independent and unfixed.

---

## 6. Battle Results Screen Frequency

**Files:** battle_results_screen.py

**Current Behavior:** Only manually-launched battles show results; auto-resolved combats never pop the screen

**Expected Changes:** None — PROJ-320 affects strategy combats only

**Assessment:** ZERO IMPACT.

---

## 7-10. Mini-Map / Hex Indicators, Audio, Tooltips, Auto-Pause

**Summary:** None of these features exist or consume COMBAT_RESOLVED events.

**Assessment:** ZERO IMPACT across all four areas.

---

## Summary Table

| Item | Change | Impact | Tests at Risk |
|------|--------|--------|---------------|
| Event Log | 1-2 combats/turn instead of 100 | Readability improved | Event-count assertions |
| Filters | None | None | None |
| Turn Report | None | None | None |
| Processing Overlay | None | None | None |
| Replay Button | Visual improvement | None | None |
| Battle Results | None | None | None |
| Mini-Map | None | None | None |
| Audio | None | None | None |
| Tooltips | None | None | None |
| Auto-Pause | None | None | None |

---

## Tests to Update

**High Priority (Will Fail):**
- tests/integration/strategy/test_event_log_integration.py — assertions on len(combat_events) > 5
- tests/integration/strategy/test_combat_shortcut_paths.py — assertions on engine._combats_resolved counts

**Medium Priority:**
- tests/unit/ui/screens/test_event_log_window.py — sample data volume assumptions

**Low Priority:**
- tests/unit/ui/screens/test_event_log_data_source.py — filtering logic (unchanged)

---

## Recommendations

1. Update event-count test assertions to realistic volumes (1-2 per turn)
2. Verify per-empire event scoping works with single-event-per-conflict model
3. No UI code changes required — all consumption paths are volume-agnostic

---

## Conclusion

**UI Breakage Risk: MEDIUM** — Only test assertions will fail; functional code is resilient.

The event log is the only UI surface affected, and the change improves it. No production code changes required; only test refactoring for realistic event volumes.
