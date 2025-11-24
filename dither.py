import numpy as np
from PIL import Image
from numba import jit


def _bayer(level: int):
    if level == 0:
        return np.array([[0, 2], [3, 1]])
    bayer_prev = _bayer(level - 1)
    res = np.block(
        [[4 * bayer_prev, 4 * bayer_prev + 2], [4 * bayer_prev + 3, 4 * bayer_prev + 1]]
    )
    return res


def _bayer_normalized(level: int):
    matrix = _bayer(level)
    return matrix / matrix.size


def _dither_image_bayer(img, level, inverse=False):
    img_arr = np.array(img.convert("L")) / 255.0
    h, w = img_arr.shape

    threshold_map = _bayer_normalized(level)
    th, tw = threshold_map.shape

    # Tile the threshold map to cover the whole image
    # This creates a matrix of the same size as the image, filled with the pattern
    tiled_map = np.tile(threshold_map, (h // th + 1, w // tw + 1))

    # Crop it exactly to image size
    tiled_map = tiled_map[:h, :w]
    if inverse:
        tiled_map = 1 - tiled_map

    result = ((img_arr > tiled_map) * 255).astype(np.uint8)
    return Image.fromarray(result)


def _dither_image_none(img, inverse=False):
    fn = (
        (lambda x: 255 if x > 127 else 0)
        if not inverse
        else (lambda x: 0 if x > 127 else 255)
    )
    return img.convert("L").point(fn, mode="1")


@jit(nopython=True)
def _fs_loop(img_arr, h, w):
    # See: https://obrhubr.org/assets/dithering-in-colour/3ac81d80f16b88d8a912b8b8e03f42f3.webp
    for y in range(h):
        for x in range(w):
            old_pixel = img_arr[y, x]
            new_pixel = 1 if old_pixel > 0.5 else 0
            img_arr[y, x] = new_pixel
            quant_error = old_pixel - new_pixel

            if x + 1 < w:
                img_arr[y, x + 1] += quant_error * (7 / 16)
            if y + 1 < h:
                if x - 1 >= 0:
                    img_arr[y + 1, x - 1] += quant_error * (3 / 16)
                img_arr[y + 1, x] += quant_error * (5 / 16)
                if x + 1 < w:
                    img_arr[y + 1, x + 1] += quant_error * (1 / 16)
    return img_arr


@jit(nopython=True)
def _atk_loop(img_arr, h, w):
    # See: https://obrhubr.org/assets/dithering-in-colour/3ac81d80f16b88d8a912b8b8e03f42f3.webp
    for y in range(h):
        for x in range(w):
            old_pixel = img_arr[y, x]
            new_pixel = 1 if old_pixel > 0.5 else 0
            img_arr[y, x] = new_pixel
            quant_error = old_pixel - new_pixel
            portion = quant_error / 8.0

            if x + 1 < w:
                img_arr[y, x + 1] += portion
            if x + 2 < w:
                img_arr[y, x + 2] += portion
            if y + 1 < h and x - 1 >= 0:
                img_arr[y + 1, x - 1] += portion
            if y + 1 < h:
                img_arr[y + 1, x] += portion
            if y + 1 < h and x + 1 < w:
                img_arr[y + 1, x + 1] += portion
            if y + 2 < h:
                img_arr[y + 2, x] += portion
    return img_arr


def _dither_image_error(img, algorithm, inverse=False):
    img_arr = np.array(img.convert("L")) / 255.0
    h, w = img_arr.shape
    match algorithm:
        case "fs":
            img_arr = _fs_loop(img_arr, h, w)
        case "atk":
            img_arr = _atk_loop(img_arr, h, w)
    if inverse:
        img_arr = 1 - img_arr
    img_arr = (img_arr * 255).astype(np.uint8)
    return Image.fromarray(img_arr)


DITHERING_TYPES = [
    "None",
    "Floyd-Steinberg",
    "Atkinson",
    "Bayer level 0",
    "Bayer level 1",
    "Bayer level 2",
    "Bayer level 3",
]

DITHERING_FUNCTIONS = {
    "None": _dither_image_none,
    "Floyd-Steinberg": (
        lambda img, inverse=False: _dither_image_error(img, "fs", inverse)
    ),
    "Atkinson": (lambda img, inverse=False: _dither_image_error(img, "atk", inverse)),
    "Bayer level 0": (lambda img, inverse=False: _dither_image_bayer(img, 0, inverse)),
    "Bayer level 1": (lambda img, inverse=False: _dither_image_bayer(img, 1, inverse)),
    "Bayer level 2": (lambda img, inverse=False: _dither_image_bayer(img, 2, inverse)),
    "Bayer level 3": (lambda img, inverse=False: _dither_image_bayer(img, 3, inverse)),
}
