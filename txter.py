import cv2
import time
import threading
from flask import Flask, Response

app = Flask(__name__)

# استيراد الفيديو من الكاميرا
video_source = 0  # أو إذا كانت لديك كاميرا USB يمكنك استخدام /dev/video0

# فتح الكاميرا
cap = cv2.VideoCapture(video_source)

# دالة لالتقاط الصورة وتحويلها إلى MJPEG
def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            # تحويل الصورة إلى تنسيق JPEG
            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            # إرسال الصورة في تنسيق MJPEG عبر HTTP
            frame = jpeg.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# صفحة رئيسية تعرض البث
@app.route('/')
def index():
    return "مرحبا! يمكنك مشاهدة البث عبر الرابط /video_feed"

# دالة لإرسال الفيديو عبر HTTP
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
