# file: core/event_handlers/__init__.py


# Impor semua kelas handler yang telah dipisah
from .general_handlers import GeneralHandlers
from .topic_handlers import TopicHandlers
from .subject_handlers import SubjectHandlers
from .content_handlers import ContentHandlers
from .category_handlers import CategoryHandlers
from .task_handlers import TaskHandlers

class EventHandlers(
    GeneralHandlers,
    TopicHandlers,
    SubjectHandlers,
    ContentHandlers,
    CategoryHandlers,
    TaskHandlers
):
    """
    Kelas utama yang menggabungkan semua logika event handling.
    Kelas ini mewarisi semua metode dari kelas-kelas handler individual.
    """
    def __init__(self, main_window):
        # Inisialisasi superclass akan memanggil __init__ dari GeneralHandlers
        # yang merupakan basis dari semua handler lainnya.
        super().__init__(main_window)