# Documentation Consistency Review: Strategy Layer

**Date:** 2026-04-05
**Scope:** `game/strategy/` code vs all strategy-related documentation in `docs/`
**Reviewer:** Claude Opus 4.6 (automated)

---

### Summary
- Total issues found: 18
- Critical: 1, Major: 5, Minor: 8, Info: 4

---

### Findings

#### MAJOR: Orders system doc still uses FleetOrder everywhere; should use Order
**ID:** DOCC-001
**Location:** `docs/systems/orders_system.md` (lines 17, 37-44, 186, 364, 387, 410)
**Issue:** The orders_system.md doc refers to the class as `FleetOrder` throughout (data structure section, lifecycle diagram, code examples, key files table, design rationale). However, per PROJ-238 and `docs/03_CONVENTIONS.md` section 1.8, `FleetOrder` was renamed to `Order`. The actual code at `game/strategy/data/order_types.py:73` defines `class Order`, with `FleetOrder = Order` as a backward-compat alias on line 170.
**Impact:** Agents/developers following the orders doc will use the deprecated alias name in new code, violating the conventions doc.
**Recommendation:** Update `orders_system.md` to use `Order` everywhere. Keep a note that `FleetOrder` is a legacy alias.
**Effort:** Simple

#### MAJOR: Orders system doc missing ACTIVATE_ABILITY and DEACTIVATE_ABILITY order types
**ID:** DOCC-002
**Location:** `docs/systems/orders_system.md` -- "Order Type Categories" section
**Issue:** The code at `game/strategy/data/order_types.py:36-37` defines `ACTIVATE_ABILITY` and `DEACTIVATE_ABILITY` order types and includes them in `ACTION_ORDER_TYPES` (line 63) and a dedicated `PLANET_ACTION_ORDER_TYPES` set (line 67-69). The orders doc does not mention these order types at all -- they are absent from the Action Orders table and from all category listings.
**Impact:** The orders doc gives an incomplete picture of the order system. Anyone adding planet orders or trying to understand the full order lifecycle will miss planet-specific ability orders.
**Recommendation:** Add ACTIVATE_ABILITY and DEACTIVATE_ABILITY to the Action Orders table in orders_system.md. Also document the `PLANET_ACTION_ORDER_TYPES` subset.
**Effort:** Simple

#### MAJOR: Turn engine has undocumented post-loop phases (QualityEngine, AtmosphereEngine)
**ID:** DOCC-003
**Location:** `game/strategy/engine/turn_engine.py:381-384` vs `docs/systems/strategy_layer.md` section 3
**Issue:** After the 100-tick loop and population growth, the turn engine runs two additional post-loop phases: `QualityEngine.process_quality_improvement(empires)` and `AtmosphereEngine.process_atmosphere(empires)`. Neither engine is mentioned in `docs/systems/strategy_layer.md` section 3 (Turn Engine), the sub-engine interfaces table, or the per-tick phase table. They also have no entries in `docs/01_ARCHITECTURE.md`.
**Impact:** The turn phase documentation is incomplete. Agents will not account for quality improvement or atmosphere modification when reasoning about turn processing order.
**Recommendation:** Add QualityEngine and AtmosphereEngine to the strategy_layer.md Turn Engine section as post-loop phases. Add their files to 01_ARCHITECTURE.md engine listing.
**Effort:** Simple

#### MAJOR: SetAtmosphereTargetCommand handler not documented in command table
**ID:** DOCC-004
**Location:** `docs/systems/strategy_layer.md` section 2 "Registered Handlers" table
**Issue:** The code registers `SetAtmosphereTargetCommand` -> `SetAtmosphereTargetCommandHandler` at `command_handlers.py:1060`, imported from `planet_command_handlers.py`. This command is absent from the Registered Handlers table in the docs. The file `planet_command_handlers.py` is also not mentioned anywhere in the docs.
**Impact:** Incomplete command reference; agents won't know this command exists when working with atmosphere features.
**Recommendation:** Add SetAtmosphereTargetCommand to the Registered Handlers table. Also mention `planet_command_handlers.py` as a handler source file.
**Effort:** Simple

#### MAJOR: Command names in docs use stale PROJ-238 pre-rename names
**ID:** DOCC-005
**Location:** `docs/systems/strategy_layer.md` section 2 "Registered Handlers" table
**Issue:** The docs list `ClearFleetOrdersCommand`, `DeleteFleetOrderCommand`, and `ReorderFleetOrderCommand` as the primary command names. In code, these are now backward-compat aliases. The primary names are `ClearOrdersCommand` (`commands.py:89`), `DeleteOrderCommand` (`commands.py:277`), and `ReorderOrderCommand` (`commands.py:292`). The compat aliases are registered in `create_default_registry()` but are secondary.
**Impact:** New code following docs will use the old alias names instead of the canonical names. While both work, this contradicts the conventions doc section 1.8 which says old aliases have been deleted (they have not been deleted from the registry, only from import modules).
**Recommendation:** Update the command table to list the new canonical names as primary, with a note about the compat aliases.
**Effort:** Simple

#### CRITICAL: Turn engine module docstring missing 4 phases that exist in code
**ID:** DOCC-006
**Location:** `game/strategy/engine/turn_engine.py:1-23` (module docstring)
**Issue:** The module-level docstring lists phases but is missing:
  - Phase 0c1: PlanetEnergyEngine (exists in code at line 458)
  - Phase 0f: EnvironmentalHazardEngine (exists in code at line 470)
  - Phase 1.6: PlanetActionEngine (exists in code at line 483)
  - Post-loop: QualityEngine + AtmosphereEngine (exists in code at lines 381-384)
The `_process_tick` method docstring (line 432) is also missing Phase 1.6 (PlanetActionEngine) despite the code executing it at line 483.
**Impact:** Internal code documentation is out of sync with actual behavior. This is the primary reference developers see when opening the file. Missing phase documentation means debugging turn processing order will be confusing.
**Recommendation:** Update both the module docstring and the `_process_tick` docstring to include all phases.
**Effort:** Simple

#### MINOR: __init__.py exports FleetOrder alias not listed in docs
**ID:** DOCC-007
**Location:** `game/strategy/__init__.py:64` vs `docs/01_ARCHITECTURE.md:190`
**Issue:** The `__init__.py` exports 16 items including `FleetOrder` as a backward-compat alias. The docs say "16 exports" but only list 15 items (they omit `FleetOrder`). The count is coincidentally correct because of the alias, but the explicit list is incomplete.
**Impact:** Minor -- the docs don't mention the FleetOrder alias export. This is consistent with conventions saying old aliases should be deleted, but the code still exports it.
**Recommendation:** Either remove the FleetOrder export from `__init__.py` (preferred per conventions) or add it to the docs with a deprecation note.
**Effort:** Simple

#### MINOR: Strategy_layer.md __init__.py docstring still refers to FleetOrder
**ID:** DOCC-008
**Location:** `game/strategy/__init__.py:11` docstring
**Issue:** The package docstring says `OrderType, FleetOrder - Fleet movement orders` but should say `OrderType, Order - Entity orders (fleet and planet)` per the PROJ-238 rename.
**Impact:** Minor misleading documentation in the package docstring.
**Recommendation:** Update the docstring to reference `Order` instead of `FleetOrder`.
**Effort:** Simple

#### MINOR: Conventions doc section 1.8 claims old backward compatibility alias modules deleted, but __init__.py still exports FleetOrder
**ID:** DOCC-009
**Location:** `docs/03_CONVENTIONS.md:134-135` vs `game/strategy/__init__.py:34,64` and `game/strategy/data/order_types.py:170`
**Issue:** Conventions doc says "Old backward compatibility alias modules have been deleted. All code must use the new names and import paths directly." However, `game/strategy/__init__.py` still imports and exports `FleetOrder` with the comment "FleetOrder alias for compat", and `order_types.py:170` still defines `FleetOrder = Order`. Additionally, `command_handlers.py` registers `ClearFleetOrdersCommand`, `DeleteFleetOrderCommand`, and `ReorderFleetOrderCommand` as compat aliases.
**Impact:** The conventions doc overstates the completeness of the migration.
**Recommendation:** Either complete the migration by removing all compat aliases, or soften the conventions doc language to acknowledge remaining aliases.
**Effort:** Medium (removing aliases requires auditing all call sites)

#### MINOR: Several data files in game/strategy/data/ not documented anywhere
**ID:** DOCC-010
**Location:** `game/strategy/data/` -- multiple files
**Issue:** The following files exist in `game/strategy/data/` but are not mentioned in any documentation:
  - `planet_atmosphere.py` -- Planet atmosphere system
  - `species_population.py` -- Species population modeling
  - `fleet_pursuer_tracker.py` -- Fleet pursuit tracking
  - `build_context.py` -- Build context data
  - `design_metadata.py` -- Design metadata
  - `race_config.py` -- Race configuration
  - `race_point_budget.py` -- Race point budget system
  - `planet_physics.py` -- Planet physics calculations
  - `planet_naming.py` -- Planet naming system
  - `homeworld_presets.py` -- Homeworld preset data
  - `naming.py` -- General naming utilities
**Impact:** These files represent undocumented subsystems. Agents discovering them won't have architectural context.
**Recommendation:** Add brief entries for these files to `docs/01_ARCHITECTURE.md` strategy data section.
**Effort:** Medium

#### MINOR: engine/empire_economy_calculator.py not documented
**ID:** DOCC-011
**Location:** `game/strategy/engine/empire_economy_calculator.py`
**Issue:** This engine file exists but is not mentioned in `docs/01_ARCHITECTURE.md` or `docs/systems/strategy_layer.md`. It's not listed as a sub-engine of TurnEngine.
**Impact:** Undocumented engine module.
**Recommendation:** Add to the architecture docs engine listing.
**Effort:** Simple

#### MINOR: strategy_layer.md DTO list missing FleetOrderInfo, ShipInfo, WarpPointInfo
**ID:** DOCC-012
**Location:** `docs/systems/strategy_layer.md` section 1 "DTO types" vs `game/strategy/facade/dto/__init__.py`
**Issue:** The DTO `__init__.py` exports `FleetOrderInfo`, `ShipInfo`, `WarpPointInfo` in addition to the DTOs listed in the docs. The docs list FleetInfo, FleetSummary, StarInfo, SystemInfo, PlanetInfo, EmpireInfo, ColonySummary but omit FleetOrderInfo, ShipInfo, and WarpPointInfo.
**Impact:** Incomplete DTO reference.
**Recommendation:** Add the missing DTOs to the strategy_layer.md DTO types list.
**Effort:** Simple

#### MINOR: star_image_registry.py in generation/ not documented
**ID:** DOCC-013
**Location:** `game/strategy/generation/star_image_registry.py`
**Issue:** The strategy_layer.md generation pipeline section mentions `PlanetImageRegistry` but not `StarImageRegistry`, which exists at `game/strategy/generation/star_image_registry.py`.
**Impact:** Minor documentation gap in the generation pipeline.
**Recommendation:** Add StarImageRegistry to the generation pipeline documentation.
**Effort:** Simple

#### INFO: orders_system.md "Adding a New Order Type" section uses FleetOrder in examples
**ID:** DOCC-014
**Location:** `docs/systems/orders_system.md` lines 364-365
**Issue:** The "Adding a New Order Type" tutorial section uses `FleetOrder` in code examples: `order = FleetOrder(OrderType.YOUR_NEW_ORDER, target=...)`. Should use `Order` per the rename.
**Impact:** Tutorial code will teach the deprecated name.
**Recommendation:** Update code examples to use `Order`.
**Effort:** Simple

#### INFO: strategy_layer.md TurnEngine docstring example shows no registries parameter
**ID:** DOCC-015
**Location:** `docs/systems/strategy_layer.md` section 3, turn_engine.py module docstring line 43
**Issue:** The module docstring example shows `engine = TurnEngine()` without `registries=` keyword argument, but `registries` is a required keyword-only parameter (line 111). The docs section 3 correctly shows `engine = TurnEngine(registries=registries)`.
**Impact:** The module docstring example would fail at runtime. The external docs are correct.
**Recommendation:** Fix the module docstring example to include `registries=registries`.
**Effort:** Simple

#### INFO: orders_system.md Key Files table lists FleetOrder class separately
**ID:** DOCC-016
**Location:** `docs/systems/orders_system.md` line 387
**Issue:** The Key Files table has a row "FleetOrder class | game/strategy/data/order_types.py" -- should be "Order class".
**Impact:** Stale naming in the reference table.
**Recommendation:** Rename to "Order class".
**Effort:** Simple

#### INFO: Production system doc mentions 6 planetary complex components but components.json may have more
**ID:** DOCC-017
**Location:** `docs/systems/production_system.md` section "Planetary Complex Components"
**Issue:** The doc lists 6 components restricted to Planetary Complex. This should be verified against the actual `data/components.json` to ensure no new complex-only components have been added (e.g., planetary shield generator, atmosphere processor, stabilizer). Given the existence of `PlanetaryShieldAbility` and atmosphere features in the codebase, there are likely additional complex components not listed.
**Impact:** If additional complex components exist, the docs provide an incomplete list.
**Recommendation:** Audit `data/components.json` for all components with `allowed_vehicle_types: ["Planetary Complex"]` and update the doc.
**Effort:** Simple

#### MINOR: Facade query method table in strategy_layer.md is incomplete
**ID:** DOCC-018
**Location:** `docs/systems/strategy_layer.md` section 1 "Query Categories" table
**Issue:** The facade's Game State category lists `get_turn_number()`, `get_human_player_ids()`, `get_save_path()` but the code has `get_save_path()` at line 529. The table does include `get_save_path()` so that is fine. However, `get_system_containing_fleet()` (line 225) is not listed in the System category table -- only `get_all_systems()`, `get_all_stars()`, `get_system_at_hex()`, `get_system_near_hex()` are listed. The code also has `get_system_containing_fleet()`.
**Impact:** Minor incomplete query reference.
**Recommendation:** Add `get_system_containing_fleet()` to the System query category.
**Effort:** Simple

---

### Top 5 Priority Issues

1. **DOCC-006 (CRITICAL):** Turn engine module docstring missing 4 phases -- direct code documentation is wrong and will mislead anyone reading the source file. Fix immediately.

2. **DOCC-003 (MAJOR):** QualityEngine and AtmosphereEngine completely undocumented in all docs -- two entire post-loop phases invisible to the documentation. Add to strategy_layer.md and architecture docs.

3. **DOCC-002 (MAJOR):** ACTIVATE_ABILITY/DEACTIVATE_ABILITY order types missing from orders doc -- the planet order system is silently undocumented in the orders reference.

4. **DOCC-001 (MAJOR):** Orders system doc pervasively uses FleetOrder instead of Order -- contradicts conventions doc and teaches the deprecated name.

5. **DOCC-004/005 (MAJOR):** SetAtmosphereTargetCommand and renamed command names missing/stale in command table -- the command registry documentation is incomplete and uses outdated names.
