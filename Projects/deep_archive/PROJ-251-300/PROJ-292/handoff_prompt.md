# PROJ-292 Handoff — Post-Close

PROJ-292 (Audit High + Major Cleanup) is CODE + DOCS COMPLETE. All 6 phases' engineering work landed in one session on 2026-04-19. The project's only remaining item is the consolidated user manual smoke checklist, which is the prerequisite for moving PROJ-283..292 from `Awaiting Verification` to `Archived`.

## Status at handoff

- **Phases 1–5:** Complete, validated (`validate_phase.py PROJ-292 N` → PASS for N=1..5).
- **Phase 6:** Code + docs tasks 6.1–6.3, 6.5, 6.6 complete. Task 6.4 (manual smoke) is user-gated; `validate_phase.py PROJ-292 6` FAILs on that item by design — a legitimate mid-phase stop per `03a_continue_working.md`.
- **Sharded suite:** 15139 tests, 15138 pass, 1 long-standing theme-bleed flake (same as PROJ-291 close, unrelated). Net +26 tests from PROJ-292.
- **PROJ-291 sibling:** same state — code complete, awaiting user manual smoke.

## What's blocking Archive

User must run through [Projects/active_projects/PROJ-292/MANUAL_SMOKE_CHECKLIST.md](MANUAL_SMOKE_CHECKLIST.md) in one sitting. Seven sections cover Treasury totals, FoodAllocationEditor, multi-species growth, per-species sub-block rendering across all 3 colonized-context entry points, uncolonized habitability, projection-grid exception handling, and race registry staleness.

## Next agent invocation (if user re-enters PROJ-292)

Load this context BEFORE touching the project plan:

### 1. Foundation docs (always)

- `CLAUDE.md` — the three non-negotiable rules. Rule 1 (TDD) was followed strictly throughout PROJ-292; re-read before writing any new code.
- `docs/README.md` — doc index.
- `docs/01_ARCHITECTURE.md` — layer rules (critical for understanding why M1 split calculator vs service).
- `docs/02_PATTERNS.md` — Pattern 2 (Protocol + TypeGuard), Pattern 3 (DI). M1's service-facade pattern reuses PROJ-287's `get_race_registry()` shape.
- `docs/03_CONVENTIONS.md` — naming, file org, test conventions.

### 2. PROJ-292-specific docs

- [plan.md](plan.md) — authoritative Current State + phase table.
- [design.md](design.md) — architectural rationale for each H/M/m finding.
- [decisions.md](decisions.md) — decision log. Critical entries: the 2026-04-19 M1 scope note, the 2026-04-19 M2 mtime-default decision, and the original 2026-04-18 H1/M1/M2 rationale.
- [manifest.md](manifest.md) — every file PROJ-292 touched (now includes Phase 1-5's additions).
- [findings/INDEX.md](findings/INDEX.md) — links to the dual-audit reports archived under PROJ-291/findings/.
- [MANUAL_SMOKE_CHECKLIST.md](MANUAL_SMOKE_CHECKLIST.md) — the Archive gate.

### 3. Related code that PROJ-292 touched

- **H1** view-threading:
  - [game/ui/screens/planet_list_window.py](../../game/ui/screens/planet_list_window.py) — `facade` kwarg + view resolution in `_on_planet_selected`.
  - [game/ui/screens/build_queue_panel_factory.py](../../game/ui/screens/build_queue_panel_factory.py) — `facade` kwarg + view resolution in `_create_context_report_panel`.
  - [game/ui/screens/strategy_window_manager.py](../../game/ui/screens/strategy_window_manager.py) — passes `facade=facade` to PlanetListWindow.
  - [game/ui/screens/build_queue_screen.py](../../game/ui/screens/build_queue_screen.py) — passes `facade=facade` to BuildQueuePanelFactory.
- **M1** service facade:
  - [game/strategy/services/empire_economy_service.py](../../game/strategy/services/empire_economy_service.py) (NEW).
  - [game/ui/panels/empire_treasury_panel.py](../../game/ui/panels/empire_treasury_panel.py) — import migration.
  - [game/ui/screens/empire_panel_window.py](../../game/ui/screens/empire_panel_window.py) — import + service construction.
- **H2** projector-vs-engine drain:
  - [tests/integration/strategy/test_projector_drain_matches_engine.py](../../tests/integration/strategy/test_projector_drain_matches_engine.py) (NEW, 3 tests).
- **M2** cache staleness:
  - [tests/unit/strategy/systems/test_race_library.py](../../tests/unit/strategy/systems/test_race_library.py) — +4 tests in `TestCachedRaceRegistryStaleness`.
- **H3** narrowed exception:
  - [game/ui/panels/planet_report_panel.py:456](../../game/ui/panels/planet_report_panel.py#L456) — narrowed to `except AttributeError`.
  - [tests/unit/ui/panels/test_planet_report_panel.py](../../tests/unit/ui/panels/test_planet_report_panel.py) — +2 tests in `TestNetCellColorExceptionHandling`, +3 in `TestProjectionGridAssembly`.
- **m4 + m5** DTO invariants:
  - [game/strategy/facade/dto/colony_demographic_view.py](../../game/strategy/facade/dto/colony_demographic_view.py) — `__post_init__` wraps `total_upkeep` in `MappingProxyType` + sorts species largest-first.
  - [tests/unit/strategy/facade/test_colony_demographic_view.py](../../tests/unit/strategy/facade/test_colony_demographic_view.py) — +5 tests.
- **m6**: [game/strategy/facade/strategy_session_facade.py](../../game/strategy/facade/strategy_session_facade.py) — `logger.warning` on `_resolve_economy_config` fallback.
- **m7**: [game/ui/screens/strategy_detail_fmt.py](../../game/ui/screens/strategy_detail_fmt.py) — tie-break docstring.
- **m13**: [docs/systems/strategy_layer.md](../../docs/systems/strategy_layer.md) — aligned growth-rate rendering claim to actual code.
- **Docs**: [docs/04_SERVICES.md](../../docs/04_SERVICES.md) (EmpireEconomyService entry), [docs/systems/strategy_layer.md](../../docs/systems/strategy_layer.md) (H1 completion note).
- **m17**: [Projects/projects_index.md](../../projects_index.md) — typo fix + PROJ-291/292 status update.

## Protocol

Follow `Projects/protocols/03a_continue_working.md`. If the user reports smoke-checklist failures, triage per finding:

- **Critical regression** (game crash, wrong numbers) → open a new PROJ-293 ticket.
- **Cosmetic / UX polish** → can land directly against the relevant source file without a project, unless the fix is non-trivial.
- **Smoke checklist has errors** → update `MANUAL_SMOKE_CHECKLIST.md` directly.

If the user signs off on smoke cleanly:

1. Update [Projects/projects_index.md](../../projects_index.md) — move PROJ-283..290, PROJ-291, PROJ-292 from `Awaiting Verification` → `Archived`.
2. Run `python Projects/scripts/validate_phase.py PROJ-292 6` — should PASS once Task 6.4 subtasks are checked.
3. Delete `Temp Review Docs/` (optional — findings/ is the durable archive).
