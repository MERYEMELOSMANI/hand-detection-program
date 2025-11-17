import cv2
import mediapipe as mp
import numpy as np
import math
import time
import string

# ================================
# MERYEM EL OSMANI PROJECT
# AIR TEXT WRITER STUDIO ✍️📝
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                       min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
PURPLE = (255, 0, 255)
CYAN = (255, 255, 0)
ORANGE = (0, 165, 255)

# Text system
text_objects = []
current_text = ""
text_size = 2.0
text_color = WHITE
text_position = [100, 200]
is_writing = False
last_letter_time = 0
writing_trail = []

# Available characters (simplified alphabet + numbers)
characters = {
    # Letters
    'A': [[(20,50), (10,10), (30,10), (15,30), (25,30)]],
    'B': [[(10,10), (10,50), (10,10), (25,10), (25,25), (10,25), (25,25), (25,50), (10,50)]],
    'C': [[(30,10), (10,10), (10,50), (30,50)]],
    'D': [[(10,10), (10,50), (10,10), (25,15), (25,45), (10,50)]],
    'E': [[(10,10), (10,50), (10,10), (25,10), (10,30), (20,30), (10,50), (25,50)]],
    'F': [[(10,10), (10,50), (10,10), (25,10), (10,30), (20,30)]],
    'G': [[(30,10), (10,10), (10,50), (30,50), (30,30), (20,30)]],
    'H': [[(10,10), (10,50), (30,10), (30,50), (10,30), (30,30)]],
    'I': [[(15,10), (25,10), (20,10), (20,50), (15,50), (25,50)]],
    'J': [[(25,10), (25,40), (20,50), (10,40)]],
    'K': [[(10,10), (10,50), (10,30), (25,10), (10,30), (25,50)]],
    'L': [[(10,10), (10,50), (25,50)]],
    'M': [[(10,50), (10,10), (20,25), (30,10), (30,50)]],
    'N': [[(10,50), (10,10), (30,50), (30,10)]],
    'O': [[(10,15), (10,45), (15,50), (25,50), (30,45), (30,15), (25,10), (15,10), (10,15)]],
    'P': [[(10,50), (10,10), (25,10), (25,30), (10,30)]],
    'Q': [[(10,15), (10,45), (15,50), (25,50), (30,45), (30,15), (25,10), (15,10), (10,15), (22,38), (35,50)]],
    'R': [[(10,50), (10,10), (25,10), (25,30), (10,30), (25,50)]],
    'S': [[(30,20), (20,10), (10,20), (20,30), (30,40), (20,50), (10,40)]],
    'T': [[(10,10), (30,10), (20,10), (20,50)]],
    'U': [[(10,10), (10,45), (15,50), (25,50), (30,45), (30,10)]],
    'V': [[(10,10), (20,50), (30,10)]],
    'W': [[(10,10), (15,50), (20,30), (25,50), (30,10)]],
    'X': [[(10,10), (30,50), (20,30), (10,50), (30,10)]],
    'Y': [[(10,10), (20,30), (30,10), (20,30), (20,50)]],
    'Z': [[(10,10), (30,10), (10,50), (30,50)]],
    
    # Numbers
    '0': [[(10,15), (10,45), (15,50), (25,50), (30,45), (30,15), (25,10), (15,10), (10,15)]],
    '1': [[(15,15), (20,10), (20,50), (15,50), (25,50)]],
    '2': [[(10,20), (15,10), (25,10), (30,20), (20,30), (10,50), (30,50)]],
    '3': [[(10,15), (15,10), (25,10), (30,20), (25,30), (20,30), (25,30), (30,40), (25,50), (15,50), (10,45)]],
    '4': [[(10,10), (10,30), (30,30), (25,10), (25,50)]],
    '5': [[(30,10), (10,10), (10,30), (25,30), (30,40), (25,50), (10,40)]],
    '6': [[(25,10), (15,10), (10,20), (10,45), (15,50), (25,50), (30,40), (25,30), (15,30)]],
    '7': [[(10,10), (30,10), (15,50)]],
    '8': [[(15,10), (25,10), (30,15), (25,25), (15,25), (10,15), (15,10), (15,25), (10,35), (15,50), (25,50), (30,35), (25,25)]],
    '9': [[(25,50), (15,50), (10,35), (15,25), (25,25), (30,15), (25,10), (15,10), (10,20), (15,25)]],
    
    # Special characters
    ' ': [],  # Space
    '!': [[(20,10), (20,35), (20,45), (20,50)]],
    '?': [[(10,20), (15,10), (25,10), (30,20), (25,30), (20,35), (20,45), (20,50)]],
    '.': [[(20,45), (20,50)]],
    ',': [[(20,45), (15,55)]],
}

class TextObject:
    def __init__(self, text, x, y, size, color, font_style=cv2.FONT_HERSHEY_SIMPLEX):
        self.text = text
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.font_style = font_style
        self.life = 500  # How long text stays on screen
        self.alpha = 1.0
        self.created_time = time.time()
        
    def update(self):
        self.life -= 1
        self.alpha = max(0, self.life / 500.0)
        return self.life > 0
    
    def draw(self, img):
        if self.alpha > 0:
            # Create text with transparency effect
            overlay = img.copy()
            cv2.putText(overlay, self.text, (int(self.x), int(self.y)), 
                       self.font_style, self.size, self.color, 3)
            cv2.addWeighted(overlay, self.alpha, img, 1 - self.alpha, 0, img)

def detect_gesture(landmarks):
    """Detect different hand gestures for text operations"""
    if not landmarks:
        return "none", 0
    
    # Get key points
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    wrist = landmarks[0]
    
    # Count extended fingers
    fingers_up = []
    
    # Thumb
    fingers_up.append(thumb_tip[0] > landmarks[3][0])
    
    # Other fingers
    for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
        fingers_up.append(landmarks[tip][1] < landmarks[pip][1])
    
    extended_count = sum(fingers_up)
    
    # Calculate hand movement speed
    hand_center = [(thumb_tip[0] + index_tip[0]) // 2, (thumb_tip[1] + index_tip[1]) // 2]
    
    # Pinch distance for precision
    pinch_dist = math.sqrt((thumb_tip[0] - index_tip[0])**2 + (thumb_tip[1] - index_tip[1])**2)
    
    # Gesture recognition
    if pinch_dist < 30:
        return "writing", pinch_dist
    elif extended_count == 5:
        # All fingers extended - size control
        hand_spread = max(
            math.sqrt((thumb_tip[0] - pinky_tip[0])**2 + (thumb_tip[1] - pinky_tip[1])**2),
            math.sqrt((index_tip[0] - ring_tip[0])**2 + (index_tip[1] - ring_tip[1])**2)
        )
        return "sizing", hand_spread
    elif extended_count == 1 and fingers_up[1]:  # Only index
        return "pointing", 0
    elif extended_count == 2 and fingers_up[1] and fingers_up[2]:  # Peace sign
        return "color_change", 0
    elif extended_count == 0:  # Fist
        return "clear", 0
    else:
        return "none", 0

def draw_virtual_keyboard(img, selected_char=''):
    """Draw a virtual keyboard for character selection"""
    keyboard_layout = [
        "ABCDEFGHIJ",
        "KLMNOPQRST", 
        "UVWXYZ0123",
        "456789!?. "
    ]
    
    start_x = 50
    start_y = img.shape[0] - 200
    key_width = 45
    key_height = 35
    
    for row_idx, row in enumerate(keyboard_layout):
        for col_idx, char in enumerate(row):
            x = start_x + col_idx * key_width
            y = start_y + row_idx * key_height
            
            # Highlight selected character
            if char == selected_char:
                cv2.rectangle(img, (x, y), (x + key_width - 5, y + key_height - 5), YELLOW, -1)
                text_color = BLACK
            else:
                cv2.rectangle(img, (x, y), (x + key_width - 5, y + key_height - 5), (100, 100, 100), 2)
                text_color = WHITE
            
            # Draw character
            if char != ' ':
                cv2.putText(img, char, (x + 10, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.7, text_color, 2)
            else:
                cv2.putText(img, "SPC", (x + 5, y + 25), cv2.FONT_HERSHEY_SIMPLEX, 0.4, text_color, 1)

def get_selected_character(hand_pos, img_shape):
    """Get character from virtual keyboard based on hand position"""
    keyboard_layout = [
        "ABCDEFGHIJ",
        "KLMNOPQRST", 
        "UVWXYZ0123",
        "456789!?. "
    ]
    
    start_x = 50
    start_y = img_shape[0] - 200
    key_width = 45
    key_height = 35
    
    for row_idx, row in enumerate(keyboard_layout):
        for col_idx, char in enumerate(row):
            x = start_x + col_idx * key_width
            y = start_y + row_idx * key_height
            
            if x <= hand_pos[0] <= x + key_width and y <= hand_pos[1] <= y + key_height:
                return char
    return ''

def draw_text_preview(img, text, position, size, color):
    """Draw preview of current text being composed"""
    if text:
        cv2.putText(img, text + "_", position, cv2.FONT_HERSHEY_SIMPLEX, size, color, 3)

def draw_ui_elements(img, current_size, current_color, mode):
    """Draw UI elements showing current settings"""
    # Title
    cv2.putText(img, 'MERYEM EL OSMANI - AIR TEXT WRITER', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    
    # Current settings
    cv2.putText(img, f'Size: {current_size:.1f}', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    cv2.rectangle(img, (120, 55), (150, 75), current_color, -1)
    cv2.rectangle(img, (120, 55), (150, 75), WHITE, 2)
    
    # Mode indicator
    mode_text = f'Mode: {mode.upper()}'
    cv2.putText(img, mode_text, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.6, YELLOW, 2)
    
    # Instructions
    instructions = [
        "🤏 PINCH = Write Mode",
        "✋ OPEN HAND = Resize Text", 
        "👆 POINT = Select Character",
        "✌️ PEACE = Change Color",
        "✊ FIST = Clear All"
    ]
    
    for i, instruction in enumerate(instructions):
        cv2.putText(img, instruction, (img.shape[1] - 300, 60 + i * 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1)

# Initialize
cap = cv2.VideoCapture(0)
color_cycle = [WHITE, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE]
color_index = 0
selected_char = ''
char_selection_timer = 0
mode = "ready"

print("✍️ MERYEM EL OSMANI'S AIR TEXT WRITER ACTIVATED! 📝")
print("Instructions:")
print("🤏 Pinch fingers together to enter writing mode")
print("👆 Point to select characters from keyboard")
print("✋ Open hand wide to resize text")
print("✌️ Peace sign to cycle colors") 
print("✊ Fist to clear all text")
print("Create amazing floating text art!")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_time = time.time()
    
    # Update existing text objects
    text_objects = [obj for obj in text_objects if obj.update()]
    
    # Draw existing text
    for text_obj in text_objects:
        text_obj.draw(frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw hand skeleton
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            gesture, value = detect_gesture(landmarks)
            hand_pos = landmarks[8]  # Index finger tip
            
            if gesture == "writing":
                mode = "writing"
                is_writing = True
                
                # Add to writing trail
                writing_trail.append(hand_pos)
                if len(writing_trail) > 20:
                    writing_trail.pop(0)
                
                # Draw writing trail
                for i in range(1, len(writing_trail)):
                    cv2.line(frame, writing_trail[i-1], writing_trail[i], text_color, 3)
                
                cv2.putText(frame, "WRITING MODE", (hand_pos[0] - 80, hand_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            
            elif gesture == "sizing":
                mode = "sizing"
                # Map hand spread to text size (20-200 pixels spread to 0.5-5.0 size)
                text_size = max(0.5, min(5.0, (value - 20) / 40 + 0.5))
                
                cv2.putText(frame, f"SIZE: {text_size:.1f}", (hand_pos[0] - 50, hand_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, text_size/3, WHITE, 2)
            
            elif gesture == "pointing":
                mode = "selecting"
                # Character selection from virtual keyboard
                selected_char = get_selected_character(hand_pos, frame.shape)
                
                if selected_char:
                    char_selection_timer += 1
                    if char_selection_timer > 30:  # Hold for 1 second
                        current_text += selected_char if selected_char != ' ' else ' '
                        char_selection_timer = 0
                        print(f"✍️ Added character: '{selected_char}' - Current text: '{current_text}'")
                else:
                    char_selection_timer = 0
                
                cv2.putText(frame, "SELECT CHAR", (hand_pos[0] - 60, hand_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, YELLOW, 2)
            
            elif gesture == "color_change":
                mode = "color"
                if current_time - last_letter_time > 1.0:
                    color_index = (color_index + 1) % len(color_cycle)
                    text_color = color_cycle[color_index]
                    last_letter_time = current_time
                    print(f"🎨 Color changed to: {color_index}")
                
                cv2.putText(frame, "COLOR CHANGE", (hand_pos[0] - 70, hand_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            
            elif gesture == "clear":
                mode = "clearing"
                if current_time - last_letter_time > 1.0:
                    text_objects = []
                    current_text = ""
                    writing_trail = []
                    last_letter_time = current_time
                    print("🧹 All text cleared!")
                
                cv2.putText(frame, "CLEARING", (hand_pos[0] - 50, hand_pos[1] - 40), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED, 2)
            else:
                mode = "ready"
                is_writing = False
                
                # Finalize current text if any
                if current_text and current_time - last_letter_time > 2.0:
                    text_objects.append(TextObject(current_text, hand_pos[0], hand_pos[1], 
                                                 text_size, text_color))
                    print(f"📝 Text finalized: '{current_text}'")
                    current_text = ""
                    last_letter_time = current_time
    else:
        mode = "no_hand"
    
    # Draw UI elements
    draw_ui_elements(frame, text_size, text_color, mode)
    
    # Draw virtual keyboard
    draw_virtual_keyboard(frame, selected_char)
    
    # Draw current text preview
    if current_text:
        text_pos = [50, 150]
        draw_text_preview(frame, current_text, tuple(text_pos), text_size, text_color)
        
        # Progress bar for character selection
        if char_selection_timer > 0:
            progress = min(1.0, char_selection_timer / 30.0)
            bar_width = int(200 * progress)
            cv2.rectangle(frame, (50, 160), (50 + bar_width, 170), YELLOW, -1)
            cv2.rectangle(frame, (50, 160), (250, 170), WHITE, 2)
    
    cv2.imshow('MERYEM EL OSMANI - AIR TEXT WRITER STUDIO', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
print("✍️ Text writing session complete! Amazing work! 📝✨")