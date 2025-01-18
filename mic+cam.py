import cv2
import requests
import sounddevice as sd
import wavio
import threading

# عنوان السيرفر
SERVER_URL_VIDEO = "http://185.37.12.147:5000/process_video"
SERVER_URL_AUDIO = "http://185.37.12.147:5000/process_audio"

# فتح الكاميرا
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

# دالة لتسجيل الصوت وإرساله إلى السيرفر
def record_and_send_audio():
    duration = 6  # مدة التسجيل بالثواني
    sample_rate = 44100
    channels = 2
    filename = "recorded_audio.wav"

    # تسجيل الصوت
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
    sd.wait()
    wavio.write(filename, audio, sample_rate, sampwidth=2)

    # إرسال الصوت إلى السيرفر
    with open(filename, 'rb') as audio_file:
        files = {'file': audio_file}
        try:
            response = requests.post(SERVER_URL_AUDIO, files=files)
            print("Audio analysis response:", response.json())
        except Exception as e:
            print("Error sending audio to server:", e)

# إرسال الإطارات إلى السيرفر
def send_frame_to_server(frame):
    _, encoded_frame = cv2.imencode('.jpg', frame)  # ترميز الإطار كصورة JPG
    try:
        response = requests.post(SERVER_URL_VIDEO, files={'frame': encoded_frame.tobytes()})
        server_response = response.json()
        print("Server response:", server_response)

        # إذا تم اكتشاف الطفل، قم بتسجيل الصوت
        if server_response.get("detected"):
            record_and_send_audio()
    except Exception as e:
        print("Error sending frame to server:", e)

# التقاط الإطارات وإرسالها إلى السيرفر
while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read a frame from the camera.")
        break

    # إرسال الإطار في مسار منفصل
    threading.Thread(target=send_frame_to_server, args=(frame,), daemon=True).start()

    # عرض الإطار محليًا (اختياري)
    cv2.imshow("Raspberry Pi Camera", frame)

    # إنهاء التشغيل عند الضغط على 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# تحرير الموارد
cap.release()
cv2.destroyAllWindows()
