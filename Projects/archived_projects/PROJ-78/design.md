# PROJ-78: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Complex System Architecture
- Complexes are JSON design files stored in `tests/fixtures/quickstart/designs/`
- They use the standard ship component system with layers (CORE, INNER, OUTER, ARMOR)
- Complexes become `PlanetaryFacility` instances when added to planets
- `PlanetaryFacility` dataclass is in `game/strategy/data/planet.py` (lines 24-94)

### Quickstart Flow
1. `app.py._start_quickstart()` creates GameConfig via QuickstartBuilder
2. Creates `GameSession` which calls `_setup_initial_scenario()` (home planet setup)
3. Saves game via `SaveGameService.save_game()`
4. Copies designs via `QuickstartBuilder.copy_quickstart_designs()`
5. **Gap:** No initial complexes are spawned on home planets

### Available Components (from data/components.json)

**Harvesters (ResourceHarvester ability):**
| Component | Mass | Crew | Rate |
|-----------|------|------|------|
| metal_harvester | 200 | 20 | 100/turn |
| organic_harvester | 200 | 20 | 100/turn |
| vapor_harvester | 200 | 20 | 100/turn |
| radioactive_harvester | 200 | 25 | 50/turn |
| exotic_harvester | 250 | 30 | 25/turn |

**Storage Vaults (EmpireStorage ability):**
| Component | Mass | Crew | Capacity |
|-----------|------|------|----------|
| resource_vault_metals | 300 | 10 | 10,000 |
| resource_vault_organics | 300 | 10 | 10,000 |
| resource_vault_vapors | 300 | 10 | 10,000 |
| resource_vault_radioactives | 400 | 15 | 5,000 |
| resource_vault_exotics | 500 | 20 | 2,500 |

**Fuel System:**
| Component | Mass | Crew | Function |
|-----------|------|------|----------|
| fuel_synthesizer | 100 | 10 | Generates 300 fuel/turn |
| fuel_tank | 40 | 0 | Stores 50,000 fuel |

## Swarm Findings Summary

### Architecture
- **Option B chosen:** Spawn complexes in `QuickstartBuilder.spawn_initial_complexes()` after designs are copied
- Called from `app.py._start_quickstart()` after `copy_quickstart_designs()`
- Uses `DesignLibrary` to load design data (standard pattern)
- Creates `PlanetaryFacility` instances following `ProductionEngine._spawn_complex()` pattern

### Key Patterns to Reuse
- **Facility Creation**: `game/strategy/engine/production_engine.py:239-280` - `_spawn_complex()` method
- **Design Loading**: `game/strategy/systems/design_library.py` - `DesignLibrary.load_design_data()`
- **Complex JSON Format**: `tests/fixtures/quickstart/designs/qs_complex.json` - template for new designs

### Dependencies & Risks
1. **Tier 1 mass budget exceeded by exotics** - Mitigated by using Tier 2 for exotics complex only
2. **Designs must exist before spawning** - Designs copied first, then spawning occurs

### Opportunities Discovered
- Resupply system already exists (`game/strategy/engine/resupply_engine.py`) - fleet resupply will work automatically once fuel depot has fuel

## Mass Budget Calculations

### Tier 1 Complexes (1000 kg budget)

| Complex | Components | Total Mass | Crew Needed |
|---------|------------|------------|-------------|
| qs_metals_complex | cmd + 4 crew + 2 life + harvester + vault | 710 kg | 40 |
| qs_organics_complex | cmd + 4 crew + 2 life + harvester + vault | 710 kg | 40 |
| qs_vapors_complex | cmd + 4 crew + 2 life + harvester + vault | 710 kg | 40 |
| qs_radioactives_complex | cmd + 5 crew + 2 life + harvester + vault | 840 kg | 50 |
| qs_resupply_depot | cmd + 2 crew + 1 life + synth + tank | 270 kg | 20 |

### Tier 2 Complex (2000 kg budget)

| Complex | Components | Total Mass | Crew Needed |
|---------|------------|------------|-------------|
| qs_exotics_complex | cmd + 6 crew + 3 life + harvester + vault | 1040 kg | 60 |

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
