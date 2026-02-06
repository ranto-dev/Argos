# ARGOS SENTINEL

## About

**Argos Sentinel** is a high-performance, AI-driven security surveillance system designed to run on local hardware (optimized for Fedora Linux). It transforms a standard webcam into an intelligent security monitor capable of detecting human intrusions in real-time. By combining Computer Vision with a modern web interface, Argos provides a seamless and immersive security experience directly in your browser.

## Key Features

- **Real-time AI Detection**: Uses the SSD Mobilenet V2 model (TensorFlow) to identify human presence with high precision.
- **Immersive Web Dashboard**: A futuristic "Command Center" UI powered by FastAPI and Three.js for 3D background animations.
- **Smart Alert System**:
- **Audio Alarm**: Triggered immediately upon detection using Pygame.
- **Reasonable Email Notifications**: A "Burst & Cool-down" logic that sends 3 rapid alerts to ensure the owner is notified, then throttles to prevent spam.

- **Live Event Logging**: A scrolling real-time console that tracks every system action and detection event.
- **Hardware Optimized**: Designed to run efficiently on CPU (Intel i5/i7) using a lightweight web-streaming approach.

## Technologies

- **Backend**: Python 3.11, FastAPI, Uvicorn.
- **Computer Vision**: OpenCV (cv2), TensorFlow 2.x (Object Detection API).
- **Frontend**: HTML5, CSS3 (Modern Grid/Flexbox), JavaScript (ES6+).
- **Graphics & Sound**: Three.js (3D particles), Pygame (Audio processing).
- **Communication**: SMTP_SSL (Gmail API) for secure alerts.

## How It Works?

The system operates through a synchronized three-layer architecture:

1. **The Capture Layer**: The system accesses the local webcam via OpenCV. Frames are captured and normalized (resized to ) to maintain high processing speeds on CPU-bound machines.
2. **The Intelligence Layer**: Each frame is passed through the **SSD Mobilenet V2** neural network. If the model identifies a "Person" (COCO Class 1) with a confidence score , an intrusion state is triggered.
3. **The Action Layer**:

- The backend initiates a non-blocking thread to play the siren.
- The Email logic checks the `last_email_time`; if valid, it dispatches a secure alert via Google's SMTP servers.
- The Web UI receives the video stream via a `Multipart` Response and updates the log console via asynchronous polling.

### Installation Quick Start

```bash
# Clone the repository
git clone git@github.com:ranto-dev/Argos.git Argos

# Install dependencies
pip install fastapi uvicorn tensorflow opencv-python pygame jinja2

# move into the derectory
cd Argos

# Run the system
python main.py

```

_Access the dashboard at `http://localhost:8000_`

## Author

**ranto-dev** _Web Developer & AI Integrator_ Specialized in Python-based security solutions and modern web architectures.
