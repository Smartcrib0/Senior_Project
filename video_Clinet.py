import cv2
import io
import socket
import struct

# تحديد عنوان السيرفر والمنفذ مباشرةً
SERVER_HOST = '192.168.1.100'  # عنوان IP الخاص بالسيرفر
SERVER_PORT = 8000             # المنفذ المستخدم

# إنشاء اتصال مع السيرفر
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

connection = client_socket.makefile('wb')

try:
    # فتح الكاميرا باستخدام OpenCV
    camera = cv2.VideoCapture(0)  # استخدام الكاميرا الافتراضية (ID = 0)
    if not camera.isOpened():
        print("Failed to open camera!")
        exit(1)
    
    print("Starting Camera...")

    while True:
        # التقاط إطار من الكاميرا
        ret, frame = camera.read()
        if not ret:
            print("Failed to grab frame!")
            break
        
        # تحويل الإطار إلى صيغة JPEG
        _, buffer = cv2.imencode('.jpg', frame)
        
        # إرسال طول الصورة أولًا
        connection.write(struct.pack('<L', len(buffer)))
        connection.flush()
        
        # إرسال الصورة
        connection.write(buffer.tobytes())

        # إنهاء البث إذا تم الضغط على مفتاح 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

finally:
    # تحرير الموارد وإغلاق الاتصال
    camera.release()
    connection.close()
    client_socket.close()
