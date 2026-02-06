import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models/ssd_mobilenet_v2")
ALARM_PATH = os.path.join(BASE_DIR, "assets/alarm.wav")

SCORE_THRESHOLD = 0.5

# Configuration Email
EMAIL_SENDER = "rantoandrianandraina@gmail.com"
EMAIL_PASSWORD = "sejwosjexpsiabdf"
EMAIL_RECEIVER = "rguypatrickroland@gmail.com"