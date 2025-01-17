import cv2
import socket
import threading
import struct
import pickle
from queue import Queue
import sounddevice as sd
import numpy as np
import wave

# Configuration
SERVER_IP = "185.37.12.147"
SERVER_PORT = 9999
FRAME_QUEUE_SIZE = 10  # Limit the frame queue size
AUDIO_QUEUE_SIZE = 10  # Limit the audio queue size
AUDIO_SAMPLE_RATE = 44100
AUDIO_DURATION = 6  # Seconds per audio clip
AUDIO_CHANNELS = 1  # Mono audio
AUDIO_FILENAME = "audio_chunk.wav"

# Initialize queues
frame_queue = Queue(maxsize=FRAME_QUEUE_SIZE)
audio_queue = Queue(maxsize=AUDIO_QUEUE_SIZE)

# Function to send frames and audio to the server
def send_to_server():
    try:
        # Create a socket connection
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        while True:
            if not frame_queue.empty():
                frame = frame_queue.get()
                if frame is None:
                    break
                # Serialize the frame
                frame_data = pickle.dumps(("frame", frame))
                frame_size = len(frame_data)
                client_socket.sendall(struct.pack(">L", frame_size) + frame_data)

            if not audio_queue.empty():
                audio_chunk = audio_queue.get()
                if audio_chunk is None:
                    break
                # Serialize the audio
                audio_data = pickle.dumps(("audio", audio_chunk))
                audio_size = len(audio_data)
                client_socket.sendall(struct.pack(">L", audio_size) + audio_data)

    except Exception as e:
        print(f"Error in sending data to server: {e}")
    finally:
        client_socket.close()
        print("Connection to server closed.")

# Function to record audio
def record_audio():
    try:
        while True:
            print("Recording audio...")
            audio = sd.rec(int(AUDIO_SAMPLE_RATE * AUDIO_DURATION), samplerate=AUDIO_SAMPLE_RATE,
                           channels=AUDIO_CHANNELS, dtype="int16")
            sd.wait()
            print("Audio recorded.")

            # Save the audio to a file for debugging (optional)
            with wave.open(AUDIO_FILENAME, "wb") as wf:
                wf.setnchannels(AUDIO_CHANNELS)
                wf.setsampwidth(2)  # 16-bit audio
                wf.setframerate(AUDIO_SAMPLE_RATE)
                wf.writeframes(audio.tobytes())

            # Add audio to the queue
            if not audio_queue.full():
                audio_queue.put(audio)
            else:
                print("Audio queue is full. Dropping audio.")
    except Exception as e:
        print(f"Error in audio recording: {e}")

# Start the server sending thread
threading.Thread(target=send_to_server, daemon=True).start()

# Start the audio recording thread
threading.Thread(target=record_audio, daemon=True).start()

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
    audio_queue.put(None)  # Signal the sending thread to terminate
    cv2.destroyAllWindows()
