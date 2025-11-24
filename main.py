import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
from PIL import Image, ImageEnhance

from gui import Ui_MainWindow

from dither import *
from img2text_converter import ascii_convert, braille_convert  # Re-added import


class ImageProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.original_image = None
        self.processed_image = None
        self.text_output = None

        # --- Connections ---
        self.ui.open_button.clicked.connect(self.open_image)
        self.ui.render_button.clicked.connect(self.render_image)
        self.ui.copy_button.clicked.connect(self.copy_text)
        self.ui.save_button.clicked.connect(self.save_text)

        # Initially disable copy/save buttons
        self.ui.copy_button.setEnabled(False)
        self.ui.save_button.setEnabled(False)

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.original_image = Image.open(file_path).convert("L")

            # Set the width input to the original image width
            self.ui.width_input.setText(str(self.original_image.width))

            # Display the original image as a preview
            self.display_output(image_to_display=self.original_image)

    def render_image(self):
        # Main func for image processing
        if not self.original_image:
            return

        # 1. Get width from text field and resize the image
        try:
            new_width = int(self.ui.width_input.text())
            if new_width <= 0:
                return
        except ValueError:
            return

        # Костыль, но не знаю как сделать лучше чтобы в текстовом поле задавалась именно ширина в символах
        if self.ui.render_type_combo.currentText() == "Braille":
            new_width = new_width * 2

        aspect_ratio = self.original_image.height / self.original_image.width
        new_height = int(new_width * aspect_ratio)
        resized_image = self.original_image.resize(
            (new_width, new_height), Image.Resampling.LANCZOS
        )

        self.processed_image = resized_image.copy()

        # 2. Add contrast to our image
        contrast_val = self.ui.contrast_slider.value() / 100.0
        enhancer = ImageEnhance.Contrast(self.processed_image)
        self.processed_image = enhancer.enhance(contrast_val)

        # 3. Check the selected render type
        render_type = self.ui.render_type_combo.currentText()

        # 3.1. Apply dithering to b&w and braille
        if render_type == "Black/White" or render_type == "Braille":
            dither_type = self.ui.dithering_combo.currentText()
            dither = DITHERING_FUNCTIONS[dither_type]
            inverse = self.ui.invert_checkbox.isChecked()
            self.processed_image = dither(self.processed_image, inverse)

        # 3.2. Display text or image
        if render_type == "ASCII" or render_type == "Braille":
            if render_type == "ASCII":
                self.text_output = ascii_convert(
                    self.processed_image, output_width=new_width
                )
            else:
                self.text_output = braille_convert(
                    self.processed_image, output_width=new_width
                )
            self.display_output(text_to_display=self.text_output)
        else:
            self.display_output(image_to_display=self.processed_image)

    def copy_text(self):
        """Copies the content of the text output to the clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.ui.text_output.toPlainText())

    def save_text(self):
        """Opens a dialog to save the text output to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save ASCII Art", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            with open(file_path, "w") as f:
                f.write(self.ui.text_output.toPlainText())

    def display_output(self, image_to_display=None, text_to_display=None):
        # Display settings both for original image and processed one
        if text_to_display is not None:
            self.ui.text_output.setPlainText(text_to_display)
            self.ui.display_stack.setCurrentIndex(1)  # Show text output
            self.ui.copy_button.setEnabled(True)
            self.ui.save_button.setEnabled(True)
        elif image_to_display is not None:
            image_data = image_to_display.tobytes("raw", "L")
            q_image = QImage(
                image_data,
                image_to_display.width,
                image_to_display.height,
                image_to_display.width,
                QImage.Format_Grayscale8,
            )
            pixmap = QPixmap.fromImage(q_image)

            self.ui.image_label.setPixmap(pixmap)
            self.ui.display_stack.setCurrentIndex(0)  # Show image label
            self.ui.copy_button.setEnabled(False)
            self.ui.save_button.setEnabled(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = ImageProcessorApp()
    main_window.show()
    sys.exit(app.exec_())
