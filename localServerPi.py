import cv2
import sounddevice as sd
import wavio
import time
import requests
import numpy as np
import threading
import librosa
import json

# عنوان السيرفر
server_ip = 'http://192.168.173.235:5001'

# دالة لتسجيل الصوت بشكل غير متزامن
def record_audio_async(filename="detected_audio.wav", duration=6):
    def _record():
        sample_rate = 44100
        channels = 2
        audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
        sd.wait()
        wavio.write(filename, audio, sample_rate, sampwidth=2)
    threading.Thread(target=_record, daemon=True).start()

# دالة للتواصل مع السيرفر لتحليل الصوت
def send_audio_to_server(filename):
    with open(filename, 'rb') as audio_file:
        files = {'file': audio_file}
        try:
            response = requests.post(f'{server_ip}/upload_audio', files=files)
            print(f'Status Code: {response.status_code}')
            print(f'Response: {response.text}')
        except Exception as e:
            print(f"Error sending audio to server: {e}")

# دالة للتعامل مع الكاميرا
def handle_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # إضافة أي عملية للكشف عن الأجسام (إذا لزم الأمر)
        # على سبيل المثال، استخدم YOLO أو أي نموذج آخر هنا للكشف عن جسم معين
        # إذا تم اكتشاف الجوال، سيتم إرسال الصوت للمعالجة

        # إرسال الصورة إلى السيرفر إذا تم اكتشاف الجوال
        cv2.imshow('Camera Feed', frame)

        # إذا تم الضغط على "q" للخروج
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# دالة لتحميل البيانات الصوتية إلى السيرفر
@app.route('/upload_audio', methods=['POST'])
def upload_audio():
    """تحميل البيانات الصوتية من Raspberry Pi."""
    audio_file = request.files['file']
    filename = "received_audio.wav"
    audio_file.save(filename)

    # معالجة الصوت
    y, sr = librosa.load(filename, sr=None)
    energy = np.sum(y**2) / len(y)  # الطاقة
    rms = librosa.feature.rms(y=y)[0].mean()  # الجهارة

    if energy < 1e-5 and rms < 0.01:
        cry_prediction = "Silence"
        cry_reason = "No Reason"
    else:
        cry_prediction = predict_cry(filename)
        if cry_prediction == "Crying":
            cry_reason = predict_cry_reason(filename)
        else:
            cry_reason = "Other Sound"

    # إرسال النتائج إلى Raspberry Pi
    response_data = {"cry": cry_prediction, "reason": cry_reason}
    return json.dumps(response_data)

# بدء التعامل مع الكاميرا
handle_camera()
