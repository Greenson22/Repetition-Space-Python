# file: core/event_handlers/general_handlers.py

from datetime import datetime
from PyQt6.QtWidgets import QMessageBox, QFileDialog

class GeneralHandlers:
    """Berisi handler untuk fungsionalitas umum dan utilitas."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def backup_all_topics(self):
        """Membuat backup semua topic dalam format zip."""
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"backup-topics-{timestamp}.zip"

        save_path, _ = QFileDialog.getSaveFileName(
            self.win,
            "Simpan Backup Topics",
            default_filename,
            "Zip Files (*.zip)"
        )

        if save_path:
            try:
                self.data_manager.create_backup_zip(save_path)
                QMessageBox.information(
                    self.win,
                    "Backup Berhasil",
                    f"Semua topics berhasil di-backup ke:\n{save_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.win,
                    "Backup Gagal",
                    f"Terjadi kesalahan saat membuat backup:\n{e}"
                )

    def import_backup(self):
        """Mengimpor topics dari file backup zip."""
        open_path, _ = QFileDialog.getOpenFileName(
            self.win,
            "Pilih File Backup untuk Diimpor",
            "",
            "Zip Files (*.zip)"
        )

        if open_path:
            try:
                self.data_manager.import_backup_zip(open_path)
                QMessageBox.information(
                    self.win,
                    "Impor Berhasil",
                    "Topics dari file backup berhasil diimpor."
                )
                self.win.refresh_manager.refresh_topic_list()
                self.win.refresh_manager.refresh_task_category_list()
            except Exception as e:
                QMessageBox.critical(
                    self.win,
                    "Impor Gagal",
                    f"Terjadi kesalahan saat mengimpor backup:\n{e}"
                )

    def update_button_states(self):
        """Memperbarui status aktif/nonaktif semua tombol berdasarkan konteks."""
        topic_selected = self.win.topic_list.currentItem() is not None
        subject_selected = self.win.subject_list.currentItem() is not None
        
        # Tombol Topic & Subject
        self.win.btn_rename_topic.setEnabled(topic_selected)
        self.win.btn_delete_topic.setEnabled(topic_selected)
        self.win.btn_change_topic_icon.setEnabled(topic_selected)
        self.win.btn_buat_subject.setEnabled(topic_selected)

        self.win.btn_rename_subject.setEnabled(subject_selected)
        self.win.btn_delete_subject.setEnabled(subject_selected)
        self.win.btn_change_subject_icon.setEnabled(subject_selected)
        
        # Tombol Content
        item = self.win.content_tree.currentItem()
        disc_sel, point_sel, item_can_have_date, item_can_be_finished = False, False, False, False
        if item and subject_selected:
            data = item.data(0, self.win.Qt.ItemDataRole.UserRole)
            if data:
                item_dict = self.get_item_dict(data)
                item_can_be_finished = True
                if data.get("type") == "discussion":
                    disc_sel = True
                    if not (item_dict and item_dict.get("points")):
                        item_can_have_date = True
                elif data.get("type") == "point":
                    point_sel, disc_sel = True, True
                    item_can_have_date = True
        
        self.win.btn_tambah_diskusi.setEnabled(subject_selected)
        self.win.btn_edit_diskusi.setEnabled(disc_sel and not point_sel)
        self.win.btn_hapus_diskusi.setEnabled(disc_sel and not point_sel)
        self.win.btn_tambah_point.setEnabled(disc_sel)
        self.win.btn_edit_point.setEnabled(point_sel)
        self.win.btn_hapus_point.setEnabled(point_sel)
        self.win.btn_ubah_tanggal.setEnabled(item_can_have_date)
        self.win.btn_tandai_selesai.setEnabled(item_can_be_finished)

        # Tombol Task & Kategori
        category_selected = self.win.task_category_list.currentItem() is not None
        task_selected = self.win.task_tree.currentItem() is not None
        is_all_tasks_category = category_selected and self.win.task_category_list.currentItem().text() == "Semua Task"
        
        self.win.btn_buat_kategori.setEnabled(True)
        self.win.btn_ubah_kategori.setEnabled(category_selected and not is_all_tasks_category)
        self.win.btn_hapus_kategori.setEnabled(category_selected and not is_all_tasks_category)
        self.win.btn_kategori_naik.setEnabled(category_selected and not is_all_tasks_category and self.win.task_category_list.currentRow() > 1)
        self.win.btn_kategori_turun.setEnabled(category_selected and not is_all_tasks_category and self.win.task_category_list.currentRow() < self.win.task_category_list.count() - 1)
        self.win.btn_ubah_icon_kategori.setEnabled(category_selected and not is_all_tasks_category)
        
        self.win.btn_tambah_task.setEnabled(category_selected and not is_all_tasks_category)
        self.win.btn_edit_task.setEnabled(task_selected)
        self.win.btn_hapus_task.setEnabled(task_selected)
        self.win.btn_task_naik.setEnabled(task_selected and not is_all_tasks_category and self.win.task_tree.currentIndex().row() > 0)
        self.win.btn_task_turun.setEnabled(task_selected and not is_all_tasks_category and self.win.task_tree.currentIndex().row() < self.win.task_tree.topLevelItemCount() - 1)