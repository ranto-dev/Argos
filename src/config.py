import os

# Chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "models/ssd_mobilenet_v2")
ALARM_PATH = os.path.join(BASE_DIR, "assets/alarm.wav")

# Paramètres Détection
SCORE_THRESHOLD = 0.5

# Config Email
EMAIL_SENDER = "rantoandrianandraina@gmail.com"
EMAIL_PASSWORD = "sejwosjexpsiabdf"
EMAIL_RECEIVER = "rguypatrickroland@gmail.com"
EMAIL_DELAY = 60