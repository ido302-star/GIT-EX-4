import csv
import sys
from pathlib import Path

import numpy as np
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

STYLE_FILE = Path(__file__).with_name("third_style.qss")

APP_NAME = "Ice Cream Sales Analyzer"
AUTHOR = "Ido Dekel"
REPO_URL = "https://github.com/ido302-star/GIT-EX-4"

# Graph colors, matching third_style.qss
ACCENT_COLOR = "#0d9488"
TEXT_COLOR = "#334155"
GRID_COLOR = "#e2e8f0"
FIT_COLOR = "#f97316"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.temperatures = []
        self.revenues = []

        self.setWindowTitle(APP_NAME)
        self.resize(900, 650)

        self._build_ui()
        self._connect_signals()
        self.plot_graph()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Top bar: title + buttons
        top_layout = QHBoxLayout()
        title_label = QLabel(APP_NAME)
        title_label.setObjectName("titleLabel")
        self.load_button = QPushButton("Load File")
        self.about_button = QPushButton("About")
        self.about_button.setObjectName("secondaryButton")

        top_layout.addWidget(title_label)
        top_layout.addStretch()
        top_layout.addWidget(self.load_button)
        top_layout.addWidget(self.about_button)
        main_layout.addLayout(top_layout)

        # Graph card: navigation toolbar above the matplotlib canvas
        graph_card = QFrame()
        graph_card.setObjectName("graphCard")
        card_layout = QVBoxLayout(graph_card)
        card_layout.setContentsMargins(12, 12, 12, 12)
        card_layout.setSpacing(8)

        self.figure = Figure(figsize=(8, 5), tight_layout=True)
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.toolbar = NavigationToolbar2QT(self.canvas, self)

        card_layout.addWidget(self.toolbar)
        card_layout.addWidget(self.canvas)
        main_layout.addWidget(graph_card)

    def _connect_signals(self):
        self.load_button.clicked.connect(self.load_file)
        self.about_button.clicked.connect(self.show_about)

    def plot_graph(self):
        self.figure.clear()
        ax = self.figure.add_subplot()

        ax.scatter(self.temperatures, self.revenues, s=1, color=ACCENT_COLOR, label="Data")

        # Best-fit straight line (linear regression) - needs at least 2 points
        if len(self.temperatures) >= 2:
            slope, intercept = np.polyfit(self.temperatures, self.revenues, 1)
            x_line = np.array([min(self.temperatures), max(self.temperatures)])
            y_line = slope * x_line + intercept
            sign = "+" if intercept >= 0 else "-"
            equation = f"y = {slope:.2f}x {sign} {abs(intercept):.2f}"
            ax.plot(x_line, y_line, color=FIT_COLOR, linewidth=2, label=equation)
            # markerscale enlarges only the legend's dot, since s=1 is hard to see there
            ax.legend(loc="upper left", frameon=False, labelcolor=TEXT_COLOR, markerscale=6)

        ax.set_title("Ice Cream Revenue vs. Temperature", color=TEXT_COLOR, fontsize=14, fontweight="bold")
        ax.set_xlabel("Temperature (°C)", color=TEXT_COLOR)
        ax.set_ylabel("Revenue ($)", color=TEXT_COLOR)
        ax.tick_params(colors=TEXT_COLOR)
        ax.grid(True, color=GRID_COLOR, linestyle="--")
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)

        self.canvas.draw()

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose Data File",
            "",
            "CSV Files (*.csv);;All Files (*)",
        )
        if not file_path:
            return  # user cancelled

        temperatures = []
        revenues = []
        try:
            # utf-8-sig also handles the hidden BOM character Excel adds to CSV files
            with open(file_path, newline="", encoding="utf-8-sig") as file:
                reader = csv.reader(file)
                next(reader, None)  # skip the header row
                # Column 1 = Temperature, column 2 = Revenue
                for row in reader:
                    if len(row) < 2 or not row[0].strip() or not row[1].strip():
                        continue  # skip empty / incomplete rows
                    temperatures.append(float(row[0]))
                    revenues.append(float(row[1]))
        except (OSError, UnicodeDecodeError, ValueError) as error:
            QMessageBox.critical(self, "Error", f"Could not read the file:\n{error}")
            return

        self.temperatures = temperatures
        self.revenues = revenues
        self.plot_graph()

    def show_about(self):
        about_box = QMessageBox(self)
        about_box.setWindowTitle(f"About {APP_NAME}")
        about_box.setIcon(QMessageBox.Icon.Information)
        # Rich text lets us use HTML, including a clickable <a> link
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(
            f"<h3>{APP_NAME}</h3>"
            "<p>Loads ice cream sales data (CSV) and shows revenue vs. temperature "
            "as a scatter plot, with a best-fit regression line and its equation.</p>"
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
