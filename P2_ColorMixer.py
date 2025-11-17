import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

# ================================
# MERYEM EL OSMANI PROJECT
# INTERACTIVE COLOR MIXER STUDIO 🎨
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, 
                       min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Color Palette 🎨
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
MAGENTA = (255, 0, 255)
CYAN = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
ORANGE = (0, 165, 255)
PURPLE = (128, 0, 128)

# Color mixing variables
canvas = None
mixed_color = [128, 128, 128]  # Start with gray
color_trail = []
brush_size = 20
is_mixing = False
color_palette = [RED, GREEN, BLUE, YELLOW, MAGENTA, CYAN, ORANGE, PURPLE]
palette_names = ["RED", "GREEN", "BLUE", "YELLOW", "MAGENTA", "CYAN", "ORANGE", "PURPLE"]
selected_colors = []
mixing_history = []
color_selection_timer = {}
selection_cooldown = {}
last_gesture = "none"
gesture_stability_count = 0

class ColorDrop:
    def __init__(self, x, y, color, size=30):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = 100
        self.original_size = size
    
    def update(self):
        self.life -= 1
        self.size = max(5, self.size - 0.5)
        return self.life > 0
    
    def draw(self, img):
        # Draw color drop with fade effect
        alpha = self.life / 100.0
        overlay = img.copy()
        cv2.circle(overlay, (int(self.x), int(self.y)), int(self.size), self.color, -1)
        cv2.addWeighted(overlay, alpha, img, 1-alpha, 0, img)

def draw_color_palette(img):
    """Draw the color palette on the left side with selection feedback"""
    palette_width = 100
    palette_height = len(color_palette) * 70
    start_y = (img.shape[0] - palette_height) // 2
    
    for i, (color, name) in enumerate(zip(color_palette, palette_names)):
        y = start_y + i * 70
        
        # Check if this color is selected
        is_selected = any(selected_name == name for _, selected_name in selected_colors)
        border_color = WHITE if not is_selected else YELLOW
        border_thickness = 2 if not is_selected else 5
        
        # Draw color swatch with selection indicator
        cv2.rectangle(img, (15, y), (15 + palette_width, y + 60), color, -1)
        cv2.rectangle(img, (15, y), (15 + palette_width, y + 60), border_color, border_thickness)
        
        # Draw selection progress if being selected
        if name in color_selection_timer:
            progress = min(1.0, color_selection_timer[name] / 2.0)  # 2 second selection time
            progress_width = int(palette_width * progress)
            cv2.rectangle(img, (15, y + 65), (15 + progress_width, y + 70), YELLOW, -1)
        
        # Draw color name
        text_color = WHITE if not is_selected else BLACK
        cv2.putText(img, name, (20, y + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
        
        # Show selection number
        if is_selected:
            selection_num = next(i+1 for i, (_, selected_name) in enumerate(selected_colors) if selected_name == name)
            cv2.circle(img, (25, y + 10), 15, YELLOW, -1)
            cv2.putText(img, str(selection_num), (20, y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLACK, 2)

def get_color_from_position(x, y, img_height):
    """Get color from palette position with improved detection"""
    palette_height = len(color_palette) * 70
    start_y = (img_height - palette_height) // 2
    
    if 15 <= x <= 115:  # Within improved palette width
        for i in range(len(color_palette)):
            color_y = start_y + i * 70
            if color_y <= y <= color_y + 60:
                return color_palette[i], palette_names[i], i
    return None, None, -1

def mix_colors(color1, color2, ratio=0.5):
    """Mix two colors with a given ratio"""
    mixed = []
    for i in range(3):
        mixed.append(int(color1[i] * (1-ratio) + color2[i] * ratio))
    return tuple(mixed)

def draw_mixing_area(img):
    """Draw the main color mixing canvas area"""
    # Main canvas area (center-right)
    canvas_x = 150
    canvas_y = 50
    canvas_w = img.shape[1] - 200
    canvas_h = img.shape[0] - 100
    
    # Draw canvas background
    cv2.rectangle(img, (canvas_x, canvas_y), (canvas_x + canvas_w, canvas_y + canvas_h), 
                  (240, 240, 240), -1)
    cv2.rectangle(img, (canvas_x, canvas_y), (canvas_x + canvas_w, canvas_y + canvas_h), 
                  BLACK, 2)
    
    # Draw current mixed color preview
    preview_size = 100
    preview_x = canvas_x + canvas_w - preview_size - 20
    preview_y = canvas_y + 20
    
    cv2.rectangle(img, (preview_x, preview_y), 
                  (preview_x + preview_size, preview_y + preview_size), 
                  tuple(map(int, mixed_color)), -1)
    cv2.rectangle(img, (preview_x, preview_y), 
                  (preview_x + preview_size, preview_y + preview_size), 
                  BLACK, 3)
    
    # Show RGB values
    cv2.putText(img, f"R: {int(mixed_color[2])}", (preview_x, preview_y + preview_size + 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 2)
    cv2.putText(img, f"G: {int(mixed_color[1])}", (preview_x, preview_y + preview_size + 45), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 2)
    cv2.putText(img, f"B: {int(mixed_color[0])}", (preview_x, preview_y + preview_size + 65), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, BLACK, 2)
    
    return canvas_x, canvas_y, canvas_w, canvas_h

def draw_instructions(img):
    """Draw usage instructions"""
    instructions = [
        "🎨 MERYEM'S COLOR MIXER STUDIO",
        "✋ Touch palette to select colors",
        "🤏 Pinch to mix colors",
        "✊ Fist to clear canvas",
        "👆 Point to paint with mixed color"
    ]
    
    for i, instruction in enumerate(instructions):
        y = 25 + i * 25
        color = WHITE if i == 0 else BLACK
        thickness = 3 if i == 0 else 1
        cv2.putText(img, instruction, (img.shape[1] - 400, y), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, thickness)

def detect_hand_gesture(landmarks):
    """Detect hand gestures with improved stability"""
    if not landmarks:
        return "none"
    
    # Get key points
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    palm = landmarks[9]
    
    # Calculate distances with better thresholds
    fingers_extended = []
    
    # Thumb (horizontal check)
    fingers_extended.append(abs(thumb_tip[0] - landmarks[3][0]) > 30)
    
    # Other fingers (vertical check with better threshold)
    for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
        fingers_extended.append((landmarks[pip][1] - landmarks[tip][1]) > 20)
    
    extended_count = sum(fingers_extended)
    
    # Pinch detection (thumb and index)
    pinch_dist = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))
    
    # More conservative gesture detection to reduce false positives
    if pinch_dist < 35 and extended_count <= 2:
        return "mixing"
    elif extended_count >= 3:  # 3+ fingers clearly extended
        return "selecting"
    elif extended_count == 0:  # All fingers clearly closed
        return "clear"
    elif fingers_extended[1] and extended_count == 1:  # Only index finger
        return "painting"
    else:
        return "none"  # Default to none for unclear gestures

# Initialize webcam
cap = cv2.VideoCapture(0)
color_drops = []
last_mixing_time = 0

print("🎨 MERYEM EL OSMANI'S COLOR MIXER STUDIO ACTIVATED! ✨")
print("Instructions:")
print("✋ Touch the color palette with your hand to select colors")
print("🤏 Pinch your fingers together to mix selected colors")
print("👆 Point with your index finger to paint")
print("✊ Make a fist to clear the canvas")
print("Press ESC to exit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    # Initialize canvas if needed
    if canvas is None:
        canvas = np.ones((h, w, 3), dtype=np.uint8) * 240  # Light gray background
    
    # Draw UI elements
    draw_color_palette(frame)
    canvas_x, canvas_y, canvas_w, canvas_h = draw_mixing_area(frame)
    draw_instructions(frame)
    
    # Update and draw color drops
    color_drops = [drop for drop in color_drops if drop.update()]
    for drop in color_drops:
        drop.draw(frame)
    
    current_time = time.time()
    
    # Update color selection timers
    for color_name in list(color_selection_timer.keys()):
        color_selection_timer[color_name] += 1/30  # Assuming 30 FPS
        if color_selection_timer[color_name] >= 2.0:  # 2 seconds to select
            del color_selection_timer[color_name]
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw hand skeleton
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Get hand gesture with stability check
            current_gesture = detect_hand_gesture(landmarks)
            
            # Gesture stability
            if current_gesture == last_gesture:
                gesture_stability_count += 1
            else:
                gesture_stability_count = 0
                last_gesture = current_gesture
            
            # Only process stable gestures (held for at least 5 frames)
            if gesture_stability_count >= 5:
                gesture = current_gesture
            else:
                gesture = "none"
                
            index_pos = landmarks[8]  # Index fingertip
            
            if gesture == "selecting":
                # Check if touching color palette
                color, color_name, color_index = get_color_from_position(index_pos[0], index_pos[1], h)
                if color and color_name:
                    # Start or update selection timer
                    if color_name not in color_selection_timer:
                        color_selection_timer[color_name] = 0
                    
                    # Check if selection is complete and color not already selected
                    if (color_selection_timer[color_name] >= 1.5 and 
                        len(selected_colors) < 2 and 
                        color_name not in [name for _, name in selected_colors] and
                        color_name not in selection_cooldown):
                        
                        selected_colors.append((color, color_name))
                        color_drops.append(ColorDrop(index_pos[0], index_pos[1], color))
                        selection_cooldown[color_name] = current_time + 1.0  # 1 second cooldown
                        print(f"🎨 Selected: {color_name} ({len(selected_colors)}/2)")
                        del color_selection_timer[color_name]
                
                # Draw selection indicator
                cv2.circle(frame, index_pos, 30, WHITE, 4)
                cv2.putText(frame, "HOLD TO SELECT", (index_pos[0] - 70, index_pos[1] - 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
            
            elif gesture == "mixing" and len(selected_colors) >= 2:
                # Mix the selected colors
                if current_time - last_mixing_time > 0.5:  # Throttle mixing
                    color1, name1 = selected_colors[0]
                    color2, name2 = selected_colors[1]
                    
                    # Create mixing animation
                    for i in range(10):
                        ratio = i / 9.0
                        mixed = mix_colors(color1, color2, ratio)
                        x = index_pos[0] + random.randint(-20, 20)
                        y = index_pos[1] + random.randint(-20, 20)
                        color_drops.append(ColorDrop(x, y, mixed, 15))
                    
                    # Update the mixed color
                    mixed_color[0] = (color1[0] + color2[0]) // 2  # B
                    mixed_color[1] = (color1[1] + color2[1]) // 2  # G  
                    mixed_color[2] = (color1[2] + color2[2]) // 2  # R
                    
                    mixing_history.append(f"{name1} + {name2}")
                    selected_colors = []  # Clear selection
                    last_mixing_time = current_time
                    print(f"🌈 Mixed: {name1} + {name2} = New Color!")
                
                # Draw mixing indicator
                cv2.circle(frame, index_pos, 30, tuple(map(int, mixed_color)), 5)
                cv2.putText(frame, "MIXING!", (index_pos[0] - 40, index_pos[1] - 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, tuple(map(int, mixed_color)), 2)
            
            elif gesture == "painting":
                # Paint with the mixed color
                if canvas_x < index_pos[0] < canvas_x + canvas_w and canvas_y < index_pos[1] < canvas_y + canvas_h:
                    cv2.circle(frame, index_pos, brush_size, tuple(map(int, mixed_color)), -1)
                    cv2.circle(canvas, index_pos, brush_size, tuple(map(int, mixed_color)), -1)
                    
                    # Add paint drops
                    color_drops.append(ColorDrop(index_pos[0], index_pos[1], tuple(map(int, mixed_color)), 10))
                
                cv2.putText(frame, "PAINTING", (index_pos[0] - 50, index_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, tuple(map(int, mixed_color)), 2)
            
            elif gesture == "clear":
                # Clear the canvas
                canvas = np.ones((h, w, 3), dtype=np.uint8) * 240
                mixed_color = [128, 128, 128]
                selected_colors = []
                color_drops = []
                color_selection_timer = {}
                selection_cooldown = {}
                print("🧹 Canvas cleared!")
                
                cv2.putText(frame, "CLEARING", (index_pos[0] - 50, index_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
    
    # Clean up expired cooldowns
    current_time = time.time()
    selection_cooldown = {k: v for k, v in selection_cooldown.items() if v > current_time}
    
    # Show selected colors
    for i, (color, name) in enumerate(selected_colors[:2]):
        y_pos = h - 80 + i * 40
        cv2.rectangle(frame, (150, y_pos), (200, y_pos + 30), color, -1)
        cv2.rectangle(frame, (150, y_pos), (200, y_pos + 30), WHITE, 2)
        cv2.putText(frame, name[:3], (210, y_pos + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 2)
    
    # Blend canvas with video feed in the mixing area
    if canvas is not None:
        mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        cv2.rectangle(mask, (canvas_x, canvas_y), (canvas_x + canvas_w, canvas_y + canvas_h), 255, -1)
        
        # Alpha blend the canvas
        alpha = 0.7
        frame_roi = frame[canvas_y:canvas_y+canvas_h, canvas_x:canvas_x+canvas_w]
        canvas_roi = canvas[canvas_y:canvas_y+canvas_h, canvas_x:canvas_x+canvas_w]
        blended = cv2.addWeighted(frame_roi, 1-alpha, canvas_roi, alpha, 0)
        frame[canvas_y:canvas_y+canvas_h, canvas_x:canvas_x+canvas_w] = blended
    
    cv2.imshow('MERYEM EL OSMANI - COLOR MIXER STUDIO', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
print("🎨 Color mixing session complete! Thanks for creating art! ✨")