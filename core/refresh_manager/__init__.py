# file: core/refresh_manager/__init__.py

from .topic_refresher import TopicRefresher
from .subject_refresher import SubjectRefresher
from .content_refresher import ContentRefresher
from .task_refresher import TaskRefresher
from .task_category_refresher import TaskCategoryRefresher

class RefreshManager:
    """Kelas untuk mengelola semua operasi refresh UI."""
    def __init__(self, main_window):
        self.win = main_window
        self.data_manager = main_window.data_manager
        self.settings = main_window.settings
        
        # Inisialisasi sub-refresher
        self.topic = TopicRefresher(main_window)
        self.subject = SubjectRefresher(main_window)
        self.content = ContentRefresher(main_window)
        self.task = TaskRefresher(main_window)
        self.task_category = TaskCategoryRefresher(main_window)

    def refresh_all_views(self):
        """Memanggil semua fungsi refresh."""
        self.topic.refresh_topic_list()
        self.subject.refresh_subject_list()
        self.content.refresh_content_tree()
        self.task_category.refresh_task_category_list()
        self.task.refresh_task_list()

    def save_and_refresh_content(self):
        """Menyimpan konten saat ini dan merefresh tampilan."""
        self.win.handlers.update_earliest_date_in_metadata()
        self.data_manager.save_content(self.win.current_subject_path, self.win.current_content)
        self.content.refresh_content_tree()
        self.subject.refresh_subject_list()
        
    def reselect_task(self, task_name_to_select, category_name_to_select):
        """Memilih kembali item task setelah operasi."""
        self.task.reselect_task(task_name_to_select, category_name_to_select)

    def refresh_topic_list(self):
        self.topic.refresh_topic_list()

    def refresh_subject_list(self):
        self.subject.refresh_subject_list()

    def refresh_content_tree(self):
        self.content.refresh_content_tree()

    def refresh_task_category_list(self):
        self.task_category.refresh_task_category_list()

    def refresh_task_list(self):
        self.task.refresh_task_list()