# file: core/refresh_manager/content_refresher.py
from PyQt6.QtWidgets import QTreeWidgetItem
from PyQt6.QtCore import Qt
from datetime import datetime
import utils
from .sorting import get_content_sort_key

class ContentRefresher:
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager
        self.settings = main_window.settings

    def refresh_content_tree(self):
        """
        Merefresh, memfilter, dan menyortir tampilan konten dengan menjaga integritas indeks data asli.
        """
        expanded_indices = {
            item.data(0, Qt.ItemDataRole.UserRole).get("index")
            for i in range(self.win.content_tree.topLevelItemCount())
            if (item := self.win.content_tree.topLevelItem(i)).isExpanded()
            and (item_data := item.data(0, Qt.ItemDataRole.UserRole))
            and item_data.get("type") == "discussion"
        }
        selected_item_data = self.win.content_tree.currentItem().data(0, Qt.ItemDataRole.UserRole) if self.win.content_tree.currentItem() else None

        self.win.content_tree.clear()
        if not self.win.current_subject_path: return

        self.win.current_content = self.data_manager.load_content(self.win.current_subject_path)
        date_format = self.settings.value("date_format", "long")

        # Langkah 1: Pasangkan data dengan indeks aslinya SEBELUM diproses
        discussions_to_process = [
            {"data": data, "original_index": index}
            for index, data in enumerate(self.win.current_content.get("content", []))
        ]
        
        # Langkah 2: Terapkan filter pencarian jika ada query
        if self.win.search_query:
            query = self.win.search_query.lower()
            search_filtered_list = []
            for item in discussions_to_process:
                discussion_data = item['data']
                # Cek apakah query ada di teks diskusi
                if query in discussion_data.get("discussion", "").lower():
                    # Jika ada, tambahkan seluruh diskusi beserta semua point-nya
                    search_filtered_list.append(item)
                else:
                    # Jika tidak, cek di setiap point
                    if discussion_data.get("points"):
                        matching_points = [
                            point for point in discussion_data.get("points", [])
                            if query in point.get("point_text", "").lower()
                        ]
                        # Jika ada point yang cocok, tambahkan diskusi tapi HANYA dengan point yang cocok
                        if matching_points:
                            new_disc_data = discussion_data.copy()
                            new_disc_data["points"] = matching_points
                            search_filtered_list.append({"data": new_disc_data, "original_index": item["original_index"]})
            discussions_to_process = search_filtered_list

        # Langkah 3: Terapkan filter tanggal pada daftar yang sudah memiliki indeks asli
        if self.win.date_filter != "all":
            today_str = datetime.now().strftime("%Y-%m-%d")
            filtered_list = []

            for item in discussions_to_process:
                disc_data = item['data']

                # Filter untuk diskusi yang memiliki 'points'
                if disc_data.get("points"):
                    filtered_points = []
                    for point in disc_data.get("points", []):
                        point_date_str = point.get("date")
                        if not point_date_str: continue

                        if (self.win.date_filter == "today" and point_date_str == today_str) or \
                           (self.win.date_filter == "past_and_today" and point_date_str <= today_str):
                            filtered_points.append(point)

                    if filtered_points:
                        new_disc_data = disc_data.copy()
                        new_disc_data["points"] = filtered_points
                        filtered_list.append({"data": new_disc_data, "original_index": item["original_index"]})

                # Filter untuk diskusi tanpa 'points'
                else:
                    disc_date_str = disc_data.get("date")
                    if not disc_date_str: continue

                    if (self.win.date_filter == "today" and disc_date_str == today_str) or \
                       (self.win.date_filter == "past_and_today" and disc_date_str <= today_str):
                        filtered_list.append(item)

            discussions_to_process = filtered_list

        # Langkah 4: Urutkan daftar (yang mungkin sudah terfilter)
        sorted_discussions = sorted(
            discussions_to_process,
            key=lambda item: get_content_sort_key(item['data'])
        )

        item_to_reselect = None
        # Langkah 5: Bangun Tree UI menggunakan daftar yang sudah benar
        for i, item in enumerate(sorted_discussions): # Tambahkan enumerate untuk penomoran
            original_index = item['original_index']
            discussion_data = item['data']

            discussion_text = discussion_data.get("discussion", "Diskusi kosong")
            parent_item = QTreeWidgetItem(self.win.content_tree)
            parent_item.setText(0, f"{i + 1}. {discussion_text}")

            # Simpan data dengan INDEKS ASLI yang benar
            item_data_for_crud = {"type": "discussion", "index": original_index}
            parent_item.setData(0, Qt.ItemDataRole.UserRole, item_data_for_crud)

            if not discussion_data.get("points", []):
                parent_item.setText(1, utils.format_date(discussion_data.get("date", ""), date_format))
                self.win.handlers.create_repetition_combobox(parent_item, 2, discussion_data.get("repetition_code", "R0D"), item_data_for_crud)
            else:
                point_dates = [p.get("date") for p in discussion_data.get("points", []) if p.get("date")]
                if point_dates:
                    parent_item.setText(1, f"({utils.format_date(min(point_dates), date_format)})")

            if selected_item_data == item_data_for_crud:
                item_to_reselect = parent_item

            # --- AWAL PERBAIKAN ---
            # Ambil daftar point asli dari data utama untuk perbandingan indeks
            original_points = self.win.current_content["content"][original_index].get("points", [])

            # Iterasi melalui point yang mungkin sudah difilter
            for point_data in discussion_data.get("points", []):
                # Cari indeks asli dari point_data di dalam daftar point asli
                try:
                    original_point_index = original_points.index(point_data)
                except ValueError:
                    # Jika point tidak ditemukan (seharusnya tidak terjadi), lewati saja
                    continue

                child_item = QTreeWidgetItem(parent_item)
                # Gunakan original_point_index untuk data CRUD
                item_data = {"type": "point", "parent_index": original_index, "index": original_point_index}
                child_item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                child_item.setText(0, point_data.get("point_text", "Point kosong"))
                child_item.setText(1, utils.format_date(point_data.get("date", ""), date_format))
                self.win.handlers.create_repetition_combobox(child_item, 2, point_data.get("repetition_code", "R0D"), item_data)

                if selected_item_data == item_data:
                    item_to_reselect = child_item
            # --- AKHIR PERBAIKAN ---

            if self.win.search_query or original_index in expanded_indices:
                parent_item.setExpanded(True)

        if item_to_reselect:
            self.win.content_tree.setCurrentItem(item_to_reselect)

        self.win.handlers.update_button_states()