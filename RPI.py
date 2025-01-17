import cv2
import sounddevice as sd
import wavio
import threading
import requests
import time

# إعدادات السيرفر
SERVER_URL = "http://<server-ip>:5000/upload_audio"  # استبدل <server-ip> بعنوان السيرفر الخاص بك

# دالة لتسجيل الصوت وإرساله إلى السيرفر
def record_and_send_audio():
    def _record_audio():
        sample_rate = 44100
        duration = 6  # مدة التسجيل بالثواني
        filename = "recorded_audio.wav"

        print("Recording audio...")
        audio = sd.rec(int(sample_rate * duration), samplerate=sample_rate, channels=2, dtype='int16')
        sd.wait()  # انتظر حتى انتهاء التسجيل
        wavio.write(filename, audio, sample_rate, sampwidth=2)  # احفظ الملف الصوتي
        
        # إرسال الملف الصوتي إلى السيرفر
        try:
            print("Sending audio to server...")
            with open(filename, 'rb') as f:
                response = requests.post(SERVER_URL, files={'file': f})
                print("Server response:", response.json())
        except Exception as e:
            print("Error sending audio:", e)
    
    threading.Thread(target=_record_audio, daemon=True).start()

# دالة لبث الفيديو
def stream_video():
    cap = cv2.VideoCapture(0)  # افتح الكاميرا
    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from the camera.")
            break

        # عرض الفيديو محليًا
        cv2.imshow("Raspberry Pi Camera", frame)

        # تحقق إذا تم الضغط على "q" للخروج
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # تسجيل الصوت وإرساله إذا اكتشف فيديو
        record_and_send_audio()

        time.sleep(6)  # انتظر قليلاً لتقليل التحميل على الشبكة

    cap.release()
    cv2.destroyAllWindows()

# تشغيل بث الفيديو
if __name__ == "__main__":
    print("Starting video stream...")
    stream_video()
