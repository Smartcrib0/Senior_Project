import cv2
import time
import requests
import threading
import sounddevice as sd
import wavio
import Adafruit_DHT

# إعدادات الكاميرا
video_capture = cv2.VideoCapture(0)  # استخدام الكاميرا المحلية
video_url = 'http://192.168.173.235:5001/video_feed'  # عنوان الخادم

# إعدادات الصوت
audio_file = "detected_audio.wav"

# إعدادات درجة الحرارة
DHT_SENSOR = Adafruit_DHT.DHT11
DHT_PIN = 4  # الرقم الذي متصل عليه المستشعر

# دالة لقراءة درجة الحرارة
def read_temperature():
    humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
    if humidity is not None and temperature is not None:
        return temperature, humidity
    else:
        return None, None

# دالة لتسجيل الصوت
def record_audio():
    sample_rate = 44100
    channels = 2
    audio = sd.rec(int(6 * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
    sd.wait()
    wavio.write(audio_file, audio, sample_rate, sampwidth=2)

# دالة لإرسال الفيديو والصوت إلى الخادم
def stream_video_and_audio():
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # إرسال الفيديو إلى الخادم
        _, buffer = cv2.imencode('.jpg', frame)
        video_data = buffer.tobytes()
        video_response = requests.post(video_url, files={'frame': video_data})

        # إرسال الصوت إلى الخادم بعد التسجيل
        record_audio()
        with open(audio_file, 'rb') as audio_file_data:
            audio_response = requests.post(f"http://192.168.173.235:5001/audio_results", files={'audio': audio_file_data})

        # إرسال درجة الحرارة إلى الخادم
        temperature, humidity = read_temperature()
        if temperature is not None:
            temperature_data = {'temperature': temperature, 'humidity': humidity}
            temp_response = requests.post(f"http://192.168.173.235:5001/temperature", data=temperature_data)

        # الانتظار بين الدورات
        time.sleep(1)

# بدء البث في خيط منفصل
threading.Thread(target=stream_video_and_audio, daemon=True).start()

# إبقاء البرنامج قيد التشغيل
while True:
    time.sleep(10)
