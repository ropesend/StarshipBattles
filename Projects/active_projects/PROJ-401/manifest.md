# PROJ-401 File Manifest

## Files

| File | Type | Notes |
|------|------|-------|
| game/strategy/validation/transfer_validator.py | Production | Add early rejection in `_validate_load` for missing `species_id` on passenger load. |
| tests/unit/strategy/validation/test_transfer_validator.py | Test | Add regression asserting validator rejects missing `species_id`. (Path may differ — confirm.) |
| game/strategy/engine/order_handlers/transfer_branches.py | Production (read-only) | Executor side that already no-ops missing `species_id` — referenced as the contract validator must agree with. |
