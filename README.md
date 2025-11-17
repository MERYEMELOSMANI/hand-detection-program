# 🖐️ Hand Detection Program

**A comprehensive computer vision project for real-time hand detection and tracking using Python, OpenCV, and MediaPipe.**

## 🌟 Overview

This Hand Detection Program demonstrates advanced computer vision capabilities by detecting and tracking hand landmarks in real-time using your webcam. Built with Google's MediaPipe framework and OpenCV, it provides accurate hand tracking with detailed landmark visualization.

## ✨ Features

- **Real-time Hand Detection**: Detects and tracks hands in live video feed
- **21 Hand Landmarks**: Tracks all 21 anatomical landmarks on each hand
- **Visual Feedback**: 
  - Purple circles on each landmark point
  - Skeletal connections between landmarks
  - Real-time FPS display
- **Multi-hand Support**: Can detect multiple hands simultaneously
- **Detailed French Comments**: Fully commented code in French for educational purposes

## 📋 Requirements

- Python 3.7+
- OpenCV (`opencv-python`)
- MediaPipe (`mediapipe`)
- Webcam/Camera device

## 🚀 Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/yourusername/hand-detection-program.git
   cd hand-detection-program
   ```

2. **Install required packages:**
   ```bash
   pip install opencv-python mediapipe
   ```

## 💻 Usage

1. **Run the hand detection program:**
   ```bash
   python P1.py
   ```

2. **Controls:**
   - Position your hand in front of the camera
   - Press 'q' to quit the application
   - The program will display:
     - Purple circles on hand landmarks
     - White lines connecting the landmarks
     - FPS counter in the top-left corner

## 🧠 How It Works

### Hand Landmark Detection
The program uses MediaPipe's hand detection model which identifies 21 key landmarks on each hand:

- **Thumb**: 5 landmarks (0-4)
- **Index Finger**: 4 landmarks (5-8)
- **Middle Finger**: 4 landmarks (9-12)
- **Ring Finger**: 4 landmarks (13-16)
- **Pinky**: 4 landmarks (17-20)

### Technical Process
1. **Video Capture**: Captures frames from the default camera
2. **Color Conversion**: Converts BGR to RGB for MediaPipe processing
3. **Hand Detection**: Uses MediaPipe to detect hand landmarks
4. **Visualization**: Draws landmarks and connections on the original frame
5. **FPS Calculation**: Displays real-time performance metrics

## 🛠️ Technical Specifications

- **Framework**: MediaPipe Hands
- **Computer Vision**: OpenCV 4.x
- **Language**: Python
- **Performance**: ~30-60 FPS (depending on hardware)
- **Accuracy**: High precision landmark detection
- **Latency**: Real-time processing with minimal delay

## 📊 Code Structure

```python
# Key Components:
- cv2.VideoCapture()     # Camera initialization
- mpHands.Hands()        # MediaPipe hand detection
- results.multi_hand_landmarks  # Detected landmarks
- mpDraw.draw_landmarks() # Visualization
```

## 🎯 Applications

This hand detection program can be extended for:
- **Gesture Recognition**: Recognize specific hand gestures
- **Sign Language Translation**: Convert signs to text
- **Virtual Controls**: Control applications with hand movements
- **Augmented Reality**: Overlay virtual objects on hands
- **Medical Analysis**: Study hand movement patterns
- **Gaming**: Hand-based game controls

## 🔧 Customization

### Modify Detection Parameters:
```python
hands = mpHands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)
```

### Change Visualization:
```python
# Change landmark circle color and size
cv2.circle(img, (cx, cy), radius, (B, G, R), thickness)

# Modify text display
cv2.putText(img, text, position, font, size, color, thickness)
```

## 🐛 Troubleshooting

**Camera not detected:**
- Check if your camera is working
- Try changing `cv2.VideoCapture(0)` to `cv2.VideoCapture(1)`

**Poor detection accuracy:**
- Ensure good lighting conditions
- Keep hands within camera frame
- Adjust `min_detection_confidence` parameter

**Low FPS:**
- Close other applications using the camera
- Reduce image processing resolution
- Check hardware specifications

## 📈 Performance Optimization

- **Lighting**: Use consistent, bright lighting for better detection
- **Background**: Plain backgrounds improve accuracy
- **Distance**: Keep hands 30-100cm from camera
- **Steady Hands**: Minimize rapid movements for stable tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Author

**MERYEM EL OSMANI**
- Project Creator and Developer
- Computer Vision Enthusiast

## 🙏 Acknowledgments

- **Google MediaPipe Team** for the amazing hand detection framework
- **OpenCV Community** for the comprehensive computer vision library
- **Python Community** for the excellent ecosystem

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Open an issue on GitHub
3. Review the code comments for detailed explanations

---

⭐ **Star this repository if you found it helpful!** ⭐

*Made with ❤️ and Python*