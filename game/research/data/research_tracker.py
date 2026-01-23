"""
ResearchTracker - Manages per-session research state including node levels,
breakthrough chances, and RP allocations.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import random


@dataclass
class NodeState:
    """Per-node research state."""
    current_level: int = 0
    current_chance: float = 0.0  # Current breakthrough probability (0.0 - 0.95)
    rp_allocation: int = 0  # RP allocated per turn (persists across turns)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'current_level': self.current_level,
            'current_chance': self.current_chance,
            'rp_allocation': self.rp_allocation
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NodeState':
        """Deserialize from dictionary."""
        return cls(
            current_level=data.get('current_level', 0),
            current_chance=data.get('current_chance', 0.0),
            rp_allocation=data.get('rp_allocation', 0)
        )


class ResearchTracker:
    """
    Tracks research progress and RP allocation for a research session.

    Manages:
    - Per-node state (level, chance, allocation)
    - Session seed for fuzzy requirement resolution
    - RP budget configuration
    - Turn event logging
    """

    MIN_RP_BUDGET = 50
    MAX_RP_BUDGET = 500
    DEFAULT_RP_BUDGET = 200

    def __init__(self, session_seed: int = None):
        """
        Initialize the research tracker.

        Args:
            session_seed: Seed for fuzzy requirement resolution.
                         If None, generates a random seed.
        """
        self.node_states: Dict[str, NodeState] = {}
        self.session_seed = session_seed if session_seed is not None else random.randint(0, 2**31 - 1)
        self.rp_budget: int = self.DEFAULT_RP_BUDGET
        self.turn_number: int = 0
        self.turn_log: List[Dict[str, Any]] = []  # Events from last turn

    def get_state(self, node_id: str) -> NodeState:
        """
        Get or create state for a node.

        Args:
            node_id: ID of the node

        Returns:
            NodeState for the node (created if not exists)
        """
        if node_id not in self.node_states:
            self.node_states[node_id] = NodeState()
        return self.node_states[node_id]

    def get_all_tech_levels(self) -> Dict[str, int]:
        """
        Get mapping of node_id -> current_level for all nodes with state.

        Returns:
            Dictionary of node IDs to their current levels
        """
        return {nid: state.current_level for nid, state in self.node_states.items()}

    def get_total_allocated(self) -> int:
        """
        Get total RP allocated across all nodes.

        Returns:
            Sum of all RP allocations
        """
        return sum(s.rp_allocation for s in self.node_states.values())

    def get_remaining_rp(self) -> int:
        """
        Get remaining RP available for allocation.

        Returns:
            rp_budget - total_allocated
        """
        return max(0, self.rp_budget - self.get_total_allocated())

    def set_allocation(self, node_id: str, rp: int) -> bool:
        """
        Set RP allocation for a node.

        The allocation is clamped to available RP and non-negative values.

        Args:
            node_id: ID of the node
            rp: RP amount to allocate

        Returns:
            True if allocation was set, False if exceeds budget
        """
        state = self.get_state(node_id)
        old_allocation = state.rp_allocation

        # Calculate max we can allocate (current allocation + remaining)
        remaining = self.get_remaining_rp() + old_allocation
        new_allocation = max(0, min(rp, remaining))

        state.rp_allocation = new_allocation
        return new_allocation == rp

    def clear_allocation(self, node_id: str) -> None:
        """
        Clear RP allocation for a node.

        Args:
            node_id: ID of the node
        """
        if node_id in self.node_states:
            self.node_states[node_id].rp_allocation = 0

    def clear_all_allocations(self) -> None:
        """Clear all RP allocations."""
        for state in self.node_states.values():
            state.rp_allocation = 0

    def set_rp_budget(self, budget: int) -> None:
        """
        Set total RP available per turn.

        Args:
            budget: RP budget (clamped to MIN_RP_BUDGET - MAX_RP_BUDGET)
        """
        self.rp_budget = max(self.MIN_RP_BUDGET, min(self.MAX_RP_BUDGET, budget))

    def increment_turn(self) -> None:
        """Increment the turn counter."""
        self.turn_number += 1

    def set_turn_log(self, events: List[Dict[str, Any]]) -> None:
        """
        Set the turn log with events from the last turn.

        Args:
            events: List of event dictionaries
        """
        self.turn_log = events

    def get_nodes_with_allocation(self) -> List[str]:
        """
        Get list of node IDs that have RP allocated.

        Returns:
            List of node IDs with non-zero allocation
        """
        return [nid for nid, state in self.node_states.items() if state.rp_allocation > 0]

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'session_seed': self.session_seed,
            'rp_budget': self.rp_budget,
            'turn_number': self.turn_number,
            'node_states': {nid: s.to_dict() for nid, s in self.node_states.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResearchTracker':
        """Deserialize from dictionary."""
        tracker = cls(session_seed=data.get('session_seed'))
        tracker.rp_budget = data.get('rp_budget', cls.DEFAULT_RP_BUDGET)
        tracker.turn_number = data.get('turn_number', 0)
        for nid, state_data in data.get('node_states', {}).items():
            tracker.node_states[nid] = NodeState.from_dict(state_data)
        return tracker

    def reset(self) -> None:
        """Reset all research progress (keep seed and budget)."""
        self.node_states.clear()
        self.turn_number = 0
        self.turn_log = []
