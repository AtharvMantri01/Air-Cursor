"""
Main Application Entry Point
Hand tracking and computer control system
"""

import cv2
import argparse
from typing import Optional
import numpy as np

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hand_tracker import HandTracker
from gesture_recognizer import GestureRecognizer
from controller import SystemController


class HandControlApp:
    """Main application for hand-controlled computer interaction"""
    
    def __init__(self, 
                 camera_id: int = 0,
                 flip_horizontal: bool = True,
                 show_preview: bool = True,
                 control_mode: str = 'pointer'):
        """
        Initialize the application
        
        Args:
            camera_id: Camera device ID
            flip_horizontal: Whether to flip camera horizontally (mirror mode)
            show_preview: Whether to show camera preview window
            control_mode: Control mode ('pointer', 'gesture', or 'both')
        """
        self.camera_id = camera_id
        self.flip_horizontal = flip_horizontal
        self.show_preview = show_preview
        self.control_mode = control_mode
        
        # Initialize components
        self.hand_tracker = HandTracker(
            max_num_hands=1,  # Focus on one hand for control
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.gesture_recognizer = GestureRecognizer()
        self.controller = SystemController(smoothing=0.7)
        
        self.cap: Optional[cv2.VideoCapture] = None
        self.running = False
        
        # Control state
        self.pointer_active = False
        self.last_gesture = None
        self.gesture_hold_time = 0
    
    def initialize_camera(self) -> bool:
        """Initialize camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera {self.camera_id}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def process_gesture(self, gesture: str, landmarks: list, frame_width: int, frame_height: int):
        """
        Process recognized gesture and perform corresponding action
        
        Args:
            gesture: Recognized gesture name
            landmarks: Hand landmarks
            frame_width: Frame width
            frame_height: Frame height
        """
        import time
        current_time = time.time()
        
        # Pointer mode: Use index finger to control mouse
        if self.control_mode in ['pointer', 'both']:
            index_pos = self.gesture_recognizer.get_index_tip_position(
                landmarks, frame_width, frame_height
            )
            
            if index_pos and gesture == "POINT":
                # Map to screen coordinates
                screen_x, screen_y = self.controller.map_to_screen(
                    index_pos[0], index_pos[1],
                    frame_width, frame_height,
                    flip_x=self.flip_horizontal
                )
                self.controller.move_mouse(screen_x, screen_y)
                self.pointer_active = True
            else:
                self.pointer_active = False
            
            # Click detection (thumb and index pinch)
            if self.gesture_recognizer.is_click_gesture(landmarks):
                if not self.pointer_active:
                    self.controller.click()
                    self.pointer_active = True
        
        # Gesture mode: Use specific gestures for actions
        if self.control_mode in ['gesture', 'both']:
            if gesture != self.last_gesture:
                self.gesture_hold_time = current_time
                self.last_gesture = gesture
            
            hold_duration = current_time - self.gesture_hold_time
            
            # Only trigger actions after holding gesture for a moment
            if hold_duration > 0.5:
                if gesture == "FIST":
                    # Right click
                    if hold_duration > 1.0 and hold_duration < 1.5:
                        self.controller.click(button='right')
                elif gesture == "PEACE":
                    # Double click
                    if hold_duration > 1.0 and hold_duration < 1.5:
                        self.controller.click(double=True)
                elif gesture == "THUMBS_UP":
                    # Scroll up
                    if hold_duration > 0.8:
                        self.controller.scroll(direction='up')
                elif gesture == "OK":
                    # Scroll down
                    if hold_duration > 0.8:
                        self.controller.scroll(direction='down')
                elif gesture == "OPEN_HAND":
                    # Reset/stop
                    self.controller.reset()
    
    def draw_ui(self, frame: np.ndarray, gesture: str, landmarks: list):
        """
        Draw UI overlay on frame
        
        Args:
            frame: Frame to draw on
            gesture: Current gesture
            landmarks: Hand landmarks
        """
        h, w = frame.shape[:2]
        
        # Draw gesture label
        cv2.putText(frame, f"Gesture: {gesture}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Draw control mode
        cv2.putText(frame, f"Mode: {self.control_mode.upper()}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Draw pointer status
        if self.pointer_active:
            cv2.putText(frame, "POINTER ACTIVE", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        
        # Draw instructions
        instructions = [
            "Controls:",
            "POINT - Move mouse",
            "PINCH - Click",
            "FIST - Right click",
            "PEACE - Double click",
            "THUMBS UP - Scroll up",
            "OK - Scroll down",
            "Press 'q' to quit"
        ]
        
        y_offset = h - 200
        for i, instruction in enumerate(instructions):
            cv2.putText(frame, instruction, (10, y_offset + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
    
    def run(self):
        """Run the main application loop"""
        if not self.initialize_camera():
            return
        
        print("Hand Control System Started")
        print("Press 'q' to quit")
        print("Controls:")
        print("  - Point with index finger to move mouse")
        print("  - Pinch thumb and index to click")
        print("  - Use gestures for other actions")
        
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to read frame")
                break
            
            # Flip frame horizontally if needed (mirror mode)
            if self.flip_horizontal:
                frame = cv2.flip(frame, 1)
            
            # Process frame for hand tracking
            annotated_frame, hands_data = self.hand_tracker.process_frame(frame)
            
            # Process each detected hand
            if hands_data:
                for hand_data in hands_data:
                    landmarks = hand_data['landmarks']
                    handedness = hand_data['handedness']
                    
                    # Recognize gesture
                    gesture = self.gesture_recognizer.recognize_gesture(landmarks)
                    
                    # Process gesture for control
                    h, w = frame.shape[:2]
                    self.process_gesture(gesture, landmarks, w, h)
                    
                    # Draw UI
                    self.draw_ui(annotated_frame, gesture, landmarks)
                    
                    # Draw handedness
                    cv2.putText(annotated_frame, f"Hand: {handedness}", (10, 150),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 255), 2)
            else:
                # No hand detected
                self.pointer_active = False
                self.draw_ui(annotated_frame, "NO HAND", [])
            
            # Show preview
            if self.show_preview:
                cv2.imshow('Hand Control System', annotated_frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.running = False
            elif key == ord('r'):
                # Reset controller
                self.controller.reset()
                print("Controller reset")
        
        self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        print("Shutting down...")
        if self.cap:
            self.cap.release()
        self.hand_tracker.release()
        cv2.destroyAllWindows()
        print("Shutdown complete")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Hand-controlled computer system')
    parser.add_argument('--camera', type=int, default=0,
                       help='Camera device ID (default: 0)')
    parser.add_argument('--no-flip', action='store_true',
                       help='Disable horizontal flip (mirror mode)')
    parser.add_argument('--no-preview', action='store_true',
                       help='Hide camera preview window')
    parser.add_argument('--mode', type=str, default='both',
                       choices=['pointer', 'gesture', 'both'],
                       help='Control mode (default: both)')
    
    args = parser.parse_args()
    
    app = HandControlApp(
        camera_id=args.camera,
        flip_horizontal=not args.no_flip,
        show_preview=not args.no_preview,
        control_mode=args.mode
    )
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        app.cleanup()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        app.cleanup()
        sys.exit(1)


if __name__ == "__main__":
    main()
