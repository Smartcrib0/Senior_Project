import cv2

# Open the camera (0 for the first camera, 1 for the second, etc.)
camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Error: Could not access the camera.")
    exit()

# Loop to capture frames continuously
while True:
    ret, frame = camera.read()  # Capture a frame
    if not ret:
        print("Error: Failed to grab frame.")
        break
    
    # Display the video frame
    cv2.imshow("Camera Feed", frame)
    
    # Exit the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
camera.release()
cv2.destroyAllWindows()
