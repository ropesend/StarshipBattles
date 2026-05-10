"""
Command pattern for undo/redo support.

Each command captures before/after state and can execute/undo.
CommandHistory manages the undo/redo stacks.
"""
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from game.research.data.tech_node import TechNode, TechRequirement


class Command(ABC):
    """Abstract base for undoable commands."""

    @abstractmethod
    def execute(self) -> None:
        """Execute the command (first time or redo)."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the command."""

    @abstractmethod
    def description(self) -> str:
        """Human-readable description for undo/redo menus."""


class CommandHistory:
    """Manages undo/redo stacks."""

    def __init__(self):
        self._undo_stack: List[Command] = []
        self._redo_stack: List[Command] = []

    def execute(self, cmd: Command) -> None:
        """Execute a command and push it onto the undo stack."""
        cmd.execute()
        self._undo_stack.append(cmd)
        self._redo_stack.clear()

    def undo(self) -> Optional[str]:
        """Undo the last command. Returns its description, or None if nothing to undo."""
        if not self._undo_stack:
            return None
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        return cmd.description()

    def redo(self) -> Optional[str]:
        """Redo the last undone command. Returns its description, or None."""
        if not self._redo_stack:
            return None
        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        return cmd.description()

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def undo_description(self) -> Optional[str]:
        return self._undo_stack[-1].description() if self._undo_stack else None

    @property
    def redo_description(self) -> Optional[str]:
        return self._redo_stack[-1].description() if self._redo_stack else None

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()


# ── Concrete Commands ────────────────────────────────────────────────


class EditNodePropertyCmd(Command):
    """Change a scalar property on a TechNode."""

    def __init__(self, node: TechNode, prop_name: str, new_value: Any):
        self._node = node
        self._prop = prop_name
        self._new_value = new_value
        self._old_value = getattr(node, prop_name)

    def execute(self):
        setattr(self._node, self._prop, self._new_value)

    def undo(self):
        setattr(self._node, self._prop, self._old_value)

    def description(self) -> str:
        return f"Edit {self._node.id}.{self._prop}"


class AddNodeCmd(Command):
    """Add a new node to the editor model."""

    def __init__(self, model, node: TechNode, section_name: Optional[str] = None):
        self._model = model
        self._node = node
        self._section_name = section_name

    def execute(self):
        self._model.add_node(self._node, self._section_name)

    def undo(self):
        self._model.remove_node(self._node.id)

    def description(self) -> str:
        return f"Add node '{self._node.name}'"


class DeleteNodeCmd(Command):
    """Delete a node from the editor model."""

    def __init__(self, model, node_id: str):
        self._model = model
        self._node_id = node_id
        # Capture full state for undo
        self._node_snapshot: Optional[TechNode] = None
        self._section_name: Optional[str] = None
        self._position: Optional[Tuple[float, float]] = None
        self._order_index: Optional[int] = None
        self._section_index: Optional[int] = None
        # Capture incoming requirements from other nodes that reference this node
        self._incoming_refs: List[Tuple[str, int, TechRequirement]] = []

    def execute(self):
        node = self._model.tech_tree.nodes.get(self._node_id)
        if not node:
            return
        self._node_snapshot = deepcopy(node)
        self._position = self._model.positions.get(self._node_id)

        # Capture order position
        if self._node_id in self._model.node_order:
            self._order_index = self._model.node_order.index(self._node_id)

        # Capture section membership
        section = self._model.get_section_for_node(self._node_id)
        if section:
            self._section_name = section.name
            self._section_index = section.node_ids.index(self._node_id)

        # Capture incoming references before deletion removes them
        self._incoming_refs.clear()
        for other_node in self._model.tech_tree.nodes.values():
            if other_node.id == self._node_id:
                continue
            for og_idx, og in enumerate(other_node.requirements):
                for req in og:
                    if req.node_id == self._node_id:
                        self._incoming_refs.append((other_node.id, og_idx, deepcopy(req)))

        self._model.remove_node(self._node_id)

    def undo(self):
        if not self._node_snapshot:
            return

        # Re-add the node
        self._model.tech_tree.nodes[self._node_id] = deepcopy(self._node_snapshot)

        # Restore position
        if self._position:
            self._model.positions[self._node_id] = self._position

        # Restore order
        if self._order_index is not None:
            self._model.node_order.insert(self._order_index, self._node_id)
        else:
            self._model.node_order.append(self._node_id)

        # Restore section membership
        if self._section_name and self._section_index is not None:
            for section in self._model.sections:
                if section.name == self._section_name:
                    section.node_ids.insert(self._section_index, self._node_id)
                    break

        # Restore incoming references
        for other_id, og_idx, req in self._incoming_refs:
            other_node = self._model.tech_tree.nodes.get(other_id)
            if other_node:
                while len(other_node.requirements) <= og_idx:
                    other_node.requirements.append([])
                other_node.requirements[og_idx].append(deepcopy(req))

        self._model.tech_tree._depth_cache.clear()
        self._model._dirty = True

    def description(self) -> str:
        name = self._node_snapshot.name if self._node_snapshot else self._node_id
        return f"Delete node '{name}'"


class AddRequirementCmd(Command):
    """Add a requirement link between two nodes."""

    def __init__(
        self,
        model,
        target_node_id: str,
        prereq_node_id: str,
        level_range: Tuple[int, int] = (1, 1),
        negate: bool = False,
        or_group_index: int = 0,
    ):
        self._model = model
        self._target = target_node_id
        self._prereq = prereq_node_id
        self._level_range = level_range
        self._negate = negate
        self._og_index = or_group_index

    def execute(self):
        self._model.add_requirement(
            self._target, self._prereq,
            self._level_range, self._negate, self._og_index,
        )

    def undo(self):
        self._model.remove_requirement(self._target, self._prereq, self._og_index)

    def description(self) -> str:
        return f"Link {self._prereq} → {self._target}"


class RemoveRequirementCmd(Command):
    """Remove a requirement link between two nodes."""

    def __init__(self, model, target_node_id: str, prereq_node_id: str, or_group_index: int = 0):
        self._model = model
        self._target = target_node_id
        self._prereq = prereq_node_id
        self._og_index = or_group_index
        self._removed_req: Optional[TechRequirement] = None

    def execute(self):
        self._removed_req = self._model.remove_requirement(
            self._target, self._prereq, self._og_index,
        )

    def undo(self):
        if self._removed_req:
            self._model.add_requirement(
                self._target,
                self._removed_req.node_id,
                self._removed_req.level_range,
                self._removed_req.negate,
                self._og_index,
            )

    def description(self) -> str:
        return f"Unlink {self._prereq} → {self._target}"


class EditRequirementCmd(Command):
    """Edit level_range or negate on an existing requirement."""

    def __init__(
        self,
        node: TechNode,
        or_group_index: int,
        req_index: int,
        new_level_range: Optional[Tuple[int, int]] = None,
        new_negate: Optional[bool] = None,
    ):
        self._node = node
        self._og_idx = or_group_index
        self._req_idx = req_index
        self._new_lr = new_level_range
        self._new_negate = new_negate
        # Capture old values
        req = node.requirements[or_group_index][req_index]
        self._old_lr = req.level_range
        self._old_negate = req.negate

    def execute(self):
        req = self._node.requirements[self._og_idx][self._req_idx]
        if self._new_lr is not None:
            req.level_range = self._new_lr
        if self._new_negate is not None:
            req.negate = self._new_negate

    def undo(self):
        req = self._node.requirements[self._og_idx][self._req_idx]
        if self._new_lr is not None:
            req.level_range = self._old_lr
        if self._new_negate is not None:
            req.negate = self._old_negate

    def description(self) -> str:
        return f"Edit requirement on {self._node.id}"


class AddOrGroupCmd(Command):
    """Add a new OR-group to a node."""

    def __init__(self, model, node_id: str):
        self._model = model
        self._node_id = node_id
        self._group_index: int = -1

    def execute(self):
        self._group_index = self._model.add_or_group(self._node_id)

    def undo(self):
        if self._group_index >= 0:
            self._model.remove_or_group(self._node_id, self._group_index)

    def description(self) -> str:
        return f"Add OR-group to {self._node_id}"


class RemoveOrGroupCmd(Command):
    """Remove an OR-group from a node."""

    def __init__(self, model, node_id: str, or_group_index: int):
        self._model = model
        self._node_id = node_id
        self._og_index = or_group_index
        self._removed_reqs: List[TechRequirement] = []

    def execute(self):
        self._removed_reqs = self._model.remove_or_group(self._node_id, self._og_index)

    def undo(self):
        node = self._model.tech_tree.nodes.get(self._node_id)
        if node:
            node.requirements.insert(self._og_index, [deepcopy(r) for r in self._removed_reqs])
            self._model.tech_tree._depth_cache.clear()
            self._model._dirty = True

    def description(self) -> str:
        return f"Remove OR-group from {self._node_id}"


class MoveNodeCmd(Command):
    """Change a node's visual position (for drag coalescing)."""

    def __init__(self, model, node_id: str, new_pos: Tuple[float, float]):
        self._model = model
        self._node_id = node_id
        self._new_pos = new_pos
        self._old_pos = model.positions.get(node_id, (0.0, 0.0))

    def execute(self):
        self._model.set_position(self._node_id, *self._new_pos)

    def undo(self):
        self._model.set_position(self._node_id, *self._old_pos)

    def description(self) -> str:
        return f"Move {self._node_id}"


class MoveNodeToSectionCmd(Command):
    """Move a node to a different section."""

    def __init__(self, model, node_id: str, target_section: str):
        self._model = model
        self._node_id = node_id
        self._target = target_section
        section = model.get_section_for_node(node_id)
        self._source = section.name if section else "Unsorted"

    def execute(self):
        self._model.move_node_to_section(self._node_id, self._target)

    def undo(self):
        self._model.move_node_to_section(self._node_id, self._source)

    def description(self) -> str:
        return f"Move {self._node_id} to {self._target}"


class RenameSectionCmd(Command):
    """Rename a section."""

    def __init__(self, model, old_name: str, new_name: str):
        self._model = model
        self._old_name = old_name
        self._new_name = new_name

    def execute(self):
        self._model.rename_section(self._old_name, self._new_name)

    def undo(self):
        self._model.rename_section(self._new_name, self._old_name)

    def description(self) -> str:
        return f"Rename section '{self._old_name}'"
