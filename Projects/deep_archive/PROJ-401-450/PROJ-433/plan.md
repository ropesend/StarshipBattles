# PROJ-433: component_inspector split

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-433` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-433 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 0. Characterization — pin current `component_inspector` surface with focused tests | Complete | [phase_0_checklist.md](phase_0_checklist.md) |
| 1. Split `component_inspector.py` into `component_abilities.py` + `component_layers.py` | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Verification + docs | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-17
**Active Phase:** Project execution complete
**Last Action:** Phase 2 complete. Full sharded suite 21144/21144 passed. `docs/04_SERVICES.md` and `docs/guides/component_system.md` updated to describe the split; PROJ-425 findings_ledger back-link added. Final LOC: `component_abilities.py` = 403, `component_layers.py` = 168, `component_inspector.py` (shim) = 67.
**Next Action:** Awaiting user verification.
**Blockers:** None. Predecessor PROJ-425 Phases 0-5 are complete on `proj/PROJ-425/main`.

## Overview
`game/strategy/services/component_inspector.py` is 537 LOC — past the 500-LOC project ceiling — after PROJ-425 Phase 2 added the per-instance layer-view helpers (`iter_components_by_layer`, `damaged_components_by_layer`, `count_damaged_components`, `lookup_design_max_hp`) to a module that already owned the ability-iteration helpers (`get_component_abilities`, `ship_has_ability`, `find_ship_with_ability`, `count_ability`, `list_ship_abilities`, `get_ability_list`, `iterate_design_components`, `iter_facility_ability_entries`, `has_warp_capability`, etc.). The split point is clean: `component_inspector.py:404-501` is the layer-view block that PROJ-425 Phase 2 added; everything above it is the pre-existing ability surface.

This project splits the module into `component_abilities.py` (ability iteration + has_warp_capability + lookup_design_max_hp helpers) and `component_layers.py` (the layer-view helpers added by PROJ-425 Phase 2). Module surface stays compatible — either via a re-export `__init__.py` shim or by updating consumers to import from the new module locations directly. No behavior change. PROJ-425's Phase 2 findings_ledger entry already flagged this split as a deferred follow-up: "Above the 500-LOC guideline but already-shared infrastructure module — split deferred as the additions are cohesive ship-introspection helpers; revisit if it grows further." Codex's consult is the "revisit" trigger.

## Goals
- Split `component_inspector.py` into two modules each materially under 500 LOC.
- Preserve all current `__all__` exports — either via the package re-export pattern (`game/strategy/services/component_inspector/__init__.py` re-exports) or by migrating consumers' imports to the new module paths (decision deferred to Phase 1).
- No behavior change; existing tests + sharded suite stay green.

## Scope
**In:**
- New module(s): `game/strategy/services/component_abilities.py` + `game/strategy/services/component_layers.py` (or equivalent package split).
- Updates to imports in any production file or test file that currently imports from `game.strategy.services.component_inspector` (only if the import surface moves — depends on Phase 1's `__init__` decision).
- Focused tests pinning the public surface in Phase 0.
- Phase 2 docs update for `docs/architecture/` or `docs/refactoring/` if the split is documented anywhere.

**Out:**
- Behavior changes to any helper function — this is a pure-mechanical move.
- Renaming any function or changing its signature.
- Adding new helpers — only the move is in scope.
- Touching `game/strategy/data/ship_instance.py` (PROJ-425 territory; the entity's delegate calls do not need to change).

## Dependencies
- **Predecessor:** PROJ-425 Phases 0-5 complete on `proj/PROJ-425/main`. Hard predecessor only in the sense that PROJ-425 Phase 2 is what pushed `component_inspector.py` over 500 LOC. PROJ-425's still-gated Phase 6 (cargo / deployable forwarder demolition) does **not** block this project — it touches a different file (`ship_instance.py` + `ship_cargo_manager.py`).
- No other hard predecessors. No phase-gate dependencies with peer projects.

## Key Files
| Component | File Path | Action |
|-----------|-----------|--------|
| Source module (slim target) | [`game/strategy/services/component_inspector.py`](../../../game/strategy/services/component_inspector.py) | Edit (Phase 1: extract layer-view block; keep ability surface or rename) |
| New module — ability iteration | `game/strategy/services/component_abilities.py` | Create (Phase 1) |
| New module — layer view | `game/strategy/services/component_layers.py` | Create (Phase 1) |
| Existing tests — ability surface | `tests/unit/strategy/services/test_component_inspector.py` (and adjacent files) | Edit (Phase 0 characterization + Phase 1 import updates) |
| Existing tests — layer surface (PROJ-425 Phase 2) | `tests/unit/strategy/services/test_component_inspector_layers.py` | Edit (Phase 0 + Phase 1) |
| Caller — entity delegate | `game/strategy/data/ship_instance.py` | Edit (Phase 1, only if import path moves) |

Full enumeration in [manifest.md](manifest.md).

## Phases

### Phase 0: Characterization
Audit the current `__all__` surface of `component_inspector.py` (15 names — see `design.md`) and confirm every helper is covered by at least one focused test. Grep for all import sites: `rg -n "from game.strategy.services.component_inspector|import.*component_inspector" game tests`. Tighten existing tests in their current locations where coverage is thin. Run the focused suites to establish the regression baseline. Decide the public-surface contract for Phase 1 — re-export package vs. caller migration.

### Phase 1: Split into two modules
Move `component_inspector.py:404-501` (the PROJ-425 Phase 2 layer-view block: `iter_components_by_layer`, `damaged_components_by_layer`, `count_damaged_components`, `lookup_design_max_hp`) into `game/strategy/services/component_layers.py`. Move the ability iteration block (everything pre-line 404) into `game/strategy/services/component_abilities.py`. Either (a) keep `component_inspector.py` as a re-export shim, or (b) delete it and migrate all import sites — choice locked in Phase 0.

Both new modules must be materially under 500 LOC. No function signatures change.

### Phase 2: Verification + docs
Run focused + sharded suites. Update `docs/architecture/` or `docs/refactoring/` if `component_inspector.py` is referenced anywhere. Update PROJ-425's `decisions.md` / `findings_ledger.md` with a back-link noting the split landed.

## Related Documents
- Predecessor: [PROJ-425 plan](../PROJ-425/plan.md) — TD-06 ShipInstance slimming; Phase 2 pushed `component_inspector.py` over 500 LOC.
- PROJ-425 findings reference: `Projects/active_projects/PROJ-425/findings_ledger.md` §"Phase 2" (the deferred-split note).
- [design.md](design.md) — distilled architecture with the file:line evidence for the split point
- [decisions.md](decisions.md) — full decisions log
- [manifest.md](manifest.md) — enumerated file touch list
- [findings_ledger.md](findings_ledger.md) — running findings ledger per the 03c protocol

## Verification
- [ ] `component_inspector.py` is gone OR is a thin re-export shim; the bulk of its body lives in `component_abilities.py` + `component_layers.py`.
- [ ] Both new modules are materially under 500 LOC.
- [ ] Every export listed in the original `__all__` is still importable from somewhere (whether via re-export or via the new module's direct path).
- [ ] No function signature changed.
- [ ] `pytest tests/unit/strategy/services/test_component_inspector*.py` is green.
- [ ] `pytest tests/unit/strategy/ship_instance/` is green (entity's delegate calls still work).
- [ ] `python Tools/test_sharded/test_sharded.py` is green.
- [ ] Docs updated where `component_inspector.py` is referenced (if any).
- [ ] User verified.
