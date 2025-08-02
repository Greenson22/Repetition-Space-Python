# file: test/core/refresh_manager.py

from PyQt6.QtWidgets import QListWidgetItem, QTreeWidgetItem
from PyQt6.QtCore import Qt
from datetime import datetime
import utils

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


class RefreshManager:
    """Kelas untuk mengelola semua operasi refresh UI."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager
        self.settings = main_window.settings

    def refresh_all_views(self):
        """Memanggil semua fungsi refresh."""
        self.refresh_topic_list()
        self.refresh_subject_list()
        self.refresh_content_tree()
        self.refresh_task_category_list()
        self.refresh_task_list()

    def refresh_topic_list(self):
        self.win.topic_list.clear()
        topics = self.data_manager.get_topics()
        for topic_data in topics:
            item = QListWidgetItem(f"{topic_data.get('icon', '??')} {topic_data.get('name', '')}")
            self.win.topic_list.addItem(item)

    def refresh_subject_list(self):
        current_item_text = self.win.subject_list.currentItem().text() if self.win.subject_list.currentItem() else None
        self.win.subject_list.blockSignals(True)
        self.win.subject_list.clear()

        subjects = self.data_manager.get_subjects(self.win.current_topic_path)
        item_to_reselect = None
        date_format = self.settings.value("date_format", "long")

        for name, date, code, icon in subjects:
            display_text = f"{icon} {name}"
            if date and code:
                formatted_date = utils.format_date(date, date_format)
                display_text += f"\n  ({formatted_date} - {code})"

            item = QListWidgetItem(display_text)
            self.win.subject_list.addItem(item)
            if display_text == current_item_text:
                item_to_reselect = item

        if item_to_reselect:
            self.win.subject_list.setCurrentItem(item_to_reselect)

        self.win.subject_list.blockSignals(False)

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

        # Langkah 2: Terapkan filter pada daftar yang sudah memiliki indeks asli
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

        # Langkah 3: Urutkan daftar (yang mungkin sudah terfilter)
        sorted_discussions = sorted(
            discussions_to_process,
            key=lambda item: get_content_sort_key(item['data'])
        )

        item_to_reselect = None
        # Langkah 4: Bangun Tree UI menggunakan daftar yang sudah benar
        for i, item in enumerate(sorted_discussions): # Tambahkan enumerate untuk penomoran
            original_index = item['original_index']
            discussion_data = item['data']

            # --- PERUBAHAN: Tambahkan nomor di depan diskusi ---
            discussion_text = discussion_data.get("discussion", "Diskusi kosong")
            parent_item = QTreeWidgetItem(self.win.content_tree)
            parent_item.setText(0, f"{i + 1}. {discussion_text}")
            # --- AKHIR PERUBAHAN ---

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

            # Indeks point bersifat relatif terhadap induknya, jadi tidak terpengaruh filter diskusi
            for j, point_data in enumerate(discussion_data.get("points", [])):
                child_item = QTreeWidgetItem(parent_item)
                item_data = {"type": "point", "parent_index": original_index, "index": j}
                child_item.setData(0, Qt.ItemDataRole.UserRole, item_data)
                child_item.setText(0, point_data.get("point_text", "Point kosong"))
                child_item.setText(1, utils.format_date(point_data.get("date", ""), date_format))
                self.win.handlers.create_repetition_combobox(child_item, 2, point_data.get("repetition_code", "R0D"), item_data)

                if selected_item_data == item_data:
                    item_to_reselect = child_item

            if self.win.search_query or original_index in expanded_indices:
                parent_item.setExpanded(True)

        if item_to_reselect:
            self.win.content_tree.setCurrentItem(item_to_reselect)

        self.win.handlers.update_button_states()


    def save_and_refresh_content(self):
        """Menyimpan konten saat ini dan merefresh tampilan."""
        self.win.handlers.update_earliest_date_in_metadata()
        self.data_manager.save_content(self.win.current_subject_path, self.win.current_content)
        self.refresh_content_tree()
        self.refresh_subject_list()

    def refresh_task_category_list(self):
        """Merefresh daftar kategori task dengan penanganan format data lama/baru."""
        current_item_text = self.win.task_category_list.currentItem().text() if self.win.task_category_list.currentItem() else None
        self.win.task_category_list.blockSignals(True)
        self.win.task_category_list.clear()

        self.win.task_category_list.addItem("Semua Task")
        categories = self.data_manager.get_task_categories()

        item_to_reselect = None
        for cat_data in categories:
            display_text = ""
            if isinstance(cat_data, dict):
                display_text = f"{cat_data.get('icon', '')} {cat_data.get('name', '')}"
            elif isinstance(cat_data, str):
                display_text = f"?? {cat_data}"
            else:
                continue

            item = QListWidgetItem(display_text)
            self.win.task_category_list.addItem(item)
            if display_text == current_item_text:
                item_to_reselect = item

        if item_to_reselect:
            self.win.task_category_list.setCurrentItem(item_to_reselect)
        else:
            self.win.task_category_list.setCurrentRow(0)

        self.win.task_category_list.blockSignals(False)
        if self.win.task_category_list.currentItem():
             self.win.handlers.task_category_selected(self.win.task_category_list.currentItem(), None)

    def refresh_task_list(self):
        """Merefresh daftar task berdasarkan kategori yang dipilih."""
        self.win.task_tree.blockSignals(True)
        self.win.task_tree.clear()

        if not self.win.current_task_category:
            self.win.handlers.update_button_states()
            self.win.task_tree.blockSignals(False)
            return

        tasks = (self.data_manager.get_all_tasks() if self.win.current_task_category == "Semua Task"
                 else self.data_manager.get_tasks(self.win.current_task_category))
        date_format = self.settings.value("date_format", "long")

        for index, task_data in enumerate(tasks):
            item = QTreeWidgetItem(self.win.task_tree)

            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            check_state = Qt.CheckState.Checked if task_data.get('checked', False) else Qt.CheckState.Unchecked
            item.setCheckState(0, check_state)

            item.setText(0, task_data.get('name', ''))
            item.setText(1, str(task_data.get('count', 0)))
            item.setText(2, utils.format_date(task_data.get('date', ''), date_format))

            user_data = {
                "original_name": task_data.get("original_name", task_data.get("name")),
                "category": task_data.get("category", self.win.current_task_category),
                "index": index
            }
            item.setData(0, Qt.ItemDataRole.UserRole, user_data)

        self.win.handlers.update_button_states()
        self.win.task_tree.blockSignals(False)

    def reselect_task(self, task_name_to_select, category_name_to_select):
        """Memilih kembali item task setelah operasi."""
        for i in range(self.win.task_tree.topLevelItemCount()):
            item = self.win.task_tree.topLevelItem(i)
            task_info = item.data(0, Qt.ItemDataRole.UserRole)
            if (task_info.get("original_name") == task_name_to_select and
                task_info.get("category") == category_name_to_select):
                self.win.task_tree.setCurrentItem(item)
                break