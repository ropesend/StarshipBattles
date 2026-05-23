# Bundling Decisions — Legacy Audit 2026-05-20

> Identical across all 7 sibling projects from this audit run (PROJ-484 through PROJ-490). The user can read it once for the full picture.

## Source Audit
`Reviews/results/2026-05-20_210635_legacy-audit/`

## Default Proposal Presented to User

| # | PROJ | Title | Cluster | Verified | Phases |
|---|------|-------|---------|----------|--------|
| 1 | PROJ-484 | Dead re-export sweep | dead_reexports | 4 | Phase 1 (2 zero-caller), Phase 2 (2 single-test-caller) |
| 2 | PROJ-485 | Dead CarrierAIController methods | carrier_dead_methods | 3 | Phase 2 |
| 3 | PROJ-486 | Dead BattleController.load_state | battle_load_state | 1 | Phase 2 |
| 4 | PROJ-487 | Fuel wrappers → consumable API | planet_fuel_wrappers | 1 | Phase 2 |
| 5 | PROJ-488 | MASS_EARTH alias removal | mass_earth_alias | 1 | Phase 3 |
| 6 | PROJ-489 | ModifierService consolidation | modifier_service_canon | 1 | Phase 2 |
| 7 | PROJ-490 | Stale-comment cleanup sweep | stale_comments | 9 | Phase 3 |

**Totals presented:** VERIFIED 17 / REJECTED 3 / OUT_OF_SCOPE 12 (audit-self-retracted) / UNCERTAIN 0 / INFO 0

## User Adjustments

User accepted the default 7-project proposal as-is. No merges or splits.

## Per-UNCERTAIN-item Decisions (Phase D Step 3)

None — every verifier verdict was VERIFIED or REJECTED, no UNCERTAIN items required user adjudication.

## Per-INFO-item Decisions (Phase D Step 4)

None surfaced — all 3 INFO-severity findings in the audit were self-retracted by the audit's own shard reviewers as Phase 1 false positives (LEG-01-005 factory, LEG-01-006 closure, LEG-02-004 ModifierManager). They were classified as OUT_OF_SCOPE at Phase B and not presented for user opt-in.

## Final Bundle Definitions

7 sibling projects as listed in the default proposal. Each project's `verification_report.md` records the specific items assigned to it. Run-wide REJECTED items (A-04, LEG-A-3, LEG-F-2) and OUT_OF_SCOPE items (the 12 audit-self-retracted findings) are documented in `verification_report.md` of the most thematically relevant sibling, or in this file's "Run-wide REJECTED / OUT_OF_SCOPE" section below.

## Run-wide REJECTED (excluded from all projects)

| ID | File:Line | Reason |
|----|-----------|--------|
| A-04 | `game/app.py:459` | TODO is a feature gap ("Replace with empire.available_tech"), not legacy removal — belongs to feature-completion work, not legacy-audit scope (wrong-skill) |
| LEG-A-3 | `game/simulation/services/ship_materializer.py:193-205` | Audit itself recommended "No remediation needed, but worth noting for potential pattern drift" — verifier honored audit's own guidance |
| LEG-F-2 | `WorkshopDataLoader` vs `RegistryLoader.reload_registries_from_directory` | Verifier confirmed `reload_registries_from_directory` has 0 production callers (test-only infrastructure) while `WorkshopDataLoader.load_all()` is production-canonical with 1 production caller — they are not duplicates serving the same need; they are different architectural layers |

## Run-wide OUT_OF_SCOPE (already filtered by the audit's own shard reviewers or by documentation)

| ID | File:Line | Reason |
|----|-----------|--------|
| LEG-01-001 | `game/simulation/components/abilities/planetary/__init__.py:1-59` | Documented Pattern #36 re-export shim with active migration project (PROJ-382) |
| LEG-01-005 | `game/simulation/components/component_constants.py:45` | Phase 1 false positive — `Modifier.create_modifier` is a documented Factory pattern (#15), not a wrapper delegate. Self-retracted by shard reviewer. |
| LEG-01-006 | `game/ui/screens/builder/weapons_viewmodel.py:392` | Phase 1 false positive — `calc_damage_at_range` is a local closure inside `_compute_points_of_interest`, not a module-level wrapper. Self-retracted. |
| LEG-01-007 | `game/ui/screens/planet_abilities_window.py:178-231` | Documented Pattern #30 legacy slot cleanup — explicitly preserved exception path per `docs/02_PATTERNS.md:652` |
| LEG-01-009 | `game/core/registry.py:287-301` | `set_default_registry_manager` is part of documented PROJ-258 DI pattern, not a legacy shim |
| LEG-02-003 | `game/strategy/services/ability_metadata.py:490-492` | `get_ability_metadata` is a documented Pattern #5 Facade — `_BY_NAME` is private, the function is the public API contract. Self-retracted. |
| LEG-02-004 | `game/simulation/components/modifier_manager.py:30` vs `game/simulation/services/modifier_service.py:16` | Phase 1 name-pair drift false positive — `ModifierManager` is a component delegate, `ModifierService` is a service-layer rule engine. Distinct responsibilities. |
| LEG-02-008 | `game/strategy/config/economy_config.py:143-147` | `set_default_economy_config` is documented Pattern #12 variant — explicit in-code justification ("module-accessor form gives tests a clean swap API"). Self-retracted. |
| S-01 (Shard 03) | Multiple `*_window.py` files | Documented Pattern #30 — superseded but explicitly allowed for legacy slot cleanup |
| W-01 (Shard 03) | `game/simulation/entities/ship.py:568,581` | `Ship.to_dict()` / `Ship.from_dict()` are Pattern #5 Facade delegates to `ShipSerializer`, not legacy shims. Self-retracted. |
| N-01 (Shard 03) | `ModifierManager` vs `ModifierService` | Same as LEG-02-004 — distinct responsibilities, false positive. |
| A-06 (Shard 03) | `game/strategy/data/ship_instance.py:142-241` | `consumable_levels` / `cargo_contents` are protocol-contract properties (declared on `IShipInstance` protocol), used in production. Not legacy. |
| LEG-04-MINOR (post_battle_hook_builder.py:67) | "# legacy direct-construction tests" comment | Reviewer noted "No action needed" — accurate documentation, not a finding. |
| LEG-04-MINOR (dialogs.py:256) | "# Old value (strikethrough)" comment | Reviewer noted "No action needed" — UI rendering annotation, not legacy code. |
| LEG-04-MINOR (component.py:391-405) | Re-exports from extracted `component_loader.py` | Documented Pattern #36 with tracked migration. Not a finding. |
| LEG-04-MINOR (policy_manager.py:22-37) | "Add `set_default_policy_manager()` for parity" | Wrong-skill — asks to ADD code, not remove/consolidate. Belongs to a separate DI-consistency project, not legacy-audit. |

(15 OUT_OF_SCOPE items — three INFO + twelve documented patterns / wrong-skill.)
