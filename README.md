# Gesture Calculator

## Overview
An innovative calculator application that replaces traditional button clicks with hand gestures. Using computer vision, this tool interprets finger movements to input numbers and operations, offering a touch-free mathematical experience perfect for hygienic or accessible computing.

## Features
-   **Touch-Free Input**: Control the entire calculator interface without touching the screen or mouse.
-   **Real-time Tracking**: Accurate hand landmark detection using MediaPipe.
-   **Gesture Mapping**: Specific gestures for digits (0-9) and operators (+, -, *, /).
-   **Visual Feedback**: On-screen overlay showing detected hand structure.
-   **Math Engine**: Robust evaluation of complex arithmetic expressions.

## Technology Stack
-   **Language**: Python.
-   **Vision**: OpenCV, MediaPipe Hands.
-   **GUI**: Tkinter / PyGame for the calculator interface.
-   **Math**: Python standard library.

## Usage Flow
1.  **Start**: Launch the application to activate the webcam.
2.  **Gesture**: Show a specific number of fingers to input digits.
3.  **Operate**: Use specific hand poses (e.g., closed fist, pinch) for operations.
4.  **Calculate**: The system evaluates the expression and displays the result.

## Quick Start
```bash
# Clone the repository
git clone https://github.com/Nytrynox/Gesture-Calculator.git

# Install dependencies
pip install -r requirements.txt

# Run the calculator
python main.py
```

## License
MIT License

## Author
**Karthik Idikuda**
