# file: core/refresh_manager/subject_refresher.py
from PyQt6.QtWidgets import QListWidgetItem
import utils

class SubjectRefresher:
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager
        self.settings = main_window.settings

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