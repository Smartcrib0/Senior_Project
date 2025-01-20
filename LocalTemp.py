import cv2
import Adafruit_DHT
import sounddevice as sd
import wavio
import os
import threading
from flask import Flask, jsonify, request, Response
import time

# إعدادات المستشعر
SENSOR = Adafruit_DHT.DHT11  # نوع المستشعر
PIN = 4  # رقم الـ GPIO المستخدم

# إعدادات الصوت
AUDIO_FOLDER = "Audio"  # تحديد مسار حفظ الملفات الصوتية
camera = cv2.VideoCapture(0)  # إذا كنت تستخدم كاميرا USB أو CSI

# تطبيق Flask للبث المباشر
app_video = Flask(__name__)

# تطبيق Flask لقراءة بيانات المستشعر
app_sensor = Flask(__name__)

# تطبيق Flask لتسجيل الصوت
app_audio = Flask(__name__)

# متغيرات لتخزين بيانات المستشعر
temperature = None
humidity = None

# دالة لقراءة بيانات المستشعر بشكل دوري
def read_sensor_data_periodically():
    global temperature, humidity
    while True:
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, PIN)
        if humidity is not None and temperature is not None:
            print(f"تم تحديث بيانات المستشعر: درجة الحرارة = {temperature}°C، الرطوبة = {humidity}%")
        else:
            print("فشل في قراءة البيانات من المستشعر")
        time.sleep(10)  # تحديث البيانات كل 10 ثوانٍ

# نقطة النهاية لعرض بيانات المستشعر
@app_sensor.route('/sensor', methods=['GET'])
def get_sensor_data():
    if temperature is not None and humidity is not None:
        return jsonify({
            "temperature": temperature,
            "humidity": humidity
        })
    else:
        return jsonify({"error": "Failed to read from sensor"}), 500

# دالة لتسجيل الصوت
def record_audio(filename, duration=6, samplerate=44100):
    try:
        print(f"بدء تسجيل الصوت لمدة {duration} ثانية...")
        audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=2, dtype='int16')
        sd.wait()  # انتظار انتهاء التسجيل
        wavio.write(filename, audio, samplerate, sampwidth=2)
        print(f"تم حفظ الملف الصوتي: {filename}")
    except Exception as e:
        print(f"حدث خطأ أثناء تسجيل الصوت: {e}")

# نقطة النهاية لتسجيل الصوت
@app_audio.route('/record', methods=['POST'])
def record():
    try:
        # قراءة البيانات من الطلب
        data = request.get_json()
        duration = data.get('duration', 6)  # مدة التسجيل (الافتراضية 6 ثوانٍ)
        filename = data.get('filename', 'detected_audio.wav')  # اسم الملف الصوتي

        # تسجيل الصوت في خيط منفصل لتجنب حظر الخادم
        threading.Thread(target=record_audio, args=(os.path.join(AUDIO_FOLDER, filename), duration), daemon=True).start()

        return jsonify({"status": "success", "message": "Recording started", "filename": filename}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# دالة لتوليد الفيديو
def generate_frames():
    while True:
        # التقاط الإطار من الكاميرا
        success, frame = camera.read()
        if not success:
            break
        else:
            # تحويل الإطار إلى صيغة JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            # إرسال الإطار كـ stream
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# مسار البث المباشر
@app_video.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# تشغيل الخوادم على منافذ مختلفة
def run_video_server():
    app_video.run(host='0.0.0.0', port=5000)  # خادم البث المباشر على المنفذ 5000

def run_sensor_server():
    app_sensor.run(host='0.0.0.0', port=5001)  # خادم المستشعرات على المنفذ 5001

def run_audio_server():
    app_audio.run(host='0.0.0.0', port=5002)  # خادم الصوت على المنفذ 5002

if __name__ == "__main__":
    # تشغيل خيط قراءة بيانات المستشعر بشكل دوري
    threading.Thread(target=read_sensor_data_periodically, daemon=True).start()

    # تشغيل الخوادم في خيوط منفصلة
    threading.Thread(target=run_video_server, daemon=True).start()
    threading.Thread(target=run_sensor_server, daemon=True).start()
    threading.Thread(target=run_audio_server, daemon=True).start()

    # إبقاء البرنامج يعمل
    while True:
        time.sleep(1)
