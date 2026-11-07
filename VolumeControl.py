import math
import time
from ctypes import cast, POINTER

import cv2
import numpy as np
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

import HandTracking as htm

###################
wCam, hCam = 640, 480       # camera width, height
MIN_LEN, MAX_LEN = 32, 269  # thumb-index distance range in pixels (calibrate for your setup)
SMOOTHNESS = 5              # volume snaps to multiples of this percent (reduces jitter)
###################

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, wCam)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, hCam)

detector = htm.handDetector(detectionCon=0.7)


def get_volume_interface():
    """Return the system volume interface; works with old and new pycaw."""
    device = AudioUtilities.GetSpeakers()
    if hasattr(device, "EndpointVolume"):          # newer pycaw
        return device.EndpointVolume
    interface = device.Activate(                    # older pycaw
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


volume = get_volume_interface()

volBar = 400
volPer = 0
pTime = 0

while True:
    success, img = cap.read()
    if not success:
        print("Could not read from camera")
        break

    img = detector.findHands(img)
    lmlist = detector.findPosition(img, draw=False)

    if len(lmlist) != 0:
        # landmark 4 = thumb tip, landmark 8 = index finger tip
        x1, y1 = lmlist[4][1], lmlist[4][2]
        x2, y2 = lmlist[8][1], lmlist[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(img, (x1, y1), 8, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 8, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
        cv2.circle(img, (cx, cy), 8, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)

        # map finger distance to bar position and percent (values are clamped automatically)
        volBar = np.interp(length, [MIN_LEN, MAX_LEN], [400, 150])
        volPer = np.interp(length, [MIN_LEN, MAX_LEN], [0, 100])

        # snap to steps so the volume does not jitter
        volPer = SMOOTHNESS * round(volPer / SMOOTHNESS)

        # scalar 0.0-1.0 matches the percentage shown (the dB scale is non-linear)
        volume.SetMasterVolumeLevelScalar(volPer / 100, None)

        if length < MIN_LEN:
            cv2.circle(img, (cx, cy), 12, (0, 255, 0), cv2.FILLED)

    # volume bar
    cv2.rectangle(img, (50, 150), (80, 400), (250, 0, 1), 2)
    cv2.rectangle(img, (50, int(volBar)), (80, 400), (250, 0, 1), cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450),
                cv2.FONT_HERSHEY_PLAIN, 1.5, (253, 0, 0), 2)

    # FPS
    cTime = time.time()
    fps = 1 / max(cTime - pTime, 1e-6)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(fps)}', (40, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    cv2.imshow('Volume Control', img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()