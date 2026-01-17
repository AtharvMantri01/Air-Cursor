"""
Hand Tracking Module using MediaPipe
Detects and tracks hand landmarks in real-time from camera feed
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Optional, Tuple


class HandTracker:
    """Hand tracking using MediaPipe Hands solution"""
    
    def __init__(self, 
                 static_image_mode: bool = False,
                 max_num_hands: int = 2,
                 min_detection_confidence: float = 0.5,
                 min_tracking_confidence: float = 0.5):
        """
        Initialize hand tracker
        
        Args:
            static_image_mode: If True, detection runs on every frame
            max_num_hands: Maximum number of hands to detect
            min_detection_confidence: Minimum confidence for hand detection
            min_tracking_confidence: Minimum confidence for hand tracking
        """
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        self.hands = self.mp_hands.Hands(
            static_image_mode=static_image_mode,
            max_num_hands=max_num_hands,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
    def process_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, List]:
        """
        Process a single frame and detect hands
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (annotated_frame, landmarks_list)
            landmarks_list contains dicts with 'landmarks' and 'handedness' for each hand
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        
        # Process the frame
        results = self.hands.process(rgb_frame)
        
        # Convert back to BGR for drawing
        rgb_frame.flags.writeable = True
        annotated_frame = cv2.cvtColor(rgb_frame, cv2.COLOR_RGB2BGR)
        
        landmarks_list = []
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(
                results.multi_hand_landmarks, 
                results.multi_hand_world_landmarks
            ):
                # Draw hand landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
                
                # Extract landmarks
                h, w, _ = frame.shape
                landmarks = []
                for landmark in hand_landmarks.landmark:
                    landmarks.append({
                        'x': landmark.x,
                        'y': landmark.y,
                        'z': landmark.z
                    })
                
                # Get handedness (Left/Right)
                hand_label = "Unknown"
                if results.multi_handedness:
                    for hand_info in results.multi_handedness:
                        if hand_info.classification:
                            hand_label = hand_info.classification[0].label
                
                landmarks_list.append({
                    'landmarks': landmarks,
                    'handedness': hand_label,
                    'world_landmarks': handedness
                })
        
        return annotated_frame, landmarks_list
    
    def get_landmark_coords(self, landmarks: List[dict], landmark_id: int) -> Optional[Tuple[float, float]]:
        """
        Get pixel coordinates of a specific landmark
        
        Args:
            landmarks: List of landmark dictionaries
            landmark_id: MediaPipe landmark ID (0-20)
            
        Returns:
            Tuple of (x, y) in pixel coordinates, or None if not found
        """
        if landmark_id < len(landmarks):
            return (landmarks[landmark_id]['x'], landmarks[landmark_id]['y'])
        return None
    
    def release(self):
        """Release resources"""
        self.hands.close()
