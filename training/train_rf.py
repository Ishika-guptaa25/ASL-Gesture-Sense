import pickle
from sklearn.ensemble import RandomForestClassifier

INPUT_FILE = "backend/features_labels.pkl"
MODEL_FILE = "backend/asl_rf_model.pkl"

with open(INPUT_FILE, "rb") as f:
    features, labels = pickle.load(f)

print("Training RandomForest model...")

clf = RandomForestClassifier(n_estimators=200)
clf.fit(features, labels)

with open(MODEL_FILE, "wb") as f:
    pickle.dump(clf, f)

print("🎉 RandomForest model saved!")
