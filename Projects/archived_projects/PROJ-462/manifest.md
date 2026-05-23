# PROJ-462 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| game/core/math.py | Production | Fix Vector2.__init__ implicit Optional (Phase 1.1) |
| game/core/validation_helpers.py | Production | Narrow validate_enum Any return (Phase 1.2) |
| game/engine/collision.py | Production | Add beam_ab None-guard (Phase 1.3) |
| game/core/formula_evaluator.py | Production | Narrow _eval_node Any return (Phase 2.1) |
| game/core/registry.py | Production | Narrow get_validator returns (Phase 2.2) |
| game/core/state_machine.py | Production | Narrow state/pop_and_return (Phase 2.3) |
| game/core/protocols/strategy_entities.py | Production | Tighten entity protocol Any returns, carve-out (Phase 2.4) |
| game/core/protocols/strategy_mutators.py | Production | Tighten mutator protocol Any params (Phase 2.5) |
| game/core/json_utils.py | Production | Fix register_serializable implicit Optional (Phase 2.6) |
| game/research/ (mypy config) | Production | Adopt --strict (Phase 3.1) |
| game/services/ (mypy config) | Production | Adopt --strict; install stubs (Phase 3.2) |
| game/assets/asset_manager.py | Production | Annotate caches; adopt --strict assets (Phase 3.3) |
| game/engine/ (mypy config) | Production | Adopt --strict (Phase 3.4) |
| game/core/ (mypy config) | Production | Adopt --strict (Phase 3.5) |
