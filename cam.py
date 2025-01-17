import cv2
import requests
import threading
import time

# عنوان السيرفر
SERVER_URL = "http://185.37.12.147:5000/process_video"

# فتح الكاميرا
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# إرسال الإطارات إلى السيرفر
def send_frame_to_server(frame):
    _, encoded_frame = cv2.imencode('.jpg', frame)  # ترميز الإطار كصورة JPG
    response = requests.post(SERVER_URL, files={'frame': encoded_frame.tobytes()})
    print("Server response:", response.json())

# التقاط الإطارات وإرسالها إلى السيرفر
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read a frame from the camera.")
        break

    # إرسال الإطار في مسار مستقل
    threading.Thread(target=send_frame_to_server, args=(frame,), daemon=True).start()

    # عرض الإطار محليًا (اختياري)
    cv2.imshow("Raspberry Pi Camera", frame)

    # إنهاء التشغيل عند الضغط على 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# تحرير الموارد
cap.release()
cv2.destroyAllWindows()
