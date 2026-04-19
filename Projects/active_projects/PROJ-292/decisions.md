# PROJ-292: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-18 | Project initialized as the sibling of PROJ-291 | PROJ-291 owns Critical findings; PROJ-292 owns High/Major/Minor. Two-project split per user answer to Q4. |
| 2026-04-18 | H1 (view-kwarg threading) classified as HIGH severity | Impartial subagent overruled the prior audit's "by design / minor" call. BuildQueuePanelFactory ONLY shows colonized planets and currently uses legacy rendering — clear UX miss. PlanetListWindow shows both colonized + uncolonized. PlanetSelectionWindow filters to uncolonized so legacy is correct there. |
| 2026-04-18 | H1 fix touches PlanetListWindow + BuildQueuePanelFactory only | PlanetSelectionWindow is uncolonized-only by design (colonization-flow filter). Touching it would add a no-op `view=None` and noise. |
| 2026-04-18 | M1 fix uses a service-layer facade (`empire_economy_service.py`), NOT a thin re-export | Per docs/01_ARCHITECTURE.md and CLAUDE.md Rule 3, the right shape is a real service that exposes a read-only snapshot, not a re-export shim. The calculator stays in the engine layer; only the read surface (`get_snapshot`) crosses into services. |
| 2026-04-18 | M2 mtime-fallback is OPT-IN, default OFF | Defaulting to mtime-watching adds filesystem-stat noise on every `get_race` call. PROJ-287's documented contract is "external file edits require restart". Don't change the default; let the user opt in via the new `auto_refresh_on_mtime: bool = False` kwarg. Phase 3 Task 3.3 surfaces the user decision to actually wire the kwarg in production callers. |
| 2026-04-18 | M3 (Treasury Upkeep e2e test) is closed by PROJ-291 Phase 1 Task 1.3, not by this project | PROJ-291's `tests/integration/strategy/test_treasury_panel_e2e.py` IS the e2e pin the audit asked for. Tracking M3 here as a no-op to confirm post-PROJ-291 that the test exists. |
| 2026-04-18 | M4 (cache-rollback concern) is CLEARED by impartial subagent | `TurnStateSnapshot.restore()` does `session.galaxy = Galaxy.from_dict(...)` — full deserialization discards stale planet objects. `init=False` cache fields can never carry stale data across rollback. No action needed. |
| 2026-04-18 | m11 (`last_food_ratio` rename to `last_supply_ratio`) is EXPLICITLY OUT OF SCOPE | Touches engine docstrings + tests + multiple docs + UI labels. Warrants its own project (PROJ-293 if user wants it later). The minor sweep in Phase 5 keeps to docstring-only changes. |
| 2026-04-18 | m14 (`IRaceRegistry` protocol surface expansion) is OUT OF SCOPE | YAGNI per CLAUDE.md. No real consumer needs `iter_races()` yet. Document the extension policy in `IRaceRegistry`'s docstring instead. |
| 2026-04-18 | m17 (`projects_index.md` `w# Projects Index` typo) FIXED in Phase 5 | Trivial. Was flagged in my session-end review but missed in the prior audit. |
| 2026-04-18 | Phase 2 (M1 facade) sequenced AFTER PROJ-291 Phase 1 (C1 fix) | Both touch `empire_economy_calculator.py`. PROJ-291's 1-line addition lands first; PROJ-292's facade wraps the calculator without modifying it. Avoids merge friction. |
