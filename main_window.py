# file: test/main_window.py

import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QMainWindow, QListWidgetItem, QStatusBar, QTreeWidgetItem, QFileDialog, QSplitter, QTreeWidgetItemIterator, QMessageBox
)
from PyQt6.QtGui import QFont, QAction, QActionGroup, QIcon
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

        self.setWindowIcon(QIcon('images/icons/bird_2.png'))
        
        # Inisialisasi properti
        self.base_path = config.BASE_PATH
        # TASK_BASE_PATH sekarang adalah file, bukan direktori
        self.task_data_file = config.TASK_BASE_PATH 
        self.current_topic_path = None
        self.current_subject_path = None
        self.current_content = None
        self.current_task_category = None 
        self.sort_column = 1
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.settings = QSettings("MyCompany", "ContentManager")
        self.date_filter = "all"
        self.scale_config = {} 

        # Inisialisasi modul-modul
        # DataManager sekarang hanya butuh base_path untuk topics
        self.data_manager = DataManager(self.base_path)
        self.handlers = EventHandlers(self)
        self.ui_builder = UIBuilder(self)
        
        # Setup UI
        self.ui_builder.setup_ui()
        self._create_menu_bar()
        self.setStatusBar(QStatusBar())
        self.status_bar = self.statusBar()
        
        # Load data dan preferensi awal
        self.load_theme()
        self.load_scale() 
        self.refresh_topic_list()
        self.refresh_task_category_list() 
        self.handlers.update_button_states()
        self.content_tree.header().setSortIndicator(self.sort_column, self.sort_order)
        
        # BARU: Memuat status terakhir
        self.load_state()

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
        
        # --- Menu Skala ---
        scale_menu = menu_bar.addMenu("Skala")
        self.scale_group = QActionGroup(self)
        self.scale_group.setExclusive(True)

        for scale_name in config.UI_SCALE_CONFIG.keys():
            action = QAction(scale_name, self, checkable=True)
            action.triggered.connect(lambda checked, name=scale_name: self.set_scale(name))
            scale_menu.addAction(action)
            self.scale_group.addAction(action)

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

        # --- Menu Backup ---
        backup_menu = menu_bar.addMenu("Backup")
        
        backup_action = QAction("Buat Cadangan...", self)
        backup_action.triggered.connect(self.handlers.backup_all_topics)
        backup_menu.addAction(backup_action)
        
        import_action = QAction("Impor Cadangan...", self)
        import_action.triggered.connect(self.handlers.import_backup)
        backup_menu.addAction(import_action)

        # --- Menu Bantuan (About) ---
        help_menu = menu_bar.addMenu("Bantuan")
        about_action = QAction("Tentang Aplikasi", self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        """Menampilkan dialog 'About' dengan informasi aplikasi."""
        about_text = """
        <b>Content Manager v1.0</b>
        <p>Aplikasi ini dibuat oleh:</p>
        <p><b>Frendy Rikal Gerung S.Kom</b></p>
        <p>
        Lulusan Universitas Negeri Manado, Fakultas Teknik,
        Program Studi Teknik Informatika.
        </p>
        <p>
        Berasal dari desa Raanan Baru. Saya sangat menyukai belajar, 
        coding, serta hal-hal menarik lainnya.
        </p>
        <p>Terima kasih telah menggunakan aplikasi ini!</p>
        """
        QMessageBox.about(self, "Tentang Content Manager", about_text)


    def set_date_filter(self, filter_type):
        """Mengatur filter tanggal dan merefresh tampilan konten."""
        self.date_filter = filter_type
        self.refresh_content_tree()

    def set_theme(self, theme):
        self.settings.setValue("theme", theme)
        self.load_theme()

    def load_theme(self):
        theme = self.settings.value("theme", "system")
        stylesheet = ""
        if theme == "dark":
            stylesheet = config.DARK_STYLESHEET
        elif theme == "light":
            stylesheet = config.LIGHT_STYLESHEET
        else: # System
            if self.palette().window().color().lightness() < 128:
                 stylesheet = config.DARK_STYLESHEET
            else:
                 stylesheet = config.LIGHT_STYLESHEET
        self.setStyleSheet(stylesheet)
    
    # --- Metode untuk Skala UI ---
    def set_scale(self, scale_name):
        """Menyimpan dan menerapkan skala UI yang dipilih."""
        self.settings.setValue("ui_scale", scale_name)
        self.load_scale()

    def load_scale(self):
        """Memuat konfigurasi skala dari pengaturan dan menerapkannya."""
        scale_name = self.settings.value("ui_scale", config.DEFAULT_SCALE)
        self.scale_config = config.UI_SCALE_CONFIG[scale_name]
        
        # Update tanda centang di menu
        for action in self.scale_group.actions():
            if action.text() == scale_name:
                action.setChecked(True)
                break
        
        self.apply_scaling()

    def apply_scaling(self):
        """Menerapkan ukuran font dan ikon ke seluruh widget."""
        if not self.scale_config:
            return

        # Ambil ukuran dari config
        list_font_size = self.scale_config['list_font_size']
        title_font_size = self.scale_config['title_font_size']
        icon_size = self.scale_config['icon_size']

        # Siapkan objek Font dan Size
        list_font = QFont("Segoe UI", list_font_size)
        title_font = QFont("Segoe UI", title_font_size, QFont.Weight.Bold)
        q_icon_size = QSize(icon_size, icon_size)

        # Terapkan ke label judul
        self.topic_title_label.setFont(title_font)
        self.subject_title_label.setFont(title_font)
        self.content_title_label.setFont(title_font)
        self.task_category_title_label.setFont(title_font)
        self.task_title_label.setFont(title_font)

        # Terapkan ke widget list dan tree
        self.topic_list.setFont(list_font)
        self.topic_list.setIconSize(q_icon_size)
        self.subject_list.setFont(list_font)
        self.subject_list.setIconSize(q_icon_size)
        self.content_tree.setFont(list_font)
        self.task_category_list.setFont(list_font) 
        self.task_category_list.setIconSize(q_icon_size) 
        self.task_tree.setFont(list_font)


        # Refresh tampilan untuk memastikan ukuran diterapkan dengan benar
        self.refresh_topic_list()
        self.refresh_subject_list()
        self.refresh_content_tree()
        self.refresh_task_category_list()
        self.refresh_task_list()

    # --- Metode untuk Refresh Tampilan ---
    def refresh_topic_list(self):
        self.topic_list.clear()
        topics = self.data_manager.get_topics()
        for topic_data in topics:
            item = QListWidgetItem(f"{topic_data['icon']} {topic_data['name']}")
            self.topic_list.addItem(item)

    def refresh_subject_list(self):
        current_item_text = None
        if self.subject_list.currentItem():
            current_item_text = self.subject_list.currentItem().text()

        self.subject_list.blockSignals(True)
        
        self.subject_list.clear()
        subjects = self.data_manager.get_subjects(self.current_topic_path)
        item_to_reselect = None
        
        for name, date, code, icon in subjects:
            display_text = f"{icon} {name}"
            if date and code:
                display_text += f"\n  ({utils.format_date_with_day(date)} - {code})"
            
            item = QListWidgetItem(display_text)
            self.subject_list.addItem(item)
            
            if display_text == current_item_text:
                item_to_reselect = item
        
        if item_to_reselect:
            self.subject_list.setCurrentItem(item_to_reselect)

        self.subject_list.blockSignals(False)

    def refresh_content_tree(self):
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
        
        self.content_tree.clear()
        if not self.current_subject_path: return
        
        self.current_content = self.data_manager.load_content(self.current_subject_path)
        discussions = self.current_content.get("content", [])
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        filtered_discussions = []
        if self.date_filter == "today":
            for index, disc_data in enumerate(discussions):
                original_discussion = {"data": disc_data, "original_index": index}
                
                if disc_data.get("date") == today_str and not disc_data.get("points"):
                    filtered_discussions.append(original_discussion)
                    continue

                matching_points = [p for p in disc_data.get("points", []) if p.get("date") == today_str]
                if matching_points:
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

    # --- BARU: Metode untuk Refresh Tampilan Task ---
    def refresh_task_category_list(self):
        """Merefresh daftar kategori task."""
        current_item_text = None
        if self.task_category_list.currentItem():
            current_item_text = self.task_category_list.currentItem().text()

        self.task_category_list.blockSignals(True)
        self.task_category_list.clear()

        # Tambahkan item "Semua Task" secara manual
        self.task_category_list.addItem("Semua Task")

        categories = self.data_manager.get_task_categories()
        item_to_reselect = None
        for cat_data in categories:
            display_text = f"{cat_data['icon']} {cat_data['name']}"
            item = QListWidgetItem(display_text)
            self.task_category_list.addItem(item)
            if display_text == current_item_text:
                item_to_reselect = item

        if item_to_reselect:
            self.task_category_list.setCurrentItem(item_to_reselect)
        else:
            self.task_category_list.setCurrentRow(0) # Default ke "Semua Task"

        self.task_category_list.blockSignals(False)
        # Panggil handler secara manual untuk memuat task
        if self.task_category_list.currentItem():
             self.handlers.task_category_selected(self.task_category_list.currentItem(), None)


    def refresh_task_list(self):
        """Merefresh daftar task berdasarkan kategori yang dipilih."""
        self.task_tree.clear()
        
        if not self.current_task_category:
            self.handlers.update_button_states()
            return
            
        if self.current_task_category == "Semua Task":
            tasks = self.data_manager.get_all_tasks()
        else:
            tasks = self.data_manager.get_tasks(self.current_task_category)
            
        for task_data in tasks:
            item = QTreeWidgetItem(self.task_tree)
            item.setText(0, task_data['name'])
            item.setText(1, str(task_data['count']))
            item.setText(2, task_data.get('date', ''))

            # Simpan info asli (nama dan kategori) di item untuk referensi nanti
            # Ini penting untuk operasi edit/delete dari tampilan "Semua Task"
            if self.current_task_category == "Semua Task":
                item.setData(0, Qt.ItemDataRole.UserRole, {
                    "original_name": task_data.get("original_name"),
                    "category": task_data.get("category")
                })
            else:
                item.setData(0, Qt.ItemDataRole.UserRole, {
                    "original_name": task_data.get("name"),
                    "category": self.current_task_category
                })
        self.handlers.update_button_states()
        
    def reselect_task(self, task_name_to_select, category_name_to_select):
        """Memilih kembali item task setelah operasi seperti penambahan hitungan."""
        for i in range(self.task_tree.topLevelItemCount()):
            item = self.task_tree.topLevelItem(i)
            task_info = item.data(0, Qt.ItemDataRole.UserRole)
            if (task_info.get("original_name") == task_name_to_select and 
                task_info.get("category") == category_name_to_select):
                self.task_tree.setCurrentItem(item)
                break

    # --- BARU: Metode untuk menyimpan dan memuat status ---
    def save_state(self):
        """Menyimpan item yang dipilih terakhir di setiap panel."""
        # Topik
        topic_item = self.topic_list.currentItem()
        if topic_item:
            self.settings.setValue("last_selected_topic", topic_item.text())

        # Subjek
        subject_item = self.subject_list.currentItem()
        if subject_item:
            self.settings.setValue("last_selected_subject", subject_item.text())

        # Konten (Diskusi/Point)
        content_item = self.content_tree.currentItem()
        if content_item:
            data = content_item.data(0, Qt.ItemDataRole.UserRole)
            self.settings.setValue("last_selected_content", data)
        
        # Kategori Task
        task_category_item = self.task_category_list.currentItem()
        if task_category_item:
            self.settings.setValue("last_selected_task_category", task_category_item.text())
        
        # Task
        task_item = self.task_tree.currentItem()
        if task_item:
            data = task_item.data(0, Qt.ItemDataRole.UserRole)
            self.settings.setValue("last_selected_task", data)

    def load_state(self):
        """Memuat dan memilih item terakhir yang disimpan."""
        # Pilih Kategori Task
        last_category = self.settings.value("last_selected_task_category")
        if last_category:
            for i in range(self.task_category_list.count()):
                if self.task_category_list.item(i).text() == last_category:
                    self.task_category_list.setCurrentRow(i)
                    break
        
        # Pilih Task
        last_task_data = self.settings.value("last_selected_task")
        if last_task_data:
            # Refresh diperlukan agar item-itemnya ada
            self.refresh_task_list() 
            for i in range(self.task_tree.topLevelItemCount()):
                item = self.task_tree.topLevelItem(i)
                if item.data(0, Qt.ItemDataRole.UserRole) == last_task_data:
                    self.task_tree.setCurrentItem(item)
                    break

        # Pilih Topik
        last_topic = self.settings.value("last_selected_topic")
        if last_topic:
            for i in range(self.topic_list.count()):
                if self.topic_list.item(i).text() == last_topic:
                    self.topic_list.setCurrentRow(i)
                    break # Berhenti setelah ditemukan
        
        # Pilih Subjek
        last_subject = self.settings.value("last_selected_subject")
        if self.current_topic_path and last_subject:
             # Refresh diperlukan agar item-itemnya ada
            self.refresh_subject_list()
            for i in range(self.subject_list.count()):
                if self.subject_list.item(i).text() == last_subject:
                    self.subject_list.setCurrentRow(i)
                    break
        
        # Pilih Konten
        last_content_data = self.settings.value("last_selected_content")
        if self.current_subject_path and last_content_data:
            # Refresh diperlukan agar item-itemnya ada
            self.refresh_content_tree() 
            iterator = QTreeWidgetItemIterator(self.content_tree)
            while iterator.value():
                item = iterator.value()
                if item.data(0, Qt.ItemDataRole.UserRole) == last_content_data:
                    self.content_tree.setCurrentItem(item)
                    break
                iterator += 1

    def closeEvent(self, event):
        """Dipanggil saat jendela ditutup."""
        self.save_state()
        event.accept()