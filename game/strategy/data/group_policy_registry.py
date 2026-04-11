"""
Group policy registry — loads and validates group-level combat policy presets.

Group policies define the targeting, movement, and retreat behavior for
fleet hierarchy nodes (Task Forces and Squadrons). Each axis is independent
and inheritable through the hierarchy.

The registry loads from data/group_policies.json and provides validation
and lookup for policy preset IDs used in CombatPolicy.
"""

import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from game.core.json_utils import load_json
from game.core.paths import Paths

if TYPE_CHECKING:
    from game.strategy.data.fleet_hierarchy import CombatPolicy

logger = logging.getLogger(__name__)


class GroupPolicyRegistry:
    """Registry for group-level combat policy presets.

    Loads targeting, movement, and retreat policy definitions from
    data/group_policies.json. Provides validation and lookup.
    """

    def __init__(self):
        self.targeting_policies: Dict[str, Dict[str, Any]] = {}
        self.movement_policies: Dict[str, Dict[str, Any]] = {}
        self.retreat_policies: Dict[str, Dict[str, Any]] = {}
        self._loaded = False

    def load(self, file_path: Optional[str] = None) -> None:
        """Load policy presets from JSON.

        Args:
            file_path: Path to group_policies.json. Defaults to Paths constant.
        """
        if file_path is None:
            file_path = Paths.GROUP_POLICIES_FILE

        data = load_json(file_path, default={})

        self.targeting_policies = data.get("targeting", {})
        self.movement_policies = data.get("movement", {})
        self.retreat_policies = data.get("retreat", {})
        self._loaded = True

        logger.info(
            f"GroupPolicyRegistry loaded: "
            f"{len(self.targeting_policies)} targeting, "
            f"{len(self.movement_policies)} movement, "
            f"{len(self.retreat_policies)} retreat"
        )

    # --- Validation ---

    def is_valid_targeting(self, policy_id: str) -> bool:
        """Check if a targeting policy ID is valid."""
        return policy_id in self.targeting_policies

    def is_valid_movement(self, policy_id: str) -> bool:
        """Check if a movement policy ID is valid."""
        return policy_id in self.movement_policies

    def is_valid_retreat(self, policy_id: str) -> bool:
        """Check if a retreat policy ID is valid."""
        return policy_id in self.retreat_policies

    def validate_policy(self, policy: 'CombatPolicy') -> List[str]:
        """Validate all non-None axes of a CombatPolicy.

        Args:
            policy: The CombatPolicy to validate.

        Returns:
            List of error messages (empty if all valid).
        """
        errors: List[str] = []

        if policy.targeting is not None and not self.is_valid_targeting(policy.targeting):
            errors.append(f"Invalid targeting policy: '{policy.targeting}'")

        if policy.movement is not None and not self.is_valid_movement(policy.movement):
            errors.append(f"Invalid movement policy: '{policy.movement}'")

        if policy.retreat is not None and not self.is_valid_retreat(policy.retreat):
            errors.append(f"Invalid retreat policy: '{policy.retreat}'")

        return errors

    # --- Lookup ---

    def get_targeting(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get targeting policy definition by ID, or None."""
        return self.targeting_policies.get(policy_id)

    def get_movement(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get movement policy definition by ID, or None."""
        return self.movement_policies.get(policy_id)

    def get_retreat(self, policy_id: str) -> Optional[Dict[str, Any]]:
        """Get retreat policy definition by ID, or None."""
        return self.retreat_policies.get(policy_id)
