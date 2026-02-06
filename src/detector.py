import tensorflow as tf
import cv2
import numpy as np
from src.config import MODEL_PATH, SCORE_THRESHOLD

class HumanDetector:
    def __init__(self):
        print("🚀 Chargement du modèle Argos...")
        self.model = tf.saved_model.load(MODEL_PATH)
        print("✅ Modèle chargé !")

    def detect_and_draw(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        tensor = tf.convert_to_tensor(img_rgb, dtype=tf.uint8)
        tensor = tf.expand_dims(tensor, 0)

        detections = self.model(tensor)
        boxes = detections["detection_boxes"][0].numpy()
        classes = detections["detection_classes"][0].numpy()
        scores = detections["detection_scores"][0].numpy()

        detected = False
        h, w, _ = frame.shape

        for i in range(len(scores)):
            if scores[i] > SCORE_THRESHOLD and int(classes[i]) == 1:
                detected = True
                ymin, xmin, ymax, xmax = boxes[i]
                cv2.rectangle(frame, (int(xmin*w), int(ymin*h)), (int(xmax*w), int(ymax*h)), (0, 0, 255), 2)
        
        return detected, frame