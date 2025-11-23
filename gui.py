# gui.py

from PyQt5.QtWidgets import (
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QComboBox,
    QStackedLayout,  # New import
    QPlainTextEdit,  # New import
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont  # Import QFont
from dither import DITHERING_TYPES


# Custom QLabel to automatically handle aspect ratio
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
        # When the label is resized, update the scaled pixmap
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self):
        if self._pixmap.isNull():
            return

        # Scale the pixmap to fit the label's size, keeping aspect ratio
        scaled_pixmap = self._pixmap.scaled(
            self.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,  # For better image quality
        )
        # Call the original QLabel's setPixmap to display the scaled version
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

        self.slider_label = QLabel("Image Width:")
        self.sidebar_layout.addWidget(self.slider_label)

        # --- Dithering Drop-down ---
        self.dithering_label = QLabel("Dithering Type:")
        self.sidebar_layout.addWidget(self.dithering_label)

        self.dithering_combo = QComboBox()
        # Add placeholder dithering options
        self.dithering_combo.addItems(DITHERING_TYPES)
        self.sidebar_layout.addWidget(self.dithering_combo)

        # --- Slider and Value Label Layout ---
        self.slider_layout = QHBoxLayout()
        self.width_slider = QSlider(Qt.Horizontal)
        self.width_slider.setMinimum(10)
        self.width_slider.setMaximum(1000)

        self.width_value_label = QLabel("400")  # Initial value
        self.width_value_label.setMinimumWidth(35)  # Ensure it has enough space

        self.slider_layout.addWidget(self.width_slider)
        self.slider_layout.addWidget(self.width_value_label)

        # Add the slider group to the sidebar
        self.sidebar_layout.addLayout(self.slider_layout)

        # Set the initial slider value after creating the label
        self.width_slider.setValue(400)

        self.main_layout.addWidget(self.sidebar_widget)

        # --- Image/Text Display Area ---
        self.display_stack = QStackedLayout()  # New stacked layout

        # Use our custom AspectLabel instead of a standard QLabel
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
        self.text_output.setStyleSheet(
            "background-color: black; color: white;"
        )  # Example styling
        self.display_stack.addWidget(self.text_output)  # Add text output to stack

        self.main_layout.addLayout(self.display_stack, 1)

