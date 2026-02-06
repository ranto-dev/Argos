import cv2
import threading
import time
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.detector import HumanDetector
from src.alert_system import AlertSystem

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Initialisation des composants
detector = HumanDetector()
alerts = AlertSystem()

# Variables d'état
monitoring_active = False
last_event = "Système prêt"

def get_frames():
    global monitoring_active, last_event
    cap = cv2.VideoCapture(0)
    
    while True:
        success, frame = cap.read()
        if not success:
            break
        
        frame = cv2.resize(frame, (640, 480))
        
        if monitoring_active:
            found, annotated_frame = detector.detect_and_draw(frame)
            if found:
                last_event = "INTRUSION DÉTECTÉE"
                threading.Thread(target=alerts.play_alarm, daemon=True).start()
                alerts.trigger_email()
                display_frame = annotated_frame
            else:
                display_frame = frame
        else:
            # Mode veille : noir et blanc partiel pour économiser du CPU visuel
            display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            display_frame = cv2.cvtColor(display_frame, cv2.COLOR_GRAY2BGR)
            cv2.putText(display_frame, "STANDBY MODE", (200, 240), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        _, buffer = cv2.imencode('.jpg', display_frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(get_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/toggle")
async def toggle():
    global monitoring_active, last_event
    monitoring_active = not monitoring_active
    if not monitoring_active:
        alerts.reset_alert_cycle()
        alerts.stop_alarm()
        last_event = "Surveillance désactivée"
    else:
        last_event = "Surveillance activée"
    return {"status": "active" if monitoring_active else "paused"}

@app.get("/get_logs")
async def get_logs():
    global last_event
    # On renvoie l'événement actuel
    return {"event": last_event}

@app.get("/stop_alarm")
async def stop_alarm():
    global last_event
    alerts.stop_alarm()
    last_event = "Alarme coupée manuellement"
    return {"status": "stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)