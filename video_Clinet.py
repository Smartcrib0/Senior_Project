import io
import socket
import struct
import time
import picamera

# تحديد عنوان السيرفر والمنفذ مباشرةً
SERVER_HOST = '192.168.1.100'  # عنوان IP الخاص بالسيرفر
SERVER_PORT = 8000             # المنفذ المستخدم

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))

connection = client_socket.makefile('wb')
try:
    with picamera.PiCamera() as camera:
        camera.resolution = (640, 480)
        print("Starting Camera...........")
        time.sleep(2)  # تأخير لضمان أن الكاميرا جاهزة
        
        stream = io.BytesIO()
        for foo in camera.capture_continuous(stream, 'jpeg'):
            # إرسال طول الصورة أولاً
            connection.write(struct.pack('<L', stream.tell()))
            connection.flush()
            
            # إرسال بيانات الصورة
            stream.seek(0)
            connection.write(stream.read())
            
            # تنظيف التدفق لإعادة الاستخدام
            stream.seek(0)
            stream.truncate()
finally:
    # إغلاق الاتصال
    connection.close()
    client_socket.close()
