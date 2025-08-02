# file: core/refresh_manager/task_refresher.py
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import Qt
import utils

class TaskRefresher:
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager
        self.settings = main_window.settings

    def refresh_task_list(self):
        """Merefresh daftar task berdasarkan kategori yang dipilih."""
        self.win.task_tree.blockSignals(True)
        self.win.task_tree.clear()

        if not self.win.current_task_category:
            self.win.handlers.update_button_states()
            self.win.task_tree.blockSignals(False)
            return

        tasks = (self.data_manager.get_all_tasks() if self.win.current_task_category == "Semua Task"
                 else self.data_manager.get_tasks(self.win.current_task_category))
        date_format = self.settings.value("date_format", "long")

        for index, task_data in enumerate(tasks):
            item = QTreeWidgetItem(self.win.task_tree)

            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            check_state = Qt.CheckState.Checked if task_data.get('checked', False) else Qt.CheckState.Unchecked
            item.setCheckState(0, check_state)

            item.setText(0, task_data.get('name', ''))
            item.setText(1, str(task_data.get('count', 0)))
            item.setText(2, utils.format_date(task_data.get('date', ''), date_format))

            user_data = {
                "original_name": task_data.get("original_name", task_data.get("name")),
                "category": task_data.get("category", self.win.current_task_category),
                "index": index
            }
            item.setData(0, Qt.ItemDataRole.UserRole, user_data)

        self.win.handlers.update_button_states()
        self.win.task_tree.blockSignals(False)

    def reselect_task(self, task_name_to_select, category_name_to_select):
        """Memilih kembali item task setelah operasi."""
        for i in range(self.win.task_tree.topLevelItemCount()):
            item = self.win.task_tree.topLevelItem(i)
            task_info = item.data(0, Qt.ItemDataRole.UserRole)
            if (task_info.get("original_name") == task_name_to_select and
                task_info.get("category") == category_name_to_select):
                self.win.task_tree.setCurrentItem(item)
                break