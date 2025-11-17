import cv2
import mediapipe as mp
import numpy as np
import math
import time
import random
from collections import deque

# ================================
# MERYEM EL OSMANI PROJECT
# NEURAL WRITING STUDIO 🧠⚡
# ================================

# Initialize MediaPipe
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, 
                       min_detection_confidence=0.85, min_tracking_confidence=0.85)

# Neural Colors
NEURAL_PINK = (255, 20, 147)
NEURAL_BLUE = (0, 191, 255)
NEURAL_GREEN = (50, 205, 50)
NEURAL_PURPLE = (138, 43, 226)
NEURAL_ORANGE = (255, 140, 0)
NEURAL_CYAN = (0, 255, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class NeuralNode:
    def __init__(self, x, y, char=''):
        self.x = x
        self.y = y
        self.char = char
        self.activation = 0.0
        self.target_activation = 0.0
        self.connections = []
        self.pulse_time = 0
        self.size = 1.0
        self.color = NEURAL_BLUE
        self.created_time = time.time()
        
    def update(self):
        # Smooth activation
        self.activation += (self.target_activation - self.activation) * 0.15
        self.pulse_time += 0.1
        
        # Size pulsing
        pulse = 1 + 0.2 * math.sin(self.pulse_time * 2)
        self.size = 0.8 + self.activation * 1.5 * pulse
        
        # Color based on activation
        if self.activation > 0.7:
            self.color = NEURAL_PINK
        elif self.activation > 0.4:
            self.color = NEURAL_ORANGE
        else:
            self.color = NEURAL_BLUE
    
    def draw(self, img):
        if self.char:
            # Neural glow effect
            glow_radius = int(20 * self.size)
            overlay = img.copy()
            cv2.circle(overlay, (int(self.x), int(self.y)), glow_radius, self.color, -1)
            cv2.addWeighted(img, 0.8, overlay, 0.2 * self.activation, 0, img)
            
            # Character
            font_size = self.size * 1.5
            cv2.putText(img, self.char, (int(self.x - 15), int(self.y + 10)), 
                       cv2.FONT_HERSHEY_SIMPLEX, font_size, WHITE, 
                       max(2, int(3 * self.size)), cv2.LINE_AA)
            
            # Neural ring
            cv2.circle(img, (int(self.x), int(self.y)), int(25 * self.size), 
                      self.color, max(1, int(2 * self.activation)))

class NeuralConnection:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        self.strength = 0.0
        self.pulse_progress = 0.0
        self.active = False
        
    def update(self):
        # Connection strength based on node activation
        self.strength = min(self.node1.activation, self.node2.activation)
        
        if self.strength > 0.3:
            self.active = True
            self.pulse_progress += 0.05
            if self.pulse_progress > 1.0:
                self.pulse_progress = 0.0
        else:
            self.active = False
    
    def draw(self, img):
        if self.active and self.strength > 0.2:
            # Neural pathway
            start = (int(self.node1.x), int(self.node1.y))
            end = (int(self.node2.x), int(self.node2.y))
            
            # Connection line with gradient effect
            thickness = max(1, int(5 * self.strength))
            alpha = self.strength * 0.8
            
            color = tuple(int(c * alpha) for c in NEURAL_CYAN)
            cv2.line(img, start, end, color, thickness)
            
            # Pulse along connection
            if self.pulse_progress < 1.0:
                pulse_x = int(start[0] + (end[0] - start[0]) * self.pulse_progress)
                pulse_y = int(start[1] + (end[1] - start[1]) * self.pulse_progress)
                cv2.circle(img, (pulse_x, pulse_y), 8, NEURAL_PINK, -1)
                cv2.circle(img, (pulse_x, pulse_y), 12, NEURAL_PINK, 2)

class BrainWave:
    def __init__(self, start_x, start_y, direction):
        self.x = start_x
        self.y = start_y
        self.direction = direction  # angle in radians
        self.speed = 3
        self.amplitude = 20
        self.frequency = 0.1
        self.life = 100
        self.age = 0
        
    def update(self):
        # Wave movement
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        
        # Add wave motion
        wave_offset = self.amplitude * math.sin(self.age * self.frequency)
        self.x += wave_offset * math.sin(self.direction + math.pi/2)
        self.y += wave_offset * math.cos(self.direction + math.pi/2)
        
        self.age += 1
        self.life -= 1
        return self.life > 0
    
    def draw(self, img):
        alpha = self.life / 100.0
        color = tuple(int(c * alpha) for c in NEURAL_GREEN)
        cv2.circle(img, (int(self.x), int(self.y)), 6, color, -1)
        cv2.circle(img, (int(self.x), int(self.y)), 12, color, 2)

class NeuralNetwork:
    def __init__(self):
        self.nodes = []
        self.connections = []
        self.brain_waves = []
        self.current_word = ""
        self.word_position = [100, 300]
        
    def add_character(self, char, x, y):
        node = NeuralNode(x, y, char)
        self.nodes.append(node)
        
        # Connect to nearby nodes
        for other_node in self.nodes[-5:]:  # Connect to last 5 nodes
            if other_node != node:
                connection = NeuralConnection(other_node, node)
                self.connections.append(connection)
        
        # Activate neural pathway
        self.activate_pathway()
        
        # Add brain wave
        wave_direction = random.uniform(0, 2 * math.pi)
        brain_wave = BrainWave(x, y, wave_direction)
        self.brain_waves.append(brain_wave)
        
        self.current_word += char
        
    def activate_pathway(self):
        """Activate neural pathway through all nodes"""
        for i, node in enumerate(self.nodes):
            delay = i * 0.1  # Sequential activation
            node.target_activation = 1.0
            
        # Create cascading effect
        if len(self.nodes) > 1:
            for connection in self.connections[-3:]:  # Activate recent connections
                connection.active = True
    
    def update(self):
        # Update nodes
        for node in self.nodes:
            node.update()
            # Gradual decay
            node.target_activation *= 0.995
        
        # Update connections
        for connection in self.connections:
            connection.update()
        
        # Update brain waves
        self.brain_waves = [wave for wave in self.brain_waves if wave.update()]
        
        # Add random brain activity
        if random.random() < 0.1:
            if self.nodes:
                source_node = random.choice(self.nodes)
                direction = random.uniform(0, 2 * math.pi)
                wave = BrainWave(source_node.x, source_node.y, direction)
                self.brain_waves.append(wave)
    
    def draw(self, img):
        # Draw connections first
        for connection in self.connections:
            connection.draw(img)
        
        # Draw nodes
        for node in self.nodes:
            node.draw(img)
        
        # Draw brain waves
        for wave in self.brain_waves:
            wave.draw(img)
        
        # Draw current word
        if self.current_word:
            cv2.putText(img, f"NEURAL WORD: {self.current_word}", 
                       tuple(self.word_position), cv2.FONT_HERSHEY_COMPLEX, 
                       1.2, NEURAL_PINK, 3, cv2.LINE_AA)
    
    def clear(self):
        self.nodes = []
        self.connections = []
        self.brain_waves = []
        self.current_word = ""

def detect_neural_gestures(landmarks):
    """Detect gestures for neural interface"""
    if not landmarks:
        return "idle", 0.0
    
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
    
    # Calculate neural energy
    hand_center = np.mean(landmarks, axis=0)
    hand_spread = np.std([np.linalg.norm(np.array(p) - hand_center) for p in landmarks])
    neural_energy = min(1.0, hand_spread / 30)
    
    # Pinch for writing
    pinch_dist = np.linalg.norm(np.array(thumb_tip) - np.array(index_tip))
    
    if pinch_dist < 35:
        return "neural_write", neural_energy
    elif finger_count == 5 and neural_energy > 0.6:
        return "brain_boost", neural_energy
    elif finger_count == 1 and fingers[1]:  # Index
        return "synaptic_point", neural_energy
    elif finger_count == 0:  # Fist
        return "neural_reset", neural_energy
    elif finger_count == 2 and fingers[1] and fingers[4]:  # Thumb + Index
        return "dendrite_mode", neural_energy
    else:
        return "thinking", neural_energy

def draw_neural_interface(img, mode, neural_activity, network_size):
    """Draw neural-themed interface"""
    h, w = img.shape[:2]
    
    # Neural background pattern
    for i in range(0, w, 50):
        for j in range(0, h, 50):
            if random.random() < 0.1:
                pulse = 0.3 + 0.2 * math.sin(time.time() * 2 + i * 0.01 + j * 0.01)
                color = tuple(int(c * pulse) for c in NEURAL_BLUE)
                cv2.circle(img, (i, j), 2, color, -1)
    
    # Title with neural glow
    title = "MERYEM EL OSMANI - NEURAL WRITING STUDIO"
    cv2.putText(img, title, (20, 40), cv2.FONT_HERSHEY_COMPLEX, 
                1.0, NEURAL_CYAN, 3, cv2.LINE_AA)
    cv2.putText(img, title, (20, 40), cv2.FONT_HERSHEY_COMPLEX, 
                1.0, WHITE, 1, cv2.LINE_AA)
    
    # Neural activity meter
    activity_bar_width = int(200 * neural_activity)
    cv2.rectangle(img, (20, 60), (220, 80), NEURAL_BLUE, 2)
    if activity_bar_width > 0:
        cv2.rectangle(img, (20, 60), (20 + activity_bar_width, 80), NEURAL_PINK, -1)
    
    cv2.putText(img, f"NEURAL ACTIVITY: {int(neural_activity * 100)}%", 
                (230, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEURAL_CYAN, 2)
    
    # Mode display
    mode_color = NEURAL_GREEN if mode != "idle" else NEURAL_BLUE
    cv2.putText(img, f"MODE: {mode.upper()}", (20, 110), 
                cv2.FONT_HERSHEY_COMPLEX, 0.8, mode_color, 2)
    
    # Network statistics
    cv2.putText(img, f"NEURAL NODES: {network_size}", (20, 140), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, NEURAL_PURPLE, 2)
    
    # Alphabet neural map
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    neural_map_y = h - 120
    
    cv2.putText(img, "NEURAL ALPHABET MAP", (20, neural_map_y - 20), 
                cv2.FONT_HERSHEY_COMPLEX, 0.6, NEURAL_ORANGE, 2)
    
    for i, char in enumerate(alphabet):
        x = 20 + (i % 13) * 40
        y = neural_map_y + (i // 13) * 40
        
        # Neural node for each letter
        activation = 0.3 + 0.3 * math.sin(time.time() * 1.5 + i * 0.2)
        node_color = tuple(int(c * activation) for c in NEURAL_GREEN)
        
        cv2.circle(img, (x + 15, y - 15), 15, node_color, 2)
        cv2.putText(img, char, (x + 8, y - 8), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.7, WHITE, 2)
    
    # Instructions
    instructions = [
        "🧠 NEURAL WRITE - Pinch to create synaptic connections",
        "⚡ BRAIN BOOST - Open hand to amplify neural signals",
        "🔗 SYNAPTIC POINT - Point to target neural pathways",
        "🔄 NEURAL RESET - Fist to reset neural network",
        "🌿 DENDRITE MODE - Thumb+Index for branch connections"
    ]
    
    for i, instruction in enumerate(instructions):
        cv2.putText(img, instruction, (w - 480, 80 + i * 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, NEURAL_CYAN, 1)

# Initialize neural system
cap = cv2.VideoCapture(0)
neural_net = NeuralNetwork()
current_char_index = 0
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
last_gesture_time = 0
neural_activity = 0.0
writing_position = [300, 300]

print("🧠 MERYEM EL OSMANI'S NEURAL WRITING STUDIO ACTIVATED! ⚡")
print("=== NEURAL INTERFACE COMMANDS ===")
print("🧠 Neural Write: Pinch fingers to create synaptic text connections")
print("⚡ Brain Boost: Open hand wide to amplify neural signals")
print("🔗 Synaptic Point: Point to navigate neural pathways")
print("🔄 Neural Reset: Fist to reset the entire neural network")
print("🌿 Dendrite Mode: Special branching connections")
print("Connect your thoughts directly to the digital realm! 🌟")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Neural background
    frame = cv2.addWeighted(frame, 0.6, np.zeros_like(frame), 0.4, 0)
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)
    
    current_time = time.time()
    
    # Update neural network
    neural_net.update()
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            landmarks = [(int(l.x * w), int(l.y * h)) for l in hand_landmarks.landmark]
            
            # Draw neural hand visualization
            for i, point in enumerate(landmarks):
                node_size = 4 + int(3 * neural_activity)
                cv2.circle(frame, point, node_size, NEURAL_PINK, -1)
                cv2.circle(frame, point, node_size + 3, NEURAL_CYAN, 1)
            
            # Neural connections between hand landmarks
            connections = [(0,1), (1,2), (2,3), (3,4),  # Thumb
                          (0,5), (5,6), (6,7), (7,8),   # Index
                          (9,10), (10,11), (11,12),     # Middle
                          (13,14), (14,15), (15,16),    # Ring
                          (17,18), (18,19), (19,20)]    # Pinky
            
            for start_idx, end_idx in connections:
                start = landmarks[start_idx]
                end = landmarks[end_idx]
                cv2.line(frame, start, end, NEURAL_BLUE, 2)
            
            gesture, energy = detect_neural_gestures(landmarks)
            neural_activity = energy
            hand_center = landmarks[8]  # Index tip
            
            if gesture == "neural_write":
                if current_time - last_gesture_time > 0.6:
                    char = alphabet[current_char_index]
                    neural_net.add_character(char, hand_center[0], hand_center[1])
                    current_char_index = (current_char_index + 1) % len(alphabet)
                    last_gesture_time = current_time
                    print(f"🧠 Neural character: '{char}' - Network: {len(neural_net.nodes)} nodes")
                
                # Writing effect
                cv2.circle(frame, hand_center, int(20 * (1 + energy)), NEURAL_PINK, 3)
                cv2.putText(frame, "NEURAL WRITING", (hand_center[0] - 80, hand_center[1] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEURAL_PINK, 2)
            
            elif gesture == "brain_boost":
                # Boost all neural activity
                for node in neural_net.nodes:
                    node.target_activation = min(1.0, node.target_activation + 0.1)
                
                # Boost visualization
                for i in range(int(energy * 15)):
                    angle = random.uniform(0, 2 * math.pi)
                    radius = 50 + i * 5
                    fx = hand_center[0] + int(radius * math.cos(angle))
                    fy = hand_center[1] + int(radius * math.sin(angle))
                    cv2.circle(frame, (fx, fy), 4, NEURAL_ORANGE, -1)
                
                cv2.putText(frame, "BRAIN BOOST", (hand_center[0] - 60, hand_center[1] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEURAL_ORANGE, 2)
            
            elif gesture == "synaptic_point":
                if current_time - last_gesture_time > 0.5:
                    current_char_index = (current_char_index + 1) % len(alphabet)
                    last_gesture_time = current_time
                
                # Synaptic beam
                cv2.line(frame, hand_center, (hand_center[0], 50), NEURAL_GREEN, 4)
                cv2.circle(frame, (hand_center[0], 50), 15, NEURAL_GREEN, 3)
                
                # Show current character
                current_char = alphabet[current_char_index]
                cv2.putText(frame, f"TARGET: {current_char}", (hand_center[0] - 50, hand_center[1] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEURAL_GREEN, 2)
            
            elif gesture == "neural_reset":
                if current_time - last_gesture_time > 1.0:
                    neural_net.clear()
                    last_gesture_time = current_time
                    print("🔄 Neural network reset - All synapses cleared")
                
                # Reset visualization
                reset_radius = int(80 * (1 + math.sin(time.time() * 10)))
                cv2.circle(frame, hand_center, reset_radius, NEURAL_PURPLE, 3)
                cv2.putText(frame, "NEURAL RESET", (hand_center[0] - 70, hand_center[1] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEURAL_PURPLE, 2)
            
            elif gesture == "dendrite_mode":
                # Special branching effect
                for angle in [0, 60, 120, 180, 240, 300]:
                    rad = math.radians(angle + time.time() * 50)
                    end_x = hand_center[0] + int(40 * math.cos(rad))
                    end_y = hand_center[1] + int(40 * math.sin(rad))
                    cv2.line(frame, hand_center, (end_x, end_y), NEURAL_CYAN, 2)
                    cv2.circle(frame, (end_x, end_y), 6, NEURAL_CYAN, -1)
                
                cv2.putText(frame, "DENDRITE MODE", (hand_center[0] - 80, hand_center[1] - 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, NEURAL_CYAN, 2)
    
    # Draw neural network
    neural_net.draw(frame)
    
    # Draw interface
    draw_neural_interface(frame, "neural_write" if results.multi_hand_landmarks else "idle", 
                         neural_activity, len(neural_net.nodes))
    
    cv2.imshow('MERYEM EL OSMANI - NEURAL WRITING STUDIO 🧠', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()
print("🧠 Neural session terminated. Synaptic connections saved! ⚡✨")