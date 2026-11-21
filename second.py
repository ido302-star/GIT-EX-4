import os
import subprocess
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

APP_NAME = "Student Grades Manager"
AUTHOR = "Ido Dekel"
REPO_URL = "https://github.com/ido302-star/GIT-EX-4"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.student_ids = []
        self.original_grades = []
        self.corrected_grades = []
        self.selected_file = ''

        self.setWindowTitle(APP_NAME)
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
        if not self.selected_file:
            QMessageBox.information(self, "No File", "Please load a students file first.")
            return

        try:
            # Load without data_only so any formulas elsewhere in the file are kept
            workbook = openpyxl.load_workbook(self.selected_file)
            sheet = workbook.active

            # Walk the rows exactly like load_file does (skip header and empty rows),
            # so each corrected grade goes back to the row it came from.
            # Only the value of the grade cell (column B) changes; its formatting stays.
            grades = iter(self.corrected_grades)
            for id_cell, grade_cell in sheet.iter_rows(min_row=2, max_col=2):
                if id_cell.value is None:
                    continue
                grade_cell.value = next(grades)

            workbook.save(self.selected_file)
            workbook.close()
        except PermissionError:
            QMessageBox.warning(
                self,
                "File Is Open",
                "The file could not be saved because it is open in another program "
                "(probably Excel).\n\nPlease close it and click \"Update File\" again.",
            )
            return
        except Exception as error:
            QMessageBox.critical(self, "Error", f"Could not update the file:\n{error}")
            return

        self.open_with_default_program(self.selected_file)

    @staticmethod
    def open_with_default_program(file_path):
        # Each OS has its own way to open a file with its default program:
        # - Windows: os.startfile() asks Windows to open the file, like double-clicking it.
        # - macOS:   the built-in "open" command opens the file with its default app.
        # - Linux:   "xdg-open" opens the file with the desktop's default app.
        if sys.platform.startswith("win"):
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", file_path])
        else:
            subprocess.Popen(["xdg-open", file_path])

    def show_about(self):
        about_box = QMessageBox(self)
        about_box.setWindowTitle(f"About {APP_NAME}")
        about_box.setIcon(QMessageBox.Icon.Information)
        # Rich text lets us use HTML, including a clickable <a> link
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(
            f"<h3>{APP_NAME}</h3>"
            "<p>Loads a students grades file (Excel), adds bonus points to every grade "
            "(capped at 100), and saves the corrected grades back to the file.</p>"
            f"<p>Created by: <b>{AUTHOR}</b></p>"
            f'<p>GitHub: <a href="{REPO_URL}">{REPO_URL}</a></p>'
        )
        # Make the link clickable and open it in the default web browser
        about_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        about_box.exec()


def main():
    app = QApplication(sys.argv)
    if STYLE_FILE.exists():
        app.setStyleSheet(STYLE_FILE.read_text(encoding="utf-8"))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
