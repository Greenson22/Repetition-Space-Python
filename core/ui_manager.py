# file: test/core/ui_manager.py

from PyQt6.QtWidgets import QMessageBox, QPushButton
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
import config
import json
from utils import resource_path

class UIManager:
    """Kelas untuk mengelola elemen UI seperti menu, tema, dan skala."""
    def __init__(self, main_window):
        self.win = main_window
        self.settings = main_window.settings

    def create_menu_bar(self):
        """Membuat dan menginisialisasi menu bar."""
        menu_bar = self.win.menuBar()

        # --- Menu Tema ---
        theme_menu = menu_bar.addMenu("Mode")
        theme_group = QActionGroup(self.win)
        theme_group.setExclusive(True)

        actions = {
            "Light": "light",
            "Dark": "dark",
            "Nordic Twilight": "nordic_twilight",
            "System": "system"
        }

        current_theme = self.settings.value("theme", "system")
        for text, theme_id in actions.items():
            action = QAction(text, self.win, checkable=True)
            action.triggered.connect(lambda checked, t=theme_id: self.set_theme(t))
            theme_menu.addAction(action)
            theme_group.addAction(action)
            if theme_id == current_theme:
                action.setChecked(True)

        # --- Menu Skala ---
        scale_menu = menu_bar.addMenu("Skala")
        self.win.scale_group = QActionGroup(self.win)
        self.win.scale_group.setExclusive(True)

        for scale_name in config.UI_SCALE_CONFIG.keys():
            action = QAction(scale_name, self.win, checkable=True)
            action.triggered.connect(lambda checked, name=scale_name: self.set_scale(name))
            scale_menu.addAction(action)
            self.win.scale_group.addAction(action)

        # --- Menu Filter Tanggal ---
        filter_menu = menu_bar.addMenu("Filter")
        filter_group = QActionGroup(self.win)
        filter_group.setExclusive(True)

        filter_actions = {
            "Tampilkan Semua": "all",
            "Tampilkan Hari Ini": "today",
            "Tampilkan Hingga Hari Ini": "past_and_today"
        }
        
        current_filter = self.settings.value("date_filter", "all")
        self.win.date_filter = current_filter
        for text, filter_id in filter_actions.items():
            action = QAction(text, self.win, checkable=True)
            action.triggered.connect(lambda checked, f=filter_id: self.set_date_filter(f))
            filter_menu.addAction(action)
            filter_group.addAction(action)
            if filter_id == current_filter:
                action.setChecked(True)

        # --- Menu Backup ---
        backup_menu = menu_bar.addMenu("Backup")
        backup_action = QAction("Buat Cadangan...", self.win)
        backup_action.triggered.connect(self.win.handlers.backup_all_topics)
        backup_menu.addAction(backup_action)
        
        import_action = QAction("Impor Cadangan...", self.win)
        import_action.triggered.connect(self.win.handlers.import_backup)
        backup_menu.addAction(import_action)

        # --- Menu Bantuan (About) ---
        help_menu = menu_bar.addMenu("Bantuan")
        about_action = QAction("Tentang Aplikasi", self.win)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def show_about_dialog(self):
        """Menampilkan dialog 'About' dengan informasi aplikasi dan tombol riwayat versi."""
        about_text = """
        <b>Repetition App Alpha v1.1</b>
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
        msg_box = QMessageBox(self.win)
        msg_box.setWindowTitle("Tentang Repetition App")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        
        # Tambahkan tombol custom untuk riwayat versi
        history_button = QPushButton("Riwayat Versi")
        msg_box.addButton(history_button, QMessageBox.ButtonRole.ActionRole)
        
        # Tambahkan tombol OK standar
        msg_box.addButton(QMessageBox.StandardButton.Ok)

        # Hubungkan tombol riwayat versi ke fungsinya
        history_button.clicked.connect(self.show_version_history_dialog)
        
        msg_box.exec()

    def show_version_history_dialog(self):
        """Menampilkan dialog dengan riwayat versi aplikasi dari file JSON."""
        try:
            with open(resource_path('assets/version_history.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            html_output = "<h3>Riwayat Versi</h3>"
            for entry in data['versions']:
                html_output += f"<p><b>{entry['version']} ({entry['date']})</b></p>"
                html_output += "<ul>"
                for change in entry['changes']:
                    html_output += f"<li>{change}</li>"
                html_output += "</ul>"
            
            QMessageBox.about(self.win, "Riwayat Versi", html_output)

        except FileNotFoundError:
            QMessageBox.critical(self.win, "Error", "File riwayat versi tidak ditemukan.")
        except json.JSONDecodeError:
            QMessageBox.critical(self.win, "Error", "Format file riwayat versi (JSON) tidak valid.")

    def set_date_filter(self, filter_type):
        """Mengatur filter tanggal dan merefresh tampilan konten."""
        self.win.date_filter = filter_type
        self.settings.setValue("date_filter", filter_type)
        self.win.refresh_manager.refresh_content_tree()

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
        elif theme == "nordic_twilight":
            stylesheet = config.NORDIC_TWILIGHT_STYLESHEET
        else: # System
            if self.win.palette().window().color().lightness() < 128:
                 stylesheet = config.DARK_STYLESHEET
            else:
                 stylesheet = config.LIGHT_STYLESHEET
        self.win.setStyleSheet(stylesheet)
    
    def set_scale(self, scale_name):
        """Menyimpan dan menerapkan skala UI yang dipilih."""
        self.settings.setValue("ui_scale", scale_name)
        self.load_scale()

    def load_scale(self):
        """Memuat konfigurasi skala dari pengaturan dan menerapkannya."""
        scale_name = self.settings.value("ui_scale", config.DEFAULT_SCALE)
        self.win.scale_config = config.UI_SCALE_CONFIG[scale_name]
        
        for action in self.win.scale_group.actions():
            if action.text() == scale_name:
                action.setChecked(True)
                break
        
        self.apply_scaling()

    def apply_scaling(self):
        """Menerapkan ukuran font dan ikon ke seluruh widget."""
        if not self.win.scale_config:
            return

        list_font_size = self.win.scale_config['list_font_size']
        title_font_size = self.win.scale_config['title_font_size']
        icon_size = self.win.scale_config['icon_size']

        list_font = QFont("Segoe UI", list_font_size)
        title_font = QFont("Segoe UI", title_font_size, QFont.Weight.Bold)
        q_icon_size = QSize(icon_size, icon_size)

        self.win.topic_title_label.setFont(title_font)
        self.win.subject_title_label.setFont(title_font)
        self.win.content_title_label.setFont(title_font)
        self.win.task_category_title_label.setFont(title_font)
        self.win.task_title_label.setFont(title_font)

        self.win.topic_list.setFont(list_font)
        self.win.topic_list.setIconSize(q_icon_size)
        self.win.subject_list.setFont(list_font)
        self.win.subject_list.setIconSize(q_icon_size)
        self.win.content_tree.setFont(list_font)
        self.win.task_category_list.setFont(list_font) 
        self.win.task_category_list.setIconSize(q_icon_size) 
        self.win.task_tree.setFont(list_font)

        self.win.refresh_manager.refresh_all_views()