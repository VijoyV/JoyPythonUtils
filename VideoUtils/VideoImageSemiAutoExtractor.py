import cv2

# pip install opencv-python

# Path to the video file
video_path = 'C:\\Users\\vijoy\\Downloads\\YouTubeVideos\\Introduction to Generative AI.mp4'
image_base_path = 'C:\\Users\\vijoy\\Downloads\\YouTubeVideos\\images\\'

# Open the video file
cap = cv2.VideoCapture(video_path)

# Check if the video file opened successfully
if not cap.isOpened():
    print("Error opening video file")
    exit()

# Function to handle mouse click events
def on_mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        image_path = image_base_path + f"frame_{frame_number}.jpg"
        cv2.imwrite(image_path, frame)
        print(f"Saved image as {image_path}")

# Create a window and set the mouse callback function
cv2.namedWindow('Video')
cv2.setMouseCallback('Video', on_mouse_click)

# Initialize variables
frame_number = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Display the frame
    cv2.imshow('Video', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_number += 1

# Release the video capture object, close the video file, and destroy the window
cap.release()
cv2.destroyAllWindows()

print(f"Extracted {frame_number} frames with new images from the video")