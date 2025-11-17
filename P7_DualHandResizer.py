import cv2
import mediapipe as mp
import numpy as np
import math
import time

# ================================
# MERYEM EL OSMANI PROJECT
# DUAL HAND TEXT RESIZER 🙌📝
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

class TextObject:
    def __init__(self, text, x, y, size=2.0):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.min_size = 0.5
        self.max_size = 8.0
        self.color = CYAN
        self.outline_color = WHITE
        self.glow_intensity = 1.0
        self.rotation = 0
        self.created_time = time.time()
        
    def update_size(self, new_size):
        """Update text size with bounds"""
        self.size = max(self.min_size, min(self.max_size, new_size))
        
    def update_position(self, x, y):
        """Update text position"""
        self.x = x
        self.y = y
    
    def draw(self, img):
        """Draw text with glow effect"""
        # Calculate text size for centering
        (text_width, text_height), baseline = cv2.getTextSize(
            self.text, cv2.FONT_HERSHEY_COMPLEX, self.size, max(2, int(self.size * 2)))
        
        # Center the text
        text_x = self.x - text_width // 2
        text_y = self.y + text_height // 2
        
        # Glow effect (multiple layers)
        for i in range(3, 0, -1):
            glow_thickness = max(2, int(self.size * 2)) + i * 2
            glow_alpha = 0.3 * self.glow_intensity / i
            glow_color = tuple(int(c * glow_alpha) for c in self.color)
            
            cv2.putText(img, self.text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_COMPLEX, self.size, glow_color, 
                       glow_thickness, cv2.LINE_AA)
        
        # Main text
        cv2.putText(img, self.text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_COMPLEX, self.size, self.color, 
                   max(2, int(self.size * 2)), cv2.LINE_AA)
        
        # Outline
        cv2.putText(img, self.text, (text_x, text_y), 
                   cv2.FONT_HERSHEY_COMPLEX, self.size, self.outline_color, 
                   1, cv2.LINE_AA)

def detect_hands_distance(left_hand, right_hand):
    """Calculate distance between thumb and index of both hands"""
    if not left_hand or not right_hand:
        return None
    
    # Get thumb and index tips for precise control
    left_thumb = np.array(left_hand[4])   # Thumb tip
    left_index = np.array(left_hand[8])   # Index tip
    right_thumb = np.array(right_hand[4]) # Thumb tip  
    right_index = np.array(right_hand[8]) # Index tip
    
    # Calculate pinch centers (midpoint between thumb and index)
    left_pinch_center = (left_thumb + left_index) / 2
    right_pinch_center = (right_thumb + right_index) / 2
    
    # Calculate distance between pinch centers
    distance = np.linalg.norm(right_pinch_center - left_pinch_center)
    
    return distance, left_pinch_center, right_pinch_center

def classify_hand(landmarks, img_width):
    """Classify if hand is left or right based on thumb position"""
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    
    # Simple classification based on thumb direction
    if thumb_tip[0] > thumb_mcp[0]:
        return "right" if thumb_tip[0] > img_width // 2 else "left"
    else:
        return "left" if thumb_tip[0] < img_width // 2 else "right"

def draw_hand_connection(img, left_center, right_center, distance, left_hand=None, right_hand=None):
    """Draw connection line between thumb+index pinch points with visual feedback"""
    if left_center is not None and right_center is not None:
        left_pt = (int(left_center[0]), int(left_center[1]))
        right_pt = (int(right_center[0]), int(right_center[1]))
        
        # Draw main connection line
        cv2.line(img, left_pt, right_pt, CYAN, 4)
        
        # Draw pinch point indicators
        cv2.circle(img, left_pt, 20, GREEN, 3)
        cv2.circle(img, right_pt, 20, GREEN, 3)
        cv2.circle(img, left_pt, 10, GREEN, -1)
        cv2.circle(img, right_pt, 10, GREEN, -1)
        
        # Draw thumb and index connections if hands provided
        if left_hand and right_hand:
            # Left hand thumb-index connection
            left_thumb = (int(left_hand[4][0]), int(left_hand[4][1]))
            left_index = (int(left_hand[8][0]), int(left_hand[8][1]))
            cv2.line(img, left_thumb, left_index, PINK, 3)
            cv2.circle(img, left_thumb, 8, PINK, -1)
            cv2.circle(img, left_index, 8, PINK, -1)
            
            # Right hand thumb-index connection  
            right_thumb = (int(right_hand[4][0]), int(right_hand[4][1]))
            right_index = (int(right_hand[8][0]), int(right_hand[8][1]))
            cv2.line(img, right_thumb, right_index, PINK, 3)
            cv2.circle(img, right_thumb, 8, PINK, -1)
            cv2.circle(img, right_index, 8, PINK, -1)
        
        # Distance text with pinch indicator
        mid_x = (left_pt[0] + right_pt[0]) // 2
        mid_y = (left_pt[1] + right_pt[1]) // 2 - 40
        cv2.putText(img, f"Pinch Distance: {int(distance)}", (mid_x - 80, mid_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
        cv2.putText(img, "👍👆 ↔️ 👍👆", (mid_x - 50, mid_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 2)

def draw_resize_indicators(img, left_center, right_center, text_size):
    """Draw visual indicators for resizing"""
    if left_center is not None and right_center is not None:
        left_pt = (int(left_center[0]), int(left_center[1]))
        right_pt = (int(right_center[0]), int(right_center[1]))
        
        # Draw resize arrows
        arrow_length = 30
        
        # Left arrow (pointing left)
        cv2.arrowedLine(img, (left_pt[0] + 20, left_pt[1]), 
                       (left_pt[0] + 20 - arrow_length, left_pt[1]), YELLOW, 3, tipLength=0.3)
        
        # Right arrow (pointing right)
        cv2.arrowedLine(img, (right_pt[0] - 20, right_pt[1]), 
                       (right_pt[0] - 20 + arrow_length, right_pt[1]), YELLOW, 3, tipLength=0.3)
        
        # Size indicator
        cv2.putText(img, f"SIZE: {text_size:.1f}", (left_pt[0] - 50, left_pt[1] + 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, PINK, 2)

def draw_instructions(img):
    """Draw usage instructions"""
    instructions = [
        "MERYEM EL OSMANI - THUMB+INDEX TEXT RESIZER",
        "",
        "👍👆 Use thumb + index of both hands:",
        "   • Move pinch points APART = Make text BIGGER",
        "   • Move pinch points TOGETHER = Make text SMALLER", 
        "   • Move both pinch points = Move text position",
        "",
        "🤏 Both hands pinch = Change text content",
        "👍👆 Thumb+Index extended = Change text color",
        "🖖 Three fingers = Reset to default size"
    ]
    
    for i, instruction in enumerate(instructions):
        y_pos = 30 + i * 25
        color = CYAN if i == 0 else WHITE
        thickness = 2 if i == 0 else 1
        font_scale = 0.8 if i == 0 else 0.5
        
        cv2.putText(img, instruction, (20, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

def detect_gesture(landmarks):
    """Detect thumb+index specific gestures"""
    if not landmarks:
        return "none"
    
    # Get thumb and index positions
    thumb_tip = landmarks[4]
    thumb_mcp = landmarks[2]
    index_tip = landmarks[8]
    index_pip = landmarks[6]
    middle_tip = landmarks[12]
    middle_pip = landmarks[10]
    
    # Check if thumb and index are extended
    thumb_up = thumb_tip[0] > thumb_mcp[0]  # Simplified thumb detection
    index_up = index_tip[1] < index_pip[1]
    middle_up = middle_tip[1] < middle_pip[1]
    
    # Calculate pinch distance
    pinch_distance = math.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
    
    # Gesture classification based on thumb+index
    if pinch_distance < 30:
        return "pinch"  # Thumb and index touching
    elif thumb_up and index_up and not middle_up:
        return "thumb_index"  # Only thumb and index extended
    elif thumb_up and index_up and middle_up:
        return "three_fingers"  # Thumb, index, middle
    elif not thumb_up and not index_up:
        return "closed"  # Thumb and index closed
    else:
        return "normal"

# Initialize
cap = cv2.VideoCapture(0)

# Text samples
text_samples = [
    "MERYEM EL OSMANI",
    "HELLO WORLD!", 
    "RESIZE ME!",
    "AMAZING TEXT",
    "DUAL HANDS",
    "COOL EFFECT",
    "BEAUTIFUL!"
]

current_text_index = 0
text_obj = TextObject(text_samples[current_text_index], 400, 300, 2.0)

# Hand tracking
left_hand_landmarks = None
right_hand_landmarks = None
initial_distance = None
initial_size = 2.0
last_gesture_time = 0

# Color cycle
colors = [CYAN, PINK, GREEN, BLUE, YELLOW, ORANGE, PURPLE, WHITE]
current_color_index = 0

print("👍👆 MERYEM EL OSMANI'S THUMB+INDEX TEXT RESIZER ACTIVATED! 📝")
print("=== THUMB + INDEX PRECISION CONTROLS ===")
print("👍👆 Move thumb+index pinch points apart/together to resize text")
print("🤝 Move both pinch points to reposition text")
print("🤏 Pinch with both hands to change text")
print("👍👆 Extend thumb+index on both hands to change color")
print("🖖 Three fingers on both hands to reset size")
print("Precise control with thumb and index fingers! ✨")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Create dark overlay for better text visibility
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
    frame = cv2.addWeighted(frame, 0.3, overlay, 0.7, 0)
    
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
            hand_type = classify_hand(landmarks, w)
            detected_hands.append((hand_type, landmarks, hand_landmarks))
        
        # Assign hands
        for hand_type, landmarks, hand_landmarks in detected_hands:
            if hand_type == "left":
                left_hand_landmarks = landmarks
            else:
                right_hand_landmarks = landmarks
            
            # Draw hand skeleton
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(0, 255, 255), thickness=2),
                                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2))
    
    # Dual hand interaction
    if left_hand_landmarks and right_hand_landmarks:
        # Calculate distance between hands
        result = detect_hands_distance(left_hand_landmarks, right_hand_landmarks)
        if result:
            distance, left_center, right_center = result
            
            # Initialize reference distance
            if initial_distance is None:
                initial_distance = distance
                initial_size = text_obj.size
            
            # Calculate new size based on distance ratio
            size_ratio = distance / initial_distance
            new_size = initial_size * size_ratio
            text_obj.update_size(new_size)
            
            # Update text position to midpoint between hands
            mid_x = (left_center[0] + right_center[0]) // 2
            mid_y = (left_center[1] + right_center[1]) // 2
            text_obj.update_position(int(mid_x), int(mid_y))
            
            # Draw connection and indicators with hand details
            draw_hand_connection(frame, left_center, right_center, distance, 
                               left_hand_landmarks, right_hand_landmarks)
            draw_resize_indicators(frame, left_center, right_center, text_obj.size)
            
            # Detect thumb+index gestures from both hands
            left_gesture = detect_gesture(left_hand_landmarks)
            right_gesture = detect_gesture(right_hand_landmarks)
            
            # Both hands pinch - change text
            if left_gesture == "pinch" and right_gesture == "pinch":
                if current_time - last_gesture_time > 1.0:
                    current_text_index = (current_text_index + 1) % len(text_samples)
                    text_obj.text = text_samples[current_text_index]
                    last_gesture_time = current_time
                    print(f"📝 Text changed to: {text_obj.text}")
            
            # Both hands thumb+index extended - change color
            elif left_gesture == "thumb_index" and right_gesture == "thumb_index":
                if current_time - last_gesture_time > 1.0:
                    current_color_index = (current_color_index + 1) % len(colors)
                    text_obj.color = colors[current_color_index]
                    last_gesture_time = current_time
                    print(f"🎨 Color changed!")
            
            # Both hands three fingers - reset size
            elif left_gesture == "three_fingers" and right_gesture == "three_fingers":
                if current_time - last_gesture_time > 1.0:
                    text_obj.update_size(2.0)
                    initial_size = 2.0
                    initial_distance = distance
                    last_gesture_time = current_time
                    print("🔄 Size reset to default")
    else:
        # Reset when hands are not detected
        if initial_distance is not None:
            initial_distance = None
    
    # Draw text
    text_obj.draw(frame)
    
    # Draw instructions
    draw_instructions(frame)
    
    # Status display
    status_y = h - 100
    cv2.putText(frame, f"Current Text: {text_obj.text}", (20, status_y), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    cv2.putText(frame, f"Size: {text_obj.size:.1f}", (20, status_y + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    cv2.putText(frame, f"Hands Detected: {len(results.multi_hand_landmarks) if results.multi_hand_landmarks else 0}/2", 
                (20, status_y + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    
    cv2.imshow('MERYEM EL OSMANI - DUAL HAND TEXT RESIZER 🙌', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("🙌 Dual hand text resizing session complete! Amazing control! 📝✨")