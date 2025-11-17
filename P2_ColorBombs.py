import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random

# ================================
# MERYEM EL OSMANI PROJECT
# COLOR BOMB EXPLOSION STUDIO 💥🎨
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                       min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Color Palette 🎨
FIRE_RED = (0, 50, 255)
OCEAN_BLUE = (255, 150, 50)
FOREST_GREEN = (50, 200, 50)
SUNSET_ORANGE = (0, 150, 255)
ROYAL_PURPLE = (200, 50, 150)
GOLDEN_YELLOW = (0, 220, 255)
PINK_BLAST = (150, 100, 255)
CYBER_CYAN = (255, 255, 100)

color_bombs = [FIRE_RED, OCEAN_BLUE, FOREST_GREEN, SUNSET_ORANGE, ROYAL_PURPLE, GOLDEN_YELLOW, PINK_BLAST, CYBER_CYAN]
color_names = ["FIRE", "OCEAN", "FOREST", "SUNSET", "ROYAL", "GOLDEN", "PINK", "CYBER"]

# Explosion system
explosions = []
color_trails = []
current_color = FIRE_RED
color_index = 0
throw_power = 0
charging = False
last_throw_time = 0
canvas_colors = np.zeros((480, 640, 3), dtype=np.uint8)

class ColorExplosion:
    def __init__(self, x, y, color, size=30):
        self.x = x
        self.y = y
        self.color = color
        self.particles = []
        self.size = size
        self.life = 100
        
        # Create explosion particles
        for _ in range(random.randint(15, 25)):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(60, 100),
                'size': random.randint(3, 8),
                'color': color
            })
    
    def update(self):
        self.life -= 2
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['vy'] += 0.1  # gravity
            particle['vx'] *= 0.98  # friction
            particle['life'] -= 1
            particle['size'] = max(1, particle['size'] - 0.05)
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        return len(self.particles) > 0 or self.life > 0
    
    def draw(self, img):
        # Draw main explosion flash
        if self.life > 80:
            cv2.circle(img, (int(self.x), int(self.y)), self.size, (255, 255, 255), -1)
        
        # Draw particles
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = particle['life'] / 100.0
                size = int(particle['size'])
                pos = (int(particle['x']), int(particle['y']))
                
                # Draw with glow effect
                cv2.circle(img, pos, size + 2, (50, 50, 50), -1)
                cv2.circle(img, pos, size, particle['color'], -1)

class ColorBomb:
    def __init__(self, start_x, start_y, target_x, target_y, color, power):
        self.x = start_x
        self.y = start_y
        self.color = color
        self.power = power
        
        # Calculate trajectory
        distance = math.sqrt((target_x - start_x)**2 + (target_y - start_y)**2)
        self.speed = min(15, power * 2)
        
        if distance > 0:
            self.vx = (target_x - start_x) / distance * self.speed
            self.vy = (target_y - start_y) / distance * self.speed
        else:
            self.vx = self.vy = 0
        
        self.trail = []
        self.life = 100
    
    def update(self):
        # Update position
        self.x += self.vx
        self.y += self.vy
        
        # Add to trail
        self.trail.append((int(self.x), int(self.y), self.color))
        if len(self.trail) > 10:
            self.trail.pop(0)
        
        self.life -= 3
        return self.life > 0
    
    def draw(self, img):
        # Draw trail
        for i, (x, y, color) in enumerate(self.trail):
            alpha = (i + 1) / len(self.trail)
            size = int(alpha * 8)
            cv2.circle(img, (x, y), size, color, -1)
        
        # Draw bomb
        cv2.circle(img, (int(self.x), int(self.y)), 12, self.color, -1)
        cv2.circle(img, (int(self.x), int(self.y)), 15, (255, 255, 255), 2)

def detect_gesture(landmarks):
    """Detect throwing gesture"""
    if not landmarks:
        return "none", 0
    
    # Get key points
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    thumb_tip = landmarks[4]
    wrist = landmarks[0]
    
    # Count extended fingers
    fingers_up = 0
    if index_tip[1] < landmarks[6][1]: fingers_up += 1
    if middle_tip[1] < landmarks[10][1]: fingers_up += 1
    if ring_tip[1] < landmarks[14][1]: fingers_up += 1
    if pinky_tip[1] < landmarks[18][1]: fingers_up += 1
    if thumb_tip[0] > landmarks[3][0]: fingers_up += 1
    
    # Calculate hand velocity (simplified)
    hand_center_y = (index_tip[1] + thumb_tip[1]) / 2
    velocity = abs(wrist[1] - hand_center_y) / 100
    
    if fingers_up >= 4:
        return "charging", min(10, velocity * 5)
    elif fingers_up <= 2:
        return "throw", min(10, velocity * 8)
    else:
        return "aiming", 0

def draw_color_wheel(img, center, radius):
    """Draw rotating color selection wheel"""
    time_factor = time.time() * 2
    
    for i, (color, name) in enumerate(zip(color_bombs, color_names)):
        angle = (i * 45 + time_factor * 30) % 360
        x = int(center[0] + radius * math.cos(math.radians(angle)))
        y = int(center[1] + radius * math.sin(math.radians(angle)))
        
        # Highlight current color
        size = 25 if i == color_index else 15
        border_color = (255, 255, 255) if i == color_index else color
        
        cv2.circle(img, (x, y), size, color, -1)
        cv2.circle(img, (x, y), size + 3, border_color, 2)
        
        # Draw color name for selected
        if i == color_index:
            cv2.putText(img, name, (x - 30, y - 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def draw_power_meter(img, power, x, y):
    """Draw charging power meter"""
    meter_width = 200
    meter_height = 20
    
    # Background
    cv2.rectangle(img, (x, y), (x + meter_width, y + meter_height), (50, 50, 50), -1)
    cv2.rectangle(img, (x, y), (x + meter_width, y + meter_height), (255, 255, 255), 2)
    
    # Power bar
    power_width = int((power / 10.0) * meter_width)
    if power_width > 0:
        color = (0, 255, 0) if power < 7 else (0, 255, 255) if power < 9 else (0, 100, 255)
        cv2.rectangle(img, (x + 2, y + 2), (x + power_width, y + meter_height - 2), color, -1)
    
    # Label
    cv2.putText(img, f"POWER: {int(power)}/10", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

def mix_colors_at_point(img, x, y, new_color, radius=30):
    """Mix new color with existing colors at explosion point"""
    h, w = img.shape[:2]
    x, y = int(x), int(y)
    
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            if dx*dx + dy*dy <= radius*radius:
                px, py = x + dx, y + dy
                if 0 <= px < w and 0 <= py < h:
                    distance = math.sqrt(dx*dx + dy*dy)
                    intensity = max(0, 1 - distance / radius)
                    
                    # Get existing color
                    existing = img[py, px]
                    
                    # Mix colors
                    mixed = [
                        int(existing[i] * (1 - intensity) + new_color[i] * intensity)
                        for i in range(3)
                    ]
                    img[py, px] = mixed

# Initialize
cap = cv2.VideoCapture(0)
bombs = []
frame_count = 0

print("💥 MERYEM EL OSMANI'S COLOR BOMB STUDIO ACTIVATED! 🎨")
print("How to use:")
print("✋ Open hand = Charge power")
print("✊ Close fist = Throw color bomb")
print("👆 Point = Change color (automatic rotation)")
print("💥 Create amazing color explosions!")
print("Press ESC to exit")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    frame_count += 1
    current_time = time.time()
    
    # Auto-rotate color selection
    if frame_count % 60 == 0:  # Change color every 2 seconds
        color_index = (color_index + 1) % len(color_bombs)
        current_color = color_bombs[color_index]
    
    # Resize canvas if needed
    if canvas_colors.shape[:2] != (h, w):
        canvas_colors = cv2.resize(canvas_colors, (w, h))
    
    # Update explosions
    explosions = [exp for exp in explosions if exp.update()]
    
    # Update bombs
    for bomb in bombs[:]:
        if not bomb.update():
            # Bomb exploded
            explosions.append(ColorExplosion(bomb.x, bomb.y, bomb.color, int(bomb.power * 3)))
            mix_colors_at_point(canvas_colors, bomb.x, bomb.y, bomb.color, int(bomb.power * 5))
            bombs.remove(bomb)
    
    # Blend canvas with frame
    alpha = 0.6
    frame = cv2.addWeighted(frame, 1 - alpha, canvas_colors, alpha, 0)
    
    # Draw explosions
    for explosion in explosions:
        explosion.draw(frame)
    
    # Draw bombs
    for bomb in bombs:
        bomb.draw(frame)
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw hand skeleton
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            gesture, power = detect_gesture(landmarks)
            hand_center = landmarks[9]
            
            if gesture == "charging":
                charging = True
                throw_power = min(10, throw_power + 0.3)
                
                # Visual charging effect
                for i in range(int(throw_power)):
                    angle = random.uniform(0, 2 * math.pi)
                    radius = random.uniform(20, 40)
                    px = int(hand_center[0] + math.cos(angle) * radius)
                    py = int(hand_center[1] + math.sin(angle) * radius)
                    cv2.circle(frame, (px, py), 3, current_color, -1)
                
                cv2.putText(frame, "CHARGING...", (hand_center[0] - 50, hand_center[1] - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            elif gesture == "throw" and charging and throw_power > 1:
                # Throw bomb
                if current_time - last_throw_time > 0.5:
                    target_x = hand_center[0] + random.randint(-100, 100)
                    target_y = hand_center[1] + random.randint(-100, 100)
                    
                    bombs.append(ColorBomb(hand_center[0], hand_center[1], 
                                         target_x, target_y, current_color, throw_power))
                    
                    print(f"💥 {color_names[color_index]} BOMB THROWN! Power: {int(throw_power)}")
                    
                    last_throw_time = current_time
                    charging = False
                    throw_power = 0
                
                cv2.putText(frame, "BOOM!", (hand_center[0] - 30, hand_center[1] - 60), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, current_color, 3)
            else:
                charging = False
                throw_power = max(0, throw_power - 0.1)
    
    # UI Elements
    cv2.putText(frame, 'MERYEM EL OSMANI - COLOR BOMB STUDIO', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    
    # Draw color wheel
    draw_color_wheel(frame, (100, h - 100), 60)
    
    # Draw power meter
    if charging or throw_power > 0:
        draw_power_meter(frame, throw_power, w - 250, 50)
    
    # Instructions
    instructions = [
        "✋ OPEN HAND = CHARGE",
        "✊ CLOSE FIST = THROW",
        f"🎨 CURRENT: {color_names[color_index]}"
    ]
    
    for i, instruction in enumerate(instructions):
        cv2.putText(frame, instruction, (w - 300, h - 120 + i * 25), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('MERYEM EL OSMANI - COLOR BOMB EXPLOSION STUDIO', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
print("💥 Epic color bombing session complete! 🎨✨")