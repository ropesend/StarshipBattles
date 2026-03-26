# FEAT-11: Data-Driven Planet Resource Generation with Mass Scaling

## Description
Planet resource quantities and quality distribution should be driven by JSON data files rather than hardcoded constants in `planet_gen.py`. Resource quantities should scale with planet mass (higher mass = more quantity, lower quality; lower mass = less quantity, higher quality). An average Earth-mass planet should start with approximately 10 million of each resource, with semi-random variance.

### Key Changes
1. **Expand `data/astrophysics.json`** with a resource generation section containing:
   - Per-resource-type generation curves (quantity and quality vs. mass)
   - Planet-type affinity modifiers (e.g., MAGMA planets favor Radioactives, PELAGIC favors Organics)
   - Baseline quantity target (~10M for Earth-mass) and scaling parameters
   - Quality inversion curve parameters (low mass = high quality, high mass = low quality)
   - Randomness/variance controls
2. **Remove all hardcoded resource generation constants** from `planet_gen.py` (~27 values including log-mass bounds 20.0/28.0, quantity/quality weight splits 0.7/0.3, max quantity cap of 1,000,000)
3. **Load and apply** the new JSON-driven parameters during `PlanetGenerator._generate_resources()`

### Current State (for reference)
- `planet_gen.py` lines 510-543 contain all resource generation logic with hardcoded constants
- Quantity formula: `size_factor * 0.7 + random * 0.3`, capped at 1,000,000
- Quality formula: `(1.0 - size_factor) * 0.7 + random * 0.3`, scaled to 0-100
- The 5 planet resources are: Metals, Organics, Vapors, Radioactives, Exotics (defined in `game/core/constants.py`)

## Priority
Medium

## Status
Pending

## Work Log
- 2026-03-25: Created from QA Session 20260325_191105.
