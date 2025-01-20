import cv2
from flask import Flask, Response, request, jsonify
import sounddevice as sd
import wavio
import threading
import time
import os

# Initialize Flask app
app = Flask(__name__)

# Open the camera
camera = cv2.VideoCapture(0)  # For USB or CSI camera

# Function to record audio
def record_audio(filename, duration, samplerate=44100):
    try:
        print(f"Starting audio recording for {duration} seconds...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
        sd.wait()  # Wait for recording to finish
        wavio.write(filename, audio, samplerate, sampwidth=2)
        print(f"Audio file saved: {filename}")
    except sd.PortAudioError as e:
        print(f"Audio library error: {e}")
    except Exception as e:
        print(f"An error occurred while recording audio: {e}")

# Endpoint to record audio
@app.route('/record', methods=['POST'])
def record():
    try:
        # Read request data
        data = request.get_json()
        duration = data.get('duration', 6)  # Default recording duration is 6 seconds
        if not isinstance(duration, (int, float)) or duration <= 0:
            return jsonify({"status": "error", "message": "Invalid duration"}), 400

        # Generate a unique filename
        filename = data.get('filename', f'detected_audio_{int(time.time())}.wav')

        # Start audio recording in a separate thread
        threading.Thread(target=record_audio, args=(filename, duration), daemon=True).start()

        return jsonify({"status": "success", "message": "Recording started", "filename": filename}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# Function to generate video frames
def generate_frames():
    while True:
        # Capture frame from the camera
        success, frame = camera.read()
        if not success:
            print("Error capturing frame from the camera. Retrying...")
            continue
        else:
            # Convert the frame to JPEG format
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # Send the frame as a stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Video feed endpoint
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ensure the camera is initialized when the server starts
@app.before_first_request
def initialize_camera():
    global camera
    if not camera.isOpened():
        camera.open(0)

# Release the camera when the server stops
@app.teardown_appcontext
def release_camera(error=None):
    global camera
    if camera.isOpened():
        camera.release()

# Run the Flask server
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
