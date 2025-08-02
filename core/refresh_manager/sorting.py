# file: core/refresh_manager/sorting.py
from datetime import datetime

def get_content_sort_key(item_data):
    """
    Menghasilkan kunci pengurutan untuk diskusi atau poin.
    - Prioritas 1: Kode repetisi (R0D, R1D, ..., Finish). 'Finish' akan dianggap paling akhir.
    - Prioritas 2: Tanggal (terlama ke terbaru).
    """
    repetition_code = item_data.get("repetition_code")
    date_str = item_data.get("date")

    # Memberikan nilai default yang besar untuk item tanpa tanggal atau dengan kode 'Finish'
    # agar mereka diletakkan di akhir.
    order_key = float('inf')
    date_key = datetime.max

    if repetition_code and repetition_code != "Finish":
        try:
            numeric_part = ''.join(filter(str.isdigit, repetition_code))
            if numeric_part:
                order_key = int(numeric_part)
            else:
                order_key = float('inf')
        except (ValueError, TypeError):
            order_key = float('inf')

    if date_str:
        try:
            date_key = datetime.strptime(date_str, "%Y-%m-%d")
        except (ValueError, TypeError):
            date_key = datetime.max

    return (order_key, date_key)