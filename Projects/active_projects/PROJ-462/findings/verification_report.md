# Verification Report — PROJ-462 (foundation)

- **Source audit:** `Reviews/results/2026-05-19_223900_type-audit/`
- **Run date:** 2026-05-19 (independent third pass by Claude against live source)
- **Batch summary (whole audit):** 51 verified / 1 rejected / 2 uncertain (resolved) / 0 out-of-scope, out of a 53-item normalized candidate set drawn from ~250 audit findings.

This report covers the foundation bundle. The Rejected and Uncertain sections below are the audit-wide results (identical narrative across siblings) so each project carries the full picture; the Verified table is foundation-specific.

## Verified (this bundle)

| id | file | symbol | current | suggested |
|----|------|--------|---------|-----------|
| TYP-VEC2 | game/core/math.py:22 | Vector2.__init__ | `y: float = None` | `y: float \| None = None` |
| TYP-VENUM | game/core/validation_helpers.py:69,86 | validate_enum | `return enum_class[value]` → no-any-return | cast(T,...) / `type[Enum]` param / isinstance guard |
| TYP-COLL | game/engine/collision.py:116,133,140 | beam_ab access | `Ability \| None` deref'd | add None guard |
| TYP-FEVAL | game/core/formula_evaluator.py:81 | _eval_node | `-> Any` | `-> int \| float \| bool \| list[float] \| tuple[float,...]` |
| TYP-REG | game/core/registry.py:248,339 | get_validator (method + module) | `-> Any` | `-> ShipDesignValidator \| None` |
| TYP-SM | game/core/state_machine.py:69,133 | state / pop_and_return | `-> Any` | `-> GameState` |
| TYP-COREPROTO | game/core/protocols/strategy_entities.py (18 sites) | IStarSystem/IPlanet/IFleet/... | `-> Any` / `list[Any]` | core types (HexCoord/list[Star]/...) — carve-out, see Uncertain |
| TYP-MUTPROTO | game/core/protocols/strategy_mutators.py | IPlanet/IFleet/IEmpire/IShipInstance mutator params | `Any` params | int\|None / dict[str,float] / ShipInstance / EventBus\|None / str |
| TYP-PIMPL (core part) | game/core/json_utils.py:56 | register_serializable | `type_name: str = None` | `str \| None = None` |
| STRICT-research | game/research/ | — (layer) | est. 0 errors | adopt `--strict` |
| STRICT-services | game/services/ | — (layer) | est. 1 error (import-untyped) | adopt `--strict` |
| STRICT-assets | game/assets/ | — (layer) | est. ~10 errors | adopt `--strict` |
| STRICT-engine | game/engine/ | — (layer) | est. ~11 errors | adopt `--strict` |
| STRICT-core | game/core/ | — (layer) | est. ~77 errors | adopt `--strict` |

Note on strict-migration counts: the audit attributed mypy errors by file path. `mypy <path>` follows imports and reports the whole transitive set (re-run here showed 2,269 errors / 325 files in aggregate, consistent with the audit's 2,108 real errors after excluding combat_lab). Treat the per-layer numbers as estimates and confirm the real count at the start of each strict-migration task. No layer is at zero, so none is OUT_OF_SCOPE.

(The implicit-Optional finding TYP-PIMPL spans layers; only its core site `json_utils.py:56` lands in this bundle. The remaining sites are split into PROJ-463/PROJ-464 by layer.)

## Rejected (audit-wide)

| id | original audit recommendation | contrary evidence | rationale |
|----|-------------------------------|-------------------|-----------|
| TYP-APP | Narrow `game/app.py` Game scene accessor properties from `-> Any` to `-> IScene` | `game/app.py:198-233` (all route through `_route_get`); audit's own Shard 04 minor#5 rates acceptable | Scene proxies are intentionally loose so `Game.__new__(Game)` tests assign attributes directly; narrowing breaks test mocks. Separate hardening question, not audit residue. Codex concurred. |

## Uncertain (resolved)

| id | verifier question | decision |
|----|-------------------|----------|
| TYP-COREPROTO | Some `strategy_entities.py` `-> Any` are narrowable (HexCoord, list[Star]) but `ICombatant.position`/`ILocatable.location` must stay `Any` (Vector2 in sim vs HexCoord in strategy); narrowing needs cycle-safe imports | **INCLUDE (this bundle)** with boundary-preserving carve-out — Phase 2.4: narrow strategy-map surfaces to core types only; leave the polymorphic position/location seams as `Any`; never import strategy concrete types into core. |
| TYP-SR | `strategy_renderer.py` 13 props: cross-layer report says narrowable, Shard 04 says acceptable; tests use MagicMock scenes | **INCLUDE (PROJ-464)** framed as a minimal renderer-scene Protocol seam cleanup, not a hard narrow to `StrategyScreen`. |

## Out of Scope

None promoted. The audit's own `findings/verification.md` already excluded justified ignores (e.g. `pygame_gui_patch.py` monkeypatch, `deployed_group.py` decorator attr), and those were never added to the candidate set.
