# Independent Re-Verification Report

**Source audit:** `Reviews/results/2026-05-05_185819_audit_shrink/`
**Verification run:** 2026-05-05
**Method:** Three parallel `Explore` subagents, one per category batch (dead code; strategy duplications; UI duplications). Each agent re-checked the audit's claims with a fresh reference search, dynamic-dispatch search, recency check, and confirmed proposed extraction targets did not already exist.

## Summary

| Bucket | Count | Notes |
|--------|-------|-------|
| Audit verified-safe candidates input to verification | 11 | 1 dead method + 9 Section-4 CRITICAL/MAJOR duplications + 1 deep-review MAJOR duplication |
| **VERIFIED — entered project plan** | **10** | 1 dead method + 9 duplications |
| **REJECTED** | **0** | None |
| **UNCERTAIN — deferred / excluded from plan** | **1** | DUP-X-08 |
| **VERIFIED but excluded from plan** | **1** | DEEP-01-004 (audit-rated low priority) |

> **Note on zero rejections:** Protocol §F flags this as worth questioning.
> Prior audit-shrink runs have produced false positives (e.g., the 2026-05-02
> run flagged `_eval_least_armor_rule` as dead when it was reachable via
> `data/targeting_policies.json`). The 2026-05-05 audit was unusually thin —
> vulture flagged only 7 items, all classified as false positives by the
> audit's own internal verifier; only 1 dead method actually entered
> verification. With so few candidates, zero rejections is plausible.

## Verified

| ID | File | Symbol / Pattern | Recommendation |
|----|------|------------------|----------------|
| DEEP-01-001 | `game/strategy/engine/planet_action_engine.py:385-387` | `_find_shield_component_id` | Delete; superseded by `_find_ability_component_id(facility, 'PlanetaryShield')` |
| DUP-X-01 | `game/strategy/engine/planet_command_handlers.py:47,110,128,149,170,191,212` | 7× owner-id check | Add `_resolve_player_planet` to `BaseCommandHandler` mirroring `_resolve_player_fleet` |
| DUP-X-02 | `planet_action_engine.py`, `water_engine.py`, `quality_engine.py`, `atmosphere_engine.py`, `planet_energy_engine.py`, `harvesting_engine.py`, `build_queue_source.py`, `empire_economy_calculator.py`, `strategy_detail_formatter.py` | "Iterate→extract→read field" pattern | Add `get_ability_field_from_facility` to `component_inspector.py` |
| DUP-X-05 | `game/strategy/services/race_description_llm_controller.py:198-219, 266-307` | Bio/socio mirror methods | Replace mirrored attribute pairs with `_fields: dict[str, FieldState]`; collapse to field-parameterized methods |
| DUP-X-06 | `game/strategy/engine/planet_action_engine.py:296-310, 312-324, 327-339, 376-380` | 4 ability-extraction variants | Subsumed by DUP-X-02's helper; migrate same time |
| DUP-X-07 (+ Cluster 11) | `game/strategy/engine/superweapon_command_handlers.py:222-353` | 4 handlers don't use existing `_emit_validated_order` | Route all 4 handlers through the existing helper |
| Cluster 5 | `game/strategy/engine/planet_command_handlers.py:142-199` | 3 near-clone `SetXTargetCommandHandler` | Merge into parameterized `SetPlanetEnvironmentalTargetCommandHandler` |
| Cluster 29+30 | `game/strategy/engine/harvesting_engine.py:38, 67, 274, 301` | Harvester/storage info+registry-lookup pairs | Generic `_get_ability_info(comp, ability_name, registries)` |
| DUP-X-03 | `game/ui/screens/workshop_event_router.py:441, 464, 493, 505, 517` | 5 dropdown handlers | Config-driven dispatcher (note: role variant uses registry-loop resolver, not options list — dispatcher must parameterize resolution) |
| DUP-X-04 | `game/ui/screens/planet_list_window.py:541-573`, `game/ui/screens/star_list_window.py:389-421` | Identical update() + filter helpers | Extend existing `DataListWindowMixin` (or add sibling) with shared template |
| Cluster 6 | `game/ui/screens/builder/structure_list_items.py:195, 472` | `_rebuild_modifier_icons` duplicated identically | Extract to shared static helper or mixin (audit miscalled second class — it's `LayerComponentItem`, not `GroupComponentItem`) |

## Rejected

*None.* No item produced contrary evidence (no missed reference, no dynamic-dispatch reach, no already-existing extraction target, no recent divergence between duplicate sites). Per protocol §F this is flagged as worth questioning if the verifier prompts were too lenient — see Summary note above for the rationale that this is plausible for this small audit.

## Uncertain

| ID | File | Question | Recommended next step |
|----|------|----------|------------------------|
| DUP-X-08 | `game/services/llm/factory.py:48-87` and `game/ui/services/image/factory.py:43-79` | The audit proposes extracting `BaseProviderFactory` to `game/services/provider_factory.py` to be imported by both factories. This creates a shared service base parameterized over two unrelated domains (LLM config vs image generation) for ~30 LOC savings. Is the architectural cost justified? | Architecture review before scoping into a future project. Excluded from PROJ-375. |

## Verified but excluded (low priority)

| ID | File | Reason for exclusion |
|----|------|----------------------|
| DEEP-01-004 | `planet_action_engine.py:65-74`, `action_execution_engine.py:70-79`, `organics_consumption_engine.py:64-73`, `order_processor.py:734-743` | The audit's own recommendation rates this "Low priority — structural duplication, not logic-level." Each engine validates a different field; a `validate_empire_context(empires, validate_fn, context_name)` helper would mostly relocate the boilerplate rather than eliminate it. The verifier (and the audit) agree it is not worth the churn. |

## Audit's Own Excluded Items (out of scope, not re-verified)

Per protocol these were not re-verified — recorded here for traceability only:

- 7 vulture-flagged items the audit identified as false positives (3 `__exit__` protocol params + 4 `TYPE_CHECKING` imports). All are standard Python patterns vulture cannot statically resolve.
- `_handle_right_click` NO-OP stub at `workshop_event_router.py:541-544` — tagged PRODUCT_DECISION (called from event loop but always returns False). User decision required: delete or keep as placeholder for future right-click behavior.
- 16 MINOR + 10 INFO duplication clusters from `findings/duplication_cross_shard.md`.
- 20 complexity hotspots (CC≥25) from Section 5. Predominantly UI event handlers; not shrinkage candidates.
- LOC-ceiling violations (DEEP-01-007 `order_processor.py` 910 LOC, DEEP-01-008 `turn_engine.py` 802 LOC). Structural refactors, not consolidation.

## Per-batch agent reports

Aggregated working buffer is in `.agent_reports/2026-05-05_audit_shrink/`:

- `verification_dead_code.md` — Pass 1, Batch 1 (DEEP-01-001).
- `verification_strategy_dups.md` — Pass 1, Batch 2 (DUP-X-01, DUP-X-02 sample, DUP-X-05, DUP-X-06, DUP-X-07, Cluster 5, Cluster 11, Cluster 29+30, DEEP-01-004).
- `verification_ui_dups.md` — Pass 1, Batch 3 (DUP-X-03, DUP-X-04, DUP-X-08, Cluster 6).
- `verification_strategy_pass2.md` — Pass 2 (DUP-X-02 unsampled sites, DUP-X-05 external readers, DUP-X-07 signature compatibility).
- `verification_ui_pass2.md` — Pass 2 (DUP-X-03 dispatcher feasibility, DUP-X-04 mixin extension, Cluster 6 location, Cluster 5+DUP-X-01 interaction).

## Second-pass adjustments to project plan

The second skeptical pass kept all 10 verified items in scope but tightened
two task descriptions:

- **Task 2.1 (DUP-X-02 + DUP-X-06):** Dropped `build_queue_source.py:142`
  from the migration list — it's a boolean "any-component-has-X" check, not
  field-extraction (fits a separate `facility_has_ability` helper, follow-up).
  Added migration-nuance notes for `harvesting_engine.py:218,258,357` (uses
  wrapper helpers — sequence with Task 2.6) and `harvesting_engine.py:258`
  (size-multiplier shape decision needed). Two sites
  (`empire_economy_calculator.py:229`, `strategy_detail_formatter.py:314`) are
  marked re-confirm-at-impl since neither pass directly read them.
- **Task 2.5 (DUP-X-05):** Mandates preserving the 6 public `@property`
  accessors on `RaceDescriptionLLMController` (`bio_status`, `socio_status`,
  `bio_error`, `socio_error`, `bio_elapsed_seconds`, `socio_elapsed_seconds`).
  External readers in `race_description_panel.py` and `llm_dialog_service.py`
  go through these properties — internal storage refactor is fine, public
  surface must stay.
- **Task 2.4 (DUP-X-07):** No change — all 4 superweapon handlers cleanly
  swap to `_emit_validated_order`.
- **Task 3.1 (DUP-X-03):** Already noted the role-resolver concern in pass 1;
  pass 2 confirmed and added that the confirmation-dialog handlers
  (class/vehicle_type) need their own dispatcher variant rather than being
  forced through the same pipeline as the simple resolvers.
- **Other items:** VERIFIED-CLEAN with no scope change.
