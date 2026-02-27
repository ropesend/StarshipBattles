"""
ResearchService - Handles the stochastic research simulation logic.

Implements the "Leaky Bucket" algorithm:
1. Decay: At turn start, Current_Chance -= Base_Decay (clamp at 0)
2. Investment: Added_Chance = Volatility * ln(1 + Invested_RP)
3. Total: Current_Chance += Added_Chance (cap at 95%)
4. Roll: Random float 0.0-1.0, if < Current_Chance, level up
5. Reset: On level up, Current_Chance = 0
"""
import logging
import math
import random
from typing import List, Dict, Any

from game.research.data.tech_tree import TechTree

logger = logging.getLogger(__name__)
from game.research.data.research_tracker import ResearchTracker


class ResearchService:
    """
    Handles research simulation logic (leaky bucket mechanics).

    This service is stateless - all state is stored in the ResearchTracker.
    """

    MAX_CHANCE = 0.95  # 95% cap on breakthrough probability

    @classmethod
    def process_turn(cls, tech_tree: TechTree, tracker: ResearchTracker,
                     tech_levels: Dict[str, int] = None) -> List[Dict[str, Any]]:
        """
        Process one turn of research for a session.

        Args:
            tech_tree: The tech tree structure
            tracker: The research tracker with current state
            tech_levels: Optional pre-computed tech levels (for performance)

        Returns:
            List of events:
            [
                {
                    'node_id': str,
                    'event': 'breakthrough' | 'progress' | 'decay',
                    'details': {...}
                },
                ...
            ]
        """
        events = []
        rng = random.Random()  # Use fresh RNG for rolls (non-deterministic)

        # Get current tech levels for status checks
        if tech_levels is None:
            tech_levels = tracker.get_all_tech_levels()
        else:
            # Make a copy since we modify it during processing
            tech_levels = dict(tech_levels)

        # Increment turn counter
        tracker.increment_turn()
        turn_num = tracker.turn_number

        logger.debug(f"ResearchService: Processing turn {turn_num}")

        # Process all nodes that have allocation or accumulated chance
        for node in tech_tree.nodes.values():
            state = tracker.get_state(node.id)
            status = node.get_status(state.current_level, tech_levels)

            # Skip completed or locked nodes
            if status == 'completed':
                continue
            if status == 'locked':
                # Still apply decay to locked nodes with accumulated chance
                if state.current_chance > 0:
                    old_chance = state.current_chance
                    state.current_chance = max(0.0, state.current_chance - node.base_decay)
                    if old_chance != state.current_chance:
                        events.append({
                            'node_id': node.id,
                            'event': 'decay',
                            'details': {
                                'name': node.name,
                                'old_chance': old_chance,
                                'new_chance': state.current_chance,
                                'decay_amount': node.base_decay
                            }
                        })
                continue

            # --- Leaky Bucket Algorithm for Available Nodes ---

            # 1. Decay: Current_Chance -= Base_Decay (clamp at 0)
            old_chance = state.current_chance
            decay_applied = min(old_chance, node.base_decay)
            state.current_chance = max(0.0, state.current_chance - node.base_decay)

            # Skip nodes with no investment
            if state.rp_allocation <= 0:
                if decay_applied > 0:
                    events.append({
                        'node_id': node.id,
                        'event': 'decay',
                        'details': {
                            'name': node.name,
                            'old_chance': old_chance,
                            'new_chance': state.current_chance,
                            'decay_amount': decay_applied
                        }
                    })
                continue

            # 2. Investment: Added_Chance = Volatility * ln(1 + Effective_RP)
            # Apply price multiplier based on target level
            target_level = state.current_level + 1
            effective_price = node.get_effective_price(target_level)
            effective_rp = state.rp_allocation / effective_price
            added_chance = node.volatility * math.log(1 + effective_rp)

            # 3. Total: Current_Chance += Added_Chance (cap at 95%)
            chance_before_investment = state.current_chance
            state.current_chance = min(cls.MAX_CHANCE, state.current_chance + added_chance)

            # 4. Roll: Random 0.0-1.0, if < Current_Chance, level up
            roll = rng.random()

            if roll < state.current_chance:
                # Breakthrough!
                old_level = state.current_level
                state.current_level += 1
                final_chance = state.current_chance

                events.append({
                    'node_id': node.id,
                    'event': 'breakthrough',
                    'details': {
                        'name': node.name,
                        'old_level': old_level,
                        'new_level': state.current_level,
                        'max_level': node.max_levels,
                        'chance': final_chance,
                        'roll': roll,
                        'rp_invested': state.rp_allocation,
                        'effective_price': effective_price,
                        'effective_rp': effective_rp,
                        'turn': turn_num
                    }
                })

                # 5. Reset: On level up, Current_Chance = 0
                state.current_chance = 0.0

                # Update tech_levels for subsequent nodes in same turn
                tech_levels[node.id] = state.current_level

                logger.info(f"Research Breakthrough: {node.name} -> Level {state.current_level}/{node.max_levels}")
            else:
                # No breakthrough, but progress accumulated
                events.append({
                    'node_id': node.id,
                    'event': 'progress',
                    'details': {
                        'name': node.name,
                        'level': state.current_level,
                        'max_level': node.max_levels,
                        'chance': state.current_chance,
                        'roll': roll,
                        'rp_invested': state.rp_allocation,
                        'effective_price': effective_price,
                        'effective_rp': effective_rp,
                        'added_chance': added_chance,
                        'decay_applied': decay_applied,
                        'turn': turn_num
                    }
                })

        # Store events in tracker for UI access
        tracker.set_turn_log(events)

        logger.debug(f"ResearchService: Turn {turn_num} complete, {len(events)} events")
        return events

    @classmethod
    def calculate_added_chance(cls, volatility: float, rp: int) -> float:
        """
        Calculate the chance increase from RP investment.

        Formula: Added_Chance = Volatility * ln(1 + Invested_RP)

        Args:
            volatility: Node's volatility coefficient
            rp: RP invested

        Returns:
            Added breakthrough chance (before capping)
        """
        if rp <= 0:
            return 0.0
        return volatility * math.log(1 + rp)

    @classmethod
    def estimate_turns_to_breakthrough(cls, volatility: float, base_decay: float, rp: int) -> float:
        """
        Estimate average turns to breakthrough with given RP investment.

        This is a rough estimate assuming constant investment and
        chance accumulation until reaching ~50% (median breakthrough).

        Args:
            volatility: Node's volatility coefficient
            base_decay: Node's base decay rate
            rp: RP invested per turn

        Returns:
            Estimated turns (or float('inf') if net gain is <= 0)
        """
        if rp <= 0:
            return float('inf')

        added_chance = cls.calculate_added_chance(volatility, rp)
        net_gain = added_chance - base_decay

        if net_gain <= 0:
            return float('inf')  # Will never accumulate enough

        # Rough estimate: turns to reach 50% chance
        target_chance = 0.50
        return target_chance / net_gain
