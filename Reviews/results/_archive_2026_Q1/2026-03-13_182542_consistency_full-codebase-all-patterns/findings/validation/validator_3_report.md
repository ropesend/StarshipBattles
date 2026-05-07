# Validation Report: Validator 3

## Summary
- **Findings Reviewed:** 20
- **Confirmed:** 6
- **Downgraded:** 6
- **Rejected:** 8
- **Rejection Rate:** 40%

## Verdicts

#### Finding: IH-03
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified ~15 methods return `Tuple[bool, str]` (in save_game_service, design_library, race_library, race_config, etc.) while the canonical `ValidationResult` class exists in `game/core/validation.py`. These are genuinely different contracts for the same concept. However, several of the `Tuple[bool, str]` uses are for simple success/failure operations (save, delete) where `ValidationResult`'s multi-error support is overkill -- the inconsistency is real but the migration benefit is moderate.

#### Finding: IH-04
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified identical copy-paste `_get_registries()` functions at `game/ui/services/ship_io.py:41-53` and `game/ui/screens/strategy_build_queue_manager.py:37-49`. Same code, same PROJ-211 comment, same caching pattern, creating two separate `GameRegistries` instances. Textbook DRY violation, simple to fix by extracting to a shared utility.

#### Finding: IH-05
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified both `handle_event` (39 occurrences) and `process_event` (17 occurrences) exist across UI classes. However, the split correlates loosely with class type: windows/dialogs tend to use `process_event`, screens/panels use `handle_event`. There is no formal interface contract requiring either name, and since these are not polymorphically dispatched through a common base class, the inconsistency is cosmetic rather than causing runtime issues. Downgraded because renaming would touch 17+ files with no functional benefit.

#### Finding: IH-06
**Original Severity:** Major
**Verdict:** CONFIRMED
**Reason:** Verified two completely different classes share the name `BattleConfig`: (1) `game/core/config.py:111` is a static constants namespace (TARGET_QUERY_RADIUS, COLLISION_BUFFER, etc.), (2) `game/simulation/battle_config.py:27` is a `@dataclass` for per-battle instance configuration (mode, seed, max_ticks, etc.). The name collision is real and IDE auto-import will cause confusion. Renaming the constants class to `BattleConstants` or `CombatConstants` is a simple fix.

#### Finding: IH-07
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified three different patterns for `registries` parameter: required keyword-only (`*, registries: GameRegistries`), optional with fallback (`registries: Optional[GameRegistries] = None`), and some with `= None` but no type hint. At least 12 files still use the Optional pattern, contradicting the PROJ-211 direction toward required DI. The inconsistency is real and creates ambiguity about whether registries are truly required.

#### Finding: IH-08
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified `IRegistryProvider` (Protocol) is used in UI services (component_service, vehicle_class_service) while `GameRegistries` (dataclass) is used directly in simulation and strategy code. Since `GameRegistries` already implements `IRegistryProvider` (PROJ-211), the two types are interchangeable but the codebase hasn't standardized on one. The copy-pasted `_get_registries()` adapters (IH-04) are a direct symptom.

#### Finding: IH-09
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified that 269 files use `typing` module generics vs only ~10 files using PEP 585 lowercase generics (list[], dict[], etc.). The PEP 585 usage is extremely rare (under 4% of files). This is a minor cosmetic inconsistency that does not affect functionality or readability. Not actionable without a project-wide linter enforcement decision.

#### Finding: IH-10
**Original Severity:** Minor
**Verdict:** CONFIRMED
**Reason:** Verified 10+ locations raise raw `ValueError` or `TypeError` despite the well-structured custom exception hierarchy. Examples include `fleet_capability_calculator.py:72,135`, `command_handlers.py:175,178`, `ship_loader.py:136`, `component.py:566,672`, and `abilities/base.py:374`. These bypass `GameException` catch handlers and lose error code context.

#### Finding: IH-11
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is a known architectural state of an ongoing migration, not an actionable finding. The facade pattern was introduced deliberately with the understanding that full migration would take multiple projects. Info-level observations about partially-completed migrations are not actionable.

#### Finding: IH-12
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The two iteration approaches serve fundamentally different contexts: `ship.iter_components()` operates on hydrated Ship objects (simulation layer), while `iter_components(design_data)` operates on raw dict data (strategy layer without hydrated ships). The report itself acknowledges this is "partially by design." The manual `.layers.items()` loops are a minor concern but this is not an inconsistency -- it is two tools for two different data shapes.

#### Finding: PC-01
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** This is a positive observation, not a finding. The report states the exception hierarchy is "clean and consistent" with no recommended action. Info-level positive observations are not actionable findings.

#### Finding: PC-02
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Verified all 20 `except Exception` catches. The majority (14 of 20) have explicit "Intentional broad catch" comments explaining why they are needed (top-level crash handler, platform-dependent code, eval() catch-and-convert). The remaining 6 without comments are in serialization/deserialization code (empire.py, fleet.py, fleet_order_serializer.py) where broad catches prevent corrupt save data from crashing the game. These are defensible patterns at I/O boundaries, not bugs.

#### Finding: PC-03
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The report itself states the dual pattern is "intentional and documented" with no recommended action. This is an observation, not a finding.

#### Finding: PC-04
**Original Severity:** Info
**Verdict:** REJECTED
**Reason:** The report identifies only 3 method-level logger declarations out of 136 files -- a 98% consistency rate. This is not a meaningful finding. The 3 outliers are trivially fixable but not worth tracking as a finding.

#### Finding: PC-05
**Original Severity:** Minor
**Verdict:** REJECTED
**Reason:** Verified all 7 `print()` calls are inside docstrings/examples (e.g., `game/core/protocols.py` line 12/15 in a docstring example, `game/simulation/interfaces/entity_protocols.py` line 16 in a docstring). Zero runtime print statements exist in the game code. This finding is factually incorrect.

#### Finding: PC-06
**Original Severity:** Info
**Verdict:** REJECTED (positive observation, not actionable)
**Reason:** The report states JSON loading is well-centralized with "no recommended action." This is a positive observation, not a finding.

#### Finding: PC-07
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** The report itself acknowledges the `from_dict`/`to_dict` vs `@dataclass` split is "actually logical" and "intentional and well-organized." Domain entities need custom serialization; DTOs use dataclasses. The recommendation is "maintain current approach." This contradicts a Minor severity -- it is an informational observation at best.

#### Finding: PC-08
**Original Severity:** Major
**Verdict:** DOWNGRADED(Minor)
**Reason:** Verified the duplicate `ICombatShip` definition exists in both `game/core/protocols.py:601` and `game/simulation/interfaces/entity_protocols.py:43`. This is a real issue. However, the broader Protocol-vs-ABC claim is overstated: ABCs are used for template method patterns (ValidationRule has shared implementation, BattleModeHandler has shared implementation), while Protocols are used for structural typing contracts. This split is actually a reasonable design choice. The `ICombatShip` duplicate and inconsistent `I` prefix naming are real but minor issues, not a Major architecture problem.

#### Finding: PC-09
**Original Severity:** Minor
**Verdict:** DOWNGRADED(Info)
**Reason:** Only 5 occurrences of `X | None` vs 207 occurrences of `Optional[X]`. At under 3% deviation, this is not a meaningful inconsistency. The codebase is 97%+ consistent on `Optional[X]`.

#### Finding: PC-10
**Original Severity:** Info
**Verdict:** REJECTED (positive observation, not actionable)
**Reason:** The report states property usage is "consistent and well-organized" with "None" impact and no recommended action. Positive observations are not findings.
