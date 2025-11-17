import cv2
import mediapipe as mp
import numpy as np
import math
import time

# ================================
# MERYEM EL OSMANI PROJECT
# THUMB+INDEX TEXT RESIZER 👍👆
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, 
                       min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Colors
WHITE = (255, 255, 255)
CYAN = (255, 255, 0)
PINK = (255, 20, 147)
GREEN = (0, 255, 100)
BLUE = (255, 100, 0)
YELLOW = (0, 255, 255)
ORANGE = (0, 165, 255)
PURPLE = (255, 0, 255)
RED = (0, 0, 255)

class TextObject:
    def __init__(self, text, x, y, size=2.0):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.min_size = 0.3
        self.max_size = 10.0
        self.color = CYAN
        self.outline_color = WHITE
        self.glow_intensity = 1.0
        self.created_time = time.time()
        
    def update_size(self, new_size):
        """Update text size with smooth bounds"""
        self.size = max(self.min_size, min(self.max_size, new_size))
        
    def update_position(self, x, y):
        """Update text position smoothly"""
        self.x = x
        self.y = y
    
    def draw(self, img):
        """Draw text with beautiful glow effect"""
        # Calculate text size for perfect centering
        (text_width, text_height), baseline = cv2.getTextSize(
            self.text, cv2.FONT_HERSHEY_COMPLEX, self.size, max(2, int(self.size * 2)))
        
        # Center the text perfectly
        text_x = self.x - text_width // 2
        text_y = self.y + text_height // 2
        
        # Multi-layer glow effect
        for i in range(4, 0, -1):
            glow_thickness = max(2, int(self.size * 2)) + i * 3
            glow_alpha = 0.2 * self.glow_intensity / i
            glow_color = tuple(int(c * glow_alpha) for c in self.color)
            
            cv2.putText(img, self.text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_COMPLEX, self.size, glow_color, 
                       glow_thickness, cv2.LINE_AA)
        
        # Main text with perfect anti-aliasing
        cv2.putText(img, self.text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_COMPLEX, self.size, self.color, 
                   max(2, int(self.size * 2)), cv2.LINE_AA)
        
        # Sharp outline for definition
        cv2.putText(img, self.text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_COMPLEX, self.size, self.outline_color, 
                   1, cv2.LINE_AA)

def calculate_pinch_distance(thumb, index):
    """Calculate precise distance between thumb and index"""
    return math.sqrt((thumb[0] - index[0])**2 + (thumb[1] - index[1])**2)

def get_pinch_center(thumb, index):
    """Get precise center point between thumb and index"""
    return [(thumb[0] + index[0]) // 2, (thumb[1] + index[1]) // 2]

def detect_thumb_index_gesture(landmarks):
    """Detect specific thumb+index gestures"""
    if not landmarks:
        return "none", 0
    
    # Get key finger positions
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    index_tip = landmarks[8]
    index_pip = landmarks[6]
    middle_tip = landmarks[12]
    middle_pip = landmarks[10]
    ring_tip = landmarks[16]
    ring_pip = landmarks[14]
    
    # Calculate pinch distance
    pinch_distance = calculate_pinch_distance(thumb_tip, index_tip)
    
    # Check finger extensions
    thumb_extended = thumb_tip[0] > thumb_mcp[0]  # Simplified thumb check
    index_extended = index_tip[1] < index_pip[1]
    middle_extended = middle_tip[1] < middle_pip[1]
    ring_extended = ring_tip[1] < ring_pip[1]
    
    # Gesture classification
    if pinch_distance < 25:
        return "pinch", pinch_distance
    elif thumb_extended and index_extended and not middle_extended and not ring_extended:
        return "thumb_index_only", pinch_distance
    elif thumb_extended and index_extended and middle_extended and not ring_extended:
        return "three_fingers", pinch_distance
    elif not thumb_extended and not index_extended:
        return "closed", pinch_distance
    else:
        return "normal", pinch_distance

def classify_hand_advanced(landmarks, img_width):
    """Advanced hand classification using multiple markers"""
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    index_tip = landmarks[8]
    wrist = landmarks[0]
    
    # Multiple classification methods
    thumb_direction = thumb_tip[0] > thumb_mcp[0]
    hand_center_x = np.mean([p[0] for p in landmarks])
    
    # More reliable classification
    if hand_center_x < img_width // 2:
        return "left" if thumb_direction else "right"
    else:
        return "right" if thumb_direction else "left"

def draw_pinch_visualization(img, left_hand, right_hand):
    """Draw advanced visualization for thumb+index control"""
    if not left_hand or not right_hand:
        return
    
    # Get thumb and index for both hands
    left_thumb = left_hand[4]
    left_index = left_hand[8]
    right_thumb = right_hand[4]
    right_index = right_hand[8]
    
    # Calculate pinch centers
    left_center = get_pinch_center(left_thumb, left_index)
    right_center = get_pinch_center(right_thumb, right_index)
    
    # Calculate pinch distances
    left_pinch_dist = calculate_pinch_distance(left_thumb, left_index)
    right_pinch_dist = calculate_pinch_distance(right_thumb, right_index)
    
    # Draw left hand thumb-index connection
    cv2.line(img, left_thumb, left_index, PINK, 4)
    cv2.circle(img, left_thumb, 8, RED, -1)
    cv2.circle(img, left_index, 8, BLUE, -1)
    cv2.circle(img, left_center, 12, GREEN, 3)
    cv2.circle(img, left_center, 6, GREEN, -1)
    
    # Draw right hand thumb-index connection
    cv2.line(img, right_thumb, right_index, PINK, 4)
    cv2.circle(img, right_thumb, 8, RED, -1)
    cv2.circle(img, right_index, 8, BLUE, -1)
    cv2.circle(img, right_center, 12, GREEN, 3)
    cv2.circle(img, right_center, 6, GREEN, -1)
    
    # Draw connection between pinch centers
    center_distance = calculate_pinch_distance(left_center, right_center)
    cv2.line(img, left_center, right_center, CYAN, 5)
    
    # Draw distance indicators
    mid_x = (left_center[0] + right_center[0]) // 2
    mid_y = (left_center[1] + right_center[1]) // 2 - 50
    
    cv2.putText(img, f"Pinch Distance: {int(center_distance)}", (mid_x - 100, mid_y),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
    
    # Individual pinch indicators
    cv2.putText(img, f"L: {int(left_pinch_dist)}", (left_center[0] - 30, left_center[1] + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)
    cv2.putText(img, f"R: {int(right_pinch_dist)}", (right_center[0] - 30, right_center[1] + 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)
    
    # Visual resize indicators
    arrow_length = 40
    # Left arrow
    cv2.arrowedLine(img, (left_center[0] + 25, left_center[1]), 
                   (left_center[0] + 25 - arrow_length, left_center[1]), YELLOW, 4, tipLength=0.3)
    # Right arrow
    cv2.arrowedLine(img, (right_center[0] - 25, right_center[1]), 
                   (right_center[0] - 25 + arrow_length, right_center[1]), YELLOW, 4, tipLength=0.3)

def draw_gesture_feedback(img, left_gesture, right_gesture, left_hand, right_hand):
    """Draw real-time gesture feedback"""
    if left_hand:
        left_center = get_pinch_center(left_hand[4], left_hand[8])
        gesture_color = GREEN if left_gesture[0] == "pinch" else CYAN if left_gesture[0] == "thumb_index_only" else WHITE
        cv2.putText(img, f"L: {left_gesture[0]}", (left_center[0] - 40, left_center[1] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, gesture_color, 2)
    
    if right_hand:
        right_center = get_pinch_center(right_hand[4], right_hand[8])
        gesture_color = GREEN if right_gesture[0] == "pinch" else CYAN if right_gesture[0] == "thumb_index_only" else WHITE
        cv2.putText(img, f"R: {right_gesture[0]}", (right_center[0] - 40, right_center[1] - 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, gesture_color, 2)

def draw_advanced_instructions(img):
    """Draw detailed instructions for thumb+index control"""
    instructions = [
        "MERYEM EL OSMANI - PRECISION THUMB+INDEX CONTROL",
        "",
        "👍👆 THUMB + INDEX CONTROLS:",
        "   • Move pinch points APART = BIGGER text",
        "   • Move pinch points TOGETHER = SMALLER text", 
        "   • Move both pinch points = MOVE text",
        "",
        "🤏 Both hands PINCH = Change text content",
        "👍👆 Thumb+Index EXTENDED = Change text color",
        "🖖 THREE FINGERS = Reset to default size",
        "",
        "🔴 Red = Thumb  🔵 Blue = Index  🟢 Green = Pinch Center"
    ]
    
    for i, instruction in enumerate(instructions):
        y_pos = 30 + i * 22
        if i == 0:
            color, thickness, scale = CYAN, 2, 0.8
        elif instruction == "":
            continue
        elif instruction.startswith("🔴"):
            color, thickness, scale = WHITE, 1, 0.4
        else:
            color, thickness, scale = WHITE, 1, 0.5
            
        cv2.putText(img, instruction, (20, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness)

# Initialize
cap = cv2.VideoCapture(0)

# Text samples with MERYEM EL OSMANI
text_samples = [
    "MERYEM EL OSMANI",
    "PRECISION CONTROL!", 
    "THUMB + INDEX",
    "AMAZING RESIZE",
    "PERFECT CONTROL",
    "SMOOTH SCALING",
    "BEAUTIFUL TEXT!"
]

current_text_index = 0
text_obj = TextObject(text_samples[current_text_index], 400, 300, 3.0)

# Tracking variables
left_hand_landmarks = None
right_hand_landmarks = None
initial_distance = None
initial_size = 3.0
last_gesture_time = 0
gesture_hold_time = 0

# Color cycle
colors = [CYAN, PINK, GREEN, BLUE, YELLOW, ORANGE, PURPLE, RED, WHITE]
current_color_index = 0

print("👍👆 MERYEM EL OSMANI'S PRECISION THUMB+INDEX TEXT RESIZER ACTIVATED! 📝")
print("=== THUMB + INDEX PRECISION CONTROLS ===")
print("👍👆 Move thumb+index pinch points apart/together for precise text resize")
print("🤝 Move both pinch points together to reposition text")
print("🤏 Pinch with both hands to change text content")
print("👍👆 Extend thumb+index on both hands to change color")
print("🖖 Three fingers on both hands to reset size")
print("Ultimate precision with thumb and index fingers! ✨")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Create elegant dark overlay
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    frame = cv2.addWeighted(frame, 0.2, overlay, 0.8, 0)
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_time = time.time()
    
    # Reset hand tracking
    left_hand_landmarks = None
    right_hand_landmarks = None
    
    if results.multi_hand_landmarks:
        detected_hands = []
        
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            hand_type = classify_hand_advanced(landmarks, w)
            detected_hands.append((hand_type, landmarks, hand_landmarks))
        
        # Assign hands correctly
        for hand_type, landmarks, hand_landmarks in detected_hands:
            if hand_type == "left":
                left_hand_landmarks = landmarks
            else:
                right_hand_landmarks = landmarks
            
            # Draw elegant hand skeleton
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(100, 255, 255), thickness=2),
                                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=3))
    
    # Dual thumb+index interaction
    if left_hand_landmarks and right_hand_landmarks:
        # Calculate distance between pinch centers
        left_center = get_pinch_center(left_hand_landmarks[4], left_hand_landmarks[8])
        right_center = get_pinch_center(right_hand_landmarks[4], right_hand_landmarks[8])
        center_distance = calculate_pinch_distance(left_center, right_center)
        
        # Initialize reference distance
        if initial_distance is None:
            initial_distance = center_distance
            initial_size = text_obj.size
        
        # Calculate size based on pinch distance ratio
        size_ratio = center_distance / initial_distance
        new_size = initial_size * size_ratio
        text_obj.update_size(new_size)
        
        # Update text position to midpoint between pinch centers
        mid_x = (left_center[0] + right_center[0]) // 2
        mid_y = (left_center[1] + right_center[1]) // 2
        text_obj.update_position(int(mid_x), int(mid_y))
        
        # Draw advanced pinch visualization
        draw_pinch_visualization(frame, left_hand_landmarks, right_hand_landmarks)
        
        # Detect thumb+index gestures
        left_gesture = detect_thumb_index_gesture(left_hand_landmarks)
        right_gesture = detect_thumb_index_gesture(right_hand_landmarks)
        
        # Draw gesture feedback
        draw_gesture_feedback(frame, left_gesture, right_gesture, 
                            left_hand_landmarks, right_hand_landmarks)
        
        # Gesture controls with hold detection
        both_pinching = left_gesture[0] == "pinch" and right_gesture[0] == "pinch"
        both_thumb_index = (left_gesture[0] == "thumb_index_only" and 
                           right_gesture[0] == "thumb_index_only")
        both_three_fingers = (left_gesture[0] == "three_fingers" and 
                             right_gesture[0] == "three_fingers")
        
        if both_pinching:
            gesture_hold_time += 1
            if gesture_hold_time > 20 and current_time - last_gesture_time > 1.0:  # Hold for ~0.7s
                current_text_index = (current_text_index + 1) % len(text_samples)
                text_obj.text = text_samples[current_text_index]
                last_gesture_time = current_time
                gesture_hold_time = 0
                print(f"📝 Text changed to: {text_obj.text}")
            
            # Show hold progress
            progress = min(1.0, gesture_hold_time / 20.0)
            progress_width = int(200 * progress)
            cv2.rectangle(frame, (mid_x - 100, mid_y + 60), (mid_x - 100 + progress_width, mid_y + 70), 
                         GREEN, -1)
            cv2.rectangle(frame, (mid_x - 100, mid_y + 60), (mid_x + 100, mid_y + 70), WHITE, 2)
            cv2.putText(frame, "HOLD TO CHANGE TEXT", (mid_x - 90, mid_y + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
        
        elif both_thumb_index:
            gesture_hold_time += 1
            if gesture_hold_time > 20 and current_time - last_gesture_time > 1.0:
                current_color_index = (current_color_index + 1) % len(colors)
                text_obj.color = colors[current_color_index]
                last_gesture_time = current_time
                gesture_hold_time = 0
                print(f"🎨 Color changed!")
            
            # Show color change progress
            progress = min(1.0, gesture_hold_time / 20.0)
            progress_width = int(200 * progress)
            cv2.rectangle(frame, (mid_x - 100, mid_y + 60), (mid_x - 100 + progress_width, mid_y + 70), 
                         colors[current_color_index], -1)
            cv2.rectangle(frame, (mid_x - 100, mid_y + 60), (mid_x + 100, mid_y + 70), WHITE, 2)
            cv2.putText(frame, "HOLD TO CHANGE COLOR", (mid_x - 95, mid_y + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
        
        elif both_three_fingers:
            gesture_hold_time += 1
            if gesture_hold_time > 20 and current_time - last_gesture_time > 1.0:
                text_obj.update_size(3.0)
                initial_size = 3.0
                initial_distance = center_distance
                last_gesture_time = current_time
                gesture_hold_time = 0
                print("🔄 Size reset to default")
            
            # Show reset progress
            progress = min(1.0, gesture_hold_time / 20.0)
            progress_width = int(200 * progress)
            cv2.rectangle(frame, (mid_x - 100, mid_y + 60), (mid_x - 100 + progress_width, mid_y + 70), 
                         PURPLE, -1)
            cv2.rectangle(frame, (mid_x - 100, mid_y + 60), (mid_x + 100, mid_y + 70), WHITE, 2)
            cv2.putText(frame, "HOLD TO RESET SIZE", (mid_x - 85, mid_y + 55),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
        else:
            gesture_hold_time = 0
    else:
        # Reset when hands not detected
        initial_distance = None
        gesture_hold_time = 0
    
    # Draw the text object
    text_obj.draw(frame)
    
    # Draw instructions
    draw_advanced_instructions(frame)
    
    # Status display
    status_y = h - 120
    cv2.putText(frame, f"Text: {text_obj.text}", (20, status_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    cv2.putText(frame, f"Size: {text_obj.size:.1f}", (20, status_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    hands_count = len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0
    cv2.putText(frame, f"Hands: {hands_count}/2", (20, status_y + 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    cv2.putText(frame, f"Color: {colors.index(text_obj.color) + 1}/{len(colors)}", (20, status_y + 75), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_obj.color, 2)
    
    cv2.imshow('MERYEM EL OSMANI - PRECISION THUMB+INDEX RESIZER 👍👆', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("👍👆 Precision thumb+index session complete! Perfect control achieved! 📝✨")