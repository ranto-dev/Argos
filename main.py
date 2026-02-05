import cv2
from ultralytics import YOLO

def launch_argos():
    # 1. Chargement du modèle (YOLOv8 Nano - très rapide)
    # Il va se télécharger automatiquement à la première exécution
    model = YOLO('yolov8n.pt') 

    # 2. Initialisation de la capture vidéo (0 = Webcam interne)
    cap = cv2.VideoCapture(0)

    print("--- Argos est activé et surveille ---")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # 3. Inférence : Détection avec YOLO
        # classes=[0] correspond à la classe 'person' dans le dataset COCO
        results = model(frame, classes=[0], conf=0.5, verbose=False)

        # 4. Analyse des résultats
        human_detected = False
        for r in results:
            if len(r.boxes) > 0:
                human_detected = True
                # Dessiner les boîtes de détection sur l'image
                frame = r.plot() 

        # 5. Gestion de l'alerte
        if human_detected:
            cv2.putText(frame, "ALERTE : HUMAIN DETECTE", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
            # Ici, vous pourriez ajouter : winsound.Beep(1000, 500) sous Windows
        else:
            cv2.putText(frame, "Statut: RAS", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # 6. Affichage du flux
        cv2.imshow("Argos - Systeme de Surveillance", frame)

        # Quitter avec la touche 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    launch_argos()