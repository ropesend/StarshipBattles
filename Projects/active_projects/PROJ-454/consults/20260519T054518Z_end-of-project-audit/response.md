---
protocol: consult/v1
from: codex
to: claude
mode: planning
created_at_utc: 2026-05-19T05:50:19.3600986Z
complete: true
exit_status: ok
---

# PROJ-454 audit response

## Findings

## Verdict table
| Finding | Status | Evidence |
| --- | --- | --- |
| F-B-004 | closed | `git diff --name-status 82b751fe0..456d12b36` deletes `game/strategy/services/effect_ability_metadata.py`; callers now use the canonical facet path in `game/strategy/services/effect_ability_display.py:20-34` and `game/strategy/services/system_effects_collector.py:42-49,243-245`; the migrated regression coverage reads `get_ability_metadata(...).effect` in `tests/unit/strategy/services/test_ability_metadata_effects.py:11-19,53-68`. |
| F-B-005 | closed | `git diff --name-status 82b751fe0..456d12b36` deletes `game/strategy/services/component_inspector.py`; `git grep -n "game.strategy.services.component_inspector\\." -- tests` and `git grep -n "from game.strategy.services.component_inspector import" -- game tests` both return zero live callers; canonical imports are visible in `game/strategy/data/ship_instance.py:636,656,666`, `tests/unit/strategy/services/test_component_abilities.py:16-26`, and `tests/unit/strategy/services/test_component_layers.py:12`. |
| F-B-017 | closed | `game/strategy/engine/order_processor.py:61-115` now exposes only `get_handler(...)`, `process_instant_orders(...)`, and `execute_action_order(...)`; the legacy `process_join_fleet` / `process_colonize` / `process_transfer` helpers and their typed result dataclasses are gone. Representative migrated call sites use the handler-direct path in `tests/integration/colonization/test_explicit_orders.py:63-66,89-93`, `tests/integration/colonization/test_planet_specific_colonization.py:285-287`, and `tests/integration/strategy/test_fleet_registration_lifecycle.py:211-214`. |
| F-B-018 | closed | `game/strategy/engine/order_handlers/base.py:37-61` now documents `OrderExecutionResult` as the live unified surface and no longer labels the five per-handler fields as "legacy". The retained fields all have live producers/readers: `game/strategy/engine/order_handlers/join_fleet.py:73-78`, `game/strategy/engine/order_handlers/colonize.py:138-143`, `game/strategy/engine/order_handlers/transfer.py:215-216`; readers include `tests/integration/strategy/test_fleet_registration_lifecycle.py:214`, `tests/integration/colonization/test_planet_specific_colonization.py:290`, and `tests/integration/colonization/test_explicit_orders.py:93`. |

- I spot-checked the Phase 3 colonize-call migration for the reported one-shot-script bug and did not find malformed duplicated kwargs; representative calls are syntactically correct in `tests/integration/colonization/test_planet_specific_colonization.py:286-287`, `tests/unit/strategy/engine/test_process_colonize_validation.py:201-202`, and `tests/unit/strategy/test_engine_event_emission.py:984-985`.
- The tightened `OrderType` cap looks correct against the current facade: the only runtime `OrderType.*` AST reference left in `game/strategy/engine/order_processor.py` is `OrderType.JOIN_FLEET` at `game/strategy/engine/order_processor.py:88`, and the guard at `tests/unit/strategy/engine/order_handlers/test_order_processor_facade.py:32-57` allows `<= 2`, which still catches a reintroduced branch ladder.
- I do not think a replacement re-emergence guard for the deleted `test_component_inspector_surface.py` is warranted. `component_inspector` was an internal shim, there are no live imports or `patch(...)` targets left, and the canonical surfaces are directly tested in `tests/unit/strategy/services/test_component_abilities.py:16-26` and `tests/unit/strategy/services/test_component_layers.py:12`.

## Side-effects / regressions

- `game/strategy/services/system_effects_collector.py:83-86` still says effect metadata lives in `effect_ability_metadata.EFFECT_ABILITY_METADATA`. That comment is now wrong; the live source of truth is `ability_metadata.py` via `get_ability_metadata(...).effect`.
- `game/strategy/services/ability_metadata.py:111-114` still describes the deleted shim in present tense ("The shim module ... derives ..."). That should be refreshed or past-tensed to avoid implying the shim still exists.
- Several touched Phase 3 tests still narrate the deleted facade methods even though they now dispatch through handlers directly: `tests/unit/strategy/engine/test_process_colonize_validation.py:2-6,176,312`, `tests/unit/strategy/engine/test_fleet_order_transfer.py:91`, `tests/unit/strategy/test_engine_event_emission.py:477-478`, and `tests/integration/strategy/test_fleet_registration_lifecycle.py:210`.

## Out-of-scope observations

- The handler-module docstrings that say "Lifted from `OrderProcessor.process_*`" read as provenance, not as live API promises, so I would not treat them as regressions by themselves: `game/strategy/engine/order_handlers/colonize.py:1-17`, `game/strategy/engine/order_handlers/transfer.py:1-31`, `game/strategy/engine/order_handlers/join_fleet.py:1-22`.
- I did not find an additional behavior bug in the touched files that rises to `discovered_issues/log.jsonl` severity. The remaining residue I saw is documentation/test narration cleanup, not a new runtime defect.

## Summary

- Overall: all four findings are closed in live code on `group-b` / `456d12b36`; the remaining issues are low-severity comment/docstring/test-narration residue, not surviving shim/facade behavior.

## Risks

- I did not run tests because the request explicitly set `allow_tests: false`. This audit is based on current-source inspection, grep, and the `group-b` compare range only.
- A few project checklist claims about "zero grep" closure are only true if you ignore historical comments/docstrings. Future audits that use raw grep without that nuance will get false positives.

## Open questions

None.
