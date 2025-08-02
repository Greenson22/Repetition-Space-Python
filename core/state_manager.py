# file: test/core/state_manager.py

from PyQt6.QtWidgets import QTreeWidgetItemIterator

class StateManager:
    """Kelas untuk mengelola penyimpanan dan pemuatan status aplikasi."""
    def __init__(self, main_window):
        self.win = main_window
        self.settings = main_window.settings

    def save_state(self):
        """Menyimpan item yang dipilih terakhir di setiap panel."""
        # Topik
        topic_item = self.win.topic_list.currentItem()
        if topic_item:
            self.settings.setValue("last_selected_topic", topic_item.text())

        # Subjek
        subject_item = self.win.subject_list.currentItem()
        if subject_item:
            self.settings.setValue("last_selected_subject", subject_item.text())

        # Konten (Diskusi/Point)
        content_item = self.win.content_tree.currentItem()
        if content_item:
            data = content_item.data(0, self.win.Qt.ItemDataRole.UserRole)
            self.settings.setValue("last_selected_content", data)
        
        # Kategori Task
        task_category_item = self.win.task_category_list.currentItem()
        if task_category_item:
            self.settings.setValue("last_selected_task_category", task_category_item.text())
        
        # Task
        task_item = self.win.task_tree.currentItem()
        if task_item:
            data = task_item.data(0, self.win.Qt.ItemDataRole.UserRole)
            self.settings.setValue("last_selected_task", data)

    def load_state(self):
        """Memuat dan memilih item terakhir yang disimpan."""
        # Pilih Kategori Task
        last_category = self.settings.value("last_selected_task_category")
        if last_category:
            for i in range(self.win.task_category_list.count()):
                if self.win.task_category_list.item(i).text() == last_category:
                    self.win.task_category_list.setCurrentRow(i)
                    break
        
        # Pilih Task
        last_task_data = self.settings.value("last_selected_task")
        if last_task_data:
            self.win.refresh_manager.refresh_task_list() 
            for i in range(self.win.task_tree.topLevelItemCount()):
                item = self.win.task_tree.topLevelItem(i)
                if item.data(0, self.win.Qt.ItemDataRole.UserRole) == last_task_data:
                    self.win.task_tree.setCurrentItem(item)
                    break

        # Pilih Topik
        last_topic = self.settings.value("last_selected_topic")
        if last_topic:
            for i in range(self.win.topic_list.count()):
                if self.win.topic_list.item(i).text() == last_topic:
                    self.win.topic_list.setCurrentRow(i)
                    break
        
        # Pilih Subjek
        last_subject = self.settings.value("last_selected_subject")
        if self.win.current_topic_path and last_subject:
            self.win.refresh_manager.refresh_subject_list()
            for i in range(self.win.subject_list.count()):
                if self.win.subject_list.item(i).text() == last_subject:
                    self.win.subject_list.setCurrentRow(i)
                    break
        
        # Pilih Konten
        last_content_data = self.settings.value("last_selected_content")
        if self.win.current_subject_path and last_content_data:
            self.win.refresh_manager.refresh_content_tree() 
            iterator = QTreeWidgetItemIterator(self.win.content_tree)
            while iterator.value():
                item = iterator.value()
                if item.data(0, self.win.Qt.ItemDataRole.UserRole) == last_content_data:
                    self.win.content_tree.setCurrentItem(item)
                    break
                iterator += 1