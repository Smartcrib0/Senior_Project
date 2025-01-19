import cv2
from flask import Flask, Response

# إعداد Flask
app = Flask(__name__)

# فتح الكاميرا
camera = cv2.VideoCapture(0)  # إذا كنت تستخدم كاميرا USB أو CSI

# تعريف دالة لتوليد الفيديو
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
    # قم بتحديد عنوان IP السيرفر والمنفذ
    app.run(host='192.168.173.235', port=5000)
