import cv2
import mediapipe as mp
import pickle

MODEL_PATH = "backend/asl_rf_model.pkl"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

print("🎥 Starting Webcam... Press 'q' to quit!")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        hand = results.multi_hand_landmarks[0]

        coords = []
        for lm in hand.landmark:
            coords.extend([lm.x, lm.y, lm.z])

        pred = model.predict([coords])[0]

        cv2.putText(frame, pred, (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)

        mp_draw.draw_landmarks(frame, hand, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("ASL Detection (Mediapipe + RF)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
