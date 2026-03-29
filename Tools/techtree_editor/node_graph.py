"""
Node graph rendering using Dear PyGui's node editor widget.

Maps TechTree nodes to dpg.node items with input/output pins,
and requirements to dpg.node_link items.
"""
import dearpygui.dearpygui as dpg
from typing import Any, Callable, Dict, List, Optional, Tuple

from game.research.data.tech_node import TechNode

from .model import EditorModel


# Branch color palette (HSV-based, 22 colors for 22 sections)
SECTION_COLORS = [
    (100, 150, 255),   # Blue
    (255, 150, 100),   # Orange
    (100, 255, 150),   # Green
    (255, 100, 150),   # Pink
    (150, 100, 255),   # Purple
    (255, 255, 100),   # Yellow
    (100, 255, 255),   # Cyan
    (255, 100, 255),   # Magenta
    (180, 220, 100),   # Lime
    (255, 180, 150),   # Peach
    (150, 200, 255),   # Light blue
    (200, 150, 100),   # Brown
    (100, 200, 200),   # Teal
    (220, 100, 100),   # Red
    (180, 180, 255),   # Lavender
    (255, 220, 150),   # Gold
    (150, 255, 200),   # Mint
    (200, 100, 200),   # Plum
    (130, 180, 130),   # Sage
    (255, 150, 200),   # Rose
    (170, 210, 230),   # Sky
    (210, 180, 140),   # Tan
]


class NodeGraph:
    """Manages the Dear PyGui node editor and its contents.

    Responsible for:
    - Creating/updating dpg nodes from TechTree data
    - Managing links between nodes
    - Handling link creation/deletion callbacks
    - Tracking the mapping between dpg items and model IDs
    """

    def __init__(self, model: EditorModel):
        self.model = model

        # Mappings between dpg item IDs and model IDs
        self._node_to_dpg: Dict[str, int] = {}       # model node_id → dpg node tag
        self._dpg_to_node: Dict[int, str] = {}        # dpg node tag → model node_id
        self._output_pins: Dict[str, int] = {}         # node_id → dpg output attribute tag
        self._input_pins: Dict[str, Dict[int, int]] = {}  # node_id → {or_group_idx: dpg input attr tag}
        self._link_to_dpg: Dict[str, int] = {}         # "source_id|target_id|og_idx" → dpg link tag
        self._dpg_to_link: Dict[int, str] = {}         # dpg link tag → link key

        # Section color mapping
        self._section_colors: Dict[str, Tuple[int, int, int]] = {}

        # Callbacks
        self.on_node_selected: Optional[Callable[[str], None]] = None
        self.on_node_deselected: Optional[Callable[[], None]] = None
        self.on_link_created: Optional[Callable[[str, str], None]] = None
        self.on_link_deleted: Optional[Callable[[int], None]] = None
        self.on_node_moved: Optional[Callable[[str, float, float], None]] = None

        # Node editor dpg tag
        self._editor_tag: Optional[int] = None

    def build_section_colors(self):
        """Assign colors to sections."""
        for i, section in enumerate(self.model.sections):
            self._section_colors[section.name] = SECTION_COLORS[i % len(SECTION_COLORS)]

    def get_section_color(self, node_id: str) -> Tuple[int, int, int]:
        """Get the color for a node based on its section."""
        section = self.model.get_section_for_node(node_id)
        if section:
            return self._section_colors.get(section.name, (150, 150, 150))
        return (150, 150, 150)

    def create_editor(self, parent: int) -> int:
        """Create the node editor widget.

        Args:
            parent: DPG parent container tag.

        Returns:
            DPG tag of the node editor.
        """
        self._editor_tag = dpg.add_node_editor(
            parent=parent,
            callback=self._on_link_created,
            delink_callback=self._on_link_deleted,
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_BottomRight,
        )
        return self._editor_tag

    def rebuild(self):
        """Rebuild all nodes and links from the model."""
        if self._editor_tag is None:
            return

        self.clear()
        self.build_section_colors()

        # Create all nodes
        for node_id, node in self.model.nodes.items():
            self._create_node(node_id, node)

        # Create all links
        for link_info in self.model.get_all_links():
            self._create_link(link_info)

        # Apply positions
        for node_id, dpg_tag in self._node_to_dpg.items():
            pos = self.model.get_position(node_id)
            dpg.set_item_pos(dpg_tag, [pos[0], pos[1]])

    def clear(self):
        """Remove all nodes and links from the editor."""
        if self._editor_tag is None:
            return

        # Delete all children of the node editor
        for dpg_tag in list(self._node_to_dpg.values()):
            if dpg.does_item_exist(dpg_tag):
                dpg.delete_item(dpg_tag)
        for dpg_tag in list(self._link_to_dpg.values()):
            if dpg.does_item_exist(dpg_tag):
                dpg.delete_item(dpg_tag)

        self._node_to_dpg.clear()
        self._dpg_to_node.clear()
        self._output_pins.clear()
        self._input_pins.clear()
        self._link_to_dpg.clear()
        self._dpg_to_link.clear()

    def _create_node(self, node_id: str, node: TechNode):
        """Create a single dpg node."""
        color = self.get_section_color(node_id)

        with dpg.node(
            label=f"{node.name} ({node.id})",
            parent=self._editor_tag,
            pos=[0, 0],  # Will be set during rebuild
        ) as dpg_node:
            self._node_to_dpg[node_id] = dpg_node
            self._dpg_to_node[dpg_node] = node_id

            # Apply theme color
            with dpg.theme() as node_theme:
                with dpg.theme_component(dpg.mvNode):
                    dpg.add_theme_color(dpg.mvNodeCol_TitleBar, (*color, 200), category=dpg.mvThemeCat_Nodes)
                    dpg.add_theme_color(dpg.mvNodeCol_TitleBarHovered, (*color, 255), category=dpg.mvThemeCat_Nodes)
                    dpg.add_theme_color(dpg.mvNodeCol_TitleBarSelected, (*color, 255), category=dpg.mvThemeCat_Nodes)
            dpg.bind_item_theme(dpg_node, node_theme)

            # Input pins (one per OR-group, or one default)
            self._input_pins[node_id] = {}
            if node.requirements:
                for og_idx in range(len(node.requirements)):
                    label = f"Req" if len(node.requirements) == 1 else f"OR-{og_idx + 1}"
                    with dpg.node_attribute(
                        attribute_type=dpg.mvNode_Attr_Input,
                    ) as input_attr:
                        dpg.add_text(label, color=(180, 180, 180))
                        self._input_pins[node_id][og_idx] = input_attr
            else:
                # Root node — still add an input pin for potential new connections
                with dpg.node_attribute(
                    attribute_type=dpg.mvNode_Attr_Input,
                ) as input_attr:
                    dpg.add_text("Req", color=(180, 180, 180))
                    self._input_pins[node_id][0] = input_attr

            # Static info display
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_text(
                    f"Lv {node.max_levels} | {node.price_curve} | P:{node.price:.2f}",
                    color=(200, 200, 200),
                )

            # Output pin
            with dpg.node_attribute(
                attribute_type=dpg.mvNode_Attr_Output,
            ) as output_attr:
                dpg.add_text("Out", color=(180, 180, 180))
                self._output_pins[node_id] = output_attr

    def _create_link(self, link_info: Dict[str, Any]):
        """Create a single dpg link from link info dict."""
        source_id = link_info["source_id"]
        target_id = link_info["target_id"]
        og_idx = link_info["or_group_index"]

        source_pin = self._output_pins.get(source_id)
        target_pins = self._input_pins.get(target_id, {})
        target_pin = target_pins.get(og_idx)

        if source_pin is None or target_pin is None:
            return

        link_key = f"{source_id}|{target_id}|{og_idx}"

        link_tag = dpg.add_node_link(
            source_pin,
            target_pin,
            parent=self._editor_tag,
        )

        self._link_to_dpg[link_key] = link_tag
        self._dpg_to_link[link_tag] = link_key

        # Color negated links differently
        if link_info.get("negate"):
            with dpg.theme() as link_theme:
                with dpg.theme_component(dpg.mvNodeLink):
                    dpg.add_theme_color(dpg.mvNodeCol_Link, (255, 80, 80, 200), category=dpg.mvThemeCat_Nodes)
                    dpg.add_theme_color(dpg.mvNodeCol_LinkHovered, (255, 120, 120, 255), category=dpg.mvThemeCat_Nodes)
                    dpg.add_theme_color(dpg.mvNodeCol_LinkSelected, (255, 50, 50, 255), category=dpg.mvThemeCat_Nodes)
            dpg.bind_item_theme(link_tag, link_theme)

    def _on_link_created(self, sender, app_data):
        """Callback when user drags a new link."""
        # app_data is (output_attr_id, input_attr_id)
        if not app_data or len(app_data) < 2:
            return

        output_attr = app_data[0]
        input_attr = app_data[1]

        # Resolve to model IDs
        source_id = self._find_node_for_output_pin(output_attr)
        target_id, og_idx = self._find_node_for_input_pin(input_attr)

        if source_id and target_id and self.on_link_created:
            self.on_link_created(source_id, target_id)

    def _on_link_deleted(self, sender, app_data):
        """Callback when user deletes a link."""
        link_tag = app_data
        if link_tag in self._dpg_to_link and self.on_link_deleted:
            self.on_link_deleted(link_tag)

    def _find_node_for_output_pin(self, attr_tag: int) -> Optional[str]:
        """Find the node_id that owns this output pin."""
        for node_id, pin_tag in self._output_pins.items():
            if pin_tag == attr_tag:
                return node_id
        return None

    def _find_node_for_input_pin(self, attr_tag: int) -> Tuple[Optional[str], int]:
        """Find the node_id and OR-group index for this input pin."""
        for node_id, og_pins in self._input_pins.items():
            for og_idx, pin_tag in og_pins.items():
                if pin_tag == attr_tag:
                    return node_id, og_idx
        return None, 0

    def get_link_key(self, dpg_link_tag: int) -> Optional[str]:
        """Get the link key string for a dpg link tag."""
        return self._dpg_to_link.get(dpg_link_tag)

    def parse_link_key(self, link_key: str) -> Tuple[str, str, int]:
        """Parse a link key into (source_id, target_id, or_group_index)."""
        parts = link_key.split("|")
        return parts[0], parts[1], int(parts[2])

    def get_selected_nodes(self) -> List[str]:
        """Get model IDs of currently selected nodes."""
        selected = dpg.get_selected_nodes(self._editor_tag)
        return [self._dpg_to_node[tag] for tag in selected if tag in self._dpg_to_node]

    def get_selected_links(self) -> List[str]:
        """Get link keys of currently selected links."""
        selected = dpg.get_selected_links(self._editor_tag)
        return [self._dpg_to_link[tag] for tag in selected if tag in self._dpg_to_link]

    def get_node_positions(self) -> Dict[str, Tuple[float, float]]:
        """Get current positions of all nodes from dpg."""
        positions = {}
        for node_id, dpg_tag in self._node_to_dpg.items():
            if dpg.does_item_exist(dpg_tag):
                pos = dpg.get_item_pos(dpg_tag)
                positions[node_id] = (float(pos[0]), float(pos[1]))
        return positions

    def update_node_label(self, node_id: str, node: TechNode):
        """Update the display label for a node."""
        dpg_tag = self._node_to_dpg.get(node_id)
        if dpg_tag and dpg.does_item_exist(dpg_tag):
            dpg.configure_item(dpg_tag, label=f"{node.name} ({node.id})")
