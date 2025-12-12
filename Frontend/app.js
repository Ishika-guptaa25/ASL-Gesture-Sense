// =============================================
//  SETUP DOM ELEMENTS
// =============================================
const videoElement = document.getElementById('video');
const canvasElement = document.getElementById('overlay');
const canvasCtx = canvasElement.getContext('2d');

const predEl = document.getElementById('prediction');
const confEl = document.getElementById('confidence');

// =============================================
//  RESIZE CANVAS TO MATCH VIDEO
// =============================================
function resizeCanvas() {
  const w = videoElement.videoWidth;
  const h = videoElement.videoHeight;

  if (w > 0 && h > 0) {
    canvasElement.width = w;
    canvasElement.height = h;
  }
}

// =============================================
//  MAIN HAND RESULT CALLBACK
// =============================================
async function onResults(results) {
  resizeCanvas();
  canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);

  // If hand detected
  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    const landmarks = results.multiHandLandmarks[0];

    // 🟢 DRAW GREEN DOTS
    canvasCtx.fillStyle = "lime";
    for (const lm of landmarks) {
      canvasCtx.beginPath();
      canvasCtx.arc(
        lm.x * canvasElement.width,
        lm.y * canvasElement.height,
        5,
        0,
        2 * Math.PI
      );
      canvasCtx.fill();
    }

    // 🔴 DRAW RED CONNECTIONS
    window.drawConnectors(
      canvasCtx,
      landmarks,
      window.HAND_CONNECTIONS,
      { color: "#FF0000", lineWidth: 2 }
    );

    // BUILD FEATURE VECTOR
    const flat = [];
    for (const lm of landmarks) {
      flat.push(lm.x, lm.y, lm.z);
    }

    // THROTTLE BACKEND CALLS
    if (!window._lastSent || Date.now() - window._lastSent > 120) {
      window._lastSent = Date.now();

      try {
        const response = await fetch("/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ landmarks: flat })
        });

        if (response.ok) {
          const data = await response.json();

          // UPDATED CONFIDENCE HANDLING
          predEl.textContent = data.prediction ?? "—";

          if (data.confidence !== undefined && data.confidence !== null) {
            confEl.textContent = data.confidence;
          } else {
            confEl.textContent = "—";
          }

        } else {
          predEl.textContent = "Error";
          confEl.textContent = "—";
        }

      } catch (err) {
        console.error("Prediction error:", err);
      }
    }
  }
}

// =============================================
//  SETUP MEDIAPIPE HANDS
// =============================================
const hands = new Hands({
  locateFile: (file) => {
    return `https://cdn.jsdelivr.net/npm/@mediapipe/hands@0.4/${file}`;
  }
});

hands.setOptions({
  maxNumHands: 1,
  modelComplexity: 1,
  minDetectionConfidence: 0.5,
  minTrackingConfidence: 0.5
});

hands.onResults(onResults);

// =============================================
//  START CAMERA
// =============================================
const camera = new Camera(videoElement, {
  onFrame: async () => {
    await hands.send({ image: videoElement });
  },
  width: 640,
  height: 480
});

camera.start();
