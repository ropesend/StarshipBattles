"""
ComponentActivationState — Per-component activation timer state machine.

Tracks the activation lifecycle of individual components on facilities and ships.
Each activatable component has its own state, allowing parallel activation.

State machine: INACTIVE → ACTIVATING → ACTIVE → DEACTIVATING → INACTIVE

Used by:
- PlanetaryFacility.component_states (planet facilities)
- ShipInstance.activation_states (fleet ships)
- ComponentActivationEngine (tick processing)
- PlanetEnergyEngine (energy drain during all non-INACTIVE phases)
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from game.core.error_codes import ErrorCode
from game.core.exceptions import StateException
from game.core.validation_helpers import require_keys


class ActivationPhase(Enum):
    """Component activation lifecycle phases."""
    INACTIVE = "inactive"
    ACTIVATING = "activating"
    ACTIVE = "active"
    DEACTIVATING = "deactivating"


@dataclass
class ComponentActivationState:
    """Per-component activation timer state.

    Tracks where a component is in the activation lifecycle and how far
    through the current transition it has progressed.

    Attributes:
        phase: Current lifecycle phase.
        progress_ticks: Ticks elapsed in the current transitional phase.
        required_ticks: Total ticks needed to complete the transition.
        ability_name: The ability this activation controls (e.g., "GeologicStabilizer").
        energy_drain_rate: Energy consumed per turn while draining (cached from component data).
    """
    phase: ActivationPhase = ActivationPhase.INACTIVE
    progress_ticks: int = 0
    required_ticks: int = 0
    ability_name: str = ""
    energy_drain_rate: float = 0.0

    def tick(self) -> bool:
        """Advance one tick. Returns True if a phase transition occurred."""
        if self.phase == ActivationPhase.ACTIVATING:
            self.progress_ticks += 1
            if self.progress_ticks >= self.required_ticks:
                self.phase = ActivationPhase.ACTIVE
                self.progress_ticks = 0
                self.required_ticks = 0
                return True
            return False

        if self.phase == ActivationPhase.DEACTIVATING:
            self.progress_ticks += 1
            if self.progress_ticks >= self.required_ticks:
                self.phase = ActivationPhase.INACTIVE
                self.progress_ticks = 0
                self.required_ticks = 0
                self.energy_drain_rate = 0.0
                return True
            return False

        return False

    def start_activating(self, required_ticks: int, energy_drain_rate: float) -> None:
        """Transition from INACTIVE to ACTIVATING.

        Raises:
            StateException: If not in INACTIVE phase.
        """
        if self.phase != ActivationPhase.INACTIVE:
            raise StateException(
                f"Cannot start activating from {self.phase.value} phase "
                f"(must be inactive)",
                code=ErrorCode.INVALID_STATE.value,
                context={
                    "current_phase": self.phase.value,
                    "expected_phase": ActivationPhase.INACTIVE.value,
                },
            )
        self.phase = ActivationPhase.ACTIVATING
        self.progress_ticks = 0
        self.required_ticks = required_ticks
        self.energy_drain_rate = energy_drain_rate

    def start_deactivating(self, required_ticks: int) -> None:
        """Transition from ACTIVE to DEACTIVATING.

        Raises:
            StateException: If not in ACTIVE phase.
        """
        if self.phase != ActivationPhase.ACTIVE:
            raise StateException(
                f"Cannot start deactivating from {self.phase.value} phase "
                f"(must be active)",
                code=ErrorCode.INVALID_STATE.value,
                context={
                    "current_phase": self.phase.value,
                    "expected_phase": ActivationPhase.ACTIVE.value,
                },
            )
        self.phase = ActivationPhase.DEACTIVATING
        self.progress_ticks = 0
        self.required_ticks = required_ticks

    def cancel(self) -> None:
        """Reset to INACTIVE immediately from any phase."""
        self.phase = ActivationPhase.INACTIVE
        self.progress_ticks = 0
        self.required_ticks = 0
        self.energy_drain_rate = 0.0

    @property
    def is_functionally_active(self) -> bool:
        """True only when the component is fully active."""
        return self.phase == ActivationPhase.ACTIVE

    @property
    def is_draining_energy(self) -> bool:
        """True during ACTIVATING, ACTIVE, and DEACTIVATING (if drain rate > 0)."""
        if self.energy_drain_rate <= 0:
            return False
        return self.phase in (
            ActivationPhase.ACTIVATING,
            ActivationPhase.ACTIVE,
            ActivationPhase.DEACTIVATING,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for save games."""
        return {
            'phase': self.phase.value,
            'progress_ticks': self.progress_ticks,
            'required_ticks': self.required_ticks,
            'ability_name': self.ability_name,
            'energy_drain_rate': self.energy_drain_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComponentActivationState':
        """Deserialize from dict.

        Requires the ``phase`` field. PROJ-466: missing/corrupt data raises
        ``PersistenceException`` (``CORRUPT_DATA``) via ``require_keys`` /
        the enum-conversion guard instead of a raw ``KeyError`` /
        ``ValueError`` at the persistence boundary.
        """
        from game.core.exceptions import PersistenceException

        require_keys(data, ['phase'], 'ComponentActivationState')
        try:
            phase = ActivationPhase(data['phase'])
        except ValueError as e:
            raise PersistenceException(
                f"ComponentActivationState: unknown phase {data['phase']!r}",
                code=ErrorCode.CORRUPT_DATA.value,
                context={"phase": str(data['phase'])},
            ) from e
        return cls(
            phase=phase,
            progress_ticks=data.get('progress_ticks', 0),
            required_ticks=data.get('required_ticks', 0),
            ability_name=data.get('ability_name', ''),
            energy_drain_rate=data.get('energy_drain_rate', 0.0),
        )
