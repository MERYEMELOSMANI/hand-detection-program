import cv2
import mediapipe as mp
import numpy as np
import random
import math
import time

# ================================
# MERYEM EL OSMANI PROJECT
# MAGIC SPELL CASTING SYSTEM 🔮✨
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, 
                       min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Magic Colors 🎨
FIRE = (0, 100, 255)      # Red-Orange
ICE = (255, 200, 100)     # Light Blue  
LIGHTNING = (0, 255, 255) # Yellow
HEALING = (100, 255, 100) # Green
SHADOW = (100, 50, 150)   # Purple
WHITE = (255, 255, 255)
GOLD = (0, 215, 255)      # Golden

# Particle system
particles = []
spell_history = []
current_spell = None
spell_start_time = 0
spell_cooldown = 0
combo_count = 0

class Particle:
    def __init__(self, x, y, color, spell_type):
        self.x = x + random.randint(-30, 30)
        self.y = y + random.randint(-30, 30)
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -2)
        self.color = color
        self.life = 60
        self.size = random.randint(3, 8)
        self.spell_type = spell_type
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.spell_type == 'fire':
            self.vy += 0.1  # fire rises
        elif self.spell_type == 'ice':
            self.vy += 0.3  # ice falls faster
        elif self.spell_type == 'lightning':
            self.vx += random.uniform(-1, 1)  # lightning jitters
        else:
            self.vy += 0.2  # normal gravity
        
        self.life -= 1
        self.size = max(1, self.size - 0.1)
        return self.life > 0

def create_spell_particles(x, y, spell_type, color, count=20):
    for _ in range(count):
        particles.append(Particle(x, y, color, spell_type))

def draw_magic_circle(img, center, radius, color, spell_type, intensity=1.0):
    time_factor = time.time() * 3
    
    # Main rotating circle
    for i in range(int(12 * intensity)):
        angle = (time_factor + i * 30) % 360
        x = int(center[0] + radius * math.cos(math.radians(angle)))
        y = int(center[1] + radius * math.sin(math.radians(angle)))
        cv2.circle(img, (x, y), int(6 * intensity), color, -1)
    
    # Inner circles
    cv2.circle(img, center, int(radius * 0.7), color, int(3 * intensity))
    cv2.circle(img, center, int(radius * 0.5), color, int(2 * intensity))
    
    # Spell-specific symbols
    if spell_type == 'fire':
        for i in range(8):
            angle = (time_factor * 2 + i * 45) % 360
            x1 = int(center[0] + radius * 0.3 * math.cos(math.radians(angle)))
            y1 = int(center[1] + radius * 0.3 * math.sin(math.radians(angle)))
            x2 = int(center[0] + radius * 0.6 * math.cos(math.radians(angle)))
            y2 = int(center[1] + radius * 0.6 * math.sin(math.radians(angle)))
            cv2.line(img, (x1, y1), (x2, y2), color, max(1, int(3 * intensity)))
    elif spell_type == 'ice':
        for i in range(6):
            angle = i * 60
            x1 = int(center[0] + radius * 0.4 * math.cos(math.radians(angle)))
            y1 = int(center[1] + radius * 0.4 * math.sin(math.radians(angle)))
            x2 = int(center[0] + radius * 0.6 * math.cos(math.radians(angle)))
            y2 = int(center[1] + radius * 0.6 * math.sin(math.radians(angle)))
            cv2.line(img, (x1, y1), (x2, y2), color, max(1, int(2 * intensity)))

def detect_spell(landmarks):
    if not landmarks:
        return None
    
    # Get key points
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    middle_tip = landmarks[12]
    ring_tip = landmarks[16]
    pinky_tip = landmarks[20]
    palm = landmarks[9]
    
    # Calculate distances
    palm_to_tips = [np.linalg.norm(np.array(tip) - np.array(palm)) for tip in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]]
    avg_distance = np.mean(palm_to_tips)
    
    # Pinch detection
    pinch_dist = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))
    
    # Spell detection logic
    if avg_distance > 80:  # Open hand
        return "lightning"  # ⚡ Lightning Bolt
    elif pinch_dist < 30:  # Tight pinch
        return "fire"       # 🔥 Fire Ball
    elif avg_distance < 40:  # Closed fist
        return "shadow"     # 🌑 Shadow Blast
    elif palm_to_tips[1] > 70 and palm_to_tips[2] > 70 and palm_to_tips[3] < 50:  # Peace sign
        return "healing"    # 💚 Healing Light
    elif palm_to_tips[0] > 60 and palm_to_tips[4] > 60 and sum(palm_to_tips[1:4]) < 150:  # Rock sign
        return "ice"        # ❄️ Ice Shard
    else:
        return "charging"   # ✨ Charging up

def draw_spell_name(img, spell, x, y):
    spell_names = {
        "fire": "🔥 FIRE BALL",
        "ice": "❄️ ICE SHARD", 
        "lightning": "⚡ LIGHTNING BOLT",
        "healing": "💚 HEALING LIGHT",
        "shadow": "🌑 SHADOW BLAST",
        "charging": "✨ CHARGING...",
    }
    
    spell_colors = {
        "fire": FIRE,
        "ice": ICE,
        "lightning": LIGHTNING, 
        "healing": HEALING,
        "shadow": SHADOW,
        "charging": GOLD,
    }
    
    name = spell_names.get(spell, "UNKNOWN MAGIC")
    color = spell_colors.get(spell, WHITE)
    
    cv2.putText(img, name, (x, y), cv2.FONT_HERSHEY_DUPLEX, 1.2, color, 3)

# Start webcam
cap = cv2.VideoCapture(0)
frame_count = 0

print("🔮 MERYEM EL OSMANI'S MAGIC SPELL SYSTEM ACTIVATED! ✨")
print("Cast spells with these gestures:")
print("✋ Open Hand = ⚡ Lightning Bolt")
print("🤏 Pinch = 🔥 Fire Ball") 
print("✊ Fist = 🌑 Shadow Blast")
print("✌️ Peace = 💚 Healing Light")
print("🤘 Rock = ❄️ Ice Shard")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1)
    frame_count += 1
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    # Update particles
    particles[:] = [p for p in particles if p.update()]
    
    # Draw particles
    for particle in particles:
        if particle.life > 0:
            cv2.circle(frame, (int(particle.x), int(particle.y)), 
                      int(particle.size), particle.color, -1)
    
    current_time = time.time()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            h, w, _ = frame.shape
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw hand skeleton
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            palm = landmarks[9]
            detected_spell = detect_spell(landmarks)
            
            if detected_spell and detected_spell != "charging":
                # Check if new spell or continuing
                if current_spell != detected_spell:
                    spell_start_time = current_time
                    current_spell = detected_spell
                
                spell_duration = current_time - spell_start_time
                
                # Cast spell after holding for 1 second
                if spell_duration > 1.0 and current_time > spell_cooldown:
                    spell_colors_map = {
                        "fire": FIRE, "ice": ICE, "lightning": LIGHTNING,
                        "healing": HEALING, "shadow": SHADOW
                    }
                    
                    spell_color = spell_colors_map.get(detected_spell, WHITE)
                    
                    # Create spell effect
                    create_spell_particles(palm[0], palm[1], detected_spell, spell_color, 25)
                    
                    # Draw intense magic circle
                    draw_magic_circle(frame, palm, 80, spell_color, detected_spell, 1.5)
                    
                    # Add to combo
                    spell_history.append(detected_spell)
                    if len(spell_history) > 5:
                        spell_history.pop(0)
                    
                    spell_cooldown = current_time + 0.5  # Cooldown
                    combo_count += 1
                    
                    print(f"🎯 SPELL CAST: {detected_spell.upper()}! Combo: {combo_count}")
                else:
                    # Charging state
                    intensity = min(spell_duration, 1.0)
                    spell_colors_map = {
                        "fire": FIRE, "ice": ICE, "lightning": LIGHTNING,
                        "healing": HEALING, "shadow": SHADOW
                    }
                    spell_color = spell_colors_map.get(detected_spell, WHITE)
                    draw_magic_circle(frame, palm, int(60 + 20 * intensity), spell_color, detected_spell, intensity)
                    
                    # Charging particles
                    if frame_count % 3 == 0:
                        create_spell_particles(palm[0], palm[1], detected_spell, spell_color, 3)
                
                # Display spell name
                draw_spell_name(frame, detected_spell, palm[0] - 100, palm[1] - 120)
            else:
                current_spell = None
                # Show charging state
                draw_magic_circle(frame, palm, 40, GOLD, "charging", 0.5)
                draw_spell_name(frame, "charging", palm[0] - 80, palm[1] - 100)
    
    # UI Elements
    cv2.putText(frame, 'MERYEM EL OSMANI - MAGIC SYSTEM', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, GOLD, 2)
    cv2.putText(frame, f'Spells Cast: {combo_count}', (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)
    
    # Show recent spells
    if spell_history:
        recent_spells = " -> ".join(spell_history[-3:])
        cv2.putText(frame, f'Combo: {recent_spells}', (10, h-30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, LIGHTNING, 2)
    
    cv2.imshow('MERYEM EL OSMANI - MAGIC SPELL CASTING SYSTEM', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
print(f"🎭 Magic session complete! Total spells cast: {combo_count}")