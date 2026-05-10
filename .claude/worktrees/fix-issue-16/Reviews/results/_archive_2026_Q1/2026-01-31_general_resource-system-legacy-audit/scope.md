# Review Scope: Resource System Legacy Audit

## Metadata
- **Date:** 2026-01-31 20:52
- **Type:** General Review (Targeted Audit)
- **Description:** Identify all legacy/hardcoded resource system usage for migration planning

## Objective
Find ALL references to legacy/hardcoded resource management patterns to enable migration to the generic `ResourceConsumption` ability system.

## Target Patterns

### Primary Search Terms (Exact Matches)
- `"Energy Storage"` / `EnergyStorage`
- `"EnergyGeneration"` / `EnergyGeneration`
- `"Fuel Storage"` / `FuelStorage`
- `"AmmoGeneration"` / `AmmoGeneration`
- `"EnergyConsumption"` / `EnergyConsumption`

### Secondary Patterns (Hardcoded Resource Logic)
- `fuel_consumption`, `fuel_cost`, `fuel_usage`
- `ammo_count`, `ammo_consumption`, `ammo_usage`
- `energy_cost`, `energy_usage`, `energy_drain`
- Direct attribute access: `.energy`, `.fuel`, `.ammo` (context-dependent)
- Resource deduction logic outside ability system
- Hardcoded resource checks in combat/movement code

## Scope Boundaries

### Target (Entire Codebase)
- [x] Entire codebase

| Area | File Count | Notes |
|------|------------|-------|
| game/ | ~266 files | All runtime code |
| tests/ | ~656 files | All test files |
| simulation_tests/ | ~26 files | Combat lab tests |
| data/*.json | ~24 files | Config files |
| ships/*.json | Ship definitions | Component configs |

### Exclusions
- Correct usage of `ResourceConsumption` ability pattern (ignore these)
- Third-party libraries
- Generated files

## Agent Configuration
**Recommended Agents:** 12 (Large scope - ~970 files)
**Confirmed Agent Count:** 12

### Selected Agents
| Agent | Role | Focus Area |
|-------|------|------------|
| Energy-Storage-Hunter | Pattern Hunter | "Energy Storage" patterns in code and JSON |
| Energy-Gen-Hunter | Pattern Hunter | "EnergyGeneration" patterns |
| Fuel-Storage-Hunter | Pattern Hunter | "Fuel Storage" patterns |
| Ammo-Gen-Hunter | Pattern Hunter | "AmmoGeneration" patterns |
| Energy-Consumption-Hunter | Pattern Hunter | "EnergyConsumption" patterns |
| Simulation-Resource-Analyst | Deep Dive | game/simulation/ - hardcoded resource logic |
| Combat-Resource-Analyst | Deep Dive | Combat code - energy/ammo deduction |
| Movement-Resource-Analyst | Deep Dive | Propulsion/movement - fuel consumption |
| Ship-Entity-Analyst | Deep Dive | Ship entity resource handling |
| JSON-Config-Analyst | Config Hunter | All JSON files for legacy patterns |
| Test-Resource-Analyst | Test Hunter | Test files using legacy resource patterns |
| UI-Resource-Analyst | UI Hunter | UI code displaying/handling resources |

## Success Criteria
Comprehensive inventory of all legacy resource handling that needs migration to the generic `ResourceConsumption` system.

## Notes
- User wants large multi-agent swarm for thorough coverage
- Focus on elimination targets, not documenting correct patterns
