import cv2
import time
from flask import Flask, Response, jsonify, request, send_file
import threading
import Adafruit_DHT
import pyaudio
import wave
import io
import os

# إعدادات الكاميرا
cap = cv2.VideoCapture(0)  # استخدم كاميرا Raspberry Pi

# إعداد Flask
app = Flask(__name__)

# إعدادات مستشعر الحرارة DHT11
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # يجب التأكد من رقم الدبوس المتصل به المستشعر

# إعدادات المايكروفون لتسجيل الصوت
p = pyaudio.PyAudio()
CHUNK = 1024  # حجم الدفعة
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100  # معدل العينة
RECORD_SECONDS = 6  # مدة التسجيل

# دالة لقراءة مستشعر الحرارة والرطوبة
def get_temperature_humidity():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return {"temperature": temperature, "humidity": humidity}
    else:
        return {"temperature": "N/A", "humidity": "N/A"}

# دالة للبث المباشر من الكاميرا
def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # تقليل حجم الإطار لتسريع البث (اختياري)
        frame = cv2.resize(frame, (640, 480))  # تغيير الحجم إلى 640x480

        # ضغط الإطار باستخدام JPEG
        _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 60])  # 60% جودة لضغط أعلى
        frame = buffer.tobytes()

        # إرسال الإطار كـ stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# دالة لتسجيل الصوت وإعادته كملف مؤقت
def record_audio_to_memory():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")
    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")
    stream.stop_stream()
    stream.close()

    # حفظ الصوت مؤقتًا في الذاكرة
    audio_memory = io.BytesIO()
    wf = wave.open(audio_memory, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    audio_memory.seek(0)

    return audio_memory

# API لبث الفيديو
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# API للحصول على بيانات المستشعر
@app.route('/sensor')
def sensor():
    data = get_temperature_humidity()
    return jsonify(data)

# API لتسجيل الصوت
@app.route('/record', methods=['POST'])
def record():
    audio_memory = record_audio_to_memory()
    return send_file(audio_memory, mimetype="audio/wav", as_attachment=False)

# تشغيل الخادم Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
