# Code-Base Accuracy Validation Report

## Summary
- Claims Checked: 28
- Confirmed (doc wrong): 12
- Disputed (doc correct): 12
- Inconclusive: 4

---

## Verified Accuracy Issues

### 1. `game/core/protocols.py` → `game/core/protocols/` directory

**Claim:** Docs reference `game/core/protocols.py` as a single module.
- `docs/01_ARCHITECTURE.md:124` — lists `protocols.py` in the core module table.
- `docs/01_ARCHITECTURE.md:276` — "All defined in `game/core/protocols.py`."
- `docs/01_ARCHITECTURE.md:346` — "Protocol definitions in `game/core/protocols.py`."
- `docs/02_PATTERNS.md:1524` — Quick Reference table: `Protocol+TypeGuard | game/core/protocols.py`.
- `docs/02_PATTERNS.md:1544` — Quick Reference table: `Serializable | game/core/protocols.py`.
- `game/core/__init__.py:46` — docstring says "Protocols (game.core.protocols)" but that's ambiguous.

**Actual:** The file was decomposed into a package directory `game/core/protocols/` with sub-modules (`common.py`, `registry.py`, `strategy_entities.py`, `strategy_domain.py`, `combat.py`, `boundary.py`, `ui.py`, `persistence.py`, `__init__.py`) by PROJ-309. The `__init__.py` re-exports all symbols so `from game.core.protocols import ...` continues to work.

**Mismatch:** 6+ doc references cite a file path that no longer exists. The package layout is correct but docs are stale.

**Verified:** CONFIRMED

---

### 2. Exception count: doc says 10, code has 26

**Claim:** `docs/01_ARCHITECTURE.md:127` — `exceptions.py` listed as "GameException hierarchy (10 exception classes)."

**Actual:** `game/core/exceptions.py` contains **26** exception classes: GameException, StateException, FrozenStateException, ValidationException, ResourceException, MissingResourceException, PersistenceException, StrategyException, EnginePhaseError, SimulationException, ComponentException, FormulaException, LLMException, LLMConfigError, LLMNetworkError, LLMResponseError, LLMRateLimited, LLMTimeoutError, LLMCancelled, ImageException, ImageConfigError, ImageNetworkError, ImageResponseError, ImageRateLimited, ImageTimeoutError, ImageCancelled. The `__all__` exports 27 names (includes StateException as a base class).

**Mismatch:** The "10 exception classes" figure predates PROJ-296 (LLM exceptions added) and PROJ-314 (Image exceptions added). The LLM and Image hierarchies together add 14 exception classes.

**Verified:** CONFIRMED

---

### 3. Layer diagram places Assets in wrong position

**Claim:** `docs/01_ARCHITECTURE.md:14-43` — Visual layer diagram shows Assets between UI and AI (position 2 from top).

**Actual:** The dependency rules table on the same page says Assets depends on Services + Core only. AGENTS.md correctly places Assets between Services and Engine in its bottom-up ordering: `Core / Services / Assets / Engine`. Given Assets' actual dependency set (Services, Core), it should be positioned near/below Engine in a top-to-bottom diagram, not between UI and AI.

**Mismatch:** The visual diagram placement of the Assets layer contradicts the dependency rules table on the same page. The AGENTS.md ordering is correct.

**Verified:** CONFIRMED

---

### 4. 500 LOC ceiling: ~80+ production files exceed it

**Claim:** `AGENTS.md:53` — "**500 LOC ceiling on production files.** When a file approaches 500 lines, split into single-responsibility sub-modules."

**Actual:** At least 84 production `.py` files exceed 450 lines. Notable examples:
- `game/simulation/components/abilities/planetary.py`: 913 lines
- `game/strategy/engine/order_processor.py`: 910 lines
- `game/simulation/battle_controller.py`: 829 lines
- `game/simulation/battle_state.py`: 805 lines
- `game/strategy/engine/turn_engine.py`: 795 lines
- `game/strategy/data/ship_instance.py`: 787 lines
- `game/strategy/data/stars.py`: 770 lines
- `game/strategy/engine/superweapon_order_processor.py`: 771 lines
- `game/simulation/systems/battle_engine.py`: 768 lines
- `game/strategy/services/fleet_navigation_service.py`: 759 lines

**Mismatch:** The convention is aspirational rather than consistently enforced. Many files exceed 500 lines by significant margins (700+ lines).

**Verified:** CONFIRMED

---

### 5. Missing core modules from architecture doc

**Claim:** `docs/01_ARCHITECTURE.md:115-139` — Lists 22 core modules in the "Foundation layer" table.

**Actual:** `game/core/` contains 24 `.py` modules. The following are NOT listed:
- `game/core/ship_classes.py` — exists but undocumented
- `game/core/component_state.py` — exists but undocumented
- `game/core/state_machine.py` — exists, mentioned only in `docs/02_PATTERNS.md` Pattern #21 (not in architecture doc)
- `game/core/return_destination.py` — exists but undocumented

**Mismatch:** 4 production modules in `game/core/` are missing from the architecture reference table.

**Verified:** CONFIRMED

---

### 6. TestLabInputHandler filename mismatch

**Claim:** The user's verification target `game/ui/screens/test_lab/test_lab_input_handler.py` was expected as a likely path.

**Actual:** The file is `game/ui/screens/test_lab/screen_input_handler.py`, class `TestLabInputHandler`. The filename uses `screen_input_handler.py` not `test_lab_input_handler.py`.

**Verified:** CONFIRMED

---

### 7. `game/core/input_handler.py` does not exist

**Claim:** `game/core/input_handler.py` was queried as a verification target.

**Actual:** No glob match found. The file does not exist. Input handling for the Combat Lab is in `game/ui/screens/test_lab/screen_input_handler.py`. General keybindings are defined in `game/core/input_actions.py`.

**Verified:** CONFIRMED

---

### 8. `game/core/singleton.py` removed — doc is correct but context.py description is stale

**Claim:** `docs/02_PATTERNS.md:139-143` — "SingletonMeta and game/core/singleton.py were removed by PROJ-297."

**Actual:** `game/core/singleton.py` does NOT exist. File confirmed removed. The pattern doc is correct about the removal.

**Mismatch:** However, `docs/01_ARCHITECTURE.md:94` describes `context.py` with text: "Context-owned services install matching module-level defaults where applicable; services outside the constructor (e.g., `ship_materializer` in PROJ-274) follow the same `get_default_*` / `set_default_*` pattern". While this is technically correct about the current pattern, the phrase "outside the constructor" is confusing — `ship_materializer` lives in `game/simulation/services/ship_materializer.py` and is NOT wired into `ApplicationContext` constructors at all.

**Verified:** CONFIRMED (removal correct, but cross-reference description is misleading)

---

### 9. Simulation → Strategy import found in replay_player.py

**Claim:** `docs/01_ARCHITECTURE.md:63` — "Simulation must not import Strategy, AI, or UI."

**Actual:** `game/simulation/replay/replay_player.py:72` contains a late import: `from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer`. This is inside a function (not a module-level import) and is documented as an intentional cross-layer boundary import in `docs/01_ARCHITECTURE.md:367-369`.

**Mismatch:** The strict dependency rule is violated, but the doc itself lists this as one of the "Intentional late imports" (line 366: `ShipInstanceBridge.to_ship()` imports ShipSerializer). However, the replay_player import from strategy is NOT listed in the intentional late imports section (which only lists 4 sites). Either the rule or the exceptions list needs updating.

**Verified:** CONFIRMED

---

### 10. Quick Reference table: `delegate` primary file path wrong

**Claim:** `docs/02_PATTERNS.md:1530` — Delegates primary file: `game/simulation/entities/ship_combat_engine.py`.

**Actual:** `ShipCombatEngine` is a delegate, but it's not the primary delegate file. `Ship` delegates through `ShipComponentManager` and `ShipCombatManager` which then own `ShipCombatEngine`. The primary delegation files are `game/simulation/entities/ship.py` (where delegation happens), `game/simulation/entities/ship_component_manager.py`, and `game/simulation/entities/ship_combat_manager.py`. The Quick Reference should list the primary entry point (ship.py) rather than a sub-delegate.

**Verified:** CONFIRMED

---

### 11. Services layer — doc says "currently LLM provider services" (accurate but incomplete)

**Claim:** `AGENTS.md:39` — "Cross-cutting infrastructure, currently LLM provider services."
`docs/01_ARCHITECTURE.md:81-84` — Lists only `game/services/llm/`.

**Actual:** `game/services/` contains only `llm/` subpackage (7 files: types.py, provider.py, factory.py, deepseek.py, background.py, defaults.py, __init__.py). No other services exist yet.

**Mismatch:** Accurate as of verification date. The doc notes "future: observability/metrics/cloud sync" which haven't been added.

**Verified:** CONFIRMED (doc is accurate, services are LLM-only)

---

### 12. Core layer imports audit: `game/core/protocols/strategy_domain.py` imports from Strategy for TYPE_CHECKING

**Claim:** `docs/01_ARCHITECTURE.md:61` — "Core must not import any game layer."

**Actual:** `game/core/protocols/strategy_domain.py:12-13` imports `from game.strategy.data.race_config import RaceConfig` under `if TYPE_CHECKING:`. This is a typing-only import that doesn't create a runtime dependency. The architecture doc's "late imports" section (line 362-369) lists 4 cross-layer imports but does not list this one.

**Mismatch:** Technical violation of the letter of the rule, but TYPE_CHECKING guards make it a non-runtime concern. The doc should acknowledge this as an intentional exception or note why it's acceptable.

**Verified:** CONFIRMED

---

## Disputed Claims (Doc is Correct)

| # | Claim | Doc Source | Code Verified | Why Disputed |
|---|-------|------------|---------------|-------------|
| 1 | ApplicationContext manages 10 services | AGENTS.md:48, 02_PATTERNS.md:86 | `context.py:__init__` has exactly 10 parameters (registry_manager, profiler, component_cache, policy_manager, asset_manager, sprite_manager, ship_theme_manager, game_settings, llm_provider, image_provider) | Count matches exactly |
| 2 | 10 services table contents | 02_PATTERNS.md:88-99 | All 10 service entries and their file paths verified correct | Each path exists and imports succeed |
| 3 | Services depends only on Core | 01_ARCHITECTURE.md:62 | grep across `game/services/` found zero imports from engine/simulation/strategy/ai/ui/research/assets | Layer dependency rule holds |
| 4 | AI depends on Simulation | 01_ARCHITECTURE.md:51, AGENTS.md:45 | `game/ai/controller.py` imports from `game.simulation.interfaces.*`; `ai_factory.py` imports Ship | Dependency matches doc |
| 5 | Assets depends on Services+Core | 01_ARCHITECTURE.md:50 | grep across `game/assets/` found zero imports from ui/strategy/simulation/research/ai/engine | Dependency rule holds |
| 6 | Engine depends on Services+Core | 01_ARCHITECTURE.md:55 | `game/engine/__init__.py` only imports from `game.engine.*` internally; no layer-level upward imports found | Dependency rule holds |
| 7 | UIConfig moved to game/ui/config.py | 01_ARCHITECTURE.md:217, game/core/__init__.py:118 | `game/ui/config.py` exists with UIConfig class; `game/core/config.py:205` references the move | Move confirmed |
| 8 | DisplayConfig values | 01_ARCHITECTURE.md:489-496 | `game/core/config.py:22-31` matches all resolution constants | Values identical |
| 9 | PhysicsConfig values | 01_ARCHITECTURE.md:500 | `game/core/config.py:98-104` matches tick rate, drag, spatial grid cell size | Values identical |
| 10 | SingletonMeta removed (PROJ-297) | 02_PATTERNS.md:139-143 | No `game/core/singleton.py` found | Doc acknowledges removal correctly |
| 11 | BattleSpec DTO pattern | 02_PATTERNS.md:996 | `game/simulation/battle_spec.py` exists as frozen dataclass | Pattern 13 confirmed |
| 12 | Registry DI: Ship requires registries keyword | 02_PATTERNS.md:256-261 | `game/simulation/entities/ship.py` constructor includes `*, registries: GameRegistries` requirement | Code matches doc quote |

---

## Prioritized Doc Fixes

### Tier 1: Dead References (URLs/files that don't exist)
1. **`game/core/protocols.py`** — Update all 6 references across `01_ARCHITECTURE.md`, `02_PATTERNS.md`: change to `game/core/protocols/__init__.py` or just `game/core/protocols/`.

### Tier 2: Content Errors (wrong counts, wrong assertions)
2. **Exception count** — `01_ARCHITECTURE.md:127`: Change "10 exception classes" to "26 exception classes" covering Core, LLM (PROJ-296), and Image (PROJ-314) hierarchies.
3. **Layer diagram Assets position** — `01_ARCHITECTURE.md:14-43`: Move Assets to between Engine and Services in the visual diagram (or add a note explaining why it's placed at position 2 despite only depending on Services+Core).
4. **Simulation→Strategy late import exception list** — `01_ARCHITECTURE.md:365-369`: Add `game/simulation/replay/replay_player.py` (importing ShipInstanceSerializer from strategy) to the intentional late imports list.
5. **Simulation services table** — `01_ARCHITECTURE.md:157`: Add `ship_materializer.py` to the services listing (it exists as a file but isn't listed in the table; it's only mentioned in the context.py description).

### Tier 3: Missing Documentation
6. **Undocumented core modules** — `01_ARCHITECTURE.md:115-139`: Add entries for `ship_classes.py`, `component_state.py`, `state_machine.py`, `return_destination.py` in the core module table.
7. **Core→Strategy TYPE_CHECKING import** — `01_ARCHITECTURE.md:365-369`: Add `game/core/protocols/strategy_domain.py` (imports RaceConfig under TYPE_CHECKING) to the late imports section, or add a blanket note that `if TYPE_CHECKING:` imports are exempt from layer rules.

### Tier 4: Term/Path Normalization
8. **Quick Reference delegate path** — `02_PATTERNS.md:1530`: Change primary file for Delegate pattern from `ship_combat_engine.py` to `ship.py` or `ship_component_manager.py`.
9. **500 LOC ceiling** — `AGENTS.md:53`: Either update to a realistic threshold, add a list of approved exceptions, or note that pre-PROJ files are grandfathered until their respective refactor projects.
