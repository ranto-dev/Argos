import cv2
import tensorflow as tf
import pygame
import threading
import os
from utils import resize_frame

# -------------------
# CONFIGURATION
# -------------------
MODEL_PATH = "models/ssd_mobilenet_v2"
ALARM_PATH = "assets/alarm.wav"
SCORE_THRESHOLD = 0.5

# -------------------
# CHARGEMENT MODELE
# -------------------
print("Chargement du modèle...")
model = tf.saved_model.load(MODEL_PATH)
print("Modèle chargé !")

# -------------------
# AUDIO
# -------------------
pygame.mixer.init()
alarm_playing = False
alarm_lock = threading.Lock()

def play_alarm():
    global alarm_playing
    with alarm_lock:
        if alarm_playing:
            return
        if not os.path.exists(ALARM_PATH):
            print("Fichier audio introuvable !")
            return

        pygame.mixer.music.load(ALARM_PATH)
        pygame.mixer.music.play(-1)  # boucle infinie
        alarm_playing = True
        print("🔔 Alarme déclenchée")

def stop_alarm():
    global alarm_playing
    with alarm_lock:
        if alarm_playing:
            pygame.mixer.music.stop()
            alarm_playing = False
            print("🔕 Alarme arrêtée")

# -------------------
# DETECTION PERSONNE
# -------------------
def detect_person(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    tensor = tf.convert_to_tensor(img_rgb, dtype=tf.uint8)
    tensor = tf.expand_dims(tensor, 0)

    detections = model(tensor)
    detections = {k: v.numpy() for k, v in detections.items()}

    classes = detections["detection_classes"][0]
    scores = detections["detection_scores"][0]

    for i in range(len(scores)):
        if scores[i] > SCORE_THRESHOLD and int(classes[i]) == 1:
            return True
    return False

# -------------------
# MAIN
# -------------------
def main():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Impossible d'accéder à la webcam")
        return

    print("Appuyez sur ESPACE pour arrêter l'alarme")
    print("Appuyez sur Q pour quitter")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = resize_frame(frame, width=640)

        if detect_person(frame):
            threading.Thread(target=play_alarm, daemon=True).start()

        cv2.imshow("Detection de presence", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  # ESPACE
            stop_alarm()

        elif key == ord('q'):
            stop_alarm()
            break

    cap.release()
    cv2.destroyAllWindows()

# -------------------
# EXECUTION
# -------------------
if __name__ == "__main__":
    main()
