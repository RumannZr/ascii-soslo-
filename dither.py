import numpy as np

DITHERING_TYPES = [
    "None",
    "Bayer level 0",
    "Bayer level 1",
    "Bayer level 2",
    "Bayer level 3",
]


def bayer(level: int):
    if level == 0:
        return np.array([[0, 2], [3, 1]])
    bayer_prev = bayer(level - 1)
    i0 = 4 * bayer_prev
    i1 = 4 * bayer_prev + 2
    i2 = 4 * bayer_prev + 3
    i3 = 4 * bayer_prev + 1

    res = np.block([[i0, i1], [i2, i3]])
    return res


def bayer_normalized(level: int):
    return bayer(level) / (2 ** (level + 2))


def bayer_inverted(level: int):
    return 1 - bayer_normalized(level)


def dither_image_bayer(img, level, inverse=False):
    threshold_map = bayer_normalized(level) if not inverse else bayer_inverted(level)
    width, height = img.size
    pixel_map = img.load()
    for i in range(width):
        for j in range(height):
            i_norm, j_norm = i % (level + 2), j % (level + 2)
            brightness = img.getpixel((i, j)) / 255

            pixel_map[i, j] = 255 if brightness > threshold_map[i_norm, j_norm] else 0
