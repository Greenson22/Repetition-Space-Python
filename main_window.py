# file: test/main_window.py

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QListWidgetItem, QStatusBar, QStyle, QTreeWidget, QTreeWidgetItem, QMenuBar, QRadioButton
)
from PyQt6.QtGui import QFont, QAction, QActionGroup
from PyQt6.QtCore import Qt, QSize, QSettings

# Impor dari modul lokal yang baru dibuat
import config
import utils
from core.ui_setup import UIBuilder
from core.data_manager import DataManager
from core.event_handlers import EventHandlers

class ContentManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Content Manager")
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon))
        
        # Inisialisasi properti
        self.base_path = config.BASE_PATH
        self.current_topic_path = None
        self.current_subject_path = None
        self.current_content = None
        self.sort_column = 1  # Default sort by Date
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.settings = QSettings("MyCompany", "ContentManager")
        self.date_filter = "all" # Opsi filter: "all" atau "today"

        # Inisialisasi modul-modul
        self.data_manager = DataManager(self.base_path)
        self.handlers = EventHandlers(self)
        self.ui_builder = UIBuilder(self)
        
        # Setup UI
        self._create_menu_bar()
        self.ui_builder.setup_ui()
        self.setStatusBar(QStatusBar())
        self.status_bar = self.statusBar()
        
        # Load data awal
        self.load_theme()
        self.refresh_topic_list()
        self.handlers.update_button_states()
        self.content_tree.header().setSortIndicator(self.sort_column, self.sort_order)

    def _create_menu_bar(self):
        menu_bar = self.menuBar()

        # --- Menu Tema ---
        theme_menu = menu_bar.addMenu("Mode")
        theme_group = QActionGroup(self)
        theme_group.setExclusive(True)

        light_action = QAction("Light", self, checkable=True)
        light_action.triggered.connect(lambda: self.set_theme("light"))
        theme_menu.addAction(light_action)
        theme_group.addAction(light_action)

        dark_action = QAction("Dark", self, checkable=True)
        dark_action.triggered.connect(lambda: self.set_theme("dark"))
        theme_menu.addAction(dark_action)
        theme_group.addAction(dark_action)

        system_action = QAction("System", self, checkable=True)
        system_action.triggered.connect(lambda: self.set_theme("system"))
        theme_menu.addAction(system_action)
        theme_group.addAction(system_action)
        
        current_theme = self.settings.value("theme", "system")
        if current_theme == "light": light_action.setChecked(True)
        elif current_theme == "dark": dark_action.setChecked(True)
        else: system_action.setChecked(True)

        # --- Menu Filter Tanggal ---
        filter_menu = menu_bar.addMenu("Filter")
        filter_group = QActionGroup(self)
        filter_group.setExclusive(True)

        all_action = QAction("Tampilkan Semua", self, checkable=True)
        all_action.triggered.connect(lambda: self.set_date_filter("all"))
        filter_menu.addAction(all_action)
        filter_group.addAction(all_action)

        today_action = QAction("Tampilkan Hari Ini", self, checkable=True)
        today_action.triggered.connect(lambda: self.set_date_filter("today"))
        filter_menu.addAction(today_action)
        filter_group.addAction(today_action)

        if self.date_filter == "all":
            all_action.setChecked(True)
        else:
            today_action.setChecked(True)

    def set_date_filter(self, filter_type):
        """Mengatur filter tanggal dan merefresh tampilan konten."""
        self.date_filter = filter_type
        self.refresh_content_tree()

    def set_theme(self, theme):
        self.settings.setValue("theme", theme)
        self.load_theme()

    def load_theme(self):
        theme = self.settings.value("theme", "system")
        if theme == "dark":
            self.setStyleSheet(config.DARK_STYLESHEET)
        elif theme == "light":
            self.setStyleSheet(config.LIGHT_STYLESHEET)
        else: # System
            if self.palette().window().color().lightness() < 128:
                 self.setStyleSheet(config.DARK_STYLESHEET)
            else:
                 self.setStyleSheet(config.LIGHT_STYLESHEET)

    # --- Metode untuk Refresh Tampilan ---
    def refresh_topic_list(self):
        self.topic_list.clear()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
        topics = self.data_manager.get_topics()
        for folder in topics:
            self.topic_list.addItem(QListWidgetItem(icon, folder))

    def refresh_subject_list(self):
        # Simpan teks item yang sedang dipilih untuk diseleksi ulang nanti
        current_item_text = None
        if self.subject_list.currentItem():
            current_item_text = self.subject_list.currentItem().text()

        # Blokir sinyal untuk mencegah 'subject_selected' terpanggil saat me-refresh list
        self.subject_list.blockSignals(True)
        
        self.subject_list.clear()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        subjects = self.data_manager.get_subjects(self.current_topic_path)
        item_to_reselect = None
        
        for name, date, code in subjects:
            display_text = name
            if date and code:
                display_text += f"\n({utils.format_date_with_day(date)} - {code})"
            
            item = QListWidgetItem(icon, display_text)
            self.subject_list.addItem(item)
            
            # Jika teksnya sama dengan yang dipilih sebelumnya, tandai untuk diseleksi ulang
            if display_text == current_item_text:
                item_to_reselect = item
        
        # Seleksi ulang item yang sebelumnya dipilih
        if item_to_reselect:
            self.subject_list.setCurrentItem(item_to_reselect)

        # Buka kembali blokir sinyal
        self.subject_list.blockSignals(False)

    def refresh_content_tree(self):
        # --- Simpan State ---
        expanded_indices = set()
        selected_item_data = None

        current_item = self.content_tree.currentItem()
        if current_item:
            selected_item_data = current_item.data(0, Qt.ItemDataRole.UserRole)

        if self.content_tree.topLevelItemCount() > 0:
            for i in range(self.content_tree.topLevelItemCount()):
                item = self.content_tree.topLevelItem(i)
                if item.isExpanded():
                    item_data = item.data(0, Qt.ItemDataRole.UserRole)
                    if item_data and item_data.get("type") == "discussion":
                        expanded_indices.add(item_data.get("index"))
        
        # --- Proses Refresh ---
        self.content_tree.clear()
        if not self.current_subject_path: return
        
        self.current_content = self.data_manager.load_content(self.current_subject_path)
        discussions = self.current_content.get("content", [])
        
        # --- Logika Filter Tanggal ---
        today_str = datetime.now().strftime("%Y-%m-%d")
        filtered_discussions = []
        if self.date_filter == "today":
            for index, disc_data in enumerate(discussions):
                original_discussion = {"data": disc_data, "original_index": index}
                
                # Cek tanggal diskusi utama
                if disc_data.get("date") == today_str and not disc_data.get("points"):
                    filtered_discussions.append(original_discussion)
                    continue

                # Cek tanggal pada points
                matching_points = [p for p in disc_data.get("points", []) if p.get("date") == today_str]
                if matching_points:
                    # Buat salinan diskusi hanya dengan point yang cocok
                    new_disc_data = disc_data.copy()
                    new_disc_data["points"] = matching_points
                    filtered_discussions.append({"data": new_disc_data, "original_index": index})
        else: # "all"
            filtered_discussions = [{"data": data, "original_index": index} for index, data in enumerate(discussions)]

        indexed_discussions = [(item["original_index"], item["data"]) for item in filtered_discussions]

        def get_sort_key(indexed_item):
            _, item_data = indexed_item
            if self.sort_column == 0: return item_data.get("discussion", "").lower()
            elif self.sort_column == 1:
                date_str = item_data.get("date")
                if not date_str:
                    point_dates = [p.get("date") for p in item_data.get("points", []) if p.get("date")]
                    date_str = min(point_dates) if point_dates else "9999-12-31"
                try: return datetime.strptime(date_str, "%Y-%m-%d")
                except (ValueError, TypeError): return datetime.max
            elif self.sort_column == 2: return item_data.get("repetition_code", "Z")
            return ""

        is_reverse = (self.sort_order == Qt.SortOrder.DescendingOrder)
        sorted_indexed_discussions = sorted(indexed_discussions, key=get_sort_key, reverse=is_reverse)
        
        item_to_reselect = None

        for original_index, discussion_data in sorted_indexed_discussions:
            parent_item = QTreeWidgetItem(self.content_tree)
            parent_item.setText(0, discussion_data.get("discussion", "Diskusi kosong"))
            item_data_for_crud = {"type": "discussion", "index": original_index}
            parent_item.setData(0, Qt.ItemDataRole.UserRole, item_data_for_crud)
            
            if not discussion_data.get("points", []):
                parent_item.setText(1, utils.format_date_with_day(discussion_data.get("date", "")))
                self.handlers.create_repetition_combobox(parent_item, 2, discussion_data.get("repetition_code", "R0D"), item_data_for_crud)
            else:
                point_dates = [p.get("date") for p in discussion_data.get("points", []) if p.get("date")]
                if point_dates: parent_item.setText(1, f"({utils.format_date_with_day(min(point_dates))})")

            if selected_item_data == item_data_for_crud:
                item_to_reselect = parent_item

            for j, point_data in enumerate(discussion_data.get("points", [])):
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, point_data.get("point_text", "Point kosong"))
                child_item.setText(1, utils.format_date_with_day(point_data.get("date", "")))
                
                # Cari index asli dari point
                original_point_index = -1
                original_points = self.current_content["content"][original_index].get("points", [])
                for idx, orig_point in enumerate(original_points):
                    if orig_point == point_data:
                        original_point_index = idx
                        break

                item_data = {"type": "point", "parent_index": original_index, "index": original_point_index}
                child_item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                self.handlers.create_repetition_combobox(child_item, 2, point_data.get("repetition_code", "R0D"), item_data)
                
                if selected_item_data == item_data:
                    item_to_reselect = child_item
            
            if original_index in expanded_indices:
                parent_item.setExpanded(True)
        
        if item_to_reselect:
            self.content_tree.setCurrentItem(item_to_reselect)
            
        self.handlers.update_button_states()


    def save_and_refresh_content(self):
        """Menyimpan konten saat ini dan merefresh tampilan."""
        self.handlers.update_earliest_date_in_metadata()
        self.data_manager.save_content(self.current_subject_path, self.current_content)
        self.refresh_content_tree()
        self.refresh_subject_list()