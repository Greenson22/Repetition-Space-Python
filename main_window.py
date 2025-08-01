# file: test/main_window.py

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QListWidgetItem, QStatusBar, QStyle, QTreeWidget, QTreeWidgetItem, QMenuBar
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
        if current_theme == "light":
            light_action.setChecked(True)
        elif current_theme == "dark":
            dark_action.setChecked(True)
        else:
            system_action.setChecked(True)

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
        self.subject_list.clear()
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)
        subjects = self.data_manager.get_subjects(self.current_topic_path)
        for name, date, code in subjects:
            display_text = name
            if date and code:
                display_text += f"\n({utils.format_date_with_day(date)} - {code})"
            item = QListWidgetItem(icon, display_text)
            self.subject_list.addItem(item)


    def refresh_content_tree(self):
        self.content_tree.clear()
        if not self.current_subject_path: return
        
        self.current_content = self.data_manager.load_content(self.current_subject_path)
        discussions = self.current_content.get("content", [])
        indexed_discussions = list(enumerate(discussions))

        # Logika pengurutan
        def get_sort_key(indexed_item):
            _, item_data = indexed_item
            if self.sort_column == 0:  # Sort by Content
                return item_data.get("discussion", "").lower()
            elif self.sort_column == 1:  # Sort by Date
                date_str = item_data.get("date")
                if not date_str:
                    point_dates = [p.get("date") for p in item_data.get("points", []) if p.get("date")]
                    date_str = min(point_dates) if point_dates else "9999-12-31"
                try:
                    return datetime.strptime(date_str, "%Y-%m-%d")
                except ValueError:
                    return datetime.max
            elif self.sort_column == 2:  # Sort by Code
                return item_data.get("repetition_code", "Z")
            return ""

        is_reverse = (self.sort_order == Qt.SortOrder.DescendingOrder)
        sorted_indexed_discussions = sorted(indexed_discussions, key=get_sort_key, reverse=is_reverse)
        
        # Populasi tree widget
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
                if point_dates:
                    parent_item.setText(1, f"({utils.format_date_with_day(min(point_dates))})")

            for j, point_data in enumerate(discussion_data.get("points", [])):
                child_item = QTreeWidgetItem(parent_item)
                child_item.setText(0, point_data.get("point_text", "Point kosong"))
                child_item.setText(1, utils.format_date_with_day(point_data.get("date", "")))
                item_data = {"type": "point", "parent_index": original_index, "index": j}
                child_item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                self.handlers.create_repetition_combobox(child_item, 2, point_data.get("repetition_code", "R0D"), item_data)
                
        self.content_tree.expandAll()
        self.handlers.update_button_states()

    def save_and_refresh_content(self):
        """Menyimpan konten saat ini dan merefresh tampilan."""
        self.data_manager.save_content(self.current_subject_path, self.current_content)
        self.refresh_content_tree()