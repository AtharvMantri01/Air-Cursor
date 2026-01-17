"""
Gesture Recognition Module
Recognizes various hand gestures for computer control
"""

import math
from typing import List, Dict, Optional, Tuple


class GestureRecognizer:
    """Recognizes hand gestures from hand landmarks"""
    
    # MediaPipe hand landmark indices
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_MCP = 5
    INDEX_PIP = 6
    INDEX_DIP = 7
    INDEX_TIP = 8
    MIDDLE_MCP = 9
    MIDDLE_PIP = 10
    MIDDLE_DIP = 11
    MIDDLE_TIP = 12
    RING_MCP = 13
    RING_PIP = 14
    RING_DIP = 15
    RING_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20
    
    def __init__(self):
        """Initialize gesture recognizer"""
        self.gesture_history = []
        self.max_history = 5
    
    def _distance(self, point1: Dict, point2: Dict) -> float:
        """Calculate Euclidean distance between two points"""
        return math.sqrt(
            (point1['x'] - point2['x'])**2 + 
            (point1['y'] - point2['y'])**2 +
            (point1['z'] - point2['z'])**2
        )
    
    def _is_finger_extended(self, landmarks: List[Dict], finger_tip: int, 
                           finger_pip: int, finger_mcp: int) -> bool:
        """
        Check if a finger is extended
        
        Args:
            landmarks: List of landmark dictionaries
            finger_tip: Landmark ID of finger tip
            finger_pip: Landmark ID of finger PIP joint
            finger_mcp: Landmark ID of finger MCP joint
            
        Returns:
            True if finger is extended, False otherwise
        """
        tip = landmarks[finger_tip]
        pip = landmarks[finger_pip]
        mcp = landmarks[finger_mcp]
        
        # For thumb, check horizontal position
        if finger_tip == self.THUMB_TIP:
            return tip['x'] > pip['x'] if landmarks[self.WRIST]['x'] < tip['x'] else tip['x'] < pip['x']
        
        # For other fingers, check vertical position
        return tip['y'] < pip['y']
    
    def recognize_gesture(self, landmarks: List[Dict]) -> str:
        """
        Recognize gesture from hand landmarks
        
        Args:
            landmarks: List of 21 landmark dictionaries
            
        Returns:
            Gesture name as string
        """
        if not landmarks or len(landmarks) < 21:
            return "UNKNOWN"
        
        # Check each finger
        thumb_extended = self._is_finger_extended(
            landmarks, self.THUMB_TIP, self.THUMB_IP, self.THUMB_MCP
        )
        index_extended = self._is_finger_extended(
            landmarks, self.INDEX_TIP, self.INDEX_PIP, self.INDEX_MCP
        )
        middle_extended = self._is_finger_extended(
            landmarks, self.MIDDLE_TIP, self.MIDDLE_PIP, self.MIDDLE_MCP
        )
        ring_extended = self._is_finger_extended(
            landmarks, self.RING_TIP, self.RING_PIP, self.RING_MCP
        )
        pinky_extended = self._is_finger_extended(
            landmarks, self.PINKY_TIP, self.PINKY_PIP, self.PINKY_MCP
        )
        
        fingers_extended = [thumb_extended, index_extended, middle_extended, 
                           ring_extended, pinky_extended]
        extended_count = sum(fingers_extended)
        
        # Gesture recognition logic
        if extended_count == 0:
            return "FIST"
        elif extended_count == 1:
            if index_extended:
                return "POINT"
            elif thumb_extended:
                return "THUMBS_UP"
        elif extended_count == 2:
            if index_extended and middle_extended:
                return "PEACE"
            elif index_extended and thumb_extended:
                return "OK"
        elif extended_count == 3:
            if index_extended and middle_extended and ring_extended:
                return "THREE"
        elif extended_count == 4:
            if not thumb_extended:
                return "FOUR"
        elif extended_count == 5:
            return "OPEN_HAND"
        
        return "UNKNOWN"
    
    def get_index_tip_position(self, landmarks: List[Dict], 
                              frame_width: int, frame_height: int) -> Optional[Tuple[int, int]]:
        """
        Get index finger tip position in pixel coordinates
        
        Args:
            landmarks: List of landmark dictionaries
            frame_width: Width of the frame
            frame_height: Height of the frame
            
        Returns:
            Tuple of (x, y) pixel coordinates, or None if not available
        """
        if not landmarks or len(landmarks) <= self.INDEX_TIP:
            return None
        
        tip = landmarks[self.INDEX_TIP]
        x = int(tip['x'] * frame_width)
        y = int(tip['y'] * frame_height)
        
        return (x, y)
    
    def is_click_gesture(self, landmarks: List[Dict]) -> bool:
        """
        Detect if user is making a clicking gesture (thumb and index finger touching)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            True if click gesture detected
        """
        if not landmarks or len(landmarks) < 21:
            return False
        
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        
        distance = self._distance(thumb_tip, index_tip)
        threshold = 0.03  # Adjust based on testing
        
        return distance < threshold
    
    def get_pinch_strength(self, landmarks: List[Dict]) -> float:
        """
        Get pinch strength between thumb and index finger (0.0 to 1.0)
        
        Args:
            landmarks: List of landmark dictionaries
            
        Returns:
            Pinch strength (0.0 = fully pinched, 1.0 = fully open)
        """
        if not landmarks or len(landmarks) < 21:
            return 1.0
        
        thumb_tip = landmarks[self.THUMB_TIP]
        index_tip = landmarks[self.INDEX_TIP]
        
        distance = self._distance(thumb_tip, index_tip)
        max_distance = 0.15  # Maximum expected distance
        strength = min(distance / max_distance, 1.0)
        
        return strength
