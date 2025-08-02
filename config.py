# file: config.py

import os
import json
from utils import resource_path

def load_stylesheet(filename):
    """Membaca file stylesheet dari direktori assets/styles."""
    # Menggunakan resource_path untuk menemukan stylesheet
    path = resource_path(os.path.join("assets", "styles", filename))
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Peringatan: Stylesheet '{filename}' tidak ditemukan di '{path}'.")
        return ""

def load_icons():
    """Membaca dan mem-parsing ikon dari file assets/icons.json."""
    # Menggunakan resource_path untuk menemukan icons.json
    path = resource_path(os.path.join("assets", "icons.json"))
    try:
        with open(path, "r", encoding="utf-8") as f:
            categorized_icons = json.load(f)
        
        # Buat daftar datar (flat list) dari semua ikon untuk validasi
        all_icons = [icon for category in categorized_icons.values() for icon in category]
        return categorized_icons, all_icons
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Peringatan: File 'icons.json' tidak ditemukan atau formatnya salah.")
        # Fallback ke daftar default jika file gagal dimuat
        default_icons = ["📁", "📚", "📂", "✔️"]
        return {"Default": default_icons}, default_icons

# --- Path Konfigurasi ---
# Path ini untuk data pengguna, JANGAN gunakan resource_path
# karena --add-data "data;data" menempatkannya relatif terhadap .exe
BASE_PATH = "data/contents/topics"
TASK_BASE_PATH = "data/contents/my_tasks.json"

# --- Ikon Default ---
DEFAULT_TOPIC_ICON = "📁"
DEFAULT_SUBJECT_ICON = "📚"
DEFAULT_CATEGORY_ICON = "📂"
DEFAULT_TASK_ICON = "✔️"

CATEGORIZED_ICONS, AVAILABLE_ICONS = load_icons()

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