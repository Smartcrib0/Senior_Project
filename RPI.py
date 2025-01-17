import socket
import cv2
import threading
import numpy as np
import sounddevice as sd
import wavio
import threading
import requests
import time

# إعدادات السيرفر
SERVER_URL = "http://<server-ip>:5000/upload_audio"  # استبدل <server-ip> بعنوان السيرفر الخاص بك

# دالة لتسجيل الصوت وإرساله إلى السيرفر
def record_and_send_audio():
    def _record_audio():
        sample_rate = 44100
        duration = 6  # مدة التسجيل بالثواني
        filename = "recorded_audio.wav"

        print("Recording audio...")
        audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=2, dtype='int16')
        sd.wait()  # انتظر حتى انتهاء التسجيل
        wavio.write(filename, audio, sample_rate, sampwidth=2)  # احفظ الملف الصوتي
        
        # إرسال الملف الصوتي إلى السيرفر
        try:
            print("Sending audio to server...")
            with open(filename, 'rb') as f:
                response = requests.post(SERVER_URL, files={'file': f})
                print("Server response:", response.json())
        except Exception as e:
            print("Error sending audio:", e)
    
    threading.Thread(target=_record_audio, daemon=True).start()

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
