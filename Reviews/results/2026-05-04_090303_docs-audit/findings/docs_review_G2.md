# Documentation Review: System Reference Docs
## Summary
- Group: System Reference Docs
- Docs in Scope: 8
- Docs Actually Read: 8
- Total Findings: 21
- Critical: 1 | Major: 6 | Minor: 14

## Dead Reference Findings

### CRITICAL: strategy_layer.md:680 — Dead file reference to `game/core/protocols.py`
- **File:** `docs/systems/strategy_layer.md`, line 680
- **Doc says:** "Both Fleet and Planet implement the `IOrderable` protocol (`game/core/protocols.py`)"
- **Reality:** `game/core/protocols.py` does NOT exist. It was refactored into `game/core/protocols/` (a directory with modules: `strategy_entities.py`, `common.py`, `boundary.py`, `combat.py`, `persistence.py`, `registry.py`, `strategy_domain.py`, `ui.py`, `__init__.py`). The import `from game.core.protocols import IOrderable` still works because Python resolves the package, but the file-path reference `game/core/protocols.py` is stale.
- **Fix:** Change to `game/core/protocols/strategy_entities.py` or simply `game/core/protocols/` (directory).

## Stale PROJ Reference Findings

### MINOR: orders_system.md:5 — PROJ-187 is archived
- **Context:** `> **PROJ-187**: Strategy Orders Tick-Based Action System`
- **Status:** PROJ-187 is in `Projects/deep_archive/PROJ-151-200/PROJ-187/`. Used as historical context for the orders system foundation; functionally accurate since it describes a shipped feature. Not stale content — just an archived project reference.

### MINOR: strategy_layer.md:672 — PROJ-238 is archived
- **Context:** Mentions "PROJ-238: Unified" for the Order class rename. PROJ-238 is in deep_archive.
- **Verdict:** Historical context, not stale content. Feature described IS implemented.

### MINOR: strategy_layer.md:190 — PROJ-253 is archived
- **Context:** Mentions PlanetEnergyEngine caching. PROJ-253 is in deep_archive.
- **Verdict:** Historical context, not stale. Feature described IS implemented.

### MINOR: PROJ references with "unknown" scanner status — non-blocking
- The deterministic scanner flagged 34 PROJ references across systems docs as "unknown" status. After manual review, all appear in deep_archive (closed) or active_projects. No PROJ reference describes a planned feature that has already shipped — the docs under this group are well-maintained for PROJ accuracy.

## Content Accuracy Findings

### MAJOR: combat_simulation.md:867 — Stale ability class names in `planetary.py` row
- **Doc lists:** `planetary.py | PlanetaryShieldAbility, PlanetaryEnergyGeneratorAbility, PlanetaryEnergyStorageAbility`
- **Reality:** `PlanetaryEnergyGeneratorAbility` and `PlanetaryEnergyStorageAbility` no longer exist. They were removed by PROJ-238 (replaced by `StrategicResourceGeneration` and reuse of combat `ResourceStorage`). The `ability_reference.md` doc correctly documents this removal, but `combat_simulation.md` was not updated.
- **Fix:** Replace `PlanetaryEnergyGeneratorAbility, PlanetaryEnergyStorageAbility` with the current abilities in `planetary.py`: `PlanetaryShieldAbility, StrategicResourceGenerationAbility, GeologicStabilizerAbility, StellarStabilizerAbility, WarpFieldStabilizerAbility, ResourceHarvestBoosterAbility, BuildRateBoosterAbility, AtmosphereModifierAbility, QualityImprovementAbility, ShieldModifierAbility, DamageModifierAbility, GravityModifierAbility, WaterModifierAbility, RadiationShieldAbility`

### MAJOR: combat_simulation.md:865 — Incomplete `harvester.py` ability list
- **Doc lists:** `harvester.py | ResourceHarvesterAbility, LocalStorageAbility, SpaceShipyardAbility`
- **Missing:** `StagingYardAbility` and `PlanetaryYardAbility` — both ARE defined in `game/simulation/components/abilities/harvester.py` and registered in `ABILITY_REGISTRY`.
- **Fix:** Add `StagingYardAbility, PlanetaryYardAbility` to the harvester.py row.

### MAJOR: combat_simulation.md:864 — `SuperweaponMarker` not listed for `superweapons.py`
- **Doc lists:** `DestroyPlanet, DestroyStar, OpenWarpPoint, CloseWarpPoint, CreateDysonSphere, SelfDestruct`
- **Missing:** `SuperweaponMarker` — a real class in `superweapons.py`, registered in `ABILITY_REGISTRY`. It exists but is absent from the ability categories table.

### MAJOR: ability_reference.md:773 — `PodStorage` has no ability class
- **Doc says:** `Class: PodStorageAbility` (line 773), listed in quick reference as `| PodStorage | PodStorageAbility |`
- **Reality:** `PodStorageAbility` does NOT exist as a Python class. The `ship_stats.py` file confirms at line 373: `# PodStorage has no ability class — read from raw abilities dict`. The ability IS in `components.json` data, but it is NOT registered in `ABILITY_REGISTRY` — it's read directly from the raw `comp.abilities` dict. There is no `PodStorageAbility` class in `cargo.py` or anywhere else.
- **Fix:** Either update the doc to note that `PodStorage` has no Python class (raw dict access from `cargo.py`), or implement the class.

### MINOR: ability_reference.md quick reference — Missing 4 strategic abilities
- The quick reference table (Registry Key → Class, lines 1529-1586) omits `EnvironmentalDamage`, `FuelDrain`, `StrategicSpeedModifier`, and `ThrustModifier`. These ARE documented in the PROJ-300..305 section at the bottom of the doc (lines 1637-1697), but they are not in the main quick-reference registry key table.
- **Fix:** Add rows for these 4 ability keys to the quick reference table, pointing to the PROJ-300..305 section for details.

### MINOR: ability_reference.md:1126 — Misplaced size-mount scaling note
- Line 1126 under `GeologicStabilizer` has: "Size mount scaling: Production rates from `production_rates.json` are multiplied by the PlanetaryYard component's `simple_size_mount` value at runtime."
- This note appears to belong to `SpaceShipyard` or `PlanetaryYard`, not `GeologicStabilizer` (which has no production rates). It reads like a copy-paste artifact.

## Code Example Issues

### MINOR: ai_system.md:195-200 — Code example uses `get_default_policy_manager` singleton pattern
- **Doc code:** `pm = get_default_policy_manager()` and `pm.get_targeting_policy(...)`, `pm.get_movement_policy(...)`
- **Status:** Function calls exist but use the singleton accessor pattern. The doc correctly notes that `PolicyManager` is "managed by ApplicationContext", but the code example shows the `get_default_*` singleton pattern. This is inconsistent with the documented architecture (ApplicationContext DI). Not a doc bug per se — the singleton pattern matches current implementation — but the architecture doc section says "Service (managed by ApplicationContext)" while the code example bypasses the context.

### MINOR: strategy_layer.md:76-78 — `ICommandHandler` protocol signature uses `Command`
- The protocol signature `def execute(self, session: GameSession, command: Command) -> ValidationResult` uses `Command` directly. This is consistent with the live code so no issue — verified working.

## Missing Documentation

The following production modules have zero mention across all 8 system docs under review. The deterministic scanner flagged them as undocumented; manual grep confirms no doc references exist.

### Entirely undocumented modules (no class name or file path in any doc):

| Module | LOC | Description (from code structure) |
|--------|-----|-----------------------------------|
| `game/strategy/systems/save_game_service.py` | 519 | Save/load game persistence service — largest undocumented module |
| `game/strategy/validation/superweapon_validator.py` | 270 | Superweapon target validation logic |
| `game/simulation/entities/ship_component_manager.py` | 293 | Ship component lifecycle management |
| `game/simulation/managers/retreat_manager.py` | 280 | Combat retreat mechanics |
| `game/strategy/validation/transfer_validator.py` | 246 | Resource/population transfer validation |
| `game/simulation/systems/tech_preset_loader.py` | 203 | Tech preset loading for combat scenarios |
| `game/simulation/projectile_manager.py` | 187 | Projectile lifecycle (creation, movement, cleanup) |
| `game/simulation/entities/ship_combat_manager.py` | 184 | Ship combat state management |
| `game/simulation/entities/ship_loader.py` | 174 | Ship deserialization/loading |
| `game/simulation/entities/combat_endurance.py` | 155 | Combat endurance/attrition tracking |
| `game/strategy/validation/colonize_validator.py` | 143 | Colonization validation rules |
| `game/simulation/managers/battle_state_manager.py` | 134 | Battle state tracking and transitions |
| `game/simulation/physics_constants.py` | 72 | Physics constants (speed scales, mass thresholds) |

### Partially documented (class mentioned, no file path):
| Module | LOC | Where class is mentioned |
|--------|-----|-------------------------|
| `game/strategy/engine/planet_action_engine.py` | 387 | `PlanetActionEngine` referenced in strategy_layer.md turn engine table |
| `game/strategy/engine/resupply_engine.py` | 294 | `ResupplyEngine` referenced in strategy_layer.md turn engine table |
| `game/strategy/engine/consumable_management_engine.py` | 164 | `ConsumableManagementEngine` referenced in strategy_layer.md turn engine table |

### Recommendation:
- `save_game_service.py` (519 LOC) is the most critical gap — it's a major subsystem with zero doc coverage.
- `retreat_manager.py` (280 LOC) and `ship_component_manager.py` (293 LOC) are simulation-layer modules that deserve at minimum a subsection in `combat_simulation.md`.
- The 3 partially-documented engines should get file path entries in the "Key Files" table of `strategy_layer.md`.

## Doc File Coverage Verification

| Doc File | Status | Findings |
|----------|--------|----------|
| `ability_reference.md` (1697 LOC) | Read | MAJOR: PodStorageAbility class doesn't exist (raw dict); MINOR: missing 4 strategic abilities in quick-reference, misplaced size-mount note |
| `ai_system.md` (311 LOC) | Read | MINOR: oldest Last verified date (2026-04-11); code example uses singleton pattern vs documented DI |
| `combat_simulation.md` (1187 LOC) | Read | MAJOR: 2 stale ability class names (PlanetaryEnergyGenerator/Storage), incomplete harvester.py list, missing SuperweaponMarker; 13 undocumented simulation modules noted |
| `orders_system.md` (502 LOC) | Read | MINOR: PROJ-187 archived reference (historical, not stale) |
| `production_system.md` (377 LOC) | Read | No issues found |
| `research_system.md` (214 LOC) | Read | No issues found |
| `resource_system.md` (242 LOC) | Read | No issues found |
| `strategy_layer.md` (1794 LOC) | Read | CRITICAL: dead file ref to `game/core/protocols.py` (line 680); MINOR: PROJ-238/253 archived; 3 partially undocumented engines; 1 fully undocumented module (save_game_service.py) |

## Spatial Terminology Audit

All 8 docs use "System" (star system) and "Sector" (single hex) consistent with AGENTS.md definitions. The `AbilityScope` enum documentation in `ability_reference.md` correctly distinguishes SYSTEM scope (star-system-wide) from SECTOR scope (single-hex). No spatial terminology issues found.

## "Last Verified" Timestamps

| Doc File | Last Verified |
|----------|--------------|
| `ability_reference.md` | 2026-04-28 |
| `ai_system.md` | 2026-04-11 |
| `combat_simulation.md` | 2026-05-02 |
| `orders_system.md` | 2026-04-28 |
| `production_system.md` | 2026-04-27 |
| `research_system.md` | 2026-03-14 |
| `resource_system.md` | 2026-03-31 |
| `strategy_layer.md` | 2026-05-02 |

- `research_system.md` (2026-03-14) is the stalest — nearly 7 weeks old. However, the research system is known to be stable with minimal changes.
- `ai_system.md` (2026-04-11) is ~3 weeks old.
- All docs have "Last verified" lines — none are missing. Format is consistent (YYYY-MM-DD).
