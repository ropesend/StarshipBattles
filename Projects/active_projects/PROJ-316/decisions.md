# PROJ-316: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-28 | Project initialized from PROJ-313 audit findings | Reviewer flagged 5 gaps after PROJ-313 merge. PROJ-316 is the focused follow-up to close them. |
| 2026-04-28 | Codify Phase 8 scope deviation (R3a) instead of executing demolition (R3b) | Demolishing `_handle_window_close` and 16 slot fields would require refactoring every `wm.X_window` caller (~30+ sites in `strategy_screen.py`, `strategy_event_router`, registrars). The structural modal-tracking fix is already complete via `iter_live_modals`; the slot fields now serve a different concern (caller-convenience pointers for rebuild_list, kill-before-reopen). Pattern #30 + #31 coexistence is sustainable with corrected docs. Full demolition can be a separate follow-up project if pursued. |
| 2026-04-28 | Keep `Optional[StrategyWindowManager]` typing on the base class but remove the default in Phase 2 | Forces every caller to pass the keyword (with either a real manager or explicit `None`) — making "I forgot it" impossible — without breaking `PlanetSelectionWindow` which legitimately needs `None` when called from `BuildQueueScreen`. |
| 2026-04-28 | Phase 3 uses three independent test types (subclass / registration / spawn-site) plus a manual mutation test | Each test catches a distinct way the structural guarantee can break. The manual mutation test in Task 3.5 is the proof the test suite has teeth — addresses the reviewer's concern that the original Phase 7 test would silently pass after a regression. |
| 2026-04-28 | PROJ-315 failures in `test_ship_instance_damage.py` are out of scope for PROJ-316 | Different project's responsibility (PROJ-315 = Fleet Report Component Damage Panel, in progress). Phase 4 verification subtracts these from the regression check. |
| 2026-04-28 | `_pending_confirmation_dialog` asymmetry remains out of scope | Was explicitly out of scope for PROJ-313; carries forward to PROJ-316 unchanged. Pre-existing latent bug, not within the audit findings. |
