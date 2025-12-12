import cv2
import mediapipe as mp
import numpy as np
import os
import pickle

DATASET_DIR = "dataset/asl_alphabet_train"
OUTPUT_FILE = "backend/features_labels.pkl"

MAX_IMAGES = 100   # <<––– FAST MODE (only first 100 images per class)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, max_num_hands=1)

features = []
labels = []

for label in os.listdir(DATASET_DIR):
    folder_path = os.path.join(DATASET_DIR, label)

    if not os.path.isdir(folder_path):
        continue

    print(f"\nProcessing class: {label}")

    # Process only FIRST 100 images
    img_files = os.listdir(folder_path)[:MAX_IMAGES]

    count = 0
    for img_name in img_files:
        img_path = os.path.join(folder_path, img_name)
        img = cv2.imread(img_path)

        if img is None:
            continue

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(imgRGB)

        if not results.multi_hand_landmarks:
            continue

        hand = results.multi_hand_landmarks[0]
        coords = []

        # 63 features (21 landmarks × 3 coords)
        for lm in hand.landmark:
            coords.extend([lm.x, lm.y, lm.z])

        features.append(coords)
        labels.append(label)
        count += 1

        # Show progress
        print(f"  Extracted: {count}/100", end="\r")

print("\n\n🎉 FAST MODE: Feature extraction completed!")
print(f"Total samples collected: {len(features)}")

with open(OUTPUT_FILE, "wb") as f:
    pickle.dump((features, labels), f)

print(f"Saved extracted features to {OUTPUT_FILE}")
