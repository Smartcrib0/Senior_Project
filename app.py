import cv2
import time
from flask import Flask, Response, jsonify
import threading
import requests
import Adafruit_DHT
import pyaudio
import wave
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

# مسار حفظ الملفات الصوتية
AUDIO_PATH = "Audio"
if not os.path.exists(AUDIO_PATH):
    os.makedirs(AUDIO_PATH)

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

# دالة لتسجيل الصوت من المايكروفون
def record_audio():
    # إعدادات تسجيل الصوت
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

    # حفظ الصوت في ملف WAV
    audio_file = f"{AUDIO_PATH}audio_{int(time.time())}.wav"
    wf = wave.open(audio_file, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return audio_file

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
    # تشغيل التسجيل الصوتي في خيط منفصل
    threading.Thread(target=record_audio).start()
    return jsonify({"message": "Audio recording started"})

# تشغيل الخادم Flask
if __name__ == '__main__':
    # تشغيل Flask مع تحسين الأداء
    app.run(host='0.0.0.0', port=5000, threaded=True)  # تفعيل خاصية threaded لتحسين الأداء
