# PROJ-482: Type cleanup — Strategy per-finding (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-482` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-482 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Critical Strategy missing returns | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Major Strategy narrowings | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Minor Strategy narrowings + closures | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Complete (all 3 phases + Codex audit closed)
**Last Action:** Codex mid-project-review audit (2026-05-23) returned 5 findings. 4 were clean bills / non-actionable (no scope creep, primary_star narrowing correct, simulation_adapter plan-correction valid, pop_construction_item annotation matches PROJ-483 protocol). 1 finding (over-specific narrowing of helper methods to concrete `PlanetWriteService`/`EmpireWriteService` instead of `IPlanetMutator` protocol) is real but architecturally out of scope — the clean fix (add `empire=` kwarg to `IPlanetMutator.add_facility`) lives in core/protocols/ which PROJ-482 explicitly defers to the Foundation track. Logged as DI-2026-05-23-001. See [findings/audit_verification.md](findings/audit_verification.md).
**Next Action:** Project ready for user verification / archival.
**Blockers:** None

## Overview
Type-safety cleanup for the `game/strategy/` layer driven by the 2026-05-20 type audit. After independent third-pass re-verification, ~28 strategy-layer findings survived and are bundled here. Includes the high-impact `GameSession` mutator-property cluster (10 missing-return annotations + 10 `# type: ignore` suppressions to fix together), several CRITICAL missing returns called cross-module, and the 8-helper `_get_*_mutator()` cluster across engine modules. mypy `--strict` adoption for `game/strategy/` (1,070 strict errors) is **deferred**.

## Goals
- Phase 1: Resolve 4 CRITICAL items — `GameSession` cluster (10 properties, one combined fix), `OrderMetadataView._registry`, `SuperweaponOrderProcessor._get_nav_service`, `StarSystem.primary_star`.
- Phase 2: Narrow `~13` MAJOR `-> Any` returns including the 8 `_get_*_mutator` cluster, `GameSession.handle_command → ValidationResult`, public handlers `_resolve_*`, and `_walk_strategic_abilities` generator.
- Phase 3: Narrow `~11` MINOR `-> Any` returns and missing returns across superweapon closures, write services, adapters, deployed_group decorator, and `_build_capture_context` (with a new `ReplayCaptureContext` type per user opt-in).

## Scope
**In:**
- All `-> Any` narrowings, missing returns, and removable `# type: ignore` sites in `game/strategy/`.
- The new `ReplayCaptureContext` type (one new type alias or small class) for `simulation_adapter._build_capture_context`.

**Out:**
- UI per-finding cleanup — see sibling [PROJ-481](../PROJ-481/plan.md).
- Foundation per-finding cleanup — see sibling [PROJ-483](../PROJ-483/plan.md).
- mypy `--strict` adoption for `game/strategy/` (1,070 errors) — deferred. See `decisions.md`.
- `strategic_ability_scanner.find_*` TypedDict refactor — user-deferred.
- `formula_evaluator._eval_node` narrowing — user-deferred.
- `battle_assembly.py:81` cast alternative — user-deferred.

## Key Files
| Component | File Path | Items |
|-----------|-----------|-------|
| GameSession mutator/registry properties | `game/strategy/engine/game_session.py` | 10 (one combined Phase 1 task) + 1 (handle_command) |
| Order metadata view | `game/strategy/engine/commands/order_metadata_view.py` | 1 (`_registry`) |
| Superweapon order processor | `game/strategy/engine/superweapon_order_processor.py` | 1 (`_get_nav_service`) + 1 (`_get_empire_mutator`) |
| StarSystem data | `game/strategy/data/star_system.py` | 1 (`primary_star`) |
| Mutator helper cluster (engine + order_handlers) | `harvesting_engine.py`, `order_handlers/base.py`, `environmental_hazard_engine.py`, `planet_modifier_effect_engine.py`, `production_spawner.py`, `atmosphere_engine.py` | 8 |
| Handlers / base | `game/strategy/engine/handlers/base.py` | 3 (`_resolve_*`, `_build_colonize_target`) |
| Game initializer | `game/strategy/engine/game_initializer.py` | 2 (generators) |
| App bootstrap | `game/app_bootstrap.py` | 1 (`_replay_combat_lab_fallback`) |
| Superweapon handlers (closures) | `superweapon_handlers/open_warp_point.py`, `close_warp_point.py`, `stellerate_star.py`, `create_dyson_sphere.py`, `implode_planet.py` | 11 closures |
| Services | `planet_write_service.py`, `replay_verification_coordinator.py`, `ability_sources/fleet.py` | 3 |
| Construction-queue handler | `handlers/construction_queue.py` | 1 |
| Adapters | `adapters/simulation_adapter.py` | 2 (`_lookup` + `_build_capture_context` with new type) |
| Deployed-group decorator | `data/deployed_group.py` | 2 (decorator factory + inner) |
| Design catalog | `systems/design_catalog.py` | 1 (`load_design_data`) |

## Related Documents
- [design.md](design.md) — Source audit, bundle counts, layer coverage
- [decisions.md](decisions.md) — Decision log including bundling rationale
- [findings/verification_report.md](findings/verification_report.md) — VERIFIED / REJECTED / UNCERTAIN / OUT_OF_SCOPE per item
- [findings/source_audit.md](findings/source_audit.md) — Pointer to originating type-audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] mypy clean on touched files
- [ ] User verified
