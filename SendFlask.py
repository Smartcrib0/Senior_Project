import cv2
import Adafruit_DHT
import requests
import subprocess
import time
import numpy as np

# إعدادات السيرفر
SERVER_IP = "185.37.12.147"
RTMP_URL = f"rtmp://{SERVER_IP}/live/stream"
TEMPERATURE_API_URL = f"http://{SERVER_IP}/api/temperature"

# إعدادات المستشعر
SENSOR_TYPE = Adafruit_DHT.DHT22
SENSOR_PIN = 4  # GPIO pin connected to the DHT22

# إعدادات الكاميرا والميكروفون
CAMERA_INDEX = 0  # عادةً 0 للكاميرا الأساسية
MIC_SOURCE = "hw:1,0"  # مصدر الصوت (الميكروفون)

def start_live_stream():
    """
    بدء إرسال لايف ستريمنغ للفيديو والصوت إلى السيرفر باستخدام OpenCV وFFmpeg.
    """
    # فتح الكاميرا
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # إعداد FFmpeg لإرسال الفيديو والصوت عبر RTMP
    command = [
        'ffmpeg',
        '-y',
        '-f', 'rawvideo', '-pix_fmt', 'bgr24',  # تنسيق الفيديو من OpenCV
        '-s', '640x480',  # حجم الفيديو (يمكن تعديله)
        '-r', '30',  # معدل الإطارات (Frame Rate)
        '-i', '-',  # المدخل من stdin (الفيديو)
        '-f', 'alsa', '-i', MIC_SOURCE,  # مصدر الصوت
        '-c:v', 'libx264', '-preset', 'ultrafast', '-tune', 'zerolatency',  # ضغط الفيديو
        '-c:a', 'aac',  # ضغط الصوت
        '-f', 'flv', RTMP_URL  # الإرسال إلى السيرفر
    ]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Failed to capture frame.")
                break

            # عرض الفيديو محليًا (اختياري)
            cv2.imshow('Live Stream', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):  # اضغط 'q' للخروج
                break

            # إرسال الإطار إلى FFmpeg
            try:
                process.stdin.write(frame.tobytes())
            except BrokenPipeError:
                print("FFmpeg process crashed. Restarting...")
                process = subprocess.Popen(command, stdin=subprocess.PIPE)

    except KeyboardInterrupt:
        print("Streaming stopped.")

    finally:
        # تحرير الموارد
        cap.release()
        cv2.destroyAllWindows()
        process.stdin.close()
        process.wait()

def read_temperature():
    """
    قراءة درجة الحرارة والرطوبة من مستشعر DHT22.
    """
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR_TYPE, SENSOR_PIN)
    if temperature is not None:
        return temperature
    else:
        print("Failed to retrieve data from sensor")
        return None

def send_temperature(temperature):
    """
    إرسال درجة الحرارة إلى السيرفر باستخدام HTTP POST.
    """
    data = {"temperature": temperature}
    try:
        response = requests.post(TEMPERATURE_API_URL, json=data)
        print(f"Temperature sent: {temperature}°C, Response: {response.text}")
    except Exception as e:
        print(f"Failed to send temperature: {e}")

if __name__ == "__main__":
    # بدء لايف ستريمنغ
    start_live_stream()

    # إرسال درجة الحرارة كل 10 ثواني
    while True:
        temperature = read_temperature()
        if temperature is not None:
            send_temperature(temperature)
        time.sleep(10)  # انتظر 10 ثواني قبل الإرسال التالي
