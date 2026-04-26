# PROJ-293 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/data/habitability_factors.py | Production | Phase 1: Add `display_unit: str = ""` + `display_precision: int = 2` fields to `HabitabilityFactor` dataclass. Populate on 7 scalar factors and on `_build_gas_factors`. |
| game/ui/widgets/preference_row.py | Production | Phase 2: Replace `format_value` if-tree with data-driven one-liner. Phase 3: Bump `_SETPOINT_LABEL_WIDTH` and `_TOLERANCE_LABEL_WIDTH` from 60 → 90. |
| tests/unit/strategy/data/test_habitability_factors.py | Test | Phase 1: New `TestDisplayFields` class (4 tests). |
| tests/unit/ui/widgets/test_preference_row.py | Test | Phase 2: 3 new tests in `TestDisplayScaling` (tectonic, radiation, fake-factor). |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\PROJ-283.md | Memory (out-of-tree) | Phase 3: Append note about the display contract extension. |
