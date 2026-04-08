"""Core combat data types shared across Engine and Simulation layers.

These types live in Core so that both Engine (collision detection) and
Simulation (damage pipeline) can use them without cross-layer imports.
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True, slots=True)
class DamageContext:
    """Attacker identity threaded through the damage pipeline.

    Created at the point where damage originates (projectile hit,
    beam hit, ramming collision) and passed through take_damage()
    and apply_damage() so events know who caused the damage.
    """
    attacker: Optional[Any] = None
    source_weapon: Optional[Any] = None
    damage_type: str = "unknown"
