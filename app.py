import cv2
import requests
import threading
import pyaudio
import wave
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

server_url_video = "http://192.168.173.235:135"
server_url_audio = "http://192.168.173.235:445"
server_url_sensor = "http://192.168.173.235:1521"

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
                    audio_thread = threading.Thread(target=record_audio, args=("audio.wav",))
                    audio_thread.start()
                    audio_thread.join()
                    if analyze_audio("audio.wav"):
                        perform_actions()
            else:
                print(f"Error: Received invalid status code {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error in stream_video: {e}")
        time.sleep(0.1)  # تأخير بسيط لإبطاء إرسال الإطارات

# دالة لتسجيل الصوت
def record_audio(filename):
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 10
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        frames = []
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
    except Exception as e:
        print(f"Error in record_audio: {e}")

# دالة لتحليل الصوت
def analyze_audio(filename):
    try:
        with open(filename, 'rb') as f:
            response = requests.post(
                server_url_audio + "/analyze_audio", 
                files={"audio": f},
                timeout=5
            )
            return response.json().get("crying") == "yes"
    except Exception as e:
        print(f"Error in analyze_audio: {e}")
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
