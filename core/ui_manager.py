# file: test/core/ui_manager.py

import os
import shutil
from PyQt6.QtWidgets import (QMessageBox, QPushButton, QFileDialog, QMenu,
                             QDialog, QVBoxLayout, QListWidget, QListWidgetItem,
                             QHBoxLayout, QAbstractItemView, QTextBrowser, QDialogButtonBox)
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
import config
import json
from utils import resource_path

class UIManager:
    """Kelas untuk mengelola elemen UI seperti menu, tema, dan skala."""
    THEMES_DIR = os.path.join("data", "themes")

    def __init__(self, main_window):
        self.win = main_window
        self.settings = main_window.settings
        self.theme_menu = None

    def create_menu_bar(self):
        """Membuat dan menginisialisasi menu bar."""
        menu_bar = self.win.menuBar()
        self.setup_theme_menu(menu_bar)

        scale_menu = menu_bar.addMenu("Skala")
        self.win.scale_group = QActionGroup(self.win)
        self.win.scale_group.setExclusive(True)
        for scale_name in config.UI_SCALE_CONFIG.keys():
            action = QAction(scale_name, self.win, checkable=True)
            action.triggered.connect(lambda checked, name=scale_name: self.set_scale(name))
            scale_menu.addAction(action)
            self.win.scale_group.addAction(action)

        # --- FITUR BARU: Menu Format Tanggal ---
        date_format_menu = menu_bar.addMenu("Format Tanggal")
        self.win.date_format_group = QActionGroup(self.win)
        self.win.date_format_group.setExclusive(True)
        date_format_actions = {
            "Panjang (Sabtu, 02 Agustus 2025)": "long",
            "Sedang (02 Agu 2025)": "medium",
            "Pendek (2025-08-02)": "short",
            "Tidak ada Tahun (08-02)": "no_year"
        }
        current_format = self.settings.value("date_format", "long")
        for text, format_id in date_format_actions.items():
            action = QAction(text, self.win, checkable=True)
            action.triggered.connect(lambda checked, f=format_id: self.set_date_format(f))
            date_format_menu.addAction(action)
            self.win.date_format_group.addAction(action)
            if format_id == current_format:
                action.setChecked(True)
        # --- AKHIR FITUR BARU ---

        filter_menu = menu_bar.addMenu("Filter")
        filter_group = QActionGroup(self.win)
        filter_group.setExclusive(True)
        filter_actions = {
            "Tampilkan Semua": "all", "Tampilkan Hari Ini": "today",
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

        backup_menu = menu_bar.addMenu("Backup")
        backup_action = QAction("Buat Cadangan...", self.win)
        backup_action.triggered.connect(self.win.handlers.backup_all_topics)
        backup_menu.addAction(backup_action)
        import_action = QAction("Impor Cadangan...", self.win)
        import_action.triggered.connect(self.win.handlers.import_backup)
        backup_menu.addAction(import_action)

        help_menu = menu_bar.addMenu("Bantuan")
        about_action = QAction("Tentang Aplikasi", self.win)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def set_date_format(self, format_type):
        """Menyimpan format tanggal dan merefresh semua tampilan."""
        self.settings.setValue("date_format", format_type)
        self.win.refresh_manager.refresh_all_views()

    def setup_theme_menu(self, menu_bar):
        """Menginisialisasi menu tema dan mengisinya."""
        self.theme_menu = menu_bar.addMenu("Mode")
        self.win.theme_group = QActionGroup(self.win)
        self.win.theme_group.setExclusive(True)
        self.populate_theme_menu()

    def populate_theme_menu(self):
        """Membangun kembali menu tema dengan tema bawaan, kustom, dan opsi manajemen."""
        self.theme_menu.clear()
        for action in self.win.theme_group.actions():
            self.win.theme_group.removeAction(action)

        current_theme = self.settings.value("theme", "system")

        actions = {
            "Light": "light", "Dark": "dark",
            "Nordic Twilight": "nordic_twilight", "System": "system"
        }
        for text, theme_id in actions.items():
            action = QAction(text, self.win, checkable=True)
            action.triggered.connect(lambda checked, t=theme_id: self.set_theme(t))
            self.theme_menu.addAction(action)
            self.win.theme_group.addAction(action)
            if theme_id == current_theme:
                action.setChecked(True)

        self.theme_menu.addSeparator()

        os.makedirs(self.THEMES_DIR, exist_ok=True)
        custom_themes = [f for f in os.listdir(self.THEMES_DIR) if f.endswith(".qss")]

        if custom_themes:
            custom_menu = self.theme_menu.addMenu("Tema Kustom")
            for theme_file in sorted(custom_themes):
                theme_path = os.path.join(self.THEMES_DIR, theme_file)
                theme_name = os.path.splitext(theme_file)[0].replace("_", " ").title()

                action = QAction(theme_name, self.win, checkable=True)
                action.triggered.connect(lambda checked, p=theme_path: self.set_theme(p))
                custom_menu.addAction(action)
                self.win.theme_group.addAction(action)
                if theme_path == current_theme:
                    action.setChecked(True)

            custom_menu.addSeparator()
            manage_action = QAction("Kelola Tema...", self.win)
            manage_action.triggered.connect(self.show_manage_themes_dialog)
            custom_menu.addAction(manage_action)

        self.theme_menu.addSeparator()
        import_action = QAction("Impor Tema...", self.win)
        import_action.triggered.connect(self.import_theme)
        self.theme_menu.addAction(import_action)

    def import_theme(self):
        """Membuka dialog, menyalin tema, dan menerapkannya."""
        file_name, _ = QFileDialog.getOpenFileName(
            self.win, "Impor Tema Kustom", "", "Qt Stylesheet Files (*.qss)")
        if file_name:
            try:
                os.makedirs(self.THEMES_DIR, exist_ok=True)
                new_theme_path = os.path.join(self.THEMES_DIR, os.path.basename(file_name))
                shutil.copy(file_name, new_theme_path)
                self.populate_theme_menu()
                self.set_theme(new_theme_path)
            except Exception as e:
                QMessageBox.critical(self.win, "Gagal Impor Tema", f"Error: {e}")

    def show_manage_themes_dialog(self):
        """Menampilkan dialog untuk menghapus tema kustom."""
        dialog = QDialog(self.win)
        dialog.setWindowTitle("Kelola Tema Kustom")
        layout = QVBoxLayout(dialog)

        list_widget = QListWidget()
        list_widget.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        custom_themes = [f for f in os.listdir(self.THEMES_DIR) if f.endswith(".qss")]
        for theme_file in sorted(custom_themes):
            list_widget.addItem(QListWidgetItem(theme_file))

        layout.addWidget(list_widget)

        button_layout = QHBoxLayout()
        delete_button = QPushButton("Hapus yang Dipilih")
        delete_button.clicked.connect(lambda: self.delete_selected_themes(list_widget, dialog))

        button_layout.addWidget(delete_button)
        layout.addLayout(button_layout)
        dialog.exec()

    def delete_selected_themes(self, list_widget, dialog):
        """Menghapus tema yang dipilih dari daftar dan file sistem."""
        selected_items = list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(dialog, "Tidak Ada Pilihan", "Pilih tema yang ingin dihapus.")
            return

        reply = QMessageBox.question(
            dialog, "Konfirmasi Hapus",
            f"Anda yakin ingin menghapus {len(selected_items)} tema terpilih?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            current_theme = self.settings.value("theme", "system")
            theme_was_deleted = False

            for item in selected_items:
                theme_file = item.text()
                theme_path = os.path.join(self.THEMES_DIR, theme_file)
                try:
                    os.remove(theme_path)
                    if theme_path == current_theme:
                        theme_was_deleted = True
                except OSError as e:
                    QMessageBox.critical(dialog, "Error", f"Gagal menghapus {theme_file}: {e}")

            if theme_was_deleted:
                self.set_theme("system") # Kembali ke tema default

            self.populate_theme_menu()
            dialog.close()

    def show_about_dialog(self):
        """Menampilkan dialog 'About'."""
        about_text = """
        <b>Repetition App Alpha v1.1</b>
        <p>Dibuat oleh: <b>Frendy Rikal Gerung S.Kom</b></p>
        <p>Lulusan Universitas Negeri Manado, Fakultas Teknik, Informatika.</p>
        <p>Terima kasih telah menggunakan aplikasi ini!</p>
        """
        msg_box = QMessageBox(self.win)
        msg_box.setWindowTitle("Tentang Repetition App")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(about_text)
        history_button = QPushButton("Riwayat Versi")
        msg_box.addButton(history_button, QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton(QMessageBox.StandardButton.Ok)
        history_button.clicked.connect(self.show_version_history_dialog)
        msg_box.exec()

    def show_version_history_dialog(self):
        """Menampilkan riwayat versi dari file JSON dalam dialog yang bisa di-scroll."""
        try:
            with open(resource_path('assets/version_history.json'), 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            html_output = "<h3>Riwayat Versi</h3>"
            for entry in data['versions']:
                html_output += f"<p><b>{entry['version']} ({entry['date']})</b></p><ul>"
                for change in entry['changes']:
                    html_output += f"<li>{change}</li>"
                html_output += "</ul>"

            # Membuat dialog custom
            dialog = QDialog(self.win)
            dialog.setWindowTitle("Riwayat Versi")
            dialog.setMinimumSize(400, 300) # Ukuran minimum agar tidak terlalu kecil

            layout = QVBoxLayout(dialog)

            # Menggunakan QTextBrowser untuk konten yang bisa di-scroll
            text_browser = QTextBrowser()
            text_browser.setHtml(html_output)
            text_browser.setOpenExternalLinks(True) # Jika ada link di masa depan

            layout.addWidget(text_browser)

            # Menambahkan tombol OK
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(dialog.accept)
            layout.addWidget(button_box)

            dialog.exec()

        except (FileNotFoundError, json.JSONDecodeError) as e:
            QMessageBox.critical(self.win, "Error", f"Gagal memuat riwayat versi: {e}")

    def set_date_filter(self, filter_type):
        """Mengatur filter tanggal."""
        self.win.date_filter = filter_type
        self.settings.setValue("date_filter", filter_type)
        self.win.refresh_manager.refresh_content_tree()

    def set_theme(self, theme_identifier):
        """Menyimpan dan menerapkan tema yang dipilih."""
        self.settings.setValue("theme", theme_identifier)
        self.load_theme()
        for action in self.win.theme_group.actions():
            if action.property("theme_id") == theme_identifier:
                action.setChecked(True)
                break
        self.populate_theme_menu()

    def load_theme(self):
        """Memuat tema dari pengaturan."""
        theme_setting = self.settings.value("theme", "system")
        stylesheet = ""
        if os.path.exists(str(theme_setting)):
            try:
                with open(theme_setting, "r", encoding="utf-8") as f:
                    stylesheet = f.read()
            except Exception as e:
                print(f"Gagal memuat tema kustom: {e}")
                self.settings.setValue("theme", "system")
                theme_setting = "system"

        if theme_setting == "dark":
            stylesheet = config.DARK_STYLESHEET
        elif theme_setting == "light":
            stylesheet = config.LIGHT_STYLESHEET
        elif theme_setting == "nordic_twilight":
            stylesheet = config.NORDIC_TWILIGHT_STYLESHEET
        elif theme_setting == "system":
            stylesheet = config.DARK_STYLESHEET if self.win.palette().window().color().lightness() < 128 else config.LIGHT_STYLESHEET

        if stylesheet:
            self.win.setStyleSheet(stylesheet)

    def set_scale(self, scale_name):
        """Menyimpan dan menerapkan skala UI."""
        self.settings.setValue("ui_scale", scale_name)
        self.load_scale()

    def load_scale(self):
        """Memuat skala UI dari pengaturan."""
        scale_name = self.settings.value("ui_scale", config.DEFAULT_SCALE)
        self.win.scale_config = config.UI_SCALE_CONFIG[scale_name]
        for action in self.win.scale_group.actions():
            if action.text() == scale_name:
                action.setChecked(True)
                break
        self.apply_scaling()

    def apply_scaling(self):
        """Menerapkan skala ke elemen UI."""
        if not self.win.scale_config: return
        list_font = QFont("Segoe UI", self.win.scale_config['list_font_size'])
        title_font = QFont("Segoe UI", self.win.scale_config['title_font_size'], QFont.Weight.Bold)
        icon_size = QSize(self.win.scale_config['icon_size'], self.win.scale_config['icon_size'])

        for label in [self.win.topic_title_label, self.win.subject_title_label,
                      self.win.content_title_label, self.win.task_category_title_label,
                      self.win.task_title_label]:
            label.setFont(title_font)

        for widget in [self.win.topic_list, self.win.subject_list,
                       self.win.task_category_list]:
            widget.setFont(list_font)
            widget.setIconSize(icon_size)

        self.win.content_tree.setFont(list_font)
        self.win.task_tree.setFont(list_font)
        self.win.refresh_manager.refresh_all_views()