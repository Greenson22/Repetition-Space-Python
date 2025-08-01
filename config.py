# file: config.py

BASE_PATH = "data/contents/topics"
REPETITION_CODES = ["R0D", "R1D", "R3D", "R7D"]

STYLESHEET = """
    QMainWindow, QWidget, QDialog { background-color: #2E3440; color: #D8DEE9; font-family: Segoe UI; font-size: 10pt; }
    QSplitter::handle { background-color: #4C566A; width: 3px; }
    QLabel { color: #ECEFF4; padding-bottom: 5px; }
    QListWidget, QTreeWidget { background-color: #3B4252; border: 1px solid #4C566A; border-radius: 5px; padding: 5px; }
    QListWidget::item:selected, QTreeWidget::item:selected { background-color: #88C0D0; color: #2E3440; }
    QComboBox { background-color: #D8DEE9; color: #2E3440; border-radius: 3px; padding: 1px 4px; }
    QPushButton { background-color: #4C566A; border: none; padding: 8px; border-radius: 5px; font-weight: bold; }
    QPushButton:hover { background-color: #5E81AC; }
    QPushButton:disabled { background-color: #434C5E; color: #6F7A8C; }
    QHeaderView::section { background-color: #434C5E; padding: 4px; border: 1px solid #4C566A; }
    QCalendarWidget QToolButton { color: white; }
    QCalendarWidget QMenu { background-color: #4C566A; }
    QCalendarWidget QSpinBox { background-color: #D8DEE9; color: #2E3440; }
    QCalendarWidget QAbstractItemView { background-color: #3B4252; selection-background-color: #88C0D0; selection-color: #2E3440; }
"""