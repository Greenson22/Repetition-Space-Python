# file: test/core/event_handlers.py

import os
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QComboBox, QFileDialog

from PyQt6.QtCore import Qt

import utils
import config
from ui_components import DateDialog

class EventHandlers:
    """Kelas yang berisi semua logika untuk event handling di ContentManager."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def backup_all_topics(self):
        """Membuat backup semua topic dalam format zip."""
        # Menentukan nama file default, contoh: backup-2023-10-27_10-30-00.zip
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        default_filename = f"backup-topics-{timestamp}.zip"

        # Membuka dialog untuk menyimpan file
        save_path, _ = QFileDialog.getSaveFileName(
            self.win,
            "Simpan Backup Topics",
            default_filename,
            "Zip Files (*.zip)"
        )

        if save_path:
            try:
                # Memanggil data_manager untuk membuat zip
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
            self.win.refresh_subject_list()
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
            self.win.refresh_content_tree()
        self.update_button_states()


    # --- Logika CRUD untuk Topics & Subjects ---
    def create_topic(self):
        name, ok = QInputDialog.getText(self.win, "Buat Topic Baru", "Nama Topic:")
        if ok and name:
            try:
                self.data_manager.create_directory(os.path.join(self.win.base_path, name))
                self.win.refresh_topic_list()
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
                self.win.refresh_topic_list()
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
                self.win.refresh_topic_list()
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
            self.win.refresh_subject_list()


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
                self.win.refresh_subject_list()
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
                self.win.refresh_subject_list()
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
            self.win.refresh_topic_list()

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
            self.win.refresh_subject_list()

    # --- Logika CRUD untuk Content ---
    def add_discussion(self):
        if not self.win.current_subject_path: return
        text, ok = QInputDialog.getText(self.win, "Tambah Diskusi", "Teks Diskusi:")
        if ok and text:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_discussion = { "discussion": text, "date": date_str, "repetition_code": "R0D", "points": [] }
            self.win.current_content["content"].append(new_discussion)
            self.win.save_and_refresh_content()

    def edit_discussion(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "discussion": return
        idx = item.data(0, Qt.ItemDataRole.UserRole)["index"]
        old_text = self.win.current_content["content"][idx]["discussion"]
        new_text, ok = QInputDialog.getText(self.win, "Edit Diskusi", "Teks Diskusi:", text=old_text)
        if ok and new_text:
            self.win.current_content["content"][idx]["discussion"] = new_text
            self.win.save_and_refresh_content()

    def delete_discussion(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "discussion": return
        idx = item.data(0, Qt.ItemDataRole.UserRole)["index"]
        if QMessageBox.question(self.win, "Konfirmasi", "Yakin hapus diskusi ini?") == QMessageBox.StandardButton.Yes:
            del self.win.current_content["content"][idx]
            self.win.save_and_refresh_content()

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
            self.win.save_and_refresh_content()

    def edit_point(self):
        item = self.win.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "point": return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_idx, point_idx = data["parent_index"], data["index"]
        old_text = self.win.current_content["content"][parent_idx]["points"][point_idx]["point_text"]
        new_text, ok = QInputDialog.getText(self.win, "Edit Point", "Teks Point:", text=old_text)
        if ok and new_text:
            self.win.current_content["content"][parent_idx]["points"][point_idx]["point_text"] = new_text
            self.win.save_and_refresh_content()

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
            self.win.save_and_refresh_content()
            
    def toggle_finish_status(self):
        item = self.win.content_tree.currentItem()
        if not item: return

        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_dict = self.get_item_dict(item_data)
        if not item_dict: return
        
        # Toggle status selesai
        current_status = item_dict.get("finished", False)
        item_dict["finished"] = not current_status

        # Jika item ditandai selesai, kosongkan tanggalnya
        if item_dict["finished"]:
            item_dict["date"] = None
            message = "Status diubah menjadi Selesai dan tanggal dikosongkan."
        else:
            # Jika status selesai dibatalkan, tanggal akan tetap kosong kecuali diatur manual lagi.
            message = "Status Selesai dibatalkan."

        self.win.save_and_refresh_content()
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
            self.win.save_and_refresh_content()
            self.win.status_bar.showMessage(f"Tanggal berhasil diubah menjadi {new_date}", 4000)

    def repetition_code_changed(self, new_code, item_data):
        item_dict = self.get_item_dict(item_data)
        if not item_dict:
            self.win.refresh_content_tree()
            return
        
        # --- PERUBAHAN DIMULAI DI SINI ---
        
        # Jika item tidak punya tanggal (misal: baru dibuat atau statusnya 'finished'),
        # gunakan tanggal hari ini sebagai basis.
        current_date_str = item_dict.get("date")
        if not current_date_str:
            current_date = datetime.now()
            # Langsung set tanggal saat ini ke item jika belum ada dan beri kode default
            item_dict["date"] = current_date.strftime("%Y-%m-%d")
            if not item_dict.get("repetition_code"):
                 item_dict["repetition_code"] = "R0D"
        else:
            current_date = datetime.strptime(current_date_str, "%Y-%m-%d")

        days_to_add = config.REPETITION_CODES_DAYS.get(new_code, 0)
        new_date_str = (current_date + timedelta(days=days_to_add)).strftime("%Y-%m-%d")

        # Tidak perlu konfirmasi jika kode sama
        if new_code == item_dict.get("repetition_code") and current_date.strftime("%Y-%m-%d") == item_dict.get("date"):
            self.win.refresh_content_tree()
            return

        reply = QMessageBox.question(self.win, "Konfirmasi Perubahan",
            f"Anda akan mengubah kode repetisi menjadi <b>{new_code}</b>.<br>"
            f"Tanggal akan diperbarui dari {current_date.strftime('%Y-%m-%d')} ke <b>{new_date_str}</b>.<br><br>"
            "Apakah Anda yakin?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            
        if reply == QMessageBox.StandardButton.Yes:
            item_dict["date"] = new_date_str
            item_dict["repetition_code"] = new_code
            self.win.save_and_refresh_content()
        else:
            # Kembalikan tampilan ke state sebelum perubahan jika dibatalkan
            self.win.refresh_content_tree()
        # --- PERUBAHAN BERAKHIR DI SINI ---


    # --- Logika Pengurutan & State ---
    def sort_by_column(self, column_index):
        if self.win.sort_column == column_index:
            self.win.sort_order = Qt.SortOrder.DescendingOrder if self.win.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.win.sort_column = column_index
            self.win.sort_order = Qt.SortOrder.AscendingOrder
        
        self.win.content_tree.header().setSortIndicator(self.win.sort_column, self.win.sort_order)
        self.win.refresh_content_tree()

    def update_button_states(self):
        topic_selected = self.win.topic_list.currentItem() is not None
        subject_selected = self.win.subject_list.currentItem() is not None
        
        self.win.btn_rename_topic.setEnabled(topic_selected)
        self.win.btn_delete_topic.setEnabled(topic_selected)
        self.win.btn_change_topic_icon.setEnabled(topic_selected) # <-- TAMBAHKAN INI
        self.win.btn_buat_subject.setEnabled(topic_selected)

        self.win.btn_rename_subject.setEnabled(subject_selected)
        self.win.btn_delete_subject.setEnabled(subject_selected)
        self.win.btn_change_subject_icon.setEnabled(subject_selected) # <-- TAMBAHKAN INI
        
        item = self.win.content_tree.currentItem()
        disc_sel, point_sel, item_can_have_date, item_can_be_finished = False, False, False, False
        if item and subject_selected:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                item_dict = self.get_item_dict(data)
                item_can_be_finished = True # Semua item bisa ditandai selesai
                if data.get("type") == "discussion":
                    disc_sel = True
                    # Diskusi bisa diubah tanggalnya jika tidak punya points
                    if not (item_dict and item_dict.get("points")):
                        item_can_have_date = True
                elif data.get("type") == "point":
                    point_sel, disc_sel = True, True
                    # Point selalu bisa diubah tanggalnya
                    item_can_have_date = True
        
        self.win.btn_tambah_diskusi.setEnabled(subject_selected)
        self.win.btn_edit_diskusi.setEnabled(disc_sel and not point_sel)
        self.win.btn_hapus_diskusi.setEnabled(disc_sel and not point_sel)
        self.win.btn_tambah_point.setEnabled(disc_sel)
        self.win.btn_edit_point.setEnabled(point_sel)
        self.win.btn_hapus_point.setEnabled(point_sel)
        self.win.btn_ubah_tanggal.setEnabled(item_can_have_date)
        self.win.btn_tandai_selesai.setEnabled(item_can_be_finished)

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
        if current_code: # Hanya set jika ada kode
             combo.setCurrentText(current_code)
        
        # Selalu aktifkan combo box agar bisa memicu perubahan
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