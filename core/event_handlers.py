# file: test/core/event_handlers.py

import os
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QComboBox, QFileDialog
from PyQt6.QtCore import Qt

import utils
import config
from ui_components import DateDialog
# Import the new TaskEditDialog
from core.ui_components.task_edit_dialog import TaskEditDialog

class EventHandlers:
    """Kelas yang berisi semua logika untuk event handling di ContentManager."""
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
                # Memanggil data_manager untuk melakukan impor
                self.data_manager.import_backup_zip(open_path)
                QMessageBox.information(
                    self.win,
                    "Impor Berhasil",
                    "Topics dari file backup berhasil diimpor."
                )
                # Refresh semua list untuk menampilkan data baru
                self.win.refresh_manager.refresh_topic_list()
                self.win.refresh_manager.refresh_task_category_list()
            except Exception as e:
                QMessageBox.critical(
                    self.win,
                    "Impor Gagal",
                    f"Terjadi kesalahan saat mengimpor backup:\n{e}"
                )

    def update_earliest_date_in_metadata(self):
        """Mencari tanggal & kode paling awal dan menyimpannya di metadata."""
        if not self.win.current_content:
            return

        content_items = self.win.current_content.get("content", [])
        earliest_date_str = None
        earliest_code = None
        
        all_items = []
        for item in content_items:
            # Item bisa berupa discussion (jika tidak punya points) atau point
            if item.get("points"):
                for point in item.get("points", []):
                    if point.get("date"):
                        all_items.append(point)
            elif item.get("date"):
                all_items.append(item)

        if all_items:
            try:
                # Cari item dengan tanggal paling awal
                earliest_item = min(
                    all_items,
                    key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d")
                )
                earliest_date_str = earliest_item.get("date")
                earliest_code = earliest_item.get("repetition_code")
            except (ValueError, TypeError):
                # Handle kasus jika tidak ada item dengan tanggal yang valid
                earliest_date_str = None
                earliest_code = None

        # Buat atau update metadata
        if "metadata" not in self.win.current_content or self.win.current_content.get("metadata") is None:
            self.win.current_content["metadata"] = {}
        
        self.win.current_content["metadata"]["earliest_date"] = earliest_date_str
        self.win.current_content["metadata"]["earliest_code"] = earliest_code

    # --- Bagian Event Handlers (Seleksi, Klik Tombol, dll) ---
    def topic_selected(self, current, previous):
        self.win.subject_list.clear()
        self.win.content_tree.clear()
        self.win.current_content = None
        if not current:
            self.win.current_topic_path = None
        else:
            topic_name = current.text().split(" ", 1)[1] # Ambil nama setelah ikon
            self.win.current_topic_path = os.path.join(self.win.base_path, topic_name)
            self.win.refresh_manager.refresh_subject_list()
            # BARU: Otomatis pilih subject pertama jika ada
            if self.win.subject_list.count() > 0:
                self.win.subject_list.setCurrentRow(0)
        self.update_button_states()

    def subject_selected(self, current, previous):
        self.win.content_tree.clear()
        if not current:
            self.win.current_subject_path = None
            self.win.current_content = None
        else:
            # Ekstrak nama subjek dari teks yang mungkin memiliki beberapa baris
            subject_name_full = current.text().split(" ", 1)[1] # Ambil nama setelah ikon
            subject_name = subject_name_full.split('\n')[0]
            
            subject_file_name = f"{subject_name}.json"
            self.win.current_subject_path = os.path.join(self.win.current_topic_path, subject_file_name)
            self.win.refresh_manager.refresh_content_tree()
        self.update_button_states()


    # --- Logika CRUD untuk Topics & Subjects ---
    def create_topic(self):
        name, ok = QInputDialog.getText(self.win, "Buat Topic Baru", "Nama Topic:")
        if ok and name:
            try:
                self.data_manager.create_directory(os.path.join(self.win.base_path, name))
                self.win.refresh_manager.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self.win, "Gagal", f"Tidak dapat membuat topic: {e}")

    def rename_topic(self):
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

    def create_subject(self):
        if not self.win.current_topic_path: return
        name, ok = QInputDialog.getText(self.win, "Buat Subject Baru", "Nama Subject:")
        if ok and name:
            # Menghapus spasi di awal/akhir nama
            name = name.strip()
            if not name:
                QMessageBox.warning(self.win, "Nama Tidak Valid", "Nama subject tidak boleh kosong.")
                return

            file_path = os.path.join(self.win.current_topic_path, f"{name}.json")

            # Cek jika file dengan nama yang sama sudah ada
            if os.path.exists(file_path):
                QMessageBox.warning(self.win, "Gagal", f"Subject dengan nama '{name}' sudah ada.")
                return

            self.win.current_content = {"content": [], "metadata": {"earliest_date": None, "earliest_code": None, "icon": config.DEFAULT_SUBJECT_ICON}}
            self.win.current_subject_path = file_path
            self.data_manager.save_content(file_path, self.win.current_content)
            self.win.refresh_manager.refresh_subject_list()


    def rename_subject(self):
        if not self.win.current_topic_path or not self.win.subject_list.currentItem(): return
        
        # Ekstrak nama subjek dari teks yang mungkin memiliki beberapa baris
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
        if not self.win.current_topic_path or not self.win.subject_list.currentItem(): return
        
        # Ekstrak nama subjek dari teks yang mungkin memiliki beberapa baris
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

    # --- LOGIKA ICON ---
    def change_topic_icon(self):
        item = self.win.topic_list.currentItem()
        if not item: return
        
        topic_name = item.text().split(" ", 1)[1]
        
        icon, ok = QInputDialog.getItem(self.win, "Pilih Ikon Topic", "Pilih ikon:", config.AVAILABLE_ICONS, 0, False)
        
        if ok and icon:
            self.data_manager.save_topic_config(topic_name, {'icon': icon})
            self.win.refresh_manager.refresh_topic_list()

    def change_subject_icon(self):
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

    # --- Logika CRUD untuk Content ---
    def add_discussion(self):
        if not self.win.current_subject_path: return
        text, ok = QInputDialog.getText(self.win, "Tambah Diskusi", "Teks Diskusi:")
        if ok and text:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_discussion = { "discussion": text, "date": date_str, "repetition_code": "R0D", "points": [] }
            self.win.current_content["content"].append(new_discussion)
            self.win.refresh_manager.save_and_refresh_content()

    def edit_discussion(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "discussion": return
        idx = item.data(0, Qt.ItemDataRole.UserRole)["index"]
        old_text = self.win.current_content["content"][idx]["discussion"]
        new_text, ok = QInputDialog.getText(self.win, "Edit Diskusi", "Teks Diskusi:", text=old_text)
        if ok and new_text:
            self.win.current_content["content"][idx]["discussion"] = new_text
            self.win.refresh_manager.save_and_refresh_content()

    def delete_discussion(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "discussion": return
        idx = item.data(0, Qt.ItemDataRole.UserRole)["index"]
        if QMessageBox.question(self.win, "Konfirmasi", "Yakin hapus diskusi ini?") == QMessageBox.StandardButton.Yes:
            del self.win.current_content["content"][idx]
            self.win.refresh_manager.save_and_refresh_content()

    def add_point(self):
        parent_item = self.win.content_tree.currentItem()
        if not parent_item: return
        if parent_item.parent(): parent_item = parent_item.parent()
        data = parent_item.data(0, Qt.ItemDataRole.UserRole)
        if data["type"] != "discussion": return
        parent_idx = data["index"]
        text, ok = QInputDialog.getText(self.win, "Tambah Point", "Teks Point:")
        if ok and text:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_point = { "point_text": text, "repetition_code": "R0D", "date": date_str }
            discussion = self.win.current_content["content"][parent_idx]
            if "points" not in discussion:
                discussion["points"] = []
            if not discussion["points"]:
                discussion["date"] = None
                discussion["repetition_code"] = None
            discussion["points"].append(new_point)
            self.win.refresh_manager.save_and_refresh_content()

    def edit_point(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "point": return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_idx, point_idx = data["parent_index"], data["index"]
        old_text = self.win.current_content["content"][parent_idx]["points"][point_idx]["point_text"]
        new_text, ok = QInputDialog.getText(self.win, "Edit Point", "Teks Point:", text=old_text)
        if ok and new_text:
            self.win.current_content["content"][parent_idx]["points"][point_idx]["point_text"] = new_text
            self.win.refresh_manager.save_and_refresh_content()

    def delete_point(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "point": return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_idx, point_idx = data["parent_index"], data["index"]
        if QMessageBox.question(self.win, "Konfirmasi", "Yakin hapus point ini?") == QMessageBox.StandardButton.Yes:
            discussion = self.win.current_content["content"][parent_idx]
            del discussion["points"][point_idx]
            if not discussion["points"]:
                discussion["date"] = datetime.now().strftime("%Y-%m-%d")
                discussion["repetition_code"] = "R0D"
            self.win.refresh_manager.save_and_refresh_content()
            
    def toggle_finish_status(self):
        item = self.win.content_tree.currentItem()
        if not item: return

        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_dict = self.get_item_dict(item_data)
        if not item_dict: return
        
        current_status = item_dict.get("finished", False)
        
        if not current_status:
            # --- Logika untuk menandai selesai ---
            reply = QMessageBox.question(self.win, "Konfirmasi Selesai",
                                         "Apakah Anda yakin ingin menandai item ini sebagai 'Selesai'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                today_str = datetime.now().strftime("%Y-%m-%d")
                item_dict["finished"] = True
                item_dict["repetition_code"] = "Finish"
                item_dict["finished_date"] = today_str # Simpan tanggal selesai
                item_dict["date"] = None # Hapus tanggal repetisi
                message = "Status diubah menjadi Selesai."
                self.win.refresh_manager.save_and_refresh_content()
                self.win.status_bar.showMessage(message, 4000)
        else:
            # --- Logika untuk membatalkan status selesai ---
            reply = QMessageBox.question(self.win, "Konfirmasi Batal",
                                         "Batalkan status 'Selesai'? Item akan kembali ke siklus repetisi.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                item_dict["finished"] = False
                item_dict["repetition_code"] = "R0D" # Kembalikan ke kode awal
                item_dict["date"] = datetime.now().strftime("%Y-%m-%d") # Atur tanggal ke hari ini
                if "finished_date" in item_dict:
                    del item_dict["finished_date"] # Hapus tanggal selesai
                message = "Status Selesai dibatalkan."
                self.win.refresh_manager.save_and_refresh_content()
                self.win.status_bar.showMessage(message, 4000)

    def change_date_manually(self):
        item = self.win.content_tree.currentItem()
        if not item: return
        
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_dict = self.get_item_dict(item_data)
        
        if not item_dict: return

        # Mencegah pengubahan tanggal pada diskusi yang sudah memiliki point,
        # karena tanggalnya seharusnya diatur dari point.
        if item_data.get("type") == "discussion" and item_dict.get("points"):
            QMessageBox.information(self.win, "Info", "Tanggal untuk diskusi yang memiliki point diatur oleh point-pointnya.")
            return

        dialog = DateDialog(self.win, initial_date=item_dict.get("date"))
        if dialog.exec():
            new_date = dialog.get_selected_date()
            item_dict["date"] = new_date
            # Jika item belum punya kode repetisi, berikan kode default.
            if not item_dict.get("repetition_code"):
                item_dict["repetition_code"] = "R0D"
            self.win.refresh_manager.save_and_refresh_content()
            self.win.status_bar.showMessage(f"Tanggal berhasil diubah menjadi {new_date}", 4000)

    def repetition_code_changed(self, new_code, item_data):
        item_dict = self.get_item_dict(item_data)
        if not item_dict:
            self.win.refresh_manager.refresh_content_tree()
            return
    
        # Get the original date for display purposes in the confirmation dialog
        original_date_str = item_dict.get("date", "tidak ada")
    
        # The new date is always calculated from today's date
        base_date = datetime.now()
        days_to_add = config.REPETITION_CODES_DAYS.get(new_code, 0)
        new_date_str = (base_date + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
    
        # If nothing would change, no need to ask for confirmation
        if new_code == item_dict.get("repetition_code") and original_date_str == new_date_str:
            self.win.refresh_manager.refresh_content_tree()
            return
    
        reply = QMessageBox.question(self.win, "Konfirmasi Perubahan",
            f"Anda akan mengubah kode repetisi menjadi <b>{new_code}</b>.<br>"
            f"Tanggal akan diperbarui dari {original_date_str} ke <b>{new_date_str}</b> (berdasarkan tanggal hari ini).<br><br>"
            "Apakah Anda yakin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
        if reply == QMessageBox.StandardButton.Yes:
            item_dict["date"] = new_date_str
            item_dict["repetition_code"] = new_code
            self.win.refresh_manager.save_and_refresh_content()
        else:
            # If the user cancels, revert the combobox to the original value.
            self.win.refresh_manager.refresh_content_tree()
    
    def on_search_text_changed(self):
        query = self.win.search_content_input.text()
        self.win.search_query = query
        self.win.refresh_manager.refresh_content_tree()

    # --- Logika Pengurutan & State ---
    def sort_by_column(self, column_index):
        if self.win.sort_column == column_index:
            self.win.sort_order = Qt.SortOrder.DescendingOrder if self.win.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.win.sort_column = column_index
            self.win.sort_order = Qt.SortOrder.AscendingOrder
        
        self.win.content_tree.header().setSortIndicator(self.win.sort_column, self.win.sort_order)
        self.win.refresh_manager.refresh_content_tree()

    def update_button_states(self):
        topic_selected = self.win.topic_list.currentItem() is not None
        subject_selected = self.win.subject_list.currentItem() is not None
        
        self.win.btn_rename_topic.setEnabled(topic_selected)
        self.win.btn_delete_topic.setEnabled(topic_selected)
        self.win.btn_change_topic_icon.setEnabled(topic_selected)
        self.win.btn_buat_subject.setEnabled(topic_selected)

        self.win.btn_rename_subject.setEnabled(subject_selected)
        self.win.btn_delete_subject.setEnabled(subject_selected)
        self.win.btn_change_subject_icon.setEnabled(subject_selected)
        
        item = self.win.content_tree.currentItem()
        disc_sel, point_sel, item_can_have_date, item_can_be_finished = False, False, False, False
        if item and subject_selected:
            data = item.data(0, Qt.ItemDataRole.UserRole)
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

        # --- BARU: Logika untuk tombol-tombol Task ---
        category_selected = self.win.task_category_list.currentItem() is not None
        task_selected = self.win.task_tree.currentItem() is not None
        is_all_tasks_category = category_selected and self.win.task_category_list.currentItem().text() == "Semua Task"
        
        # --- Logika Tombol Kategori ---
        self.win.btn_buat_kategori.setEnabled(True)
        self.win.btn_ubah_kategori.setEnabled(category_selected and not is_all_tasks_category)
        self.win.btn_hapus_kategori.setEnabled(category_selected and not is_all_tasks_category)
        self.win.btn_kategori_naik.setEnabled(category_selected and not is_all_tasks_category and self.win.task_category_list.currentRow() > 1) # >1 karena index 0 adalah "Semua Task"
        self.win.btn_kategori_turun.setEnabled(category_selected and not is_all_tasks_category and self.win.task_category_list.currentRow() < self.win.task_category_list.count() - 1)
        self.win.btn_ubah_icon_kategori.setEnabled(category_selected and not is_all_tasks_category)
        
        # --- Logika Tombol Task ---
        self.win.btn_tambah_task.setEnabled(category_selected and not is_all_tasks_category)
        self.win.btn_edit_task.setEnabled(task_selected)
        self.win.btn_hapus_task.setEnabled(task_selected)
        self.win.btn_task_naik.setEnabled(task_selected and not is_all_tasks_category and self.win.task_tree.currentIndex().row() > 0)
        self.win.btn_task_turun.setEnabled(task_selected and not is_all_tasks_category and self.win.task_tree.currentIndex().row() < self.win.task_tree.topLevelItemCount() - 1)

    # --- Bagian utilitas internal ---
    def get_item_dict(self, item_data):
        if not item_data: return None
        content_list = self.win.current_content.get("content", [])
        try:
            if item_data["type"] == "discussion":
                return content_list[item_data["index"]]
            elif item_data["type"] == "point":
                return content_list[item_data["parent_index"]]["points"][item_data["index"]]
        except (IndexError, KeyError):
            return None
        return None

    def create_repetition_combobox(self, item, column, current_code, item_data):
        combo = QComboBox()
        combo.addItems(config.REPETITION_CODES)
        if current_code:
             combo.setCurrentText(current_code)
        
        item_dict = self.get_item_dict(item_data)
        can_have_date = False
        if item_data.get("type") == "point":
            can_have_date = True
        elif item_data.get("type") == "discussion" and not (item_dict and item_dict.get("points")):
            can_have_date = True
        
        combo.setEnabled(can_have_date)

        if can_have_date:
            combo.currentTextChanged.connect(
                lambda new_code, data=item_data: self.repetition_code_changed(new_code, data)
            )

        self.win.content_tree.setItemWidget(item, column, combo)
    
    # --- BARU: Event Handlers untuk Task dan Kategori ---
    def task_category_selected(self, current, previous):
        """Handler saat kategori task dipilih."""
        if not current:
            self.win.current_task_category = None
        else:
            text = current.text()
            if text == "Semua Task":
                self.win.current_task_category = "Semua Task"
            else:
                # Perbaikan: Ekstrak nama dengan aman
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
            # Pilih item yang baru diubah namanya
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
            # Pilih kembali item yang sama
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
                'checked': False  # Default status checklist
            }
            self.data_manager.save_task(self.win.current_task_category, task_name, new_task)
            self.win.refresh_manager.refresh_task_list()

    def edit_task(self):
        """Membuka dialog untuk mengedit nama, hitungan, dan tanggal task."""
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
            
            # Jika nama berubah, kita harus menghapus yang lama dan menambahkan yang baru
            if new_task_name != old_task_name:
                self.data_manager.delete_task(category_name, old_task_name)
            
            self.data_manager.save_task(category_name, new_task_name, updated_data)
            
            self.win.refresh_manager.refresh_task_list()
            # Coba pilih kembali task yang baru di-edit
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

    # --- BARU: Handler untuk memindahkan item ---
    def move_category_up(self):
        self._move_category(-1)

    def move_category_down(self):
        self._move_category(1)

    def _move_category(self, direction):
        current_row = self.win.task_category_list.currentRow()
        # Index 0 adalah "Semua Task", jadi tidak bisa dipindahkan
        if current_row <= 0: return

        tasks_data = self.data_manager.load_tasks_data()
        categories = tasks_data.get("categories", [])
        
        # Penyesuaian index karena ada "Semua Task" di UI
        cat_index = current_row - 1
        
        if 0 <= cat_index < len(categories):
            new_index = cat_index + direction
            if 0 <= new_index < len(categories):
                # Tukar posisi
                categories[cat_index], categories[new_index] = categories[new_index], categories[cat_index]
                self.data_manager.save_tasks_data(tasks_data)
                
                # Refresh list dan pilih kembali item yang dipindahkan
                self.win.refresh_manager.refresh_task_category_list()
                self.win.task_category_list.setCurrentRow(new_index + 1)

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
                        # Tukar posisi
                        tasks[current_index], tasks[new_index] = tasks[new_index], tasks[current_index]
                        self.data_manager.save_tasks_data(tasks_data)
                        
                        # Refresh dan pilih kembali
                        self.win.refresh_manager.refresh_task_list()
                        # Cari item yang baru untuk diseleksi
                        new_item_to_select = self.win.task_tree.topLevelItem(new_index)
                        if new_item_to_select:
                            self.win.task_tree.setCurrentItem(new_item_to_select)
                        break

    # --- BARU: Handler untuk checklist ---
    def task_item_changed(self, item, column):
        """Handler saat status checklist sebuah task diubah."""
        if column == 0: # Hanya bereaksi pada perubahan di kolom pertama (tempat checkbox)
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