# PROJ-382: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-07_220452_pattern-audit/`
- **Audit date:** 2026-05-07
- **Audit verifier outcome:** 2 CRITICAL confirmed (VER-002, VER-003), 1 DISPUTED (VER-001 → out-of-scope here), 1 INCONCLUSIVE.

### Bundle counts
- **Audit verified candidates entering this run:** 49 (incl. 14 LOC, 5 doc-drift/undoc, 30 pattern items)
- **This bundle:** 21 verified + 6 user-included uncertain (U4, U5, U6) + 5 in-scope LOC ceiling files = ~32 actionable items
- **Deferred / out-of-scope:** U1 (~127 UI command DTO imports), U2 (40 service imports), U3 (26 systems imports), 9 LOC files in active PROJs, 13 REJECTED items, 1 DISPUTED (VER-001).
- **Project siblings created in this run:** none — single-bundle decision per V<30 rule and user direction.

### Layer + pattern-area coverage
| Layer | Pattern areas in scope |
|-------|------------------------|
| `ui/` | #5 Facade (CRITICAL), #31 Strategy Modal Window, #10 EventBus rename, #12 json_utils (detail_panel, setup_data_io), undocumented Re-Export Shim |
| `strategy/` | #5 Facade root (StrategyScreen privatization), #6 CQRS-lite tautology, #7 CommandHandlerRegistry shim import + doc, #10 EventBus dual-path (Empire/Fleet), #12 json_utils (race_library, galaxy_warp_generator), #3 ProductionSpawner DI tightening, undocumented Strategy Config Singleton |
| `simulation/` | #2 TypeGuard miss (galaxy_spatial_index), #10 module-level `log_event` (projectile), convention §6.5 (hardcoded superweapon list), empty `__init__.py`, LOC ceiling (planetary.py, battle_engine.py) |
| `docs/` | Pattern #23 phase list, Pattern #7 canonical path, Re-Export Shim doc-add, Pattern #12 singleton-accessor clarification |

### Severity breakdown (final after re-verification)
- **CRITICAL:** 2 (Pattern #5 facade bypass, both rooted in StrategyScreen session leakage)
- **MAJOR:** 9 (Pattern #2 TypeGuard, 4× Pattern #10 dual-path/module-level, Pattern #31, hardcoded superweapon list, EventBus rename, empty `__init__.py`)
- **MINOR:** 7 (Pattern #6 tautology, Pattern #7 shim import, 4× Pattern #12 json/json_utils, Pattern #3 ProductionSpawner)
- **MINOR doc-drift:** 2 (Pattern #23, Pattern #7)
- **STRATEGIC:** 2 (Re-Export Shim doc-add, Strategy Config Singleton doc-add)
- **LOC ceiling:** 5 files (Phase 5)

## Risk Notes

### Phase 1: Pattern #5 facade-bypass decay
The two CRITICAL findings in this project (VER-002, VER-003) are not minor stylistic drift — they are architectural-decay paths. Specifically:

- **Dual command paths (`session.handle_command` vs `facade.handle_command`)** mean the same UI action can land in two different write channels depending on whether `facade` happened to be passed at construction time. This is the precise shape of the bug class CQRS-lite (Pattern #6) is designed to prevent.
- **Public `self.session` on `StrategyScreen`** is the *root cause* of the dual-dispatch bypass downstream. Privatizing it without an AST static-guard is reversible silently — a future PR adding a child screen could trivially re-introduce `session=self._screen.session` and the bypass would re-grow without any test failing.

PROJ-306 shipped exactly this kind of static-guard against `get_default_registry_provider` calls in `game/simulation/`. Phase 1 Task 1.5 is a direct application of that template — *do not skip it.* The acknowledged-debt comments (`# PROJ-208 Phase 3`) on the bypass sites confirm the team knew this was wrong; the static guard ensures the next decay attempt is caught at test-time.

### Phase 2: Pattern #10 EventBus rename surface
Renaming the workshop `EventBus` to `WorkshopEventBus` touches ~15 importers but is mechanically straightforward. The risk is missing an importer; mitigation is grep-completeness verification before the phase verification step.

### Phase 5: LOC decompositions are real refactors
Each Phase 5 file is a real architectural decomposition (mostly file splits with re-exports). Do not attempt them alongside Phases 1-4. Run them sequentially after the pattern work lands. If any of them needs significant design work, escalate to a sibling project rather than hammering through Phase 5.

## Key Patterns to Reuse
- **AST static-guard test (PROJ-306 reference):** `tests/architecture/test_no_simulation_get_default_registry_provider.py` — copy this shape for Phase 1 Task 1.5.
- **`StrategyModalWindow` base class (Pattern #31):** `game/ui/screens/strategy_modal_window.py` — Phase 2 `DesignSelectorWindow` migration.
- **`SUPERWEAPONS` registry (data-driven):** `game/strategy/services/superweapon_registry.py` — Phase 2 `_SUPERWEAPON_ABILITIES` replacement.
- **`is_planet` TypeGuard:** `game/core/protocols/strategy_entities.py:424` — Phase 2 `galaxy_spatial_index.py` replacement.
- **`json_utils`:** `game/core/json_utils.py` — Phase 3 bare-json replacements.

## Design Decisions
See [decisions.md](decisions.md) for the bundling rationale and Phase D user decisions.
