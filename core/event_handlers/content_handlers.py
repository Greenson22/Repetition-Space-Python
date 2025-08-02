# file: core/event_handlers/content_handlers.py

from datetime import datetime, timedelta
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QComboBox
from PyQt6.QtCore import Qt
import config
from ui_components import DateDialog

class ContentHandlers:
    """Berisi handler untuk event terkait Content Tree (Diskusi dan Point)."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager
    
    # >>>>>>>> MULAI KODE BARU <<<<<<<<
    def update_earliest_date_in_metadata(self):
        """Mencari tanggal dan kode repetisi paling awal dan menyimpannya di metadata."""
        if not self.win.current_content:
            return

        earliest_date = None
        earliest_code = None
        
        for item in self.win.current_content.get("content", []):
            items_to_check = []
            if item.get("points"):
                items_to_check.extend(item["points"])
            else:
                items_to_check.append(item)

            for sub_item in items_to_check:
                if sub_item.get("date") and not sub_item.get("finished"):
                    current_date = datetime.strptime(sub_item["date"], "%Y-%m-%d")
                    if earliest_date is None or current_date < earliest_date:
                        earliest_date = current_date
                        earliest_code = sub_item.get("repetition_code")

        if "metadata" not in self.win.current_content:
            self.win.current_content["metadata"] = {}

        if earliest_date:
            self.win.current_content["metadata"]["earliest_date"] = earliest_date.strftime("%Y-%m-%d")
            self.win.current_content["metadata"]["earliest_code"] = earliest_code
        else:
            self.win.current_content["metadata"]["earliest_date"] = None
            self.win.current_content["metadata"]["earliest_code"] = None
    # >>>>>>>> SELESAI KODE BARU <<<<<<<<

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
            reply = QMessageBox.question(self.win, "Konfirmasi Selesai",
                                         "Apakah Anda yakin ingin menandai item ini sebagai 'Selesai'?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            
            if reply == QMessageBox.StandardButton.Yes:
                today_str = datetime.now().strftime("%Y-%m-%d")
                item_dict["finished"] = True
                item_dict["repetition_code"] = "Finish"
                item_dict["finished_date"] = today_str
                item_dict["date"] = None
                message = "Status diubah menjadi Selesai."
                self.win.refresh_manager.save_and_refresh_content()
                self.win.status_bar.showMessage(message, 4000)
        else:
            reply = QMessageBox.question(self.win, "Konfirmasi Batal",
                                         "Batalkan status 'Selesai'? Item akan kembali ke siklus repetisi.",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)

            if reply == QMessageBox.StandardButton.Yes:
                item_dict["finished"] = False
                item_dict["repetition_code"] = "R0D"
                item_dict["date"] = datetime.now().strftime("%Y-%m-%d")
                if "finished_date" in item_dict:
                    del item_dict["finished_date"]
                message = "Status Selesai dibatalkan."
                self.win.refresh_manager.save_and_refresh_content()
                self.win.status_bar.showMessage(message, 4000)

    def change_date_manually(self):
        item = self.win.content_tree.currentItem()
        if not item: return
        
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_dict = self.get_item_dict(item_data)
        
        if not item_dict: return

        if item_data.get("type") == "discussion" and item_dict.get("points"):
            QMessageBox.information(self.win, "Info", "Tanggal untuk diskusi yang memiliki point diatur oleh point-pointnya.")
            return

        dialog = DateDialog(self.win, initial_date=item_dict.get("date"))
        if dialog.exec():
            new_date = dialog.get_selected_date()
            item_dict["date"] = new_date
            if not item_dict.get("repetition_code"):
                item_dict["repetition_code"] = "R0D"
            self.win.refresh_manager.save_and_refresh_content()
            self.win.status_bar.showMessage(f"Tanggal berhasil diubah menjadi {new_date}", 4000)

    def repetition_code_changed(self, new_code, item_data):
        item_dict = self.get_item_dict(item_data)
        if not item_dict:
            self.win.refresh_manager.refresh_content_tree()
            return
    
        original_date_str = item_dict.get("date", "tidak ada")
    
        base_date = datetime.now()
        days_to_add = config.REPETITION_CODES_DAYS.get(new_code, 0)
        new_date_str = (base_date + timedelta(days=days_to_add)).strftime("%Y-%m-%d")
    
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
            self.win.refresh_manager.refresh_content_tree()
    
    def on_search_text_changed(self):
        query = self.win.search_content_input.text()
        self.win.search_query = query
        self.win.refresh_manager.refresh_content_tree()

    def sort_by_column(self, column_index):
        if self.win.sort_column == column_index:
            self.win.sort_order = Qt.SortOrder.DescendingOrder if self.win.sort_order == Qt.SortOrder.AscendingOrder else Qt.SortOrder.AscendingOrder
        else:
            self.win.sort_column = column_index
            self.win.sort_order = Qt.SortOrder.AscendingOrder
        
        self.win.content_tree.header().setSortIndicator(self.win.sort_column, self.win.sort_order)
        self.win.refresh_manager.refresh_content_tree()
        
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