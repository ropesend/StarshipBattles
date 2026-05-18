# PROJ-439 File Manifest

> Generated during charter creation from the agreed roadmap and direct code review.
> Update this file whenever implementation discovers additional touched files.

## Files

### Production - added (Phase 2)

| File | Type | Notes |
|------|------|-------|
| `game/core/content_validation.py` | Production (new) | Shared Core-layer schema/validation helper used by startup, tools, and on-demand loaders. |
| `data/schemas/resources.schema.json` | Data (new) | Resource contract. |
| `data/schemas/modifiers.schema.json` | Data (new) | Modifier contract. |
| `data/schemas/components.schema.json` | Data (new) | Component and ability payload contract. |
| `data/schemas/design.schema.json` | Data (new) | Design file contract. |
| `data/schemas/race.schema.json` | Data (new) | Race file contract. |
| `game/simulation/components/abilities/registry.py` | Production (new, Phase 4) | Typed registrar surface replacing the hand-maintained map pattern. |
| `game/core/content_models.py` | Production (new, Phase 4) | Typed intermediate content models for high-churn loader inputs. |

### Production - modified

| File | Type | Notes |
|------|------|-------|
| `game/core/json_utils.py` | Production | Shared JSON load flow likely grows a validation hook or helper integration. |
| `game/core/resources.py` | Production | ResourceCatalog validation, typed normalization, and contract enforcement. |
| `game/core/registry.py` | Production | Registry/container interaction with validated resource/catalog content. |
| `game/core/formula_evaluator.py` | Production | Formula-surface narrowing in the final phase. |
| `game/app_bootstrap.py` | Production | Startup resource hydration should consume validated content. |
| `game/simulation/components/component_loader.py` | Production | Components/modifiers validation and normalization before object instantiation. |
| `game/simulation/services/registry_loader.py` | Production | Reload behavior must align with the chosen validation semantics. |
| `game/simulation/entities/ship_loader.py` | Production | Vehicle-class validation and normalization. |
| `game/simulation/components/abilities/__init__.py` | Production | `ABILITY_REGISTRY`, `create_ability`, and `get_ability_default_scope` migrate to registrar-backed behavior. |
| `game/simulation/components/abilities/base.py` | Production | Registrar/default-scope metadata may move or tighten here. |
| `game/simulation/components/modifier_schema.py` | Production | Existing local schema precedent may be reused or folded into the shared helper. |
| `game/strategy/systems/design_repository.py` | Production | On-demand design loads should validate before entering strategy/UI consumers. |
| `game/ui/services/design_loader_adapter.py` | Production | UI-facing design loads should surface validation failures cleanly. |
| `Tools/validate_designs/validate_designs.py` | Tooling | Design validation tool should consume the shared schema/helper layer. |
| `requirements.txt` | Support | Runtime schema-validation dependency, if Phase 1 chooses one. |
| `requirements-dev.txt` | Support | Dev/test dependency mirror if needed by the chosen validation engine. |
| `data/components.json` | Data | Formula-surface narrowing may require field normalization in the shipped content. |
| `data/modifiers.json` | Data | May need normalization to satisfy the shared contract if the existing local schema is broader/narrower than production reality. |
| `data/resources.json` | Data | Must validate cleanly under the new schema. |

### Production - referenced content roots

| File | Type | Notes |
|------|------|-------|
| `data/designs/` | Data directory | Production design files validated by tooling and on-demand load paths. |
| `data/races/` | Data directory | Production race files validated by tooling and/or load helpers. |

### Tests - added

| File | Type | Notes |
|------|------|-------|
| `tests/unit/core/test_content_validation.py` | Test (new) | Shared helper behavior and boundary modes. |
| `tests/unit/core/test_content_schemas.py` | Test (new) | Schema validity/invalidity coverage for first-pass production contracts. |
| `tests/integration/content/test_loader_validation_boundaries.py` | Test (new) | Characterization of startup/reload/on-demand validation behavior. |
| `tests/unit/simulation/components/abilities/test_registry_contract.py` | Test (new) | Registrar contract, duplicate-key protection, default-scope behavior. |
| `tests/unit/core/test_content_models.py` | Test (new) | Typed intermediate content-model normalization and error surfacing. |

### Tests - modified

| File | Type | Notes |
|------|------|-------|
| `tests/unit/core/resources_registry/test_loading.py` | Test | Resource contract and loader behavior. |
| `tests/unit/core/test_pure_loaders.py` | Test | Shared loader assumptions and catalog behavior. |
| `tests/unit/test_app_bootstrap_invariants.py` | Test | Startup invariants after validated resource/bootstrap wiring. |
| `tests/unit/simulation/components/test_component_loader.py` | Test | Component/modifier loader validation behavior. |
| `tests/unit/quickstart/test_quickstart_designs.py` | Test | Design contract expectations. |
| `tests/unit/strategy/design_repository/test_load_design_data.py` | Test | On-demand design loading with validation. |
| `tests/unit/ui/services/test_design_loader_adapter.py` | Test | UI adapter response to validated/invalid design files. |
| `tests/unit/simulation/components/test_component_stats_calculator.py` | Test | Formula-surface reduction safety. |
| `tests/unit/validation/test_component_definitions.py` | Test | Shipped component data still valid under the new contracts. |
| `tests/unit/entities/test_abilities.py` | Test | Ability payload compatibility after schema and registrar work. |
| `tests/unit/core/test_formula_evaluator.py` | Test | Evaluator behavior after formula-surface narrowing. |

### Docs - modified

| File | Type | Notes |
|------|------|-------|
| `docs/03_CONVENTIONS.md` | Doc | Content-authoring and validation policy. |
| `docs/guides/component_system.md` | Doc | Component/ability contract updates. |
| `docs/systems/resource_system.md` | Doc | Resource-catalog contract updates. |
| `docs/systems/ability_reference.md` | Doc | Ability registry/contract updates. |
