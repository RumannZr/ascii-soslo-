# gui.py

from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QStackedLayout,
    QPlainTextEdit,
    QCheckBox,
    QLineEdit,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont  # Import QFont
from dither import DITHERING_TYPES


class AspectLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pixmap = QPixmap()
        self.setMinimumSize(1, 1)

    def setPixmap(self, pixmap):
        if not isinstance(pixmap, QPixmap):
            super().setPixmap(pixmap)
            return

        self._pixmap = pixmap
        self._update_scaled_pixmap()

    def resizeEvent(self, event):
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self):
        if self._pixmap.isNull():
            return

        scaled_pixmap = self._pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,  # For better image quality
        )
        super().setPixmap(scaled_pixmap)


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowTitle("Image to ASCII/Braille Art Helper")
        MainWindow.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        MainWindow.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        # --- Sidebar ---
        self.sidebar_widget = QWidget()
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        self.sidebar_layout.setAlignment(Qt.AlignTop)
        self.sidebar_widget.setMaximumWidth(250)

        self.open_button = QPushButton("Open Image")
        self.sidebar_layout.addWidget(self.open_button)

        # --- Render Type Drop-down ---
        self.render_type_label = QLabel("Render Type:")
        self.sidebar_layout.addWidget(self.render_type_label)
        self.render_type_combo = QComboBox()
        self.render_type_combo.addItems(["Braille", "ASCII"])  # Updated items
        self.sidebar_layout.addWidget(self.render_type_combo)

        # --- Invert Colors Checkbox ---
        self.invert_checkbox = QCheckBox("Invert Colors")
        self.sidebar_layout.addWidget(self.invert_checkbox)

        # --- Dithering Drop-down ---
        self.dithering_label = QLabel("Dithering Type:")
        self.sidebar_layout.addWidget(self.dithering_label)
        self.dithering_combo = QComboBox()
        self.dithering_combo.addItems(DITHERING_TYPES)
        self.sidebar_layout.addWidget(self.dithering_combo)

        # --- Width Input ---
        self.width_label = QLabel("Image Width:")
        self.sidebar_layout.addWidget(self.width_label)
        self.width_input = QLineEdit("400")  # Default value
        self.sidebar_layout.addWidget(self.width_input)

        # --- Convert Button ---
        self.render_button = QPushButton("Convert")  # Renamed
        self.sidebar_layout.addWidget(self.render_button)

        # --- Spacer ---
        self.sidebar_layout.addStretch(1)

        # --- Text Output Buttons ---
        self.copy_button = QPushButton("Copy Text")
        self.sidebar_layout.addWidget(self.copy_button)
        self.save_button = QPushButton("Save to File")
        self.sidebar_layout.addWidget(self.save_button)

        self.main_layout.addWidget(self.sidebar_widget)

        # --- Image/Text Display Area ---
        self.display_stack = QStackedLayout()  # New stacked layout

        # custom AspectLabel instead of a standard QLabel
        self.image_label = AspectLabel("Open an image to begin")
        self.image_label.setAlignment(Qt.AlignCenter)
        self.display_stack.addWidget(self.image_label)  # Add image label to stack

        # New QPlainTextEdit for ASCII/Braille output
        self.text_output = QPlainTextEdit()
        self.text_output.setReadOnly(True)  # Make it read-only
        # У меня были проблемы с отображением текста, так что делай че хочешь с этим  TODO:
        font = QFont("Cascadia Code")  # Create a QFont object
        font.setStyleHint(QFont.Monospace)  # Set a style hint for fallback
        self.text_output.setFont(font)  # Use the correct setFont method
        self.text_output.setStyleSheet("background-color: black; color: white;")
        # Example styling
        self.display_stack.addWidget(self.text_output)  # Add text output to stack

        self.main_layout.addLayout(self.display_stack, 1)
