import cv2
import socket
import struct
import threading
import sounddevice as sd
import numpy as np

# إعدادات السيرفر
SERVER_IP = "185.37.12.147"  # IP الخاص بالخادم
SERVER_PORT = 9999
FRAME_QUEUE_SIZE = 10  # حجم الطابور الخاص بالإطارات
AUDIO_QUEUE_SIZE = 10  # حجم الطابور الخاص بالصوت
AUDIO_SAMPLE_RATE = 44100
AUDIO_DURATION = 6  # مدة الصوت لكل مقطع (بالثواني)
AUDIO_CHANNELS = 1  # قناة واحدة (مونوفوني)

# طابور الإطارات وطابور الصوت
frame_queue = Queue(maxsize=FRAME_QUEUE_SIZE)
audio_queue = Queue(maxsize=AUDIO_QUEUE_SIZE)

# دالة لإرسال الفيديو والصوت إلى الخادم
def send_to_server():
    try:
        # إنشاء socket للاتصال بالخادم
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, SERVER_PORT))
        print(f"Connected to server at {SERVER_IP}:{SERVER_PORT}")

        while True:
            # إرسال الإطارات
            if not frame_queue.empty():
                frame = frame_queue.get()
                if frame is None:
                    break

                # ضغط الإطار إلى JPEG
                ret, frame_encoded = cv2.imencode('.jpg', frame)
                if not ret:
                    continue

                frame_data = frame_encoded.tobytes()
                frame_size = len(frame_data)

                # إرسال حجم البيانات ثم البيانات نفسها
                client_socket.sendall(struct.pack(">L", frame_size) + frame_data)

            # إرسال الصوت
            if not audio_queue.empty():
                audio_chunk = audio_queue.get()
                if audio_chunk is None:
                    break

                # إرسال بيانات الصوت
                audio_data = audio_chunk.tobytes()
                audio_size = len(audio_data)
                client_socket.sendall(struct.pack(">L", audio_size) + audio_data)

    except Exception as e:
        print(f"Error in sending data to server: {e}")
    finally:
        client_socket.close()
        print("Connection to server closed.")

# دالة لتسجيل الصوت
def record_audio():
    try:
        while True:
            print("Recording audio...")
            audio = sd.rec(int(AUDIO_SAMPLE_RATE * AUDIO_DURATION), samplerate=AUDIO_SAMPLE_RATE,
                           channels=AUDIO_CHANNELS, dtype="int16")
            sd.wait()
            print("Audio recorded.")

            # إضافة الصوت إلى الطابور
            if not audio_queue.full():
                audio_queue.put(audio)
            else:
                print("Audio queue is full. Dropping audio.")
    except Exception as e:
        print(f"Error in audio recording: {e}")

# بدء الخيط الخاص بإرسال البيانات
threading.Thread(target=send_to_server, daemon=True).start()

# بدء الخيط الخاص بتسجيل الصوت
threading.Thread(target=record_audio, daemon=True).start()

# فتح الكاميرا
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open the camera.")
    exit()

print("Starting video stream...")
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read a frame from the camera.")
            break

        # تغيير حجم الإطار لتقليل حجم البيانات
        frame = cv2.resize(frame, (640, 480))

        # إضافة الإطار إلى الطابور
        if not frame_queue.full():
            frame_queue.put(frame)
        else:
            print("Frame queue is full. Dropping frame.")

        # عرض الإطار محليًا
        cv2.imshow("Live Stream", frame)

        # الخروج عند الضغط على مفتاح 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("Exiting video stream...")
            break

finally:
    # تنظيف
    cap.release()
    frame_queue.put(None)  # إشارة لإنهاء إرسال البيانات
    audio_queue.put(None)  # إشارة لإنهاء إرسال البيانات
    cv2.destroyAllWindows()
