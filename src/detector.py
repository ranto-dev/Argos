import tensorflow as tf
import cv2
import numpy as np
from src.config import MODEL_PATH, SCORE_THRESHOLD

class HumanDetector:
    def __init__(self):
        self.model = tf.saved_model.load(MODEL_PATH)

    def detect_and_draw(self, frame):
        h, w, _ = frame.shape
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_tensor = tf.convert_to_tensor(img_rgb)[tf.newaxis, ...]

        detections = self.model(input_tensor)
        boxes = detections['detection_boxes'][0].numpy()
        classes = detections['detection_classes'][0].numpy().astype(np.int32)
        scores = detections['detection_scores'][0].numpy()

        detected = False
        for i in range(len(scores)):
            if scores[i] > SCORE_THRESHOLD and classes[i] == 1:
                detected = True
                ymin, xmin, ymax, xmax = boxes[i]
                cv2.rectangle(frame, (int(xmin*w), int(ymin*h)), (int(xmax*w), int(ymax*h)), (0, 0, 255), 2)
                cv2.putText(frame, "INTRUS", (int(xmin*w), int(ymin*h)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
        
        return detected, frame