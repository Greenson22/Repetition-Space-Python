# file: core/event_handlers/task_handlers.py

from datetime import datetime
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from PyQt6.QtCore import Qt
from ..ui_components.task_edit_dialog import TaskEditDialog

class TaskHandlers:
    """Berisi handler untuk event terkait Tasks."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def add_task(self):
        """Menambahkan task baru ke kategori yang dipilih."""
        if not self.win.current_task_category or self.win.current_task_category == "Semua Task":
            QMessageBox.warning(self.win, "Gagal", "Pilih atau buat kategori terlebih dahulu untuk menambahkan task.")
            return
        
        task_name, ok = QInputDialog.getText(self.win, "Tambah Task Baru", "Nama Task:")
        if ok and task_name:
            new_task = {
                'name': task_name, 
                'count': 0, 
                'date': datetime.now().strftime("%Y-%m-%d"),
                'checked': False
            }
            self.data_manager.save_task(self.win.current_task_category, task_name, new_task)
            self.win.refresh_manager.refresh_task_list()

    def edit_task(self):
        """Membuka dialog untuk mengedit task."""
        item = self.win.task_tree.currentItem()
        if not item: return

        task_info = item.data(0, Qt.ItemDataRole.UserRole)
        if not task_info: return
        
        old_task_name = task_info.get("original_name")
        category_name = task_info.get("category")

        tasks_data = self.data_manager.load_tasks_data()
        original_task_data = None
        for cat in tasks_data.get("categories", []):
            if cat['name'] == category_name:
                for task in cat.get("tasks", []):
                    if task['name'] == old_task_name:
                        original_task_data = task
                        break
                break
        
        if not original_task_data:
            QMessageBox.warning(self.win, "Error", "Data task tidak ditemukan.")
            return
        
        dialog = TaskEditDialog(original_task_data, self.win)
        
        if dialog.exec():
            updated_data = dialog.get_data()
            new_task_name = updated_data.get("name")
            
            if new_task_name != old_task_name:
                self.data_manager.delete_task(category_name, old_task_name)
            
            self.data_manager.save_task(category_name, new_task_name, updated_data)
            
            self.win.refresh_manager.refresh_task_list()
            self.win.refresh_manager.reselect_task(new_task_name, category_name)

    def delete_task(self):
        """Menghapus task yang dipilih."""
        item = self.win.task_tree.currentItem()
        if not item: return

        task_info = item.data(0, Qt.ItemDataRole.UserRole)
        task_name = task_info.get("original_name")
        category_name = task_info.get("category")

        reply = QMessageBox.question(self.win, "Konfirmasi", f"Yakin ingin menghapus task '{task_name}' dari kategori '{category_name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_task(category_name, task_name)
            self.win.refresh_manager.refresh_task_list()

    def move_task_up(self):
        self._move_task(-1)

    def move_task_down(self):
        self._move_task(1)

    def _move_task(self, direction):
        item = self.win.task_tree.currentItem()
        if not item or self.win.current_task_category == "Semua Task": return

        task_info = item.data(0, Qt.ItemDataRole.UserRole)
        category_name = task_info.get("category")
        current_index = task_info.get("index")
        
        tasks_data = self.data_manager.load_tasks_data()
        categories = tasks_data.get("categories", [])

        for category in categories:
            if category['name'] == category_name:
                tasks = category.get("tasks", [])
                if 0 <= current_index < len(tasks):
                    new_index = current_index + direction
                    if 0 <= new_index < len(tasks):
                        tasks[current_index], tasks[new_index] = tasks[new_index], tasks[current_index]
                        self.data_manager.save_tasks_data(tasks_data)
                        
                        self.win.refresh_manager.refresh_task_list()
                        new_item_to_select = self.win.task_tree.topLevelItem(new_index)
                        if new_item_to_select:
                            self.win.task_tree.setCurrentItem(new_item_to_select)
                        break

    def task_item_changed(self, item, column):
        """Handler saat status checklist sebuah task diubah."""
        if column == 0:
            task_info = item.data(0, Qt.ItemDataRole.UserRole)
            if not task_info: return

            category_name = task_info.get("category")
            task_name = task_info.get("original_name")
            is_checked = item.checkState(0) == Qt.CheckState.Checked

            tasks_data = self.data_manager.load_tasks_data()
            for category in tasks_data.get("categories", []):
                if category['name'] == category_name:
                    for task in category.get("tasks", []):
                        if task['name'] == task_name:
                            task['checked'] = is_checked
                            self.data_manager.save_tasks_data(tasks_data)
                            return