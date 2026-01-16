import cv2
import mediapipe as mp
import numpy as np
import math

class GestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def find_hands(self, img, draw=True):
        """Find hands in the image"""
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_drawing.draw_landmarks(
                        img, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                    )
        return img
    
    def find_position(self, img, hand_no=0, draw=True):
        """Find positions of hand landmarks"""
        landmark_list = []
        if self.results.multi_hand_landmarks:
            if hand_no < len(self.results.multi_hand_landmarks):
                my_hand = self.results.multi_hand_landmarks[hand_no]
                for id, lm in enumerate(my_hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([id, cx, cy])
                    
                    if draw and id in [4, 8]:  # Thumb tip and index finger tip
                        cv2.circle(img, (cx, cy), 10, (255, 0, 255), cv2.FILLED)
                        
        return landmark_list
    
    def fingers_up(self, landmark_list):
        """Check which fingers are up"""
        if len(landmark_list) == 0:
            return []
            
        fingers = []
        tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky
        
        # Thumb (different logic because it moves horizontally)
        if landmark_list[tip_ids[0]][1] > landmark_list[tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Other four fingers
        for id in range(1, 5):
            if landmark_list[tip_ids[id]][2] < landmark_list[tip_ids[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
                
        return fingers
    
    def find_distance(self, p1, p2, img, landmark_list, draw=True):
        """Find distance between two landmarks with enhanced visualization"""
        if len(landmark_list) < max(p1, p2) + 1:
            return 0, img, []
            
        x1, y1 = landmark_list[p1][1], landmark_list[p1][2]
        x2, y2 = landmark_list[p2][1], landmark_list[p2][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        if draw:
            # Enhanced connection line with gradient effect
            cv2.line(img, (x1, y1), (x2, y2), (255, 100, 255), 2)
            cv2.circle(img, (x1, y1), 8, (255, 100, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 8, (255, 100, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), 6, (100, 255, 255), cv2.FILLED)
        
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]
    
    def is_pinching(self, landmark_list, threshold=40):
        """Enhanced pinch detection with multiple finger combinations"""
        if len(landmark_list) < 21:
            return False
            
        # Primary: thumb tip (4) and index finger tip (8)
        thumb_tip = landmark_list[4]
        index_tip = landmark_list[8]
        primary_distance = math.hypot(thumb_tip[1] - index_tip[1], thumb_tip[2] - index_tip[2])
        
        # Secondary: thumb tip and middle finger tip (12) for alternative gesture
        middle_tip = landmark_list[12]
        secondary_distance = math.hypot(thumb_tip[1] - middle_tip[1], thumb_tip[2] - middle_tip[2])
        
        # Return true if either primary or secondary pinch is detected
        return primary_distance < threshold or secondary_distance < (threshold + 10)
    
    def get_pinch_strength(self, landmark_list):
        """Get normalized pinch strength (0.0 = open, 1.0 = closed)"""
        if len(landmark_list) < 9:
            return 0.0
            
        thumb_tip = landmark_list[4]
        index_tip = landmark_list[8]
        distance = math.hypot(thumb_tip[1] - index_tip[1], thumb_tip[2] - index_tip[2])
        
        # Normalize to 0-1 range (assuming max comfortable distance is ~100px)
        max_distance = 100
        strength = max(0.0, 1.0 - (distance / max_distance))
        return min(1.0, strength)
    
    def get_hand_center(self, landmark_list):
        """Get the center point of the hand"""
        if len(landmark_list) < 21:
            return None
            
        # Calculate center based on key palm points
        palm_points = [0, 5, 9, 13, 17]  # Wrist and base of each finger
        total_x = sum(landmark_list[i][1] for i in palm_points)
        total_y = sum(landmark_list[i][2] for i in palm_points)
        
        center_x = total_x // len(palm_points)
        center_y = total_y // len(palm_points)
        
        return [center_x, center_y]
