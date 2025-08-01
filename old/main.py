import sys
import os
import shutil
import json
import locale
from datetime import datetime, timedelta
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QListWidget, QListWidgetItem,
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QStatusBar, QStyle,
    QPushButton, QLineEdit, QMessageBox, QInputDialog, QMenu, QSplitter,
    QTreeWidget, QTreeWidgetItem, QComboBox, QDialog, QCalendarWidget,
    QDialogButtonBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize, Qt, QDate

# --- Dialog Kustom untuk Memilih Tanggal ---
class DateDialog(QDialog):
    def __init__(self, parent=None, initial_date=None):
        super().__init__(parent)
        self.setWindowTitle("Pilih Tanggal")
        
        self.layout = QVBoxLayout(self)
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        if initial_date:
            self.calendar.setSelectedDate(QDate.fromString(initial_date, "yyyy-MM-dd"))
        
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        
        self.layout.addWidget(self.calendar)
        self.layout.addWidget(self.buttons)

    def get_selected_date(self):
        return self.calendar.selectedDate().toString("yyyy-MM-dd")

class ContentManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Content Manager")
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))

        self.base_path = "data/contents/topics"
        self.current_topic_path = None
        self.current_subject_path = None
        self.current_content = None
        self.REPETITION_CODES = ["R0D", "R1D", "R3D", "R7D"]

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        topic_panel = self.create_list_panel("📚 Topics", self.topic_selected, [
            ("btn_buat_topic", "Buat", self.create_topic),
            ("btn_rename_topic", "Ubah Nama", self.rename_topic),
            ("btn_delete_topic", "Hapus", self.delete_topic)
        ])
        self.topic_list = topic_panel.findChild(QListWidget)
        splitter.addWidget(topic_panel)

        subject_panel = self.create_list_panel("📄 Subjects", self.subject_selected, [
            ("btn_buat_subject", "Buat", self.create_subject),
            ("btn_rename_subject", "Ubah Nama", self.rename_subject),
            ("btn_delete_subject", "Hapus", self.delete_subject)
        ])
        self.subject_list = subject_panel.findChild(QListWidget)
        splitter.addWidget(subject_panel)

        content_panel = QWidget()
        content_layout = QVBoxLayout(content_panel)
        content_title = QLabel("📝 Content")
        content_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        
        self.content_tree = QTreeWidget()
        self.content_tree.setHeaderLabels(["Content", "Date", "Code"])
        self.content_tree.header().setStretchLastSection(False)
        self.content_tree.header().resizeSection(0, 350)
        self.content_tree.header().resizeSection(1, 150)
        self.content_tree.header().resizeSection(2, 80)
        self.content_tree.currentItemChanged.connect(self.update_button_states)
        
        discussion_button_layout = QHBoxLayout()
        self.btn_tambah_diskusi = QPushButton("Tambah Diskusi")
        self.btn_edit_diskusi = QPushButton("Edit Diskusi")
        self.btn_hapus_diskusi = QPushButton("Hapus Diskusi")
        discussion_button_layout.addWidget(self.btn_tambah_diskusi)
        discussion_button_layout.addWidget(self.btn_edit_diskusi)
        discussion_button_layout.addWidget(self.btn_hapus_diskusi)

        point_button_layout = QHBoxLayout()
        self.btn_tambah_point = QPushButton("Tambah Point")
        self.btn_edit_point = QPushButton("Edit Point")
        self.btn_hapus_point = QPushButton("Hapus Point")
        self.btn_ubah_tanggal = QPushButton("🗓️ Ubah Tanggal")
        point_button_layout.addWidget(self.btn_tambah_point)
        point_button_layout.addWidget(self.btn_edit_point)
        point_button_layout.addWidget(self.btn_hapus_point)
        point_button_layout.addWidget(self.btn_ubah_tanggal)
        
        content_layout.addWidget(content_title)
        content_layout.addWidget(self.content_tree)
        content_layout.addWidget(QLabel("Manajemen Diskusi:"))
        content_layout.addLayout(discussion_button_layout)
        content_layout.addWidget(QLabel("Manajemen Point & Tanggal:"))
        content_layout.addLayout(point_button_layout)
        splitter.addWidget(content_panel)

        self.btn_tambah_diskusi.clicked.connect(self.add_discussion)
        self.btn_edit_diskusi.clicked.connect(self.edit_discussion)
        self.btn_hapus_diskusi.clicked.connect(self.delete_discussion)
        self.btn_tambah_point.clicked.connect(self.add_point)
        self.btn_edit_point.clicked.connect(self.edit_point)
        self.btn_hapus_point.clicked.connect(self.delete_point)
        self.btn_ubah_tanggal.clicked.connect(self.change_date_manually)

        splitter.setSizes([200, 200, 800])
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.apply_stylesheet()
        self.refresh_topic_list()
        self.update_button_states()

    def create_list_panel(self, title, selection_handler, buttons_config):
        panel = QWidget()
        layout = QVBoxLayout(panel)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        list_widget = QListWidget()
        list_widget.setIconSize(QSize(22, 22))
        list_widget.currentItemChanged.connect(selection_handler)
        button_layout = QHBoxLayout()
        for attr_name, text, func in buttons_config:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            setattr(self, attr_name, btn)
            button_layout.addWidget(btn)
        layout.addWidget(title_label)
        layout.addWidget(list_widget)
        layout.addLayout(button_layout)
        return panel

    def topic_selected(self, current, previous):
        self.subject_list.clear()
        self.content_tree.clear()
        self.current_content = None
        if not current:
            self.current_topic_path = None
            self.update_button_states()
            return
        self.current_topic_path = os.path.join(self.base_path, current.text())
        self.refresh_subject_list()

    def subject_selected(self, current, previous):
        self.content_tree.clear()
        if not current:
            self.current_subject_path = None
            self.current_content = None
            self.update_button_states()
            return
        subject_name = f"{current.text()}.json"
        self.current_subject_path = os.path.join(self.current_topic_path, subject_name)
        self.refresh_content_tree()

    def refresh_topic_list(self):
        self.topic_list.clear()
        if not os.path.exists(self.base_path): os.makedirs(self.base_path)
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        folders = sorted([d for d in os.listdir(self.base_path) if os.path.isdir(os.path.join(self.base_path, d))])
        for folder in folders:
            self.topic_list.addItem(QListWidgetItem(icon, folder))

    def refresh_subject_list(self):
        self.subject_list.clear()
        if not self.current_topic_path: return
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        files = sorted([f for f in os.listdir(self.current_topic_path) if f.endswith('.json')])
        for file in files:
            self.subject_list.addItem(QListWidgetItem(icon, os.path.splitext(file)[0]))

    def refresh_content_tree(self):
        self.content_tree.clear()
        if not self.current_subject_path: return
        try:
            with open(self.current_subject_path, 'r', encoding='utf-8') as f:
                self.current_content = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.current_content = {"content": [], "metadata": None}
            self.save_current_subject()

        for i, discussion_data in enumerate(self.current_content.get("content", [])):
            discussion_text = discussion_data.get("discussion", "Diskusi kosong")
            points = discussion_data.get("points", [])
            parent_item = QTreeWidgetItem(self.content_tree)
            parent_item.setText(0, discussion_text)
            parent_item.setData(0, Qt.ItemDataRole.UserRole, {"type": "discussion", "index": i})
            if not points:
                date_str = discussion_data.get("date", "")
                code = discussion_data.get("repetition_code", "R0D")
                parent_item.setText(1, self.format_date_with_day(date_str))
                self.create_repetition_combobox(parent_item, 2, code, {"type": "discussion", "index": i})
            for j, point_data in enumerate(points):
                point_text = point_data.get("point_text", "Point kosong")
                date_str = point_data.get("date", "")
                code = point_data.get("repetition_code", "R0D")
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, point_text)
                child_item.setText(1, self.format_date_with_day(date_str))
                item_data = {"type": "point", "parent_index": i, "index": j}
                child_item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                self.create_repetition_combobox(child_item, 2, code, item_data)
        self.content_tree.expandAll()
        self.update_button_states()

    def format_date_with_day(self, date_str):
        if not date_str: return ""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%A, %Y-%m-%d")
        except ValueError:
            return date_str

    def change_date_manually(self):
        item = self.content_tree.currentItem()
        if not item: return
        item_data = item.data(0, Qt.ItemDataRole.UserRole)
        item_dict = self.get_item_dict(item_data)
        if not item_dict or not item_dict.get("date"):
            QMessageBox.information(self, "Info", "Item ini tidak memiliki tanggal untuk diubah.")
            return
        dialog = DateDialog(self, initial_date=item_dict.get("date"))
        if dialog.exec():
            new_date = dialog.get_selected_date()
            item_dict["date"] = new_date
            self.save_and_refresh_content()
            self.status_bar.showMessage(f"Tanggal berhasil diubah menjadi {new_date}", 4000)

    def get_item_dict(self, item_data):
        if not item_data: return None
        item_type = item_data.get("type")
        if item_type == "discussion":
            return self.current_content["content"][item_data["index"]]
        elif item_type == "point":
            return self.current_content["content"][item_data["parent_index"]]["points"][item_data["index"]]
        return None

    def create_repetition_combobox(self, item, column, current_code, item_data):
        combo = QComboBox()
        combo.addItems(self.REPETITION_CODES)
        combo.setCurrentText(current_code)
        combo.currentTextChanged.connect(
            lambda new_code, data=item_data: self.repetition_code_changed(new_code, data)
        )
        self.content_tree.setItemWidget(item, column, combo)
        
    def repetition_code_changed(self, new_code, item_data):
        item_dict = self.get_item_dict(item_data)
        if not item_dict:
            self.refresh_content_tree()
            return
        old_date_str = item_dict.get("date")
        if not old_date_str:
            QMessageBox.warning(self, "Gagal", "Item ini tidak memiliki tanggal untuk diperbarui.")
            self.refresh_content_tree()
            return
        try:
            days_to_add_map = {'R0D': 0, 'R1D': 1, 'R3D': 3, 'R7D': 7}
            days_to_add = days_to_add_map.get(new_code, 0)
            old_date = datetime.strptime(old_date_str, "%Y-%m-%d")
            new_date = old_date + timedelta(days=days_to_add)
            new_date_str = new_date.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            QMessageBox.critical(self, "Error", "Format tanggal tidak valid.")
            self.refresh_content_tree()
            return
        reply = QMessageBox.question(self, "Konfirmasi Perubahan",
            f"""Anda akan mengubah kode repetisi menjadi <b>{new_code}</b>.<br><br>
            Tanggal akan diperbarui:<br>
            - Tanggal Lama: <b>{old_date_str}</b><br>
            - Tanggal Baru: <b>{new_date_str}</b><br><br>
            Apakah Anda yakin ingin melanjutkan?""",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            item_dict["date"] = new_date_str
            item_dict["repetition_code"] = new_code
            self.save_current_subject()
            self.status_bar.showMessage(f"Item berhasil diperbarui ke {new_date_str} ({new_code})", 4000)
        self.refresh_content_tree()

    def save_current_subject(self):
        if self.current_subject_path and self.current_content is not None:
            with open(self.current_subject_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_content, f, indent=2, ensure_ascii=False)

    def save_and_refresh_content(self):
        self.save_current_subject()
        self.refresh_content_tree()

    def update_button_states(self):
        topic_selected = self.topic_list.currentItem() is not None
        subject_selected = self.subject_list.currentItem() is not None
        self.btn_rename_topic.setEnabled(topic_selected)
        self.btn_delete_topic.setEnabled(topic_selected)
        self.btn_buat_subject.setEnabled(topic_selected)
        self.btn_rename_subject.setEnabled(subject_selected)
        self.btn_delete_subject.setEnabled(subject_selected)
        content_item = self.content_tree.currentItem()
        discussion_selected = False
        point_selected = False
        date_exists = False
        if content_item and subject_selected:
            item_data = content_item.data(0, Qt.ItemDataRole.UserRole)
            if item_data:
                item_dict = self.get_item_dict(item_data)
                if item_dict and item_dict.get("date"):
                    date_exists = True
                item_type = item_data.get("type")
                if item_type == "discussion":
                    discussion_selected = True
                elif item_type == "point":
                    point_selected = True
                    discussion_selected = True
        self.btn_tambah_diskusi.setEnabled(subject_selected)
        self.btn_edit_diskusi.setEnabled(discussion_selected)
        self.btn_hapus_diskusi.setEnabled(discussion_selected and not point_selected)
        self.btn_tambah_point.setEnabled(discussion_selected)
        self.btn_edit_point.setEnabled(point_selected)
        self.btn_hapus_point.setEnabled(point_selected)
        self.btn_ubah_tanggal.setEnabled(date_exists)

    def create_topic(self):
        name, ok = QInputDialog.getText(self, "Buat Topic Baru", "Nama Topic:")
        if ok and name:
            try:
                os.makedirs(os.path.join(self.base_path, name))
                self.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self, "Gagal", f"Tidak dapat membuat topic: {e}")

    def rename_topic(self):
        item = self.topic_list.currentItem()
        if not item: return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Ubah Nama Topic", "Nama Baru:", text=old_name)
        if ok and new_name and new_name != old_name:
            try:
                os.rename(os.path.join(self.base_path, old_name), os.path.join(self.base_path, new_name))
                self.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self, "Gagal", f"Tidak dapat mengubah nama: {e}")

    def delete_topic(self):
        item = self.topic_list.currentItem()
        if not item: return
        name = item.text()
        reply = QMessageBox.question(self, "Konfirmasi", f"Yakin ingin menghapus topic '{name}' dan semua isinya?")
        if reply == QMessageBox.StandardButton.Yes:
            try:
                shutil.rmtree(os.path.join(self.base_path, name))
                self.refresh_topic_list()
            except Exception as e:
                QMessageBox.warning(self, "Gagal", f"Tidak dapat menghapus: {e}")

    def create_subject(self):
        if not self.current_topic_path: return
        name, ok = QInputDialog.getText(self, "Buat Subject Baru", "Nama Subject:")
        if ok and name:
            file_path = os.path.join(self.current_topic_path, f"{name}.json")
            self.current_content = {"content": [], "metadata": None}
            self.current_subject_path = file_path
            self.save_current_subject()
            self.refresh_subject_list()

    def rename_subject(self):
        if not self.current_topic_path or not self.subject_list.currentItem(): return
        old_name = self.subject_list.currentItem().text()
        new_name, ok = QInputDialog.getText(self, "Ubah Nama Subject", "Nama Baru:", text=old_name)
        if ok and new_name and new_name != old_name:
            old_file = os.path.join(self.current_topic_path, f"{old_name}.json")
            new_file = os.path.join(self.current_topic_path, f"{new_name}.json")
            try:
                os.rename(old_file, new_file)
                self.refresh_subject_list()
            except Exception as e:
                QMessageBox.warning(self, "Gagal", f"Tidak dapat mengubah nama file: {e}")

    def delete_subject(self):
        if not self.current_topic_path or not self.subject_list.currentItem(): return
        name = self.subject_list.currentItem().text()
        reply = QMessageBox.question(self, "Konfirmasi", f"Yakin ingin menghapus subject '{name}'?")
        if reply == QMessageBox.StandardButton.Yes:
            file_path = os.path.join(self.current_topic_path, f"{name}.json")
            try:
                os.remove(file_path)
                self.refresh_subject_list()
            except Exception as e:
                QMessageBox.warning(self, "Gagal", f"Tidak dapat menghapus file: {e}")

    def add_discussion(self):
        text, ok = QInputDialog.getText(self, "Tambah Diskusi", "Teks Diskusi:")
        if ok and text:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_discussion = { "discussion": text, "date": date_str, "repetition_code": "R0D", "points": [] }
            self.current_content["content"].append(new_discussion)
            self.save_and_refresh_content()

    def edit_discussion(self):
        item = self.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "discussion": return
        idx = item.data(0, Qt.ItemDataRole.UserRole)["index"]
        old_text = self.current_content["content"][idx]["discussion"]
        new_text, ok = QInputDialog.getText(self, "Edit Diskusi", "Teks Diskusi:", text=old_text)
        if ok and new_text:
            self.current_content["content"][idx]["discussion"] = new_text
            self.save_and_refresh_content()

    def delete_discussion(self):
        item = self.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "discussion": return
        idx = item.data(0, Qt.ItemDataRole.UserRole)["index"]
        if QMessageBox.question(self, "Konfirmasi", "Yakin hapus diskusi ini?") == QMessageBox.StandardButton.Yes:
            del self.current_content["content"][idx]
            self.save_and_refresh_content()

    def add_point(self):
        parent_item = self.content_tree.currentItem()
        if not parent_item: return
        if parent_item.parent(): parent_item = parent_item.parent()
        data = parent_item.data(0, Qt.ItemDataRole.UserRole)
        if data["type"] != "discussion": return
        parent_idx = data["index"]
        text, ok = QInputDialog.getText(self, "Tambah Point", "Teks Point:")
        if ok and text:
            date_str = datetime.now().strftime("%Y-%m-%d")
            new_point = { "point_text": text, "repetition_code": "R0D", "date": date_str }
            if not self.current_content["content"][parent_idx]["points"]:
                self.current_content["content"][parent_idx]["date"] = None
                self.current_content["content"][parent_idx]["repetition_code"] = None
            self.current_content["content"][parent_idx]["points"].append(new_point)
            self.save_and_refresh_content()

    def edit_point(self):
        item = self.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "point": return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_idx, point_idx = data["parent_index"], data["index"]
        old_text = self.current_content["content"][parent_idx]["points"][point_idx]["point_text"]
        new_text, ok = QInputDialog.getText(self, "Edit Point", "Teks Point:", text=old_text)
        if ok and new_text:
            self.current_content["content"][parent_idx]["points"][point_idx]["point_text"] = new_text
            self.save_and_refresh_content()

    def delete_point(self):
        item = self.content_tree.currentItem()
        if not item or item.data(0, Qt.ItemDataRole.UserRole)["type"] != "point": return
        data = item.data(0, Qt.ItemDataRole.UserRole)
        parent_idx, point_idx = data["parent_index"], data["index"]
        if QMessageBox.question(self, "Konfirmasi", "Yakin hapus point ini?") == QMessageBox.StandardButton.Yes:
            del self.current_content["content"][parent_idx]["points"][point_idx]
            if not self.current_content["content"][parent_idx]["points"]:
                 self.current_content["content"][parent_idx]["date"] = datetime.now().strftime("%Y-%m-%d")
                 self.current_content["content"][parent_idx]["repetition_code"] = "R0D"
            self.save_and_refresh_content()

    def apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget, QDialog { background-color: #2E3440; color: #D8DEE9; font-family: Segoe UI; font-size: 10pt; }
            QSplitter::handle { background-color: #4C566A; width: 3px; }
            QLabel { color: #ECEFF4; padding-bottom: 5px; }
            QListWidget, QTreeWidget { background-color: #3B4252; border: 1px solid #4C566A; border-radius: 5px; padding: 5px; }
            QListWidget::item:selected, QTreeWidget::item:selected { background-color: #88C0D0; color: #2E3440; }
            QComboBox { background-color: #D8DEE9; color: #2E3440; border-radius: 3px; padding: 1px 4px; }
            QPushButton { background-color: #4C566A; border: none; padding: 8px; border-radius: 5px; font-weight: bold; }
            QPushButton:hover { background-color: #5E81AC; }
            QPushButton:disabled { background-color: #434C5E; color: #6F7A8C; }
            QHeaderView::section { background-color: #434C5E; padding: 4px; border: 1px solid #4C566A; }
            QCalendarWidget QToolButton { color: white; }
            QCalendarWidget QMenu { background-color: #4C566A; }
            QCalendarWidget QSpinBox { background-color: #D8DEE9; color: #2E3440; }
            QCalendarWidget QAbstractItemView { background-color: #3B4252; selection-background-color: #88C0D0; selection-color: #2E3440; }
        """)

def main():
    try:
        locale.setlocale(locale.LC_TIME, 'id_ID.UTF-8')
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'Indonesian_Indonesia.1252')
        except locale.Error:
            print("Peringatan: Locale Bahasa Indonesia tidak ditemukan. Nama hari mungkin dalam Bahasa Inggris.")

    app = QApplication(sys.argv)
    window = ContentManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()