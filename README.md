# HANDS Project - Hand-Controlled Computer System

A real-time hand and finger tracking system that allows you to control your computer using hand gestures and finger movements. The system uses your webcam to track hand movements and translates them into mouse and keyboard actions.

## Features

- **Real-time Hand Tracking**: Uses MediaPipe for robust hand detection and tracking
- **Gesture Recognition**: Recognizes multiple hand gestures (point, click, scroll, etc.)
- **Mouse Control**: Control mouse cursor with your index finger
- **Click Detection**: Pinch thumb and index finger to click
- **Gesture-Based Actions**: Use specific gestures for different actions
- **Smooth Movement**: Configurable smoothing for natural mouse movement
- **Mirror Mode**: Optional horizontal flip for intuitive control

## Requirements

- Python 3.8 or higher
- Webcam/Camera
- macOS, Windows, or Linux

## Installation

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the application with default settings:
```bash
python run.py
```

Or directly:
```bash
python src/main.py
```

### Command Line Options

```bash
python run.py [OPTIONS]
```

Or:
```bash
python src/main.py [OPTIONS]

Options:
  --camera ID          Camera device ID (default: 0)
  --no-flip            Disable horizontal flip (mirror mode)
  --no-preview         Hide camera preview window
  --mode MODE          Control mode: 'pointer', 'gesture', or 'both' (default: both)
```

### Examples

```bash
# Use a different camera
python src/main.py --camera 1

# Disable mirror mode
python src/main.py --no-flip

# Gesture-only mode (no pointer control)
python src/main.py --mode gesture

# Pointer-only mode
python src/main.py --mode pointer
```

## Controls

### Pointer Mode
- **Point with index finger**: Move mouse cursor
- **Pinch thumb and index finger**: Left click
- **Hold pinch**: Continuous clicking

### Gesture Mode
- **FIST**: Right click (hold for 1 second)
- **PEACE (two fingers)**: Double click (hold for 1 second)
- **THUMBS UP**: Scroll up
- **OK (thumb + index circle)**: Scroll down
- **OPEN HAND**: Reset/stop actions

### Combined Mode (Default)
Both pointer and gesture controls are active simultaneously.

## Project Structure

```
HANDS Project/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── hand_tracker.py       # MediaPipe hand tracking
│   ├── gesture_recognizer.py # Gesture recognition logic
│   ├── controller.py         # System control (mouse/keyboard)
│   └── main.py              # Main application entry point
├── config/
│   └── config.yaml          # Configuration file
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore              # Git ignore rules
```

## How It Works

1. **Hand Tracking**: The system continuously captures frames from your webcam and uses MediaPipe to detect and track hand landmarks (21 points per hand).

2. **Gesture Recognition**: The gesture recognizer analyzes the hand landmarks to identify specific gestures based on finger positions and extensions.

3. **System Control**: Based on the detected gestures and finger positions, the controller translates them into mouse movements, clicks, scrolls, and keyboard actions using PyAutoGUI.

4. **Smoothing**: Mouse movements are smoothed to provide natural cursor control without jitter.

## Configuration

You can modify `config/config.yaml` to adjust:
- Camera settings
- Hand tracking sensitivity
- Control behavior
- Gesture mappings
- Display options

## Troubleshooting

### Camera not detected
- Check that your camera is connected and not being used by another application
- Try different camera IDs: `--camera 1`, `--camera 2`, etc.

### Poor tracking accuracy
- Ensure good lighting conditions
- Keep your hand clearly visible in the frame
- Adjust `min_detection_confidence` and `min_tracking_confidence` in the config

### Mouse movement too jittery
- Increase the `smoothing` value in the config (closer to 1.0)
- Ensure stable camera position

### Mouse movement too slow
- Decrease the `smoothing` value in the config (closer to 0.0)
- Check camera frame rate

## Safety

- The system includes PyAutoGUI's failsafe feature - move your mouse to the top-left corner to trigger an emergency stop
- Be careful when using this system as it can control your computer automatically
- Test in a safe environment first

## Future Enhancements

Potential improvements:
- Multi-hand support
- Custom gesture training
- Keyboard shortcuts via gestures
- Window management gestures
- Voice commands integration
- Calibration system

## License

This project is open source and available for personal and educational use.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Acknowledgments

- MediaPipe by Google for hand tracking technology
- OpenCV for computer vision capabilities
- PyAutoGUI for system automation
