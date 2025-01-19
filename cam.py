import cv2
from flask import Flask, Response
import torch
import pyaudio
import wave
import threading

# إعداد Flask
app = Flask(__name__)

# تحميل نموذج YOLOv8
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # YOLOv5 أسرع وأسهل لاستخدام نفس الفكرة مع YOLOv8
model.classes = [0]  # التركيز فقط على اكتشاف الأشخاص (class 0)

# إعدادات تسجيل الصوت
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 6
OUTPUT_FILENAME = "output.wav"

# فتح الكاميرا
camera = cv2.VideoCapture(0)

# قفل للتحكم في التسجيل
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

# تعريف دالة لتوليد الفيديو
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # تطبيق YOLO على الإطار
            results = model(frame)
            for detection in results.xyxy[0]:  # نتائج الكشف
                x1, y1, x2, y2, conf, cls = detection
                if int(cls) == 0:  # اكتشاف شخص
                    # رسم صندوق حول الشخص
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, f'Person {conf:.2f}', (int(x1), int(y1) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    # بدء تسجيل الصوت إذا لم يكن هناك تسجيل نشط
                    if not recording_lock.locked():
                        threading.Thread(target=record_audio).start()

            # تحويل الإطار إلى JPEG
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
    app.run(host='0.0.0.0', port=5000)
