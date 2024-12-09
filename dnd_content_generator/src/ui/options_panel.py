from PySide6.QtWidgets import (
    QWidget, QLabel, QSpinBox, QCheckBox, QSlider, QGroupBox, QVBoxLayout, 
    QHBoxLayout, QGridLayout, QFormLayout, QComboBox, QPushButton, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

class OptionsPanel(QWidget):
    """
    Updated OptionsPanel:
    - Number of Results
    - Detail Display Mode
    - Min/Max Level sliders with enforced constraints
    - 2x2 button grid: Generate, Export Detailed, Export Table, More Info
    """

    generateRequested = Signal()
    exportDetailsRequested = Signal()
    exportResultsRequested = Signal()
    moreInfoRequested = Signal()
    optionsChanged = Signal(dict)

    def __init__(self, on_options_changed, parent=None):
        super().__init__(parent)
        self.on_options_changed = on_options_changed

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10,10,10,10)
        main_layout.setSpacing(10)

        group_box = QGroupBox("Generation Options")
        group_box_layout = QVBoxLayout()
        group_box_layout.setContentsMargins(10,10,10,10)
        group_box_layout.setSpacing(10)

        # Form layout for main options
        form_layout = QFormLayout()
        form_layout.setHorizontalSpacing(20)
        form_layout.setVerticalSpacing(10)

        # Number of Results
        self.num_results = QSpinBox()
        self.num_results.setRange(1, 100)
        self.num_results.setValue(3)
        self.num_results.valueChanged.connect(self.options_changed)

        # Detail Display Mode
        self.detail_display_mode = QComboBox()
        self.detail_display_mode.addItems(["Plain Text", "Markdown", "Formatted (3.5e Style)", "JSON Raw"])
        self.detail_display_mode.currentIndexChanged.connect(self.options_changed)

        # Min/Max Level controls with constraints
        self.min_label = QLabel("Min Level: 1")
        self.min_label.setFixedWidth(80)
        self.min_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.min_level = QSlider(Qt.Horizontal)
        self.min_level.setRange(1,20)
        self.min_level.setValue(1)
        self.min_level.valueChanged.connect(self.update_min_level)

        min_level_layout = QHBoxLayout()
        min_level_layout.addWidget(self.min_label)
        min_level_layout.addWidget(self.min_level)

        self.max_label = QLabel("Max Level: 3")
        self.max_label.setFixedWidth(80)
        self.max_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.max_level = QSlider(Qt.Horizontal)
        self.max_level.setRange(1,20)
        self.max_level.setValue(3)
        self.max_level.valueChanged.connect(self.update_max_level)

        max_level_layout = QHBoxLayout()
        max_level_layout.addWidget(self.max_label)
        max_level_layout.addWidget(self.max_level)

        level_layout = QVBoxLayout()
        level_layout.addLayout(min_level_layout)
        level_layout.addLayout(max_level_layout)

        level_widget = QWidget()
        level_widget.setLayout(level_layout)

        # Add form fields (no regeneration options now)
        form_layout.addRow("Number of Results:", self.num_results)
        form_layout.addRow("Detail Display Mode:", self.detail_display_mode)
        form_layout.addRow("Level Range:", level_widget)

        group_box_layout.addLayout(form_layout)

        # Button grid (2x2)
        button_grid = QGridLayout()
        button_grid.setContentsMargins(0,0,0,0)
        button_grid.setSpacing(10)
        
        self.generate_btn = QPushButton("Generate")
        self.more_info_btn = QPushButton("More Info")
        self.export_details_btn = QPushButton("Export Preview")
        self.export_table_btn = QPushButton("Export Table")

        # Connect signals
        self.generate_btn.clicked.connect(self.generateRequested.emit)
        self.export_details_btn.clicked.connect(self.exportDetailsRequested.emit)
        self.export_table_btn.clicked.connect(self.exportResultsRequested.emit)
        self.more_info_btn.clicked.connect(self.moreInfoRequested.emit)

        # Place them in the 2x2 grid
        button_grid.addWidget(self.generate_btn, 0, 0)
        button_grid.addWidget(self.export_details_btn, 0, 1)
        button_grid.addWidget(self.export_table_btn, 1, 0)
        button_grid.addWidget(self.more_info_btn, 1, 1)

        group_box_layout.addSpacing(10)
        group_box_layout.addLayout(button_grid)

        group_box.setLayout(group_box_layout)
        main_layout.addWidget(group_box)
        self.setLayout(main_layout)

    def set_tooltips(self, tooltips):
        if not isinstance(tooltips, dict):
            return
        if "num_results" in tooltips:
            self.num_results.setToolTip(tooltips["num_results"])
        if "min_level" in tooltips:
            self.min_level.setToolTip(tooltips["min_level"])
            self.min_label.setToolTip(tooltips["min_level"])
        if "max_level" in tooltips:
            self.max_level.setToolTip(tooltips["max_level"])
            self.max_label.setToolTip(tooltips["max_level"])

    def update_min_level(self, value):
        # Ensure min_level is not greater than max_level
        if value > self.max_level.value():
            self.max_level.setValue(value)
        self.min_label.setText(f"Min Level: {self.min_level.value()}")
        self.options_changed()

    def update_max_level(self, value):
        # Ensure max_level is not less than min_level
        if value < self.min_level.value():
            self.min_level.setValue(value)
        self.max_label.setText(f"Max Level: {self.max_level.value()}")
        self.options_changed()

    def options_changed(self, *args):
        opts = {
            "num_results": self.num_results.value(),
            "min_level": self.min_level.value(),
            "max_level": self.max_level.value(),
            "detail_display_mode": self.detail_display_mode.currentText()
        }
        self.on_options_changed(opts)
