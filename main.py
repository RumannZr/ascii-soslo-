from PIl import Image
from pathlib import Path


ASCII_CHARS = "`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"
IMAGE_PATH = Path(input("Введите путь к файлу: "))
BRAILLE_CHARS = ""



def ascii_convert(IMAGE_PATH, ASCII_CHARS):

    try:
        with Image.open(IMAGE_PATH) as img:

        width, height = img.size()
        aspect_ratio = 0.5
        output_width = 100
        output_height = output_width * aspect_ratio
        img_prep = img.convert('L').resize(output_width, output_height)

        output = []

        for y in range(output_height):

            for x in range(output_width):

                map_index = img.getpixel(x,y) * (len(ASCII_CHARS) - 1) // 255
                output_string.append(ASCII_CHARS[map_index])

            output.append("\n") 

    except FileNotFound:
        print(f"File was not found")
    except Exception as e:
        print(f"An error was accured: {e}")

    return "".join(output)
