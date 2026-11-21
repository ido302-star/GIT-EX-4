import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

STYLE_FILE = Path(__file__).with_name("style.qss")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ''

        self.setWindowTitle("Student Grades Manager")
        self.resize(800, 600)

        self._build_ui()
        self._connect_signals()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top bar: load file
        top_layout = QHBoxLayout()
        self.load_button = QPushButton("Load File")
        top_layout.addWidget(self.load_button)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # Grades table
        self.table = QTableWidget(50, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Original Grades", "Corrected Grades"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        # Bottom bar: bonus, update, about
        bottom_layout = QHBoxLayout()
        bonus_label = QLabel("Bonus Points")
        self.bonus_spinbox = QSpinBox()
        self.bonus_spinbox.setRange(0, 100)
        bonus_label.setBuddy(self.bonus_spinbox)

        self.update_button = QPushButton("Update File")
        self.about_button = QPushButton("About")
        self.about_button.setObjectName("secondaryButton")

        bottom_layout.addWidget(bonus_label)
        bottom_layout.addWidget(self.bonus_spinbox)
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.update_button)
        bottom_layout.addWidget(self.about_button)
        main_layout.addLayout(bottom_layout)

    def _connect_signals(self):
        self.load_button.clicked.connect(self.load_file)
        self.bonus_spinbox.valueChanged.connect(self.bonus_changed)
        self.update_button.clicked.connect(self.update_file)
        self.about_button.clicked.connect(self.show_about)

    def load_file(self):
        pass

    def bonus_changed(self, value):
        pass

    def update_file(self):
        pass

    def show_about(self):
        pass


def main():
    app = QApplication(sys.argv)
    if STYLE_FILE.exists():
        app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
