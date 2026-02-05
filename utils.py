# utils.py
import cv2

def resize_frame(frame, width=None, height=None):
    h, w = frame.shape[:2]
    if width is None and height is None:
        return frame
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))
    return cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
