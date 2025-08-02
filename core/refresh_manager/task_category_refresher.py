# file: core/refresh_manager/task_category_refresher.py
from PyQt6.QtWidgets import QListWidgetItem

class TaskCategoryRefresher:
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def refresh_task_category_list(self):
        """Merefresh daftar kategori task dengan penanganan format data lama/baru."""
        current_item_text = self.win.task_category_list.currentItem().text() if self.win.task_category_list.currentItem() else None
        self.win.task_category_list.blockSignals(True)
        self.win.task_category_list.clear()

        self.win.task_category_list.addItem("Semua Task")
        categories = self.data_manager.get_task_categories()

        item_to_reselect = None
        for cat_data in categories:
            # Struktur baru adalah dictionary
            if isinstance(cat_data, dict):
                icon = cat_data.get('icon', '📂') # Default icon jika tidak ada
                name = cat_data.get('name', 'Kategori tanpa nama')
                display_text = f"{icon} {name}"
            # Menjaga kompatibilitas dengan format lama (string)
            elif isinstance(cat_data, str):
                display_text = f"📂 {cat_data}"
            else:
                continue

            item = QListWidgetItem(display_text)
            self.win.task_category_list.addItem(item)
            if display_text == current_item_text:
                item_to_reselect = item

        if item_to_reselect:
            self.win.task_category_list.setCurrentItem(item_to_reselect)
        else:
            self.win.task_category_list.setCurrentRow(0)

        self.win.task_category_list.blockSignals(False)
        if self.win.task_category_list.currentItem():
             self.win.handlers.task_category_selected(self.win.task_category_list.currentItem(), None)