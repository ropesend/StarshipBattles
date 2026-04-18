"""PROJ-282 Phase 8: shared constants for the battle setup package.

Module-level tables + helpers previously held at the top of the old
`battle_setup_screen.py`. Relocated here so panels, the controller, and
the input handler all import from a stable module — the old screen's
location was transient (it's being deleted).
"""
from __future__ import annotations

from game.strategy.data.fleet_hierarchy import BattleRole

# Complex design IDs that affect combat (system-scope)
_SYSTEM_SCOPE_COMPLEXES = [
    ("qs_system_shield_booster_complex", "System Shield Booster"),
    ("qs_system_shield_suppressor_complex", "System Shield Suppressor"),
    ("qs_system_shield_projector_complex", "System Shield Projector"),
    ("qs_system_damage_booster_complex", "System Damage Booster"),
    ("qs_system_damage_suppressor_complex", "System Damage Suppressor"),
]

_SECTOR_SCOPE_COMPLEXES = [
    ("qs_sector_shield_booster_complex", "Sector Shield Booster"),
    ("qs_sector_shield_suppressor_complex", "Sector Shield Suppressor"),
    ("qs_sector_shield_projector_complex", "Sector Shield Projector"),
    ("qs_sector_damage_booster_complex", "Sector Damage Booster"),
    ("qs_sector_damage_suppressor_complex", "Sector Damage Suppressor"),
]

# Targeting policy options for dropdowns
_TARGETING_OPTIONS = [
    ("focus_strongest", "Focus Strongest"),
    ("focus_nearest", "Focus Nearest"),
    ("focus_weakest", "Focus Weakest"),
    ("distributed", "Distributed"),
    ("anti_fighter", "Anti-Fighter"),
    ("anti_capital", "Anti-Capital"),
]

_MOVEMENT_OPTIONS = [
    ("advance", "Advance"),
    ("hold_range", "Hold Range"),
    ("hold_position", "Hold Position"),
    ("pursue", "Pursue"),
    ("hit_and_run", "Hit & Run"),
]

_BATTLE_ROLE_OPTIONS = [
    (BattleRole.MAIN_BODY, "Main Body"),
    (BattleRole.VANGUARD, "Vanguard"),
    (BattleRole.SCREEN, "Screen"),
    (BattleRole.FLANKER_LEFT, "Flanker Left"),
    (BattleRole.FLANKER_RIGHT, "Flanker Right"),
    (BattleRole.RESERVE, "Reserve"),
]
