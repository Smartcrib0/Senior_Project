from flask import Flask, jsonify, request, Response
import Adafruit_DHT  # مكتبة مستشعر DHT
import sounddevice as sd  # لتسجيل الصوت
import numpy as np
import librosa
import cv2
import threading
import time

# إعدادات المستشعر
SENSOR = Adafruit_DHT.DHT11  # نوع المستشعر (يمكنك استخدام DHT22 أيضًا)
PIN = 4  # رقم الـ GPIO الموصل عليه المستشعر

app = Flask(__name__)

# موجه لاسترجاع بيانات درجة الحرارة والرطوبة
@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    try:
        # قراءة درجة الحرارة والرطوبة من المستشعر
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
        if humidity is not None and temperature is not None:
            return jsonify({"temperature": temperature, "humidity": humidity})
        else:
            return jsonify({"error": "Failed to read from sensor"}), 500
    except Exception as e:
        print(f"خطأ في الحصول على بيانات المستشعر: {e}")
        return jsonify({"error": "Failed to get sensor data"}), 500

# موجه لتسجيل الصوت
@app.route('/record', methods=['POST'])
def record_audio():
    try:
        data = request.get_json()
        duration = data.get('duration', 6)  # مدة التسجيل بالثواني
        sample_rate = 22050  # معدل العينة
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()  # الانتظار حتى ينتهي التسجيل

        # تحويل الصوت إلى numpy array وإرجاعه
        audio_data = recording.flatten().tobytes()
        return audio_data, 200
    except Exception as e:
        print(f"خطأ في تسجيل الصوت: {e}")
        return jsonify({"error": "Failed to record audio"}), 500

# دالة للبث المباشر
def generate_frames():
    # فتح الكاميرا
    cap = cv2.VideoCapture(0)  # استخدم 0 لكاميرا الكمبيوتر
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # تحويل الإطار إلى صيغة JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        # إرسال الإطار كـ stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()

# موجه لبث الفيديو المباشر
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)  # الخادم سيعمل على المنفذ 5001
