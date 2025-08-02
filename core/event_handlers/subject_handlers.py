# file: core/event_handlers/subject_handlers.py

import os
from PyQt6.QtWidgets import QInputDialog, QMessageBox
import config

class SubjectHandlers:
    """Berisi handler untuk event terkait Subjects."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def subject_selected(self, current, previous):
        """Handler saat sebuah subject dipilih."""
        self.win.content_tree.clear()
        if not current:
            self.win.current_subject_path = None
            self.win.current_content = None
        else:
            subject_name_full = current.text().split(" ", 1)[1]
            subject_name = subject_name_full.split('\n')[0]
            
            subject_file_name = f"{subject_name}.json"
            self.win.current_subject_path = os.path.join(self.win.current_topic_path, subject_file_name)
            self.win.refresh_manager.refresh_content_tree()
        self.update_button_states()

    def create_subject(self):
        """Membuat subject baru."""
        if not self.win.current_topic_path: return
        name, ok = QInputDialog.getText(self.win, "Buat Subject Baru", "Nama Subject:")
        if ok and name:
            name = name.strip()
            if not name:
                QMessageBox.warning(self.win, "Nama Tidak Valid", "Nama subject tidak boleh kosong.")
                return

            file_path = os.path.join(self.win.current_topic_path, f"{name}.json")

            if os.path.exists(file_path):
                QMessageBox.warning(self.win, "Gagal", f"Subject dengan nama '{name}' sudah ada.")
                return

            self.win.current_content = {"content": [], "metadata": {"earliest_date": None, "earliest_code": None, "icon": config.DEFAULT_SUBJECT_ICON}}
            self.win.current_subject_path = file_path
            self.data_manager.save_content(file_path, self.win.current_content)
            self.win.refresh_manager.refresh_subject_list()

    def rename_subject(self):
        """Mengubah nama subject yang dipilih."""
        if not self.win.current_topic_path or not self.win.subject_list.currentItem(): return
        
        old_name_full = self.win.subject_list.currentItem().text().split(" ", 1)[1]
        old_name = old_name_full.split('\n')[0]

        new_name, ok = QInputDialog.getText(self.win, "Ubah Nama Subject", "Nama Baru:", text=old_name)
        if ok and new_name and new_name != old_name:
            old_file = os.path.join(self.win.current_topic_path, f"{old_name}.json")
            new_file = os.path.join(self.win.current_topic_path, f"{new_name}.json")
            try:
                self.data_manager.rename_path(old_file, new_file)
                self.win.refresh_manager.refresh_subject_list()
            except Exception as e:
                QMessageBox.warning(self.win, "Gagal", f"Tidak dapat mengubah nama file: {e}")

    def delete_subject(self):
        """Menghapus subject yang dipilih."""
        if not self.win.current_topic_path or not self.win.subject_list.currentItem(): return
        
        name_full = self.win.subject_list.currentItem().text().split(" ", 1)[1]
        name = name_full.split('\n')[0]

        reply = QMessageBox.question(self.win, "Konfirmasi", f"Yakin ingin menghapus subject '{name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            file_path = os.path.join(self.win.current_topic_path, f"{name}.json")
            try:
                self.data_manager.delete_file(file_path)
                self.win.refresh_manager.refresh_subject_list()
            except Exception as e:
                QMessageBox.warning(self.win, "Gagal", f"Tidak dapat menghapus file: {e}")

    def change_subject_icon(self):
        """Mengubah ikon untuk subject yang dipilih."""
        if not self.win.current_subject_path: return
        
        icon, ok = QInputDialog.getItem(self.win, "Pilih Ikon Subject", "Pilih ikon:", config.AVAILABLE_ICONS, 0, False)
        
        if ok and icon:
            if not self.win.current_content:
                self.win.current_content = self.data_manager.load_content(self.win.current_subject_path)
            
            if "metadata" not in self.win.current_content or self.win.current_content["metadata"] is None:
                self.win.current_content["metadata"] = {}
                
            self.win.current_content["metadata"]["icon"] = icon
            self.data_manager.save_content(self.win.current_subject_path, self.win.current_content)
            self.win.refresh_manager.refresh_subject_list()