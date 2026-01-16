import cv2
import numpy as np
from gesture_detector import GestureDetector
from calculator_gui import CalculatorGUI
import time

class AirCalculator:
    def __init__(self):
        self.detector = GestureDetector()
        self.calculator = CalculatorGUI()
        self.cap = cv2.VideoCapture(0)
        
        # Enhanced camera properties for better quality
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 60)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        # Advanced gesture control variables
        self.last_press_time = 0
        self.press_cooldown = 0.3  # Faster response
        self.pinch_detected = False
        self.current_button = None
        self.gesture_smoothing = []
        self.max_smoothing = 5
        
        # Multi-level pinch detection
        self.pinch_thresholds = {
            'hover': 80,    # Show hover effect
            'press': 45,    # Trigger button press
            'strong': 25    # Strong press for special effects
        }
        
        # Performance tracking
        self.fps_history = []
        self.frame_count = 0
        self.last_fps_time = time.time()
        
    def run(self):
        """Main application loop with full-screen support"""
        print("🚀 Advanced AI Air Gesture Calculator")
        print("📷 Initializing high-resolution camera...")
        print("✨ Loading futuristic effects...")
        print("\n💡 Enhanced Features:")
        print("   • Full-screen adaptive layout")
        print("   • Advanced particle effects & animations")
        print("   • Multi-level pinch detection")
        print("   • Scientific calculator functions")
        print("   • Memory operations & history")
        print("   • Press 'f' for fullscreen, 'q' to quit")
        print("\n🧮 Calculator ready!")
        
        # Initialize window
        cv2.namedWindow("Advanced AI Air Gesture Calculator", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Advanced AI Air Gesture Calculator", 
                             cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
        
        fullscreen = False
        
        while True:
            success, img = self.cap.read()
            if not success:
                print("❌ Camera error - retrying...")
                continue
                
            # Flip for mirror effect
            img = cv2.flip(img, 1)
            h, w, c = img.shape
            
            # Update calculator layout based on current window size
            self.calculator.calculate_layout(w, h)
            
            # Hand detection and tracking
            img = self.detector.find_hands(img, draw=True)
            landmark_list = self.detector.find_position(img, draw=True)
            
            # Draw enhanced calculator interface
            img = self.calculator.draw_buttons(img)
            
            # Process advanced gestures
            if landmark_list:
                self.process_advanced_gestures(img, landmark_list)
            
            # Draw performance info and title
            self.draw_interface_overlay(img)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('f'):
                fullscreen = not fullscreen
                if fullscreen:
                    cv2.setWindowProperty("Advanced AI Air Gesture Calculator", 
                                        cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                else:
                    cv2.setWindowProperty("Advanced AI Air Gesture Calculator", 
                                        cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
            
            # Display the enhanced interface
            cv2.imshow("Advanced AI Air Gesture Calculator", img)
            self.update_fps()
                
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("\n👋 Advanced Calculator closed. Thanks for the futuristic experience!")
    
    def process_advanced_gestures(self, img, landmark_list):
        """Enhanced gesture processing with multi-level detection and smoothing"""
        current_time = time.time()
        
        if len(landmark_list) < 9:
            return
            
        # Calculate pinch distance with smoothing
        thumb_pos = landmark_list[4]
        index_pos = landmark_list[8]
        pinch_distance = self.detector.find_distance(4, 8, img, landmark_list)[0]
        
        # Smooth gesture data
        self.gesture_smoothing.append(pinch_distance)
        if len(self.gesture_smoothing) > self.max_smoothing:
            self.gesture_smoothing.pop(0)
        smooth_distance = sum(self.gesture_smoothing) / len(self.gesture_smoothing)
        
        # Calculate interaction point
        middle_x = (thumb_pos[1] + index_pos[1]) // 2
        middle_y = (thumb_pos[2] + index_pos[2]) // 2
        virtual_finger = [0, middle_x, middle_y]
        
        # Determine hover button
        hover_button = self.calculator.check_button_press(virtual_finger)
        self.calculator.hover_button = hover_button
        
        # Multi-level interaction feedback
        if smooth_distance <= self.pinch_thresholds['hover']:
            # Hover state - show subtle effects
            if hover_button:
                cv2.circle(img, (middle_x, middle_y), 12, (100, 255, 255), 1)
                cv2.putText(img, hover_button, (middle_x - 20, middle_y - 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 255), 1)
        
        if smooth_distance <= self.pinch_thresholds['press']:
            # Press threshold - trigger button
            if hover_button:
                cv2.circle(img, (middle_x, middle_y), 18, (0, 255, 150), 2)
                cv2.putText(img, "PRESS", (middle_x - 25, middle_y - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 150), 2)
                
                if (not self.pinch_detected and 
                    current_time - self.last_press_time > self.press_cooldown):
                    
                    self.calculator.process_button_press(hover_button)
                    self.last_press_time = current_time
                    self.pinch_detected = True
                    
                    # Enhanced visual feedback
                    cv2.putText(img, f"✓ {hover_button}", (10, img.shape[0] - 80), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 150), 2)
                    
                    print(f"🔥 Button: {hover_button} | Expr: '{self.calculator.expression}' | Display: '{self.calculator.current_display}'")
        
        if smooth_distance <= self.pinch_thresholds['strong']:
            # Strong press - extra effects
            if hover_button:
                cv2.circle(img, (middle_x, middle_y), 25, (255, 100, 255), 3)
                # Add extra particle burst for strong press
                if not self.pinch_detected:
                    self.calculator.add_particle(middle_x, middle_y, (255, 150, 255))
                    self.calculator.add_particle(middle_x, middle_y, (255, 150, 255))
        
        # Reset pinch state when distance increases
        if smooth_distance > self.pinch_thresholds['hover']:
            if self.pinch_detected:
                self.calculator.pressed_button = None
                self.pinch_detected = False

    def draw_interface_overlay(self, img):
        """Draw enhanced interface elements"""
        h, w = img.shape[:2]
        
        # Title with glow effect
        title = "Advanced AI Calculator"
        cv2.putText(img, title, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (100, 255, 255), 3)
        cv2.putText(img, title, (15, 35), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        
        # Performance info
        avg_fps = sum(self.fps_history) / len(self.fps_history) if self.fps_history else 0
        perf_text = f"FPS: {avg_fps:.1f} | Resolution: {w}x{h}"
        cv2.putText(img, perf_text, (w - 300, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Controls info
        controls = ["F: Fullscreen", "Q: Quit", f"Memory: {self.calculator.memory:.2f}"]
        for i, control in enumerate(controls):
            cv2.putText(img, control, (w - 200, 50 + i * 20), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # Gesture status with advanced info
        if len(self.gesture_smoothing) > 0:
            smooth_dist = sum(self.gesture_smoothing) / len(self.gesture_smoothing)
            status = f"Gesture: {smooth_dist:.1f}px"
            if smooth_dist <= self.pinch_thresholds['strong']:
                status += " [STRONG]"
            elif smooth_dist <= self.pinch_thresholds['press']:
                status += " [PRESS]"
            elif smooth_dist <= self.pinch_thresholds['hover']:
                status += " [HOVER]"
            
            cv2.putText(img, status, (15, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    def update_fps(self):
        """Update FPS tracking"""
        current_time = time.time()
        self.frame_count += 1
        
        if current_time - self.last_fps_time >= 1.0:  # Update every second
            fps = self.frame_count / (current_time - self.last_fps_time)
            self.fps_history.append(fps)
            if len(self.fps_history) > 10:  # Keep last 10 seconds
                self.fps_history.pop(0)
            
            self.frame_count = 0
            self.last_fps_time = current_time

def main():
    """Main function to start the application"""
    try:
        calculator = AirCalculator()
        calculator.run()
    except KeyboardInterrupt:
        print("\n⚠️  Application interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure your camera is working and dependencies are installed")
    finally:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
