from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QComboBox

class CategorySelector(QWidget):
    """
    CategorySelector displays two combo boxes: one for Category and one for Type.
    A placeholder is shown in Category to force the user to select a valid category.
    The Type combo is disabled until a valid category is chosen.

    Signals:
    - on_category_selected(category_or_none)
    - on_type_selected(type_or_none)
    """

    def __init__(self, categories, on_category_selected, on_type_selected, placeholder_text="Select a Category...", parent=None):
        super().__init__(parent)
        self.categories = categories
        self.on_category_selected = on_category_selected
        self.on_type_selected = on_type_selected
        self.placeholder_text = placeholder_text

        layout = QHBoxLayout()

        self.category_label = QLabel("Category:")
        self.category_combo = QComboBox()
        # Insert placeholder as the first item
        self.category_combo.addItem(self.placeholder_text)
        for c in self.categories.keys():
            self.category_combo.addItem(c)

        self.category_combo.currentTextChanged.connect(self.category_changed)

        self.type_label = QLabel("Type:")
        self.type_combo = QComboBox()
        self.type_combo.setEnabled(False)  # Disabled until a valid category is selected
        self.type_combo.currentTextChanged.connect(self.type_changed)

        layout.addWidget(self.category_label)
        layout.addWidget(self.category_combo)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_combo)

        self.setLayout(layout)

    def category_changed(self, category):
        """
        Called when the category combo changes.
        If placeholder is selected, disable type combo and notify None.
        Otherwise, populate the type combo and notify the selected category.
        """
        if category == self.placeholder_text:
            self.type_combo.clear()
            self.type_combo.setEnabled(False)
            self.on_category_selected(None)
            return

        self.on_category_selected(category)
        self.type_combo.clear()
        self.type_combo.setEnabled(True)
        # Populate type combo
        if category in self.categories:
            self.type_combo.addItem("Select a Type...")  # Add a placeholder for type
            for t in self.categories[category]:
                self.type_combo.addItem(t)
        else:
            # No valid types for this category?
            self.type_combo.setEnabled(False)

    def type_changed(self, t):
        """
        Called when the type combo changes.
        If 'Select a Type...' is selected, treat as None.
        """
        if t == "Select a Type...":
            self.on_type_selected(None)
        else:
            self.on_type_selected(t)
