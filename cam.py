import cv2
from flask import Flask, Response
import pyaudio
import wave
import threading

# إعداد Flask
app = Flask(__name__)

# تحميل نموذج YOLO باستخدام OpenCV DNN
net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")  # قم بتحميل yolov4 أو yolov3 أو النموذج الذي تود استخدامه
layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]

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
    """توليد الإطارات ومعالجتها باستخدام YOLO عبر OpenCV DNN"""
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # تحويل الإطار إلى مدخلات DNN
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)
            outs = net.forward(output_layers)

            # معالجة النتائج للتعرف على الأجسام
            class_ids = []
            confidences = []
            boxes = []
            height, width, channels = frame.shape

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    if confidence > 0.5:  # عتبة الثقة
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w / 2)
                        y = int(center_y - h / 2)

                        boxes.append([x, y, w, h])
                        confidences.append(float(confidence))
                        class_ids.append(class_id)

            # تصفية النتائج باستخدام NMS (Non-Maximum Suppression)
            indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

            # التحقق إذا تم اكتشاف شخص
            for i in indices.flatten():
                if class_ids[i] == 0:  # إذا كان الكائن المكتشف هو شخص
                    # بدء تسجيل الصوت إذا لم يكن هناك تسجيل نشط
                    if not recording_lock.locked():
                        threading.Thread(target=record_audio).start()

            # رسم الصناديق على الإطار
            for i in indices.flatten():
                x, y, w, h = boxes[i]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Person", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

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
