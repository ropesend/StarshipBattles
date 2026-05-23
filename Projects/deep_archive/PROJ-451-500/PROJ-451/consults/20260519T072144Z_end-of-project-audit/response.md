---
protocol: consult/v1
from: codex
to: claude
mode: planning
created_at_utc: 2026-05-19T07:25:55.5141010Z
complete: true
exit_status: ok
---

## Findings

1. `DI-2026-05-18-006` data half is closed. `Fleet.has_cargo_resources` rounds affordability via `int(round(amount))` at `game/strategy/data/fleet.py:245-269`, and `Fleet.consume_cargo_resource` now rounds the consume-side gate the same way at `game/strategy/data/fleet.py:271-295`. The targeted symmetry ratchet covers rounded-to-zero, rounded-to-one, and under-budget whole-number cases at `tests/unit/strategy/data/test_fleet_consume_cargo_symmetry.py:29-82`, and the broader implementer ratchet covers `0.1`, `0.4`, `0.6`, multi-resource, and exact-balance shapes at `tests/unit/strategy/data/test_production_resource_source_ratchet.py:61-156`.

2. `DI-2026-05-18-006` engine UX gap is closed. `_apply_resource_consumption` records a before/after diff, collects resources with `actually_consumed == 0`, and routes them to `_log_zero_consume_shortage` at `game/strategy/engine/production_engine.py:654-724`. `_log_zero_consume_shortage` emits `EventType.RESOURCE_SHORTAGE` with `cause="rounded_to_zero"` at `game/strategy/engine/production_engine.py:726-772`. The stalled-queue plus shortage-event path is pinned through the queue loop at `tests/integration/test_production_engine_fractional_fleet_cost.py:160-280`.

3. `DI-2026-05-18-007` and `F-B-019` are closed. The `IProductionResourceSource` contract docstring carries MUST-language at `game/strategy/engine/production_engine.py:65-99`, and the engine enforces it immediately after `production_consume_resource(...)` with `assert consume_succeeded` at `game/strategy/engine/production_engine.py:685-701`. Concrete implementer behavior is reinforced by `tests/unit/strategy/data/test_production_resource_source_ratchet.py:73-156`, and the presence of the unified methods on both production owners is guarded at `tests/static_guards/test_no_legacy_storage_fields.py:310-360`.

4. The two fixture updates look realistic, not bug-hiding. The shortage-event colony fixture in `tests/unit/strategy/engine/test_production_refactor.py:357-382` mutates `colony.stockpile` and returns `bool`, which matches real `Planet.consume_from_stockpile` / `get_stockpile` behavior at `game/strategy/data/planet.py:267-298`; that is exactly what the engine's before/after truth-up expects at `game/strategy/engine/production_engine.py:685-707`. The paused-queue helper in `tests/unit/strategy/production_engine/test_paused_queue.py:76-102` mirrors the same stockpile mutation + bool-return contract, so it also composes correctly with the Phase-12 diff math.

5. I did not find other concrete `IProductionResourceSource` implementers on HEAD. Search for `production_has_resources|production_get_resource|production_consume_resource` in `game/` only returned the protocol/engine plus `Planet` at `game/strategy/data/planet.py:291-298` and `Fleet` at `game/strategy/data/fleet.py:308-320`. I also did not find active pre-PROJ-436 routing residue inside `ProductionEngine`: the remaining `context_type` / "empire pool" mentions are retirement notes at `game/strategy/engine/production_engine.py:16-21`, `:49-54`, `:577-580`, and `:663-666`, while the only live `resource_pool` use is the shape precondition in `_validate_tick_inputs` at `game/strategy/engine/production_engine.py:252-259`.

6. The exact `actually_consumed == 0` check is appropriate on current HEAD. The zero-consume branch is keyed by exact equality at `game/strategy/engine/production_engine.py:703-709`, so a tiny non-zero diff would not be misclassified as zero. For current sources, Fleet's integer cargo produces an exact zero/non-zero diff through `game/strategy/data/fleet.py:271-320`, and Planet subtracts the exact requested amount from float stockpile at `game/strategy/data/planet.py:267-298`. I would not add a blanket epsilon here; that would create more risk of misclassifying legitimate tiny planet charges than it would remove.

## Risks

- `tests/unit/strategy/production_engine/test_paused_queue.py:250-255` still wires `fleet.production_consume_resource` to `cargo.__setitem__(...)`, which returns `None`. It is currently unreachable in the audited path because the same test sets `construction_queue_paused = True` at `tests/unit/strategy/production_engine/test_paused_queue.py:242`, and the engine skips paused fleet queues before any consume call at `game/strategy/engine/production_engine.py:319-323`. If that fixture is ever reused for an unpaused fleet path, the Phase-3 assertion will trip immediately. I consider this nearby test residue, not a project-closing defect on current HEAD.

- The Phase-4 ratchet covers the only two production owners currently in the tree. If a future queue owner is added, it needs both the unified `production_*` methods and an implementer ratchet before relying on the engine assertion alone.

## Open questions

None.
