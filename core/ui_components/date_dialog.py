# file: ui_components.py

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QCalendarWidget, QDialogButtonBox
from PyQt6.QtCore import QDate

class DateDialog(QDialog):
    """Dialog untuk memilih tanggal dari kalender."""
    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setWindowTitle("Pilih Tanggal")
        
        self.layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        if initial_date:
            self.calendar.setSelectedDate(QDate.fromString(initial_date, "yyyy-MM-dd"))
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addWidget(self.calendar)
        self.layout.addWidget(self.buttons)

    def get_selected_date(self):
        return self.calendar.selectedDate().toString("yyyy-MM-dd")