from PIL import Image

ASCII_CHARS = "`.-':_,^=;><+!rc*/z?sLTv)J7(|Fi{C}fI31tlu[neoZ5Yxjya]2ESwqkP6h9d4VpOGbUAKXHm8RD#$Bg0MNWQ%&@"


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

