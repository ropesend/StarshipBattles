# PROJ-234 File Manifest

> Generated during Protocol 01. Used by parallel execution for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| `game/strategy/data/ship_instance.py` | Production | Primary target. Delete from_ship(), add facades, wire bridge delegate. |
| `game/strategy/data/ship_instance_serializer.py` | Production | **NEW** — Static utility class for serialization (to_dict, from_dict, clone, to_json, from_json) |
| `game/strategy/data/ship_instance_bridge.py` | Production | **NEW** — Eager delegate for simulation bridge (to_ship, update_from_ship, _capture_resource_levels) |
| `game/strategy/data/ship_display_formatter.py` | Production | Fix magic number (max_hp=100) and format string ('06d') |
| `game/core/protocols.py` | Production | Update docstrings referencing from_ship |
| `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` | Test | **NEW** — Serializer unit tests |
| `tests/unit/strategy/ship_instance/test_ship_instance_bridge.py` | Test | **NEW** — Bridge unit tests |
