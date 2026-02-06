import cv2
import tensorflow as tf
import pygame
import threading
import os
import smtplib
import time
from email.message import EmailMessage
from utils import resize_frame

# -------------------
# CONFIGURATION
# -------------------
MODEL_PATH = "models/ssd_mobilenet_v2"
ALARM_PATH = "assets/alarm.wav"
SCORE_THRESHOLD = 0.5

# Config Email
EMAIL_SENDER = "rantoandrianandraina@gmail.com"
EMAIL_PASSWORD = "sejwosjexpsiabdf"  # Attention: bien enlever l'espace à la fin
EMAIL_RECEIVER = "rguypatrickroland@gmail.com"
EMAIL_DELAY = 60  # On passe à 60s pour éviter d'être banni par Google
last_email_time = 0

# -------------------
# CHARGEMENT MODELE
# --------------------
print("🚀 Chargement du modèle Argos...")
model = tf.saved_model.load(MODEL_PATH)
print("✅ Modèle chargé !")

# -------------------
# AUDIO
# -------------------
pygame.mixer.init()
alarm_playing = False
alarm_lock = threading.Lock()

def play_alarm():
    global alarm_playing
    with alarm_lock:
        if alarm_playing: return
        if not os.path.exists(ALARM_PATH):
            print("⚠️ Fichier audio introuvable")
            return
        pygame.mixer.music.load(ALARM_PATH)
        pygame.mixer.music.play(-1)
        alarm_playing = True

def stop_alarm():
    global alarm_playing
    with alarm_lock:
        if alarm_playing:
            pygame.mixer.music.stop()
            alarm_playing = False
            print("🔕 Alarme arrêtée manuellement")

# -------------------
# EMAIL AVEC VERROU (PROTECTION SPAM)
# -------------------
email_lock = threading.Lock()

def _send_email_task():
    """Tâche de fond pour l'envoi d'email"""
    global last_email_time
    
    # Si un autre thread est déjà en train d'envoyer, on annule celui-ci
    if not email_lock.acquire(blocking=False):
        return

    try:
        msg = EmailMessage()
        msg.set_content(f"Alerte : Une présence humaine a été détectée par Argos à {time.ctime()}")
        msg['Subject'] = "🚨 ALERTE INTRUSION - ARGOS"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        print("📧 Tentative d'envoi de l'email...")
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        
        last_email_time = time.time()
        print("✅ Email d'alerte envoyé avec succès !")
    except Exception as e:
        print(f"❌ Erreur critique email : {e}")
    finally:
        email_lock.release()

def trigger_email():
    """Vérifie le délai avant de lancer le thread d'envoi"""
    global last_email_time
    if (time.time() - last_email_time) > EMAIL_DELAY:
        threading.Thread(target=_send_email_task, daemon=True).start()

# -------------------
# DETECTION PERSONNE
# -------------------
def detect_and_draw(frame):
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    tensor = tf.convert_to_tensor(img_rgb, dtype=tf.uint8)
    tensor = tf.expand_dims(tensor, 0)

    detections = model(tensor)
    boxes = detections["detection_boxes"][0].numpy()
    classes = detections["detection_classes"][0].numpy()
    scores = detections["detection_scores"][0].numpy()

    detected = False
    h, w, _ = frame.shape

    for i in range(len(scores)):
        if scores[i] > SCORE_THRESHOLD and int(classes[i]) == 1:
            detected = True
            ymin, xmin, ymax, xmax = boxes[i]
            # Dessin des boîtes
            cv2.rectangle(frame, (int(xmin*w), int(ymin*h)), (int(xmax*w), int(ymax*h)), (0, 0, 255), 2)
    
    return detected, frame

# -------------------
# MAIN
# -------------------
def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Erreur: Caméra inaccessible")
        return

    print("🛡️ ARGOS ACTIVÉ (Q pour quitter / ESPACE pour stopper l'alarme)")

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = resize_frame(frame, width=640)
        found, frame = detect_and_draw(frame)

        if found:
            # Gestion Alarme
            threading.Thread(target=play_alarm, daemon=True).start()
            # Gestion Email avec protection
            trigger_email()

        cv2.imshow("Argos Sentinel", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '): 
            stop_alarm()
        elif key == ord('q'):
            stop_alarm()
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()