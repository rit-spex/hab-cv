import cv2
import numpy as np

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
