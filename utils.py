# file: utils.py

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