# Review Scope: PROJ-370 Data Layer Boundary Protocols — mutator routing, AST guards, GameSession wiring

**Type:** code (delegated by Claude Code)
**Request ID:** req_20260506_090314_5da777
**Scope:** Six commits on `feat/03c-phase-aware-execution` spanning:
- `game/core/protocols/strategy_mutators.py` (NEW, 211 LOC)
- `game/strategy/services/fleet_write_service.py` (NEW, 136 LOC)
- `game/strategy/services/planet_write_service.py` (NEW, 147 LOC)
- `game/strategy/services/empire_write_service.py` (NEW, 136 LOC)
- `game/strategy/services/ship_instance_write_service.py` (NEW, 118 LOC)
- `game/strategy/engine/game_session.py` — wiring site
- `game/strategy/engine/turn_engine_config.py` — `create_default()` mutator wiring
- `game/strategy/engine/handlers/base.py` — `add_move_order_if_needed` fleet.path routing
- `game/strategy/engine/superweapon_order_processor.py` — empire_mutator kwarg
- `game/strategy/engine/order_handlers/transfer_branches.py` — _get_ship_mutator routing
- `game/strategy/engine/order_handlers/base.py` — _get_planet_mutator/_get_ship_mutator helpers
- `game/strategy/combat/post_battle_hook.py` — mutator routing for all post-battle writes
- `game/strategy/engine/environmental_hazard_engine.py` — ship_mutator routing
- `tests/unit/strategy/data/test_mutator_boundary_ast_guard.py` (NEW)
- `tests/unit/strategy/data/_mutator_ast_walker.py` (NEW)

**Instructions:** 7 focus areas: AST guard correctness, write-site routing soundness, GameSession wiring, Empire prune_empty_fleets lift, ShipInstance manager forwarding, TurnEngineConfig field growth, cross-cutting concerns.

**Context:** Wave B project 4 of 5. PROJ-368/369/371 closed cleanly. PROJ-370 is the largest production refactor in the chain.
