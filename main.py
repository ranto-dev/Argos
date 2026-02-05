import cv2
import tensorflow as tf
from utils import resize_frame
import pygame
import threading
import os

# -------------------
# CONFIG
# -------------------
MODEL_PATH = "models/ssd_mobilenet_v2"
ALARM_PATH = "assets/alarm.wav"
SCORE_THRESHOLD = 0.5  # seuil de confiance

# -------------------
# INITIALISATION
# -------------------
print("Chargement du modèle...")
model = tf.saved_model.load(MODEL_PATH)
print("Modèle chargé !")

# Initialiser pygame pour le son
pygame.mixer.init()

def play_alarm():
    """Jouer l'alarme dans un thread pour ne pas bloquer la webcam"""
    def _play():
        if os.path.exists(ALARM_PATH):
            pygame.mixer.music.load(ALARM_PATH)
            pygame.mixer.music.play()
    threading.Thread(target=_play, daemon=True).start()

# -------------------
# FONCTION DE DETECTION
# -------------------
def detect_person(frame):
    """Détecte la présence d'une personne dans une frame"""
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_tensor = tf.convert_to_tensor(img_rgb, dtype=tf.uint8)
    img_tensor = tf.expand_dims(img_tensor, 0)

    result = model(img_tensor)
    result = {key: value.numpy() for key, value in result.items()}

    detection_classes = result['detection_classes'].squeeze()
    detection_scores = result['detection_scores'].squeeze()
    detection_boxes = result['detection_boxes'].squeeze()

    for i in range(len(detection_scores)):
        score = detection_scores[i]
        class_id = int(detection_classes[i])
        if score > SCORE_THRESHOLD and class_id == 1:  # 1 = personne
            return True
    return False

# -------------------
# BOUCLE PRINCIPALE
# -------------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Impossible d'ouvrir la webcam")
        return

    print("Appuyez sur 'q' pour quitter.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, width=640)
        detected = detect_person(frame)

        if detected:
            print("Présence détectée !")
            play_alarm()

        # Afficher la webcam (optionnel)
        cv2.imshow("Webcam", frame)

        # Sortie avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------
# EXECUTION
# -------------------
if __name__ == "__main__":
    main()