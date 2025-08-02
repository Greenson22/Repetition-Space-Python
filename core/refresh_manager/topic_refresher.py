# file: core/refresh_manager/topic_refresher.py
from PyQt6.QtWidgets import QListWidgetItem

class TopicRefresher:
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager

    def refresh_topic_list(self):
        self.win.topic_list.clear()
        topics = self.data_manager.get_topics()
        for topic_data in topics:
            item = QListWidgetItem(f"{topic_data.get('icon', '??')} {topic_data.get('name', '')}")
            self.win.topic_list.addItem(item)