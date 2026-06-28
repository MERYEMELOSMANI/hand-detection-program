# Computer Vision Gesture Suite

A collection of real-time hand gesture applications built with Python, OpenCV, and Google MediaPipe. All demos run from your webcam with no additional hardware.

---

## Demos

| File | Demo | Description |
|---|---|---|
| `P1.py` | Hand Landmark Detection | Tracks all 21 hand landmarks in real time with FPS counter |
| `P2.py` | Rock Paper Scissors | Play Rock Paper Scissors against the computer using hand gestures |
| `P2_ColorBombs.py` | Color Bombs | Hand movement triggers particle explosions on screen |
| `P2_ColorMixer.py` | Color Mixer | Blend colors by moving hands across zones |
| `P2_Magic.py` | Magic Effects | Visual magic effects driven by finger positions |
| `P3_AirTextWriter.py` | Air Text Writer | Write text in the air using your index finger |
| `P3_MAGIC.py` | Air Text (Magic Mode) | Air writing with enhanced visual effects |
| `P4_HolographicMatrix.py` | Holographic Matrix | Futuristic holographic text creation with gesture controls and particle effects |
| `P5_NeuralStudio.py` | Neural Studio | AI-style visual canvas controlled by hand pose |
| `P6_GesturePainter.py` | Gesture Painter | Draw on screen with finger gestures, multiple colors |
| `P7_DualHandResizer.py` | Dual Hand Text Resizer | Scale text up/down using a two-hand pinch-stretch gesture |
| `P8_ThumbIndexResizer.py` | Precision Resizer | Fine-grained text scaling using thumb + index finger distance |

---

## Core Module

**`HandTrackingModule.py`** — reusable hand tracking class used across all demos:
- Detects up to 2 hands simultaneously
- Returns landmark coordinates normalized or in pixel space
- Finger state detection (up/down) for gesture logic
- Configurable confidence thresholds

---

## Requirements

- Python 3.7+
- Webcam

```bash
pip install -r requirements.txt
```

Dependencies: `opencv-python`, `mediapipe`, `numpy`

---

## Usage

Each demo is self-contained. Run any one:

```bash
python P1.py          # Basic hand landmarks
python P2.py          # Rock Paper Scissors
python P4_HolographicMatrix.py   # Holographic text
python P6_GesturePainter.py      # Gesture painter
```

**Controls** (all demos): press `q` to quit.

---

## How It Works

```
Webcam frame
    → BGR to RGB conversion
    → MediaPipe Hands model (21 landmarks per hand)
    → HandTrackingModule (landmark coordinates + finger states)
    → Demo-specific gesture logic
    → OpenCV visualization → display
```

MediaPipe identifies 21 anatomical landmarks per hand (wrist, 4 joints per finger). Each demo maps specific landmark positions or finger states to interactive behaviors.

---

## Tips for Best Performance

- Use a plain background and consistent lighting
- Keep hands 30–80 cm from camera
- 30–60 FPS expected on standard hardware

---

## Author

**MERYEM EL OSMANI**

---

## License

MIT License
