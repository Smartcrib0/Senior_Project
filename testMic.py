from flask import Flask, Response, request, send_file
import cv2
import sounddevice as sd
import numpy as np
import wave
import os
import threading
import time

app = Flask(__name__)

# إعداد مسار الملف المؤقت لتسجيل الصوت
TEMP_AUDIO_FILE = "temp_audio.wav"
VIDEO_PORT = 5000
AUDIO_PORT = 5001

# إعداد الكاميرا
camera = cv2.VideoCapture(0)  # استخدام الكاميرا الافتراضية
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
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# تسجيل الصوت
def record_audio(duration, filename):
    try:
        fs = 22050  # معدل العينة (هرتز)
        print("Recording audio...")
        audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait()  # الانتظار حتى ينتهي التسجيل
        print("Recording finished.")
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(fs)
            wf.writeframes(audio.tobytes())
        return True
    except Exception as e:
        print(f"خطأ أثناء تسجيل الصوت: {e}")
        return False

@app.route('/record', methods=['POST'])
def record():
    try:
        data = request.get_json()
        duration = data.get("duration", 6)  # الافتراضي: 6 ثوانٍ
        if record_audio(duration, TEMP_AUDIO_FILE):
            return send_file(TEMP_AUDIO_FILE, as_attachment=True)
        else:
            return jsonify({"error": "Failed to record audio"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(TEMP_AUDIO_FILE):
            os.remove(TEMP_AUDIO_FILE)

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=AUDIO_PORT, debug=False), daemon=True).start()
    app.run(host='0.0.0.0', port=VIDEO_PORT, debug=False)
