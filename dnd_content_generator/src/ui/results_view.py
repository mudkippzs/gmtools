from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PySide6.QtWidgets import QHeaderView
from PySide6.QtCore import Qt, Signal

from src.services.logger import logger

class ResultsView(QWidget):
    """
    ResultsView displays generated results in a table only.
    The 'Export Table' and 'More Info' buttons were moved to the OptionsPanel.
    """

    request_more_info = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(0)
        self.table.setRowCount(0)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addWidget(self.table)
        self.setLayout(layout)

        self.results = []
        self.last_headers = []

    def display_results(self, results):
        self.results = results
        self.table.clear()
        if not results:
            if self.last_headers:
                self.table.setColumnCount(len(self.last_headers))
                self.table.setHorizontalHeaderLabels(self.last_headers)
            else:
                self.table.setColumnCount(0)
            self.table.setRowCount(0)
            return

        # Extract keys from the first result
        keys = list(results[0].keys())

        # Ensure "Name" and "Description" are the first two columns
        # Remove them from keys if they exist to avoid duplication
        if "Name" in keys:
            keys.remove("Name")
        if "Description" in keys:
            keys.remove("Description")
            
        # Re-insert them at the front
        keys = ["Name", "Description"] + keys

        logger.info(f"Reordered Table Column Keys: {keys}")
        self.last_headers = keys
        self.table.setColumnCount(len(keys))
        self.table.setHorizontalHeaderLabels(keys)
        self.table.setRowCount(len(results))

        for r, res in enumerate(results):
            # Always set Name and Description at columns 0 and 1
            name_val = str(res.get("Name", ""))
            description_val = str(res.get("Description", ""))
            name_item = QTableWidgetItem(name_val)
            description_item = QTableWidgetItem(description_val)

            self.table.setItem(r, 0, name_item)
            self.table.setItem(r, 1, description_item)

            # Set remaining columns
            # Start from column 2 for other keys
            col_index = 2
            for k in keys[2:]:  # keys after Name and Description
                val = str(res.get(k, ""))
                item = QTableWidgetItem(val)
                self.table.setItem(r, col_index, item)
                col_index += 1

        # Adjust column widths:
        for i in range(0, len(keys)):
            self.table.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
