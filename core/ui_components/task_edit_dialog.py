# file: core/ui_components/task_edit_dialog.py

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QDateEdit, QSpinBox, QCheckBox
)
from PyQt6.QtCore import QDate, Qt
from datetime import datetime

class TaskEditDialog(QDialog):
    """
    Jendela dialog untuk mengedit nama, hitungan, tanggal, dan status checklist sebuah task.
    """
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task")

        self.layout = QVBoxLayout(self)

        # Input untuk Nama Task
        self.name_label = QLabel("Nama Task:")
        self.name_input = QLineEdit(task_data.get("name", ""))
        self.layout.addWidget(self.name_label)
        self.layout.addWidget(self.name_input)

        # Input untuk Jumlah Hitungan (Count)
        self.count_label = QLabel("Jumlah Hitungan:")
        self.count_input = QSpinBox()
        self.count_input.setRange(0, 9999) # Atur batas maksimal hitungan
        self.count_input.setValue(task_data.get("count", 0))
        self.layout.addWidget(self.count_label)
        self.layout.addWidget(self.count_input)

        # Input untuk Tanggal
        self.date_label = QLabel("Tanggal:")
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        
        # Atur tanggal awal dari data task, atau gunakan hari ini jika tidak ada
        initial_date_str = task_data.get("date")
        if initial_date_str:
            initial_date = QDate.fromString(initial_date_str, "yyyy-MM-dd")
        else:
            initial_date = QDate.currentDate()
        self.date_input.setDate(initial_date)
        
        self.layout.addWidget(self.date_label)
        self.layout.addWidget(self.date_input)

        # Checkbox untuk status Selesai
        self.checked_checkbox = QCheckBox("Tandai sebagai selesai (checklist)")
        self.checked_checkbox.setChecked(task_data.get("checked", False))
        self.layout.addWidget(self.checked_checkbox)

        # Tombol OK dan Batal
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_data(self):
        """Mengembalikan data yang telah diubah dari dialog."""
        return {
            "name": self.name_input.text(),
            "count": self.count_input.value(),
            "date": self.date_input.date().toString("yyyy-MM-dd"),
            "checked": self.checked_checkbox.isChecked() # Ambil status checkbox
        }