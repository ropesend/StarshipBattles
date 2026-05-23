# PROJ-470: Independent Verification Report

**Source audit:** `Reviews/results/2026-05-20_075227_pattern-audit/`
**Re-verification run:** 2026-05-21 (independent third pass; live code read directly by a different reader than the audit's Phase-1 shard reviewers and its internal `verification.md`)
**Batch summary:** 15 VERIFIED / 0 REJECTED / 3 UNCERTAIN (all resolved → Defer) / 3 OUT_OF_SCOPE, out of 18 actionable candidates.

> Note on 0 REJECTED: Protocol 18 Phase G flags a zero-rejection downstream pass as suspicious. Here it is explained: the audit's own `verification.md` already downgraded/disputed its weakest claims (MAJ-H1, MAJ-H4, MAJ-H5 severity), so the candidate set that entered this pass was pre-filtered. My independent reads confirmed every surviving claim against live code and additionally **corrected one audit artifact error**: `raw/protocol_registry.json` wrongly omitted `is_fleet`/`is_planet`/`is_storm`/`is_star_system`, which exist at `game/core/protocols/strategy_entities.py:415-445`.

## Verified

| ID | File | Symbol | Pattern | Current state | Recommended state | Severity | Risk |
|----|------|--------|---------|---------------|-------------------|----------|------|
| FAC-001 | `game/ui/` (135+ sites) | n/a | #5 | UI imports strategy data/engine types directly for reads | facade read DTOs or documented UI-safe read surface + static guard | CRITICAL | Write-path-only half-facade; boundary erodes silently without a read-path guard |
| FAC-002 | `game/ui/panels/build_queue_controller.py`, `game/ui/screens/build_queue_screen.py:23`, `game/ui/screens/fleet_data_source.py:242` | BuildQueue/fleet | #5 | densest single-file strategy-import bypass sites (build_queue_controller imports TYPE_CHECKING-only; the others runtime) | route reads through facade or sanctioned surface | CRITICAL | Same as FAC-001; these are the highest-density sites |
| FAC-003 | `game/ui/screens/strategy_screen.py:242-257` | `StrategyScreen.session` | #5 | public `session` property exposes `_session`; 4 consumers read domain objects directly | facade accessors + read-path guard | MAJOR | AST guard protects write path only; read bypass persists |
| MOD-001 | `game/ui/screens/settings_window.py:14` | `SettingsWindow` | #31 | `class SettingsWindow(UIWindow)`; manual on_close_callback; no `is_blocking`, no modal registration | subclass `StrategyModalWindow`, add `window_manager` | MAJOR | Background hover/click leaks through; not counted by `has_modal_open()` |
| EVT-001 | `game/ui/screens/builder/event_bus.py:5` | `WorkshopEventBus` docstring | #10 | docstring references `game/core/events/event_bus.py` (confirmed nonexistent) | reference `game/core/event_logging.py`; name `WorkshopEventBus` in doc | MAJOR | Stale path is a maintainability hazard; doc omits class name |
| ENUM-001 | `game/core/protocols/strategy_entities.py:374` | `IAbilitySource.source_kind` | #29 | `source_kind(self) -> str`, 7 values in docstring, no enum | `StrEnum`/`Literal` for the 7 kinds | MINOR | Adding an 8th kind produces no type error |
| TG-001 | `game/strategy/data/order_types.py:104,116,119` | `Order.__repr__/__str__` | #2 | `isinstance(self.target, Planet/Fleet)` | `is_planet`/`is_fleet` (exist at strategy_entities.py:425,430) | MINOR | Same-layer drift from Protocol+TypeGuard convention |
| TG-002 | `game/strategy/facade/dto/fleet_dto.py:152-183` | `FleetInfo.from_fleet` | #2 | `isinstance(order.target, Planet/Fleet)` arms | `is_planet`/`is_fleet` TypeGuards | MINOR | Same as TG-001 |
| TG-003 | `game/strategy/facade/slices/system_slice.py:132` | `get_storm_names_at_hex` | #2 | `isinstance(zone, Storm)` | `is_storm` (exists at strategy_entities.py:445) | MINOR | Same as TG-001 |
| TG-004 | `game/strategy/data/build_queue_source.py:294` | n/a | #2 | `isinstance(entity, Fleet)` | `is_fleet` | MINOR | Same as TG-001 |
| DOC-032 | `docs/02_PATTERNS.md` (Pattern #32) | Compositional Construction | #32 | doc implies 3+ adopters; only `StrategyScreen` consumes it | add single-consumer usage note | MINOR | Doc-side; misleads on adoption |
| DOC-036 | `docs/02_PATTERNS.md` (Pattern #36) | Re-Export Shim | #36 | doc says lines 395-405; block is at component.py:392 | update to 392-405 | MINOR | Doc-side; trivial offset |
| LOC-001 | 69 files (`raw/file_size_violations.txt`) | n/a | n/a | 69 production files >500 LOC under `game/` | triage; split top-10 | MINOR | Maintainability; full remediation deferred to separate project |
| UP-001 | `game/strategy/data/habitability_factors.py` | `FACTOR_REGISTRY` | new | undocumented; AGENTS.md names it a key pattern; 24 refs | new pattern entry | STRATEGIC | Agents lack a documented contract |
| UP-002 | `game/strategy/services/ability_metadata.py` | `AbilityMetadataRegistry` | new | undocumented; 566 LOC; cycle-safety guard | new pattern entry | STRATEGIC | Large API undocumented |
| UP-006 | `game/core/roles.py` + `game/strategy/data/design_role_registry.py` | `RoleRegistry` | new/#4 | undocumented layered-loading registry, 2 instances | new entry or #4 sub-section | STRATEGIC | Layered-load + invalidation recipe undocumented |

## Rejected

None. (The audit's internal `verification.md` had already disputed/downgraded its weakest claims before this pass — see the Out of Scope section.)

## Uncertain (resolved)

| ID | Question raised | Decision |
|----|-----------------|----------|
| UP-003 PerPlayerUiState | Standalone pattern entry, or leave under Pattern #11 which already documents the per-player view-state contract? | **Defer** — already covered by Pattern #11 (docs validator rates #11 ACCURATE incl. this subsection); promote only if a future audit shows it needs its own heading. |
| UP-004 Declarative Dispatch Table | Promote to a pattern, or treat as a Pattern #4 variant? Recurs in only 2 registries (below the 3+ bar). | **Defer** — below the audit's own 3+ promotion bar; the docs validator frames it as a Pattern #4 variant, not a standalone pattern. |
| UP-005 FacadeSessionState | Split out from Pattern #11 into its own mini-pattern? | **Defer** — already documented as a sub-section under Pattern #11; elevation is a judgement call for a future audit. |

## Out of Scope

| ID | Why excluded |
|----|--------------|
| MAJ-H1 (simulation_adapter `get_default_registry_provider`) | Audit's own `verification.md` marked DISPUTED — `simulation_adapter.py:51-52` is the designated strategy-layer injection point (strategy injects the provider into simulation); correct adapter pattern, not a violation. |
| MAJ-H4 (RaceSetupScreen/NewGameSetupScreen extend UIWindow) | Audit's own `verification.md` marked DISPUTED (downgrade) — these are full-screen setup wizards that own the entire UI context, not strategy-screen modals; Pattern #31 does not apply. |
| Pattern #3 `component_layers.py:52` fallback | Scorecard MINOR_DRIFT; strategy-layer (Pattern #3 permits global access outside simulation), narrow legacy-save-only fallback with the required `# Intentional broad catch:` comment. All 3 shard reviewers classified it as a non-violation MINOR. Treated as accepted convention, not actionable. |
