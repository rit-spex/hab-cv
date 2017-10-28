
import io
import picamera
import numpy as np
import cv2
import imutils

def smooth(img, radius, kind='open'):
    kernel = np.ones((radius, radius), np.uint8)
    if kind == 'gaussian':
        img = cv2.GaussianBlur(img, (radius, radius), 0)
    elif kind == 'open':
        img = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    elif kind == 'close':
        img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)
    elif kind == 'erode':
        img = cv2.erode(mask, kernel, iterations=1)
    elif kind == 'dilate':
        img = cv2.dilate(mask, kernel, iterations=1)
    return img


def mask_as_color(binary_mask, bgr_color):
    bgr_mask = np.zeros((binary_mask.shape[0], binary_mask.shape[1], 3))
    for i in range(len(bgr_color)):
        bgr_mask[:, :, i] = binary_mask * bgr_color[i]
    return bgr_mask


def mask_color(img, limits, radius=1):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS_FULL)
    lower_limit, upper_limit = np.array(limits[0], dtype='uint8'), np.array(limits[1], dtype='uint8')
    mask = cv2.inRange(hls, lower_limit, upper_limit)
    mask = smooth(mask, radius, kind='close')
    masked_img = cv2.bitwise_and(img, img, mask=mask)
    return mask, masked_img


def get_hsl_mask(img, selection='vegetation', smoothing=2):
    # LIMITS IN HLS - Hue, Lightness, Saturation
    # range: 0 to 255
    # SEE: color_previewer()
    ranges = {'vegetation': ([35, 5, 35], [120, 140, 255]),
              'water': ([120, 35, 20], [180, 175, 255]),
              'urban': ([0, 0, 0], [255, 255, 20])
              }
    mask, masked_img = mask_color(img, ranges[selection], smoothing)
    return mask, masked_img


def ndvi(img_color, img_nir):
    nir = cv2.cvtColor(img_nir, cv2.COLOR_RGB2GRAY)
    r, g, b = cv2.split(img_color)

    num = nir.astype(float) - r.astype(float)
    den = nir.astype(float) + r.astype(float)
    den[den == 0] = np.finfo(float).eps  # very small number instead of zero

    return np.divide(num, den)


def cap(selection='vegetation', stream=False):
    if stream: stream = io.BytesIO()
    while True:
        image = np.array()
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        mask, masked_img = get_hsl_mask(image, selection, 2)
