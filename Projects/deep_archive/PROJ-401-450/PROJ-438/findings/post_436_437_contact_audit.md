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

---

## Phase 0 Re-Verification (2026-05-18)

Re-validated the audit against the current `main` HEAD after PROJ-436 Phases 0–9 and PROJ-437 Phase 0 landed. No load-bearing assumption invalidated. Line numbers shifted slightly because Phase 9 reshaped `ship_instance.py` (–185 LOC) and surrounding files; file paths and structural claims are intact.

### Predecessor reality on this checkout

| Project | Code on `main` | Artifact in tree | Notes |
|---------|----------------|------------------|-------|
| PROJ-423 | Complete | n/a (archived) | GameSession bootstrap extraction landed; reused, not reopened. |
| PROJ-424 | Complete | n/a (archived) | Order metadata convergence landed; `OrderMetadataView` is canonical read. |
| PROJ-425 | Complete | n/a (archived) | ShipInstance slimming + 910-caller shims (kept by intent). |
| PROJ-429 | Complete | n/a (archived) | Ability metadata unified; `AbilityMetadataRegistry` is canonical. |
| PROJ-436 Phases 0–9 | **On main** (merge `eb8da3d85`) | Stale: `plan.md` still shows Phase 9 = Not Started | Other-machine artifact updates not yet pushed; *code* is current. Verified `_CarriedItemsProxy` deleted (`ship_instance.py:512–514, 765–768` are deletion-marker comments only). |
| PROJ-436 Phase 10 (docs) | **NOT on main** | Stub checklist | Phase 8 of PROJ-438 must wait. |
| PROJ-436 Phase 11 (Codex consult) | **NOT on main** | Stub checklist | Independent of PROJ-438. |
| PROJ-437 Phase 0 | On main (`963f1859d`) | `findings/transfer_ui_migration_map.md` present | Container-API survey done. Phases 1–5 not started. No file overlap with PROJ-438. |
| PROJ-443 (hidden-tests recovery) | Complete on main | n/a | **Flipped `pytest.ini` `norecursedirs`** in Phase 4 (`e12603992`). D1 settled by side-effect. |

### Residual `#1` re-verification

| Claim | Verified location (post-436 Phase 9) | Status |
|-------|--------------------------------------|--------|
| 4-loop graph restoration duplication in save-load path | [`persistence_adapter.py:172–197`](../../../../game/strategy/engine/session/persistence_adapter.py#L172) (galaxy backref, fleet register, order resolve, pursuer rebuild) | **Intact.** |
| Mirroring 4-loop restoration in rollback path | [`turn_state_snapshot.py:112–136`](../../../../game/strategy/engine/turn_state_snapshot.py#L112) (verbatim shape, with explicit `Mirrors persistence_adapter.py:NNN–NNN` comments) | **Intact.** Duplication is acknowledged in-source by PROJ-432 comments — confirms the seam wasn't drift-corrected sideways. |
| Asymmetric `DesignCatalog` handling | `persistence_adapter.py:199–228` populates per-empire `DesignCatalog`; `turn_state_snapshot.restore()` does not | **Intact.** The asymmetry remains the high-signal divergence point Phase 1 must call out (canonicalize or document). |
| GameSession mixed concerns | `save_path`, `human_player_ids`, derived `active_empire`/`enemy_empire`, lazy race-registry, façade cache holder | **Intact** (file unchanged by PROJ-436 Phase 9). Phase 2 named-concern list still load-bearing. |
| Broad entity roots | `Planet` (~47 dataclass fields, ~166 LOC of state declaration), `Fleet`, `Empire`, `ShipInstance` (768 LOC post-Phase 9; D2 default (a) is to narrow surface without forcing the 910-caller sweep) | **Intact, with ship_instance.py shape reset by Phase 9.** Phase 3 should re-audit `ship_instance.py` shape directly at phase start; do not rely on pre-Phase-9 line numbers. |
| Façade compensation cache | `strategy_session_facade.py:181`, `_facade_state.py:34` | **Intact.** Per kickoff prompt, this is a legitimate performance boundary — Phase 2 does not eliminate it. |

### Residual `#3` re-verification

| Claim | Verified location | Status |
|-------|-------------------|--------|
| `IssuePlanetOrderCommand.order_type: str` | [`game/strategy/engine/commands/__init__.py:557–574`](../../../../game/strategy/engine/commands/__init__.py#L557) (shifted from prompt's 558–574 by 1 line) | **Intact.** Phase 5 surgical target. |
| String→enum bounded mapping | [`planet_command_handlers.py:62–90`](../../../../game/strategy/engine/planet_command_handlers.py#L62) — closed `{ACTIVATE_ABILITY, DEACTIVATE_ABILITY}` with else-reject | **Intact.** Type-stub of the eventual typed planet intents. |
| Private `_handler_registry` reach-in + `TypeError` fallback | [`action_execution_engine.py:299–337`](../../../../game/strategy/engine/action_execution_engine.py#L299) — comment at L322 explicitly identifies the recovery vs launch handler signature split as the fallback's reason | **Intact.** Phase 6 surgical target. Only external `_handler_registry` consumer in the repo. |
| Blast radius ≈ 40 contained changes for `IssuePlanetOrderCommand` retirement | UI entry `planet_abilities_controller.py:234` + ~32 tests + registry registration | **Intact** (not re-counted; predecessor figure adopted). |
| Order persistence outside live metadata | `CommandSpec.serializer_codec`, `Order.to_dict()`, `OrderSerializer` hardcoded target-shape branching | **Intact.** Phase 7 surgical target. |
| `IMPLICIT_ACTION_ORDER_TYPES`, mission decomposition, `JOIN_FLEET` instant path | D3 default LOCKED: acceptable specialized behavior unless implementation audit proves blocking leakage | **Intact.** Decision locked in `decisions.md` D3. |

### Support-surface re-verification

- **D1 (verification gate) is settled in option (a) on disk.** `pytest.ini` line 6 reads `norecursedirs = .* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes` — `data` is *not* listed. PROJ-443 Phase 4 (`e12603992`) explicitly flipped this with +1953 tests newly visible. The canonical sharded suite alone is the verification gate; no supplemental direct-run matrix needed. Decisions log updated.
- **Anti-drift guards still present** (file count check, not re-content-audited): `tests/unit/strategy/engine/session/test_bootstrap.py`, `tests/unit/strategy/engine/test_game_session_shape.py`, `tests/unit/strategy/ship_instance/`, `tests/unit/strategy/engine/commands/test_order_metadata_view.py`, `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`.

### Hard-block gates re-checked

| Phase | Predecessor gate | Status on this checkout |
|-------|------------------|--------------------------|
| 0, 1, 2 | None | **Clear.** Proceed. |
| 3 | PROJ-436 Phase 9 (`_CarriedItemsProxy` deletion) | **Cleared.** Merge `eb8da3d85`; symbol absent from production code path. |
| 4 (doc-touch only via galaxy_protocols.py) | Co-touch risk with PROJ-436 Phase 10 docs | **Low risk.** Phase 4's doc footprint is narrow (`galaxy_protocols.py` read contracts). Three-way merge unlikely. |
| 5, 6, 7 | Independent | **Clear.** |
| 8 | PROJ-436 Phase 10 (docs) | **NOT cleared yet.** No Phase 10 commit on main. Hard-stop and surface to user before Phase 8 (per kickoff prompt). |

### Outcome doc availability

The kickoff prompt referenced `AgentCoordination/Scratchpad/Discussion/20260518T015908Z_proj-438-feedback/outcome.md`. The Scratchpad tree is gitignored and not present on this checkout. Consensus content is already reflected in `decisions.md` and `plan.md` — no information loss. Not a blocker.

### No changes to scope, decisions, or phase ordering required from this audit.
