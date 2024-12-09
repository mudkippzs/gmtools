from PySide6.QtWidgets import (QWidget, QVBoxLayout, QCheckBox, QScrollArea, 
                               QWidget, QFormLayout, QLabel, QPushButton, QHBoxLayout, QFrame)
from PySide6.QtCore import Qt

class ContextSelector(QWidget):
    """
    ContextSelector displays a list of categories and their respective contexts.
    Each category is shown with a label (bold) followed by its options.
    Provides 'Select All' and 'Deselect All' convenience buttons.
    Emits on_contexts_changed when the set of selected contexts changes.
    """

    def __init__(self, contexts, on_contexts_changed, parent=None):
        super().__init__(parent)
        self.contexts = contexts
        self.on_contexts_changed = on_contexts_changed
        self.selected_contexts = []

        main_layout = QVBoxLayout()

        # Select / Deselect All buttons
        btn_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)

        btn_layout.addWidget(select_all_btn)
        btn_layout.addWidget(deselect_all_btn)
        main_layout.addLayout(btn_layout)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        form_layout = QFormLayout()

        self.checkboxes = []
        # Display categories in bold to separate them visually
        for cat, opts in self.contexts.items():
            # Category label as a section header
            cat_label = QLabel(f"<b>{cat}</b>")
            form_layout.addRow(cat_label)
            # Add some spacing or a line separator
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            form_layout.addRow(line)

            for opt in opts:
                cb = QCheckBox(opt)
                cb.stateChanged.connect(self.update_contexts)
                form_layout.addRow("", cb)
                self.checkboxes.append(cb)

        container.setLayout(form_layout)
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def update_contexts(self):
        self.selected_contexts = [cb.text() for cb in self.checkboxes if cb.isChecked()]
        self.on_contexts_changed(self.selected_contexts)

    def select_all(self):
        for cb in self.checkboxes:
            cb.setChecked(True)
        self.update_contexts()

    def deselect_all(self):
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.update_contexts()
