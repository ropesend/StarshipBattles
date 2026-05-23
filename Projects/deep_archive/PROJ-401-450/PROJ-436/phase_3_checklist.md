# Phase 3: `ShipInstance.cargo_contents` + `consumable_levels` migration

**Status:** Not Started
**Depends on:** phase_2
**Review Mode:** standard
**Files (planned):** see `phase_state.json` phase_3.planned_files

**Objective:** Delete `ShipInstance.cargo_contents: Dict[str, int]` and `ShipInstance.consumable_levels: Dict[str, float]` dataclass fields. Both become projections over per-operational-component `Container` accessors during sweep, then deleted at final cutover. Migrate `ShipCargoManager`, `ShipConsumableManager`, `ShipInstanceBridge`, `ShipDisplayFormatter`, and `ship_instance_serializer` to read/write through `Container`. Per CLAUDE.md "no save-file migration" — final cutover commit drops the legacy serializer keys and old saves stop loading.

---

## Tasks

To be authored at phase start. Expected PROJ-431 sub-phase shape:
- 3a — substrate: `Container` view-projection over `cargo_contents` + `consumable_levels` on `ShipInstance`.
- 3b — migrate `ShipCargoManager` reads/writes.
- 3c — migrate `ShipConsumableManager` reads/writes.
- 3d — migrate `ShipInstanceBridge` + `ShipDisplayFormatter`.
- 3e — migrate `ship_instance_serializer.py` round-trip.
- 3f — final cutover: delete `cargo_contents` + `consumable_levels` dataclass fields; AST guard test `test_no_legacy_storage_fields.py` pins absence.

---

## Phase Completion Checklist
- [ ] All sub-phases complete
- [ ] `tests/static_guards/test_no_legacy_storage_fields.py` green
- [ ] Save/load round-trip integration test green
- [ ] Full sharded suite green
- [ ] Update status to Complete; update plan.md + phase_state.json
