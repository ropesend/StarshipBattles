# BUG-34: Fleet Report Window shows incorrect warp capability

## Description
In the Fleet Report Window, a vehicle that has a warp drive but doesn't have the resource capacity to run it, should not be listed as having warp capability.

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log
- 2026-01-23: Ticket created.
- 2026-01-23: Fixed. Modified `has_warp_capability()` in `game/ui/screens/fleet_report_filters.py` to check resource storage capacity in addition to warp drive tonnage. A ship is now only considered warp-capable if:
  1. It has a warp drive with sufficient tonnage for its mass
  2. The warp drive is undamaged
  3. It has enough energy storage capacity (`max_energy >= warp_energy_cost`)
  4. It has enough fuel storage capacity (`max_fuel >= warp_fuel_cost`)

  All existing tests pass.
