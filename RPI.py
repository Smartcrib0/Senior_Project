import socket
import cv2
import threading
import numpy as np
import sounddevice as sd
import wavio

# Server configuration
SERVER_IP = "185.37.12.147"
SERVER_PORT = 5000
BUFFER_SIZE = 4096

# Audio recording settings
AUDIO_SAMPLE_RATE = 44100
AUDIO_DURATION = 6
AUDIO_FILENAME = "audio.wav"

# Initialize video capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not access the camera.")
    exit()

# Function to send data to the server
def send_to_server(data, data_type):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((SERVER_IP, SERVER_PORT))
            header = f"{data_type}:{len(data)}".encode('utf-8')
            client_socket.sendall(header + b'\n' + data)
            print(f"Sent {data_type} to server.")
    except Exception as e:
        print(f"Error sending {data_type} to server: {e}")

# Function to record audio
def record_audio():
    print("Recording audio...")
    audio_data = sd.rec(int(AUDIO_DURATION * AUDIO_SAMPLE_RATE), samplerate=AUDIO_SAMPLE_RATE, channels=1, dtype='int16')
    sd.wait()
    wavio.write(AUDIO_FILENAME, audio_data, AUDIO_SAMPLE_RATE, sampwidth=2)
    with open(AUDIO_FILENAME, 'rb') as f:
        audio_bytes = f.read()
    send_to_server(audio_bytes, "audio")

# Function to send video frames
def stream_video():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from camera.")
            break

        _, buffer = cv2.imencode('.jpg', frame)
        send_to_server(buffer.tobytes(), "video")

        # Display the frame locally
        cv2.imshow("Streaming Video", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Function to manage audio recording in intervals
def audio_thread():
    while True:
        record_audio()

# Start the audio recording thread
audio_thread = threading.Thread(target=audio_thread, daemon=True)
audio_thread.start()

try:
    print("Starting video stream...")
    stream_video()
finally:
    cap.release()
    cv2.destroyAllWindows()
