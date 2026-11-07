# Hand Tracking and Gesture Volume Control

Control your computer's volume with your hand. A webcam tracks your thumb and index finger using **OpenCV** and **MediaPipe**, and the distance between the two fingertips sets the system volume.

The project has two parts:

- **`HandTracking.py`**: a reusable hand detector module (`handDetector` class) that can also run on its own as a demo.
- **`VolumeControl.py`**: uses the detector and **pycaw** to change the Windows system volume with a pinch gesture.

> **Platform:** Volume control uses `pycaw`, which works on **Windows only**. `HandTracking.py` runs on any OS with a webcam.

## Features

- Real-time hand detection and 21-point landmark tracking
- Thumb-to-index distance mapped to a 0-100% volume level
- On-screen volume bar, percentage and FPS counter
- Volume snaps in steps to avoid jitter
- Clean, reusable `handDetector` class for other gesture projects

## How it works

1. OpenCV captures frames from the webcam.
2. MediaPipe Hands finds the hand and returns 21 landmarks.
3. Landmark **4** (thumb tip) and landmark **8** (index fingertip) are read in pixel coordinates.
4. The distance between them is calculated with `math.hypot`.
5. `numpy.interp` maps that distance (default 32 to 269 px) to 0-100%.
6. `pycaw` sets the system volume with `SetMasterVolumeLevelScalar`.

## Project structure

```
.
├── HandTracking.py     # handDetector class + standalone demo
├── VolumeControl.py    # gesture volume control
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

`requirements.txt`:

```
opencv-python>=4.8.0,<4.12
numpy>=1.26.0,<2
mediapipe==0.10.21
pycaw; sys_platform == "win32"
comtypes; sys_platform == "win32"
```

`mediapipe` is pinned to `0.10.21` because newer releases removed the legacy `mp.solutions` API used here.

## Usage

**Hand tracking demo** (shows landmarks and prints the thumb tip position):

```bash
python HandTracking.py
```

**Gesture volume control:**

```bash
python VolumeControl.py
```

- Show your hand to the camera.
- Move your **thumb and index finger apart** to raise the volume, and **together** to lower it.
- Press **q** in the video window to quit.

## Using the detector in your own code

```python
import cv2
import HandTracking as htm

detector = htm.handDetector(detectionCon=0.7)
cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break
    img = detector.findHands(img)
    lmlist = detector.findPosition(img, handNo=0, draw=False)
    if lmlist:
        print(lmlist[8])      # [id, x, y] of the index fingertip
    cv2.imshow("Demo", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
```

## Configuration

At the top of `VolumeControl.py`:

| Setting | Default | Meaning |
|---|---|---|
| `wCam, hCam` | `640, 480` | Camera resolution |
| `MIN_LEN, MAX_LEN` | `32, 269` | Thumb-index distance range in pixels (calibrate for your camera distance) |
| `SMOOTHNESS` | `5` | Volume snaps to multiples of this percent |

To calibrate, temporarily add `print(int(length))` inside the loop, note your smallest and largest finger distance, and update `MIN_LEN` and `MAX_LEN`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `module 'mediapipe' has no attribute 'solutions'` | Install the pinned version: `pip install mediapipe==0.10.21` |
| `no attribute 'GetMessageClass'` | Protobuf is outdated: `pip install --upgrade "protobuf>=4.25.3,<5"` |
| `AttributeError` from pycaw on `Activate` | Use the current `VolumeControl.py`, which supports both old and new pycaw |
| Camera does not open | Close other apps using the webcam, or change `VideoCapture(0)` to `1` |
| Volume too sensitive or too slow | Adjust `MIN_LEN` and `MAX_LEN` |
| MediaPipe log warnings in the terminal | Harmless; they can be ignored |

## Possible improvements

- Mute and unmute with a fist or pinch gesture
- Support for both hands (separate volume and brightness control)
- Smooth the volume with a moving average
- Port to the MediaPipe Tasks API (`HandLandmarker`) to use the latest MediaPipe

## Tech stack

Python, OpenCV, MediaPipe, NumPy, pycaw

## License

MIT