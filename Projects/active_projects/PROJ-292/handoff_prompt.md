# Handoff: PROJ-292 — Phase 1 (H1 — Thread `view` kwarg into PlanetListWindow + BuildQueuePanelFactory)

Resume **PROJ-292** at **Phase 1**. PROJ-292 is the sibling of PROJ-291. PROJ-291 fixes 3 Critical bugs (gates PROJ-283..290 sign-off); PROJ-292 cleans up 3 High + 3 Major + 11 Minor findings from the same dual cross-project audit. **Phase 1 + Phase 4 + Phase 5 are fully parallel-safe with PROJ-291** — pick them up any time. Phase 2 + Phase 6 should sequence after PROJ-291 Phase 1 (both touch `empire_economy_calculator.py` indirectly).

## Orientation (read BEFORE touching the project plan)

PROJ-292 is largely mechanical — UI threading, an exception-narrow, a service facade, and a Minor sweep — but the H1 fix corrects an actual UX regression that was discovered via impartial-subagent adjudication of a disagreement between two prior reviews. Load context first.

### 1. Audit provenance (read these THREE FIRST so you understand why this project exists)

- [`Projects/active_projects/PROJ-291/findings/INDEX.md`](Projects/active_projects/PROJ-291/findings/INDEX.md) — directs you to the dual audit + impartial subagent verdicts. PROJ-292's findings live in this index.
- [`Projects/active_projects/PROJ-291/findings/SUMMARY.md`](Projects/active_projects/PROJ-291/findings/SUMMARY.md) — the prior audit's executive summary. PROJ-292 owns its M1, M2, m1, m4, m5, m13.
- [`Projects/active_projects/PROJ-291/findings/merge_hazards_skeptic.md`](Projects/active_projects/PROJ-291/findings/merge_hazards_skeptic.md) — the report that ORIGINALLY claimed H1 was "by design / minor". The impartial-subagent adjudication overruled it (see [PROJ-292 decisions.md](Projects/active_projects/PROJ-292/decisions.md) row 2).

### 2. Foundation docs (always read these before any work)

- `docs/README.md` — doc index.
- `docs/01_ARCHITECTURE.md` — layer rules. **Critical for Phase 2:** UI must not import from engine layer; the M1 facade fixes this.
- `docs/02_PATTERNS.md` — Pattern 5 (Facade), Pattern 6 (CQRS-lite). M1's facade follows the established pattern.
- `docs/03_CONVENTIONS.md` — file org + test conventions.
- `CLAUDE.md` — three non-negotiable rules. Rule 1 (TDD) enforced in every phase checklist.

### 3. Task-specific docs

- `docs/systems/strategy_layer.md` § Planet Report Panel UI surface (PROJ-289) — the section to update post-Phase 1 (note view threading completion).
- `docs/04_SERVICES.md` — add EmpireEconomyService entry post-Phase 2.

### 4. Reference code (read for context, even if you won't modify it)

**Phase 1 reference (correct view-threading):**
- [`game/ui/screens/strategy_detail_formatter.py:240-273`](game/ui/screens/strategy_detail_formatter.py#L240-L273) — `_show_planet_report` is the canonical wiring pattern. PROJ-292 backports it.

**Phase 2 reference (existing facade pattern):**
- [`game/strategy/facade/strategy_session_facade.py`](game/strategy/facade/strategy_session_facade.py) — `get_race_registry()` (PROJ-287) is the closest precedent for a service-layer accessor.
- [`game/strategy/services/`](game/strategy/services/) — existing services (FleetSpeedCalculator, ComponentInspector, etc.) for naming conventions.

### 5. The files PROJ-292 modifies

**Phase 1 (H1):**
- [`game/ui/screens/planet_list_window.py:511`](game/ui/screens/planet_list_window.py#L511) — Phase 1 Task 1.3 adds `view = facade.get_colony_demographic_view(planet.id) if planet.owner_id is not None else None` then passes `view=view` to `PlanetReportPanel(...)`.
- [`game/ui/screens/build_queue_panel_factory.py:181`](game/ui/screens/build_queue_panel_factory.py#L181) — Phase 1 Task 1.5 same pattern. **High-value fix:** BuildQueuePanel ONLY shows colonized planets, so this goes from 0% to 100% PROJ-289 coverage in this context.
- `tests/unit/ui/screens/test_planet_list_window.py` + `test_build_queue_panel_factory.py` — Phase 1 Tasks 1.2 + 1.4 add `TestViewThreading` test classes (write FIRST, watch them fail, then apply fixes).

**Phase 2 (M1):**
- `game/strategy/services/empire_economy_service.py` (NEW) — Phase 2 Task 2.3 creates the facade. Shape in design.md § M1.
- [`game/ui/panels/empire_treasury_panel.py:19`](game/ui/panels/empire_treasury_panel.py#L19) — replace direct engine import.
- [`game/ui/screens/empire_panel_window.py:18`](game/ui/screens/empire_panel_window.py#L18) — same.
- ⚠️ **Phase 2 must NOT start until PROJ-291 Phase 1 has landed** (the C1 1-line fix to `total_expenses` aggregation in `empire_economy_calculator.py`). Phase 2 wraps the post-fix calculator. Task 2.1 verifies this gate.

**Phase 3 (H2 + M2):**
- `tests/integration/strategy/test_projector_drain_matches_engine.py` (NEW) — pin H2 contract.
- [`tests/unit/strategy/systems/test_race_library.py`](tests/unit/strategy/systems/test_race_library.py) — add `TestCachedRaceRegistryStaleness` for M2.
- ⚠️ **Phase 3 Task 3.3 has a USER DECISION POINT** for the optional mtime-fallback. Recommend NO; don't add the kwarg unless user opts in.

**Phase 4 (H3):**
- [`game/ui/panels/planet_report_panel.py`](game/ui/panels/planet_report_panel.py) — narrow `except (AttributeError, Exception)` to `except AttributeError` in `_build_projection_grid` net-cell colour code.

**Phase 5 (Minor sweep):**
- 11 small tasks. Each is independent. See `phase_5_checklist.md` for the per-task file references. Notable: m17 = `Projects/projects_index.md` line-1 typo fix; m4 = `MappingProxyType` wrap on `ColonyDemographicView.total_upkeep`; m5 = sort enforcement in `ColonyDemographicView.__post_init__`.

**Phase 6:**
- Doc updates + final sharded suite + projects_index.md status updates.

## Only now: read the project files

1. [`Projects/active_projects/PROJ-292/design.md`](Projects/active_projects/PROJ-292/design.md) — § Architecture has the exact code shape for each fix.
2. [`Projects/active_projects/PROJ-292/decisions.md`](Projects/active_projects/PROJ-292/decisions.md) — full decisions log. Row 2 explains the H1 severity-override (impartial verdict).
3. [`Projects/active_projects/PROJ-292/plan.md`](Projects/active_projects/PROJ-292/plan.md) § **Current State** — authoritative handoff context.
4. [`Projects/active_projects/PROJ-292/phase_1_checklist.md`](Projects/active_projects/PROJ-292/phase_1_checklist.md) — starts here.
5. [`Projects/active_projects/PROJ-292/manifest.md`](Projects/active_projects/PROJ-292/manifest.md) — files this project touches + cross-project overlap with PROJ-291.

## First action

Open `phase_1_checklist.md`. The literal next unchecked item is:

> **Task 1.1: Read the reference wiring [Simple]**
> Open [game/ui/screens/strategy_detail_formatter.py:240-273](game/ui/screens/strategy_detail_formatter.py#L240-L273) and locate `_show_planet_report`. Note the canonical wiring pattern:
> ```python
> view = None
> if obj.owner_id is not None:
>     facade = getattr(self.scene, "facade", None)
>     if facade is not None:
>         view = facade.get_colony_demographic_view(obj.id)
> ```
> This is the pattern Phase 1 backports to PlanetListWindow + BuildQueuePanelFactory.

TDD ordering for the project:
1. Phase 1 (H1) — view threading. Highest user-visible payoff. Six tasks, all mechanical.
2. Phase 4 (H3) — exception narrow. Three tasks. Very small.
3. Phase 5 (Minor sweep) — 12 tiny tasks. Pick by user priority.
4. Phase 3 (H2 + M2) — two new tests. One has a user-decision Q.
5. Phase 2 (M1) — service facade. **Sequence after PROJ-291 Phase 1 lands.**
6. Phase 6 — docs + final suite.

## Watchouts

1. **H1 was a real UX regression, not "by design".** The prior audit's `merge_hazards_skeptic.md` called this minor; an impartial subagent overruled it. Don't second-guess the decision — the impartial verdict was crisp: BuildQueuePanel ONLY shows colonized planets and currently shows the legacy single-line per-species rendering instead of PROJ-289's per-species sub-block. This is exactly the kind of "feature shipped half-done" gap PROJ-289 should not have closed without spotting.

2. **PlanetSelectionWindow is intentionally untouched** in Phase 1 — it filters to uncolonized planets in the colonization flow, so its legacy rendering is correct.

3. **Phase 2 sequencing.** Wait until PROJ-291 Phase 1 has landed (`tests/unit/strategy/engine/test_empire_economy_calculator.py::TestTreasuryTotalIncludesUpkeep` passes). Phase 2 wraps `EmpireEconomyCalculator` — if PROJ-291's 1-line fix isn't there yet, the wrapped calculator carries the C1 bug into PROJ-292's facade.

4. **Phase 3 Task 3.3 — USER DECISION REQUIRED.** Don't unilaterally add the `auto_refresh_on_mtime` kwarg. Stop and ask the user. Default recommendation: NO (preserves PROJ-287's documented contract; no filesystem-stat noise on every read).

5. **m11 and m14 are EXPLICITLY OUT OF SCOPE** — `last_food_ratio` rename + `IRaceRegistry` protocol surface expansion. Don't get sucked in. Documented in decisions.md.

6. **Phase 5's 12 tasks are independent.** If the user wants to prioritize a subset, run only those. The phase completion checklist allows partial sweeps documented as user-deferred.

7. **m9 (UI assembly test for `_build_projection_grid`)** is the only task in Phase 5 that's medium-complexity. The rest are doc tweaks, single-line fixes, or test additions. Sequence m9 after Phase 4 (H3 narrow) so the test can also exercise the corrected exception handling.

8. **Pre-existing flake.** Same as PROJ-291 — `test_copy_designs_without_themes_preserves_original` is long-standing. Phase 6 Task 6.3 expects it; not a PROJ-292 regression.

9. **Context budget.** PROJ-292 is 6 phases. Phase 1 + Phase 4 + Phase 5 are easily one session each. Phase 2 + Phase 3 + Phase 6 can fold into one session if landed sequentially. Hand off after any phase boundary.

10. **`Temp Review Docs/` cleanup.** PROJ-291 already copied the audit reports to `findings/`. The originals can be deleted by the user after they verify the archive — not PROJ-292's responsibility.

## Protocol

Follow `Projects/protocols/03a_continue_working.md`. Phase completion is a checkpoint, not an exit. Run `python Projects/scripts/validate_phase.py PROJ-292 [phase]` before stopping.

Final test command for the project: `python Tools/test_sharded/test_sharded.py` — expect ~15090 tests (15080 from PROJ-291 close + ~10 net new), ~1 known failure (the long-standing flake).
