import cv2
from flask import Flask, Response
from ultralytics import YOLO
import pyaudio
import wave
import threading

# إعداد Flask
app = Flask(__name__)

# تحميل نموذج YOLOv8
model = YOLO("yolov8n.pt")  # استخدم النموذج الذي قمت بتنزيله (yolov8n أو غيره)

# إعدادات تسجيل الصوت
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 6
OUTPUT_FILENAME = "output.wav"

# فتح الكاميرا
camera = cv2.VideoCapture(0)

# قفل التحكم في التسجيل
recording_lock = threading.Lock()

def record_audio():
    """تسجيل الصوت لمدة محددة"""
    with recording_lock:
        audio = pyaudio.PyAudio()
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("Recording audio...")
        frames = []

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("Audio recording finished.")

        stream.stop_stream()
        stream.close()
        audio.terminate()

        # حفظ ملف الصوت
        wf = wave.open(OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

def generate_frames():
    """توليد الإطارات ومعالجتها باستخدام YOLO"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # تطبيق YOLO على الإطار
            results = model.predict(frame, conf=0.5, verbose=False)  # تنفيذ التوقع
            annotated_frame = results[0].plot()  # الحصول على الإطار مع الرسوم التوضيحية

            # التحقق إذا تم اكتشاف شخص
            for result in results[0].boxes.data:
                cls = int(result[5])  # صنف الكائن
                if cls == 0:  # إذا كان الكائن المكتشف هو شخص
                    # بدء تسجيل الصوت إذا لم يكن هناك تسجيل نشط
                    if not recording_lock.locked():
                        threading.Thread(target=record_audio).start()
            
            # تحويل الإطار إلى JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
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
    app.run(host='0.0.0.0', port=5000)
