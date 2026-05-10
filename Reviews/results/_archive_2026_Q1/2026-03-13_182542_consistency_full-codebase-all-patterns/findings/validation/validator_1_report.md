# Validation Report: Validator 1

## Summary
- **Findings Reviewed:** 20
- **Confirmed:** 10
- **Downgraded:** 3
- **Rejected:** 7
- **Rejection Rate:** 35%

## Verdicts

#### Finding: AR-01
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified that `get_ui_rows()` methods exist in the base `Ability` class and 12 ability subclasses in `game/simulation/components/abilities/`. These return UI-formatted dicts with label/value/color_hint, which is presentation logic living in the simulation layer. This violates the stated layer separation principle (simulation should not depend on UI concerns).

#### Finding: AR-02
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Two distinct `ICombatShip` Protocol classes exist: one at `game/core/protocols.py:601` and another at `game/simulation/interfaces/entity_protocols.py:43`. They have different property sets (the simulation version includes `angle`, `velocity`; the core version includes `resources`, `secondary_targets`). This is a genuine duplication that could cause confusion about which protocol to implement against.

#### Finding: AR-03
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified that strategy uses ABCs (`game/strategy/interfaces/engines.py` has 11+ ABC-based interfaces) while core/simulation use Protocols. However, this is a deliberate architectural choice -- ABCs enforce implementation contracts for engine plugins while Protocols enable structural subtyping for cross-layer boundaries. This is a reasonable pattern, not a defect. Downgraded to Minor as a consistency observation.

#### Finding: AR-04
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** StrategyScreen does create a `StrategySessionFacade` and passes it to sub-modules (`FleetOperations`, `ColonizationSystem`, `SuperweaponOperations`). It also has convenience properties delegating to `self.session` (galaxy, empires, systems, etc.), but these are explicitly documented as "for internal convenience" with a comment stating "External callers should use the facade." The bypass is limited to read-only property access within the screen's own sub-modules, not a fundamental design flaw.

#### Finding: AR-05
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `_has_attrs` is defined identically in 4 separate files: `game/core/protocols.py:694`, `game/ai/protocols.py:174`, `game/simulation/interfaces/entity_protocols.py:480`, and `game/simulation/interfaces/ability_protocols.py:315`. This is genuine triplication (actually quadruplication). A shared utility would reduce maintenance burden.

#### Finding: AR-06
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** `ValidationService.__init__` accepts an optional `validator` parameter for DI but falls back to `get_or_create_validator(registry_provider=get_default_registry_provider())` if None. Meanwhile, `ShipValidatorHelper` (which does the same validation) always uses the global fallback with no DI option at all. The inconsistency in DI strictness between these two related services is real.

#### Finding: AR-07
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** The module-level `_event_handler` global in `game/core/event_logging.py` is well-documented with explicit lifecycle management (set by GameSession, cleared in test fixtures). It's a standard callback registration pattern with proper no-op behavior when unset and exception safety. The docstring even explains the rationale. This is a controlled, appropriate design, not a defect.

#### Finding: AR-08
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** In `game/strategy/engine/game_session.py`, imports are interleaved with code: `logger = logging.getLogger(__name__)` appears at line 59 between import blocks, and imports appear both before and after the TYPE_CHECKING block. While functionally correct, this violates PEP 8 import ordering conventions.

#### Finding: AR-09
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** `game/engine/` is well-documented with a clear `__init__.py` listing its public API (PhysicsBody, CollisionSystem, SpatialGrid). `game/research/` exists with its own `__init__.py`. These are not "undocumented" -- they have module docstrings. The finding overstates the issue. Downgraded to Info as these modules exist with clear purpose.

#### Finding: AR-10
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** At `game/simulation/components/modifier_introspection.py:142`, `hasattr(mod_def, 'evaluate_effects')` is used as a duck-typing guard instead of a protocol check. While this is a single instance, it's inconsistent with the project's established pattern of using Protocol-based type guards elsewhere in the simulation layer.

#### Finding: AR-11
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Non-actionable observation. The instructions state info-level observations that are not actionable should be rejected.

#### Finding: AR-12
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** Non-actionable observation. The instructions state info-level observations that are not actionable should be rejected.

#### Finding: CQ-01
**Original Severity:** Critical
**Verdict:** CONFIRMED
**Reason:** `add_component` (lines 502-531) and `add_components_bulk` (lines 538-576) share near-identical code for validation, layer assignment, component setup, modifier application, and cache invalidation. The bulk method duplicates the entire inner logic instead of calling `add_component`. Both also use `get_default_registry_provider()` instead of the ship's own `self._registries`, which is a genuine DI bypass since Ship requires strict DI via constructor.

#### Finding: CQ-02
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `ShipValidatorHelper` calls `get_default_registry_provider()` on lines 44, 55, and 64 instead of using `self._ship._registries`. The Ship class enforces strict DI (raises ValidationException if registries is None), but the validator helper bypasses this by going to the global default. This undermines the DI guarantees.

#### Finding: CQ-03
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** The magic number 100 (ticks per turn) appears hardcoded across multiple engine files: `turn_engine.py` uses `range(1, 101)`, `production_engine.py` defines `TICKS_PER_TURN = 100` locally, `environmental_hazard_engine.py` divides by `100.0` directly, and `maintenance_engine.py` documents "1/100th" throughout. Only `production_engine.py` uses a named constant, and it's local to that module. A single shared constant would be appropriate.

#### Finding: CQ-04
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** "129 potentially unused imports" is a vague claim with no specific examples provided. Many apparent "unused" imports are TYPE_CHECKING imports, re-exports in `__init__.py` files, or imports used by frameworks (pytest fixtures, etc.). Without specific verified examples, this is not actionable.

#### Finding: CQ-05
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** `Fleet.from_dict` at lines 247-250 manually parses HexCoord from dict/list format, while `hex_from_dict` exists in `game/core/hex_math.py` and is used by other strategy data classes (`stars.py`, `planet.py`, `galaxy.py`, `storm.py`). This is a genuine DRY violation where the utility is available but not used.

#### Finding: CQ-06
**Original Severity:** Major
**Verdict:** REJECTED
**Reason:** Ship.__init__ is part of PROJ-88 (Simulation Core Tier god class decomposition), which is an active project. The instructions state findings about classes with active decomposition projects should be rejected.

#### Finding: CQ-07
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** "331 lines at depth >= 7" across the entire UI codebase is a statistical observation without specific actionable locations. UI code often has legitimate deep nesting from event handling and rendering logic. Without specific problematic instances identified, this is not actionable.

#### Finding: CQ-08
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** "25 functions exceeding 80 lines" is a statistical observation without specific examples. Many of the likely candidates (Ship.__init__, GameSession methods) are already covered by active decomposition projects (PROJ-86 through PROJ-89). Without specific non-PROJ functions identified, this is not actionable.
