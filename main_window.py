# file: test/main_window.py

from PyQt6.QtWidgets import QMainWindow, QStatusBar
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSettings

import config
from core.ui_setup import UIBuilder
from core.data_manager import DataManager
from core.event_handlers import EventHandlers
from core.ui_manager import UIManager
from core.state_manager import StateManager
from core.refresh_manager import RefreshManager

class ContentManager(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Content Manager")
        self.setGeometry(100, 100, 1200, 650)
        self.setWindowIcon(QIcon('images/icons/bird_2.png'))
        
        # --- Inisialisasi Properti Inti ---
        self.base_path = config.BASE_PATH
        self.task_data_file = config.TASK_BASE_PATH 
        self.current_topic_path = None
        self.current_subject_path = None
        self.current_content = None
        self.current_task_category = None 
        self.sort_column = 1
        self.sort_order = Qt.SortOrder.AscendingOrder
        self.settings = QSettings("MyCompany", "ContentManager")
        self.date_filter = "all"
        self.search_query = ""
        self.scale_config = {} 
        self.Qt = Qt # Memberikan akses ke namespace Qt untuk manajer

        # --- Inisialisasi Modul-Modul Helper ---
        self.data_manager = DataManager(self.base_path)
        self.handlers = EventHandlers(self)
        self.ui_builder = UIBuilder(self)
        self.ui_manager = UIManager(self)
        self.state_manager = StateManager(self)
        self.refresh_manager = RefreshManager(self)
        
        # --- Setup UI ---
        self.ui_builder.setup_ui()
        self.ui_manager.create_menu_bar()
        self.setStatusBar(QStatusBar())
        self.status_bar = self.statusBar()
        
        # --- Load Data dan Preferensi Awal ---
        self.ui_manager.load_theme()
        self.ui_manager.load_scale() 
        self.refresh_manager.refresh_topic_list()
        self.refresh_manager.refresh_task_category_list() 
        self.handlers.update_button_states()
        self.content_tree.header().setSortIndicator(self.sort_column, self.sort_order)
        
        # --- Memuat Status Terakhir ---
        self.state_manager.load_state()

    def closeEvent(self, event):
        """Dipanggil saat jendela ditutup."""
        self.state_manager.save_state()
        event.accept()