# import cv2
# import requests
# import threading
# import pyaudio
# import wave
# import RPi.GPIO as GPIO
# import time
# import subprocess
# import os
# import Adafruit_DHT

# # إعداد GPIO
# servo_pin = 18
# dc_motor_pin = 17
# GPIO.setmode(GPIO.BCM)
# GPIO.setup(servo_pin, GPIO.OUT)
# GPIO.setup(dc_motor_pin, GPIO.OUT)

# servo_pwm = GPIO.PWM(servo_pin, 50)
# servo_pwm.start(0)

# server_url_video = "http://192.168.211.235:5000"
# server_url_audio = "http://192.168.211.235:5001"
# server_url_sensor = "http://192.168.211.235:5050"

# DHT_SENSOR = Adafruit_DHT.DHT11
# DHT_PIN = 4  # رقم الـ PIN المتصل بالحساس

# # متغيرات الحالة
# child_present = False
# other_sound_detected = False
# stop_actions = False
# actions_running = False

# # دالة لتحريك السرير لمدة دقيقتين
# def shake_crib_timed():
#     global stop_actions
#     start_time = time.time()
#     while time.time() - start_time < 30:  # تشغيل لمدة دقيقتين
#         if stop_actions:
#             break
#         try:
#             servo_pwm.ChangeDutyCycle(7)
#             time.sleep(2)
#             servo_pwm.ChangeDutyCycle(0)
#         except Exception as e:
#             print(f"Error in shake_crib: {e}")

# # دالة لتشغيل الموسيقى لمدة دقيقتين
# def play_music_timed():
#     global stop_actions
#     try:
#         file_path = os.path.join(os.getcwd(), "0117.MP3")
#         process = subprocess.Popen(["mpg321", file_path])
#         start_time = time.time()
#         while time.time() - start_time < 30:  # تشغيل لمدة دقيقتين
#             if stop_actions:
#                 process.terminate()  # إيقاف الموسيقى
#                 break
#         process.terminate()
#     except Exception as e:
#         print(f"Error in play_music_timed: {e}")

# # دالة لتشغيل المحرك DC لمدة دقيقتين
# def activate_dc_motor_timed():
#     global stop_actions
#     start_time = time.time()
#     while time.time() - start_time < 30:  # تشغيل لمدة دقيقتين
#         if stop_actions:
#             break
#         try:
#             GPIO.output(dc_motor_pin, GPIO.HIGH)
#             time.sleep(2)
#             GPIO.output(dc_motor_pin, GPIO.LOW)
#         except Exception as e:
#             print(f"Error in activate_dc_motor: {e}")

# # دالة لتنفيذ جميع الإجراءات بالتوازي
# def perform_actions_parallel():
#     global stop_actions, actions_running
#     actions_running = True
#     stop_actions = False

#     # إنشاء خيوط لتنفيذ الإجراءات بالتوازي
#     shake_thread = threading.Thread(target=shake_crib_timed)
#     music_thread = threading.Thread(target=play_music_timed)
#     motor_thread = threading.Thread(target=activate_dc_motor_timed)

#     shake_thread.start()
#     music_thread.start()
#     motor_thread.start()

#     # انتظار انتهاء جميع الخيوط
#     shake_thread.join()
#     music_thread.join()
#     motor_thread.join()

#     actions_running = False
#     print("All actions completed.")

# # دالة لتسجيل الصوت
# def record_audio(filename):
#     try:
#         CHUNK = 1024
#         FORMAT = pyaudio.paInt16
#         CHANNELS = 1
#         RATE = 44100
#         RECORD_SECONDS = 6
#         p = pyaudio.PyAudio()
#         stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
#         frames = []
#         for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
#             data = stream.read(CHUNK)
#             frames.append(data)
#         stream.stop_stream()
#         stream.close()
#         p.terminate()
#         with wave.open(filename, 'wb') as wf:
#             wf.setnchannels(CHANNELS)
#             wf.setsampwidth(p.get_sample_size(FORMAT))
#             wf.setframerate(RATE)
#             wf.writeframes(b''.join(frames))
#     except Exception as e:
#         print(f"Error in record_audio: {e}")

# # دالة لتحليل الصوت
# def analyze_audio(filename):
#     global other_sound_detected
#     try:
#         with open(filename, 'rb') as f:
#             response = requests.post(
#                 server_url_audio + "/analyze_audio", 
#                 files={"audio": f},
#                 timeout=5
#             )
#             other_sound_detected = response.json().get("Other Sound") == "yes"
#             return other_sound_detected
#     except Exception as e:
#         print(f"Error in analyze_audio: {e}")
#         return False

# # دالة لقراءة بيانات الحساس وإرسالها
# def read_and_send_sensor_data():
#     while True:
#         try:
#             humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
#             if humidity is not None and temperature is not None:
#                 data = {"temperature": temperature, "humidity": humidity}
#                 try:
#                     response = requests.post(server_url_sensor + "/upload_sensor_data", json=data, timeout=5)
#                     if response.status_code != 200:
#                         print(f"Error: Failed to send sensor data, status code {response.status_code}")
#                 except requests.exceptions.RequestException as e:
#                     print(f"Error in sending sensor data: {e}")
#             time.sleep(5)  # إرسال البيانات كل 5 ثوانٍ
#         except Exception as e:
#             print(f"Error in read_and_send_sensor_data: {e}")

# # دالة لمتابعة الفيديو وتحليل الإطارات
# def stream_video():
#     global child_present, other_sound_detected, stop_actions, actions_running
#     cap = cv2.VideoCapture(0)
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             print("Error: Unable to access camera")
#             continue
#         _, buffer = cv2.imencode('.jpg', frame)
#         try:
#             response = requests.post(
#                 server_url_video + "/upload_frame", 
#                 files={"frame": buffer.tobytes()},
#                 timeout=10
#             )
#             if response.status_code == 200:
#                 response_data = response.json()
#                 child_present = response_data.get("child_detected", False)
                
#                 if child_present:
#                     print("Child detected.")
#                     if not actions_running:  # إذا لم تكن المهام تعمل
#                         if not other_sound_detected:
#                             record_audio("audio.wav")
#                             if analyze_audio("audio.wav"):
#                                 print("Other sound detected, starting actions.")
#                                 perform_actions_parallel()
#                     else:
#                         print("Actions already running.")
#                 else:
#                     print("No child detected, stopping actions.")
#                     stop_actions = True
#         except requests.exceptions.RequestException as e:
#             print(f"Error in stream_video: {e}")
#         time.sleep(0.1)

# # تشغيل الخيوط
# video_thread = threading.Thread(target=stream_video)
# sensor_thread = threading.Thread(target=read_and_send_sensor_data)

# video_thread.start()
# sensor_thread.start()




import cv2
import requests
import threading
import pyaudio
import wave
import RPi.GPIO as GPIO
import time
import subprocess
import os
import Adafruit_DHT

# إعداد GPIO
servo_pin = 18
dc_motor_pin = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)
GPIO.setup(dc_motor_pin, GPIO.OUT)

servo_pwm = GPIO.PWM(servo_pin, 50)
servo_pwm.start(0)

server_url_video = "http://192.168.211.235:5000"
server_url_audio = "http://192.168.211.235:5001"
server_url_sensor = "http://192.168.211.235:5050"

DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # رقم الـ PIN المتصل بالحساس

# متغيرات الحالة
child_present = False
other_sound_detected = False
stop_actions = False
actions_running = False

# دالة لتحريك السرير لمدة دقيقتين
def shake_crib_timed():
    global stop_actions
    start_time = time.time()
    while time.time() - start_time < 30:  # تشغيل لمدة دقيقتين
        if stop_actions:
            break
        try:
            servo_pwm.ChangeDutyCycle(7)
            time.sleep(2)
            servo_pwm.ChangeDutyCycle(0)
        except Exception as e:
            print(f"Error in shake_crib: {e}")

# دالة لتشغيل الموسيقى لمدة دقيقتين
def play_music_timed():
    global stop_actions
    try:
        file_path = os.path.join(os.getcwd(), "0117.MP3")
        process = subprocess.Popen(["mpg321", file_path])
        start_time = time.time()
        while time.time() - start_time < 30:  # تشغيل لمدة دقيقتين
            if stop_actions:
                process.terminate()  # إيقاف الموسيقى
                break
        process.terminate()
    except Exception as e:
        print(f"Error in play_music_timed: {e}")

# دالة لتشغيل المحرك DC لمدة دقيقتين
def activate_dc_motor_timed():
    global stop_actions
    start_time = time.time()
    while time.time() - start_time < 30:  # تشغيل لمدة دقيقتين
        if stop_actions:
            break
        try:
            GPIO.output(dc_motor_pin, GPIO.HIGH)
            time.sleep(2)
            GPIO.output(dc_motor_pin, GPIO.LOW)
        except Exception as e:
            print(f"Error in activate_dc_motor: {e}")

# دالة لتنفيذ جميع الإجراءات بالتوازي
def perform_actions_parallel():
    global stop_actions, actions_running
    actions_running = True
    stop_actions = False

    # إنشاء خيوط لتنفيذ الإجراءات بالتوازي
    shake_thread = threading.Thread(target=shake_crib_timed)
    music_thread = threading.Thread(target=play_music_timed)
    motor_thread = threading.Thread(target=activate_dc_motor_timed)

    shake_thread.start()
    music_thread.start()
    motor_thread.start()

    # انتظار انتهاء جميع الخيوط
    shake_thread.join()
    music_thread.join()
    motor_thread.join()

    actions_running = False
    print("All actions completed.")

# دالة لتسجيل الصوت
def record_audio(filename):
    try:
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        RECORD_SECONDS = 6
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
    global other_sound_detected
    try:
        with open(filename, 'rb') as f:
            response = requests.post(
                server_url_audio + "/analyze_audio", 
                files={"audio": f},
                timeout=5
            )
            other_sound_detected = response.json().get("Other Sound") == "yes"
            return other_sound_detected
    except Exception as e:
        print(f"Error in analyze_audio: {e}")
        return False

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

# دالة لمتابعة الفيديو وتحليل الإطارات
def stream_video():
    global child_present, other_sound_detected, stop_actions, actions_running
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Unable to access camera")
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        try:
            response = requests.post(
                server_url_video + "/upload_frame", 
                files={"frame": buffer.tobytes()},
                timeout=10
            )
            if response.status_code == 200:
                response_data = response.json()
                child_present = response_data.get("child_detected", False)
                
                if child_present:
                    print("Child detected.")
                    if not actions_running:  # إذا لم تكن المهام تعمل
                        if not other_sound_detected:
                            record_audio("audio.wav")
                            if analyze_audio("audio.wav"):
                                print("Other sound detected, starting actions.")
                                perform_actions_parallel()
                    else:
                        print("Actions already running.")
                else:
                    print("No child detected, stopping actions.")
                    stop_actions = True
        except requests.exceptions.RequestException as e:
            print(f"Error in stream_video: {e}")
        time.sleep(0.1)

# تشغيل الخيوط
video_thread = threading.Thread(target=stream_video)
sensor_thread = threading.Thread(target=read_and_send_sensor_data)

video_thread.start()
sensor_thread.start()