import pygame
import threading
import os
import smtplib
import time
from email.message import EmailMessage
from src.config import ALARM_PATH, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER, EMAIL_DELAY

class AlertSystem:
    def __init__(self):
        pygame.mixer.init()
        self.alarm_playing = False
        self.alarm_lock = threading.Lock()
        self.email_lock = threading.Lock()
        self.last_email_time = 0

    def play_alarm(self):
        with self.alarm_lock:
            if self.alarm_playing: return
            if not os.path.exists(ALARM_PATH): return
            pygame.mixer.music.load(ALARM_PATH)
            pygame.mixer.music.play(-1)
            self.alarm_playing = True

    def stop_alarm(self):
        with self.alarm_lock:
            if self.alarm_playing:
                pygame.mixer.music.stop()
                self.alarm_playing = False

    def trigger_email(self):
        current_time = time.time()
        if (current_time - self.last_email_time) > EMAIL_DELAY:
            if self.email_lock.acquire(blocking=False):
                threading.Thread(target=self._send_email_task, daemon=True).start()

    def _send_email_task(self):
        try:
            msg = EmailMessage()
            msg.set_content(f"Alerte : Présence humaine détectée par Argos à {time.ctime()}")
            msg['Subject'] = "🚨 ALERTE INTRUSION - ARGOS"
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
            
            self.last_email_time = time.time()
            print("📧 Email d'alerte envoyé !")
        except Exception as e:
            print(f"❌ Erreur email : {e}")
        finally:
            self.email_lock.release()