import cv2
import numpy as np
import tensorflow as tf
from utils import resize_frame

# Charger le modèle depuis le disque
model = tf.saved_model.load("models/ssd_mobilenet_v2")
print("Modèle chargé depuis le disque !")

def detect_person(frame):
    """Détecte les personnes dans une frame"""
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_tensor = tf.convert_to_tensor(img_rgb, dtype=tf.uint8)
    img_tensor = tf.expand_dims(img_tensor, 0)

    result = model(img_tensor)
    result = {key: value.numpy() for key, value in result.items()}

    height, width, _ = frame.shape
    detected = False

    # Applatir arrays pour compatibilité modèle hors ligne
    detection_classes = result['detection_classes'].squeeze()
    detection_scores = result['detection_scores'].squeeze()
    detection_boxes = result['detection_boxes'].squeeze()

    for i in range(len(detection_scores)):
        score = detection_scores[i]
        class_id = int(detection_classes[i])
        if score > 0.5 and class_id == 1:  # 1 = personne
            ymin, xmin, ymax, xmax = detection_boxes[i]
            left, right = int(xmin * width), int(xmax * width)
            top, bottom = int(ymin * height), int(ymax * height)
            detected = True
            break  # on s'arrête dès qu'on détecte une personne

    return detected

def main():
    # Ouvrir la webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Impossible d'ouvrir la webcam")
        return

    print("Appuyez sur 'q' pour quitter.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Impossible de lire la frame.")
            break

        frame = resize_frame(frame, width=640)
        detected = detect_person(frame)

        if detected:
            print("Présence détectée !")
        else:
            print("Aucune présence")

        # Afficher la frame si tu veux visualiser (optionnel)
        cv2.imshow("Webcam", frame)

        # Sortir avec la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
