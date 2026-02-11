# PROJ-78: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-08 | Project initialized | Starting point for Quickstart Initial Complexes |
| 2026-02-08 | Pre-built complexes (operational at turn 1) | User preference - quickstart should be immediately playable |
| 2026-02-08 | Resupply depot includes generator + storage | User preference - fuel_synthesizer (300/turn) + fuel_tank (50k) enables fleet resupply |
| 2026-02-08 | Use Tier 1 for all complexes except exotics | User preference - keep complexes small to match existing qs_complex |
| 2026-02-08 | Use Tier 2 for exotics complex only | User choice - exotics exceeds Tier 1 mass limit (1040 kg > 1000 kg) |
| 2026-02-08 | Spawn complexes via QuickstartBuilder method | Option B chosen - spawn after designs copied using DesignLibrary (cleanest approach) |
| 2026-02-08 | 7 total complexes per home planet | shipyard + 5 resource harvesters + fuel depot = complete starting infrastructure |

## Detailed Rationale

### Why Pre-built Instead of In-Queue?
The purpose of quickstart is to get players into the game immediately. Having to wait several turns for basic infrastructure would defeat the purpose of the quickstart mode.

### Why Generator + Storage for Resupply?
The `ResupplyEngine` already exists and handles fleet resupply from facilities with fuel storage. By including both a generator (fuel_synthesizer) and storage (fuel_tank), ships can refuel at the home planet depot. The resupply depot will:
1. Generate 300 fuel per turn
2. Store up to 50,000 fuel
3. Automatically distribute fuel to fleets at the planet

### Why Tier 2 for Exotics?
Mass budget calculation:
- central_complex_command: 50 kg
- 6x crew_quarters: 180 kg (60 crew needed)
- 3x life_support: 60 kg (75 capacity for 60 crew)
- exotic_harvester: 250 kg
- resource_vault_exotics: 500 kg
- **Total: 1040 kg** (exceeds Tier 1's 1000 kg limit)

Alternatives considered:
1. Remove vault - player loses storage, defeats purpose
2. Reduce crew - would cause operational issues
3. Use Tier 2 - **chosen** - slightly larger complex but fully functional
