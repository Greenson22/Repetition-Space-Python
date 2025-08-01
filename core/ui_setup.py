# file: test/core/ui_setup.py

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QListWidget, 
    QTreeWidget, QPushButton, QSplitter, QFrame, QHeaderView
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize

class UIBuilder:
    """Kelas untuk membangun komponen antarmuka pengguna untuk ContentManager."""
    def __init__(self, main_window):
        self.win = main_window

    def setup_ui(self):
        """Membangun UI utama dan menempatkannya di window utama."""
        main_splitter = QSplitter(self.win)
        self.win.setCentralWidget(main_splitter)

        # --- Membuat Panel-Panel dengan Tata Letak Baru ---

        # 1. Panel Paling Kiri: Tasks & Kategori
        task_and_category_panel = self._create_task_and_category_panel()
        
        # 2. Panel Tengah: Topics & Subjects
        topic_and_subject_panel = self._create_topic_and_subject_panel()

        # 3. Panel Paling Kanan: Konten
        content_panel = self._create_content_panel()

        # --- Menambahkan Panel ke Splitter Utama ---
        main_splitter.addWidget(task_and_category_panel)
        main_splitter.addWidget(topic_and_subject_panel)
        main_splitter.addWidget(content_panel)
        
        # Mengatur ukuran awal panel-panel
        main_splitter.setSizes([250, 250, 600])

    def _create_task_and_category_panel(self):
        """Membuat panel gabungan untuk tasks (atas) dan kategori (bawah)."""
        main_panel = QWidget()
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(9, 9, 9, 9)

        # --- Bagian Tasks (Atas) ---
        self.win.task_title_label = QLabel("✔️ Tasks")
        self.win.task_tree = QTreeWidget()
        self.win.task_tree.setHeaderLabels(["Task", "Count", "Date"])
        # Mengubah ukuran kolom agar menyesuaikan dengan isi
        self.win.task_tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.win.task_tree.header().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.win.task_tree.header().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.win.task_tree.currentItemChanged.connect(self.win.handlers.update_button_states)
        
        task_buttons = self._create_button_layout([
            ("btn_tambah_task", "Tambah Task", self.win.handlers.add_task),
            ("btn_edit_task", "Edit Task", self.win.handlers.edit_task),
            ("btn_hapus_task", "Hapus Task", self.win.handlers.delete_task),
        ])

        main_layout.addWidget(self.win.task_title_label)
        main_layout.addWidget(self.win.task_tree)
        main_layout.addLayout(task_buttons)

        # --- Pemisah ---
        main_layout.addWidget(self._create_separator())

        # --- Bagian Kategori (Bawah) ---
        self.win.task_category_title_label = QLabel("Kategori Task")
        self.win.task_category_list = QListWidget()
        self.win.task_category_list.currentItemChanged.connect(self.win.handlers.task_category_selected)
        
        category_buttons = self._create_button_layout([
            ("btn_buat_kategori", "Buat", self.win.handlers.create_task_category),
            ("btn_ubah_kategori", "Ubah Nama", self.win.handlers.rename_task_category),
            ("btn_hapus_kategori", "Hapus", self.win.handlers.delete_task_category),
        ])

        main_layout.addWidget(self.win.task_category_title_label)
        main_layout.addWidget(self.win.task_category_list)
        main_layout.addLayout(category_buttons)

        return main_panel

    def _create_topic_and_subject_panel(self):
        """Membuat panel gabungan untuk topics (atas) dan subjects (bawah)."""
        main_panel = QWidget()
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(9, 9, 9, 9)

        # --- Bagian Topics (Atas) ---
        self.win.topic_title_label = QLabel("Topics")
        self.win.topic_list = QListWidget()
        self.win.topic_list.currentItemChanged.connect(self.win.handlers.topic_selected)
        
        topic_buttons = self._create_button_layout([
            ("btn_buat_topic", "Buat", self.win.handlers.create_topic),
            ("btn_rename_topic", "Ubah Nama", self.win.handlers.rename_topic),
            ("btn_delete_topic", "Hapus", self.win.handlers.delete_topic),
            ("btn_change_topic_icon", "Ubah Ikon", self.win.handlers.change_topic_icon),
        ])

        main_layout.addWidget(self.win.topic_title_label)
        main_layout.addWidget(self.win.topic_list)
        main_layout.addLayout(topic_buttons)

        # --- Pemisah ---
        main_layout.addWidget(self._create_separator())

        # --- Bagian Subjects (Bawah) ---
        self.win.subject_title_label = QLabel("Subjects")
        self.win.subject_list = QListWidget()
        self.win.subject_list.currentItemChanged.connect(self.win.handlers.subject_selected)
        
        subject_buttons = self._create_button_layout([
            ("btn_buat_subject", "Buat", self.win.handlers.create_subject),
            ("btn_rename_subject", "Ubah Nama", self.win.handlers.rename_subject),
            ("btn_delete_subject", "Hapus", self.win.handlers.delete_subject),
            ("btn_change_subject_icon", "Ubah Ikon", self.win.handlers.change_subject_icon),
        ])

        main_layout.addWidget(self.win.subject_title_label)
        main_layout.addWidget(self.win.subject_list)
        main_layout.addLayout(subject_buttons)
        
        return main_panel

    def _create_content_panel(self):
        """Membuat panel utama untuk menampilkan konten."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        self.win.content_title_label = QLabel("📝 Content")
        
        self.win.content_tree = QTreeWidget()
        self.win.content_tree.setHeaderLabels(["Content", "Date", "Code"])
        self.win.content_tree.header().resizeSection(0, 350)
        self.win.content_tree.header().resizeSection(1, 150)
        self.win.content_tree.header().setSectionsClickable(True)
        self.win.content_tree.header().setSortIndicatorShown(True)
        self.win.content_tree.header().sectionClicked.connect(self.win.handlers.sort_by_column)
        self.win.content_tree.currentItemChanged.connect(self.win.handlers.update_button_states)

        discussion_buttons = self._create_button_layout([
            ("btn_tambah_diskusi", "Tambah Diskusi", self.win.handlers.add_discussion),
            ("btn_edit_diskusi", "Edit Diskusi", self.win.handlers.edit_discussion),
            ("btn_hapus_diskusi", "Hapus Diskusi", self.win.handlers.delete_discussion),
        ])

        point_buttons = self._create_button_layout([
            ("btn_tambah_point", "Tambah Point", self.win.handlers.add_point),
            ("btn_edit_point", "Edit Point", self.win.handlers.edit_point),
            ("btn_hapus_point", "Hapus Point", self.win.handlers.delete_point),
            ("btn_ubah_tanggal", "Ubah Tanggal", self.win.handlers.change_date_manually),
            ("btn_tandai_selesai", "Tandai Selesai", self.win.handlers.toggle_finish_status),
        ])
        
        layout.addWidget(self.win.content_title_label)
        layout.addWidget(self.win.content_tree)
        layout.addWidget(QLabel("Manajemen Diskusi:"))
        layout.addLayout(discussion_buttons)
        layout.addWidget(QLabel("Manajemen Point & Tanggal:"))
        layout.addLayout(point_buttons)
        return panel
    
    def _create_button_layout(self, buttons_config):
        """Membuat layout horizontal berisi tombol-tombol."""
        layout = QHBoxLayout()
        for attr, text, func in buttons_config:
            btn = QPushButton(text)
            btn.clicked.connect(func)
            setattr(self.win, attr, btn)
            layout.addWidget(btn)
        return layout

    def _create_separator(self):
        """Membuat widget garis pemisah horizontal."""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator