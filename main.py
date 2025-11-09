# main.py

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image

# Import the UI class from the gui.py file
from gui import Ui_MainWindow

from dither import *


class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.original_image = None
        self.resized_image = None
        self.processed_image = None

        self.ui.open_button.clicked.connect(self.open_image)
        self.ui.width_slider.valueChanged.connect(self.resize_image)
        self.ui.dithering_combo.currentTextChanged.connect(self.dither_image)

        self.dither_type = "None"

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.original_image = Image.open(file_path).convert("L")
            self.processed_image = self.original_image.copy()

            # Update slider range and value
            self.ui.width_slider.setMaximum(self.original_image.width)
            self.ui.width_slider.setValue(self.original_image.width)

            # Update the width value label
            self.ui.width_value_label.setText(str(self.original_image.width))

            self.dither_image()
            self.display_image()

    def resize_image(self):
        if self.original_image:
            new_width = self.ui.width_slider.value()

            # Update the width value label as the slider moves
            self.ui.width_value_label.setText(str(new_width))

            aspect_ratio = self.original_image.height / self.original_image.width
            new_height = int(new_width * aspect_ratio)

            self.resized_image = self.original_image.resize(
                (new_width, new_height), Image.Resampling.LANCZOS
            )
            self.dither_image()
            self.display_image()

    def display_image(self):
        if self.processed_image:
            image_data = self.processed_image.tobytes("raw", "L")
            q_image = QImage(
                image_data,
                self.processed_image.width,
                self.processed_image.height,
                self.processed_image.width,
                QImage.Format_Grayscale8,
            )
            pixmap = QPixmap.fromImage(q_image)

            # Set the pixmap on our custom AspectLabel
            self.ui.image_label.setPixmap(pixmap)

    def dither_image(self):
        self.dither_type = self.ui.dithering_combo.currentText()
        self.processed_image = self.resized_image.copy()
        match self.dither_type:
            case "Bayer level 0":
                dither_image_bayer(self.processed_image, 0)
            case "Bayer level 1":
                dither_image_bayer(self.processed_image, 1)
            case "Bayer level 2":
                dither_image_bayer(self.processed_image, 2)
            case "Bayer level 3":
                dither_image_bayer(self.processed_image, 3, inverse=True)
            case _:
                pass
        self.display_image()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ImageProcessorApp()
    main_window.show()
    sys.exit(app.exec_())
