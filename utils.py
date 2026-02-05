import cv2

def resize_frame(frame, width=640):
    """
    Redimensionne l'image tout en gardant le ratio
    """
    h, w = frame.shape[:2]
    ratio = width / w
    return cv2.resize(frame, (width, int(h * ratio)))
