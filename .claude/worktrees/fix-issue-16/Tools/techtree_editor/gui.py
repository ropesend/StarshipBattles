"""
Dear PyGui GUI for the Tech Tree Editor.

Creates the main window with:
- Node editor canvas (center)
- Property panel (right sidebar)
- Menu bar (top)
- Validation/balance panel (bottom)
"""
import dearpygui.dearpygui as dpg
from typing import Optional

from game.research.data.tech_node import TechNode

from .app import App
from .model import PRICE_CURVES
from .node_graph import NodeGraph
from .balance import estimate_node_balance, find_outliers, RP_LEVELS


# Layout constants
SIDEBAR_WIDTH = 380
BOTTOM_PANEL_HEIGHT = 200
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080


class EditorGUI:
    """Main GUI class for the Tech Tree Editor."""

    def __init__(self, app: App):
        self.app = app
        self.graph: Optional[NodeGraph] = None

        # DPG tags for updateable widgets
        self._prop_group: Optional[int] = None
        self._validation_text: Optional[int] = None
        self._balance_group: Optional[int] = None
        self._status_text: Optional[int] = None
        self._title_needs_update: bool = False

        # Property panel input tags
        self._prop_tags = {}

        # Polling state for selection changes
        self._last_selected_nodes = []
        self._last_selected_links = []

    def setup(self):
        """Initialize Dear PyGui and create the GUI."""
        dpg.create_context()
        dpg.create_viewport(
            title=self.app.window_title,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
        )

        # Global key handlers
        with dpg.handler_registry():
            dpg.add_key_press_handler(dpg.mvKey_Z, callback=self._on_key_undo)
            dpg.add_key_press_handler(dpg.mvKey_Y, callback=self._on_key_redo)
            dpg.add_key_press_handler(dpg.mvKey_S, callback=self._on_key_save)
            dpg.add_key_press_handler(dpg.mvKey_Delete, callback=self._on_key_delete)

        self._build_main_window()

        dpg.setup_dearpygui()
        dpg.show_viewport()

    def _build_main_window(self):
        """Build the main window layout."""
        with dpg.window(tag="main_window"):
            self._build_menu_bar()

            # Main content area: horizontal layout
            with dpg.group(horizontal=True):
                # Node editor (fills remaining space)
                with dpg.child_window(
                    tag="editor_panel",
                    width=-SIDEBAR_WIDTH,
                    height=-BOTTOM_PANEL_HEIGHT,
                    no_scrollbar=True,
                ):
                    self.graph = NodeGraph(self.app.model)
                    self.graph.on_link_created = self._on_link_created
                    self.graph.on_link_deleted = self._on_link_deleted
                    self.graph.create_editor(parent="editor_panel")

                # Right sidebar: properties
                with dpg.child_window(
                    tag="sidebar",
                    width=SIDEBAR_WIDTH,
                    height=-BOTTOM_PANEL_HEIGHT,
                ):
                    dpg.add_text("Properties", color=(255, 255, 100))
                    dpg.add_separator()
                    self._prop_group = dpg.add_group(tag="prop_group")
                    dpg.add_text("Select a node to view properties", parent=self._prop_group, tag="prop_placeholder")

            # Bottom panel: validation + balance + status
            with dpg.child_window(tag="bottom_panel", height=BOTTOM_PANEL_HEIGHT):
                with dpg.tab_bar():
                    with dpg.tab(label="Validation"):
                        self._validation_text = dpg.add_text(
                            "Press Ctrl+V or use menu to validate",
                            wrap=WINDOW_WIDTH - 40,
                        )
                    with dpg.tab(label="Balance Preview"):
                        self._balance_group = dpg.add_group(tag="balance_group")
                    with dpg.tab(label="Outliers"):
                        self._outlier_group = dpg.add_group(tag="outlier_group")

                self._status_text = dpg.add_text("Ready", color=(150, 150, 150))

        dpg.set_primary_window("main_window", True)

    def _build_menu_bar(self):
        """Build the menu bar."""
        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Open...", callback=self._on_open)
                dpg.add_menu_item(label="Save", callback=self._on_save, shortcut="Ctrl+S")
                dpg.add_menu_item(label="Save As...", callback=self._on_save_as)
                dpg.add_separator()
                dpg.add_menu_item(label="Exit", callback=self._on_exit)

            with dpg.menu(label="Edit"):
                dpg.add_menu_item(label="Undo", callback=self._on_undo, shortcut="Ctrl+Z")
                dpg.add_menu_item(label="Redo", callback=self._on_redo, shortcut="Ctrl+Y")
                dpg.add_separator()
                dpg.add_menu_item(label="Add Node...", callback=self._show_add_node_dialog)
                dpg.add_menu_item(label="Delete Selected", callback=self._on_delete_selected, shortcut="Del")
                dpg.add_separator()
                dpg.add_menu_item(label="Add OR-Group to Selected", callback=self._on_add_or_group)

            with dpg.menu(label="View"):
                dpg.add_menu_item(label="Reset Layout", callback=self._on_reset_layout)
                dpg.add_menu_item(label="Validate", callback=self._on_validate)
                dpg.add_menu_item(label="Balance Preview", callback=self._on_balance_preview)
                dpg.add_menu_item(label="Show Outliers", callback=self._on_show_outliers)

            with dpg.menu(label="Sections"):
                dpg.add_menu_item(label="New Section...", callback=self._show_new_section_dialog)

    # ── File Dialogs ─────────────────────────────────────────────────

    def _on_open(self):
        dpg.add_file_dialog(
            callback=self._on_file_selected,
            default_path=self.app.get_default_file_path(),
            file_count=1,
            directory_selector=False,
            modal=True,
            width=700,
            height=400,
        )

    def _on_file_selected(self, sender, app_data):
        if app_data and "file_path_name" in app_data:
            path = app_data["file_path_name"]
            errors = self.app.load_file(path)
            self.graph.model = self.app.model
            self.graph.rebuild()
            self._update_title()
            if errors:
                self._set_status(f"Loaded with {len(errors)} validation warnings")
            else:
                self._set_status(f"Loaded {len(self.app.model.nodes)} nodes")

    def _on_save(self):
        if self.app.model.file_path:
            self._sync_positions_from_graph()
            success = self.app.save_file()
            self._update_title()
            self._set_status("Saved" if success else "Save failed!")
        else:
            self._on_save_as()

    def _on_save_as(self):
        dpg.add_file_dialog(
            callback=self._on_save_as_selected,
            default_path=self.app.get_default_file_path(),
            file_count=1,
            directory_selector=False,
            modal=True,
            width=700,
            height=400,
        )

    def _on_save_as_selected(self, sender, app_data):
        if app_data and "file_path_name" in app_data:
            path = app_data["file_path_name"]
            self._sync_positions_from_graph()
            success = self.app.save_file(path)
            self._update_title()
            self._set_status("Saved" if success else "Save failed!")

    def _on_exit(self):
        if self.app.model.dirty:
            self._show_confirm_dialog(
                "Unsaved Changes",
                "You have unsaved changes. Exit anyway?",
                self._do_exit,
            )
        else:
            self._do_exit()

    def _do_exit(self):
        dpg.stop_dearpygui()

    # ── Undo/Redo ────────────────────────────────────────────────────

    def _on_undo(self):
        desc = self.app.undo()
        if desc:
            self.graph.rebuild()
            self._set_status(f"Undo: {desc}")
            self._update_title()
            self._update_property_panel()

    def _on_redo(self):
        desc = self.app.redo()
        if desc:
            self.graph.rebuild()
            self._set_status(f"Redo: {desc}")
            self._update_title()
            self._update_property_panel()

    # ── Key Handlers ─────────────────────────────────────────────────

    def _on_key_undo(self):
        if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
            self._on_undo()

    def _on_key_redo(self):
        if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
            self._on_redo()

    def _on_key_save(self):
        if dpg.is_key_down(dpg.mvKey_LControl) or dpg.is_key_down(dpg.mvKey_RControl):
            self._on_save()

    def _on_key_delete(self):
        self._on_delete_selected()

    # ── Node/Link Operations ─────────────────────────────────────────

    def _on_link_created(self, source_id: str, target_id: str):
        """Called when user drags a new link in the node editor."""
        self.app.add_link(source_id, target_id)
        self.graph.rebuild()
        self._set_status(f"Added link: {source_id} → {target_id}")
        self._update_title()

    def _on_link_deleted(self, dpg_link_tag: int):
        """Called when user deletes a link in the node editor."""
        link_key = self.graph.get_link_key(dpg_link_tag)
        if link_key:
            source_id, target_id, og_idx = self.graph.parse_link_key(link_key)
            self.app.remove_link(source_id, target_id, og_idx)
            self.graph.rebuild()
            self._set_status(f"Removed link: {source_id} → {target_id}")
            self._update_title()

    def _on_delete_selected(self):
        """Delete selected nodes or links."""
        selected_nodes = self.graph.get_selected_nodes()
        selected_links = self.graph.get_selected_links()

        for link_key in selected_links:
            source_id, target_id, og_idx = self.graph.parse_link_key(link_key)
            self.app.remove_link(source_id, target_id, og_idx)

        for node_id in selected_nodes:
            self.app.delete_node(node_id)

        if selected_nodes or selected_links:
            self.graph.rebuild()
            self._set_status(f"Deleted {len(selected_nodes)} nodes, {len(selected_links)} links")
            self._update_title()
            self._update_property_panel()

    def _on_add_or_group(self):
        """Add an OR-group to the selected node."""
        if self.app.selected_node_id:
            self.app.add_or_group(self.app.selected_node_id)
            self.graph.rebuild()
            self._set_status(f"Added OR-group to {self.app.selected_node_id}")

    # ── Add Node Dialog ──────────────────────────────────────────────

    def _show_add_node_dialog(self):
        if dpg.does_item_exist("add_node_dialog"):
            dpg.delete_item("add_node_dialog")

        section_names = self.app.model.get_section_names()

        with dpg.window(
            label="Add New Node",
            modal=True,
            tag="add_node_dialog",
            width=400,
            height=200,
            pos=[WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 100],
        ):
            dpg.add_text("Create a new tech node")
            dpg.add_separator()

            dpg.add_input_text(label="Node ID", tag="new_node_id", default_value=self.app.model.get_next_id("AS"))
            dpg.add_input_text(label="Name", tag="new_node_name", default_value="New Technology")
            dpg.add_combo(
                label="Section",
                tag="new_node_section",
                items=section_names,
                default_value=section_names[0] if section_names else "",
            )

            with dpg.group(horizontal=True):
                dpg.add_button(label="Create", callback=self._on_add_node_confirm)
                dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("add_node_dialog"))

    def _on_add_node_confirm(self):
        node_id = dpg.get_value("new_node_id")
        name = dpg.get_value("new_node_name")
        section = dpg.get_value("new_node_section")

        if not node_id or not name:
            self._set_status("Node ID and name are required")
            return

        if node_id in self.app.model.nodes:
            self._set_status(f"Node ID '{node_id}' already exists")
            return

        node = self.app.add_node(node_id, name, section or None)
        if node:
            # Position near center of viewport
            self.app.model.set_position(node_id, 400.0, 300.0)
            self.graph.rebuild()
            self._set_status(f"Added node: {name} ({node_id})")
            self._update_title()

        if dpg.does_item_exist("add_node_dialog"):
            dpg.delete_item("add_node_dialog")

    # ── New Section Dialog ───────────────────────────────────────────

    def _show_new_section_dialog(self):
        if dpg.does_item_exist("new_section_dialog"):
            dpg.delete_item("new_section_dialog")

        with dpg.window(
            label="New Section",
            modal=True,
            tag="new_section_dialog",
            width=400,
            height=120,
            pos=[WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 60],
        ):
            dpg.add_input_text(label="Section Name", tag="new_section_name", default_value="--- NEW BRANCH ---")
            with dpg.group(horizontal=True):
                dpg.add_button(label="Create", callback=self._on_new_section_confirm)
                dpg.add_button(label="Cancel", callback=lambda: dpg.delete_item("new_section_dialog"))

    def _on_new_section_confirm(self):
        name = dpg.get_value("new_section_name")
        if name:
            self.app.create_section(name)
            self._set_status(f"Created section: {name}")
        if dpg.does_item_exist("new_section_dialog"):
            dpg.delete_item("new_section_dialog")

    # ── Confirm Dialog ───────────────────────────────────────────────

    def _show_confirm_dialog(self, title: str, message: str, on_confirm):
        if dpg.does_item_exist("confirm_dialog"):
            dpg.delete_item("confirm_dialog")

        with dpg.window(
            label=title,
            modal=True,
            tag="confirm_dialog",
            width=400,
            height=120,
            pos=[WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 60],
        ):
            dpg.add_text(message)
            with dpg.group(horizontal=True):
                dpg.add_button(label="Yes", callback=lambda: (dpg.delete_item("confirm_dialog"), on_confirm()))
                dpg.add_button(label="No", callback=lambda: dpg.delete_item("confirm_dialog"))

    # ── Property Panel ───────────────────────────────────────────────

    def _update_property_panel(self):
        """Update the property panel for the currently selected node."""
        # Clear existing
        if dpg.does_item_exist("prop_group"):
            children = dpg.get_item_children("prop_group", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)

        self._prop_tags.clear()
        node_id = self.app.selected_node_id

        if not node_id or node_id not in self.app.model.nodes:
            dpg.add_text("Select a node to view properties", parent="prop_group")
            return

        node = self.app.model.nodes[node_id]
        section = self.app.model.get_section_for_node(node_id)
        parent = "prop_group"

        # Header
        dpg.add_text(f"{node.name}", parent=parent, color=(255, 255, 100))
        dpg.add_text(f"ID: {node.id}", parent=parent, color=(150, 150, 150))
        if section:
            dpg.add_text(f"Section: {section.name}", parent=parent, color=(150, 150, 150))
        dpg.add_separator(parent=parent)

        # Editable fields
        dpg.add_text("Node Properties", parent=parent, color=(200, 200, 255))

        self._prop_tags["name"] = dpg.add_input_text(
            label="Name", default_value=node.name, parent=parent,
            callback=lambda s, a: self._on_prop_changed("name", a),
            on_enter=True,
        )
        self._prop_tags["max_levels"] = dpg.add_input_int(
            label="Max Levels", default_value=node.max_levels, parent=parent,
            min_value=1, max_value=50, min_clamped=True, max_clamped=True,
            callback=lambda s, a: self._on_prop_changed("max_levels", a),
            on_enter=True,
        )
        self._prop_tags["base_decay"] = dpg.add_input_float(
            label="Base Decay", default_value=node.base_decay, parent=parent,
            min_value=0.0, max_value=1.0, min_clamped=True, max_clamped=True,
            format="%.4f", step=0.001,
            callback=lambda s, a: self._on_prop_changed("base_decay", a),
            on_enter=True,
        )
        self._prop_tags["volatility"] = dpg.add_input_float(
            label="Volatility", default_value=node.volatility, parent=parent,
            min_value=0.0, max_value=1.0, min_clamped=True, max_clamped=True,
            format="%.4f", step=0.01,
            callback=lambda s, a: self._on_prop_changed("volatility", a),
            on_enter=True,
        )
        self._prop_tags["price"] = dpg.add_input_float(
            label="Price", default_value=node.price, parent=parent,
            min_value=0.01, max_value=100.0, min_clamped=True, max_clamped=True,
            format="%.2f", step=0.1,
            callback=lambda s, a: self._on_prop_changed("price", a),
            on_enter=True,
        )
        self._prop_tags["price_curve"] = dpg.add_combo(
            label="Price Curve",
            items=list(PRICE_CURVES),
            default_value=node.price_curve,
            parent=parent,
            callback=lambda s, a: self._on_prop_changed("price_curve", a),
        )

        # Section assignment
        dpg.add_separator(parent=parent)
        dpg.add_text("Section Assignment", parent=parent, color=(200, 200, 255))
        dpg.add_combo(
            label="Move to Section",
            items=self.app.model.get_section_names(),
            default_value=section.name if section else "",
            parent=parent,
            callback=lambda s, a: self._on_section_changed(a),
        )

        # Requirements display
        dpg.add_separator(parent=parent)
        dpg.add_text("Requirements", parent=parent, color=(200, 200, 255))

        if not node.requirements:
            dpg.add_text("  (none — root node)", parent=parent, color=(150, 150, 150))
        else:
            for og_idx, or_group in enumerate(node.requirements):
                if len(node.requirements) > 1:
                    dpg.add_text(f"  OR-Group {og_idx + 1}:", parent=parent, color=(180, 180, 255))
                for req_idx, req in enumerate(or_group):
                    prereq_name = self.app.model.nodes.get(req.node_id, None)
                    name_str = prereq_name.name if prereq_name else req.node_id
                    negate_str = " [NEGATED]" if req.negate else ""
                    dpg.add_text(
                        f"    {name_str} Lv {req.level_range[0]}-{req.level_range[1]}{negate_str}",
                        parent=parent,
                        color=(255, 100, 100) if req.negate else (150, 255, 150),
                    )

                    # Editable controls for this requirement
                    with dpg.group(horizontal=True, parent=parent):
                        dpg.add_text("      ")
                        # Store indices for callback closure
                        _og = og_idx
                        _ri = req_idx
                        dpg.add_input_int(
                            label="", default_value=req.level_range[0], width=50,
                            min_value=1, max_value=50, min_clamped=True, max_clamped=True,
                            callback=lambda s, a, og=_og, ri=_ri: self._on_req_level_min_changed(og, ri, a),
                            on_enter=True,
                        )
                        dpg.add_text("-")
                        dpg.add_input_int(
                            label="", default_value=req.level_range[1], width=50,
                            min_value=1, max_value=50, min_clamped=True, max_clamped=True,
                            callback=lambda s, a, og=_og, ri=_ri: self._on_req_level_max_changed(og, ri, a),
                            on_enter=True,
                        )
                        dpg.add_checkbox(
                            label="Negate",
                            default_value=req.negate,
                            callback=lambda s, a, og=_og, ri=_ri: self._on_req_negate_changed(og, ri, a),
                        )

        # Balance preview for this node
        dpg.add_separator(parent=parent)
        dpg.add_text("Balance (Level 1)", parent=parent, color=(200, 200, 255))
        metrics = estimate_node_balance(node, level=1)
        dpg.add_text(f"  Effective price: {metrics['effective_price']:.2f}", parent=parent)
        for rp, data in metrics["rp_levels"].items():
            color = (255, 100, 100) if data["starvation"] else (150, 255, 150)
            turns_str = f"{data['est_turns']:.0f}" if data["est_turns"] != float('inf') else "INF"
            dpg.add_text(
                f"  RP={rp}: net {data['net_chance']:.4f}/turn, ~{turns_str} turns",
                parent=parent,
                color=color,
            )

    def _on_prop_changed(self, prop: str, value):
        """Handle property change from the panel."""
        if self.app.selected_node_id:
            self.app.edit_node_property(self.app.selected_node_id, prop, value)
            # Update node label in graph
            node = self.app.model.nodes.get(self.app.selected_node_id)
            if node:
                self.graph.update_node_label(self.app.selected_node_id, node)
            self._update_title()

    def _on_section_changed(self, section_name: str):
        """Handle section change from the panel."""
        if self.app.selected_node_id and section_name:
            self.app.move_node_to_section(self.app.selected_node_id, section_name)
            self.graph.rebuild()
            self._update_title()

    def _on_req_level_min_changed(self, og_idx: int, req_idx: int, value: int):
        """Handle requirement level_range min change."""
        if not self.app.selected_node_id:
            return
        node = self.app.model.nodes.get(self.app.selected_node_id)
        if not node or og_idx >= len(node.requirements) or req_idx >= len(node.requirements[og_idx]):
            return
        req = node.requirements[og_idx][req_idx]
        new_range = (value, max(value, req.level_range[1]))
        self.app.edit_requirement(self.app.selected_node_id, og_idx, req_idx, level_range=new_range)
        self._update_title()

    def _on_req_level_max_changed(self, og_idx: int, req_idx: int, value: int):
        """Handle requirement level_range max change."""
        if not self.app.selected_node_id:
            return
        node = self.app.model.nodes.get(self.app.selected_node_id)
        if not node or og_idx >= len(node.requirements) or req_idx >= len(node.requirements[og_idx]):
            return
        req = node.requirements[og_idx][req_idx]
        new_range = (min(value, req.level_range[0]), value)
        self.app.edit_requirement(self.app.selected_node_id, og_idx, req_idx, level_range=new_range)
        self._update_title()

    def _on_req_negate_changed(self, og_idx: int, req_idx: int, value: bool):
        """Handle requirement negate toggle."""
        if self.app.selected_node_id:
            self.app.edit_requirement(self.app.selected_node_id, og_idx, req_idx, negate=value)
            self._update_title()

    # ── Layout ───────────────────────────────────────────────────────

    def _on_reset_layout(self):
        self.app.reset_layout()
        self.graph.rebuild()
        self._set_status("Layout reset to auto-layout")

    # ── Validation ───────────────────────────────────────────────────

    def _on_validate(self):
        errors = self.app.validate()
        if errors:
            text = f"Found {len(errors)} issue(s):\n" + "\n".join(f"  - {e}" for e in errors)
            color = (255, 200, 100)
        else:
            text = "Validation passed — no issues found"
            color = (100, 255, 100)

        if dpg.does_item_exist(self._validation_text):
            dpg.set_value(self._validation_text, text)
            dpg.configure_item(self._validation_text, color=color)
        self._set_status(f"Validation: {len(errors)} issues" if errors else "Validation passed")

    # ── Balance ──────────────────────────────────────────────────────

    def _on_balance_preview(self):
        if dpg.does_item_exist("balance_group"):
            children = dpg.get_item_children("balance_group", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)

        if not self.app.selected_node_id:
            dpg.add_text("Select a node first", parent="balance_group")
            return

        node = self.app.model.nodes.get(self.app.selected_node_id)
        if not node:
            return

        dpg.add_text(f"Balance for: {node.name} ({node.id})", parent="balance_group", color=(255, 255, 100))

        for level in range(1, min(node.max_levels + 1, 6)):
            metrics = estimate_node_balance(node, level)
            dpg.add_text(f"  Level {level} (price: {metrics['effective_price']:.2f}):", parent="balance_group")
            for rp, data in metrics["rp_levels"].items():
                color = (255, 100, 100) if data["starvation"] else (200, 200, 200)
                turns_str = f"{data['est_turns']:.0f}" if data["est_turns"] != float('inf') else "INF"
                dpg.add_text(
                    f"    RP={rp}: net={data['net_chance']:.4f}, ~{turns_str}t",
                    parent="balance_group", color=color,
                )

    def _on_show_outliers(self):
        if dpg.does_item_exist("outlier_group"):
            children = dpg.get_item_children("outlier_group", slot=1)
            if children:
                for child in children:
                    dpg.delete_item(child)

        outliers = find_outliers(self.app.model.nodes)
        if not outliers:
            dpg.add_text("No outliers found at RP=50", parent="outlier_group", color=(100, 255, 100))
            return

        dpg.add_text(f"Found {len(outliers)} outlier(s) at RP=50:", parent="outlier_group", color=(255, 200, 100))
        for nid, est, reason in outliers[:20]:
            node = self.app.model.nodes.get(nid)
            name = node.name if node else nid
            dpg.add_text(f"  {name} ({nid}): {reason}", parent="outlier_group", color=(255, 180, 100))

    # ── Status & Title ───────────────────────────────────────────────

    def _set_status(self, text: str):
        if dpg.does_item_exist(self._status_text):
            dpg.set_value(self._status_text, text)

    def _update_title(self):
        dpg.set_viewport_title(self.app.window_title)

    def _sync_positions_from_graph(self):
        """Sync node positions from dpg back to the model."""
        if self.graph:
            positions = self.graph.get_node_positions()
            for node_id, pos in positions.items():
                self.app.model.set_position(node_id, pos[0], pos[1])

    # ── Main Loop ────────────────────────────────────────────────────

    def run(self):
        """Run the Dear PyGui render loop with selection polling."""
        while dpg.is_dearpygui_running():
            self._poll_selection()
            dpg.render_dearpygui_frame()

        # Cleanup
        self._sync_positions_from_graph()
        dpg.destroy_context()

    def _poll_selection(self):
        """Poll for node/link selection changes."""
        if not self.graph or not self.graph._editor_tag:
            return

        selected_nodes = self.graph.get_selected_nodes()
        selected_links = self.graph.get_selected_links()

        # Node selection changed
        if selected_nodes != self._last_selected_nodes:
            self._last_selected_nodes = selected_nodes
            if selected_nodes:
                self.app.selected_node_id = selected_nodes[0]
                self._update_property_panel()
            elif not selected_links:
                self.app.selected_node_id = None
                self._update_property_panel()

        # Link selection changed
        if selected_links != self._last_selected_links:
            self._last_selected_links = selected_links
            if selected_links and not selected_nodes:
                self.app.selected_link_key = selected_links[0]
            else:
                self.app.selected_link_key = None
