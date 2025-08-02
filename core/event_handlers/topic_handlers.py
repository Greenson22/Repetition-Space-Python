# file: core/event_handlers/topic_handlers.py

import os
from PyQt6.QtWidgets import QInputDialog, QMessageBox
import config

class TopicHandlers:
    """Berisi handler untuk event terkait Topics."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def topic_selected(self, current, previous):
        """Handler saat sebuah topic dipilih."""
        self.win.subject_list.clear()
        self.win.content_tree.clear()
        self.win.current_content = None
        if not current:
            self.win.current_topic_path = None
        else:
            topic_name = current.text().split(" ", 1)[1]
            self.win.current_topic_path = os.path.join(self.win.base_path, topic_name)
            self.win.refresh_manager.refresh_subject_list()
            if self.win.subject_list.count() > 0:
                self.win.subject_list.setCurrentRow(0)
        self.update_button_states()

    def create_topic(self):
        """Membuat topic baru."""
        name, ok = QInputDialog.getText(self.win, "Buat Topic Baru", "Nama Topic:")
        if ok and name:
            try:
                self.data_manager.create_directory(os.path.join(self.win.base_path, name))
                self.win.refresh_manager.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self.win, "Gagal", f"Tidak dapat membuat topic: {e}")

    def rename_topic(self):
        """Mengubah nama topic yang dipilih."""
        item = self.win.topic_list.currentItem()
        if not item: return
        old_name = item.text().split(" ", 1)[1]
        new_name, ok = QInputDialog.getText(self.win, "Ubah Nama Topic", "Nama Baru:", text=old_name)
        if ok and new_name and new_name != old_name:
            try:
                self.data_manager.rename_path(os.path.join(self.win.base_path, old_name), os.path.join(self.win.base_path, new_name))
                self.win.refresh_manager.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self.win, "Gagal", f"Tidak dapat mengubah nama: {e}")
    
    def delete_topic(self):
        """Menghapus topic yang dipilih."""
        item = self.win.topic_list.currentItem()
        if not item: return
        name = item.text().split(" ", 1)[1]
        reply = QMessageBox.question(self.win, "Konfirmasi", f"Yakin ingin menghapus topic '{name}' dan semua isinya?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_directory(os.path.join(self.win.base_path, name))
                self.win.refresh_manager.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self.win, "Gagal", f"Tidak dapat menghapus: {e}")
    
    def change_topic_icon(self):
        """Mengubah ikon untuk topic yang dipilih."""
        item = self.win.topic_list.currentItem()
        if not item: return
        
        topic_name = item.text().split(" ", 1)[1]
        icon, ok = QInputDialog.getItem(self.win, "Pilih Ikon Topic", "Pilih ikon:", config.AVAILABLE_ICONS, 0, False)
        
        if ok and icon:
            self.data_manager.save_topic_config(topic_name, {'icon': icon})
            self.win.refresh_manager.refresh_topic_list()