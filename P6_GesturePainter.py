import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

# ================================
# MERYEM EL OSMANI PROJECT
# DIGITAL GESTURE PAINTER 🎨✨
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, 
                       min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Beautiful Color Palette
COLORS = {
    'coral': (127, 255, 212),
    'sky': (250, 206, 135),  
    'lavender': (255, 182, 193),
    'mint': (152, 251, 152),
    'peach': (255, 218, 185),
    'rose': (255, 192, 203),
    'gold': (255, 215, 0),
    'turquoise': (224, 255, 255),
    'sunset': (255, 94, 77),
    'ocean': (72, 209, 204)
}

COLOR_LIST = list(COLORS.values())
COLOR_NAMES = list(COLORS.keys())

class Brush:
    def __init__(self):
        self.size = 15
        self.color = COLOR_LIST[0]
        self.opacity = 255
        self.style = "normal"  # normal, spray, glow, rainbow
        self.trail = []
        
    def update_trail(self, x, y):
        self.trail.append((x, y, time.time()))
        # Keep only recent points
        self.trail = [(px, py, t) for px, py, t in self.trail if time.time() - t < 2.0]

class Canvas:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        self.canvas.fill(20)  # Dark background
        self.temp_canvas = self.canvas.copy()
        
    def clear(self):
        self.canvas.fill(20)
        self.temp_canvas = self.canvas.copy()
    
    def draw_line(self, start, end, brush):
        if brush.style == "normal":
            cv2.line(self.canvas, start, end, brush.color, brush.size)
        elif brush.style == "glow":
            # Multiple layers for glow effect
            for i in range(5):
                size = brush.size + i * 3
                alpha = 1.0 / (i + 1)
                color = tuple(int(c * alpha) for c in brush.color)
                cv2.line(self.canvas, start, end, color, size)
        elif brush.style == "spray":
            # Spray paint effect
            distance = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            for i in range(int(distance)):
                t = i / distance if distance > 0 else 0
                x = int(start[0] + (end[0] - start[0]) * t)
                y = int(start[1] + (end[1] - start[1]) * t)
                
                # Random spray particles
                for _ in range(brush.size // 3):
                    offset_x = random.randint(-brush.size, brush.size)
                    offset_y = random.randint(-brush.size, brush.size)
                    px = max(0, min(self.width-1, x + offset_x))
                    py = max(0, min(self.height-1, y + offset_y))
                    cv2.circle(self.canvas, (px, py), random.randint(1, 3), brush.color, -1)
        elif brush.style == "rainbow":
            # Rainbow effect
            hue = (time.time() * 100) % 360
            hsv = np.array([[[hue, 255, 255]]], dtype=np.uint8)
            rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0][0]
            rainbow_color = (int(rgb[0]), int(rgb[1]), int(rgb[2]))
            cv2.line(self.canvas, start, end, rainbow_color, brush.size)
    
    def draw_circle(self, center, radius, brush):
        if brush.style == "glow":
            for i in range(5):
                size = radius + i * 2
                alpha = 1.0 / (i + 1)
                color = tuple(int(c * alpha) for c in brush.color)
                cv2.circle(self.canvas, center, size, color, 2)
        else:
            cv2.circle(self.canvas, center, radius, brush.color, -1)

def detect_painting_gestures(landmarks):
    """Detect gestures for painting"""
    if not landmarks:
        return "none", {}
    
    # Key points
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Finger states
    fingers = []
    fingers.append(thumb_tip[0] > landmarks[3][0])  # Thumb
    for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
        fingers.append(landmarks[tip][1] < landmarks[pip][1])
    
    finger_count = sum(fingers)
    
    # Gesture data
    gesture_data = {
        'index_tip': index_tip,
        'finger_count': finger_count,
        'hand_center': [(thumb_tip[0] + index_tip[0]) // 2, (thumb_tip[1] + index_tip[1]) // 2]
    }
    
    # Pinch distance
    pinch_dist = math.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
    
    if pinch_dist < 40:
        return "paint", gesture_data
    elif finger_count == 1 and fingers[1]:  # Index only
        return "paint_fine", gesture_data
    elif finger_count == 2 and fingers[1] and fingers[2]:  # Peace
        return "change_color", gesture_data
    elif finger_count == 5:  # Open hand
        return "change_brush", gesture_data
    elif finger_count == 0:  # Fist
        return "clear_canvas", gesture_data
    elif finger_count == 3 and fingers[1] and fingers[2] and fingers[3]:  # Three fingers
        return "stamp_mode", gesture_data
    else:
        return "hover", gesture_data

def draw_palette(img, current_color_index, brush):
    """Draw color palette"""
    palette_y = img.shape[0] - 100
    
    # Background for palette
    cv2.rectangle(img, (20, palette_y - 20), (img.shape[1] - 20, img.shape[0] - 20), 
                 (40, 40, 40), -1)
    cv2.rectangle(img, (20, palette_y - 20), (img.shape[1] - 20, img.shape[0] - 20), 
                 (255, 255, 255), 2)
    
    cv2.putText(img, "COLOR PALETTE", (30, palette_y - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Draw color swatches
    for i, (color, name) in enumerate(zip(COLOR_LIST, COLOR_NAMES)):
        x = 40 + i * 60
        y = palette_y + 20
        
        # Highlight current color
        if i == current_color_index:
            cv2.rectangle(img, (x-5, y-5), (x+35, y+35), (255, 255, 255), 3)
        
        cv2.rectangle(img, (x, y), (x+30, y+30), color, -1)
        cv2.rectangle(img, (x, y), (x+30, y+30), (255, 255, 255), 1)
        
        # Color name
        cv2.putText(img, name[:4], (x-2, y+45), cv2.FONT_HERSHEY_SIMPLEX, 0.3, 
                   (255, 255, 255), 1)
    
    # Brush info
    brush_info_x = img.shape[1] - 200
    cv2.putText(img, f"BRUSH: {brush.style.upper()}", (brush_info_x, palette_y + 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(img, f"SIZE: {brush.size}", (brush_info_x, palette_y + 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    # Draw brush preview
    cv2.circle(img, (brush_info_x + 100, palette_y + 20), brush.size // 2, brush.color, -1)
    cv2.circle(img, (brush_info_x + 100, palette_y + 20), brush.size // 2, (255, 255, 255), 1)

def draw_instructions(img):
    """Draw gesture instructions"""
    instructions = [
        "🤏 PINCH = Paint with brush",
        "👆 POINT = Fine detail painting", 
        "✌️ PEACE = Change color",
        "✋ OPEN HAND = Change brush style",
        "✊ FIST = Clear canvas",
        "🖖 THREE FINGERS = Stamp mode"
    ]
    
    for i, instruction in enumerate(instructions):
        y_pos = 80 + i * 25
        cv2.putText(img, instruction, (img.shape[1] - 350, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

def create_magical_effects(img, position, effect_type="sparkle"):
    """Add magical painting effects"""
    x, y = position
    
    if effect_type == "sparkle":
        for _ in range(5):
            offset_x = random.randint(-20, 20)
            offset_y = random.randint(-20, 20)
            px = max(0, min(img.shape[1]-1, x + offset_x))
            py = max(0, min(img.shape[0]-1, y + offset_y))
            
            cv2.circle(img, (px, py), random.randint(1, 3), 
                      (255, 255, random.randint(200, 255)), -1)
    
    elif effect_type == "glow":
        for radius in range(10, 30, 5):
            alpha = 1.0 - (radius - 10) / 20.0
            color = tuple(int(255 * alpha) for _ in range(3))
            cv2.circle(img, (x, y), radius, color, 1)

# Initialize
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    h, w, _ = frame.shape
    canvas = Canvas(w, h)
else:
    canvas = Canvas(640, 480)
    
brush = Brush()
current_color_index = 0
brush_styles = ["normal", "glow", "spray", "rainbow"]
current_brush_index = 0
last_gesture_time = 0
painting_mode = "ready"
last_paint_pos = None

print("🎨 MERYEM EL OSMANI'S DIGITAL GESTURE PAINTER ACTIVATED! ✨")
print("=== ARTISTIC GESTURE COMMANDS ===")
print("🤏 Pinch: Paint with current brush")
print("👆 Point: Fine detail painting")
print("✌️ Peace: Cycle through beautiful colors")
print("✋ Open Hand: Change brush style (normal/glow/spray/rainbow)")
print("✊ Fist: Clear canvas for new masterpiece")
print("🖖 Three Fingers: Special stamp mode")
print("Create beautiful digital art with your hands! 🌟")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_time = time.time()
    
    # Create display with canvas overlay
    display = frame.copy()
    
    # Blend canvas with camera feed
    alpha = 0.7
    blended = cv2.addWeighted(display, 1-alpha, canvas.canvas, alpha, 0)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw elegant hand skeleton
            mp_drawing.draw_landmarks(blended, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2),
                                    mp_drawing.DrawingSpec(color=(200, 200, 200), thickness=2))
            
            gesture, data = detect_painting_gestures(landmarks)
            
            if gesture == "paint":
                painting_mode = "painting"
                current_pos = data['index_tip']
                brush.update_trail(current_pos[0], current_pos[1])
                
                if last_paint_pos:
                    canvas.draw_line(last_paint_pos, current_pos, brush)
                
                last_paint_pos = current_pos
                
                # Magical painting effects
                create_magical_effects(blended, current_pos, "sparkle")
                cv2.circle(blended, current_pos, brush.size, brush.color, 2)
            
            elif gesture == "paint_fine":
                painting_mode = "fine_painting"
                current_pos = data['index_tip']
                
                # Fine painting with smaller brush
                temp_brush = Brush()
                temp_brush.size = max(3, brush.size // 3)
                temp_brush.color = brush.color
                temp_brush.style = "normal"
                
                if last_paint_pos:
                    canvas.draw_line(last_paint_pos, current_pos, temp_brush)
                
                last_paint_pos = current_pos
                cv2.circle(blended, current_pos, temp_brush.size, brush.color, -1)
            
            elif gesture == "change_color":
                painting_mode = "color_selecting"
                if current_time - last_gesture_time > 0.8:
                    current_color_index = (current_color_index + 1) % len(COLOR_LIST)
                    brush.color = COLOR_LIST[current_color_index]
                    last_gesture_time = current_time
                    print(f"🎨 Color changed to: {COLOR_NAMES[current_color_index]}")
                
                # Show color change effect
                cv2.circle(blended, data['hand_center'], 50, brush.color, 5)
            
            elif gesture == "change_brush":
                painting_mode = "brush_changing"
                if current_time - last_gesture_time > 1.0:
                    current_brush_index = (current_brush_index + 1) % len(brush_styles)
                    brush.style = brush_styles[current_brush_index]
                    # Adjust size based on style
                    if brush.style == "spray":
                        brush.size = max(20, brush.size)
                    elif brush.style == "glow":
                        brush.size = max(15, brush.size)
                    last_gesture_time = current_time
                    print(f"🖌️ Brush style: {brush.style}")
                
                # Show brush change effect
                for i in range(data['finger_count']):
                    angle = i * (360 / data['finger_count'])
                    rad = math.radians(angle + time.time() * 100)
                    fx = data['hand_center'][0] + int(30 * math.cos(rad))
                    fy = data['hand_center'][1] + int(30 * math.sin(rad))
                    cv2.circle(blended, (fx, fy), 8, brush.color, -1)
            
            elif gesture == "clear_canvas":
                painting_mode = "clearing"
                if current_time - last_gesture_time > 1.5:
                    canvas.clear()
                    last_gesture_time = current_time
                    print("🗑️ Canvas cleared - ready for new masterpiece!")
                
                # Clear effect
                clear_radius = int(50 + 20 * math.sin(time.time() * 10))
                cv2.circle(blended, data['hand_center'], clear_radius, (255, 0, 0), 3)
            
            elif gesture == "stamp_mode":
                painting_mode = "stamping"
                if current_time - last_gesture_time > 0.6:
                    # Create decorative stamp
                    center = data['hand_center']
                    canvas.draw_circle(center, brush.size, brush)
                    
                    # Add decorative elements
                    for angle in range(0, 360, 45):
                        rad = math.radians(angle)
                        fx = center[0] + int(brush.size * 1.5 * math.cos(rad))
                        fy = center[1] + int(brush.size * 1.5 * math.sin(rad))
                        canvas.draw_circle((fx, fy), brush.size // 3, brush)
                    
                    last_gesture_time = current_time
                    print("⭐ Decorative stamp created!")
                
                # Show stamp preview
                cv2.circle(blended, data['hand_center'], brush.size, brush.color, 2)
                for angle in range(0, 360, 45):
                    rad = math.radians(angle)
                    fx = data['hand_center'][0] + int(brush.size * 1.5 * math.cos(rad))
                    fy = data['hand_center'][1] + int(brush.size * 1.5 * math.sin(rad))
                    cv2.circle(blended, (fx, fy), brush.size // 3, brush.color, 1)
            
            else:
                painting_mode = "ready"
                last_paint_pos = None
    else:
        painting_mode = "no_hand"
        last_paint_pos = None
    
    # Update canvas blend
    blended = cv2.addWeighted(frame, 1-alpha, canvas.canvas, alpha, 0)
    
    # Draw UI elements
    cv2.putText(blended, 'MERYEM EL OSMANI - DIGITAL PAINTER', (20, 40), 
                cv2.FONT_HERSHEY_COMPLEX, 1.0, (255, 255, 255), 2)
    
    cv2.putText(blended, f'MODE: {painting_mode.upper()}', (20, 70), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    
    draw_palette(blended, current_color_index, brush)
    draw_instructions(blended)
    
    cv2.imshow('MERYEM EL OSMANI - DIGITAL GESTURE PAINTER 🎨', blended)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("🎨 Painting session complete! Your digital artwork is magnificent! ✨🌟")