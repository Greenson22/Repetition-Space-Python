# file: config.py

BASE_PATH = "data/contents/topics"
REPETITION_CODES = ["R0D", "R1D", "R3D", "R7D", "R7D1", "R7D2", "R7D3", "R30D", "Finish"]

# TAMBAHKAN INI
REPETITION_CODES_DAYS = {
    "R0D": 0,
    "R1D": 1,
    "R3D": 3,
    "R7D": 7,
    "R7D1": 7,
    "R7D2": 7,
    "R7D3": 7,
    "R30D": 30,
}

DARK_STYLESHEET = """
    QMainWindow, QWidget, QDialog { background-color: #2E3440; color: #D8DEE9; font-family: Segoe UI; font-size: 10pt; }
    QSplitter::handle { background-color: #4C566A; width: 3px; }
    QLabel { color: #ECEFF4; padding-bottom: 5px; }
    QListWidget, QTreeWidget { background-color: #3B4252; border: 1px solid #4C566A; border-radius: 5px; padding: 5px; }
    QListWidget::item:selected, QTreeWidget::item:selected { background-color: #88C0D0; color: #2E3440; }
    QComboBox { background-color: #D8DEE9; color: #2E3440; border-radius: 3px; padding: 1px 4px; }
    QPushButton { background-color: #4C566A; border: none; padding: 8px; border-radius: 5px; font-weight: bold; }
    QPushButton:hover { background-color: #5E81AC; }
    QPushButton:disabled { background-color: #434C5E; color: #6F7A8C; }
    QHeaderView::section { background-color: #434C5E; padding: 4px; border: 1px solid #4C566A; color: #ECEFF4; font-weight: bold; }
    QHeaderView::down-arrow { subcontrol-origin: padding; subcontrol-position: center right; width: 12px; }
    QHeaderView::up-arrow { subcontrol-origin: padding; subcontrol-position: center right; width: 12px; }
    QCalendarWidget QToolButton { color: white; }
    QCalendarWidget QMenu { background-color: #4C566A; }
    QCalendarWidget QSpinBox { background-color: #D8DEE9; color: #2E3440; }
    QCalendarWidget QAbstractItemView { background-color: #3B4252; selection-background-color: #88C0D0; selection-color: #2E3440; }
"""

LIGHT_STYLESHEET = """
    QMainWindow, QWidget, QDialog { background-color: #F0F0F0; color: #000000; font-family: Segoe UI; font-size: 10pt; }
    QSplitter::handle { background-color: #D0D0D0; width: 3px; }
    QLabel { color: #000000; padding-bottom: 5px; }
    QListWidget, QTreeWidget { background-color: #FFFFFF; border: 1px solid #D0D0D0; border-radius: 5px; padding: 5px; }
    QListWidget::item:selected, QTreeWidget::item:selected { background-color: #0078D7; color: #FFFFFF; }
    QComboBox { background-color: #FFFFFF; color: #000000; border: 1px solid #D0D0D0; border-radius: 3px; padding: 1px 4px; }
    QPushButton { background-color: #E0E0E0; border: 1px solid #D0D0D0; padding: 8px; border-radius: 5px; font-weight: bold; }
    QPushButton:hover { background-color: #D0D0D0; }
    QPushButton:disabled { background-color: #F5F5F5; color: #A0A0A0; }
    QHeaderView::section { background-color: #E0E0E0; padding: 4px; border: 1px solid #D0D0D0; color: #000000; font-weight: bold; }
    QHeaderView::down-arrow { subcontrol-origin: padding; subcontrol-position: center right; width: 12px; }
    QHeaderView::up-arrow { subcontrol-origin: padding; subcontrol-position: center right; width: 12px; }
    QCalendarWidget QToolButton { color: black; }
    QCalendarWidget QMenu { background-color: #FFFFFF; }
    QCalendarWidget QSpinBox { background-color: #FFFFFF; color: #000000; }
    QCalendarWidget QAbstractItemView { background-color: #FFFFFF; selection-background-color: #0078D7; selection-color: #FFFFFF; }
"""