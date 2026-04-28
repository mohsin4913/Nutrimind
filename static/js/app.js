let simulatedSteps = 0;
let walkInterval = null;
let motionEnabled = false;
let lastMagnitude = null;
let stepCooldown = 0;

function getNumber(value, fallback = 0) {
    const parsed = parseInt(value, 10);
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : fallback;
}

function updateStepUI() {
    const liveStepCount = document.getElementById('liveStepCount');
    const stepsInput = document.getElementById('stepsInput');
    const stepsSyncInput = document.getElementById('stepsSyncInput');

    if (liveStepCount) liveStepCount.textContent = simulatedSteps.toLocaleString();
    if (stepsInput) stepsInput.value = simulatedSteps;
    if (stepsSyncInput) stepsSyncInput.value = simulatedSteps;
}

function setMessage(message) {
    const box = document.getElementById('stepTrackerMessage');
    if (box) box.textContent = message;
}

function toggleStepPreview() {
    const button = document.getElementById('simulateWalkBtn');
    if (!button) return;

    if (walkInterval) {
        clearInterval(walkInterval);
        walkInterval = null;
        button.textContent = 'Start Step Preview';
        setMessage('Step preview paused. Save or sync the current value when ready.');
        return;
    }

    walkInterval = window.setInterval(() => {
        const increment = Math.floor(Math.random() * 5) + 2;
        simulatedSteps += increment;
        updateStepUI();
    }, 700);

    button.textContent = 'Pause Step Preview';
    setMessage('Step preview is active. Steps are increasing for presentation mode.');
}

function resetSteps() {
    if (walkInterval) {
        clearInterval(walkInterval);
        walkInterval = null;
        const button = document.getElementById('simulateWalkBtn');
        if (button) button.textContent = 'Start Step Preview';
    }
    simulatedSteps = 0;
    updateStepUI();
    setMessage('Counter reset successfully.');
}

function handleMotion(event) {
    if (!motionEnabled || !event.accelerationIncludingGravity) return;

    const { x = 0, y = 0, z = 0 } = event.accelerationIncludingGravity;
    const magnitude = Math.sqrt(x * x + y * y + z * z);

    if (lastMagnitude === null) {
        lastMagnitude = magnitude;
        return;
    }

    const delta = Math.abs(magnitude - lastMagnitude);
    lastMagnitude = magnitude;

    if (stepCooldown > 0) {
        stepCooldown -= 1;
        return;
    }

    if (delta > 1.8) {
        simulatedSteps += 1;
        stepCooldown = 3;
        updateStepUI();
    }
}

async function enableMotionTracking() {
    try {
        if (motionEnabled) {
            setMessage('Mobile motion tracking is already enabled.');
            return;
        }

        if (typeof DeviceMotionEvent === 'undefined') {
            setMessage('Device motion is not supported on this browser. Use step preview on laptop.');
            return;
        }

        if (typeof DeviceMotionEvent.requestPermission === 'function') {
            const permission = await DeviceMotionEvent.requestPermission();
            if (permission !== 'granted') {
                setMessage('Motion permission was denied. Use step preview instead.');
                return;
            }
        }

        motionEnabled = true;
        window.addEventListener('devicemotion', handleMotion);
        setMessage('Mobile motion tracking enabled. Walk with your phone to count steps. HTTPS may be required on some phones.');
    } catch (error) {
        setMessage('Unable to enable motion tracking. Use step preview instead.');
        console.error(error);
    }
}

function fadeFlashMessages() {
    window.setTimeout(() => {
        document.querySelectorAll('.flash').forEach((flash) => {
            flash.style.opacity = '0.92';
        });
    }, 3500);
}

window.addEventListener('DOMContentLoaded', () => {
    const stepsInput = document.getElementById('stepsInput');

    if (stepsInput) {
        const serverSteps = getNumber(stepsInput.value, 0);
        simulatedSteps = serverSteps;
        updateStepUI();
        stepsInput.addEventListener('input', () => {
            simulatedSteps = getNumber(stepsInput.value, 0);
            updateStepUI();
        });
    }

    const simulateBtn = document.getElementById('simulateWalkBtn');
    const resetBtn = document.getElementById('resetStepsBtn');
    const mobileBtn = document.getElementById('mobileTrackingBtn');

    if (simulateBtn) simulateBtn.addEventListener('click', toggleStepPreview);
    if (resetBtn) resetBtn.addEventListener('click', resetSteps);
    if (mobileBtn) mobileBtn.addEventListener('click', enableMotionTracking);

    fadeFlashMessages();
});
