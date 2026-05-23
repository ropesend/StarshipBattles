# PROJ-482 — Codex Audit Verification Table

- **Audit date:** 2026-05-23
- **Auditor:** codex (mid-project-review, sandbox=workspace-write, allow_tests=false)
- **Consult artifact:** `AgentCoordination/Scratchpad/Consult/20260523T042752Z_audit-PROJ-482/response.md`
- **Orchestrator:** Batch 2 (claude)

## Findings table

| # | Finding (Codex) | Cite | Verified? | Scope | Disposition |
|---|---|---|---|---|---|
| 1 | No file creep relative to plan.md:30-38; diff stays on planned return-type surface. `simulation_adapter` correction is a plan correction, not a safety loss. | plan.md:30-38; simulation_adapter.py:427-506; replay_capture.py:35-56; ship_instance_serializer.py:26 | YES | n/a | REJECTED — clean bill |
| 2 | Helper methods narrowed to concrete `PlanetWriteService`/`EmpireWriteService` where most call sites only need protocol surface (over-specific / abstraction leak). Clean fix is protocol-side: `IPlanetMutator.add_facility` lacks the `empire=` kwarg that the concrete service implements and that `production_spawner.py:295` + `order_handlers/colonize.py:203` rely on. | production_spawner.py:104-108,292-295; harvesting_engine.py:198-214,329-339; atmosphere_engine.py:31-37,139; order_handlers/base.py:148-164; strategy_mutators.py:97-98; planet_write_service.py:60-78 | YES | OUT-OF-SCOPE — plan.md:40-43 explicitly leaves Core protocols to the sibling Foundation track (PROJ-483, now complete) | LOG via `/claude-di-log` for future protocol-alignment project. Do NOT remediate in PROJ-482. |
| 3 | `StarSystem.primary_star -> Star \| None` is correct; did not introduce new unsoundness. The implementer's note about "open_warp_point.py issues" was misattributed — those are pre-existing `_get_system_at_hex()` Optional gaps, NOT `primary_star`-related. | star_system.py:87-89; test_system_dto.py:105,152; create_dyson_sphere.py:39-54; open_warp_point.py:38-64; close_warp_point.py:63-112; stellerate_star.py:47-64 | YES | n/a | REJECTED — non-issue (and pre-existing data-flow gaps are not in PROJ-482's scope) |
| 4 | `simulation_adapter._build_capture_context -> ReplayCaptureContext` (using existing class) and `_lookup -> Optional[Dict[str, Any]]` are the right shapes, not safety regressions. | simulation_adapter.py:427-506; replay_capture.py:35-56; replay_spec.py:45; ship_instance_serializer.py:26 | YES | n/a | REJECTED — implementer's plan-correction is correct |
| 5 | `pop_construction_item -> dict[str, Any] \| None` annotation is looser than the implementation (which still raises `IndexError` on empty pop). Not a regression, just an annotation that matches the protocol shape. | planet_write_service.py:125-128; strategy_mutators.py:118-120 | YES | n/a (annotation matches PROJ-483 protocol; behavior unchanged) | REJECTED — non-actionable. Tightening would need to revisit PROJ-483's protocol decision. |

## Out-of-scope items / Discovered Issues
- **Finding 2 → DI log:** `IPlanetMutator.add_facility` / `remove_facility` should expose the `empire=` keyword that `PlanetWriteService` already implements, so the mutator-helper return annotations in strategy engines can collapse back to protocol form. Cross-cutting protocol work; touches `game/core/protocols/strategy_mutators.py` which PROJ-482 leaves to the Foundation track.

## Scope-creep escalation
None.

## Remediation plan
No Phase 4 needed for PROJ-482. The single in-scope-shaped finding (#2) is actually OUT-OF-SCOPE per the project's own plan; it gets logged for future work via `/claude-di-log`. All other findings are clean bills.

PROJ-482 status: **Complete**.
