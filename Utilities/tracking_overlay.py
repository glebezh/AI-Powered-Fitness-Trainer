import cv2

def tracking_overlay(frame):
    # Feedback for missing landmarks
    text = "Oops! We couldn't detect all necessary tracking points right now. Please try adjusting your position or ensure your face/body is in view."

    # Get the frame dimensions
    frame_height, frame_width, _ = frame.shape

    # Split the text into multiple lines
    words = text.split(' ')
    lines = []
    current_line = ""

    # Add words to the line until it exceeds the frame width
    for word in words:
        # Predict the width if this word is added
        test_line = f"{current_line} {word}".strip()
        text_width, _ = cv2.getTextSize(test_line, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]

        if text_width < frame_width - 20:  # Leave some margin
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)

    # Calculate the starting y position to center the text vertically
    line_height = cv2.getTextSize("Test", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][1] + 10
    y_position = (frame_height // 2) - (len(lines) * line_height // 2)

    # Draw each line on the frame
    for line in lines:
        text_width, text_height = cv2.getTextSize(line, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        x_position = (frame_width - text_width) // 2
        cv2.putText(frame, line, (x_position, y_position), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 234, 255), 2, cv2.LINE_AA)
        y_position += line_height  # Move to the next line
                      
