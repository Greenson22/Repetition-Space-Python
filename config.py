# file: config.py

import os

def load_stylesheet(filename):
    """Membaca file stylesheet dari direktori assets/styles."""
    # Pastikan path ini sesuai dengan struktur proyek Anda
    path = os.path.join("assets", "styles", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Peringatan: Stylesheet '{filename}' tidak ditemukan di '{path}'.")
        return ""

# --- Path Konfigurasi ---
BASE_PATH = "data/contents/topics"
TASK_BASE_PATH = "data/contents/my_tasks.json"

# --- Ikon Default ---
DEFAULT_TOPIC_ICON = "📁"
DEFAULT_SUBJECT_ICON = "📚"
DEFAULT_CATEGORY_ICON = "📂"
DEFAULT_TASK_ICON = "✔️"

AVAILABLE_ICONS = ["📁", "💼", "📝", "📓", "📚", "💡", "🎯", "⭐", "⚙️", "🔧", "📂", "✔️"]

# --- Konfigurasi Skala UI ---
UI_SCALE_CONFIG = {
    "Kecil": {
        "list_font_size": 10,
        "title_font_size": 13,
        "icon_size": 20
    },
    "Sedang": {
        "list_font_size": 11,
        "title_font_size": 14,
        "icon_size": 22
    },
    "Besar": {
        "list_font_size": 13,
        "title_font_size": 16,
        "icon_size": 26
    }
}
DEFAULT_SCALE = "Sedang"

# --- Kode Repetisi ---
REPETITION_CODES = ["R0D", "R1D", "R3D", "R7D", "R7D2", "R7D3", "R30D", "Finish"]

REPETITION_CODES_DAYS = {
    "R0D": 0,
    "R1D": 1,
    "R3D": 3,
    "R7D": 7,
    "R7D2": 7,
    "R7D3": 7,
    "R30D": 30,
}

# --- Memuat Stylesheets dari File Eksternal ---
DARK_STYLESHEET = load_stylesheet("dark.qss")
LIGHT_STYLESHEET = load_stylesheet("light.qss")
NORDIC_TWILIGHT_STYLESHEET = load_stylesheet("nordic_twilight.qss")