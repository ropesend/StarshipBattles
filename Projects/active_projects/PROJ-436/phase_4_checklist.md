# Phase 4: `Planet.stockpile` + `max_stockpile` + `staging_yard` migration

**Status:** Not Started
**Depends on:** phase_3
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_4.planned_files

**Objective:** Delete `Planet.stockpile: Dict[str, float]`, `Planet.max_stockpile: Dict[str, float]`, `Planet.staging_yard: List[Dict[str, Any]]` dataclass fields. Replace with per-facility-component `Container` access. Planet's `add_to_stockpile` / `consume_from_stockpile` / `has_stockpile` / `get_stockpile` / `add_to_staging_yard` / `remove_from_staging_yard` / `get_staging_yard_mass` rewrite around `Container` ops. If Phase 0 D1 default holds, `PlanetaryFacility.consumable_levels` stays as facility-internal state; if Phase 4 evidence forces (a) fold-in, revert the D1 default in `decisions.md` and absorb the cost here.

---

## Tasks

To be authored at phase start. Expected sub-phase shape:
- 4a — substrate: `Container` view-projection over `Planet.stockpile`+`Planet.max_stockpile` keyed on resource_id.
- 4b — substrate: `Container` view-projection over `Planet.staging_yard`.
- 4c — migrate `add_to_stockpile` / `consume_from_stockpile` / `has_stockpile` / `get_stockpile` callers.
- 4d — migrate `add_to_staging_yard` / `remove_from_staging_yard` / `get_staging_yard_mass` callers.
- 4e — migrate planet serializer round-trip; update `ProductionEngine` planet reads (without yet deleting `context_type` branching — that's Phase 8).
- 4f — final cutover: delete the three legacy fields; AST guard.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/static_guards/test_no_legacy_storage_fields.py` extended to cover Planet fields, green
- [ ] Planet-detail UI smoke test green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
