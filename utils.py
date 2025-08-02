# file: utils.py

import sys
import os
from datetime import datetime

def format_date_with_day(date_str):
    """Mengubah format tanggal YYYY-MM-DD menjadi 'Nama Hari, YYYY-MM-DD'."""
    if not date_str:
        return ""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.strftime("%A, %Y-%m-%d")
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