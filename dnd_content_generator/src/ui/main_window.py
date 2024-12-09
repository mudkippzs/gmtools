import os
import glob
import json

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QLabel, QTreeWidget,
    QTreeWidgetItem, QPushButton, QSplitter, QTextEdit, QFrame, QProgressDialog,
    QComboBox, QDialog, QScrollArea
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush

from src.ui.dialogs import show_error, show_info
from src.utils import load_config
from src.services.logger import logger
from src.ui.results_view import ResultsView
from src.ui.options_panel import OptionsPanel


class MainWindow(QMainWindow):
    def __init__(self, app_controller, parent=None):
        super().__init__(parent)
        self.app_controller = app_controller
        self.config = load_config("src/config/config.json")
        self.ui_config = self.config.get("ui", {})
        self.setWindowTitle("D&D Content Generator")

        main_splitter = QSplitter(Qt.Horizontal, self)

        # --- Left panel: Categories and Contexts ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)

        categories_files = sorted(glob.glob("src/resources/*_categories.json"))
        contexts_files = sorted(glob.glob("src/resources/*_contexts.json"))

        # File selectors for categories and contexts
        file_selection_layout = QHBoxLayout()
        file_selection_layout.setContentsMargins(0,0,0,0)
        file_selection_layout.setSpacing(5)

        self.category_file_combo = QComboBox()
        self.category_file_combo.addItem("Select a categories file...")
        for cat_file in categories_files:
            self.category_file_combo.addItem(os.path.basename(cat_file))
        self.category_file_combo.currentTextChanged.connect(self.on_category_file_changed)

        self.context_file_combo = QComboBox()
        self.context_file_combo.addItem("Select a contexts file...")
        for ctx_file in contexts_files:
            self.context_file_combo.addItem(os.path.basename(ctx_file))
        self.context_file_combo.currentTextChanged.connect(self.on_context_file_changed)

        file_selection_layout.addWidget(QLabel("Cat. File:"))
        file_selection_layout.addWidget(self.category_file_combo)
        file_selection_layout.addWidget(QLabel("Ctx. File:"))
        file_selection_layout.addWidget(self.context_file_combo)
        left_layout.addLayout(file_selection_layout)

        # Category Breadcrumb Section
        cat_breadcrumb_container = QWidget()
        cat_breadcrumb_container_layout = QVBoxLayout(cat_breadcrumb_container)
        cat_breadcrumb_container_layout.setContentsMargins(0,0,0,0)
        cat_breadcrumb_container_layout.setSpacing(0)

        cat_breadcrumb_label = QLabel("<b><small>Breadcrumbs:</small></b>")
        cat_breadcrumb_label.setContentsMargins(0,0,0,0)
        cat_breadcrumb_container_layout.addWidget(cat_breadcrumb_label)

        self.category_breadcrumb_scroll = QScrollArea()
        self.category_breadcrumb_scroll.setWidgetResizable(True)
        self.category_breadcrumb_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.category_breadcrumb_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.category_breadcrumb_scroll.setContentsMargins(0,0,0,0)
        self.category_breadcrumb_scroll.setFixedHeight(30)

        self.category_breadcrumb_content_label = QLabel("")
        self.category_breadcrumb_content_label.setWordWrap(True)
        self.category_breadcrumb_content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.category_breadcrumb_content_label.setContentsMargins(0,0,0,0)

        scroll_content_cat = QWidget()
        scroll_content_cat_layout = QVBoxLayout(scroll_content_cat)
        scroll_content_cat_layout.setContentsMargins(0,0,0,0)
        scroll_content_cat_layout.setSpacing(0)
        scroll_content_cat_layout.addWidget(self.category_breadcrumb_content_label)
        scroll_content_cat.setLayout(scroll_content_cat_layout)

        self.category_breadcrumb_scroll.setWidget(scroll_content_cat)
        cat_breadcrumb_container_layout.addWidget(self.category_breadcrumb_scroll)
        left_layout.addWidget(cat_breadcrumb_container)

        # Category Filter + Tree
        self.category_filter = QLineEdit()
        self.category_filter.setPlaceholderText("Filter categories...")
        self.category_filter.textChanged.connect(self.filter_categories)
        left_layout.addWidget(self.category_filter)

        # Controls for Category Tree
        cat_controls_layout = QHBoxLayout()
        cat_controls_layout.setContentsMargins(0,0,0,0)
        cat_controls_layout.setSpacing(5)

        self.cat_expand_all_btn = QPushButton("Expand All")
        self.cat_expand_all_btn.clicked.connect(lambda: self.set_all_expanded(self.category_tree, True))
        self.cat_collapse_all_btn = QPushButton("Collapse All")
        self.cat_collapse_all_btn.clicked.connect(lambda: self.set_all_expanded(self.category_tree, False))
        self.cat_deselect_all_btn = QPushButton("Deselect All")
        self.cat_deselect_all_btn.clicked.connect(lambda: self.set_all_checked(self.category_tree, Qt.Unchecked))
        self.cat_select_siblings_btn = QPushButton("Select Siblings")
        self.cat_select_siblings_btn.clicked.connect(lambda: self.select_siblings(self.category_tree))
        cat_controls_layout.addWidget(self.cat_expand_all_btn)
        cat_controls_layout.addWidget(self.cat_collapse_all_btn)
        cat_controls_layout.addWidget(self.cat_deselect_all_btn)
        cat_controls_layout.addWidget(self.cat_select_siblings_btn)
        left_layout.addLayout(cat_controls_layout)

        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Categories & Types")
        self.category_tree.setSelectionMode(QTreeWidget.SingleSelection)
        self.category_tree.itemChanged.connect(self.on_item_changed)
        left_layout.addWidget(self.category_tree, 1)  # Stretch factor to give tree more space

        # Context Breadcrumb Section
        ctx_breadcrumb_container = QWidget()
        ctx_breadcrumb_container_layout = QVBoxLayout(ctx_breadcrumb_container)
        ctx_breadcrumb_container_layout.setContentsMargins(0,0,0,0)
        ctx_breadcrumb_container_layout.setSpacing(0)

        ctx_breadcrumb_label = QLabel("<b><small>Breadcrumbs:</small></b>")
        ctx_breadcrumb_label.setContentsMargins(0,0,0,0)
        ctx_breadcrumb_container_layout.addWidget(ctx_breadcrumb_label)

        self.context_breadcrumb_scroll = QScrollArea()
        self.context_breadcrumb_scroll.setWidgetResizable(True)
        self.context_breadcrumb_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.context_breadcrumb_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.context_breadcrumb_scroll.setContentsMargins(0,0,0,0)
        self.context_breadcrumb_scroll.setFixedHeight(30)

        self.context_breadcrumb_content_label = QLabel("")
        self.context_breadcrumb_content_label.setWordWrap(True)
        self.context_breadcrumb_content_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.context_breadcrumb_content_label.setContentsMargins(0,0,0,0)

        scroll_content_ctx = QWidget()
        scroll_content_ctx_layout = QVBoxLayout(scroll_content_ctx)
        scroll_content_ctx_layout.setContentsMargins(0,0,0,0)
        scroll_content_ctx_layout.setSpacing(0)
        scroll_content_ctx_layout.addWidget(self.context_breadcrumb_content_label)
        scroll_content_ctx.setLayout(scroll_content_ctx_layout)

        self.context_breadcrumb_scroll.setWidget(scroll_content_ctx)
        ctx_breadcrumb_container_layout.addWidget(self.context_breadcrumb_scroll)
        left_layout.addWidget(ctx_breadcrumb_container)

        # Context Filter + Tree
        self.context_filter = QLineEdit()
        self.context_filter.setPlaceholderText("Filter contexts...")
        self.context_filter.textChanged.connect(self.filter_contexts)
        left_layout.addWidget(self.context_filter)

        ctx_controls_layout = QHBoxLayout()
        ctx_controls_layout.setContentsMargins(0,0,0,0)
        ctx_controls_layout.setSpacing(5)

        self.ctx_expand_all_btn = QPushButton("Expand All")
        self.ctx_expand_all_btn.clicked.connect(lambda: self.set_all_expanded(self.context_tree, True))
        self.ctx_collapse_all_btn = QPushButton("Collapse All")
        self.ctx_collapse_all_btn.clicked.connect(lambda: self.set_all_expanded(self.context_tree, False))
        self.ctx_deselect_all_btn = QPushButton("Deselect All")
        self.ctx_deselect_all_btn.clicked.connect(lambda: self.set_all_checked(self.context_tree, Qt.Unchecked))
        self.ctx_select_siblings_btn = QPushButton("Select Siblings")
        self.ctx_select_siblings_btn.clicked.connect(lambda: self.select_siblings(self.context_tree))
        ctx_controls_layout.addWidget(self.ctx_expand_all_btn)
        ctx_controls_layout.addWidget(self.ctx_collapse_all_btn)
        ctx_controls_layout.addWidget(self.ctx_deselect_all_btn)
        ctx_controls_layout.addWidget(self.ctx_select_siblings_btn)
        left_layout.addLayout(ctx_controls_layout)

        self.context_tree = QTreeWidget()
        self.context_tree.setHeaderLabel("Contexts")
        self.context_tree.setSelectionMode(QTreeWidget.MultiSelection)
        self.context_tree.itemChanged.connect(self.on_item_changed)
        left_layout.addWidget(self.context_tree, 2)  # More space for contexts as well

        # --- Right side: Options, Campaign Notes, Preview, Results ---
        right_vertical_splitter = QSplitter(Qt.Vertical)
        top_horizontal_splitter = QSplitter(Qt.Horizontal)

        options_container = QWidget()
        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(5,5,5,5)
        options_layout.setSpacing(5)

        self.options_panel = OptionsPanel(on_options_changed=self.on_options_changed)
        self.options_panel.generateRequested.connect(self.generate_content)
        self.options_panel.exportDetailsRequested.connect(self.export_detailed)
        self.options_panel.exportResultsRequested.connect(self.export_results_triggered)
        self.options_panel.moreInfoRequested.connect(self.more_info_triggered)

        options_layout.addWidget(self.options_panel)
        options_layout.addStretch()

        notes_and_preview_container = QWidget()
        notes_layout = QVBoxLayout(notes_and_preview_container)
        notes_layout.setContentsMargins(5,5,5,5)
        notes_layout.setSpacing(5)

        system_setting_layout = QHBoxLayout()
        system_setting_layout.setContentsMargins(0,0,0,0)
        system_setting_layout.setSpacing(5)

        self.system_edit = QLineEdit()
        self.system_edit.setPlaceholderText("Enter RPG system (e.g. D&D 3.5e)")
        self.system_edit.textChanged.connect(self.on_system_text_changed)

        self.setting_edit = QLineEdit()
        self.setting_edit.setPlaceholderText("Enter setting or theme (e.g. Forgotten Realms)")
        self.setting_edit.textChanged.connect(self.on_setting_text_changed)

        system_setting_layout.addWidget(QLabel("System:"))
        system_setting_layout.addWidget(self.system_edit)
        system_setting_layout.addWidget(QLabel("Setting:"))
        system_setting_layout.addWidget(self.setting_edit)

        notes_layout.addLayout(system_setting_layout)

        self.campaign_prompt_edit = QTextEdit()
        self.campaign_prompt_edit.setPlaceholderText("Add campaign-specific instructions here...")
        self.campaign_prompt_edit.textChanged.connect(self.on_campaign_text_changed)
        notes_layout.addWidget(QLabel("Campaign Notes:"))
        notes_layout.addWidget(self.campaign_prompt_edit, 1)

        self.preview_box = QTextEdit()
        self.preview_box.setReadOnly(True)
        preview_frame = QFrame()
        preview_frame.setFrameShape(QFrame.StyledPanel)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(5,5,5,5)
        preview_layout.setSpacing(5)
        preview_layout.addWidget(QLabel("Preview:"))
        preview_layout.addWidget(self.preview_box)
        notes_layout.addWidget(preview_frame, 2)

        top_horizontal_splitter.addWidget(options_container)
        top_horizontal_splitter.addWidget(notes_and_preview_container)
        top_horizontal_splitter.setStretchFactor(0, 1)
        top_horizontal_splitter.setStretchFactor(1, 3)

        results_container = QWidget()
        results_layout = QVBoxLayout(results_container)
        results_layout.setContentsMargins(5,5,5,5)
        results_layout.setSpacing(5)

        self.results_view = ResultsView()
        self.results_view.table.itemSelectionChanged.connect(self.update_preview)
        self.results_view.setMinimumHeight(300)
        results_layout.addWidget(self.results_view)

        right_vertical_splitter.addWidget(top_horizontal_splitter)
        right_vertical_splitter.addWidget(results_container)
        right_vertical_splitter.setStretchFactor(0, 1)
        right_vertical_splitter.setStretchFactor(1, 2)

        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_vertical_splitter)
        self.resize(1920, 1080)
        main_splitter.setSizes([int(self.width() * 0.15), int(self.width() * 0.85)])
        self.setCentralWidget(main_splitter)

        self._show_category_placeholder()
        self._show_context_placeholder()

    def _show_category_placeholder(self):
        self.category_tree.clear()
        placeholder_item = QTreeWidgetItem(["Select a Category..."])
        placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsUserCheckable)
        self.category_tree.addTopLevelItem(placeholder_item)

    def _show_context_placeholder(self):
        self.context_tree.clear()
        placeholder_item = QTreeWidgetItem(["Select a Context..."])
        placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsUserCheckable)
        self.context_tree.addTopLevelItem(placeholder_item)

    def on_category_file_changed(self, filename):
        if filename.startswith("Select"):
            self.app_controller.set_categories_file("")
            self.app_controller.reload_categories()
            self._show_category_placeholder()
        else:
            self.app_controller.set_categories_file(filename)
            self.app_controller.reload_categories()
            self._populate_category_tree()
        self.on_category_type_selected()  # Refresh breadcrumb

    def on_context_file_changed(self, filename):
        if filename.startswith("Select"):
            self.app_controller.set_contexts_file("")
            self.app_controller.reload_contexts()
            self._show_context_placeholder()
        else:
            self.app_controller.set_contexts_file(filename)
            self.app_controller.reload_contexts()
            self._populate_context_tree()
        self.on_context_selected()  # Refresh breadcrumb

    def _populate_category_tree(self):
        self.category_tree.clear()
        categories = self.app_controller.categories
        if not categories:
            placeholder_item = QTreeWidgetItem(["Select a Category..."])
            placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsUserCheckable)
            self.category_tree.addTopLevelItem(placeholder_item)
            return

        for top_key, top_value in categories.items():
            top_item = QTreeWidgetItem([top_key])
            self.category_tree.addTopLevelItem(top_item)
            self._add_items(top_item, top_value)
        self.apply_color_coding(self.category_tree)
        self._finalize_tree_checkstates(self.category_tree)

    def _populate_context_tree(self):
        self.context_tree.clear()
        contexts = self.app_controller.contexts
        if not contexts:
            placeholder_item = QTreeWidgetItem(["Select a Context..."])
            placeholder_item.setFlags(placeholder_item.flags() & ~Qt.ItemIsUserCheckable)
            self.context_tree.addTopLevelItem(placeholder_item)
            return

        for top_key, top_value in contexts.items():
            top_item = QTreeWidgetItem([top_key])
            self.context_tree.addTopLevelItem(top_item)
            self._add_context_items(top_item, top_value)
        self.apply_color_coding(self.context_tree)
        self._finalize_tree_checkstates(self.context_tree)

    def _add_items(self, parent_item, data):
        if isinstance(data, dict):
            for key, value in data.items():
                node = QTreeWidgetItem([key])
                parent_item.addChild(node)
                self._add_items(node, value)
        elif isinstance(data, list):
            for val in data:
                leaf = QTreeWidgetItem([val])
                parent_item.addChild(leaf)

    def _add_context_items(self, parent_item, data):
        if isinstance(data, dict):
            for key, value in data.items():
                node = QTreeWidgetItem([key])
                parent_item.addChild(node)
                self._add_context_items(node, value)
        elif isinstance(data, list):
            for val in data:
                leaf = QTreeWidgetItem([val])
                parent_item.addChild(leaf)

    def _finalize_tree_checkstates(self, tree):
        def finalize_item(item):
            if item.childCount() > 0:
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                item.setCheckState(0, Qt.Unchecked)
                for i in range(item.childCount()):
                    finalize_item(item.child(i))
            else:
                flags = item.flags() | Qt.ItemIsUserCheckable
                item.setFlags(flags & ~Qt.ItemIsTristate)
                item.setCheckState(0, Qt.Unchecked)

        for i in range(tree.topLevelItemCount()):
            top_item = tree.topLevelItem(i)
            finalize_item(top_item)

    def on_item_changed(self, item, column):
        if column != 0:
            return
        self.propagate_check_state_to_children(item, item.checkState(0))
        # After changing checks, update categories and contexts accordingly
        self.on_category_type_selected()
        self.on_context_selected()

    def propagate_check_state_to_children(self, item, state):
        for i in range(item.childCount()):
            child = item.child(i)
            child.setCheckState(0, state)
            self.propagate_check_state_to_children(child, state)

    def get_checked_leaves(self, tree):
        """Return a list of all checked leaf node texts from the given QTreeWidget."""
        checked_items = []
        def recurse(node):
            if node.childCount() == 0 and node.checkState(0) == Qt.Checked:
                checked_items.append(node.text(0))
            for i in range(node.childCount()):
                recurse(node.child(i))
        for i in range(tree.topLevelItemCount()):
            top = tree.topLevelItem(i)
            recurse(top)
        return checked_items

    def on_category_type_selected(self):
        # Gather all checked leaves from category tree
        checked_categories = self.get_checked_leaves(self.category_tree)
        if checked_categories:
            lines = self._group_siblings(self.category_tree, checked_categories)
            breadcrumb_text = " | ".join(lines)
            self.update_category_breadcrumb(breadcrumb_text)
        else:
            self.app_controller.set_category(None)
            self.app_controller.set_type(None)
            self.update_category_breadcrumb("")

    def on_context_selected(self):
        # Gather all checked leaves from context tree
        checked_contexts = self.get_checked_leaves(self.context_tree)
        if checked_contexts:
            lines = self._group_siblings(self.context_tree, checked_contexts)
            breadcrumb_text = " | ".join(lines)
            self.update_context_breadcrumb(breadcrumb_text)
        else:
            self.app_controller.set_contexts([])
            self.update_context_breadcrumb("")

    def _group_siblings(self, tree, checked_leaves):
        """
        Given a tree and a list of checked leaves, group siblings by their parent.
        Returns a list of strings like "Parent: child1, child2" or single-level items.
        Also updates the app_controller accordingly.
        """
        def find_parents(item):
            parts = []
            current = item
            while current is not None:
                parts.insert(0, current.text(0))
                current = current.parent()
            return parts

        def find_item_by_text(root_item, text):
            if root_item.text(0) == text and root_item.childCount() == 0:
                return root_item
            for idx in range(root_item.childCount()):
                found = find_item_by_text(root_item.child(idx), text)
                if found:
                    return found
            return None

        parent_map = {}
        root = tree.invisibleRootItem()

        for leaf_text in checked_leaves:
            found_item = None
            for i in range(root.childCount()):
                top_item = root.child(i)
                found_item = find_item_by_text(top_item, leaf_text)
                if found_item:
                    break
            if found_item:
                path = find_parents(found_item)
                if len(path) > 1:
                    parent = path[-2]
                    child = path[-1]
                    parent_map.setdefault(parent, []).append(child)
                else:
                    parent_map.setdefault(path[-1], [])

        lines = []
        categories_used = set()
        types_used = set()
        # For contexts, we just gather them all together
        contexts_used = []

        for parent, children in parent_map.items():
            if children:
                lines.append(f"{parent}: {', '.join(children)}")
                categories_used.add(parent)
                types_used.update(children)
                contexts_used.extend(children)
            else:
                lines.append(parent)
                categories_used.add(parent)
                contexts_used.append(parent)

        if tree == self.category_tree:
            self.app_controller.set_category(", ".join(categories_used) if categories_used else None)
            self.app_controller.set_type(", ".join(types_used) if types_used else None)
        else:
            self.app_controller.set_contexts(contexts_used)

        return lines

    def filter_categories(self):
        filter_text = self.category_filter.text().strip().lower()
        if not filter_text:
            self._set_tree_items_visible(self.category_tree, True)
        else:
            self._filter_tree(self.category_tree, filter_text)

    def filter_contexts(self):
        filter_text = self.context_filter.text().strip().lower()
        if not filter_text:
            self._set_tree_items_visible(self.context_tree, True)
        else:
            self._filter_tree(self.context_tree, filter_text)

    def _filter_tree(self, tree, text):
        for i in range(tree.topLevelItemCount()):
            top_item = tree.topLevelItem(i)
            self._filter_item(top_item, text)

    def _filter_item(self, item, text):
        match = text in item.text(0).lower()
        child_match = False
        for i in range(item.childCount()):
            child = item.child(i)
            if self._filter_item(child, text):
                child_match = True
        item.setHidden(not (match or child_match))
        return match or child_match

    def _set_tree_items_visible(self, tree, visible):
        for i in range(tree.topLevelItemCount()):
            top_item = tree.topLevelItem(i)
            self._set_item_visible(top_item, visible)

    def _set_item_visible(self, item, visible):
        item.setHidden(not visible)
        for i in range(item.childCount()):
            self._set_item_visible(item.child(i), visible)

    def set_all_expanded(self, tree, expand):
        def recurse_expand(item):
            item.setExpanded(expand)
            for i in range(item.childCount()):
                child = item.child(i)
                recurse_expand(child)

        for i in range(tree.topLevelItemCount()):
            top = tree.topLevelItem(i)
            recurse_expand(top)

    def set_all_checked(self, tree, state):
        for i in range(tree.topLevelItemCount()):
            top = tree.topLevelItem(i)
            top.setCheckState(0, state)
            self.propagate_check_state_to_children(top, state)

    def select_siblings(self, tree):
        selected_items = tree.selectedItems()
        if not selected_items:
            return
        item = selected_items[0]
        parent = item.parent()
        if parent is not None:
            for i in range(parent.childCount()):
                sibling = parent.child(i)
                sibling.setCheckState(0, Qt.Checked)
                self.propagate_check_state_to_children(sibling, Qt.Checked)
        else:
            root = tree.invisibleRootItem()
            for i in range(root.childCount()):
                sibling = root.child(i)
                sibling.setCheckState(0, Qt.Checked)
                self.propagate_check_state_to_children(sibling, Qt.Checked)

    def apply_color_coding(self, tree):
        palette = [
            "#7BD3EA",
            "#A1EEBD",
            "#F6D6D6",
            "#F6F7C4",
            "#999B84",
            "#FFF6E3",
            "#F9C0AB",
            "#C1D8C3",
            "#E4C59E",
        ]

        def color_item(item, depth, parent_color=None):
            for offset in range(len(palette)):
                color_str = palette[(depth + offset) % len(palette)]
                if color_str != parent_color:
                    brush = QBrush(QColor(color_str))
                    item.setBackground(0, brush)
                    break
            for i in range(item.childCount()):
                child = item.child(i)
                current_color = item.background(0).color().name()
                color_item(child, depth + 1, current_color)

        for i in range(tree.topLevelItemCount()):
            top_item = tree.topLevelItem(i)
            color_item(top_item, 0, None)

    def on_options_changed(self, opts):
        self.app_controller.set_num_results(opts["num_results"])
        self.app_controller.set_detail_display_mode(opts["detail_display_mode"])
        self.app_controller.set_level_range(opts["min_level"], opts["max_level"])

    def on_campaign_text_changed(self):
        text = self.campaign_prompt_edit.toPlainText()
        self.app_controller.set_campaign_prompt(text)

    def on_system_text_changed(self, text):
        self.app_controller.set_system(text)

    def on_setting_text_changed(self, text):
        self.app_controller.set_setting(text)

    def generate_content(self):
        self.progress_dialog = QProgressDialog("Generating content...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(False)
        self.progress_dialog.setAutoReset(False)
        self.progress_dialog.show()

        def on_finished(results):
            self.progress_dialog.close()
            self.app_controller.state.last_results = results
            self.results_view.display_results(results)
            if results:
                show_info(self, "Content generated successfully!")
            else:
                show_info(self, "No results generated.")

        def on_error(message):
            self.progress_dialog.close()
            show_error(self, message)

        self.app_controller.generate_content_async(on_finished, on_error)

    def export_detailed(self):
        self.app_controller.export_to_logs(detailed=True)
        show_info(self, "Detailed content exported successfully!")

    def export_results_triggered(self):
        self.app_controller.export_to_logs(detailed=False)
        show_info(self, "Table exported successfully!")

    def more_info_triggered(self):
        row = self.results_view.table.currentRow()
        if row < 0 or row >= len(self.results_view.results):
            show_error(self, "No item selected for detailed info.")
            return
        content = self.results_view.results[row]
        self.show_full_statblock(content)

    def show_full_statblock(self, base_content):
        statblock = self.app_controller.get_full_statblock(base_content)
        if not statblock:
            show_error(self, "Failed to retrieve full statblock.")
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Detailed Statblock")
        dlg.resize(300, 600)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(5,5,5,5)
        layout.setSpacing(5)

        text = QTextEdit()
        text.setReadOnly(True)
        mode = self.app_controller.state.detail_display_mode
        name = statblock.get("Name", "")
        desc = statblock.get("Description", "")
        other_fields = [(k, v) for k, v in statblock.items() if k not in ["Name", "Description"]]

        if mode == "Plain Text":
            parts = [f"Name: {name}", f"Description: {desc}"]
            for k, v in other_fields:
                parts.append(f"{k}: {v}")
            text.setPlainText("\n".join(parts))
        elif mode == "Markdown":
            parts = [f"**{name}**", f"_{desc}_"]
            for k, v in other_fields:
                parts.append(f"**{k}:** {v}")
            md_text = "\n\n".join(parts)
            text.setPlainText(md_text)
        elif mode == "Formatted (3.5e Style)":
            template_path = "src/resources/statblock_template.html"
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    template = f.read()
            except Exception:
                template = "<h2>{{NAME}}</h2><p><i>{{DESCRIPTION}}</i></p>{{EXTRA_FIELDS}}"
            extra_html_parts = []
            for k, v in other_fields:
                extra_html_parts.append(f"<p><b>{k}:</b> {v}</p>")
            extra_fields_html = "\n".join(extra_html_parts)
            html = template.replace("{{NAME}}", name)
            html = html.replace("{{DESCRIPTION}}", desc)
            html = html.replace("{{EXTRA_FIELDS}}", extra_fields_html)
            text.setHtml(html)
        elif mode == "JSON Raw":
            raw_json = json.dumps(statblock, indent=2)
            text.setPlainText(raw_json)

        layout.addWidget(text)
        dlg.setLayout(layout)
        dlg.exec()

    def update_preview(self):
        row = self.results_view.table.currentRow()
        if row < 0 or row >= len(self.results_view.results):
            self.preview_box.clear()
            return
        result = self.results_view.results[row]
        keys = list(result.keys())
        preview_text = ""
        if keys:
            name_value = result.get('Name', '')
            description_value = result.get('Description', '')
            preview_text += f"<strong>Name:</strong> {name_value}<br />"
            preview_text += f"Description:<br /><br /><i>{description_value}</i><br /><br />"
            for key, value in result.items():
                if key in ["Name", "Description"]:
                    continue
                preview_text += f"<strong>{key}:</strong> <i>{value}</i><br />"

        self.preview_box.setHtml(preview_text)

    def update_category_breadcrumb(self, text):
        self.category_breadcrumb_content_label.setText(text)

    def update_context_breadcrumb(self, text):
        self.context_breadcrumb_content_label.setText(text)
