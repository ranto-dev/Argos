import cv2
import threading
from src.detector import HumanDetector
from src.alert_system import AlertSystem
from src.utils import resize_frame

def main():
    detector = HumanDetector()
    alerts = AlertSystem()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Erreur: Caméra inaccessible")
        return

    print("🛡️ ARGOS ACTIVÉ (Q pour quitter / ESPACE pour stopper l'alarme)")

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = resize_frame(frame, width=640)
        found, frame = detector.detect_and_draw(frame)

        if found:
            threading.Thread(target=alerts.play_alarm, daemon=True).start()
            alerts.trigger_email()

        cv2.imshow("Argos Sentinel", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '): 
            alerts.stop_alarm()
        elif key == ord('q'):
            alerts.stop_alarm()
            break

    cap.release()
    cv2.destroyAllWindows()