import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

# ================================
# MERYEM EL OSMANI PROJECT
# HOLOGRAPHIC TEXT MATRIX 🌟💫
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, 
                       min_detection_confidence=0.8, min_tracking_confidence=0.8)

# Futuristic Colors
NEON_BLUE = (255, 100, 0)
NEON_GREEN = (0, 255, 100)
NEON_PINK = (255, 0, 255)
NEON_CYAN = (255, 255, 0)
NEON_ORANGE = (0, 165, 255)
NEON_PURPLE = (255, 0, 128)
ELECTRIC_BLUE = (255, 200, 0)
LASER_RED = (0, 50, 255)

class HolographicParticle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.life = 100
        self.max_life = 100
        self.size = random.uniform(1, 4)
        self.color = random.choice([NEON_BLUE, NEON_GREEN, NEON_PINK, NEON_CYAN])
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vx *= 0.99
        self.vy *= 0.99
        return self.life > 0
    
    def draw(self, img):
        alpha = self.life / self.max_life
        if alpha > 0:
            color = tuple(int(c * alpha) for c in self.color)
            cv2.circle(img, (int(self.x), int(self.y)), int(self.size), color, -1)
            # Glow effect
            cv2.circle(img, (int(self.x), int(self.y)), int(self.size * 2), color, 1)

class HolographicText:
    def __init__(self, text, x, y, target_size=3.0):
        self.text = text
        self.x = x
        self.y = y
        self.current_size = 0.5
        self.target_size = target_size
        self.life = 300
        self.max_life = 300
        self.particles = []
        self.glow_intensity = 1.0
        self.wave_offset = random.uniform(0, math.pi * 2)
        self.creation_time = time.time()
        
        # Generate particles around text
        for i in range(20):
            px = x + random.uniform(-50, 50)
            py = y + random.uniform(-30, 30)
            self.particles.append(HolographicParticle(px, py))
    
    def update(self):
        # Smooth size animation
        self.current_size += (self.target_size - self.current_size) * 0.1
        
        # Wave effect
        current_time = time.time() - self.creation_time
        wave = math.sin(current_time * 3 + self.wave_offset) * 10
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Add new particles occasionally
        if random.random() < 0.1 and len(self.particles) < 30:
            px = self.x + random.uniform(-30, 30)
            py = self.y + random.uniform(-20, 20)
            self.particles.append(HolographicParticle(px, py))
        
        self.life -= 1
        return self.life > 0
    
    def draw(self, img):
        if self.life <= 0:
            return
            
        alpha = min(1.0, self.life / self.max_life)
        current_time = time.time() - self.creation_time
        
        # Wave position effect
        wave_y = math.sin(current_time * 2 + self.wave_offset) * 5
        wave_x = math.cos(current_time * 1.5 + self.wave_offset) * 3
        
        text_x = int(self.x + wave_x)
        text_y = int(self.y + wave_y)
        
        # Multiple glow layers for holographic effect
        colors = [NEON_CYAN, NEON_BLUE, ELECTRIC_BLUE]
        sizes = [self.current_size + 0.3, self.current_size + 0.1, self.current_size]
        
        for i, (color, size) in enumerate(zip(colors, sizes)):
            intensity = alpha * (0.3 + 0.7 / (i + 1))
            glow_color = tuple(int(c * intensity) for c in color)
            
            # Main text
            cv2.putText(img, self.text, (text_x, text_y), 
                       cv2.FONT_HERSHEY_COMPLEX, size, glow_color, 
                       3 + i, cv2.LINE_AA)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(img)
        
        # Scanlines effect
        if random.random() < 0.3:
            scan_y = text_y + random.randint(-20, 20)
            cv2.line(img, (text_x - 50, scan_y), (text_x + 200, scan_y), 
                    tuple(int(c * 0.3) for c in NEON_GREEN), 1)

class QuantumCursor:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.trail = []
        self.energy_level = 0
        self.pulse_phase = 0
        
    def update(self, new_x, new_y, energy):
        self.x = new_x
        self.y = new_y
        self.energy_level = energy
        self.pulse_phase += 0.2
        
        # Add to trail
        self.trail.append((new_x, new_y, time.time()))
        self.trail = [(x, y, t) for x, y, t in self.trail if time.time() - t < 1.0]
    
    def draw(self, img):
        # Draw energy trail
        for i in range(1, len(self.trail)):
            age = time.time() - self.trail[i][2]
            alpha = max(0, 1 - age)
            
            color = tuple(int(c * alpha) for c in NEON_CYAN)
            thickness = max(1, int(5 * alpha))
            
            cv2.line(img, self.trail[i-1][:2], self.trail[i][:2], color, thickness)
        
        # Draw cursor with pulse
        pulse = 1 + 0.3 * math.sin(self.pulse_phase)
        cursor_size = int(15 * pulse * (1 + self.energy_level))
        
        # Multi-layer cursor
        cv2.circle(img, (self.x, self.y), cursor_size, NEON_CYAN, 2)
        cv2.circle(img, (self.x, self.y), cursor_size // 2, NEON_BLUE, -1)
        cv2.circle(img, (self.x, self.y), cursor_size // 4, (255, 255, 255), -1)
        
        # Energy rings
        if self.energy_level > 0.5:
            for ring_size in range(cursor_size + 10, cursor_size + 40, 10):
                ring_alpha = max(0, 1 - (ring_size - cursor_size) / 30)
                ring_color = tuple(int(c * ring_alpha * self.energy_level) for c in NEON_PINK)
                cv2.circle(img, (self.x, self.y), ring_size, ring_color, 1)

def detect_futuristic_gestures(landmarks):
    """Advanced gesture detection for futuristic interface"""
    if not landmarks:
        return "none", 0, {}
    
    # Key points
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    
    # Count fingers
    fingers = []
    fingers.append(thumb_tip[0] > landmarks[3][0])  # Thumb
    for tip, pip in [(8,6), (12,10), (16,14), (20,18)]:
        fingers.append(landmarks[tip][1] < landmarks[pip][1])
    
    finger_count = sum(fingers)
    
    # Calculate hand energy (movement + spread)
    hand_center = np.mean(landmarks, axis=0)
    spread = np.max([np.linalg.norm(np.array(p) - hand_center) for p in landmarks])
    energy = min(1.0, spread / 100)
    
    # Gesture patterns
    pinch_dist = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))
    
    gesture_data = {
        'energy': energy,
        'spread': spread,
        'finger_count': finger_count,
        'hand_center': hand_center.astype(int)
    }
    
    if pinch_dist < 40:
        return "quantum_write", energy, gesture_data
    elif finger_count == 5 and energy > 0.7:
        return "energy_charge", energy, gesture_data
    elif finger_count == 1 and fingers[1]:  # Index only
        return "laser_point", energy, gesture_data
    elif finger_count == 2 and fingers[1] and fingers[2]:  # Peace
        return "dimension_shift", energy, gesture_data
    elif finger_count == 0:  # Fist
        return "void_clear", energy, gesture_data
    elif finger_count == 3:  # Three fingers
        return "matrix_code", energy, gesture_data
    else:
        return "scanning", energy, gesture_data

def draw_futuristic_ui(img, mode, energy_level, text_count):
    """Draw holographic UI elements"""
    h, w = img.shape[:2]
    
    # Holographic border
    border_color = tuple(int(c * (0.5 + 0.5 * math.sin(time.time() * 3))) for c in NEON_BLUE)
    cv2.rectangle(img, (10, 10), (w-10, h-10), border_color, 2)
    
    # Corner decorations
    corner_size = 30
    for corner in [(20, 20), (w-50, 20), (20, h-50), (w-50, h-50)]:
        cv2.line(img, corner, (corner[0]+corner_size, corner[1]), border_color, 3)
        cv2.line(img, corner, (corner[0], corner[1]+corner_size), border_color, 3)
    
    # Title with glow
    title = "MERYEM EL OSMANI - HOLOGRAPHIC MATRIX"
    cv2.putText(img, title, (30, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, NEON_CYAN, 3)
    cv2.putText(img, title, (30, 50), cv2.FONT_HERSHEY_COMPLEX, 1.2, (255, 255, 255), 1)
    
    # Status display
    status_y = 90
    cv2.putText(img, f"MODE: {mode.upper()}", (30, status_y), 
                cv2.FONT_HERSHEY_COMPLEX, 0.7, NEON_GREEN, 2)
    
    # Energy bar
    bar_width = 200
    energy_width = int(bar_width * energy_level)
    cv2.rectangle(img, (30, status_y + 20), (30 + bar_width, status_y + 35), NEON_BLUE, 2)
    
    if energy_width > 0:
        energy_color = NEON_GREEN if energy_level < 0.7 else NEON_PINK
        cv2.rectangle(img, (30, status_y + 20), (30 + energy_width, status_y + 35), energy_color, -1)
    
    cv2.putText(img, f"ENERGY: {int(energy_level * 100)}%", (250, status_y + 33), 
                cv2.FONT_HERSHEY_COMPLEX, 0.5, NEON_CYAN, 1)
    
    # Holographic alphabet matrix
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    matrix_start_y = h - 150
    
    cv2.putText(img, "QUANTUM ALPHABET MATRIX", (30, matrix_start_y - 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.6, NEON_PINK, 2)
    
    for i, char in enumerate(alphabet):
        x = 30 + (i % 12) * 45
        y = matrix_start_y + (i // 12) * 40
        
        # Glowing character
        glow_intensity = 0.5 + 0.5 * math.sin(time.time() * 2 + i * 0.1)
        char_color = tuple(int(c * glow_intensity) for c in NEON_GREEN)
        
        cv2.putText(img, char, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.8, char_color, 2)
        
        # Selection indicator
        cv2.rectangle(img, (x-5, y-25), (x+25, y+5), 
                     tuple(int(c * 0.3) for c in NEON_BLUE), 1)
    
    # Gesture instructions
    instructions = [
        "🤏 QUANTUM WRITE - Pinch to create holographic text",
        "✋ ENERGY CHARGE - Open hand to charge text size",
        "👆 LASER POINT - Point to select characters", 
        "✌️ DIMENSION SHIFT - Change holographic colors",
        "✊ VOID CLEAR - Clear all holograms",
        "🖖 MATRIX CODE - Three fingers for special effects"
    ]
    
    for i, instruction in enumerate(instructions):
        y_pos = 200 + i * 25
        cv2.putText(img, instruction, (w - 450, y_pos), 
                    cv2.FONT_HERSHEY_COMPLEX, 0.4, NEON_CYAN, 1)

def generate_matrix_rain(img):
    """Generate Matrix-style digital rain effect"""
    if random.random() < 0.3:
        for _ in range(5):
            x = random.randint(0, img.shape[1])
            y = random.randint(0, 50)
            char = random.choice("01")
            color = tuple(int(c * random.uniform(0.3, 1.0)) for c in NEON_GREEN)
            cv2.putText(img, char, (x, y), cv2.FONT_HERSHEY_COMPLEX, 0.5, color, 1)

# Initialize system
cap = cv2.VideoCapture(0)
holographic_texts = []
current_text = ""
quantum_cursor = None
current_energy = 0
selected_char = 'A'
char_index = 0
last_gesture_time = 0
mode = "INITIALIZING"

# Matrix characters for special effects
matrix_chars = ['0', '1', '∴', '∵', '≡', '≈', '∞', '◊', '◈', '◉']

print("🚀 MERYEM EL OSMANI'S HOLOGRAPHIC TEXT MATRIX ACTIVATED! 💫")
print("=== FUTURISTIC INTERFACE COMMANDS ===")
print("🤏 Quantum Write: Pinch fingers to create holographic text")
print("✋ Energy Charge: Open hand wide to charge text size") 
print("👆 Laser Point: Point to cycle through alphabet")
print("✌️ Dimension Shift: Peace sign to change colors")
print("✊ Void Clear: Fist to clear all holograms")
print("🖖 Matrix Code: Three fingers for special effects")
print("Experience the future of text creation! 🌟✨")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Create holographic background
    frame = cv2.addWeighted(frame, 0.7, np.zeros_like(frame), 0.3, 0)
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_time = time.time()
    
    # Generate matrix rain effect
    generate_matrix_rain(frame)
    
    # Update holographic texts
    holographic_texts = [text for text in holographic_texts if text.update()]
    for text in holographic_texts:
        text.draw(frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw holographic hand skeleton
            for connection in mp_hands.HAND_CONNECTIONS:
                start = landmarks[connection[0]]
                end = landmarks[connection[1]]
                cv2.line(frame, start, end, NEON_CYAN, 2)
            
            # Draw landmarks with glow
            for point in landmarks:
                cv2.circle(frame, point, 4, NEON_PINK, -1)
                cv2.circle(frame, point, 8, NEON_PINK, 1)
            
            gesture, energy, data = detect_futuristic_gestures(landmarks)
            current_energy = energy
            
            # Update quantum cursor
            hand_center = data.get('hand_center', landmarks[8])
            if quantum_cursor is None:
                quantum_cursor = QuantumCursor(hand_center[0], hand_center[1])
            else:
                quantum_cursor.update(hand_center[0], hand_center[1], energy)
            
            if gesture == "quantum_write":
                mode = "QUANTUM WRITING"
                if current_time - last_gesture_time > 0.5:
                    if current_text:
                        # Create holographic text
                        text_size = 2.0 + energy * 3.0
                        holo_text = HolographicText(current_text, hand_center[0], hand_center[1], text_size)
                        holographic_texts.append(holo_text)
                        print(f"✨ Holographic text created: '{current_text}' - Size: {text_size:.1f}")
                        current_text = ""
                    last_gesture_time = current_time
            
            elif gesture == "energy_charge":
                mode = "ENERGY CHARGING"
                # Visual charging effect
                for i in range(int(energy * 10)):
                    angle = (time.time() * 5 + i) % (2 * math.pi)
                    radius = 50 + i * 10
                    fx = hand_center[0] + int(radius * math.cos(angle))
                    fy = hand_center[1] + int(radius * math.sin(angle))
                    cv2.circle(frame, (fx, fy), 3, NEON_PINK, -1)
            
            elif gesture == "laser_point":
                mode = "LASER TARGETING"
                if current_time - last_gesture_time > 0.8:
                    char_index = (char_index + 1) % 36
                    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
                    selected_char = alphabet[char_index]
                    current_text += selected_char
                    last_gesture_time = current_time
                    print(f"📡 Character targeted: '{selected_char}' - Text: '{current_text}'")
                
                # Laser beam effect
                cv2.line(frame, hand_center, (hand_center[0], 50), LASER_RED, 3)
                cv2.circle(frame, (hand_center[0], 50), 10, LASER_RED, 2)
            
            elif gesture == "dimension_shift":
                mode = "DIMENSION SHIFTING"
                # Color shift all existing texts
                for text in holographic_texts:
                    text.wave_offset += 0.5
                
                # Dimension shift visual effect
                for i in range(5):
                    shift_x = random.randint(-20, 20)
                    shift_y = random.randint(-20, 20)
                    cv2.circle(frame, (hand_center[0] + shift_x, hand_center[1] + shift_y), 
                              random.randint(5, 15), random.choice([NEON_PINK, NEON_PURPLE, ELECTRIC_BLUE]), 2)
            
            elif gesture == "void_clear":
                mode = "VOID CLEARING"
                if current_time - last_gesture_time > 1.0:
                    holographic_texts = []
                    current_text = ""
                    last_gesture_time = current_time
                    print("🌀 All holograms cleared - Void activated")
                
                # Void effect
                void_radius = int(100 * (1 + math.sin(time.time() * 10)))
                cv2.circle(frame, hand_center, void_radius, (0, 0, 0), 3)
                cv2.circle(frame, hand_center, void_radius + 10, NEON_PURPLE, 2)
            
            elif gesture == "matrix_code":
                mode = "MATRIX CODING"
                # Special matrix effect
                for i in range(10):
                    mx = hand_center[0] + random.randint(-50, 50)
                    my = hand_center[1] + random.randint(-50, 50)
                    matrix_char = random.choice(matrix_chars)
                    cv2.putText(frame, matrix_char, (mx, my), cv2.FONT_HERSHEY_COMPLEX, 
                               random.uniform(0.5, 1.5), NEON_GREEN, 2)
            
            else:
                mode = "SCANNING"
    else:
        mode = "NO QUANTUM SIGNAL"
    
    # Draw quantum cursor
    if quantum_cursor:
        quantum_cursor.draw(frame)
    
    # Draw futuristic UI
    draw_futuristic_ui(frame, mode, current_energy, len(holographic_texts))
    
    # Current text preview with holographic effect
    if current_text:
        preview_y = 180
        cv2.putText(frame, f"COMPOSING: {current_text}_", (30, preview_y), 
                    cv2.FONT_HERSHEY_COMPLEX, 1.0, NEON_CYAN, 2)
        
        # Selected character highlight
        char_display = f"CURRENT: [{selected_char}]"
        cv2.putText(frame, char_display, (400, preview_y), 
                    cv2.FONT_HERSHEY_COMPLEX, 1.0, NEON_PINK, 2)
    
    cv2.imshow('MERYEM EL OSMANI - HOLOGRAPHIC TEXT MATRIX 🚀', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("🚀 Holographic session terminated. Quantum matrix deactivated! ✨💫")