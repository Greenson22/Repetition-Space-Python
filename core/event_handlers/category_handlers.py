# file: core/event_handlers/category_handlers.py

from PyQt6.QtWidgets import QInputDialog, QMessageBox
import config

class CategoryHandlers:
    """Berisi handler untuk event terkait Task Categories."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def task_category_selected(self, current, previous):
        """Handler saat kategori task dipilih."""
        if not current:
            self.win.current_task_category = None
        else:
            text = current.text()
            if text == "Semua Task":
                self.win.current_task_category = "Semua Task"
            else:
                parts = text.split(" ", 1)
                self.win.current_task_category = parts[1] if len(parts) > 1 else parts[0]
                
        self.win.refresh_manager.refresh_task_list()
        self.update_button_states()

    def create_task_category(self):
        """Membuat kategori task baru."""
        name, ok = QInputDialog.getText(self.win, "Buat Kategori Baru", "Nama Kategori:")
        if ok and name:
            self.data_manager.create_task_category(name)
            self.win.refresh_manager.refresh_task_category_list()

    def rename_task_category(self):
        """Mengubah nama kategori task yang dipilih."""
        item = self.win.task_category_list.currentItem()
        if not item or item.text() == "Semua Task": return

        text = item.text()
        parts = text.split(" ", 1)
        old_name = parts[1] if len(parts) > 1 else parts[0]
        
        new_name, ok = QInputDialog.getText(self.win, "Ubah Nama Kategori", "Nama Baru:", text=old_name)
        if ok and new_name and new_name != old_name:
            self.data_manager.rename_task_category(old_name, new_name)
            self.win.refresh_manager.refresh_task_category_list()
            for i in range(self.win.task_category_list.count()):
                list_item = self.win.task_category_list.item(i)
                new_text = list_item.text()
                new_parts = new_text.split(" ", 1)
                current_name = new_parts[1] if len(new_parts) > 1 else new_parts[0]
                if current_name == new_name:
                    self.win.task_category_list.setCurrentItem(list_item)
                    break
            self.win.refresh_manager.refresh_task_list()
            
    def change_task_category_icon(self):
        """Mengubah ikon untuk kategori yang dipilih."""
        item = self.win.task_category_list.currentItem()
        if not item or item.text() == "Semua Task": return

        text = item.text()
        parts = text.split(" ", 1)
        category_name = parts[1] if len(parts) > 1 else parts[0]

        icon, ok = QInputDialog.getItem(self.win, "Pilih Ikon Kategori", "Pilih ikon:", config.AVAILABLE_ICONS, 0, False)
        
        if ok and icon:
            self.data_manager.update_task_category_icon(category_name, icon)
            self.win.refresh_manager.refresh_task_category_list()
            for i in range(self.win.task_category_list.count()):
                list_item = self.win.task_category_list.item(i)
                if list_item.text() == f"{icon} {category_name}":
                    self.win.task_category_list.setCurrentItem(list_item)
                    break

    def delete_task_category(self):
        """Menghapus kategori task yang dipilih."""
        item = self.win.task_category_list.currentItem()
        if not item or item.text() == "Semua Task": return
        
        text = item.text()
        parts = text.split(" ", 1)
        name = parts[1] if len(parts) > 1 else parts[0]
        
        reply = QMessageBox.question(self.win, "Konfirmasi", f"Yakin ingin menghapus kategori '{name}' dan semua isinya?")
        if reply == QMessageBox.StandardButton.Yes:
            self.data_manager.delete_task_category(name)
            self.win.refresh_manager.refresh_task_category_list()

    def move_category_up(self):
        self._move_category(-1)

    def move_category_down(self):
        self._move_category(1)

    def _move_category(self, direction):
        current_row = self.win.task_category_list.currentRow()
        if current_row <= 0: return

        tasks_data = self.data_manager.load_tasks_data()
        categories = tasks_data.get("categories", [])
        
        cat_index = current_row - 1
        
        if 0 <= cat_index < len(categories):
            new_index = cat_index + direction
            if 0 <= new_index < len(categories):
                categories[cat_index], categories[new_index] = categories[new_index], categories[cat_index]
                self.data_manager.save_tasks_data(tasks_data)
                
                self.win.refresh_manager.refresh_task_category_list()
                self.win.task_category_list.setCurrentRow(new_index + 1)