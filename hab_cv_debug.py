import numpy as np
import cv2
from PIL import ImageGrab

def threshold(grayscaled_img, blur_radius):
    img = smooth(img, 5, kind='gaussian')
    ret, th = cv2.threshold(img, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return ret, th


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


def hsl_mask(img, selection='vegetation', smoothing=2):
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
    r = cv2.cvtColor(img_color, cv2.COLOR_RGB2GRAY)

    num = nir.astype(float) - r.astype(float)
    den = nir.astype(float) + r.astype(float)
    den[den == 0] = np.finfo(float).eps  # very small number instead of zero

    return np.divide(num, den)


def cap(source='screen', selection='vegetation'):
    if source == 'file':
        video_file = cv2.VideoCapture('images/HAB2 Complete GoPro Footage.mp4')
    while True:
        ## SCREENSHOT
        if source == 'screen':
            screen = np.array(ImageGrab.grab(bbox=(350, 200, 750, 750)))
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        # FROM FILE
        if source == 'file':
            if video_file.isOpened():
                isValid, screen = video_file.read()
            else:
                cv2.destroyAllWindows()
                break
            if not isValid:
                cv2.destroyAllWindows()
                break

        mask, masked_img = hsl_mask(screen, selection, 2)
        cv2.imshow('RGB', screen)
        cv2.imshow(selection + ' mask', mask)
        cv2.imshow(selection, masked_img)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

rgb=cv2.imread('images/RGB-test.jpg')
ir=cv2.imread('images/IR-test.jpg')
while(True):
    cv2.imshow('rgb', cv2.cvtColor(rgb,cv2.COLOR_RGB2BGR))
    cv2.imshow('ir', cv2.cvtColor(ir,cv2.COLOR_RGB2BGR))
    cv2.imshow('ndvi',ndvi(rgb,ir))

    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
# # TOGGLE VIEWING MODE
# source = 'screen'  # or 'file' or 'picamera'
# selection = 'vegetation'
# cap(source, selection)