# PROJ-439: Content Contracts and Loader Validation

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-439` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-439 [phase]` before stopping
> - Update Current State with specific handoff context

**Execution Protocol:** 03c-phase-aware-execution

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Inventory content contracts and validation boundaries | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Schema assets and shared validation helper | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Tooling and load-pipeline enforcement | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Typed registrars and loader models | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Formula surface reduction and docs sync | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-05-17 20:40
**Active Phase:** Planning
**Last Action:** Created the project scaffold, loaded the project/content-system docs, incorporated the agreed roadmap from `AgentCoordination/Scratchpad/Discussion/20260518T030705Z_tech-debt-roadmap/plans/tech_debt_roadmap_r001.md`, and ran the canonical baseline suite: `python Tools/test_sharded/test_sharded.py` -> `21233/21233` passed.
**Next Action:** User review of the charter. On approval, begin Phase 1 inventory and validation-boundary mapping.
**Blockers:** None.
**Context for Next Agent:** This project is the first charter from the post-PROJ-438 tech-debt roadmap. It targets production content contracts, loader validation, typed registrars, and formula-surface narrowing. It does **not** reopen UI substrate, battle-session convergence, or ambient-default cleanup beyond documenting touchpoints. No fresh Codex subagent swarm was launched because current Codex instructions disallow unrequested delegation; `design.md` records that limitation explicitly.

## Overview
Establish schema-backed contracts and shared validation seams for production content so malformed components, modifiers, resources, designs, and races fail fast at the right boundary instead of surfacing later during gameplay. The project also reduces registry drift by moving high-churn content families toward typed registrar patterns and narrows the set of fields that rely on ad hoc formula strings.

## Goals
- Add production-facing content contracts for the highest-churn data domains: components, modifiers, resources, designs, and races.
- Validate those contracts in both tooling and runtime load paths without violating existing layer boundaries.
- Reduce hand-maintained registry drift in high-churn content families, starting with component abilities.
- Narrow the formula surface where fields can become typed calculators or bounded values instead of free-form expression strings.

## Scope
**In:**
- New production schema assets under `data/schemas/`.
- A shared validation helper in the Core layer so startup, strategy loaders, and tools can share one validation surface.
- Validation integration for `ResourceCatalog`, component/modifier loading, vehicle-class loading, design loading, and design-validation tooling.
- Typed registrar/model work for the highest-churn manual registry surfaces, especially abilities.
- Targeted formula-surface reduction and the matching docs updates.

**Out:**
- UI substrate redesign and screen-architecture work (the excluded clean-sheet item 1).
- Battle-session convergence and `BattleController` retirement (roadmap PROJ-440).
- Ambient-default removal beyond documenting relevant touchpoints (roadmap PROJ-441).
- Broad seam/orphan cleanup and any test-pyramid reduction (roadmap PROJ-442).
- Full runtime migration to Pydantic or a whole-sale replacement of `FormulaEvaluator`.
- Save-file migration or backward-compat shims for old content shapes.

## Dependencies
**No hard predecessor.** PROJ-439 was explicitly ordered first in the agreed roadmap because it improves future maintainability and makes later cleanup safer.

**Soft relationships:**
- PROJ-440 benefits from stronger content guarantees but does not block this project.
- PROJ-441 and PROJ-442 should build on the contracts landed here rather than duplicating validation logic.
- The runtime dependency decision for JSON Schema consumption is open and must be resolved in Phase 1 before code is added to the load path.

## Key Files
| Component | File Path |
|-----------|-----------|
| Unified resource definitions | `game/core/resources.py` |
| Registry container/provider seam | `game/core/registry.py` |
| Shared JSON loader helpers | `game/core/json_utils.py` |
| Formula evaluator | `game/core/formula_evaluator.py` |
| Bootstrap resource hydration | `game/app_bootstrap.py` |
| Component/modifier pure loaders | `game/simulation/components/component_loader.py` |
| Registry reload wrapper | `game/simulation/services/registry_loader.py` |
| Vehicle-class loaders | `game/simulation/entities/ship_loader.py` |
| Ability factory and registry | `game/simulation/components/abilities/__init__.py` |
| Ability base metadata | `game/simulation/components/abilities/base.py` |
| Existing modifier-schema precedent | `game/simulation/components/modifier_schema.py` |
| Strategy design load path | `game/strategy/systems/design_repository.py` |
| UI design load adapter | `game/ui/services/design_loader_adapter.py` |
| Design validation tool | `Tools/validate_designs/validate_designs.py` |
| Production content roots | `data/components.json`, `data/modifiers.json`, `data/resources.json`, `data/designs/`, `data/races/` |

## Related Documents
- [design.md](design.md) - architecture analysis, risks, and phase rationale
- [decisions.md](decisions.md) - design decisions and project-scoping choices
- [tech_debt_roadmap_r001.md](../../../AgentCoordination/Scratchpad/Discussion/20260518T030705Z_tech-debt-roadmap/plans/tech_debt_roadmap_r001.md) - agreed parent roadmap for PROJ-439..442
- [component_system.md](../../../docs/guides/component_system.md) - current component/ability contracts
- [resource_system.md](../../../docs/systems/resource_system.md) - current resource-catalog and production contracts
- [ability_reference.md](../../../docs/systems/ability_reference.md) - live ability keys and payload shapes

## Initial Analysis
- The canonical baseline suite is green on this checkout: `python Tools/test_sharded/test_sharded.py` collected `21233` tests and passed `21233/21233`.
- There is no production `data/schemas/` directory today. Schema assets exist only in `combat_lab/data/schemas/` and `Tools/captioning/schemas/`.
- `grep -r "jsonschema|schema_validate" game/` returns zero hits, so production content currently has no shared schema-validation layer.
- `ABILITY_REGISTRY` is still a hand-maintained dict in `game/simulation/components/abilities/__init__.py:130`, and `create_ability()` / `get_ability_default_scope()` depend on that manual map (`game/simulation/components/abilities/__init__.py:236-278`).
- `FormulaEvaluator` is a hand-rolled AST walker with a blocklist-based safety model (`game/core/formula_evaluator.py:35-203`), and component/ability docs still describe many live formula-bearing fields.
- Loader behavior is inconsistent by design today:
  - `ResourceCatalog.from_json()` logs and returns an empty catalog on load failure (`game/core/resources.py:75-101`).
  - `load_modifiers_data()` warns on schema failure but still attempts to load the modifier (`game/simulation/components/component_loader.py:186-236`).
  - `RegistryLoader` catches and logs load failures per file family rather than failing the full reload (`game/simulation/services/registry_loader.py:31-132`).
- There is already a useful local precedent in `validate_modifier_v2()` (`game/simulation/components/modifier_schema.py:193`) that this project should reuse rather than bypass.

## Swarm Findings Summary
This planning session did **not** launch a fresh Codex swarm. Current Codex instructions prohibit unrequested delegation, so the findings below combine:
- verified Claude/Codex discussion output from `AgentCoordination/Scratchpad/Discussion/20260518T030705Z_tech-debt-roadmap/`, and
- direct local code review in this session.

### Architecture
- Production content enters through several different seams with different failure semantics: `ResourceCatalog.from_json()` (`game/core/resources.py:75-101`), component/modifier/vehicle-class loaders (`game/simulation/components/component_loader.py:77-278`, `game/simulation/entities/ship_loader.py:50-117`), bootstrap hydration (`game/app_bootstrap.py:228-246`), registry reload (`game/simulation/services/registry_loader.py:31-132`), and design/UI load paths (`game/strategy/systems/design_repository.py:280`, `game/ui/services/design_loader_adapter.py:83`).
- The current architecture already prefers Core-layer shared utilities for cross-layer concerns. That makes a Core validation helper the right shape for this project and avoids a new Core -> Simulation dependency.

### Key Patterns to Reuse
- **Core shared utility surface**: `game/core/json_utils.py:119` already owns required JSON loading; validation should layer beside it rather than creating another ad hoc loader stack.
- **Existing local schema precedent**: `game/simulation/components/modifier_schema.py:193` proves the project already tolerates schema-style validation for content families.
- **Registry DI boundary**: `game/simulation/services/registry_loader.py:31-132` and `game/app_bootstrap.py:228-246` show the current intended injection flow. Validation must plug into that flow, not bypass it with new globals.

### Risks Identified
1. **Components are the hardest schema surface.** Ability payloads currently allow bool, scalar, dict, list, and formula-string forms under one key family. Phase 2 must avoid over-constraining legal live data before tests pin the accepted shapes.
2. **Failure semantics are inconsistent today.** Some loaders warn and continue; others should fail fast. Phase 1 must decide where strictness belongs before Phase 3 changes runtime behavior.
3. **Formula narrowing can break legitimate runtime behavior.** Runtime weapon formulas and load-time ship-class formulas are different categories; only bounded/static cases should move first.
4. **Dependency choice can spread quickly.** If JSON Schema consumption requires a runtime package, that decision affects `requirements.txt`, startup, tests, and tooling. It must be made once and documented.

### Opportunities Discovered
- The project can create one reusable content-validation surface for both startup and tools instead of letting every subsystem invent its own checks.
- A typed registrar for abilities can reduce one of the highest-visibility manual registry surfaces without forcing a full runtime object-model rewrite.
- Stronger load-time guarantees should make later cleanup projects smaller because malformed content will stop leaking into later logic.

## Phases

### Phase 1: Inventory content contracts and validation boundaries
Define the exact production content surfaces, current loader entry points, and failure-policy decisions before any schema files or runtime helpers are added. This phase is the decision gate for strict-vs-warning behavior and for any runtime dependency needed to consume schemas.

### Phase 2: Schema assets and shared validation helper
Introduce the schema assets and the shared Core-layer validation helper. Start with the highest-signal and lower-ambiguity domains first, then extend toward the harder component/ability shapes once the helper and tests are in place.

### Phase 3: Tooling and load-pipeline enforcement
Thread the validation helper through startup, registry reloads, and design-loading/tooling seams. The main deliverable is consistent, tested behavior at the correct boundary for resources, components, modifiers, vehicle classes, designs, and races.

### Phase 4: Typed registrars and loader models
Reduce string-key drift in the highest-churn registry surfaces and normalize the raw loaded payloads through typed intermediate models where that improves safety without creating a new runtime model layer.

### Phase 5: Formula surface reduction and docs sync
Remove or narrow bounded formula cases that do not need free-form expressions, then update docs and project metadata to reflect the landed contract.

## Verification
- [x] Baseline full-suite equivalent run recorded: `python Tools/test_sharded/test_sharded.py` -> `21233/21233` passed
- [ ] All phase checklists complete
- [ ] Focused phase tests pass at each boundary
- [ ] Sharded suite green at the closing project boundary
- [ ] Audit passed
- [ ] User verified
