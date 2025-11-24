from PIL import Image
import numpy as np

ASCII_CHARS = " `.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"


def ascii_convert(img: Image.Image, output_width: int = 100) -> str:
    """
    Converts a given PIL Image object to ASCII art.

    Args:
        img: The input PIL Image object.
        output_width: The desired width of the ASCII art output.

    Returns:
        A string representing the ASCII art.
    """
    width, height = img.size
    aspect_ratio = height / width
    output_height = int(output_width * aspect_ratio * 0.5)
    img_prep = img.convert("L").resize((output_width, output_height))

    output = []
    for y in range(output_height):
        for x in range(output_width):
            pixel_value = img_prep.getpixel((x, y))
            map_index = pixel_value * (len(ASCII_CHARS) - 1) // 255
            output.append(ASCII_CHARS[map_index])
        output.append("\n")

    return "".join(output)


# See: https://en.wikipedia.org/wiki/Braille_Patterns
def _blocks_to_braille(blocks):
    # Веса для преобразования блока в символ Брайля
    weights = np.array([[1, 8], [2, 16], [4, 32], [64, 128]])
    # Поэлементное умножение каждого блока на веса
    weighted_blocks = (blocks // 255) * weights
    # Складываем значения внутри каждого блока для получения оффсетов
    offsets = weighted_blocks.sum(axis=(-2, -1))
    # Конвертируем каждый оффсет в соответствующий символ
    return np.vectorize(chr)(offsets + 0x2800)


def braille_convert(img: Image.Image, output_width: int = 100) -> str:
    width, height = img.size

    # Обрезаем чтобы изображение делилось на блоки
    width = width - (width % 2)
    height = height - (height % 4)

    # Делим наше изображение на массив блоков 4х2
    shape = (height // 4, 4, width // 2, 2)
    blocks = (
        np.array(img.convert("L").resize((width, height))).reshape(shape).swapaxes(1, 2)
    )

    chars = _blocks_to_braille(blocks)

    # Объединяем наши символы из двумерного массива в одну строку
    return "\n".join("".join(row) for row in chars)
