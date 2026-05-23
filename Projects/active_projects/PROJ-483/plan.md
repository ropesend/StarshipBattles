# PROJ-483: Type cleanup — Foundation + strict quick wins (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-483` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-483 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Foundation missing return | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Foundation narrowings | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor narrowings + AI protos + Protocol narrowings | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Strict-mode adoption — clean & near-clean layers | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** All phases complete — Phase 5 closed (audit remediation done).
**Last Action:** Executed all 5 Phase 5 tasks. (1) `game/engine/collision.py` — replaced silent `if beam_ab is not None:` guard with an assertion + cast; added regression test `test_beam_missing_ability_raises_assertion` in `tests/unit/engine/collision_edge_cases/test_beam_ramming.py`. (2) `game/ai/controller.py` — swapped `is_combatant` guard to `is_grid_entity` and dropped the `# type: ignore[attr-defined]`; updated 4 avoidance tests in `tests/unit/ai/test_ai_controller_unit.py` to patch the new symbol. (3) `game/simulation/interfaces/entity_protocols.py` — declared `get_components_by_layer` on `ICombatShip`; dropped the `# type: ignore` in `game/ai/target_evaluator.py`. (4) `game/simulation/entities/ship.py` — added class-level `layers: Dict[LayerType, "LayerData"]`; dropped the `# type: ignore` in `game/ai/interfaces/controllable.py`; widened abstract `IControllable.get_layers` to `Dict[Any, Any]` to keep adapter override Liskov-compatible. (5) `game/strategy/data/empire.py` — coerced `data['color']` list→tuple in `Empire.from_dict` to satisfy `IEmpire.color` protocol. Cross-cutting: `mypy game/research/ game/services/ game/assets/ game/engine/ game/ai/ game/core/` → 0 errors across 83 source files; `pytest tests/unit/engine/ tests/unit/ai/ tests/unit/simulation/interfaces/` → 493 passed.
**Next Action:** Project ready for user verification / archival.
**Blockers:** None

## Overview
Type-safety cleanup for the Foundation layers (core, simulation, ai, engine, services, assets, research) driven by the 2026-05-20 type audit. Combines ~10 per-finding narrowings + 5 AI protocol items + 16 Protocol-narrowing items (user opted in to use TYPE_CHECKING string annotations) with mypy `--strict` adoption for the 6 layers where adoption is bounded: research (0 errors → config-only), engine (14), ai (60), core (116), services (1), assets (15). Heavy strict-migration for simulation (622 errors per verifier) is **deferred** even though some simulation per-finding items are bundled here.

## Goals
- Phase 1: Resolve 1 CRITICAL — `_StatContributorRegistry.iter_for` missing return (generator method crossing layer boundary).
- Phase 2: Narrow ~5 MAJOR `-> Any` returns across simulation systems (`attack_processor`, `fighter_reboard` × 2), core registry (`get_validator`), and `evaluate_recursive` in `component_stats_calculator`.
- Phase 3: Narrow ~25 MINOR items: `planet_write_service.pop_construction_item`, 5 AI protocol narrowings (`IControllable.get_position/get_velocity`, `ShipControllableAdapter.get_position`, `IGridEntity.position`, `IProjectile.type`), and 16 Protocol-narrowing items across `core/protocols/*` and `simulation/interfaces/entity_protocols.py` (all TYPE_CHECKING string-annotation pattern, zero runtime cost).
- Phase 4: Adopt mypy `--strict` on the 6 bounded layers — config-enable research + investigate-and-fix engine/ai/core/services/assets.

## Scope
**In:**
- Per-finding narrowings + missing returns in `game/core/`, `game/simulation/`, `game/ai/`, `game/engine/`, `game/services/`, `game/assets/`, `game/research/`.
- Bulk Protocol-narrowing in `game/core/protocols/*` and `game/simulation/interfaces/entity_protocols.py` (16 items via TYPE_CHECKING).
- mypy `--strict` adoption for research / engine / ai / core / services / assets.

**Out:**
- UI per-finding cleanup — see sibling [PROJ-481](../PROJ-481/plan.md).
- Strategy per-finding cleanup — see sibling [PROJ-482](../PROJ-482/plan.md).
- mypy `--strict` adoption for `game/simulation/` (622 errors), `game/strategy/` (1,070), `game/ui/` (2,571) — deferred. See `decisions.md`.
- `formula_evaluator._eval_node` narrowing — user-deferred.
- `json_utils.load_json` / `load_json_required` — JSON inherently `Any`, OUT_OF_SCOPE.
- `ILocatable.location`, `IResourceHolder.resources` — intentional duck-typing seams.

## Key Files
| Component | File Path | Items |
|-----------|-----------|-------|
| Stat contributors registry | `game/simulation/entities/stat_contributors/registry.py` | 1 CRITICAL (`iter_for`) |
| Simulation systems | `game/simulation/systems/attack_processor.py`, `fighter_reboard.py` | 3 |
| Component stats calculator | `game/simulation/components/component_stats_calculator.py` | 1 (`evaluate_recursive`) |
| Core registry | `game/core/registry.py` | 1 (`get_validator`) |
| Planet write service | `game/strategy/services/planet_write_service.py` | 1 (`pop_construction_item` — also in PROJ-482 Phase 3; this is the Protocol-side narrowing in `core/protocols/strategy_mutators.py`) |
| AI controllable | `game/ai/interfaces/controllable.py` | 3 |
| AI protocols | `game/ai/protocols.py` | 2 |
| Core Protocols (strategy_entities) | `game/core/protocols/strategy_entities.py` | 12 |
| Core Protocols (ui) | `game/core/protocols/ui.py` | 3 |
| Core Protocols (strategy_domain) | `game/core/protocols/strategy_domain.py` | 2 |
| Core Protocols (strategy_mutators) | `game/core/protocols/strategy_mutators.py` | 1 |
| Simulation entity protocols | `game/simulation/interfaces/entity_protocols.py` | up to 7 (subset of the 16 — verifier flagged some duck-type subset as OOS) |
| Strict-mode config | `mypy.ini` / `pyproject.toml` | 1 per layer enabled |

## Related Documents
- [design.md](design.md) — Source audit, bundle counts, layer coverage
- [decisions.md](decisions.md) — Decision log including bundling rationale
- [findings/verification_report.md](findings/verification_report.md) — VERIFIED / REJECTED / UNCERTAIN / OUT_OF_SCOPE per item
- [findings/source_audit.md](findings/source_audit.md) — Pointer to originating type-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] mypy `--strict` enabled on research, engine, ai, core, services, assets and clean (or deltas justified)
- [ ] User verified
