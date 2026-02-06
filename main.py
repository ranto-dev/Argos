import cv2
import threading
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from src.detector import HumanDetector
from src.alert_system import AlertSystem

app = FastAPI()
templates = Jinja2Templates(directory="templates")

detector = HumanDetector()
alerts = AlertSystem()
monitoring_active = False

def get_frames():
    global monitoring_active
    cap = cv2.VideoCapture(0)
    while True:
        success, frame = cap.read()
        if not success: break
        
        if monitoring_active:
            frame = cv2.resize(frame, (640, 480))
            found, frame = detector.detect_and_draw(frame)
            if found:
                threading.Thread(target=alerts.play_alarm, daemon=True).start()
                alerts.trigger_email()
        else:
            frame = cv2.resize(frame, (640, 480))
            cv2.putText(frame, "MODE VEILLE", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
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
    global monitoring_active
    monitoring_active = not monitoring_active
    if not monitoring_active:
        alerts.reset_alert_cycle()
        alerts.stop_alarm()
    return {"status": "active" if monitoring_active else "paused"}

@app.get("/stop_alarm")
async def stop_alarm():
    alerts.stop_alarm()
    return {"status": "alarm_stopped"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)