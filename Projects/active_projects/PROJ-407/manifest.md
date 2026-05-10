# PROJ-407 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| docs/* | Doc | D-01, D-02, D-03 — update outdated references. |
| docs/05_ERROR_HANDLING.md | Doc | D-03 — reconcile with EventBus session-scope architecture. |
| game/ui/screens/strategy_* | Production (comments only) | D-04 — remove stale `pixel_to_hex` import comments. |
| game/strategy/data/galaxy.py | Production (docstring only) | D-05 — fix post-PROJ-394 wording. |
| game/strategy/engine/superweapon_handlers/*.py | Production | D-06, D-07 — modern type syntax. |
| Other PROJ-380/391/396 new modules | Production | D-07 — modern type syntax sweep. |
| game/strategy/data/formation_spec.py | Production | D-08 — tighten `object` slot. |
| tests/...test_formation_spec*.py | Test | D-08 regression. |
| Projects/active_projects/PROJ-407/findings/loc_deferrals.md | Findings | D-09 — read-only audit log. |
