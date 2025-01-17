import cv2
import socket
import threading
import struct
import pickle
from queue import Queue

# Configuration
SERVER_IP = "185.37.12.147"
SERVER_PORT = 9999
QUEUE_SIZE = 10  # Limit the queue size to prevent memory overflow

# Initialize queue for frames
frame_queue = Queue(maxsize=QUEUE_SIZE)

# Function to send frames to the server
def send_frames_to_server():
    try:
        # Create a socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        while True:
            frame = frame_queue.get()  # Get a frame from the queue
            if frame is None:  # Check for termination signal
                print("Terminating frame sender thread.")
                break

            # Serialize the frame
            data = pickle.dumps(frame)
            size = len(data)

            # Send size and frame
            client_socket.sendall(struct.pack(">L", size) + data)

    except Exception as e:
        print(f"Error in sending frames: {e}")
    finally:
        client_socket.close()
        print("Connection to server closed.")

# Start the thread for sending frames
threading.Thread(target=send_frames_to_server, daemon=True).start()

# Open the camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Starting video stream...")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read a frame from the camera.")
            break

        # Resize the frame to reduce data size
        frame = cv2.resize(frame, (640, 480))

        # Add frame to the queue
        if not frame_queue.full():
            frame_queue.put(frame)
        else:
            print("Frame queue is full. Dropping frame.")

        # Show the frame locally
        cv2.imshow("Live Stream", frame)

        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting video stream...")
            break

finally:
    # Cleanup
    cap.release()
    frame_queue.put(None)  # Signal the sending thread to terminate
    cv2.destroyAllWindows()
