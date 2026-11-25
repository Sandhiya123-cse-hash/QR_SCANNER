const video = document.getElementById("video");
const canvas = document.getElementById("canvas");
const context = canvas.getContext("2d");

const startButton = document.getElementById("startButton");
const calibrateButton = document.getElementById("calibrateButton");

const statusText = document.getElementById("status");
const resultText = document.getElementById("result");
const angleText = document.getElementById("angle");

let currentAngle = null;
let baselineAngle = null;
let cameraStarted = false;

// Normalize angle to 0...359
function normalizeAngle(angle) {
    return (angle % 360 + 360) % 360;
}

// Find the nearest 90-degree orientation
function nearestQuarterTurn(angle) {
    return normalizeAngle(Math.round(angle / 90) * 90);
}

// Calculate QR orientation from its detected corners
function getQRAngle(location) {
    const topLeft = location.topLeftCorner;
    const topRight = location.topRightCorner;

    const dx = topRight.x - topLeft.x;
    const dy = topRight.y - topLeft.y;

    const angle = Math.atan2(dy, dx) * 180 / Math.PI;

    return normalizeAngle(angle);
}

// Map rotation to A, B, C, D
function getAnswer(angle) {
    if (baselineAngle === null) {
        return "--";
    }

    const difference = normalizeAngle(angle - baselineAngle);
    const turn = nearestQuarterTurn(difference);

    if (turn === 0) return "A";
    if (turn === 90) return "B";
    if (turn === 180) return "C";
    if (turn === 270) return "D";

    return "--";
}

// Start camera
startButton.addEventListener("click", async () => {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({
            video: {
                facingMode: "environment"
            },
            audio: false
        });

        video.srcObject = stream;
        await video.play();

        cameraStarted = true;
        startButton.disabled = true;
        calibrateButton.disabled = false;

        statusText.textContent = "Camera started. Scan your QR.";
        requestAnimationFrame(scanFrame);

    } catch (error) {
        statusText.textContent =
            "Camera error: " + error.message;
    }
});

// Calibrate when QR is upright
calibrateButton.addEventListener("click", () => {
    if (currentAngle === null) {
        statusText.textContent =
            "QR not detected yet. Point the camera at the QR.";
        return;
    }

    baselineAngle = currentAngle;

    resultText.textContent = "Result: A";
    statusText.textContent =
        "Calibration complete. Upright position is A.";
});

// Read camera frames
function scanFrame() {
    if (!cameraStarted) return;

    if (video.readyState === video.HAVE_ENOUGH_DATA) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;

        context.drawImage(
            video,
            0,
            0,
            canvas.width,
            canvas.height
        );

        const imageData = context.getImageData(
            0,
            0,
            canvas.width,
            canvas.height
        );

        const code = jsQR(
            imageData.data,
            imageData.width,
            imageData.height,
            {
                inversionAttempts: "attemptBoth"
            }
        );

        if (code && code.location) {
            currentAngle = getQRAngle(code.location);

            const roundedAngle = nearestQuarterTurn(currentAngle);

            angleText.textContent =
                "Detected angle: " + roundedAngle + "°";

            if (baselineAngle === null) {
                resultText.textContent = "Result: Calibrate first";
                statusText.textContent =
                    "Keep QR upright and tap Set Current Position as A.";
            } else {
                const answer = getAnswer(currentAngle);

                resultText.textContent = "Result: " + answer;
                statusText.textContent =
                    "QR detected: " + code.data;
            }
        } else {
            statusText.textContent = "Searching for QR...";
        }
    }

    requestAnimationFrame(scanFrame);
}