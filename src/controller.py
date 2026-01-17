"""
System Control Module
Controls mouse and keyboard based on hand gestures
"""

import pyautogui
import time
from typing import Optional, Tuple


class SystemController:
    """Controls system mouse and keyboard based on gestures"""
    
    def __init__(self, 
                 screen_width: int = None,
                 screen_height: int = None,
                 smoothing: float = 0.5,
                 click_threshold: float = 0.03):
        """
        Initialize system controller
        
        Args:
            screen_width: Screen width (auto-detected if None)
            screen_height: Screen height (auto-detected if None)
            smoothing: Mouse movement smoothing factor (0.0-1.0)
            click_threshold: Distance threshold for click detection
        """
        self.screen_width = screen_width or pyautogui.size().width
        self.screen_height = screen_height or pyautogui.size().height
        
        self.smoothing = smoothing
        self.click_threshold = click_threshold
        
        self.last_mouse_pos = None
        self.is_dragging = False
        self.last_click_time = 0
        self.click_cooldown = 0.3  # Minimum time between clicks (seconds)
        
        # Disable pyautogui failsafe for smoother operation
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.01  # Small pause between actions
    
    def map_to_screen(self, x: float, y: float, 
                     frame_width: int, frame_height: int,
                     flip_x: bool = False) -> Tuple[int, int]:
        """
        Map camera coordinates to screen coordinates
        
        Args:
            x: X coordinate in frame (0.0-1.0)
            y: Y coordinate in frame (0.0-1.0)
            frame_width: Width of camera frame
            frame_height: Height of camera frame
            flip_x: Whether to flip X axis (for mirror mode)
            
        Returns:
            Tuple of (screen_x, screen_y) in pixels
        """
        # Normalize to 0-1 range
        norm_x = x / frame_width if x > 1.0 else x
        norm_y = y / frame_height if y > 1.0 else y
        
        # Flip X if needed (mirror mode)
        if flip_x:
            norm_x = 1.0 - norm_x
        
        # Map to screen coordinates
        screen_x = int(norm_x * self.screen_width)
        screen_y = int(norm_y * self.screen_height)
        
        # Apply smoothing
        if self.last_mouse_pos:
            screen_x = int(self.smoothing * screen_x + (1 - self.smoothing) * self.last_mouse_pos[0])
            screen_y = int(self.smoothing * screen_y + (1 - self.smoothing) * self.last_mouse_pos[1])
        
        # Clamp to screen bounds
        screen_x = max(0, min(screen_x, self.screen_width - 1))
        screen_y = max(0, min(screen_y, self.screen_height - 1))
        
        self.last_mouse_pos = (screen_x, screen_y)
        return (screen_x, screen_y)
    
    def move_mouse(self, x: int, y: int):
        """
        Move mouse to specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
        """
        try:
            pyautogui.moveTo(x, y, duration=0.05)
        except Exception as e:
            print(f"Error moving mouse: {e}")
    
    def click(self, button: str = 'left', double: bool = False):
        """
        Perform mouse click
        
        Args:
            button: 'left', 'right', or 'middle'
            double: Whether to perform double click
        """
        current_time = time.time()
        if current_time - self.last_click_time < self.click_cooldown:
            return
        
        try:
            if double:
                pyautogui.doubleClick(button=button)
            else:
                pyautogui.click(button=button)
            self.last_click_time = current_time
        except Exception as e:
            print(f"Error clicking: {e}")
    
    def scroll(self, direction: str = 'up', amount: int = 3):
        """
        Scroll mouse wheel
        
        Args:
            direction: 'up' or 'down'
            amount: Number of scroll units
        """
        try:
            scroll_amount = amount if direction == 'up' else -amount
            pyautogui.scroll(scroll_amount)
        except Exception as e:
            print(f"Error scrolling: {e}")
    
    def drag(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int]):
        """
        Perform mouse drag operation
        
        Args:
            start_pos: Starting position (x, y)
            end_pos: Ending position (x, y)
        """
        try:
            pyautogui.mouseDown(start_pos[0], start_pos[1])
            pyautogui.moveTo(end_pos[0], end_pos[1], duration=0.1)
            pyautogui.mouseUp()
        except Exception as e:
            print(f"Error dragging: {e}")
    
    def press_key(self, key: str):
        """
        Press a keyboard key
        
        Args:
            key: Key name (e.g., 'space', 'enter', 'ctrl', etc.)
        """
        try:
            pyautogui.press(key)
        except Exception as e:
            print(f"Error pressing key: {e}")
    
    def type_text(self, text: str):
        """
        Type text
        
        Args:
            text: Text to type
        """
        try:
            pyautogui.write(text, interval=0.05)
        except Exception as e:
            print(f"Error typing: {e}")
    
    def reset(self):
        """Reset controller state"""
        self.last_mouse_pos = None
        self.is_dragging = False
