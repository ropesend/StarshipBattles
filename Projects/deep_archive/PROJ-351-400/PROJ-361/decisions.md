# PROJ-361: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Top finding (P1) of Strategy Layer Tech Debt Review (Reviews/results/2026-05-05_strategy-layer-tech-debt-review/report.md, finding #1) |
| 2026-05-04 | Renumbered from PROJ-351 to PROJ-361 | Merge-conflict collision on PROJ-351..360 from commit 97a96e7d0; user chose to leave existing IDs alone and start fresh at 361 |
| 2026-05-04 | No `IRegistryProvider` adapter class — pass `registries` directly | `GameRegistries` already implements the Protocol per PROJ-211 (`game/core/registry.py:66-112`). An adapter would be dead code. |
| 2026-05-04 | Preserve `get_default_registry_provider()` as `None`-fallback | PROJ-306 explicitly permits strategy layer to call it; we are correcting the asymmetry of ignoring an injected `registries`, not removing the default. |
| 2026-05-04 | Single-phase project, no decomposition | Bug fix scope: one production line + one regression test. Decomposing into phases would be ceremonial. |
| 2026-05-04 | New regression test uses marker-design fixture pattern | Inject a `GameRegistries` containing a design name not in defaults; assert the materialized ship contains it. Simplest end-to-end proof. |

---

## Audit Remediation (2026-05-05)

OpenCode review `req_20260505_055831_416bac` flagged 0 CRIT and 4 MAJOR
findings against PROJ-361 (review report:
`Reviews/results/2026-05-05_055833_code_proj-361-review-battle-resolver-registry-threading_req-req_20260505_055831_416bac/report.md`).

| ID | Verdict | Rationale |
|----|---------|-----------|
| CQ-01 | fix-now | `_instances_to_ships` and the `shortcut_sole_survivor` branch passed raw `registries` (could be `None`) directly to `ShipInstance.to_ship`, which requires non-None — pre-existing crash path on the documented `IBattleResolver` default contract. |
| CQ-02 | fix-now | `_build_spec` accepted `Optional[GameRegistries]` and forwarded it to `build_strategy_battle_spec` (non-Optional) — latent type hole that would crash once `spec_compiler` actually consumes `registries`. |
| TC-01 | fix-now | Regression test only asserted `run_battle.registry_provider`; it did not verify registries reached `_instances_to_ships`. False confidence; CQ-01-style regressions could ship undetected. |
| TC-02 | fix-now | `_MockShipInstance.to_ship` was permissive (`registries=None`), masking the real signature (`*, registries` keyword-only, no default) and hiding `None`-passing bugs. |

### Fix shape

Centralized the `None` fallback into a single helper
`_resolve_registries(registries)` invoked once at `resolve_battle` entry.
All downstream call sites (`_run_simulated_battle`, `_build_spec`,
`_instances_to_ships`, `run_battle.registry_provider`) now receive
guaranteed non-None `'GameRegistries'` and their type signatures were
tightened accordingly. The PROJ-306-permitted boundary call to
`get_default_registry_provider()` lives in exactly one place. The
`shortcut_sole_survivor` branch now uses the resolved registries instead
of the raw input.

### Test additions

- Updated `_MockShipInstance.to_ship` to match the real signature
  (`*, registries` keyword-only, no default) and to capture the value.
- Existing test now also asserts `_instances_to_ships` received the
  injected registries (TC-01).
- Existing fallback test now also asserts the default provider reaches
  `_instances_to_ships`.
- Two new tests cover the `shortcut_sole_survivor` branch under both
  injected and `None` registries (CQ-01 regression coverage).

### Validation

- `pytest tests/unit/strategy/adapters/ -v`: 20 passed.
- `python Tools/test_sharded/test_sharded.py`: 17770 passed, 0 failed,
  0 errors, 4 skipped.

### Deferred

- CQ-03/CQ-04/AR-01/CQ-05/AR-02 are MINOR/INFO and out of scope for this
  remediation pass per the audit instructions.
