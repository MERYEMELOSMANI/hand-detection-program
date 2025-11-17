# Importation des bibliothèques nécessaires
import cv2  # OpenCV pour traitement d'image et vidéo
import mediapipe as mp  # MediaPipe de Google pour détection des mains
import time  # Pour calculer le FPS (images par seconde)

# Initialisation de la capture vidéo (webcam)
cap = cv2.VideoCapture(0)  # 0 = première caméra disponible

# Variables pour calculer le FPS
pTime = 0  # Temps précédent
cTime = 0  # Temps actuel

# Configuration de MediaPipe pour la détection des mains
mpHands = mp.solutions.hands  # Module de détection des mains
hands = mpHands.Hands()  # Créer un objet de détection des mains
mpDraw = mp.solutions.drawing_utils  # Utilitaires pour dessiner les landmarks

# Boucle principale pour traiter chaque frame de la vidéo
while True:
    # Capture une image de la webcam
    success, img = cap.read()  # success = booléen, img = image capturée
    
    # Conversion de l'image de BGR (Blue-Green-Red) vers RGB (Red-Green-Blue)
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)  # MediaPipe utilise RGB
    
    # Détection des mains dans l'image
    results = hands.process(imgRGB)  # Traite l'image et détecte les mains
    
    # Affiche les résultats de détection dans la console (debug)
    print(results.multi_hand_landmarks)
    
    # Si des mains sont détectées
    if results.multi_hand_landmarks:
        # Parcourir chaque main détectée
        for handLms in results.multi_hand_landmarks:
            # Parcourir chaque point de repère (landmark) de la main
            for id, lm in enumerate(handLms.landmark):
                # id = numéro du point (0-20), lm = coordonnées du point
                #print(id,lm)  # Ligne commentée pour debug
                
                # Obtenir les dimensions de l'image
                h, w, c = img.shape  # h=hauteur, w=largeur, c=canaux de couleur
                
                # Convertir les coordonnées relatives (0-1) en pixels
                cx, cy = int(lm.x*w), int(lm.y*h)  # cx,cy = coordonnées en pixels
                #print(id, cx, cy)  # Ligne commentée pour debug
                
                # Dessiner un cercle violet sur chaque point de repère
                #if id == 4:  # Ligne commentée - ne dessine que le pouce
                cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)  # Cercle violet rempli
            
            # Dessiner les connexions entre les points (squelette de la main)
            mpDraw.draw_landmarks(img,handLms,mpHands.HAND_CONNECTIONS)
    
    # Calcul du FPS (images par seconde)
    cTime = time.time()  # Obtenir le temps actuel
    fps = 1/(cTime - pTime)  # Calculer FPS = 1 / temps écoulé
    pTime = cTime  # Mémoriser le temps actuel pour le prochain calcul
    
    # Afficher le FPS sur l'image
    cv2.putText(img, f'FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 0, 255), 3)
    # (image, texte, position, police, taille, couleur, épaisseur)
    
    # Afficher l'image dans une fenêtre
    cv2.imshow("Image", img)  # Nom de la fenêtre = "Image"
    
    # Vérifier si l'utilisateur a appuyé sur 'q' pour quitter
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Sortir de la boucle

# Nettoyage : libérer la caméra et fermer les fenêtres
cap.release()  # Libérer la ressource caméra
cv2.destroyAllWindows()  # Fermer toutes les fenêtres OpenCV
    









"""# Initialize MediaPipe hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Create a resizable window
cv2.namedWindow("Image", cv2.WINDOW_NORMAL)

while True:
    success, img = cap.read()
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)
    
    # Draw hand landmarks
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
    
    cv2.imshow("Image", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()"""
    


