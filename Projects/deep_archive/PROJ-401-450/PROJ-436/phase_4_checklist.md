# Phase 4: `Planet.stockpile` + `max_stockpile` + `staging_yard` migration

**Status:** Complete (pending Codex consult)
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_4.planned_files

**Objective:** Delete `Planet.stockpile: Dict[str, float]`, `Planet.max_stockpile: Dict[str, float]`, `Planet.staging_yard: List[Dict[str, Any]]` dataclass fields. The names survive as backward-compatible `@property` accessors over renamed private fields (`_stockpile`, `_max_stockpile`, `_staging_yard`). Production writers continue to route through `IPlanetMutator` / Planet's own stockpile + staging helpers (`add_to_stockpile`, `consume_from_stockpile`, `add_to_staging_yard`, `remove_from_staging_yard`). Per Phase 0 D1 default, `PlanetaryFacility.consumable_levels` stays as facility-internal state — no audit-discovered transfer flow required (a) fold-in.

---

## Sub-Phase Plan (executed)

The Phase 3 PROJ-431-template sub-phase plan (4a-4e caller migration + 4f cutover) was investigated and collapsed: an audit of every direct field access showed that production writers were already routed through `IPlanetMutator` (`set_stockpile_amount`, `set_max_stockpile`, `add_staging_item`, `pop_staging_item`) or through Planet's own helpers — with three remaining outliers (`issuer_adapter.PlanetStagingYardIssuerAdapter.pop_carried` replacing the full list, `transfer_branches._dispatch_carried_vehicle_load` restore-path append, and `Empire.resource_pool.setter` reseeding the first colony). All three are write paths that target the underlying dict / list, NOT path replacements requiring a manager-API redirect — they continue to work unchanged against the `@property` setter / mutable-dict view. Reads use `getattr(planet, 'stockpile', ...)` / `.get(...)` patterns that route through the property transparently.

Result: a single cutover commit, mirroring Phase 3f's substrate-flip-via-property approach exactly.

- **4f** — final cutover (landed): rename dataclass fields to `_stockpile` / `_max_stockpile` / `_staging_yard`; expose public names as `@property` accessors with setters that translate full-list / full-dict replacement. Module-level legacy-kwarg constructor wrapper translates `stockpile=` / `max_stockpile=` / `staging_yard=` kwargs into the private-field names for the planet serializer + ~15 test fixtures. Internal methods on Planet (`add_to_stockpile` / `consume_from_stockpile` / `has_stockpile` / `get_stockpile` / `get_staging_mass` / `add_to_staging_yard` / `remove_from_staging_yard`) updated to read / write the private names directly (one less property indirection on the hot path; no observable behavior change). AST guard at `tests/static_guards/test_no_legacy_storage_fields.py` extended with 3 new tests pinning absence of the dataclass field names (RED-then-GREEN).

---

## Phase Completion Checklist
- [x] All sub-phases complete
- [x] `tests/static_guards/test_no_legacy_storage_fields.py` extended to cover Planet fields, green
- [x] Planet-detail UI tests + planet-stockpile / staging-yard / harvesting / consumption / write-service tests green
- [x] Full sharded suite green (21187/21187, +3 vs Phase 3 baseline 21184)
- [x] Update status to Complete; update plan.md + phase_state.json
- [x] End-of-phase Codex consult pre-final-check complete — zero verified findings require remediation (see decisions.md)
