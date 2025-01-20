import cv2
import sounddevice as sd
import wavio
import os
import threading
from flask import Flask, request, jsonify, Response

# إعداد Flask
app = Flask(__name__)

# إعدادات الصوت
AUDIO_FOLDER = "Audio"  # تحديد مسار حفظ الملفات الصوتية
camera = cv2.VideoCapture(0)  # إذا كنت تستخدم كاميرا USB أو CSI

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
@app.route('/record', methods=['POST'])
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
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# تشغيل الخادم
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # ملاحظة: استخدم منفذ مختلف عن الخادم الآخر
