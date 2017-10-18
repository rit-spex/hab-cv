import numpy as np
import cv2
from PIL import ImageGrab

def threshold(grayscaled_img,blur_radius):
    img=smooth(img,5,kind='gaussian')
    ret,th = cv2.threshold(img,125,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    return ret, th


def smooth(img,radius,kind='open'):
    kernel=np.ones((radius,radius),np.uint8)
    if kind=='gaussian':
        img=cv2.GaussianBlur(img,(radius,radius),0)
    elif kind=='open':
        img=cv2.morphologyEx(img,cv2.MORPH_OPEN,kernel)
    elif kind=='close':
        img=cv2.morphologyEx(img,cv2.MORPH_CLOSE,kernel)
    elif kind=='erode':
        img=cv2.erode(mask,kernel,iterations=1)
    elif kind=='dilate':
        img=cv2.dilate(mask,kernel,iterations=1)
    return img


def mask_color(img,dark_limit,light_limit,radius):
    hls = cv2.cvtColor(img, cv2.COLOR_BGR2HLS_FULL)
    dark_limit,light_limit = np.array(dark_limit,dtype='uint8'),np.array(light_limit,dtype='uint8')
    mask = cv2.inRange(hls,dark_limit,light_limit)
    mask=smooth(mask,radius,kind='close')
    masked_img = cv2.bitwise_and(img,img,mask=mask)
    return mask, masked_img


def main():
    sources=['file','screen']
    # TOGGLE VIEWING MODE
    source=sources[0]

    if source=='file':
        video_file = cv2.VideoCapture('images/HAB2 Complete GoPro Footage.mp4')
    while True:
        ## SCREENSHOT
        if source=='screen':
            screen = np.array(ImageGrab.grab(bbox=(350, 200, 750, 750)))
            screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)

        # FROM FILE
        if source=='file':
            if video_file.isOpened():
                isValid,screen = video_file.read()
            else:
                cv2.destroyAllWindows()
                break
            if not isValid:
                cv2.destroyAllWindows()
                break
        cv2.imshow('RGB', screen)

        # LIMITS IN HLS - Hue, Lightness, Saturation
        # range: 0 to 255
        # SEE: color_previewer()
        smoothing_amount=2
        dark_green,light_green=[35,5,35],[100,140,255]
        veg_mask,veg = mask_color(screen,dark_green,light_green,smoothing_amount)

        dark_blue,light_blue=[160 ],[245,90,100]
        cv2.imshow('mask',veg_mask)
        cv2.imshow('greens',veg)

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

def nothing(x):
    pass
def color_previewer():
    # https://docs.opencv.org/3.0-beta/doc/py_tutorials/py_gui/py_trackbar/py_trackbar.html

    # Create a black image, a window
    img = np.zeros((300,512,3), np.uint8)
    img=cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
    cv2.namedWindow('image')

    # create trackbars for color change
    cv2.createTrackbar('H','image',0,255,nothing)
    cv2.createTrackbar('L','image',0,255,nothing)
    cv2.createTrackbar('S','image',0,255,nothing)

    while(1):
        cv2.imshow('image',cv2.cvtColor(img,cv2.COLOR_HLS2BGR))

        # get current positions of four trackbars
        h = cv2.getTrackbarPos('H','image')
        l = cv2.getTrackbarPos('L','image')
        s = cv2.getTrackbarPos('S','image')

        img[:] = [h,l,s]

        if cv2.waitKey(25) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break


# color_previewer()
main()
