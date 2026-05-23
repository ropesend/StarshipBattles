# PROJ-493 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/engine/superweapon_order_processor.py | Production | Phase 1 — add `validator` constructor parameter; route static call through injected validator (lines 62-79, 275-282) |
| game/strategy/validation/superweapon_validator.py | Production READ | Verify protocol interface (lines 14-33) |
| tests/unit/strategy/engine/test_superweapon_order_processor.py | Test | Phase 2 — migrate 16 patch sites (lines 131, 166, 201, 622, 669, 708, 749, 786, 854, 910, 1009, 1049, 1098, 1132, 1181, 1239) |
| docs/02_PATTERNS.md | Docs | Phase 1 — document the new seam if not covered by existing constructor-injection guidance |
