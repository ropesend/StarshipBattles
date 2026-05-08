# PROJ-386 — Verification Report

**Source audit:** `Reviews/results/2026-05-07_220621_legacy-audit/`
**Run date:** 2026-05-08
**Cluster:** Save-format migration eradication
**Batch summary:** 4 verified / 0 rejected / 0 uncertain / 0 INFO / 0 out-of-scope (within this bundle)

## Verified

| ID | File | Symbol | Replaces | Call sites | Recommendation | Severity | Policy violation |
|---|---|---|---|---|---|---|---|
| LEG-03-008 | `game/ui/screens/battle_setup/controller.py:548-568` | `_complex_toggles` legacy migration | (none — old format unsupported) | reached via `_load_from_path` | delete | MAJOR | CLAUDE.md Rule 3 |
| LEG-03-017 | `game/strategy/data/component_activation_state.py:144-149` | `{'active': bool}` old-format branch | (none — required field is `phase`) | reached via `from_dict` | delete | MAJOR | CLAUDE.md Rule 3 |
| LEG-03-018 | `game/strategy/data/ship_instance_serializer.py:100-102, 127-138` | silent-ignore `component_damage` + graceful-degrade missing `components` | (none — disposable per CLAUDE.md) | reached via `from_dict` | delete | MINOR | CLAUDE.md Rule 3 |
| LEG-04-005 | `game/ui/screens/battle_setup_state.py:257-300` | `side_0`/`side_1` legacy emit + read | new `sides` list format | reached via `to_dict` / `from_dict` | delete | MAJOR | CLAUDE.md Rule 3 |

## Rejected

None — all 4 items survived independent re-verification.

## Uncertain (resolved)

None for this bundle.

## INFO (resolved)

None for this bundle.

## Out of Scope

The audit's deterministic `save_migration_code` scanner found 0 findings across this codebase. All 4 items in this bundle were caught by agent review (deprecation_marker / additional indicators paths) and reclassified as save-migration. This is a known false-negative pattern in the source skill — recorded for the refinement-feedback channel.
