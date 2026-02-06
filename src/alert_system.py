import pygame
import smtplib
import time
import threading
from email.message import EmailMessage
from src.config import ALARM_PATH, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

class AlertSystem:
    def __init__(self):
        pygame.mixer.init()
        self.alarm_playing = False
        self.last_email_time = 0
        self.alert_count = 0 

    def play_alarm(self):
        if not self.alarm_playing:
            pygame.mixer.music.load(ALARM_PATH)
            pygame.mixer.music.play(-1)
            self.alarm_playing = True

    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.alarm_playing = False

    def trigger_email(self):
        current_time = time.time()
        # Rafale : 30s pour les 3 premiers, puis 5 minutes (300s)
        delay = 30 if self.alert_count < 3 else 300

        if (current_time - self.last_email_time) > delay:
            self.alert_count += 1
            self.last_email_time = current_time
            threading.Thread(target=self._send_email, daemon=True).start()

    def _send_email(self):
        try:
            msg = EmailMessage()
            msg.set_content(f"Alerte n°{self.alert_count} : Intrusion détectée à {time.ctime()}")
            msg['Subject'] = f"🚨 ALERTE ARGOS #{self.alert_count}"
            msg['From'] = EMAIL_SENDER
            msg['To'] = EMAIL_RECEIVER

            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_SENDER, EMAIL_PASSWORD)
                smtp.send_message(msg)
            print(f"Email #{self.alert_count} envoyé.")
        except Exception as e:
            print(f"Erreur Email: {e}")

    def reset_alert_cycle(self):
        self.alert_count = 0
        self.last_email_time = 0