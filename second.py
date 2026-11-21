import sys
from pathlib import Path

import openpyxl
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

TABLE_MIN_ROWS = 50

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
        self.table = QTableWidget(TABLE_MIN_ROWS, 3)
        self.table.setHorizontalHeaderLabels(["ID", "Original Grades", "Corrected Grades"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        # Bottom bar: bonus, update, about
        bottom_layout = QHBoxLayout()
        bonus_label = QLabel("Bonus Points")
        self.bonus_spinbox = QSpinBox()
        self.bonus_spinbox.setRange(0, 100)
        self.bonus_spinbox.setKeyboardTracking(False)
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
        self.bonus_spinbox.editingFinished.connect(self.bonus_changed)
        self.update_button.clicked.connect(self.update_file)
        self.about_button.clicked.connect(self.show_about)

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Students File",
            "",
            "Excel Files (*.xlsx);;All Files (*)",
        )
        if not file_path:
            return  # user cancelled

        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not open the file:\n{error}")
            return

        self.selected_file = file_path
        self.student_ids = []
        self.original_grades = []

        sheet = workbook.active
        # Column A = ID, column B = Grade; row 1 is the header
        for student_id, grade in sheet.iter_rows(min_row=2, max_col=2, values_only=True):
            if student_id is None:
                continue  # skip empty rows
            self.student_ids.append(student_id)
            self.original_grades.append(grade)
        workbook.close()

        self.corrected_grades = self.original_grades.copy()
        self.update_table()

    def update_table(self):
        self.table.clearContents()
        self.table.setRowCount(max(TABLE_MIN_ROWS, len(self.student_ids)))

        columns = (self.student_ids, self.original_grades, self.corrected_grades)
        for col, values in enumerate(columns):
            for row, value in enumerate(values):
                item = QTableWidgetItem("" if value is None else str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, item)

    def bonus_changed(self):
        if not self.selected_file:
            return  # no file loaded yet

        bonus = self.bonus_spinbox.value()
        self.corrected_grades = []
        for grade in self.original_grades:
            if grade is None:
                self.corrected_grades.append(None)  # keep missing grades empty
            else:
                self.corrected_grades.append(min(grade + bonus, 100))

        self.update_table()

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
