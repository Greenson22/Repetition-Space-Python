# file: utils.py

import sys
import os
from datetime import datetime

def format_date(date_str, format_type="long"):
    """
    Mengubah format tanggal YYYY-MM-DD ke format yang ditentukan.
    format_type: "short", "medium", "long"
    """
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if format_type == "short":
            return date_obj.strftime("%Y-%m-%d")
        elif format_type == "medium":
            return date_obj.strftime("%d %b %Y")
        # Default to long format
        return date_obj.strftime("%A, %d %B %Y")
    except ValueError:
        return date_str

def resource_path(relative_path):
    """ Mendapatkan path absolut ke resource, berfungsi untuk mode dev dan PyInstaller """
    try:
        # PyInstaller membuat folder temp dan menyimpan path di _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)