import cv2
import requests
import threading
import pyaudio
import RPi.GPIO as GPIO
import time
import subprocess
import Adafruit_DHT

# إعداد GPIO
servo_pin = 18
dc_motor_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setup(dc_motor_pin, GPIO.OUT)

servo_pwm = GPIO.PWM(servo_pin, 50)
servo_pwm.start(0)

server_url_video = "http://192.168.173.235:5000"
server_url_audio = "http://192.168.173.235:5001"
server_url_sensor = "http://192.168.173.235:5050"

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # رقم الـ PIN المتصل بالحساس

# دالة لتسجيل الفيديو
def stream_video():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to access camera")
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        
        # تحقق من الاتصال بالسيرفر قبل إرسال البيانات
        try:
            response = requests.post(
                server_url_video + "/upload_frame", 
                files={"frame": buffer.tobytes()},
                timeout=5
            )
            if response.status_code == 200:
                response_data = response.json()
                if response_data.get("child_detected"):
                    print("Child detected, starting audio recording...")
                    if record_and_send_audio():
                        perform_actions()
            else:
                print(f"Error: Received invalid status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error in stream_video: {e}")
        time.sleep(0.1)  # تأخير بسيط لإبطاء إرسال الإطارات

# دالة لتسجيل الصوت وإرساله إلى السيرفر مباشرة
def record_and_send_audio():
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

        print("Recording audio...")
        audio_data = b""
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            audio_data += data

        print("Sending audio to server...")
        response = requests.post(
            server_url_audio + "/analyze_audio",
            files={"audio": ("audio.wav", audio_data, "audio/wav")},
            timeout=10
        )

        stream.stop_stream()
        stream.close()
        p.terminate()

        if response.status_code == 200:
            print(f"Server response: {response.json()}")
            return response.json().get("crying") == "yes"
        else:
            print(f"Error: Received status code {response.status_code}")
            return False

    except Exception as e:
        print(f"Error in record_and_send_audio: {e}")
        return False

# دالة لتنفيذ الإجراءات عند اكتشاف الطفل يبكي
def perform_actions():
    shake_crib()
    play_music()
    activate_dc_motor()

# دالة لتحريك السرير
def shake_crib():
    try:
        servo_pwm.ChangeDutyCycle(7)
        time.sleep(2)
        servo_pwm.ChangeDutyCycle(0)
    except Exception as e:
        print(f"Error in shake_crib: {e}")

# دالة لتشغيل الموسيقى
def play_music():
    try:
        subprocess.call(["mpg321", "0117.MP3"])
    except Exception as e:
        print(f"Error in play_music: {e}")

# دالة لتشغيل المحرك DC
def activate_dc_motor():
    try:
        GPIO.output(dc_motor_pin, GPIO.HIGH)
        time.sleep(2)
        GPIO.output(dc_motor_pin, GPIO.LOW)
    except Exception as e:
        print(f"Error in activate_dc_motor: {e}")

# دالة لقراءة بيانات الحساس وإرسالها
def read_and_send_sensor_data():
    while True:
        try:
            humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
            if humidity is not None and temperature is not None:
                data = {"temperature": temperature, "humidity": humidity}
                try:
                    response = requests.post(server_url_sensor + "/upload_sensor_data", json=data, timeout=5)
                    if response.status_code != 200:
                        print(f"Error: Failed to send sensor data, status code {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print(f"Error in sending sensor data: {e}")
            time.sleep(5)  # إرسال البيانات كل 5 ثوانٍ
        except Exception as e:
            print(f"Error in read_and_send_sensor_data: {e}")

# تشغيل الخيوط
video_thread = threading.Thread(target=stream_video)
sensor_thread = threading.Thread(target=read_and_send_sensor_data)

video_thread.start()
sensor_thread.start()