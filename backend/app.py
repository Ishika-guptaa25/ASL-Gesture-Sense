# backend/app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pickle
import os

APP_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(APP_DIR, "..", "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

MODEL_PATH = os.path.join(APP_DIR, "asl_rf_model.pkl")

# Load model
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run training first.")

with open(MODEL_PATH, "rb") as f:
    clf = pickle.load(f)

@app.route("/", methods=["GET"])
def index():
    # Serve frontend index.html
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    # Serve JS/CSS from frontend folder
    return send_from_directory(FRONTEND_DIR, filename)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    if not data or "landmarks" not in data:
        return jsonify({"error": "Missing 'landmarks' in JSON body"}), 400

    landmarks = data["landmarks"]
    # Expect 63 values (21 * 3)
    if not isinstance(landmarks, list):
        return jsonify({"error": "'landmarks' must be a list"}), 400

    if len(landmarks) != 63:
        return jsonify({"error": f"Expected 63 landmark values, got {len(landmarks)}"}), 400

    # Predict
    try:
        pred = clf.predict([landmarks])[0]
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"prediction": str(pred)})

if __name__ == "__main__":
    # Run on 0.0.0.0 if you want other devices on LAN to access
    app.run(host="127.0.0.1", port=5000, debug=True)
