from flask import Flask, Response, request, send_file,jsonify
import cv2
import sounddevice as sd
import numpy as np
import wave
import os
import threading
import requests
import wavio

app = Flask(__name__)

# إعداد المسارات والمنافذ
TEMP_AUDIO_FILE = "temp_audio.wav"
VIDEO_PORT = 5000
AUDIO_PORT = 5001

# إعداد الكاميرا
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    raise RuntimeError("Error: Could not open the camera.")

# بث الفيديو
def generate_video_stream():
    while True:
        success, frame = camera.read()
        if not success:
            break
        _, buffer = cv2.imencode('.jpg', frame)
        frame_data = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')

@app.route('/video_feed', methods=['GET'])
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

# تسجيل الصوت
def record_audio(duration, filename):
    try:
        fs = 22050
        print("Recording audio...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()
        print("Recording finished.")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio.tobytes())
        return True
    except Exception as e:
        print(f"Error recording audio: {e}")
        return False

@app.route('/record', methods=['POST'])
def record():
    try:
        data = request.get_json()
        duration = data.get("duration", 6)
        if record_audio(duration, TEMP_AUDIO_FILE):
            return send_file(TEMP_AUDIO_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Failed to record audio"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)

# تسجيل الصوت وإرساله
def record_audio_and_send(duration=6, filename="detected_audio.wav", laptop_ip="192.168.1.100", laptop_port=5000):
    sample_rate = 44100
    channels = 2

    try:
        print("Recording audio...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()
        wavio.write(filename, audio, sample_rate, sampwidth=2)
        print(f"Audio recorded and saved to {filename}")

        with open(filename, 'rb') as f:
            response = requests.post(f'http://{laptop_ip}:{laptop_port}/upload', files={'file': f})
        
        if response.status_code == 200:
            print("File sent successfully to the laptop")
        else:
            print(f"Failed to send file: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error recording or sending audio: {e}")

# بدء تشغيل الخوادم
if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=AUDIO_PORT, debug=False), daemon=True).start()
    app.run(host='0.0.0.0', port=VIDEO_PORT, debug=False)
    
import sounddevice as sd
import wavio
import requests

def record_audio_and_send(duration=6, filename="detected_audio.wav", laptop_ip="192.168.173.191", laptop_port=5000):
    """Function to record audio and send it to a laptop."""
    sample_rate = 44100
    channels = 2

    try:
        print("بدء تسجيل الصوت...")
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()  # انتظار انتهاء التسجيل
        wavio.write(filename, audio, sample_rate, sampwidth=2)
        print(f"تم تسجيل الصوت بنجاح وحفظه في {filename}")

        # إرسال الملف إلى اللابتوب
        with open(filename, 'rb') as f:
            response = requests.post(f'http://{laptop_ip}:{laptop_port}/upload', files={'file': f})
        
        if response.status_code == 200:
            print("تم إرسال الملف بنجاح إلى اللابتوب")
        else:
            print(f"فشل في إرسال الملف: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"خطأ أثناء تسجيل الصوت أو الإرسال: {e}")

# استدعاء الوظيفة مع عنوان IP والبوابة الخاصة باللابتوب
record_audio_and_send(laptop_ip="192.168.173.191", laptop_port=5000)