# file: main.py

import sys
import locale
from PyQt6.QtWidgets import QApplication

# Impor kelas utama dari file lain
from main_window import ContentManager

def main():
    """Fungsi utama untuk menjalankan aplikasi."""
    # Mengatur locale untuk nama hari dalam Bahasa Indonesia
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