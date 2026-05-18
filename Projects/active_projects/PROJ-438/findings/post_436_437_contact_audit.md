# Post-436/437 Contact Audit

Created during PROJ-438 chartering from:

- direct Codex code review;
- Codex subagent audit on remaining `#1` state-model residue;
- Codex subagent audit on remaining `#3` intent-pipeline residue;
- Codex subagent audit on tests/docs/protocol/public seam contact points.

## Residual `#1` surfaces

- Duplicated graph-repair logic between `SessionPersistenceAdapter.rehydrate_state()` and `TurnStateSnapshot.restore()`.
- `GameSession` still mixes runtime/persistence/UI-adjacent concerns after PROJ-423.
- `Planet`, `Fleet`, `Empire`, and especially `ShipInstance` remain broad mutable roots even after storage leaves.
- The façade read side still compensates via caches/DTO rebuilds rather than a first-class query model.

## Residual `#3` surfaces

- `IssuePlanetOrderCommand(order_type: str, target: dict)` remains the stringly planet strategic-intent path.
- `PlanetActionEngine` + `ComponentActivationEngine` still form a separate activation lifecycle.
- `ActionExecutionEngine` still has the planet-FMS/private-dispatch graft (`_handler_registry` reach-in + `TypeError` fallback).
- `Order.to_dict()` / `OrderSerializer` still sit partly outside the live metadata surface.

## Support-surface concerns

- `tests/unit/strategy/data/` visibility under the canonical full suite must be explicitly decided in Phase 0.
- High-signal guards already exist and should be reused, not recreated:
  - `tests/unit/strategy/engine/session/test_bootstrap.py`
  - `tests/unit/strategy/engine/test_game_session_shape.py`
  - `tests/unit/strategy/ship_instance/`
  - `tests/unit/strategy/engine/commands/test_order_metadata_view.py`
  - `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`
  - `tests/unit/strategy/services/test_ability_metadata_registry.py`
- Docs likely to drift with this work:
  - `docs/systems/strategy_layer.md`
  - `docs/systems/orders_system.md`
  - `docs/04_SERVICES.md`
  - `docs/systems/ability_reference.md`

## Explicit exclusions

- Storage/container/transfer-UI work belongs to PROJ-436/437.
- Temporal scheduler / 100-tick rethink stays out (#2).
- Battle boundary is already retired by PROJ-426.
- `Empire.is_eliminated()` semantics are product-review, not architecture cleanup.
