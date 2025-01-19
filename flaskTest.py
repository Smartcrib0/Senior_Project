import cv2
import requests

# فتح الكاميرا
camera = cv2.VideoCapture(0)

while True:
    success, frame = camera.read()
    if not success:
        break
    # تحويل الإطار إلى JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    # إرسال الإطار إلى السيرفر
    response = requests.post("http://192.168.173.235:5000/upload", data=buffer.tobytes(), headers={"Content-Type": "image/jpeg"})
    print(response.status_code)
