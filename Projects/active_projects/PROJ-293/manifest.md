# PROJ-293 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes | Status |
|------|------|-------|--------|
| game/strategy/data/habitability_factors.py | Production | Phase 1: Added `display_unit: str = ""` + `display_precision: int = 2` fields to `HabitabilityFactor` dataclass (with docstring update). Populated on 7 scalar factors and on `_build_gas_factors`. | Complete |
| game/ui/widgets/preference_row.py | Production | Phase 2: Replaced `format_value` if-tree with data-driven 7-line implementation. Phase 3: Bumped `_SETPOINT_LABEL_WIDTH` and `_TOLERANCE_LABEL_WIDTH` from 60 → 90 (with rationale comment). | Complete |
| tests/unit/strategy/data/test_habitability_factors.py | Test | Phase 1: Added `TestDisplayFields` class (4 tests). Extended `test_has_required_fields` to require the new fields. | Complete |
| tests/unit/ui/widgets/test_preference_row.py | Test | Phase 2: Added 3 new tests in `TestDisplayScaling` (tectonic, radiation, fake-factor). | Complete |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\proj_293_display_contract.md | Memory (out-of-tree, NEW) | Phase 3: Topic file holding the per-factor display contract table + format_value before/after + rationale. | Complete |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md | Memory (out-of-tree) | Phase 3: Added one-line index entry pointing to the new topic file (kept short to respect MEMORY.md size budget). | Complete |
