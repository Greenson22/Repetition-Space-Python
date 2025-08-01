# file: test/core/ui_setup.py

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QWidget, QLabel, QListWidget, 
    QTreeWidget, QPushButton, QSplitter
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize

class UIBuilder:
    """Kelas untuk membangun komponen antarmuka pengguna untuk ContentManager."""
    def __init__(self, main_window):
        self.win = main_window

    def setup_ui(self):
        """Membangun UI utama dan menempatkannya di window utama."""
        splitter = QSplitter(self.win)
        self.win.setCentralWidget(splitter)

        # Buat dan tambahkan panel-panel
        topic_panel = self._create_list_panel(
            title="Topics",
            selection_handler=self.win.handlers.topic_selected,
            buttons=[
                ("btn_buat_topic", "Buat", self.win.handlers.create_topic),
                ("btn_rename_topic", "Ubah Nama", self.win.handlers.rename_topic),
                ("btn_delete_topic", "Hapus", self.win.handlers.delete_topic),
                ("btn_change_topic_icon", "Ubah Ikon", self.win.handlers.change_topic_icon),
            ],
            type="topic" # Tandai tipe panel
        )
        self.win.topic_list = topic_panel.findChild(QListWidget)
        
        subject_panel = self._create_list_panel(
            title="Subjects",
            selection_handler=self.win.handlers.subject_selected,
            buttons=[
                ("btn_buat_subject", "Buat", self.win.handlers.create_subject),
                ("btn_rename_subject", "Ubah Nama", self.win.handlers.rename_subject),
                ("btn_delete_subject", "Hapus", self.win.handlers.delete_subject),
                ("btn_change_subject_icon", "Ubah Ikon", self.win.handlers.change_subject_icon),
            ],
            type="subject" # Tandai tipe panel
        )
        self.win.subject_list = subject_panel.findChild(QListWidget)

        content_panel = self._create_content_panel()

        splitter.addWidget(topic_panel)
        splitter.addWidget(subject_panel)
        splitter.addWidget(content_panel)
        splitter.setSizes([200, 250, 750])

    def _create_list_panel(self, title, selection_handler, buttons, type):
        """Membuat panel standar untuk daftar (Topics/Subjects)."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        title_label = QLabel(title)
        # Simpan label judul ke window utama untuk scaling
        if type == "topic":
            self.win.topic_title_label = title_label
        else:
            self.win.subject_title_label = title_label
        
        list_widget = QListWidget()
        list_widget.currentItemChanged.connect(selection_handler)
        
        button_layout = self._create_button_layout(buttons)
        
        layout.addWidget(title_label)
        layout.addWidget(list_widget)
        layout.addLayout(button_layout)
        return panel

    def _create_content_panel(self):
        """Membuat panel utama untuk menampilkan konten."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        title = QLabel("📝 Content")
        self.win.content_title_label = title # Simpan untuk scaling
        
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
        
        layout.addWidget(title)
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