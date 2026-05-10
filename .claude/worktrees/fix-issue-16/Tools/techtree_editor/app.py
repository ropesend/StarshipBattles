"""
Application controller for the Tech Tree Editor.

Orchestrates the model, command history, node graph, and GUI.
Handles file operations, validation, and undo/redo.
"""
import os
from typing import Optional

from game.research.data.tech_node import TechNode, TechRequirement

from .model import EditorModel, PRICE_CURVES
from .commands import (
    CommandHistory, EditNodePropertyCmd, AddNodeCmd, DeleteNodeCmd,
    AddRequirementCmd, RemoveRequirementCmd, EditRequirementCmd,
    AddOrGroupCmd, RemoveOrGroupCmd, MoveNodeCmd, MoveNodeToSectionCmd,
    RenameSectionCmd,
)
from .layout import apply_auto_layout


class App:
    """Central controller for the tech tree editor."""

    def __init__(self):
        self.model = EditorModel()
        self.history = CommandHistory()
        self._selected_node_id: Optional[str] = None
        self._selected_link_key: Optional[str] = None

    @property
    def selected_node_id(self) -> Optional[str]:
        return self._selected_node_id

    @selected_node_id.setter
    def selected_node_id(self, value: Optional[str]):
        self._selected_node_id = value

    @property
    def selected_link_key(self) -> Optional[str]:
        return self._selected_link_key

    @selected_link_key.setter
    def selected_link_key(self, value: Optional[str]):
        self._selected_link_key = value

    # ── File Operations ──────────────────────────────────────────────

    def load_file(self, file_path: str) -> list:
        """Load a tech tree file. Returns validation errors."""
        errors = self.model.load(file_path)
        self.history.clear()
        self._selected_node_id = None
        self._selected_link_key = None

        # Generate positions if not loaded from sidecar
        if not self.model.positions:
            apply_auto_layout(self.model, only_unpositioned=False)
        else:
            # Fill in any missing positions
            apply_auto_layout(self.model, only_unpositioned=True)

        return errors

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save the current tree. Returns True on success."""
        return self.model.save(file_path)

    def get_default_file_path(self) -> str:
        """Get the default techtree.json path."""
        from game.core.paths import Paths
        return os.path.join(Paths.DATA_DIR, "techtree.json")

    @property
    def window_title(self) -> str:
        """Generate window title with dirty indicator."""
        name = os.path.basename(self.model.file_path) if self.model.file_path else "Untitled"
        dirty = " *" if self.model.dirty else ""
        return f"Tech Tree Editor - {name}{dirty}"

    # ── Undo/Redo ────────────────────────────────────────────────────

    def undo(self) -> Optional[str]:
        desc = self.history.undo()
        if desc:
            self.model.mark_dirty()
        return desc

    def redo(self) -> Optional[str]:
        desc = self.history.redo()
        if desc:
            self.model.mark_dirty()
        return desc

    def execute(self, cmd):
        """Execute a command through the history."""
        self.history.execute(cmd)
        self.model.mark_dirty()

    # ── Node Editing ─────────────────────────────────────────────────

    def edit_node_property(self, node_id: str, prop: str, value):
        """Edit a property on a node via command."""
        node = self.model.nodes.get(node_id)
        if not node:
            return
        old_value = getattr(node, prop, None)
        if old_value == value:
            return
        self.execute(EditNodePropertyCmd(node, prop, value))

    def add_node(self, node_id: str, name: str, section_name: Optional[str] = None) -> Optional[TechNode]:
        """Create and add a new node."""
        if node_id in self.model.nodes:
            return None
        node = TechNode(id=node_id, name=name, max_levels=1)
        self.execute(AddNodeCmd(self.model, node, section_name))
        return node

    def delete_node(self, node_id: str):
        """Delete a node."""
        if node_id not in self.model.nodes:
            return
        self.execute(DeleteNodeCmd(self.model, node_id))
        if self._selected_node_id == node_id:
            self._selected_node_id = None

    # ── Requirement Editing ──────────────────────────────────────────

    def add_link(self, source_id: str, target_id: str, or_group_index: int = 0):
        """Add a requirement link."""
        self.execute(AddRequirementCmd(self.model, target_id, source_id, or_group_index=or_group_index))

    def remove_link(self, source_id: str, target_id: str, or_group_index: int = 0):
        """Remove a requirement link."""
        self.execute(RemoveRequirementCmd(self.model, target_id, source_id, or_group_index))

    def edit_requirement(self, node_id: str, og_idx: int, req_idx: int,
                         level_range=None, negate=None):
        """Edit a requirement's properties."""
        node = self.model.nodes.get(node_id)
        if not node or og_idx >= len(node.requirements) or req_idx >= len(node.requirements[og_idx]):
            return
        self.execute(EditRequirementCmd(node, og_idx, req_idx, level_range, negate))

    def add_or_group(self, node_id: str):
        """Add an OR-group to a node."""
        self.execute(AddOrGroupCmd(self.model, node_id))

    def remove_or_group(self, node_id: str, og_idx: int):
        """Remove an OR-group from a node."""
        self.execute(RemoveOrGroupCmd(self.model, node_id, og_idx))

    # ── Section Management ───────────────────────────────────────────

    def move_node_to_section(self, node_id: str, section_name: str):
        """Move a node to a different section."""
        self.execute(MoveNodeToSectionCmd(self.model, node_id, section_name))

    def rename_section(self, old_name: str, new_name: str):
        """Rename a section."""
        self.execute(RenameSectionCmd(self.model, old_name, new_name))

    def create_section(self, name: str):
        """Create a new section (not undoable — lightweight operation)."""
        self.model.create_section(name)

    # ── Layout ───────────────────────────────────────────────────────

    def reset_layout(self):
        """Reset all positions to auto-layout."""
        apply_auto_layout(self.model, only_unpositioned=False)

    def save_node_position(self, node_id: str, x: float, y: float):
        """Save a node's position after dragging."""
        self.model.set_position(node_id, x, y)

    # ── Validation ───────────────────────────────────────────────────

    def validate(self) -> list:
        """Run all validations."""
        return self.model.validate()
